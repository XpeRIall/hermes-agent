"""Nova Phase 1 mutation policy inventory and gate helpers.

This module classifies future-affecting mutation surfaces and evaluates a
minimal policy decision. It does not install hooks, replace existing
terminal/file approvals, or mutate trusted state. The only side effect is an
optional append to a caller-supplied Nova ledger.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

from agent.nova.evidence import MissingEvidenceError, require_evidence_refs
from agent.nova.kernel import (
    ArtifactProposal,
    EvidenceBundle,
    EvidenceRefKind,
    LedgerEntryKind,
    PolicyDecision,
    PolicyDecisionAction,
    stable_hash,
    tool_args_hash,
)
from agent.nova.ledger import AppendOnlyLedger


class MutationSurface(StrEnum):
    """Persistent or future-affecting Hermes mutation surface."""

    MEMORY = "memory"
    SKILLS = "skills"
    PROVIDERS = "providers"
    PLUGINS = "plugins"
    BACKGROUND_REVIEW = "background_review"
    CRON = "cron"
    CONFIG = "config"
    SESSION = "session"
    CHECKPOINT = "checkpoint"
    PROMPT_CONTEXT = "prompt_context"
    TERMINAL = "terminal"
    FILE_TOOL = "file_tool"


class MutationOperation(StrEnum):
    """Coarse operation family used for policy metadata."""

    READ = "read"
    WRITE = "write"
    PATCH = "patch"
    DELETE = "delete"
    EXECUTE = "execute"
    SYNC = "sync"
    CONFIGURE = "configure"
    ACTIVATE = "activate"
    CHECKPOINT = "checkpoint"
    UNKNOWN = "unknown"


class PolicyViolationError(ValueError):
    """Raised by trusted-state guard helpers when policy evidence is missing."""


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _dict_copy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"metadata must be a mapping, got {type(value).__name__}")
    return dict(value)


def _tuple_of_str(values: Iterable[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values)


def _tuple_of_evidence_kinds(
    values: Iterable[EvidenceRefKind | str] | None,
) -> tuple[EvidenceRefKind, ...]:
    if values is None:
        return ()
    return tuple(EvidenceRefKind(value) for value in values)


@dataclass(frozen=True)
class MutationSurfacePolicy:
    """Static Phase 1 policy for one future-affecting mutation surface."""

    surface: MutationSurface
    default_action: PolicyDecisionAction
    description: str
    known_paths: tuple[str, ...] = ()
    known_operations: tuple[str, ...] = ()
    required_evidence_for_trusted_write: tuple[EvidenceRefKind, ...] = ()
    existing_authority: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "surface", MutationSurface(self.surface))
        object.__setattr__(self, "default_action", PolicyDecisionAction(self.default_action))
        object.__setattr__(self, "known_paths", _tuple_of_str(self.known_paths))
        object.__setattr__(self, "known_operations", _tuple_of_str(self.known_operations))
        object.__setattr__(
            self,
            "required_evidence_for_trusted_write",
            _tuple_of_evidence_kinds(self.required_evidence_for_trusted_write),
        )


MUTATION_SURFACE_POLICIES: dict[MutationSurface, MutationSurfacePolicy] = {
    MutationSurface.MEMORY: MutationSurfacePolicy(
        surface=MutationSurface.MEMORY,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Built-in memory writes and external memory-provider mirrors.",
        known_paths=("tools/memory_tool.py", "agent/memory_manager.py", "plugins/memory/"),
        known_operations=("add", "update", "remove", "sync_turn", "on_memory_write"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.TOOL_RESULT),
    ),
    MutationSurface.SKILLS: MutationSurfacePolicy(
        surface=MutationSurface.SKILLS,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Skill create, edit, patch, support-file, and delete operations.",
        known_paths=("tools/skill_manager_tool.py", "skills/", "optional-skills/"),
        known_operations=("create", "edit", "patch", "delete", "write_file", "remove_file"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.TOOL_RESULT),
    ),
    MutationSurface.PROVIDERS: MutationSurfacePolicy(
        surface=MutationSurface.PROVIDERS,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Model-provider profiles, routing, and provider plugin changes.",
        known_paths=("providers/", "plugins/model-providers/", "hermes_cli/providers.py"),
        known_operations=("register_provider", "switch_provider", "configure_provider"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.FILE),
    ),
    MutationSurface.PLUGINS: MutationSurfacePolicy(
        surface=MutationSurface.PLUGINS,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="General plugin installation, manifests, hooks, and registered tools.",
        known_paths=("hermes_cli/plugins.py", "plugins/", ".hermes/plugins/"),
        known_operations=("install", "enable", "disable", "register_tool", "invoke_hook"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.FILE),
    ),
    MutationSurface.BACKGROUND_REVIEW: MutationSurfacePolicy(
        surface=MutationSurface.BACKGROUND_REVIEW,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Background reviewer memory and skill writes after a turn.",
        known_paths=("agent/background_review.py",),
        known_operations=("memory", "skill_manage", "review_write"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.TOOL_RESULT),
    ),
    MutationSurface.CRON: MutationSurfacePolicy(
        surface=MutationSurface.CRON,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Scheduled unattended jobs and cron-delivered writes.",
        known_paths=("cron/", "agent/prompt_builder.py"),
        known_operations=("schedule", "run_job", "approve_mode", "deliver_result"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.COMMAND),
    ),
    MutationSurface.CONFIG: MutationSurfacePolicy(
        surface=MutationSurface.CONFIG,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Config writes that alter future models, tools, gateways, or approvals.",
        known_paths=("~/.hermes/config.yaml", "cli.py", "hermes_cli/config.py"),
        known_operations=("save_config_value", "model_global", "setup", "config_set"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.FILE),
    ),
    MutationSurface.SESSION: MutationSurfacePolicy(
        surface=MutationSurface.SESSION,
        default_action=PolicyDecisionAction.SHADOW,
        description="Session messages, titles, branch metadata, and searchable history.",
        known_paths=("hermes_state.py",),
        known_operations=("create_session", "add_message", "set_session_title", "delete_session"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE,),
    ),
    MutationSurface.CHECKPOINT: MutationSurfacePolicy(
        surface=MutationSurface.CHECKPOINT,
        default_action=PolicyDecisionAction.SHADOW,
        description="Filesystem checkpoints, rollback metadata, restore, and pruning.",
        known_paths=("tools/checkpoint_manager.py", "~/.hermes/checkpoints/"),
        known_operations=("ensure_checkpoint", "restore", "prune", "clear"),
        required_evidence_for_trusted_write=(EvidenceRefKind.COMMAND, EvidenceRefKind.FILE),
    ),
    MutationSurface.PROMPT_CONTEXT: MutationSurfacePolicy(
        surface=MutationSurface.PROMPT_CONTEXT,
        default_action=PolicyDecisionAction.CONVERT_TO_PROPOSAL,
        description="Prompt/context files and snapshots that influence later runs.",
        known_paths=(
            "AGENTS.md",
            "CLAUDE.md",
            "SOUL.md",
            ".hermes.md",
            ".cursor/rules/",
            "agent/prompt_builder.py",
        ),
        known_operations=("context_load", "activate_context", "write_context_file"),
        required_evidence_for_trusted_write=(EvidenceRefKind.MESSAGE, EvidenceRefKind.FILE),
    ),
    MutationSurface.TERMINAL: MutationSurfacePolicy(
        surface=MutationSurface.TERMINAL,
        default_action=PolicyDecisionAction.SHADOW,
        description="Terminal commands that may mutate future agent behavior.",
        known_paths=("tools/terminal_tool.py", "tools/approval.py", "agent/tool_executor.py"),
        known_operations=("terminal", "execute_code", "shell_write"),
        required_evidence_for_trusted_write=(EvidenceRefKind.COMMAND,),
        existing_authority="tools.approval dangerous-command approval remains authoritative",
    ),
    MutationSurface.FILE_TOOL: MutationSurfacePolicy(
        surface=MutationSurface.FILE_TOOL,
        default_action=PolicyDecisionAction.SHADOW,
        description="write_file and patch operations not classified to a narrower surface.",
        known_paths=("tools/file_tools.py", "agent/tool_executor.py"),
        known_operations=("write_file", "patch"),
        required_evidence_for_trusted_write=(EvidenceRefKind.FILE,),
        existing_authority="tools.file_tools and checkpoint approval behavior remains authoritative",
    ),
}


@dataclass(frozen=True)
class MutationRequest:
    """One candidate future-affecting mutation to evaluate."""

    run_id: str
    surface: MutationSurface
    operation: MutationOperation | str
    subject_ref: str
    actor: str = "assistant"
    tool_name: str | None = None
    args: Mapping[str, Any] = field(default_factory=dict)
    future_affecting: bool = True
    direct_trusted_state: bool = False
    requested_action: PolicyDecisionAction | str | None = None
    candidate_payload_ref: str | None = None
    scope: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: _new_id("mut"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", str(self.run_id))
        object.__setattr__(self, "surface", MutationSurface(self.surface))
        object.__setattr__(self, "operation", _normalize_operation(self.operation))
        object.__setattr__(self, "subject_ref", str(self.subject_ref))
        object.__setattr__(self, "actor", str(self.actor))
        if self.tool_name is not None:
            object.__setattr__(self, "tool_name", str(self.tool_name))
        if not isinstance(self.args, Mapping):
            object.__setattr__(self, "args", {})
        else:
            object.__setattr__(self, "args", dict(self.args))
        if self.requested_action is not None:
            object.__setattr__(
                self,
                "requested_action",
                PolicyDecisionAction(self.requested_action),
            )
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))
        object.__setattr__(self, "id", str(self.id))

    @property
    def args_hash(self) -> str:
        return tool_args_hash(self.args)


@dataclass(frozen=True)
class PolicyGateResult:
    """Result of evaluating one mutation request."""

    request: MutationRequest
    decision: PolicyDecision
    proposal: ArtifactProposal | None = None
    ledger_entry_ids: tuple[str, ...] = ()
    reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ledger_entry_ids",
            _tuple_of_str(self.ledger_entry_ids),
        )

    @property
    def allowed(self) -> bool:
        return self.decision.action is PolicyDecisionAction.ALLOW

    @property
    def blocked(self) -> bool:
        return self.decision.action is PolicyDecisionAction.BLOCK

    @property
    def shadowed(self) -> bool:
        return self.decision.action is PolicyDecisionAction.SHADOW

    @property
    def converted_to_proposal(self) -> bool:
        return self.decision.action is PolicyDecisionAction.CONVERT_TO_PROPOSAL


def mutation_surface_inventory() -> tuple[MutationSurfacePolicy, ...]:
    """Return the static Phase 1 inventory in enum order."""

    return tuple(MUTATION_SURFACE_POLICIES[surface] for surface in MutationSurface)


def policy_for_surface(surface: MutationSurface | str) -> MutationSurfacePolicy:
    """Return the static policy for a known mutation surface."""

    return MUTATION_SURFACE_POLICIES[MutationSurface(surface)]


def classify_tool_mutation(
    tool_name: str,
    args: Mapping[str, Any] | None = None,
    *,
    run_id: str = "",
    actor: str = "assistant",
    subject_ref: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> MutationRequest | None:
    """Classify known Hermes tool calls into Nova mutation surfaces.

    Read-only tools return ``None``. Terminal and file-tool classifications are
    for shadow/policy recording only; this helper does not approve, block, or
    sandbox those tools.
    """

    tool = str(tool_name)
    tool_args = dict(args or {})
    merged_metadata = _dict_copy(metadata)

    if tool in {"read_file", "search_files", "skill_view", "memory_search", "session_search"}:
        return None
    if tool == "memory":
        action = str(tool_args.get("action") or "write").lower()
        return MutationRequest(
            run_id=run_id,
            surface=MutationSurface.MEMORY,
            operation=_operation_from_action(action),
            subject_ref=subject_ref or f"memory:{tool_args.get('target', 'memory')}",
            actor=actor,
            tool_name=tool,
            args=tool_args,
            metadata=merged_metadata,
        )
    if tool == "skill_manage":
        action = str(tool_args.get("action") or "write").lower()
        name = str(tool_args.get("name") or "unknown")
        return MutationRequest(
            run_id=run_id,
            surface=MutationSurface.SKILLS,
            operation=_operation_from_action(action),
            subject_ref=subject_ref or f"skill:{name}",
            actor=actor,
            tool_name=tool,
            args=tool_args,
            metadata=merged_metadata,
        )
    if tool in {"write_file", "patch"}:
        path = _path_from_file_tool_args(tool, tool_args)
        surface = classify_path_surface(path) or MutationSurface.FILE_TOOL
        action = "patch" if tool == "patch" else "write"
        return MutationRequest(
            run_id=run_id,
            surface=surface,
            operation=_operation_from_action(action),
            subject_ref=subject_ref or f"file:{path or 'unknown'}",
            actor=actor,
            tool_name=tool,
            args=tool_args,
            metadata={
                **merged_metadata,
                "path": path or "",
                "classified_by": "file_tool_path",
            },
        )
    if tool in {"terminal", "execute_code"}:
        command = str(tool_args.get("command") or tool_args.get("code") or "")
        return MutationRequest(
            run_id=run_id,
            surface=MutationSurface.TERMINAL,
            operation=MutationOperation.EXECUTE,
            subject_ref=subject_ref or f"terminal:{stable_hash(command)[:16]}",
            actor=actor,
            tool_name=tool,
            args=tool_args,
            metadata={
                **merged_metadata,
                "existing_approval_authority": policy_for_surface(
                    MutationSurface.TERMINAL
                ).existing_authority,
            },
        )
    return None


def classify_path_surface(path: str | None) -> MutationSurface | None:
    """Classify a path that may affect later Hermes/Nova behavior."""

    if not path:
        return None
    normalized = _normalize_path(path)
    name = PurePosixPath(normalized).name.lower()

    if normalized.startswith(("skills/", "optional-skills/")) or "/skills/" in normalized:
        return MutationSurface.SKILLS
    if normalized.startswith("plugins/model-providers/") or "/model-providers/" in normalized:
        return MutationSurface.PROVIDERS
    if normalized.startswith((".hermes/plugins/", "plugins/")) or "/plugins/" in normalized:
        return MutationSurface.PLUGINS
    if normalized.startswith(("providers/",)) or "/providers/" in normalized:
        return MutationSurface.PROVIDERS
    if normalized.startswith(("cron/",)) or "/cron/" in normalized:
        return MutationSurface.CRON
    if normalized.endswith("config.yaml") or normalized.endswith("config.toml"):
        return MutationSurface.CONFIG
    if normalized in {"agents.md", "claude.md", "soul.md", ".hermes.md"}:
        return MutationSurface.PROMPT_CONTEXT
    if name in {"agents.md", "claude.md", "soul.md", ".hermes.md"}:
        return MutationSurface.PROMPT_CONTEXT
    if normalized.startswith(".cursor/rules/") or "/.cursor/rules/" in normalized:
        return MutationSurface.PROMPT_CONTEXT
    if "prompt_builder.py" in normalized or "context_engine" in normalized:
        return MutationSurface.PROMPT_CONTEXT
    if "checkpoint" in normalized:
        return MutationSurface.CHECKPOINT
    return None


def gate_mutation(
    request: MutationRequest,
    *,
    evidence_bundle: EvidenceBundle | None = None,
    ledger: AppendOnlyLedger | None = None,
    reason: str | None = None,
    now: float | None = None,
) -> PolicyGateResult:
    """Evaluate a Phase 1 policy gate for a mutation request.

    The gate is conservative: shadow-only records may lack evidence, but
    proposal conversion and allowed trusted writes require evidence. Passing a
    ledger records the policy decision, and proposal conversions also record a
    ``proposal.attempt`` entry.
    """

    if not isinstance(request, MutationRequest):
        raise TypeError(f"request must be MutationRequest, got {type(request).__name__}")

    policy = policy_for_surface(request.surface)
    action = request.requested_action or (
        policy.default_action if request.future_affecting else PolicyDecisionAction.ALLOW
    )
    resolved_reason = reason or _default_reason(request, policy, action)
    validated_bundle = evidence_bundle

    try:
        if (
            request.direct_trusted_state
            or action is PolicyDecisionAction.CONVERT_TO_PROPOSAL
            or (action is PolicyDecisionAction.ALLOW and request.future_affecting)
        ):
            validated_bundle = require_evidence_refs(
                evidence_bundle,
                policy.required_evidence_for_trusted_write,
            )
    except MissingEvidenceError as exc:
        action = PolicyDecisionAction.BLOCK
        resolved_reason = f"{resolved_reason}; blocked: {exc}"
        validated_bundle = evidence_bundle

    decision = PolicyDecision(
        id=_new_id("pol"),
        run_id=request.run_id,
        action=action,
        subject_ref=request.subject_ref,
        reason=resolved_reason,
        evidence_bundle_id=validated_bundle.id if validated_bundle is not None else None,
        created_at=time.time() if now is None else float(now),
    )

    proposal = None
    if action is PolicyDecisionAction.CONVERT_TO_PROPOSAL:
        proposal = _build_proposal(request, validated_bundle)

    ledger_entry_ids = ()
    if ledger is not None:
        ledger_entry_ids = _record_policy_result(
            ledger=ledger,
            request=request,
            policy=policy,
            decision=decision,
            proposal=proposal,
            evidence_bundle=validated_bundle,
        )

    return PolicyGateResult(
        request=request,
        decision=decision,
        proposal=proposal,
        ledger_entry_ids=ledger_entry_ids,
        reason=resolved_reason,
    )


def require_trusted_state_gate(
    *,
    decision: PolicyDecision | None,
    evidence_bundle: EvidenceBundle | None,
    required_kinds: Iterable[EvidenceRefKind | str] = (),
) -> PolicyDecision:
    """Fail closed before an integration performs direct trusted-state mutation."""

    if decision is None:
        raise PolicyViolationError("trusted-state mutation requires a policy decision")
    if decision.action is not PolicyDecisionAction.ALLOW:
        raise PolicyViolationError(
            f"trusted-state mutation requires allow decision, got {decision.action.value}"
        )
    bundle = require_evidence_refs(evidence_bundle, required_kinds)
    if decision.evidence_bundle_id != bundle.id:
        raise PolicyViolationError("policy decision does not cite the evidence bundle")
    return decision


def _record_policy_result(
    *,
    ledger: AppendOnlyLedger,
    request: MutationRequest,
    policy: MutationSurfacePolicy,
    decision: PolicyDecision,
    proposal: ArtifactProposal | None,
    evidence_bundle: EvidenceBundle | None,
) -> tuple[str, ...]:
    entry_ids: list[str] = []
    policy_entry = ledger.append_event(
        request.run_id,
        LedgerEntryKind.POLICY_DECISION,
        actor="kernel",
        subject_ref=request.subject_ref,
        args_hash=request.args_hash,
        evidence_bundle_id=evidence_bundle.id if evidence_bundle is not None else None,
        policy_decision_id=decision.id,
        metadata={
            "request_id": request.id,
            "surface": request.surface.value,
            "operation": request.operation.value,
            "tool_name": request.tool_name or "",
            "action": decision.action.value,
            "reason": decision.reason,
            "future_affecting": bool(request.future_affecting),
            "direct_trusted_state": bool(request.direct_trusted_state),
            "existing_authority": policy.existing_authority or "",
            "args_keys": sorted(str(key) for key in request.args.keys()),
            "request_metadata": request.metadata,
        },
    )
    if policy_entry is not None:
        entry_ids.append(policy_entry.id)

    if proposal is not None:
        proposal_entry = ledger.append_event(
            request.run_id,
            LedgerEntryKind.PROPOSAL_ATTEMPT,
            actor=request.actor,
            subject_ref=proposal.id,
            evidence_bundle_id=proposal.evidence_bundle_id,
            policy_decision_id=decision.id,
            payload_ref=proposal.candidate_payload_ref,
            parent_seq=policy_entry.seq if policy_entry is not None else None,
            metadata={
                "request_id": request.id,
                "originating_subject_ref": request.subject_ref,
                "artifact_type": proposal.artifact_type,
                "scope": proposal.scope,
                "surface": request.surface.value,
                "operation": request.operation.value,
                "status": proposal.status.value,
            },
        )
        if proposal_entry is not None:
            entry_ids.append(proposal_entry.id)

    return tuple(entry_ids)


def _build_proposal(
    request: MutationRequest,
    evidence_bundle: EvidenceBundle | None,
) -> ArtifactProposal:
    if evidence_bundle is None:
        raise PolicyViolationError("proposal conversion requires evidence")
    return ArtifactProposal(
        id=_new_id("proposal"),
        artifact_type=request.surface.value,
        scope=request.scope or request.subject_ref,
        candidate_payload_ref=request.candidate_payload_ref or _candidate_payload_ref(request),
        evidence_bundle_id=evidence_bundle.id,
        originating_run_id=request.run_id,
        proposed_by=request.actor,
    )


def _candidate_payload_ref(request: MutationRequest) -> str:
    digest = stable_hash(
        {
            "request_id": request.id,
            "surface": request.surface.value,
            "operation": request.operation.value,
            "subject_ref": request.subject_ref,
            "tool_name": request.tool_name,
            "args_hash": request.args_hash,
        }
    )
    return f"sha256:{digest}"


def _default_reason(
    request: MutationRequest,
    policy: MutationSurfacePolicy,
    action: PolicyDecisionAction,
) -> str:
    if request.direct_trusted_state and action is not PolicyDecisionAction.BLOCK:
        return "direct trusted-state mutation requires evidence and an allow decision"
    if action is PolicyDecisionAction.CONVERT_TO_PROPOSAL:
        return f"{request.surface.value} mutation is future-affecting; convert to proposal"
    if action is PolicyDecisionAction.SHADOW:
        if policy.existing_authority:
            return f"{request.surface.value} mutation is shadow-recorded; {policy.existing_authority}"
        return f"{request.surface.value} mutation is shadow-recorded"
    if action is PolicyDecisionAction.ALLOW:
        return f"{request.surface.value} mutation allowed by policy"
    return f"{request.surface.value} mutation blocked by policy"


def _operation_from_action(action: str) -> MutationOperation:
    normalized = str(action or "").strip().lower()
    if normalized in {"add", "create", "write", "write_file", "save", "set"}:
        return MutationOperation.WRITE
    if normalized in {"edit", "patch", "update", "replace"}:
        return MutationOperation.PATCH
    if normalized in {"delete", "remove", "remove_file", "clear"}:
        return MutationOperation.DELETE
    if normalized in {"sync", "sync_turn", "mirror", "on_memory_write"}:
        return MutationOperation.SYNC
    if normalized in {"run", "execute", "terminal", "execute_code"}:
        return MutationOperation.EXECUTE
    if normalized in {"configure", "config", "enable", "disable", "install"}:
        return MutationOperation.CONFIGURE
    if normalized in {"activate", "activation"}:
        return MutationOperation.ACTIVATE
    if normalized in {"checkpoint", "restore", "prune"}:
        return MutationOperation.CHECKPOINT
    return MutationOperation.UNKNOWN


def _normalize_operation(operation: MutationOperation | str) -> MutationOperation:
    if isinstance(operation, MutationOperation):
        return operation
    try:
        return MutationOperation(str(operation))
    except ValueError:
        return _operation_from_action(str(operation))


def _path_from_file_tool_args(tool_name: str, args: Mapping[str, Any]) -> str:
    if tool_name == "write_file":
        return str(args.get("path") or "")
    if str(args.get("mode") or "replace") == "replace":
        return str(args.get("path") or "")
    patch = str(args.get("patch") or "")
    match = re.search(
        r"^\*\*\*\s+(?:Add|Update|Delete)\s+File:\s*(.+)$",
        patch,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def _normalize_path(path: str) -> str:
    normalized = str(path).strip().replace("\\", "/")
    normalized = re.sub(r"^[a-zA-Z]:", "", normalized).lstrip("/")
    return normalized.lower()
