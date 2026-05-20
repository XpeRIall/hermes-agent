import pytest

from agent.nova.kernel import ArtifactTrustState, EvidenceBundle, ProposalStatus
from agent.nova.substrate import (
    ARTIFACT_SHELL_TYPES,
    RUNTIME_COMPOSITION_ENABLED,
    SUBSTRATE_ARTIFACT_TYPES,
    ArtifactProposalRecord,
    ProposalGate,
    ProposalRiskLevel,
    SchemaOnlyArtifactShell,
    SkillArtifactShell,
    SubstrateArtifactType,
    SubstrateMetadataEnvelope,
    SubstrateValidationError,
    build_artifact_proposal_record,
    build_schema_only_shell,
    is_schema_only_shell,
)


def test_substrate_artifact_taxonomy_reserves_phase_one_families():
    assert {artifact_type.value for artifact_type in SUBSTRATE_ARTIFACT_TYPES} == {
        "lens",
        "schema",
        "eval",
        "context_projector",
        "skill",
        "tool_adapter",
        "analyzer",
        "transform",
        "policy",
        "memory_adapter",
        "model_adapter",
    }
    assert set(ARTIFACT_SHELL_TYPES) == set(SUBSTRATE_ARTIFACT_TYPES)


def test_proposal_record_references_evidence_expected_effect_risk_and_gates():
    bundle = EvidenceBundle(run_id="run-1", id="evb-1")

    proposal = build_artifact_proposal_record(
        artifact_type="skill",
        scope="repo:E:/Repositories/hermes-agent",
        expected_effect="Prefer the Nova evidence path during future repo inspections.",
        risk_level="high",
        required_gates=(ProposalGate.EVIDENCE_REVIEW, "human_approval"),
        evidence_bundles=(bundle, "evb-2"),
        candidate_payload_ref="sha256:payload",
        originating_run_id="run-1",
        proposed_by="worker-c",
    )

    assert proposal.artifact_type is SubstrateArtifactType.SKILL
    assert proposal.scope == "repo:E:/Repositories/hermes-agent"
    assert proposal.expected_effect.startswith("Prefer the Nova evidence path")
    assert proposal.risk_level is ProposalRiskLevel.HIGH
    assert proposal.required_gates == ("evidence_review", "human_approval")
    assert proposal.evidence_bundle_ids == ("evb-1", "evb-2")
    assert proposal.candidate_payload_ref == "sha256:payload"
    assert proposal.status is ProposalStatus.PROPOSED


def test_schema_only_shell_uses_shared_metadata_envelope_without_runtime_behavior():
    proposal = build_artifact_proposal_record(
        artifact_type=SubstrateArtifactType.SKILL,
        scope="repo:E:/Repositories/hermes-agent",
        expected_effect="Capture a future workflow hint without activating it.",
        risk_level=ProposalRiskLevel.MEDIUM,
        required_gates=(ProposalGate.SCHEMA_VALIDATION,),
        evidence_bundles=("evb-1",),
        candidate_payload_ref="sha256:payload",
        originating_run_id="run-1",
        proposed_by="worker-c",
    )

    shell = build_schema_only_shell(
        proposal,
        artifact_id="artifact-1",
        definition={"summary": "Schema shell only."},
        payload_schema={"type": "object", "additionalProperties": True},
        labels=("phase-1",),
    )

    assert isinstance(shell, SkillArtifactShell)
    assert shell.schema_only is True
    assert shell.runtime_enabled is False
    assert shell.envelope.artifact_id == "artifact-1"
    assert shell.envelope.proposal_id == proposal.id
    assert shell.envelope.artifact_type is SubstrateArtifactType.SKILL
    assert shell.envelope.trust_state is ArtifactTrustState.UNTRUSTED
    assert shell.envelope.evidence_bundle_ids == ("evb-1",)
    assert shell.envelope.payload_ref == "sha256:payload"
    assert shell.envelope.required_gates == ("schema_validation",)
    assert shell.to_record()["runtime_enabled"] is False


def test_all_artifact_families_have_schema_only_shell_models():
    for artifact_type, shell_class in ARTIFACT_SHELL_TYPES.items():
        proposal = build_artifact_proposal_record(
            artifact_type=artifact_type,
            scope="repo:E:/Repositories/hermes-agent",
            expected_effect=f"Reserve {artifact_type.value} as an inert substrate shell.",
            required_gates=(ProposalGate.SCHEMA_VALIDATION,),
        )

        shell = build_schema_only_shell(proposal)

        assert isinstance(shell, shell_class)
        assert isinstance(shell, SchemaOnlyArtifactShell)
        assert shell.envelope.artifact_type is artifact_type
        assert is_schema_only_shell(shell)


def test_schema_only_shells_reject_active_trust_and_family_mismatch():
    active_envelope = SubstrateMetadataEnvelope(
        artifact_type=SubstrateArtifactType.SKILL,
        scope="repo:E:/Repositories/hermes-agent",
        trust_state=ArtifactTrustState.ACTIVE,
    )
    mismatched_envelope = SubstrateMetadataEnvelope(
        artifact_type=SubstrateArtifactType.LENS,
        scope="repo:E:/Repositories/hermes-agent",
    )

    with pytest.raises(SubstrateValidationError):
        SkillArtifactShell(envelope=active_envelope)

    with pytest.raises(SubstrateValidationError):
        SkillArtifactShell(envelope=mismatched_envelope)


def test_runtime_composition_remains_disabled_and_unimplemented():
    proposal = ArtifactProposalRecord(
        artifact_type=SubstrateArtifactType.SKILL,
        scope="repo:E:/Repositories/hermes-agent",
        expected_effect="Do not activate anything.",
        risk_level=ProposalRiskLevel.LOW,
        required_gates=("schema_validation",),
        status=ProposalStatus.ACTIVE,
    )

    assert RUNTIME_COMPOSITION_ENABLED is False

    with pytest.raises(SubstrateValidationError):
        build_schema_only_shell(proposal)
