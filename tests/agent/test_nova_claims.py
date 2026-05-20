import sqlite3
from dataclasses import replace

import pytest

from agent.nova.claims import (
    ClaimRecord,
    ClaimStore,
    ClaimTransitionKind,
    ClaimTrustError,
    ClaimTrustState,
    DisabledClaimStore,
    SQLiteClaimStore,
    build_claim_transition,
    invalidate_claim,
    propose_claim,
    trust_claim,
)
from agent.nova.evidence import MissingEvidenceError
from agent.nova.kernel import ClaimStatus, EvidenceRef, EvidenceRefKind, GateDecision, GateResult


def _ref(kind=EvidenceRefKind.CHECK, ref="check:pytest") -> EvidenceRef:
    return EvidenceRef(kind, ref, digest="a" * 64)


def _passing_gate(claim_id: str) -> GateDecision:
    return GateDecision(
        id="gate-pass-1",
        proposal_id=claim_id,
        gate_type="claim_trust",
        result=GateResult.PASS,
        reviewer_or_eval_id="eval:unit",
    )


def test_claim_record_contains_typed_state_fields_and_future_metadata():
    evidence_ref = _ref(EvidenceRefKind.RETRIEVAL, "retrieval:docs-concept")

    claim = propose_claim(
        claim_type="substrate.capability",
        scope="repo:E:/Repositories/hermes-agent",
        statement="Nova can model substrate-compatible facts before artifact families exist.",
        source="run:run-1",
        evidence_refs=(evidence_ref,),
        evidence_bundle_id="bundle-1",
        metadata={
            "subject_ref": "substrate://skills/example",
            "payload_ref": "sha256:abc123",
            "schema_version": 1,
        },
        claim_id="claim-1",
    )

    assert claim.id == "claim-1"
    assert claim.claim_type == "substrate.capability"
    assert claim.scope == "repo:E:/Repositories/hermes-agent"
    assert claim.source == "run:run-1"
    assert claim.status is ClaimStatus.PROPOSED
    assert claim.trust_state is ClaimTrustState.UNTRUSTED
    assert claim.evidence_refs == (evidence_ref,)
    assert claim.evidence_bundle_id == "bundle-1"
    assert claim.invalidation_refs == ()
    assert claim.created_at <= claim.updated_at
    assert claim.metadata["subject_ref"] == "substrate://skills/example"


def test_trusted_claim_records_require_gate_and_evidence_refs():
    with pytest.raises(ClaimTrustError):
        ClaimRecord(
            id="claim-1",
            claim_type="repo.fact",
            scope="repo:hermes",
            statement="trusted without gate",
            source="run:run-1",
            status=ClaimStatus.ACTIVE,
            trust_state=ClaimTrustState.TRUSTED,
            evidence_refs=(_ref(),),
        )

    with pytest.raises(MissingEvidenceError):
        ClaimRecord(
            id="claim-1",
            claim_type="repo.fact",
            scope="repo:hermes",
            statement="trusted without evidence",
            source="run:run-1",
            status=ClaimStatus.ACTIVE,
            trust_state=ClaimTrustState.TRUSTED,
            gate_decision_id="gate-1",
        )


def test_trust_transition_requires_passing_gate_for_target_claim_and_required_evidence():
    claim = propose_claim(
        claim_type="repo.fact",
        scope="repo:hermes",
        statement="agent.nova.claims is side-effect free until store calls.",
        source="run:run-1",
        evidence_refs=(_ref(EvidenceRefKind.MESSAGE, "message:1"),),
        claim_id="claim-1",
    )

    with pytest.raises(ClaimTrustError):
        trust_claim(
            claim,
            gate_decision=GateDecision(
                id="gate-fail",
                proposal_id=claim.id,
                gate_type="claim_trust",
                result=GateResult.FAIL,
                reviewer_or_eval_id="eval:unit",
            ),
            required_evidence_kinds=(EvidenceRefKind.MESSAGE,),
        )

    with pytest.raises(ClaimTrustError):
        trust_claim(
            claim,
            gate_decision=GateDecision(
                id="gate-other",
                proposal_id="other-claim",
                gate_type="claim_trust",
                result=GateResult.PASS,
                reviewer_or_eval_id="eval:unit",
            ),
            required_evidence_kinds=(EvidenceRefKind.MESSAGE,),
        )

    with pytest.raises(MissingEvidenceError):
        trust_claim(
            claim,
            gate_decision=_passing_gate(claim.id),
            required_evidence_kinds=(EvidenceRefKind.CHECK,),
        )

    transition = trust_claim(
        claim,
        gate_decision=_passing_gate(claim.id),
        required_evidence_kinds=(EvidenceRefKind.MESSAGE,),
        actor="policy-gate",
        reason="message evidence was checked",
    )

    assert transition.transition_kind is ClaimTransitionKind.TRUSTED
    assert transition.previous_status is ClaimStatus.PROPOSED
    assert transition.claim.status is ClaimStatus.ACTIVE
    assert transition.claim.trust_state is ClaimTrustState.TRUSTED
    assert transition.claim.gate_decision_id == "gate-pass-1"
    assert transition.actor == "policy-gate"


