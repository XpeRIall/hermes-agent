import pytest

from agent.nova.kernel import (
    EvidenceBundle,
    EvidenceRef,
    EvidenceRefKind,
    LedgerEntryKind,
    PolicyDecision,
    PolicyDecisionAction,
)
from agent.nova.ledger import DisabledLedger, SQLiteAppendOnlyLedger
from agent.nova.policy import (
    MUTATION_SURFACE_POLICIES,
    MutationRequest,
    MutationSurface,
    PolicyViolationError,
    classify_path_surface,
    classify_tool_mutation,
    gate_mutation,
    mutation_surface_inventory,
    require_trusted_state_gate,
)


def _bundle(run_id: str = "run-1") -> EvidenceBundle:
    return EvidenceBundle(
        run_id=run_id,
        message_refs=(EvidenceRef(EvidenceRefKind.MESSAGE, "session:s1:message:1"),),
        file_refs=(EvidenceRef(EvidenceRefKind.FILE, "file:skills/example/SKILL.md"),),
        command_refs=(EvidenceRef(EvidenceRefKind.COMMAND, "command:pytest"),),
        tool_result_refs=(
            EvidenceRef(EvidenceRefKind.TOOL_RESULT, "session:s1:tool_result:call-1"),
        ),
    )


def test_mutation_inventory_covers_phase_one_surfaces():
    assert {policy.surface for policy in mutation_surface_inventory()} == {
        MutationSurface.MEMORY,
        MutationSurface.SKILLS,
        MutationSurface.PROVIDERS,
        MutationSurface.PLUGINS,
        MutationSurface.BACKGROUND_REVIEW,
        MutationSurface.CRON,
        MutationSurface.CONFIG,
        MutationSurface.SESSION,
        MutationSurface.CHECKPOINT,
        MutationSurface.PROMPT_CONTEXT,
        MutationSurface.TERMINAL,
        MutationSurface.FILE_TOOL,
    }
    assert set(MUTATION_SURFACE_POLICIES) == set(MutationSurface)


def test_classify_known_future_affecting_tool_calls():
    memory = classify_tool_mutation(
        "memory",
        {"action": "add", "target": "user", "content": "likes concise docs"},
        run_id="run-1",
    )
    skill = classify_tool_mutation(
        "skill_manage",
        {"action": "patch", "name": "reviewer", "old_string": "a", "new_string": "b"},
        run_id="run-1",
    )
    prompt_file = classify_tool_mutation(
        "write_file",
        {"path": "AGENTS.md", "content": "instructions"},
        run_id="run-1",
    )
    terminal = classify_tool_mutation(
        "terminal",
        {"command": "python scripts/update_config.py"},
        run_id="run-1",
    )

    assert memory.surface is MutationSurface.MEMORY
    assert skill.surface is MutationSurface.SKILLS
    assert prompt_file.surface is MutationSurface.PROMPT_CONTEXT
    assert terminal.surface is MutationSurface.TERMINAL
    assert "existing_approval_authority" in terminal.metadata
    assert classify_tool_mutation("read_file", {"path": "AGENTS.md"}, run_id="run-1") is None


def test_classify_paths_that_influence_future_runs():
    assert classify_path_surface("skills/reviewer/SKILL.md") is MutationSurface.SKILLS
    assert classify_path_surface("plugins/model-providers/acme/__init__.py") is MutationSurface.PROVIDERS
    assert classify_path_surface("plugins/acme/plugin.yaml") is MutationSurface.PLUGINS
    assert classify_path_surface("cron/jobs.py") is MutationSurface.CRON
    assert classify_path_surface("C:/Users/me/.hermes/config.yaml") is MutationSurface.CONFIG
    assert classify_path_surface(".cursor/rules/hermes.mdc") is MutationSurface.PROMPT_CONTEXT
    assert classify_path_surface("src/app.py") is None


