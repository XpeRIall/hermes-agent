"""Schema-only Nova substrate proposal and artifact records.

This module defines the Phase 1 substrate seam as inert data. Importing it does
not enable activation, composition, adapter expansion, or runtime mutation.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Iterable, Mapping

from agent.nova.kernel import (
    ArtifactTrustState,
    EvidenceBundle,
    ProposalStatus,
    stable_json_dumps,
)


SCHEMA_VERSION = "nova.substrate.v1"
RUNTIME_COMPOSITION_ENABLED = False


class SubstrateValidationError(ValueError):
    """Raised when a substrate proposal or schema shell is malformed."""


class SubstrateArtifactType(StrEnum):
    """Reserved substrate artifact families.

    These names are taxonomy only in Phase 1. None of them imply an activator,
    composer, adapter, evaluator, or runtime hook.
    """

    LENS = "lens"
    SCHEMA = "schema"
    EVAL = "eval"
    CONTEXT_PROJECTOR = "context_projector"
    SKILL = "skill"
    TOOL_ADAPTER = "tool_adapter"
    ANALYZER = "analyzer"
    TRANSFORM = "transform"
    POLICY = "policy"
    MEMORY_ADAPTER = "memory_adapter"
    MODEL_ADAPTER = "model_adapter"


class ProposalRiskLevel(StrEnum):
    """Coarse proposal risk used before promotion gates exist."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProposalGate(StrEnum):
    """Named gate slots that future promotion records can satisfy."""

    EVIDENCE_REVIEW = "evidence_review"
    SCHEMA_VALIDATION = "schema_validation"
    SCOPE_REVIEW = "scope_review"
    RISK_REVIEW = "risk_review"
    EVAL_CHECK = "eval_check"
    POLICY_REVIEW = "policy_review"
    HUMAN_APPROVAL = "human_approval"


SUBSTRATE_ARTIFACT_TYPES = tuple(SubstrateArtifactType)
SCHEMA_ONLY_TRUST_STATE = ArtifactTrustState.UNTRUSTED


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _dict_copy(value: Mapping[str, Any] | None, *, field_name: str = "metadata") -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping, got {type(value).__name__}")
    return dict(value)