def test_sqlite_claim_store_appends_transitions_and_queries_latest_state(tmp_path):
    store = SQLiteClaimStore(tmp_path / "nova.db")
    try:
        claim = propose_claim(
            claim_type="repo.fact",
            scope="repo:hermes",
            statement="Claims transition through an append-only audit log.",
            source="run:run-1",
            evidence_refs=(_ref(EvidenceRefKind.CHECK, "check:unit"),),
            claim_id="claim-1",
        )

        initial = store.create_claim(claim, actor="agent")
        trusted = store.transition_claim(
            claim.id,
            ClaimStatus.ACTIVE,
            gate_decision=_passing_gate(claim.id),
            required_evidence_kinds=(EvidenceRefKind.CHECK,),
            actor="policy-gate",
        )
        invalidated = store.transition_claim(
            claim.id,
            ClaimStatus.INVALIDATED,
            invalidation_refs=("claim:claim-2", "evidence:bundle-2"),
            actor="reviewer",
            reason="newer evidence contradicted the claim",
        )

        latest = store.get_claim(claim.id)
        transitions = store.iter_transitions(claim_id=claim.id)

        assert latest.status is ClaimStatus.INVALIDATED
        assert latest.trust_state is ClaimTrustState.INVALIDATED
        assert latest.invalidation_refs == ("claim:claim-2", "evidence:bundle-2")
        assert [transition.id for transition in transitions] == [
            initial.id,
            trusted.id,
            invalidated.id,
        ]
        assert [transition.transition_kind for transition in transitions] == [
            ClaimTransitionKind.PROPOSED,
            ClaimTransitionKind.TRUSTED,
            ClaimTransitionKind.INVALIDATED,
        ]
        assert store.iter_claims(status=ClaimStatus.INVALIDATED) == [latest]
        assert store.iter_claims(trust_state=ClaimTrustState.TRUSTED) == []
    finally:
        store.close()


def test_sqlite_claim_store_rejects_stale_and_duplicate_transitions(tmp_path):
    store = SQLiteClaimStore(tmp_path / "nova.db")
    try:
        claim = propose_claim(
            claim_type="repo.fact",
            scope="repo:hermes",
            statement="Stale transitions do not rewrite the latest claim state.",
            source="run:run-1",
            evidence_refs=(_ref(),),
            claim_id="claim-1",
        )
        store.create_claim(claim)

        stale = build_claim_transition(
            claim,
            ClaimStatus.STAGED,
            trust_state=ClaimTrustState.STAGED,
        )
        trusted = trust_claim(
            claim,
            gate_decision=_passing_gate(claim.id),
            required_evidence_kinds=(EvidenceRefKind.CHECK,),
        )
        store.append_transition(trusted)

        with pytest.raises(ValueError):
            store.append_transition(stale)

        duplicate_id_transition = replace(
            build_claim_transition(
                store.get_claim(claim.id),
                ClaimStatus.DEMOTED,
                trust_state=ClaimTrustState.DEMOTED,
            ),
            id=trusted.id,
        )
        with pytest.raises(sqlite3.IntegrityError):
            store.append_transition(duplicate_id_transition)
    finally:
        store.close()


def test_disabled_claim_store_builds_initial_transition_without_persisting():
    store: ClaimStore = DisabledClaimStore()
    claim = propose_claim(
        claim_type="repo.fact",
        scope="repo:hermes",
        statement="Disabled mode does not persist claim state.",
        source="run:run-1",
    )

    transition = store.create_claim(claim)

    assert transition.claim is claim
    assert store.get_claim(claim.id) is None
    assert store.iter_transitions(claim_id=claim.id) == []
