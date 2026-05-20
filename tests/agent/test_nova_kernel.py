import sqlite3

import pytest

from agent.nova import (
    ArtifactProposal,
    ClaimStatus,
    DisabledLedger,
    EvidenceBundle,
    EvidenceRef,
    EvidenceRefKind,
    LedgerEntryKind,
    ProposalStatus,
    SQLiteAppendOnlyLedger,
    ToolLedgerBatchPlan,
    TypedClaim,
    tool_args_hash,
)
from agent.nova.kernel import RunLedgerEntry


def test_stable_entry_kinds_cover_phase_one_acceptance_criteria():
    assert {kind.value for kind in LedgerEntryKind} == {
        "run.started",
        "run.ended",
        "tool.call",
        "tool.result",
        "policy.decision",
        "proposal.attempt",
        "activation.snapshot",
        "outcome",
    }


def test_tool_args_hash_is_canonical_and_does_not_expose_raw_args():
    args_a = {"z": [2, 1], "a": {"token": "secret", "n": 3}}
    args_b = {"a": {"n": 3, "token": "secret"}, "z": [2, 1]}

    digest = tool_args_hash(args_a)

    assert digest == tool_args_hash(args_b)
    assert len(digest) == 64
    assert "secret" not in digest


def test_evidence_bundle_claim_and_proposal_keep_refs_compact():
    bundle = EvidenceBundle(
        run_id="run-1",
        message_refs=(EvidenceRef(EvidenceRefKind.MESSAGE, "session:s1:message:1"),),
        tool_result_refs=(
            EvidenceRef(
                EvidenceRefKind.TOOL_RESULT,
                "tool-call:call-1",
                digest="abc123",
            ),
        ),
    )
    claim = TypedClaim(
        id="claim-1",
        claim_type="repo_fact",
        scope="repo:E:/Repositories/hermes-agent",
        statement="agent.conversation_loop is the first integration seam",
        status=ClaimStatus.PROPOSED,
        evidence_bundle_id=bundle.id,
        created_from="run-1",
    )
    proposal = ArtifactProposal(
        id="proposal-1",
        artifact_type="skill",
        scope="repo:E:/Repositories/hermes-agent",
        candidate_payload_ref="sha256:payload",
        evidence_bundle_id=bundle.id,
        originating_run_id="run-1",
        proposed_by="assistant",
    )

    assert claim.evidence_bundle_id == bundle.id
    assert proposal.status is ProposalStatus.PROPOSED
    assert proposal.candidate_payload_ref == "sha256:payload"


def test_sqlite_ledger_appends_and_replays_entries_in_sequence(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        first = ledger.append_event(
            "run-1",
            LedgerEntryKind.RUN_STARTED,
            actor="agent",
            metadata={"session_id": "s1"},
        )
        second = ledger.append_event(
            "run-1",
            LedgerEntryKind.OUTCOME,
            actor="agent",
            parent_seq=first.seq,
            payload_ref="outcome:run-1",
        )

        entries = ledger.iter_entries("run-1")

        assert [entry.seq for entry in entries] == [1, 2]
        assert [entry.kind for entry in entries] == [
            LedgerEntryKind.RUN_STARTED,
            LedgerEntryKind.OUTCOME,
        ]
        assert ledger.get_entry(second.id).payload_ref == "outcome:run-1"
        assert ledger.iter_entries("run-1", kind=LedgerEntryKind.OUTCOME) == [second]
    finally:
        ledger.close()


def test_sqlite_ledger_is_append_only_for_duplicate_run_sequence(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        entry = RunLedgerEntry(
            run_id="run-1",
            seq=1,
            kind=LedgerEntryKind.RUN_STARTED,
        )

        ledger.append(entry)

        with pytest.raises(sqlite3.IntegrityError):
            ledger.append(
                RunLedgerEntry(
                    run_id="run-1",
                    seq=1,
                    kind=LedgerEntryKind.RUN_ENDED,
                )
            )
    finally:
        ledger.close()


def test_reserved_sequence_range_makes_concurrent_tool_replay_deterministic(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        reserved = ledger.reserve_sequence("run-1", count=4)
        plan = ToolLedgerBatchPlan.from_tool_call_ids(
            "run-1",
            ["call-a", "call-b"],
            first_seq=reserved.start,
            batch_id="batch-1",
        )
        slot_a = plan.slot_for("call-a")
        slot_b = plan.slot_for("call-b")

        # Simulate worker completion order racing ahead of model tool-call order.
        ledger.append_event(
            "run-1",
            LedgerEntryKind.TOOL_RESULT,
            seq=slot_b.result_seq,
            actor="tool",
            subject_ref="call-b",
            batch_id=slot_b.batch_id,
            batch_index=slot_b.batch_index,
        )
        ledger.append_event(
            "run-1",
            LedgerEntryKind.TOOL_CALL,
            seq=slot_a.call_seq,
            actor="assistant",
            subject_ref="call-a",
            batch_id=slot_a.batch_id,
            batch_index=slot_a.batch_index,
        )
        ledger.append_event(
            "run-1",
            LedgerEntryKind.TOOL_RESULT,
            seq=slot_a.result_seq,
            actor="tool",
            subject_ref="call-a",
            batch_id=slot_a.batch_id,
            batch_index=slot_a.batch_index,
        )
        ledger.append_event(
            "run-1",
            LedgerEntryKind.TOOL_CALL,
            seq=slot_b.call_seq,
            actor="assistant",
            subject_ref="call-b",
            batch_id=slot_b.batch_id,
            batch_index=slot_b.batch_index,
        )

        assert [(entry.kind, entry.subject_ref) for entry in ledger.iter_entries("run-1")] == [
            (LedgerEntryKind.TOOL_CALL, "call-a"),
            (LedgerEntryKind.TOOL_CALL, "call-b"),
            (LedgerEntryKind.TOOL_RESULT, "call-a"),
            (LedgerEntryKind.TOOL_RESULT, "call-b"),
        ]
    finally:
        ledger.close()


def test_disabled_ledger_builds_entries_without_persisting_them():
    ledger = DisabledLedger()

    entry = ledger.append_event("run-1", LedgerEntryKind.RUN_STARTED)

    assert entry.kind is LedgerEntryKind.RUN_STARTED
    assert ledger.iter_entries("run-1") == []
