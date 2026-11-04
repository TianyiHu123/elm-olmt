#!/usr/bin/env python
"""Train one locked Iter002 spinup-development work unit."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require
from model_ELM.three_stage_spinup import fit_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-kind", required=True, choices=("smoke", "operational"))
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be in 1..4")
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-spinup-iter002-config-v1", "config schema mismatch")
    require(config["target_transform"] == "natural_log", "target transform mismatch")
    require(Path(config["repository_root"]).resolve() == REPO_ROOT, "repository root mismatch")
    require(config["plan_sha256"] == "9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128", "plan hash mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "config snapshot hash mismatch")
    if args.run_kind == "smoke":
        train_members, validation_members = snapshot.smoke_split()
        run_dir = Path(config["run_directories"]["smoke"])
    else:
        train_members, validation_members = snapshot.operational_split()
        run_dir = Path(config["run_directories"]["operational"])
    package = run_dir / f"attempt_{args.attempt}" / "package"
    source_identity = {
        "repository_base_commit": config["repository_base_commit"],
        "execution_manifest_sha256": os.environ.get("ITER002_EXECUTION_MANIFEST_SHA256"),
        "config_sha256": os.environ.get("ITER002_CONFIG_SHA256"),
        "attempt": int(args.attempt),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }
    result = fit_baseline(
        snapshot,
        train_members,
        validation_members,
        run_kind=args.run_kind,
        output_directory=package,
        source_identity=source_identity,
    )
    print(
        f"ITER002_TRAIN_OK run_kind={args.run_kind} attempt={args.attempt} "
        f"train={len(train_members)} validation={len(validation_members)} "
        f"artifact_sha256={result['artifact_sha256']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
