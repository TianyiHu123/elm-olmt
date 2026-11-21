#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_sr import write_json
from model_ELM.three_stage_sr_release import validate_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--release-core", required=True, type=Path)
    parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    validation_dir = args.attempt_directory / "validation"
    report = validate_release(config, Path(config["raw_directory"]), args.release_core, validation_dir)
    require(report["result"] == "pass" and report["raw_interface_replay_complete"] is True, "release validation failed")
    require(report["raw_interface_replay_count"] == 100442160, "release replay count mismatch")
    release = validation_dir / "release_0001"
    final = {
        "schema": "three-stage-sr-iter013-final-v1", "result": "pass",
        "performance_gate_applied": False, "release_basis": config["release_basis"],
        "artifact_sha256": report["artifact_sha256"], "predictions_sha256": report["handoff_sha256"],
        "release_manifest_sha256": sha256_file(release / "release_manifest.json"),
        "prediction_count": report["raw_interface_replay_count"], "fixed_test_access": False,
    }
    write_json(args.attempt_directory / "final_report.json", final)
    print(f"ITER013_FINAL_VALIDATE_OK artifact={final['artifact_sha256']} predictions={final['predictions_sha256']} count={final['prediction_count']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
