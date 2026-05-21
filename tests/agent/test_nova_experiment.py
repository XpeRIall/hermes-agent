import json
import sys

from agent.nova.experiment import TrialManifest, analyze_results, replay_trial, run_trial


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


def _manifest(repo, *, arm="nova_active", command=None, metrics=None):
    return TrialManifest.from_mapping(
        {
            "trial_id": f"{arm}-trial",
            "arm": arm,
            "repo": str(repo),
            "repo_sha": "abc123",
            "chain_id": "chain-a",
            "task_id": f"{arm}-task",
            "task_text": "run the task",
            "model": "stub-model",
            "task_command": command or [sys.executable, "-c", "print('ok')"],
            "checks": [[sys.executable, "-c", "print('check')"]],
            "outcome_metrics": metrics or {},
        }
    )


def test_nova_active_trial_fails_if_activation_log_is_missing(tmp_path):
    repo = _repo(tmp_path)

    result = run_trial(_manifest(repo), tmp_path / "out")

    assert result["status"] == "failed"
    assert result["reason"] == "nova_active arm produced no valid activation log"
    assert result["activation_count"] == 0


def test_nova_active_trial_passes_only_with_real_activation_log(tmp_path):
    repo = _repo(tmp_path)
    code = (
        "import os, pathlib; "
        "p = pathlib.Path(os.environ['HERMES_HOME']) / 'nova' / "
        "'skill_artifact_activations.jsonl'; "
        "p.parent.mkdir(parents=True, exist_ok=True); "
        "p.write_text("
        "'{\"run_id\":\"r1\",\"artifact_id\":\"a1\",\"version_id\":\"v1\","
        "\"activation_context_hash\":\"h1\"}\\n')"
    )

    result = run_trial(
        _manifest(repo, command=[sys.executable, "-c", code]),
        tmp_path / "out",
    )

    assert result["status"] == "passed"
    assert result["activation_count"] == 1


def test_nova_active_trial_rejects_malformed_activation_log(tmp_path):
    repo = _repo(tmp_path)
    code = (
        "import os, pathlib; "
        "p = pathlib.Path(os.environ['HERMES_HOME']) / 'nova' / "
        "'skill_artifact_activations.jsonl'; "
        "p.parent.mkdir(parents=True, exist_ok=True); "
        "p.write_text('{\"run_id\":\"r1\"}\\n')"
    )

    result = run_trial(
        _manifest(repo, command=[sys.executable, "-c", code]),
        tmp_path / "out",
    )

    assert result["status"] == "failed"
    assert result["activation_log_lines"] == 1
    assert result["activation_count"] == 0


def test_adjacent_only_trial_fails_if_nova_activation_metadata_appears(tmp_path):
    repo = _repo(tmp_path)
    code = (
        "import os, pathlib; "
        "p = pathlib.Path(os.environ['HERMES_HOME']) / 'nova' / "
        "'skill_artifact_activations.jsonl'; "
        "p.parent.mkdir(parents=True, exist_ok=True); "
        "p.write_text('{\"run_id\":\"r1\"}\\n')"
    )

    result = run_trial(
        _manifest(repo, arm="adjacent_only", command=[sys.executable, "-c", code]),
        tmp_path / "out",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "non-active arm produced activation metadata"


def test_analysis_returns_inconclusive_for_missing_samples_or_metrics():
    result = analyze_results([], min_trials_per_arm=1)

    assert result["recommendation"] == "inconclusive"
    assert result["blockers"]


def test_analysis_rejects_stringified_boolean_labels():
    rows = [
        {
            "arm": "adjacent_only",
            "metrics": {
                "repeated_error": "false",
                "debug_time_seconds": 10,
                "token_count": 100,
                "wall_time_seconds": 10,
            },
        },
        {"arm": "nova_staged", "metrics": {"repeated_error": True, "debug_time_seconds": 12}},
        {
            "arm": "nova_active",
            "metrics": {
                "repeated_error": False,
                "debug_time_seconds": 8,
                "token_count": 110,
                "wall_time_seconds": 11,
                "activation_relevant": True,
                "bad_artifact_attributed": True,
                "demotion_effective": True,
            },
        },
    ]

    result = analyze_results(rows, min_trials_per_arm=1)

    assert result["recommendation"] == "inconclusive"
    assert any(
        "adjacent_only.repeated_error must be boolean" in blocker
        for blocker in result["blockers"]
    )


def test_analysis_emits_continue_only_when_thresholds_are_met():
    rows = [
        {
            "arm": "adjacent_only",
            "metrics": {
                "repeated_error": True,
                "debug_time_seconds": 10,
                "token_count": 100,
                "wall_time_seconds": 10,
            },
        },
        {
            "arm": "nova_staged",
            "metrics": {
                "repeated_error": True,
                "debug_time_seconds": 12,
            },
        },
        {
            "arm": "nova_active",
            "metrics": {
                "repeated_error": False,
                "debug_time_seconds": 8,
                "token_count": 110,
                "wall_time_seconds": 11,
                "activation_relevant": True,
                "bad_artifact_attributed": True,
                "demotion_effective": True,
            },
        },
    ]

    result = analyze_results(rows, min_trials_per_arm=1)

    assert result["recommendation"] == "continue"
    assert result["failed_thresholds"] == []


def test_replay_adds_excluded_artifact_and_links_original_trial(tmp_path):
    repo = _repo(tmp_path)
    trial = tmp_path / "trial.json"
    trial.write_text(json.dumps(_manifest(repo).to_record()), encoding="utf-8")

    result = replay_trial(trial, exclude_artifact_id="artifact-1", output_dir=tmp_path / "out")

    assert result["replay"]["excluded_artifact_id"] == "artifact-1"
    assert result["manifest"]["metadata"]["replay_of"] == "nova_active-trial"
    assert result["manifest"]["exclude_artifact_ids"] == ["artifact-1"]
    assert result["commands"][0]["argv"][0] == sys.executable
    assert result["commands"][0]["returncode"] == 0
