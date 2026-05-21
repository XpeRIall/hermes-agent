#!/usr/bin/env python
"""Run and analyze RES-11 Nova counterfactual experiment trials."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent.nova.experiment import (
    analyze_results,
    load_manifests,
    load_results,
    replay_trial,
    run_trial,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one manifest or manifest set")
    run_parser.add_argument("--manifest", required=True, help="JSON/YAML trial manifest")
    run_parser.add_argument("--output-dir", required=True, help="directory for trial outputs")

    replay_parser = subparsers.add_parser("replay", help="rerun a trial with an artifact excluded")
    replay_parser.add_argument("--trial", required=True, help="trial manifest or trial_result.json")
    replay_parser.add_argument("--exclude-artifact", required=True, help="artifact id to exclude")
    replay_parser.add_argument("--output-dir", required=True, help="directory for replay outputs")

    analyze_parser = subparsers.add_parser("analyze", help="analyze trial_result.json outputs")
    analyze_parser.add_argument("--results", required=True, help="result file or output directory")
    analyze_parser.add_argument("--min-trials-per-arm", type=int, default=2)

    args = parser.parse_args()
    if args.command == "run":
        results = [
            run_trial(manifest, args.output_dir)
            for manifest in load_manifests(args.manifest)
        ]
        print(json.dumps({"results": results}, indent=2, sort_keys=True))
        return 0
    if args.command == "replay":
        result = replay_trial(
            args.trial,
            exclude_artifact_id=args.exclude_artifact,
            output_dir=args.output_dir,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "analyze":
        result = analyze_results(
            load_results(Path(args.results)),
            min_trials_per_arm=args.min_trials_per_arm,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
