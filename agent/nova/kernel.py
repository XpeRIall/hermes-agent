"""Typed Nova trusted-kernel model skeleton.

The objects in this module model the kernel boundary only. They do not install
hooks, mutate Hermes runtime behavior, or make trust decisions on their own.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import StrEnum
from typing import Any, Iterable, Mapping


class KernelMode(StrEnum):
    """Runtime posture for future Nova integration."""

    DISABLED = "disabled"
    SHADOW = "shadow"


class LedgerEntryKind(StrEnum):
    """Stable append-only ledger entry kinds for Phase 1."""

    RUN_STARTED = "run.started"
    RUN_ENDED = "run.ended"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    POLICY_DECISION = "policy.decision"
    PROPOSAL_ATTEMPT = "proposal.attempt"
    ACTIVATION_SNAPSHOT = "activation.snapshot"
    OUTCOME = "outcome"


class EvidenceRefKind(StrEnum):
    """Compact evidence reference families."""

    MESSAGE = "message"
    FILE = "file"
    COMMAND = "command"
    TOOL_RESULT = "tool_result"
    CHECK = "check"
    RETRIEVAL = "retrieval"
    APPROVAL = "approval"


class ClaimStatus(StrEnum):
    """Trust states for typed claims and reusable state."""

    PROPOSED = "proposed"
    REJECTED = "rejected"
    STAGED = "staged"
    ACTIVE = "active"
    DEMOTED = "demoted"
    INVALIDATED = "invalidated"


class PolicyDecisionAction(StrEnum):
    """Policy outcomes for future-affecting writes."""

    ALLOW = "allow"
    SHADOW = "shadow"
    BLOCK = "block"
    CONVERT_TO_PROPOSAL = "convert_to_proposal"


class GateResult(StrEnum):
    """Verification gate outcomes."""

    PASS = "pass"
    FAIL = "fail"
    NEEDS_REVIEW = "needs_review"
    BLOCKED = "blocked"


class ProposalStatus(StrEnum):
    """Lifecycle states for untrusted artifact proposals."""

    PROPOSED = "proposed"
    REJECTED = "rejected"
    STAGED = "staged"
    ACTIVE = "active"


class ArtifactTrustState(StrEnum):
    """Trust states for artifact versions."""

    UNTRUSTED = "untrusted"
    STAGED = "staged"
    ACTIVE = "active"
    DEMOTED = "demoted"


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _tuple_of_str(values: Iterable[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values)


def _tuple_of_refs(values: Iterable["EvidenceRef"] | None) -> tuple["EvidenceRef", ...]:
    if values is None:
        return ()
    return tuple(values)


def _dict_copy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"metadata must be a mapping, got {type(value).__name__}")
    return dict(value)


def _jsonable(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    return value


def stable_json_dumps(value: Any) -> str:
    """Return deterministic compact JSON for hashing and storage."""

    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def stable_hash(value: Any) -> str:
    """Return a stable SHA-256 hash for JSON-compatible data."""

    return hashlib.sha256(stable_json_dumps(value).encode("utf-8")).hexdigest()


def tool_args_hash(args: Mapping[str, Any] | None) -> str:
    """Hash tool arguments without storing the raw argument payload."""

    if args is None:
        args = {}
    if not isinstance(args, Mapping):
        raise TypeError(f"tool args must be a mapping, got {type(args).__name__}")
    return stable_hash(_redact_for_hash(args))


_SENSITIVE_HASH_KEYS = {
    "accesstoken",
    "apikey",
    "authorization",
    "authorizationheader",
    "authtoken",
    "bearer",
    "clientsecret",
    "credential",
    "credentials",
    "idtoken",
    "keymaterial",
    "password",
    "passwd",
    "rawsecret",
    "refreshtoken",
    "secret",
    "secretinput",
    "secretvalue",
    "token",
}


def _redact_for_hash(value: Any, *, key: str | None = None) -> Any:
    if key is not None and _is_sensitive_hash_key(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): _redact_for_hash(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_for_hash(item) for item in value]
    if isinstance(value, str):
        try:
            from agent.redact import redact_sensitive_text
            return redact_sensitive_text(value, force=True)
        except Exception:
            return value
    return value


def _is_sensitive_hash_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    if normalized in _SENSITIVE_HASH_KEYS:
        return True
    return normalized.endswith(("apikey", "token", "secret", "password", "passwd"))


@dataclass(frozen=True)
class EvidenceRef:
    """Pointer to evidence without embedding unbounded raw payloads."""

    kind: EvidenceRefKind
    ref: str
    digest: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", EvidenceRefKind(self.kind))
        object.__setattr__(self, "ref", str(self.ref))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))


@dataclass(frozen=True)
class EvidenceBundle:
    """Auditable evidence refs associated with a run, claim, or proposal."""

    run_id: str
    id: str = field(default_factory=lambda: _new_id("evb"))
    message_refs: tuple[EvidenceRef, ...] = ()
    file_refs: tuple[EvidenceRef, ...] = ()
    command_refs: tuple[EvidenceRef, ...] = ()
    tool_result_refs: tuple[EvidenceRef, ...] = ()
    check_refs: tuple[EvidenceRef, ...] = ()
    retrieval_refs: tuple[EvidenceRef, ...] = ()
    approval_refs: tuple[EvidenceRef, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", str(self.run_id))
        object.__setattr__(self, "message_refs", _tuple_of_refs(self.message_refs))
        object.__setattr__(self, "file_refs", _tuple_of_refs(self.file_refs))
        object.__setattr__(self, "command_refs", _tuple_of_refs(self.command_refs))
        object.__setattr__(self, "tool_result_refs", _tuple_of_refs(self.tool_result_refs))
        object.__setattr__(self, "check_refs", _tuple_of_refs(self.check_refs))
        object.__setattr__(self, "retrieval_refs", _tuple_of_refs(self.retrieval_refs))
        object.__setattr__(self, "approval_refs", _tuple_of_refs(self.approval_refs))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))

    @property
    def refs(self) -> tuple[EvidenceRef, ...]:
        """Return all refs in stable family order."""

        return (
            self.message_refs
            + self.file_refs
            + self.command_refs
            + self.tool_result_refs
            + self.check_refs
            + self.retrieval_refs
            + self.approval_refs
        )

    def has_refs(self, *kinds: EvidenceRefKind | str) -> bool:
        """Return True when the bundle contains at least one ref for each kind."""

        required = {EvidenceRefKind(kind) for kind in kinds}
        present = {ref.kind for ref in self.refs}
        return required.issubset(present)


@dataclass(frozen=True)
class RunLedgerEntry:
    """Single append-only causal ledger entry.

    ``seq`` is unique per run. Sequential execution appends monotonically.
    Concurrent execution should reserve a contiguous sequence range before
    launching workers, then append with the reserved sequence numbers in the
    original model/tool-call order. Replay is always ordered by ``seq``.
    """

    run_id: str
    seq: int
    kind: LedgerEntryKind
    id: str = field(default_factory=lambda: _new_id("rle"))
    actor: str = "kernel"
    subject_ref: str | None = None
    args_hash: str | None = None
    evidence_bundle_id: str | None = None
    policy_decision_id: str | None = None
    payload_ref: str | None = None
    parent_seq: int | None = None
    batch_id: str | None = None
    batch_index: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if int(self.seq) < 1:
            raise ValueError("ledger sequence numbers start at 1")
        if self.parent_seq is not None and int(self.parent_seq) < 1:
            raise ValueError("parent_seq must be positive when set")
        if self.batch_index is not None and int(self.batch_index) < 0:
            raise ValueError("batch_index must be non-negative when set")
        object.__setattr__(self, "run_id", str(self.run_id))
        object.__setattr__(self, "seq", int(self.seq))
        object.__setattr__(self, "kind", LedgerEntryKind(self.kind))
        object.__setattr__(self, "actor", str(self.actor))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))


@dataclass(frozen=True)
class ToolLedgerSlot:
    """Reserved ledger slots for one tool call inside a batch."""

    tool_call_id: str
    batch_id: str
    batch_index: int
    call_seq: int
    result_seq: int

    def __post_init__(self) -> None:
        if self.batch_index < 0:
            raise ValueError("batch_index must be non-negative")
        if self.call_seq < 1 or self.result_seq < 1:
            raise ValueError("tool ledger sequences must be positive")
        object.__setattr__(self, "tool_call_id", str(self.tool_call_id))
        object.__setattr__(self, "batch_id", str(self.batch_id))


@dataclass(frozen=True)
class ToolLedgerBatchPlan:
    """Deterministic sequence plan for sequential or concurrent tool calls.

    For a batch of N tool calls, call entries receive ``first_seq`` through
    ``first_seq + N - 1`` in the model's tool-call order. Result entries receive
    the following N sequence numbers in the same order. This makes replay stable
    even when worker threads finish out of order.
    """

    run_id: str
    batch_id: str
    slots: tuple[ToolLedgerSlot, ...]

    @classmethod
    def from_tool_call_ids(
        cls,
        run_id: str,
        tool_call_ids: Iterable[str],
        first_seq: int,
        batch_id: str | None = None,
    ) -> "ToolLedgerBatchPlan":
        ids = tuple(str(tool_call_id) for tool_call_id in tool_call_ids)
        if int(first_seq) < 1:
            raise ValueError("first_seq must be positive")
        resolved_batch_id = batch_id or _new_id("toolbatch")
        total = len(ids)
        slots = tuple(
            ToolLedgerSlot(
                tool_call_id=tool_call_id,
                batch_id=resolved_batch_id,
                batch_index=index,
                call_seq=int(first_seq) + index,
                result_seq=int(first_seq) + total + index,
            )
            for index, tool_call_id in enumerate(ids)
        )
        return cls(run_id=str(run_id), batch_id=resolved_batch_id, slots=slots)

    @property
    def reserved_count(self) -> int:
        return len(self.slots) * 2

    def slot_for(self, tool_call_id: str) -> ToolLedgerSlot:
        for slot in self.slots:
            if slot.tool_call_id == tool_call_id:
                return slot
        raise KeyError(tool_call_id)


@dataclass(frozen=True)
class PolicyDecision:
    id: str
    run_id: str
    action: PolicyDecisionAction
    subject_ref: str
    reason: str = ""
    evidence_bundle_id: str | None = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", PolicyDecisionAction(self.action))


@dataclass(frozen=True)
class GateDecision:
    id: str
    proposal_id: str
    gate_type: str
    result: GateResult
    reviewer_or_eval_id: str
    reason: str = ""
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "result", GateResult(self.result))


@dataclass(frozen=True)
class TypedClaim:
    id: str
    claim_type: str
    scope: str
    statement: str
    status: ClaimStatus
    evidence_bundle_id: str
    created_from: str
    gate_decision_id: str | None = None
    invalidated_by: str | None = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ClaimStatus(self.status))


@dataclass(frozen=True)
class ArtifactProposal:
    id: str
    artifact_type: str
    scope: str
    candidate_payload_ref: str
    evidence_bundle_id: str
    originating_run_id: str
    proposed_by: str
    status: ProposalStatus = ProposalStatus.PROPOSED
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ProposalStatus(self.status))


@dataclass(frozen=True)
class ArtifactVersion:
    artifact_id: str
    version: int
    payload_ref: str
    trust_state: ArtifactTrustState
    activation_rule: str
    evidence_bundle_id: str
    parent_version: int | None = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if int(self.version) < 1:
            raise ValueError("artifact versions start at 1")
        if self.parent_version is not None and int(self.parent_version) < 1:
            raise ValueError("parent_version must be positive when set")
        object.__setattr__(self, "version", int(self.version))
        object.__setattr__(self, "trust_state", ArtifactTrustState(self.trust_state))


@dataclass(frozen=True)
class ActivationSnapshot:
    id: str
    run_id: str
    artifact_version_ids: tuple[str, ...]
    activation_context_hash: str
    policy_snapshot_id: str
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_version_ids", _tuple_of_str(self.artifact_version_ids))


@dataclass(frozen=True)
class RunOutcome:
    id: str
    run_id: str
    checks_run: tuple[str, ...] = ()
    checks_passed: tuple[str, ...] = ()
    regressions: tuple[str, ...] = ()
    reviewer_feedback_refs: tuple[str, ...] = ()
    diff_summary_ref: str | None = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks_run", _tuple_of_str(self.checks_run))
        object.__setattr__(self, "checks_passed", _tuple_of_str(self.checks_passed))
        object.__setattr__(self, "regressions", _tuple_of_str(self.regressions))
        object.__setattr__(
            self,
            "reviewer_feedback_refs",
            _tuple_of_str(self.reviewer_feedback_refs),
        )
