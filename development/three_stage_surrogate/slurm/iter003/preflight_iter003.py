#!/usr/bin/env python
"""No-training Iter003 contract validation and manifest materialization."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_screen import balanced_split_manifest, candidate_manifest


def write_new(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be in 1..4")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-spinup-iter003-config-v1", "config schema mismatch")
    require(config["candidate_count"] == 96 and config["array_range"] == "0-95", "array contract mismatch")
    require(config["array_concurrency_cap"] is None, "array must be unthrottled")
    require(config["fixed_test_allowed"] is False, "fixed-test boundary mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split hash mismatch")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=False)
    candidates_path = output / "candidate_manifest.json"
    splits_path = output / "repeated_split_manifest.json"
    write_new(candidates_path, candidate_manifest())
    write_new(splits_path, balanced_split_manifest(snapshot.development_ranked))
    report = {
        "schema": "three-stage-spinup-iter003-preflight-v1",
        "result": "pass",
        "attempt": args.attempt,
        "no_training": True,
        "candidate_count": 96,
        "split_count": 20,
        "candidate_manifest_sha256": sha256_file(candidates_path),
        "split_manifest_sha256": sha256_file(splits_path),
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": sha256_file(snapshot.split_path),
    }
    write_new(output / "preflight_report.json", report)
    print("ITER003_PREFLIGHT_OK candidates=96 splits=20 no_training=true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
