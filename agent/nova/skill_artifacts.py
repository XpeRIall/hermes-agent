"""Narrow Nova SkillArtifact records and activation logging.

This module is deliberately smaller than general substrate composition. It
models one promoted skill artifact family and writes explicit activation logs;
it does not activate other substrate families or change skill-manager writes.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from agent.nova.kernel import ArtifactTrustState, stable_json_dumps
from agent.nova.substrate import SubstrateArtifactType
from hermes_constants import get_hermes_home


SKILL_ARTIFACTS_FILENAME = "skill_artifacts.jsonl"
SKILL_ACTIVATIONS_FILENAME = "skill_artifact_activations.jsonl"


class SkillArtifactError(ValueError):
    """Raised when a promoted skill artifact is invalid or unsafe to use."""


def default_skill_artifact_store_path() -> Path:
    return get_hermes_home() / "nova" / SKILL_ARTIFACTS_FILENAME


def default_skill_activation_log_path() -> Path:
    return get_hermes_home() / "nova" / SKILL_ACTIVATIONS_FILENAME


def skill_content_hash(content: str | bytes) -> str:
    data = content if isinstance(content, bytes) else str(content).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def read_skill_payload(path: str | Path, *, expected_hash: str | None = None) -> str:
    payload_path = Path(path)
    content = payload_path.read_text(encoding="utf-8")
    digest = skill_content_hash(content)
    if expected_hash is not None and digest != _normalize_hash(expected_hash):
        raise SkillArtifactError(
            f"skill payload hash mismatch for {payload_path}: expected "
            f"{_normalize_hash(expected_hash)}, got {digest}"
        )
    return content


@dataclass(frozen=True)
class PromotedSkillArtifact:
    """One governed skill artifact version eligible for narrow activation."""

    artifact_id: str
    version_id: str
    version: int
    scope: str
    activation_rule: Mapping[str, Any]
    skill_name: str
    skill_slug: str
    skill_path: str
    content_hash: str
    payload_ref: str
    evidence_bundle_id: str
    gate_decision_id: str
    trust_state: ArtifactTrustState
    created_at: float = field(default_factory=time.time)
    artifact_type: SubstrateArtifactType = SubstrateArtifactType.SKILL

    def __post_init__(self) -> None:
        artifact_type = SubstrateArtifactType(self.artifact_type)
        trust_state = ArtifactTrustState(self.trust_state)
        if artifact_type is not SubstrateArtifactType.SKILL:
            raise SkillArtifactError("promoted skill artifacts must have artifact_type=skill")
        if int(self.version) < 1:
            raise SkillArtifactError("artifact versions start at 1")
        for field_name in (
            "artifact_id",
            "version_id",
            "scope",
            "skill_name",
            "skill_slug",
            "skill_path",
            "content_hash",
            "payload_ref",
            "evidence_bundle_id",
            "gate_decision_id",
        ):
            if not str(getattr(self, field_name)).strip():
                raise SkillArtifactError(f"{field_name} is required")
        if not isinstance(self.activation_rule, Mapping):
            raise SkillArtifactError("activation_rule must be a mapping")
        object.__setattr__(self, "artifact_id", str(self.artifact_id))
        object.__setattr__(self, "version_id", str(self.version_id))
        object.__setattr__(self, "version", int(self.version))
        object.__setattr__(self, "scope", str(self.scope))
        object.__setattr__(self, "activation_rule", dict(self.activation_rule))
        object.__setattr__(self, "skill_name", str(self.skill_name))
        object.__setattr__(self, "skill_slug", str(self.skill_slug))
        object.__setattr__(self, "skill_path", str(self.skill_path))
        object.__setattr__(self, "content_hash", _normalize_hash(self.content_hash))
        object.__setattr__(self, "payload_ref", str(self.payload_ref))
        object.__setattr__(self, "evidence_bundle_id", str(self.evidence_bundle_id))
        object.__setattr__(self, "gate_decision_id", str(self.gate_decision_id))
        object.__setattr__(self, "trust_state", trust_state)
        object.__setattr__(self, "artifact_type", artifact_type)
        object.__setattr__(self, "created_at", float(self.created_at))

    def to_record(self) -> dict[str, Any]:
        return _stable_record(self)


@dataclass(frozen=True)
class SkillArtifactActivation:
    """Audit record for one activated skill artifact in one run."""

    run_id: str
    artifact_id: str
    version_id: str
    reason: str
    scope: str
    projected_content_hash: str
    projected_content_preview: str
    activation_context_hash: str
    id: str = field(default_factory=lambda: f"act_{uuid.uuid4().hex}")
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        for field_name in (
            "run_id",
            "artifact_id",
            "version_id",
            "reason",
            "scope",
            "projected_content_hash",
            "activation_context_hash",
            "id",
        ):
            if not str(getattr(self, field_name)).strip():
                raise SkillArtifactError(f"{field_name} is required")
        object.__setattr__(self, "run_id", str(self.run_id))
        object.__setattr__(self, "artifact_id", str(self.artifact_id))
        object.__setattr__(self, "version_id", str(self.version_id))
        object.__setattr__(self, "reason", str(self.reason))
        object.__setattr__(self, "scope", str(self.scope))
        object.__setattr__(
            self,
            "projected_content_hash",
            _normalize_hash(self.projected_content_hash),
        )
        object.__setattr__(
            self,
            "projected_content_preview",
            _bounded_preview(self.projected_content_preview, limit=1000),
        )
        object.__setattr__(self, "activation_context_hash", str(self.activation_context_hash))
        object.__setattr__(self, "id", str(self.id))
        object.__setattr__(self, "created_at", float(self.created_at))

    def to_record(self) -> dict[str, Any]:
        return _stable_record(self)


class JSONLSkillArtifactStore:
    """Append-only JSONL storage for promoted artifacts and activation logs."""

    def __init__(
        self,
        artifact_path: str | Path | None = None,
        activation_log_path: str | Path | None = None,
    ) -> None:
        self.artifact_path = Path(artifact_path) if artifact_path else default_skill_artifact_store_path()
        self.activation_log_path = (
            Path(activation_log_path) if activation_log_path else default_skill_activation_log_path()
        )

    def put_artifact(self, artifact: PromotedSkillArtifact) -> PromotedSkillArtifact:
        if not isinstance(artifact, PromotedSkillArtifact):
            raise TypeError(
                "artifact must be PromotedSkillArtifact, "
                f"got {type(artifact).__name__}"
            )
        _append_jsonl(self.artifact_path, artifact.to_record())
        return artifact

    def iter_artifacts(self) -> list[PromotedSkillArtifact]:
        return [
            PromotedSkillArtifact(**record)
            for record in _read_jsonl(self.artifact_path)
        ]

    def latest_artifacts(self) -> list[PromotedSkillArtifact]:
        latest: dict[str, PromotedSkillArtifact] = {}
        for artifact in self.iter_artifacts():
            current = latest.get(artifact.artifact_id)
            if current is None or artifact.version > current.version:
                latest[artifact.artifact_id] = artifact
        return list(latest.values())

    def get_artifact(
        self,
        artifact_id: str,
        *,
        version_id: str | None = None,
    ) -> PromotedSkillArtifact | None:
        matches = [
            artifact
            for artifact in self.iter_artifacts()
            if artifact.artifact_id == str(artifact_id)
            and (version_id is None or artifact.version_id == str(version_id))
        ]
        if not matches:
            return None
        return max(matches, key=lambda artifact: artifact.version)

    def put_activation(
        self,
        activation: SkillArtifactActivation,
    ) -> SkillArtifactActivation:
        if not isinstance(activation, SkillArtifactActivation):
            raise TypeError(
                "activation must be SkillArtifactActivation, "
                f"got {type(activation).__name__}"
            )
        _append_jsonl(self.activation_log_path, activation.to_record())
        return activation

    def iter_activations(self) -> list[SkillArtifactActivation]:
        return [
            SkillArtifactActivation(**record)
            for record in _read_jsonl(self.activation_log_path)
        ]


def build_promoted_skill_artifact(
    *,
    skill_path: str | Path,
    scope: str,
    activation_rule: Mapping[str, Any],
    evidence_bundle_id: str,
    gate_decision_id: str,
    skill_name: str | None = None,
    skill_slug: str | None = None,
    artifact_id: str | None = None,
    version: int = 1,
    trust_state: ArtifactTrustState | str = ArtifactTrustState.ACTIVE,
) -> PromotedSkillArtifact:
    payload_path = Path(skill_path)
    content = read_skill_payload(payload_path)
    digest = skill_content_hash(content)
    resolved_artifact_id = artifact_id or f"skill_artifact_{uuid.uuid4().hex}"
    resolved_version = int(version)
    return PromotedSkillArtifact(
        artifact_id=resolved_artifact_id,
        version_id=f"{resolved_artifact_id}:v{resolved_version}",
        version=resolved_version,
        scope=scope,
        activation_rule=activation_rule,
        skill_name=skill_name or payload_path.parent.name,
        skill_slug=skill_slug or payload_path.parent.name,
        skill_path=str(payload_path),
        content_hash=digest,
        payload_ref=f"sha256:{digest}",
        evidence_bundle_id=evidence_bundle_id,
        gate_decision_id=gate_decision_id,
        trust_state=trust_state,
    )


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(stable_json_dumps(record))
        fh.write("\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise SkillArtifactError(f"invalid JSONL in {path}:{line_no}: {exc}") from exc
            if not isinstance(value, dict):
                raise SkillArtifactError(f"JSONL record in {path}:{line_no} is not an object")
            rows.append(value)
    return rows


def _stable_record(value: Any) -> dict[str, Any]:
    return json.loads(stable_json_dumps(value))


def _normalize_hash(value: str) -> str:
    text = str(value).strip()
    if text.startswith("sha256:"):
        text = text[len("sha256:"):]
    if len(text) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in text):
        raise SkillArtifactError("content hashes must be sha256 hex digests")
    return text.lower()


def _bounded_preview(content: str, *, limit: int) -> str:
    text = str(content)
    return text[:limit]


__all__ = [
    "JSONLSkillArtifactStore",
    "PromotedSkillArtifact",
    "SKILL_ACTIVATIONS_FILENAME",
    "SKILL_ARTIFACTS_FILENAME",
    "SkillArtifactActivation",
    "SkillArtifactError",
    "build_promoted_skill_artifact",
    "default_skill_activation_log_path",
    "default_skill_artifact_store_path",
    "read_skill_payload",
    "skill_content_hash",
]
