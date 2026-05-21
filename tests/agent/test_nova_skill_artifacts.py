from pathlib import Path

import pytest

from agent.nova.activation import (
    SkillActivationContext,
    SkillArtifactActivationController,
    SkillArtifactActivationError,
    repo_scope_for_path,
    resolve_skill_artifact,
)
from agent.nova.kernel import ArtifactTrustState, LedgerEntryKind
from agent.nova.ledger import SQLiteAppendOnlyLedger
from agent.nova.skill_artifacts import (
    JSONLSkillArtifactStore,
    PromotedSkillArtifact,
    SkillArtifactError,
    build_promoted_skill_artifact,
    skill_content_hash,
)
from agent.nova.substrate import RUNTIME_COMPOSITION_ENABLED


def _skill(tmp_path, name="skill-a", content="Use repo-specific test commands.\n"):
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True)
    path = skill_dir / "SKILL.md"
    path.write_text(content, encoding="utf-8")
    return path


def _artifact(tmp_path, *, artifact_id="artifact-1", scope=None, chain_id="chain-a"):
    skill_path = _skill(tmp_path / artifact_id)
    return build_promoted_skill_artifact(
        skill_path=skill_path,
        scope=scope or repo_scope_for_path(tmp_path),
        activation_rule={"benchmark_chain_id": chain_id},
        evidence_bundle_id="evb-1",
        gate_decision_id="gate-1",
        artifact_id=artifact_id,
    )


def test_promoted_skill_artifact_requires_evidence_and_gate_ids(tmp_path):
    skill_path = _skill(tmp_path)

    with pytest.raises(SkillArtifactError):
        build_promoted_skill_artifact(
            skill_path=skill_path,
            scope=repo_scope_for_path(tmp_path),
            activation_rule={},
            evidence_bundle_id="",
            gate_decision_id="gate-1",
        )

    with pytest.raises(SkillArtifactError):
        PromotedSkillArtifact(
            artifact_id="artifact-1",
            version_id="artifact-1:v1",
            version=1,
            scope=repo_scope_for_path(tmp_path),
            activation_rule={},
            skill_name="x",
            skill_slug="x",
            skill_path=str(skill_path),
            content_hash=skill_content_hash("x"),
            payload_ref="sha256:" + skill_content_hash("x"),
            evidence_bundle_id="evb-1",
            gate_decision_id="",
            trust_state=ArtifactTrustState.ACTIVE,
        )


def test_resolver_activates_one_exact_scope_artifact_and_honors_exclusion(tmp_path):
    artifact = _artifact(tmp_path, scope=repo_scope_for_path(tmp_path))
    context = SkillActivationContext.from_task(
        run_id="run-1",
        task_text="modernize a skill",
        repo_scope=repo_scope_for_path(tmp_path),
    )

    resolved, reason = resolve_skill_artifact([artifact], context)

    assert resolved.artifact_id == artifact.artifact_id
    assert reason == "exact repo scope match"
    excluded_context = SkillActivationContext.from_task(
        run_id="run-1",
        task_text="modernize a skill",
        repo_scope=repo_scope_for_path(tmp_path),
        excluded_artifact_ids=(artifact.artifact_id,),
    )
    assert resolve_skill_artifact([artifact], excluded_context) is None


def test_resolver_fails_closed_on_multiple_matches_without_explicit_artifact(tmp_path):
    artifact_a = _artifact(tmp_path, artifact_id="artifact-a")
    artifact_b = _artifact(tmp_path, artifact_id="artifact-b")
    context = SkillActivationContext.from_task(
        run_id="run-1",
        task_text="modernize a skill",
        repo_scope=repo_scope_for_path(tmp_path),
    )

    with pytest.raises(SkillArtifactActivationError):
        resolve_skill_artifact([artifact_a, artifact_b], context)

    explicit_context = SkillActivationContext.from_task(
        run_id="run-1",
        task_text="modernize a skill",
        repo_scope=repo_scope_for_path(tmp_path),
        explicit_artifact_id="artifact-b",
    )
    resolved, _ = resolve_skill_artifact([artifact_a, artifact_b], explicit_context)
    assert resolved.artifact_id == "artifact-b"


def test_activation_writes_log_and_ledger_before_projection(tmp_path):
    artifact = _artifact(tmp_path)
    store = JSONLSkillArtifactStore(
        tmp_path / "nova" / "skill_artifacts.jsonl",
        tmp_path / "nova" / "skill_artifact_activations.jsonl",
    )
    store.put_artifact(artifact)
    ledger = SQLiteAppendOnlyLedger(tmp_path / "nova" / "kernel.db")
    controller = SkillArtifactActivationController(
        store=store,
        enabled=True,
        repo_scope=repo_scope_for_path(tmp_path),
    )
    try:
        result = controller.activate_for_run(
            run_id="run-1",
            task_text="modernize a skill",
            ledger=ledger,
        )

        assert "Use repo-specific test commands." in result.context_block
        activations = store.iter_activations()
        assert len(activations) == 1
        assert activations[0].artifact_id == artifact.artifact_id
        entries = ledger.iter_entries("run-1", kind=LedgerEntryKind.ACTIVATION_SNAPSHOT)
        assert len(entries) == 1
        assert entries[0].subject_ref == f"artifact:{artifact.artifact_id}"
        assert entries[0].metadata["activation_id"] == activations[0].id
        assert RUNTIME_COMPOSITION_ENABLED is False
    finally:
        ledger.close()


def test_activation_rejects_payload_hash_mismatch(tmp_path):
    artifact = _artifact(tmp_path)
    store = JSONLSkillArtifactStore(tmp_path / "artifacts.jsonl", tmp_path / "acts.jsonl")
    store.put_artifact(artifact)
    skill_path = Path(artifact.skill_path)
    skill_path.write_text("mutated content\n", encoding="utf-8")
    controller = SkillArtifactActivationController(
        store=store,
        enabled=True,
        repo_scope=repo_scope_for_path(tmp_path),
    )

    with pytest.raises(SkillArtifactError):
        controller.activate_for_run(run_id="run-1", task_text="task")