def _tuple_of_str(values: Iterable[Any] | None, *, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    result = tuple(str(value) for value in values)
    if any(not value.strip() for value in result):
        raise SubstrateValidationError(f"{field_name} cannot contain empty values")
    return result


def _evidence_bundle_ids(
    values: Iterable[EvidenceBundle | str] | None,
) -> tuple[str, ...]:
    if values is None:
        return ()
    ids: list[str] = []
    for value in values:
        if isinstance(value, EvidenceBundle):
            ids.append(value.id)
        else:
            ids.append(str(value))
    return _tuple_of_str(ids, field_name="evidence_bundle_ids")


def _stable_dict(value: Any) -> dict[str, Any]:
    return json.loads(stable_json_dumps(value))


@dataclass(frozen=True)
class ArtifactProposalRecord:
    """Evidence-backed request to create or revise a substrate artifact shell."""

    artifact_type: SubstrateArtifactType
    scope: str
    expected_effect: str
    risk_level: ProposalRiskLevel
    required_gates: tuple[str, ...]
    id: str = field(default_factory=lambda: _new_id("proposal"))
    evidence_bundle_ids: tuple[str, ...] = ()
    candidate_payload_ref: str | None = None
    originating_run_id: str | None = None
    proposed_by: str = "assistant"
    status: ProposalStatus = ProposalStatus.PROPOSED
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        artifact_type = SubstrateArtifactType(self.artifact_type)
        risk_level = ProposalRiskLevel(self.risk_level)
        status = ProposalStatus(self.status)
        scope = str(self.scope).strip()
        expected_effect = str(self.expected_effect).strip()
        required_gates = _tuple_of_str(self.required_gates, field_name="required_gates")
        evidence_bundle_ids = _evidence_bundle_ids(self.evidence_bundle_ids)

        if not str(self.id).strip():
            raise SubstrateValidationError("proposal id cannot be empty")
        if not scope:
            raise SubstrateValidationError("proposal scope cannot be empty")
        if not expected_effect:
            raise SubstrateValidationError("proposal expected_effect cannot be empty")
        if not required_gates:
            raise SubstrateValidationError("proposal required_gates cannot be empty")

        object.__setattr__(self, "id", str(self.id))
        object.__setattr__(self, "artifact_type", artifact_type)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "expected_effect", expected_effect)
        object.__setattr__(self, "risk_level", risk_level)
        object.__setattr__(self, "required_gates", required_gates)
        object.__setattr__(self, "evidence_bundle_ids", evidence_bundle_ids)
        if self.candidate_payload_ref is not None:
            object.__setattr__(self, "candidate_payload_ref", str(self.candidate_payload_ref))
        if self.originating_run_id is not None:
            object.__setattr__(self, "originating_run_id", str(self.originating_run_id))
        object.__setattr__(self, "proposed_by", str(self.proposed_by))
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))

    def to_record(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible record."""

        return _stable_dict(self)


ProposalRecord = ArtifactProposalRecord


@dataclass(frozen=True)
class SubstrateMetadataEnvelope:
    """Shared substrate metadata carried by every artifact shell."""

    artifact_type: SubstrateArtifactType
    scope: str
    artifact_id: str = field(default_factory=lambda: _new_id("artifact"))
    schema_version: str = SCHEMA_VERSION
    proposal_id: str | None = None
    version: int = 0
    trust_state: ArtifactTrustState = SCHEMA_ONLY_TRUST_STATE
    evidence_bundle_ids: tuple[str, ...] = ()
    created_from_run_id: str | None = None
    created_by: str = "assistant"
    expected_effect: str = ""
    risk_level: ProposalRiskLevel = ProposalRiskLevel.MEDIUM
    required_gates: tuple[str, ...] = ()
    payload_ref: str | None = None
    labels: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        artifact_type = SubstrateArtifactType(self.artifact_type)
        trust_state = ArtifactTrustState(self.trust_state)
        risk_level = ProposalRiskLevel(self.risk_level)
        scope = str(self.scope).strip()
        version = int(self.version)

        if not str(self.artifact_id).strip():
            raise SubstrateValidationError("artifact_id cannot be empty")
        if not scope:
            raise SubstrateValidationError("artifact scope cannot be empty")
        if version < 0:
            raise SubstrateValidationError("artifact shell version cannot be negative")
        if not str(self.schema_version).strip():
            raise SubstrateValidationError("schema_version cannot be empty")

        object.__setattr__(self, "artifact_id", str(self.artifact_id))
        object.__setattr__(self, "artifact_type", artifact_type)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "schema_version", str(self.schema_version))
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "trust_state", trust_state)
        object.__setattr__(
            self,
            "evidence_bundle_ids",
            _evidence_bundle_ids(self.evidence_bundle_ids),
        )
        object.__setattr__(self, "risk_level", risk_level)
        object.__setattr__(
            self,
            "required_gates",
            _tuple_of_str(self.required_gates, field_name="required_gates"),
        )
        object.__setattr__(self, "labels", _tuple_of_str(self.labels, field_name="labels"))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))
        if self.proposal_id is not None:
            object.__setattr__(self, "proposal_id", str(self.proposal_id))
        if self.created_from_run_id is not None:
            object.__setattr__(self, "created_from_run_id", str(self.created_from_run_id))
        object.__setattr__(self, "created_by", str(self.created_by))
        object.__setattr__(self, "expected_effect", str(self.expected_effect))
        if self.payload_ref is not None:
            object.__setattr__(self, "payload_ref", str(self.payload_ref))

    def to_record(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible envelope."""

        return _stable_dict(self)


@dataclass(frozen=True)
class SchemaOnlyArtifactShell:
    """Inert artifact shell with no runtime activation behavior."""

    envelope: SubstrateMetadataEnvelope
    definition: Mapping[str, Any] = field(default_factory=dict)
    payload_schema: Mapping[str, Any] = field(default_factory=dict)
    compatibility: Mapping[str, Any] = field(default_factory=dict)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    artifact_type: ClassVar[SubstrateArtifactType | None] = None

    def __post_init__(self) -> None:
        if not isinstance(self.envelope, SubstrateMetadataEnvelope):
            raise TypeError(
                "envelope must be SubstrateMetadataEnvelope, "
                f"got {type(self.envelope).__name__}"
            )
        object.__setattr__(self, "definition", _dict_copy(self.definition, field_name="definition"))
        object.__setattr__(
            self,
            "payload_schema",
            _dict_copy(self.payload_schema, field_name="payload_schema"),
        )
        object.__setattr__(
            self,
            "compatibility",
            _dict_copy(self.compatibility, field_name="compatibility"),
        )
        object.__setattr__(
            self,
            "constraints",
            _dict_copy(self.constraints, field_name="constraints"),
        )
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))
        validate_schema_only_shell(self)

    @property
    def schema_only(self) -> bool:
        return True

    @property
    def runtime_enabled(self) -> bool:
        return False

    def to_record(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible shell record."""

        record = _stable_dict(self)
        record["schema_only"] = True
        record["runtime_enabled"] = False
        return record


class LensArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.LENS


class SchemaArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.SCHEMA


class EvalArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.EVAL


class ContextProjectorArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.CONTEXT_PROJECTOR


class SkillArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.SKILL


class ToolAdapterArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.TOOL_ADAPTER


class AnalyzerArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.ANALYZER


class TransformArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.TRANSFORM


class PolicyArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.POLICY


class MemoryAdapterArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.MEMORY_ADAPTER


class ModelAdapterArtifactShell(SchemaOnlyArtifactShell):
    artifact_type = SubstrateArtifactType.MODEL_ADAPTER


ARTIFACT_SHELL_TYPES: Mapping[SubstrateArtifactType, type[SchemaOnlyArtifactShell]] = {
    SubstrateArtifactType.LENS: LensArtifactShell,
    SubstrateArtifactType.SCHEMA: SchemaArtifactShell,
    SubstrateArtifactType.EVAL: EvalArtifactShell,
    SubstrateArtifactType.CONTEXT_PROJECTOR: ContextProjectorArtifactShell,
    SubstrateArtifactType.SKILL: SkillArtifactShell,
    SubstrateArtifactType.TOOL_ADAPTER: ToolAdapterArtifactShell,
    SubstrateArtifactType.ANALYZER: AnalyzerArtifactShell,
    SubstrateArtifactType.TRANSFORM: TransformArtifactShell,
    SubstrateArtifactType.POLICY: PolicyArtifactShell,
    SubstrateArtifactType.MEMORY_ADAPTER: MemoryAdapterArtifactShell,
    SubstrateArtifactType.MODEL_ADAPTER: ModelAdapterArtifactShell,
}


def build_artifact_proposal_record(
    *,
    artifact_type: SubstrateArtifactType | str,
    scope: str,
    expected_effect: str,
    required_gates: Iterable[ProposalGate | str],
    risk_level: ProposalRiskLevel | str = ProposalRiskLevel.MEDIUM,
    evidence_bundles: Iterable[EvidenceBundle | str] | None = None,
    candidate_payload_ref: str | None = None,
    originating_run_id: str | None = None,
    proposed_by: str = "assistant",
    metadata: Mapping[str, Any] | None = None,
    proposal_id: str | None = None,
) -> ArtifactProposalRecord:
    """Create a normalized proposal record from refs or EvidenceBundle objects."""

    kwargs: dict[str, Any] = {
        "artifact_type": artifact_type,
        "scope": scope,
        "expected_effect": expected_effect,
        "risk_level": risk_level,
        "required_gates": tuple(required_gates),
        "evidence_bundle_ids": _evidence_bundle_ids(evidence_bundles),
        "candidate_payload_ref": candidate_payload_ref,
        "originating_run_id": originating_run_id,
        "proposed_by": proposed_by,
        "metadata": _dict_copy(metadata),
    }
    if proposal_id is not None:
        kwargs["id"] = proposal_id
    return ArtifactProposalRecord(**kwargs)


def build_schema_only_shell(
    proposal: ArtifactProposalRecord,
    *,
    definition: Mapping[str, Any] | None = None,
    payload_schema: Mapping[str, Any] | None = None,
    compatibility: Mapping[str, Any] | None = None,
    constraints: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    artifact_id: str | None = None,
    labels: Iterable[str] | None = None,
) -> SchemaOnlyArtifactShell:
    """Build an inert artifact shell from a proposal record."""

    proposal = validate_proposal_record(proposal)
    shell_class = ARTIFACT_SHELL_TYPES[proposal.artifact_type]
    shell_metadata = _dict_copy(metadata)
    envelope = SubstrateMetadataEnvelope(
        artifact_type=proposal.artifact_type,
        scope=proposal.scope,
        artifact_id=artifact_id or _new_id("artifact"),
        proposal_id=proposal.id,
        trust_state=SCHEMA_ONLY_TRUST_STATE,
        evidence_bundle_ids=proposal.evidence_bundle_ids,
        created_from_run_id=proposal.originating_run_id,
        created_by=proposal.proposed_by,
        expected_effect=proposal.expected_effect,
        risk_level=proposal.risk_level,
        required_gates=proposal.required_gates,
        payload_ref=proposal.candidate_payload_ref,
        labels=tuple(labels or ()),
        metadata={
            "proposal_status": proposal.status.value,
            **shell_metadata,
        },
    )
    return shell_class(
        envelope=envelope,
        definition=definition or {},
        payload_schema=payload_schema or {},
        compatibility=compatibility or {},
        constraints=constraints or {},
        metadata=shell_metadata,
    )


def build_artifact_shell(*args: Any, **kwargs: Any) -> SchemaOnlyArtifactShell:
    """Alias for build_schema_only_shell; still schema-only and inert."""

    return build_schema_only_shell(*args, **kwargs)


def validate_proposal_record(proposal: ArtifactProposalRecord) -> ArtifactProposalRecord:
    """Return a proposal record after type and invariant checks."""

    if not isinstance(proposal, ArtifactProposalRecord):
        raise TypeError(f"proposal must be ArtifactProposalRecord, got {type(proposal).__name__}")
    if proposal.status is ProposalStatus.ACTIVE:
        raise SubstrateValidationError("active proposals cannot be used as schema-only shells")
    return proposal


def validate_metadata_envelope(
    envelope: SubstrateMetadataEnvelope,
) -> SubstrateMetadataEnvelope:
    """Return an envelope after type checks."""

    if not isinstance(envelope, SubstrateMetadataEnvelope):
        raise TypeError(f"envelope must be SubstrateMetadataEnvelope, got {type(envelope).__name__}")
    return envelope


def validate_schema_only_shell(shell: SchemaOnlyArtifactShell) -> SchemaOnlyArtifactShell:
    """Fail if a shell looks active, promoted, or bound to the wrong family."""

    if not isinstance(shell, SchemaOnlyArtifactShell):
        raise TypeError(f"shell must be SchemaOnlyArtifactShell, got {type(shell).__name__}")
    envelope = validate_metadata_envelope(shell.envelope)
    expected = getattr(shell, "artifact_type", None)
    if expected is not None and envelope.artifact_type is not SubstrateArtifactType(expected):
        raise SubstrateValidationError(
            f"{type(shell).__name__} requires {expected.value}, "
            f"got {envelope.artifact_type.value}"
        )
    if envelope.trust_state is not SCHEMA_ONLY_TRUST_STATE:
        raise SubstrateValidationError(
            "schema-only artifact shells must remain untrusted and inactive"
        )
    if RUNTIME_COMPOSITION_ENABLED:
        raise SubstrateValidationError("runtime composition must remain disabled in Phase 1")
    return shell


def is_schema_only_shell(value: Any) -> bool:
    """Return True for valid inert substrate shell records."""

    try:
        validate_schema_only_shell(value)
    except (SubstrateValidationError, TypeError, ValueError):
        return False
    return True


__all__ = [
    "ARTIFACT_SHELL_TYPES",
    "ArtifactProposalRecord",
    "AnalyzerArtifactShell",
    "ContextProjectorArtifactShell",
    "EvalArtifactShell",
    "LensArtifactShell",
    "MemoryAdapterArtifactShell",
    "ModelAdapterArtifactShell",
    "PolicyArtifactShell",
    "ProposalGate",
    "ProposalRecord",
    "ProposalRiskLevel",
    "RUNTIME_COMPOSITION_ENABLED",
    "SCHEMA_ONLY_TRUST_STATE",
    "SCHEMA_VERSION",
    "SUBSTRATE_ARTIFACT_TYPES",
    "SchemaArtifactShell",
    "SchemaOnlyArtifactShell",
    "SkillArtifactShell",
    "SubstrateArtifactType",
    "SubstrateMetadataEnvelope",
    "SubstrateValidationError",
    "ToolAdapterArtifactShell",
    "TransformArtifactShell",
    "build_artifact_proposal_record",
    "build_artifact_shell",
    "build_schema_only_shell",
    "is_schema_only_shell",
    "validate_metadata_envelope",
    "validate_proposal_record",
    "validate_schema_only_shell",
]
