#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_gpp_release import aggregate, validate_aggregate, validate_release
from model_ELM.three_stage_spinup_release import write_json

UNCERTAINTY_FILES = (
    "gpp_uncertainty.nc",
    "metric_distribution.csv",
    "uncertainty_estimates.csv",
    "repeated_split_manifest.json",
    "convergence.json",
    "uncertainty_report.json",
    "aggregate_validation.json",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--robustness-directory", required=True, type=Path)
    parser.add_argument("--release-core", required=True, type=Path)
    parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    attempt = args.attempt_directory

    aggregate_dir = attempt / "aggregate"
    aggregate_report = aggregate(config, args.robustness_directory, aggregate_dir)
    validated_aggregate = validate_aggregate(config, args.robustness_directory, aggregate_dir)
    require(aggregate_report["gate"]["result"] == "not_applicable", "performance gate unexpectedly applied")
    require(validated_aggregate["result"] == "pass", "aggregate validation failed")

    assembled = attempt / "assembled_release_0001"
    shutil.copytree(args.release_core, assembled)
    for name in UNCERTAINTY_FILES:
        shutil.copy2(aggregate_dir / name, assembled / "uncertainty" / name)

    validation_dir = attempt / "validation"
    validation_report = validate_release(config, Path(config["raw_directory"]), assembled, validation_dir)
    validated_release = validation_dir / "release_0001"
    release_manifest = validated_release / "release_manifest.json"
    require(release_manifest.is_file(), "release manifest missing")
    report = {
        "schema": "three-stage-gpp-iter008-final-v1",
        "result": "pass",
        "performance_gate_applied": False,
        "release_basis": "iter007_best_configuration",
        "metric_rows": validated_aggregate["metric_rows"],
        "uncertainty_rows": validated_aggregate["uncertainty_rows"],
        "artifact_sha256": validation_report["artifact_sha256"],
        "handoff_sha256": validation_report["handoff_sha256"],
        "release_manifest_sha256": sha256_file(release_manifest),
        "fixed_test_access": False,
    }
    write_json(attempt / "final_report.json", report)
    print(
        "ITER008_FINAL_VALIDATE_OK "
        f"metrics={report['metric_rows']} uncertainty={report['uncertainty_rows']} "
        f"artifact={report['artifact_sha256']} handoff={report['handoff_sha256']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