def test_policy_gate_records_decision_and_proposal_attempt(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        request = classify_tool_mutation(
            "skill_manage",
            {"action": "patch", "name": "reviewer", "old_string": "a", "new_string": "b"},
            run_id="run-1",
        )
        result = gate_mutation(request, evidence_bundle=_bundle(), ledger=ledger)

        entries = ledger.iter_entries("run-1")

        assert result.converted_to_proposal
        assert result.proposal is not None
        assert result.proposal.artifact_type == "skills"
        assert [entry.kind for entry in entries] == [
            LedgerEntryKind.POLICY_DECISION,
            LedgerEntryKind.PROPOSAL_ATTEMPT,
        ]
        assert entries[0].policy_decision_id == result.decision.id
        assert entries[1].policy_decision_id == result.decision.id
        assert entries[1].payload_ref == result.proposal.candidate_payload_ref
    finally:
        ledger.close()


def test_policy_gate_is_side_effect_free_without_ledger():
    ledger = DisabledLedger()
    request = MutationRequest(
        run_id="run-1",
        surface=MutationSurface.SESSION,
        operation="set_session_title",
        subject_ref="session:s1",
    )

    result = gate_mutation(request)

    assert result.shadowed
    assert result.ledger_entry_ids == ()
    assert ledger.iter_entries("run-1") == []


def test_non_future_affecting_allow_does_not_require_evidence():
    request = MutationRequest(
        run_id="run-1",
        surface=MutationSurface.SESSION,
        operation="set_session_title",
        subject_ref="session:s1",
        future_affecting=False,
    )

    result = gate_mutation(request)

    assert result.allowed
    assert result.decision.evidence_bundle_id is None


def test_direct_trusted_mutation_blocks_without_evidence_and_records_decision(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        request = MutationRequest(
            run_id="run-1",
            surface=MutationSurface.MEMORY,
            operation="write",
            subject_ref="memory:user",
            direct_trusted_state=True,
            requested_action=PolicyDecisionAction.ALLOW,
        )

        result = gate_mutation(request, ledger=ledger)
        entries = ledger.iter_entries("run-1")

        assert result.blocked
        assert result.proposal is None
        assert len(entries) == 1
        assert entries[0].kind is LedgerEntryKind.POLICY_DECISION
        assert entries[0].metadata["action"] == "block"
        assert entries[0].evidence_bundle_id is None
    finally:
        ledger.close()


def test_require_trusted_state_gate_requires_allow_decision_and_evidence():
    bundle = _bundle()
    allowed = PolicyDecision(
        id="pol-1",
        run_id="run-1",
        action=PolicyDecisionAction.ALLOW,
        subject_ref="memory:user",
        evidence_bundle_id=bundle.id,
    )

    assert (
        require_trusted_state_gate(
            decision=allowed,
            evidence_bundle=bundle,
            required_kinds=(EvidenceRefKind.MESSAGE, EvidenceRefKind.TOOL_RESULT),
        )
        is allowed
    )
    with pytest.raises(PolicyViolationError):
        require_trusted_state_gate(decision=None, evidence_bundle=bundle)
    with pytest.raises(PolicyViolationError):
        require_trusted_state_gate(
            decision=PolicyDecision(
                id="pol-2",
                run_id="run-1",
                action=PolicyDecisionAction.SHADOW,
                subject_ref="memory:user",
                evidence_bundle_id=bundle.id,
            ),
            evidence_bundle=bundle,
        )


def test_terminal_and_generic_file_writes_are_shadow_records_not_new_approvals(tmp_path):
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova.db")
    try:
        terminal = classify_tool_mutation(
            "terminal",
            {"command": "rm -rf build"},
            run_id="run-1",
        )
        file_write = classify_tool_mutation(
            "write_file",
            {"path": "src/app.py", "content": "print('hi')"},
            run_id="run-1",
        )

        terminal_result = gate_mutation(terminal, ledger=ledger)
        file_result = gate_mutation(file_write, ledger=ledger)
        entries = ledger.iter_entries("run-1")

        assert terminal_result.shadowed
        assert file_result.shadowed
        assert terminal_result.proposal is None
        assert file_result.proposal is None
        assert [entry.kind for entry in entries] == [
            LedgerEntryKind.POLICY_DECISION,
            LedgerEntryKind.POLICY_DECISION,
        ]
        assert "tools.approval" in entries[0].metadata["existing_authority"]
    finally:
        ledger.close()
