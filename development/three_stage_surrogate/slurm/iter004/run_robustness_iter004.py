#!/usr/bin/env python
"""Run the frozen Iter004 candidate over all fresh robustness splits."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_release import run_robustness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--split-manifest", required=True, type=Path)
    parser.add_argument("--split-sha256", required=True)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["fixed_test_allowed"] is False, "fixed-test boundary mismatch")
    require(sha256_file(args.split_manifest) == args.split_sha256, "split file hash mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    report = run_robustness(snapshot, json.loads(args.split_manifest.read_text(encoding="utf-8")), args.output_directory)
    print(f"ITER004_ROBUSTNESS_OK observations={report['observation_count']} warnings={report['convergence_warning_count']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
