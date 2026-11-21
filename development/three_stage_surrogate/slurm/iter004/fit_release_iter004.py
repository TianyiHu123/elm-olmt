#!/usr/bin/env python
"""Fit the frozen all-development release and stage its handoff package."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require
from model_ELM.three_stage_spinup_release import copy_uncertainty_to_staging, fit_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--uncertainty-directory", required=True, type=Path)
    parser.add_argument("--staging-directory", required=True, type=Path)
    parser.add_argument("--source-manifest-sha256", required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["fixed_test_allowed"] is False, "fixed-test boundary mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    report = fit_release(snapshot, args.staging_directory, {
        "repository_base_commit": config["repository_base_commit"],
        "source_manifest_sha256": args.source_manifest_sha256,
        "plan_sha256": config["plan_sha256"],
    })
    copy_uncertainty_to_staging(args.uncertainty_directory, args.staging_directory)
    print(f"ITER004_RELEASE_FIT_OK artifact_sha256={report['artifact_sha256']} members=819", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
