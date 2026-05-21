"""Narrow runtime activation for governed Nova SkillArtifacts."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from agent.nova.kernel import ArtifactTrustState, LedgerEntryKind, stable_hash
from agent.nova.ledger import AppendOnlyLedger
from agent.nova.skill_artifacts import (
    JSONLSkillArtifactStore,
    PromotedSkillArtifact,
    SkillArtifactActivation,
    SkillArtifactError,
    read_skill_payload,
    skill_content_hash,
)

logger = logging.getLogger(__name__)


class SkillArtifactActivationError(SkillArtifactError):
    """Raised when enabled SkillArtifact activation cannot safely proceed."""


@dataclass(frozen=True)
class SkillActivationContext:
    run_id: str
    repo_scope: str
    task_hash: str
    benchmark_chain_id: str = ""
    explicit_artifact_id: str = ""
    excluded_artifact_ids: tuple[str, ...] = ()

    @classmethod
    def from_task(
        cls,
        *,
        run_id: str,
        task_text: str,
        repo_scope: str,
        benchmark_chain_id: str = "",
        explicit_artifact_id: str = "",
        excluded_artifact_ids: Iterable[str] | None = None,
    ) -> "SkillActivationContext":
        excluded = tuple(sorted(str(item) for item in (excluded_artifact_ids or ()) if str(item)))
        return cls(
            run_id=str(run_id),
            repo_scope=str(repo_scope),
            task_hash=stable_hash({"task_text": str(task_text)}),
            benchmark_chain_id=str(benchmark_chain_id or ""),
            explicit_artifact_id=str(explicit_artifact_id or ""),
            excluded_artifact_ids=excluded,
        )

    @property
    def activation_context_hash(self) -> str:
        return stable_hash(
            {
                "run_id": self.run_id,
                "repo_scope": self.repo_scope,
                "task_hash": self.task_hash,
                "benchmark_chain_id": self.benchmark_chain_id,
                "explicit_artifact_id": self.explicit_artifact_id,
                "excluded_artifact_ids": self.excluded_artifact_ids,
            }
        )


@dataclass(frozen=True)
class SkillArtifactActivationResult:
    artifact: PromotedSkillArtifact
    activation: SkillArtifactActivation
    context_block: str


class DisabledSkillArtifactActivationController:
    enabled = False
    strict = False

    def activate_for_run(self, *args: Any, **kwargs: Any) -> None:
        return None


class SkillArtifactActivationController:
    """Resolve and log at most one promoted skill artifact for a run."""

    def __init__(
        self,
        *,
        store: JSONLSkillArtifactStore,
        repo_scope: str,
        enabled: bool = False,
        benchmark_chain_id: str = "",
        explicit_artifact_id: str = "",
        excluded_artifact_ids: Iterable[str] | None = None,
        allowed_trust_states: Iterable[ArtifactTrustState | str] | None = None,
        strict: bool = True,
        require_match: bool = True,
    ) -> None:
        self.store = store
        self.repo_scope = str(repo_scope)
        self.enabled = bool(enabled)
        self.benchmark_chain_id = str(benchmark_chain_id or "")
        self.explicit_artifact_id = str(explicit_artifact_id or "")
        self.excluded_artifact_ids = tuple(
            sorted(str(item) for item in (excluded_artifact_ids or ()) if str(item))
        )
        self.allowed_trust_states = tuple(
            ArtifactTrustState(state)
            for state in (allowed_trust_states or (ArtifactTrustState.ACTIVE,))
        )
        self.strict = bool(strict)
        self.require_match = bool(require_match)

    def activate_for_run(
        self,
        *,
        run_id: str,
        task_text: str,
        ledger: AppendOnlyLedger | None = None,
    ) -> SkillArtifactActivationResult | None:
        if not self.enabled:
            return None
        context = SkillActivationContext.from_task(
            run_id=run_id,
            task_text=task_text,
            repo_scope=self.repo_scope,
            benchmark_chain_id=self.benchmark_chain_id,
            explicit_artifact_id=self.explicit_artifact_id,
            excluded_artifact_ids=self.excluded_artifact_ids,
        )
        try:
            resolved = resolve_skill_artifact(
                self.store.latest_artifacts(),
                context,
                allowed_trust_states=self.allowed_trust_states,
            )
            if resolved is None:
                if self.require_match:
                    raise SkillArtifactActivationError("no promoted SkillArtifact matched context")
                return None
            artifact, reason = resolved
            content = read_skill_payload(artifact.skill_path, expected_hash=artifact.content_hash)
            digest = skill_content_hash(content)
            activation = SkillArtifactActivation(
                run_id=context.run_id,
                artifact_id=artifact.artifact_id,
                version_id=artifact.version_id,
                reason=reason,
                scope=artifact.scope,
                projected_content_hash=digest,
                projected_content_preview=_preview(content),
                activation_context_hash=context.activation_context_hash,
            )
            self.store.put_activation(activation)
            if ledger is not None:
                ledger.append_event(
                    context.run_id,
                    LedgerEntryKind.ACTIVATION_SNAPSHOT,
                    actor="nova",
                    subject_ref=f"artifact:{artifact.artifact_id}",
                    evidence_bundle_id=artifact.evidence_bundle_id,
                    policy_decision_id=artifact.gate_decision_id,
                    payload_ref=f"skill-artifact:{artifact.version_id}",
                    metadata={
                        "activation_id": activation.id,
                        "artifact_id": artifact.artifact_id,
                        "version_id": artifact.version_id,
                        "reason": reason,
                        "scope": artifact.scope,
                        "content_hash": digest,
                        "activation_context_hash": context.activation_context_hash,
                    },
                )
            return SkillArtifactActivationResult(
                artifact=artifact,
                activation=activation,
                context_block=format_skill_activation_block(artifact, activation, content),
            )
        except Exception:
            if self.strict:
                raise
            logger.warning("Nova SkillArtifact activation failed closed", exc_info=True)
            return None


def resolve_skill_artifact(
    artifacts: Iterable[PromotedSkillArtifact],
    context: SkillActivationContext,
    *,
    allowed_trust_states: Iterable[ArtifactTrustState | str] = (ArtifactTrustState.ACTIVE,),
) -> tuple[PromotedSkillArtifact, str] | None:
    allowed = {ArtifactTrustState(state) for state in allowed_trust_states}
    candidates: list[tuple[PromotedSkillArtifact, str]] = []
    excluded = set(context.excluded_artifact_ids)
    for artifact in artifacts:
        if artifact.artifact_id in excluded:
            continue
        if artifact.trust_state not in allowed:
            continue
        reason = _match_reason(artifact, context)
        if reason:
            candidates.append((artifact, reason))
    if context.explicit_artifact_id:
        candidates = [
            item for item in candidates if item[0].artifact_id == context.explicit_artifact_id
        ]
    if not candidates:
        return None
    if len(candidates) > 1:
        ids = ", ".join(sorted(item[0].artifact_id for item in candidates))
        raise SkillArtifactActivationError(
            f"multiple SkillArtifacts matched activation context: {ids}"
        )
    return candidates[0]


def format_skill_activation_block(
    artifact: PromotedSkillArtifact,
    activation: SkillArtifactActivation,
    content: str,
) -> str:
    return (
        "[Nova SkillArtifact activation]\n"
        f"artifact_id: {artifact.artifact_id}\n"
        f"version_id: {artifact.version_id}\n"
        f"scope: {artifact.scope}\n"
        f"content_hash: {activation.projected_content_hash}\n"
        "\n"
        f"{content.rstrip()}\n"
        "[/Nova SkillArtifact activation]"
    )


def repo_scope_for_path(path: str | Path | None = None) -> str:
    base = Path(path or Path.cwd()).resolve()
    return f"repo:{base.as_posix()}"


def build_skill_activation_controller_from_config(
    config: Mapping[str, Any],
    *,
    cwd: str | Path | None = None,
) -> SkillArtifactActivationController | DisabledSkillArtifactActivationController:
    nova_cfg = config.get("nova", {}) if isinstance(config, Mapping) else {}
    skill_cfg = nova_cfg.get("skill_artifacts", {}) if isinstance(nova_cfg, Mapping) else {}
    if not isinstance(skill_cfg, Mapping) or not _as_bool(skill_cfg.get("enabled", False)):
        return DisabledSkillArtifactActivationController()

    store = JSONLSkillArtifactStore(
        skill_cfg.get("artifact_store_path") or None,
        skill_cfg.get("activation_log_path") or None,
    )
    return SkillArtifactActivationController(
        store=store,
        enabled=True,
        repo_scope=str(skill_cfg.get("repo_scope") or repo_scope_for_path(cwd)),
        benchmark_chain_id=str(skill_cfg.get("benchmark_chain_id") or ""),
        explicit_artifact_id=str(
            skill_cfg.get("explicit_artifact_id")
            or skill_cfg.get("allowed_artifact_id")
            or ""
        ),
        excluded_artifact_ids=_as_list(skill_cfg.get("exclude_artifact_ids")),
        allowed_trust_states=_as_list(skill_cfg.get("allowed_trust_states")) or (
            ArtifactTrustState.ACTIVE,
        ),
        strict=_as_bool(skill_cfg.get("strict", True)),
        require_match=_as_bool(skill_cfg.get("require_match", True)),
    )


def _match_reason(artifact: PromotedSkillArtifact, context: SkillActivationContext) -> str:
    rule = artifact.activation_rule
    if artifact.scope == context.repo_scope or rule.get("repo_scope") == context.repo_scope:
        return "exact repo scope match"
    if context.benchmark_chain_id and rule.get("benchmark_chain_id") == context.benchmark_chain_id:
        return "exact benchmark chain match"
    return ""


def _preview(content: str, *, limit: int = 1000) -> str:
    return str(content)[:limit]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    return [str(value)]


__all__ = [
    "DisabledSkillArtifactActivationController",
    "SkillActivationContext",
    "SkillArtifactActivationController",
    "SkillArtifactActivationError",
    "SkillArtifactActivationResult",
    "build_skill_activation_controller_from_config",
    "format_skill_activation_block",
    "repo_scope_for_path",
    "resolve_skill_artifact",
]
