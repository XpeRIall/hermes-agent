"""Counterfactual experiment harness for RES-11 Nova SkillArtifact tests."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from agent.nova.activation import repo_scope_for_path
from agent.nova.skill_artifacts import (
    JSONLSkillArtifactStore,
    PromotedSkillArtifact,
    SKILL_ACTIVATIONS_FILENAME,
    SKILL_ARTIFACTS_FILENAME,
)
from agent.nova.kernel import stable_json_dumps


class ExperimentArm(StrEnum):
    BASELINE_HOST = "baseline_host"
    ADJACENT_ONLY = "adjacent_only"
    NOVA_STAGED = "nova_staged"
    NOVA_ACTIVE = "nova_active"
    SHADOW_PROJECTOR = "shadow_projector"


class TrialStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Recommendation(StrEnum):
    CONTINUE = "continue"
    SHRINK = "shrink"
    STOP = "stop"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    argv: tuple[str, ...]
    timeout_seconds: int = 300
    shell: bool = False

    @classmethod
    def from_value(cls, value: Any, *, default_name: str) -> "CommandSpec | None":
        if value in (None, "", []):
            return None
        if isinstance(value, Mapping):
            if "shell" in value:
                return cls(
                    name=str(value.get("name") or default_name),
                    argv=(str(value["shell"]),),
                    timeout_seconds=int(value.get("timeout_seconds", 300)),
                    shell=True,
                )
            return cls(
                name=str(value.get("name") or default_name),
                argv=tuple(str(part) for part in value.get("argv", ())),
                timeout_seconds=int(value.get("timeout_seconds", 300)),
                shell=False,
            )
        if isinstance(value, (list, tuple)):
            return cls(name=default_name, argv=tuple(str(part) for part in value))
        raise ValueError("commands must be argv lists or explicit {shell: ...} mappings")

    def run(self, *, cwd: Path, env: Mapping[str, str]) -> dict[str, Any]:
        started = time.time()
        try:
            completed = subprocess.run(
                self.argv[0] if self.shell else list(self.argv),
                cwd=str(cwd),
                env=dict(env),
                text=True,
                capture_output=True,
                shell=self.shell,
                timeout=self.timeout_seconds,
            )
            return {
                "name": self.name,
                "argv": list(self.argv),
                "shell": self.shell,
                "returncode": completed.returncode,
                "duration_seconds": time.time() - started,
                "stdout_tail": _tail(completed.stdout),
                "stderr_tail": _tail(completed.stderr),
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "name": self.name,
                "argv": list(self.argv),
                "shell": self.shell,
                "returncode": None,
                "duration_seconds": time.time() - started,
                "stdout_tail": _tail(exc.stdout or ""),
                "stderr_tail": _tail(exc.stderr or ""),
                "timed_out": True,
            }


@dataclass(frozen=True)
class TrialManifest:
    trial_id: str
    arm: ExperimentArm
    repo: str
    repo_sha: str
    chain_id: str
    task_id: str
    task_text: str
    model: str
    repeat: int = 1
    checks: tuple[CommandSpec, ...] = ()
    task_command: CommandSpec | None = None
    active_artifacts: tuple[PromotedSkillArtifact, ...] = ()
    exclude_artifact_ids: tuple[str, ...] = ()
    outcome_metrics: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    requires_activation: bool | None = None
    forbids_activation: bool | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "TrialManifest":
        arm = ExperimentArm(data["arm"])
        active_artifacts = tuple(
            PromotedSkillArtifact(**record)
            for record in data.get("active_artifacts", ())
        )
        return cls(
            trial_id=str(data.get("trial_id") or f"trial_{uuid.uuid4().hex}"),
            arm=arm,
            repo=str(data["repo"]),
            repo_sha=str(data.get("repo_sha") or ""),
            chain_id=str(data.get("chain_id") or ""),
            task_id=str(data.get("task_id") or data.get("trial_id") or ""),
            task_text=str(data.get("task_text") or ""),
            model=str(data.get("model") or ""),
            repeat=int(data.get("repeat", 1)),
            checks=tuple(
                command
                for command in (
                    CommandSpec.from_value(value, default_name=f"check-{idx + 1}")
                    for idx, value in enumerate(data.get("checks", ()))
                )
                if command is not None
            ),
            task_command=CommandSpec.from_value(
                data.get("task_command"),
                default_name="task",
            ),
            active_artifacts=active_artifacts,
            exclude_artifact_ids=tuple(str(item) for item in data.get("exclude_artifact_ids", ())),
            outcome_metrics=dict(data.get("outcome_metrics", {})),
            metadata=dict(data.get("metadata", {})),
            requires_activation=data.get("requires_activation"),
            forbids_activation=data.get("forbids_activation"),
        )

    def to_record(self) -> dict[str, Any]:
        record = json.loads(stable_json_dumps(self))
        record["arm"] = self.arm.value
        return record

    @property
    def activation_required(self) -> bool:
        if self.requires_activation is not None:
            return bool(self.requires_activation)
        return self.arm is ExperimentArm.NOVA_ACTIVE

    @property
    def activation_forbidden(self) -> bool:
        if self.forbids_activation is not None:
            return bool(self.forbids_activation)
        return self.arm in {
            ExperimentArm.BASELINE_HOST,
            ExperimentArm.ADJACENT_ONLY,
            ExperimentArm.NOVA_STAGED,
        }


def load_manifests(path: str | Path) -> list[TrialManifest]:
    data = _read_json_or_yaml(Path(path))
    if isinstance(data, Mapping) and "trials" in data:
        rows = data["trials"]
    elif isinstance(data, list):
        rows = data
    else:
        rows = [data]
    return [TrialManifest.from_mapping(row) for row in rows]


def run_trial(manifest: TrialManifest, output_dir: str | Path) -> dict[str, Any]:
    output_root = Path(output_dir)
    trial_dir = output_root / manifest.arm.value / manifest.trial_id
    hermes_home = trial_dir / "hermes_home"
    hermes_home.mkdir(parents=True, exist_ok=True)
    artifact_path = hermes_home / "nova" / SKILL_ARTIFACTS_FILENAME
    activation_log_path = hermes_home / "nova" / SKILL_ACTIVATIONS_FILENAME
    store = JSONLSkillArtifactStore(artifact_path, activation_log_path)
    for artifact in manifest.active_artifacts:
        store.put_artifact(artifact)
    _write_arm_config(manifest, hermes_home, artifact_path, activation_log_path)

    env = os.environ.copy()
    env.update(
        {
            "HERMES_HOME": str(hermes_home),
            "NOVA_EXPERIMENT_ARM": manifest.arm.value,
            "NOVA_EXPERIMENT_TRIAL_ID": manifest.trial_id,
            "NOVA_EXPERIMENT_TASK_ID": manifest.task_id,
        }
    )
    commands: list[dict[str, Any]] = []
    status = TrialStatus.PASSED
    reason = ""
    started = time.time()

    if manifest.task_command is None:
        status = TrialStatus.BLOCKED
        reason = "no task_command supplied; no outcome was inferred"
    else:
        task_result = manifest.task_command.run(cwd=Path(manifest.repo), env=env)
        commands.append(task_result)
        if task_result["timed_out"] or task_result["returncode"] != 0:
            status = TrialStatus.FAILED
            reason = "task_command failed"
        for check in manifest.checks:
            check_result = check.run(cwd=Path(manifest.repo), env=env)
            commands.append(check_result)
            if check_result["timed_out"] or check_result["returncode"] != 0:
                status = TrialStatus.FAILED
                reason = reason or "one or more checks failed"

    activation_count = _activation_count(activation_log_path)
    if status is TrialStatus.PASSED and manifest.activation_required and activation_count == 0:
        status = TrialStatus.FAILED
        reason = "nova_active arm produced no activation log"
    if status is TrialStatus.PASSED and manifest.activation_forbidden and activation_count > 0:
        status = TrialStatus.FAILED
        reason = "non-active arm produced activation metadata"

    result = {
        "trial_id": manifest.trial_id,
        "arm": manifest.arm.value,
        "status": status.value,
        "reason": reason,
        "manifest": manifest.to_record(),
        "commands": commands,
        "activation_count": activation_count,
        "hermes_home": str(hermes_home),
        "duration_seconds": time.time() - started,
        "metrics": {
            "success": status is TrialStatus.PASSED,
            "wall_time_seconds": time.time() - started,
            **dict(manifest.outcome_metrics),
        },
    }
    trial_dir.mkdir(parents=True, exist_ok=True)
    result_path = trial_dir / "trial_result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def replay_trial(
    trial_or_result_path: str | Path,
    *,
    exclude_artifact_id: str,
    output_dir: str | Path,
) -> dict[str, Any]:
    data = _read_json_or_yaml(Path(trial_or_result_path))
    manifest_data = data.get("manifest", data) if isinstance(data, Mapping) else data
    manifest = TrialManifest.from_mapping(manifest_data)
    replay_manifest = TrialManifest.from_mapping(
        {
            **manifest.to_record(),
            "trial_id": f"{manifest.trial_id}-replay-{uuid.uuid4().hex[:8]}",
            "exclude_artifact_ids": sorted(
                set(manifest.exclude_artifact_ids) | {str(exclude_artifact_id)}
            ),
            "metadata": {
                **dict(manifest.metadata),
                "replay_of": manifest.trial_id,
                "excluded_artifact_id": str(exclude_artifact_id),
            },
        }
    )
    result = run_trial(replay_manifest, output_dir)
    result["replay"] = {
        "original_trial_id": manifest.trial_id,
        "excluded_artifact_id": str(exclude_artifact_id),
    }
    result_path = (
        Path(output_dir)
        / replay_manifest.arm.value
        / replay_manifest.trial_id
        / "trial_result.json"
    )
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def load_results(path: str | Path) -> list[dict[str, Any]]:
    base = Path(path)
    if base.is_file():
        data = _read_json_or_yaml(base)
        if isinstance(data, Mapping) and "results" in data:
            return list(data["results"])
        if isinstance(data, list):
            return list(data)
        return [dict(data)]
    return [
        json.loads(result_path.read_text(encoding="utf-8"))
        for result_path in sorted(base.glob("**/trial_result.json"))
    ]


def analyze_results(
    results: Iterable[Mapping[str, Any]],
    *,
    min_trials_per_arm: int = 2,
) -> dict[str, Any]:
    rows = [dict(row) for row in results]
    by_arm: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_arm.setdefault(str(row.get("arm")), []).append(row)
    required_arms = [
        ExperimentArm.ADJACENT_ONLY.value,
        ExperimentArm.NOVA_STAGED.value,
        ExperimentArm.NOVA_ACTIVE.value,
    ]
    blockers: list[str] = []
    for arm in required_arms:
        if len(by_arm.get(arm, ())) < min_trials_per_arm:
            blockers.append(f"{arm} has fewer than {min_trials_per_arm} trials")
    missing_metrics = _missing_required_metrics(by_arm)
    if missing_metrics:
        blockers.extend(f"missing metric: {name}" for name in missing_metrics)
    if not blockers:
        blockers.extend(_threshold_evidence_blockers(by_arm))
    if blockers:
        return {
            "recommendation": Recommendation.INCONCLUSIVE.value,
            "reason": "insufficient evidence for configured thresholds",
            "blockers": blockers,
            "arm_counts": {arm: len(values) for arm, values in by_arm.items()},
        }

    metrics = _compute_metrics(by_arm)
    failed: list[str] = []
    if metrics["repeated_error_reduction_vs_adjacent"] < 0.20:
        failed.append("repeated-error reduction below 20% versus adjacent-only")
    if metrics["debug_time_reduction_vs_adjacent"] < 0.15:
        failed.append("median debug-time reduction below 15% versus adjacent-only")
    if not metrics["active_beats_staged"]:
        failed.append("nova_active does not beat nova_staged")
    if metrics["token_overhead_vs_adjacent"] > 0.15:
        failed.append("token overhead above 15% versus adjacent-only")
    if metrics["time_overhead_vs_adjacent"] > 0.15:
        failed.append("wall-time overhead above 15% versus adjacent-only")
    if metrics["activation_precision"] < 0.70:
        failed.append("activation precision below 70%")
    if metrics["bad_artifact_attribution"] < 0.70:
        failed.append("bad-artifact attribution below 70%")
    if metrics["demotion_effectiveness"] < 0.70:
        failed.append("demotion effectiveness below 70%")

    if not failed:
        recommendation = Recommendation.CONTINUE
        reason = "configured RES-11 thresholds passed"
    elif "nova_active does not beat nova_staged" in failed:
        recommendation = Recommendation.STOP
        reason = "staged governance matches or beats activation"
    elif any("overhead" in item for item in failed):
        recommendation = Recommendation.SHRINK
        reason = "activation value is not high enough for its overhead"
    else:
        recommendation = Recommendation.STOP
        reason = "activation did not beat the strong adjacent baseline"
    return {
        "recommendation": recommendation.value,
        "reason": reason,
        "failed_thresholds": failed,
        "metrics": metrics,
        "arm_counts": {arm: len(values) for arm, values in by_arm.items()},
    }


def _write_arm_config(
    manifest: TrialManifest,
    hermes_home: Path,
    artifact_path: Path,
    activation_log_path: Path,
) -> None:
    nova_mode = "shadow" if manifest.arm in {
        ExperimentArm.NOVA_STAGED,
        ExperimentArm.NOVA_ACTIVE,
        ExperimentArm.SHADOW_PROJECTOR,
    } else "disabled"
    config = {
        "nova": {
            "mode": nova_mode,
            "kernel_db_path": str(hermes_home / "nova" / "kernel.db"),
            "skill_artifacts": {
                "enabled": manifest.arm is ExperimentArm.NOVA_ACTIVE,
                "artifact_store_path": str(artifact_path),
                "activation_log_path": str(activation_log_path),
                "repo_scope": repo_scope_for_path(manifest.repo),
                "benchmark_chain_id": manifest.chain_id,
                "exclude_artifact_ids": list(manifest.exclude_artifact_ids),
                "strict": True,
                "require_match": manifest.arm is ExperimentArm.NOVA_ACTIVE,
            },
        },
    }
    hermes_home.mkdir(parents=True, exist_ok=True)
    (hermes_home / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=True), encoding="utf-8")


def _activation_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _read_json_or_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def _tail(value: str, *, limit: int = 4000) -> str:
    text = value if isinstance(value, str) else value.decode("utf-8", errors="replace")
    return text[-limit:]


def _missing_required_metrics(by_arm: Mapping[str, list[dict[str, Any]]]) -> list[str]:
    missing: list[str] = []
    required_by_arm = {
        ExperimentArm.ADJACENT_ONLY.value: (
            "repeated_error",
            "debug_time_seconds",
            "token_count",
            "wall_time_seconds",
        ),
        ExperimentArm.NOVA_STAGED.value: (
            "repeated_error",
            "debug_time_seconds",
        ),
        ExperimentArm.NOVA_ACTIVE.value: (
            "repeated_error",
            "debug_time_seconds",
            "token_count",
            "wall_time_seconds",
            "activation_relevant",
            "bad_artifact_attributed",
            "demotion_effective",
        ),
    }
    bool_metrics = {
        "activation_relevant",
        "bad_artifact_attributed",
        "demotion_effective",
        "repeated_error",
    }
    numeric_metrics = {
        "debug_time_seconds",
        "token_count",
        "wall_time_seconds",
    }
    for arm, names in required_by_arm.items():
        for name in names:
            for row in by_arm.get(arm, ()):
                metrics = row.get("metrics", {})
                if name not in metrics:
                    missing.append(f"{arm}.{name}")
                    continue
                value = metrics[name]
                if name in bool_metrics and not isinstance(value, bool):
                    missing.append(f"{arm}.{name} must be boolean")
                if (
                    name in numeric_metrics
                    and (not isinstance(value, (int, float)) or isinstance(value, bool))
                ):
                    missing.append(f"{arm}.{name} must be numeric")
    return sorted(set(missing))


def _threshold_evidence_blockers(by_arm: Mapping[str, list[dict[str, Any]]]) -> list[str]:
    adjacent = by_arm[ExperimentArm.ADJACENT_ONLY.value]
    blockers: list[str] = []
    if _rate(adjacent, "repeated_error") <= 0:
        blockers.append(
            "adjacent-only repeated-error rate is zero; reduction threshold cannot be evaluated"
        )
    if _median(adjacent, "debug_time_seconds") <= 0:
        blockers.append(
            "adjacent-only median debug time is zero; reduction threshold cannot be evaluated"
        )
    if _median(adjacent, "token_count") <= 0:
        blockers.append("adjacent-only token count is zero; overhead threshold cannot be evaluated")
    if _median(adjacent, "wall_time_seconds") <= 0:
        blockers.append("adjacent-only wall time is zero; overhead threshold cannot be evaluated")
    return blockers


def _compute_metrics(by_arm: Mapping[str, list[dict[str, Any]]]) -> dict[str, float | bool]:
    adjacent = by_arm[ExperimentArm.ADJACENT_ONLY.value]
    staged = by_arm[ExperimentArm.NOVA_STAGED.value]
    active = by_arm[ExperimentArm.NOVA_ACTIVE.value]
    adj_error = _rate(adjacent, "repeated_error")
    active_error = _rate(active, "repeated_error")
    staged_error = _rate(staged, "repeated_error")
    adj_debug = _median(adjacent, "debug_time_seconds")
    active_debug = _median(active, "debug_time_seconds")
    staged_debug = _median(staged, "debug_time_seconds")
    return {
        "repeated_error_reduction_vs_adjacent": _reduction(adj_error, active_error),
        "debug_time_reduction_vs_adjacent": _reduction(adj_debug, active_debug),
        "active_beats_staged": (
            (active_error < staged_error or active_debug < staged_debug)
            and active_error <= staged_error
            and active_debug <= staged_debug
        ),
        "token_overhead_vs_adjacent": _overhead(
            _median(adjacent, "token_count"),
            _median(active, "token_count"),
        ),
        "time_overhead_vs_adjacent": _overhead(
            _median(adjacent, "wall_time_seconds"),
            _median(active, "wall_time_seconds"),
        ),
        "activation_precision": _rate(active, "activation_relevant"),
        "bad_artifact_attribution": _rate(active, "bad_artifact_attributed"),
        "demotion_effectiveness": _rate(active, "demotion_effective"),
    }


def _rate(rows: Iterable[Mapping[str, Any]], metric: str) -> float:
    values = [row["metrics"][metric] is True for row in rows]
    return sum(1 for value in values if value) / len(values)


def _median(rows: Iterable[Mapping[str, Any]], metric: str) -> float:
    return float(statistics.median(float(row["metrics"][metric]) for row in rows))


def _reduction(base: float, treatment: float) -> float:
    if base <= 0:
        return 0.0
    return (base - treatment) / base


def _overhead(base: float, treatment: float) -> float:
    if base <= 0:
        return 0.0
    return (treatment - base) / base


__all__ = [
    "ExperimentArm",
    "Recommendation",
    "TrialManifest",
    "TrialStatus",
    "analyze_results",
    "load_manifests",
    "load_results",
    "replay_trial",
    "run_trial",
]
