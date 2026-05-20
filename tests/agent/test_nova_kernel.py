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
    MissingEvidenceError,
    NovaRecorder,
    ProposalStatus,
    SQLiteAppendOnlyLedger,
    SQLiteEvidenceStore,
    ToolCallEvidence,
    ToolLedgerBatchPlan,
    ToolResultEvidence,
    TypedClaim,
    require_evidence_refs,
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


def test_tool_args_hash_redacts_secret_values_before_hashing():
    assert tool_args_hash({"token": "first-low-entropy-secret"}) == tool_args_hash(
        {"token": "second-low-entropy-secret"}
    )
    assert tool_args_hash({"path": "a.py"}) != tool_args_hash({"path": "b.py"})


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
    assert bundle.has_refs(EvidenceRefKind.MESSAGE, EvidenceRefKind.TOOL_RESULT)


def test_required_evidence_refs_fail_closed():
    bundle = EvidenceBundle(
        run_id="run-1",
        message_refs=(EvidenceRef(EvidenceRefKind.MESSAGE, "session:s1:message:1"),),
    )

    assert require_evidence_refs(bundle, [EvidenceRefKind.MESSAGE]) is bundle

    with pytest.raises(MissingEvidenceError):
        require_evidence_refs(bundle, [EvidenceRefKind.TOOL_RESULT])

    with pytest.raises(MissingEvidenceError):
        require_evidence_refs(None, [EvidenceRefKind.MESSAGE])


def test_sqlite_evidence_store_persists_compact_refs_without_raw_payloads(tmp_path):
    db_path = tmp_path / "nova.db"
    store = SQLiteEvidenceStore(db_path)
    try:
        secret = "OPENAI_API_KEY=sk-proj-secretsecretsecretsecret"
        bundle = EvidenceBundle(
            run_id="run-1",
            tool_result_refs=(
                EvidenceRef(
                    EvidenceRefKind.TOOL_RESULT,
                    "session:s1:tool_result:call-1",
                    digest="a" * 64,
                    metadata={"tool_name": "terminal", "content_size": len(secret)},
                ),
            ),
            metadata={"capture": "tool_result"},
        )

        store.put_bundle(bundle)
        loaded = store.get_bundle(bundle.id)

        assert loaded.id == bundle.id
        assert loaded.tool_result_refs[0].ref == "session:s1:tool_result:call-1"
        assert loaded.tool_result_refs[0].metadata["tool_name"] == "terminal"
        assert secret.encode() not in db_path.read_bytes()
    finally:
        store.close()


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


def test_nova_recorder_captures_run_and_tool_evidence_in_shadow_mode(tmp_path):
    db_path = tmp_path / "nova.db"
    ledger = SQLiteAppendOnlyLedger(db_path)
    store = SQLiteEvidenceStore(db_path)
    recorder = NovaRecorder(mode="shadow", ledger=ledger, evidence_store=store)
    try:
        recorder.record_run_start(
            run_id="run-1",
            session_id="s1",
            user_message="inspect repository",
            message_index=0,
            task_id="task-1",
        )
        plan = recorder.record_tool_call_batch(
            run_id="run-1",
            session_id="s1",
            api_call_count=1,
            calls=(
                ToolCallEvidence("call-a", "read_file", {"path": "a.py"}),
                ToolCallEvidence("call-b", "terminal", {"command": "pytest"}),
            ),
        )
        recorder.record_tool_result(
            run_id="run-1",
            session_id="s1",
            plan=plan,
            result=ToolResultEvidence(
                "call-b",
                "terminal",
                {"command": "pytest"},
                "failed",
                duration_seconds=1.2,
                is_error=True,
                message_index=3,
            ),
        )
        recorder.record_tool_result(
            run_id="run-1",
            session_id="s1",
            plan=plan,
            result=ToolResultEvidence(
                "call-a",
                "read_file",
                {"path": "a.py"},
                "contents",
                duration_seconds=0.1,
                message_index=2,
            ),
        )
        recorder.record_run_end(
            run_id="run-1",
            session_id="s1",
            final_response="done",
            completed=True,
            exit_reason="text_response",
            api_calls=2,
            message_index=4,
        )

        entries = ledger.iter_entries("run-1")

        assert [(entry.kind, entry.subject_ref) for entry in entries] == [
            (LedgerEntryKind.RUN_STARTED, "session:s1"),
            (LedgerEntryKind.TOOL_CALL, "call-a"),
            (LedgerEntryKind.TOOL_CALL, "call-b"),
            (LedgerEntryKind.TOOL_RESULT, "call-a"),
            (LedgerEntryKind.TOOL_RESULT, "call-b"),
            (LedgerEntryKind.RUN_ENDED, "session:s1"),
            (LedgerEntryKind.OUTCOME, "session:s1"),
        ]
        tool_result_entries = [
            entry for entry in entries if entry.kind is LedgerEntryKind.TOOL_RESULT
        ]
        bundles = [store.get_bundle(entry.evidence_bundle_id) for entry in tool_result_entries]
        assert all(bundle.tool_result_refs for bundle in bundles)
        assert {bundle.metadata["tool_name"] for bundle in bundles} == {"read_file", "terminal"}
    finally:
        recorder.close()


def test_disabled_ledger_builds_entries_without_persisting_them():
    ledger = DisabledLedger()

    entry = ledger.append_event("run-1", LedgerEntryKind.RUN_STARTED)

    assert entry.kind is LedgerEntryKind.RUN_STARTED
    assert ledger.iter_entries("run-1") == []
