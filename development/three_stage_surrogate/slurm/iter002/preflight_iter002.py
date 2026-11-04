from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, schema_sha256
from model_ELM.three_stage_spinup import MODEL_CONFIG


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be in 1..4")
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-spinup-iter002-config-v1", "config schema mismatch")
    require(Path(config["repository_root"]).resolve() == REPO_ROOT, "repository root mismatch")
    require(config["model"] == MODEL_CONFIG, "model config mismatch")
    require(config["target_transform"] == "natural_log", "target transform mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    require(len(snapshot.feature_names) == 25, "feature count mismatch")
    require(schema_sha256(snapshot.feature_names), "empty feature schema hash")
    smoke_train, smoke_validation = snapshot.smoke_split()
    operational_train, operational_validation = snapshot.operational_split()
    require(smoke_train == operational_train[:80], "smoke train is not nested")
    require(smoke_validation == operational_validation[:20], "smoke validation is not nested")
    require(len(operational_train) == 655 and len(operational_validation) == 164, "operational split mismatch")
    train_rows = snapshot.load_rows(smoke_train[:2], include_targets=True)
    validation_rows = snapshot.load_rows(smoke_validation[:2], include_targets=True)
    require(train_rows.X.shape == (4, 25) and validation_rows.X.shape == (4, 25), "real-data row shape mismatch")
    require(train_rows.y is not None and np.all(train_rows.y > 0.0), "real train targets invalid")
    try:
        snapshot.load_rows([snapshot.fixed_test_ranked[0]], include_targets=True)
    except ValueError as error:
        require("outside development partition" in str(error), "fixed-test rejection reason mismatch")
    else:
        raise ValueError("fixed-test member was not rejected")
    report = {
        "schema": "three-stage-spinup-preflight-v1",
        "result": "pass",
        "attempt": args.attempt,
        "python_executable": sys.executable,
        "python_prefix": sys.prefix,
        "snapshot_sha256": snapshot.snapshot_sha256,
        "feature_names": list(snapshot.feature_names),
        "feature_schema_sha256": schema_sha256(snapshot.feature_names),
        "target_transform": "natural_log",
        "smoke": {"train": 80, "validation": 20},
        "operational": {"train": 655, "validation": 164},
        "fixed_test_rejected": True,
        "execution_manifest_sha256": os.environ.get("ITER002_EXECUTION_MANIFEST_SHA256"),
        "config_sha256": os.environ.get("ITER002_CONFIG_SHA256"),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }
    destination = args.run_dir.resolve() / f"attempt_{args.attempt}" / "preflight_report.json"
    destination.parent.mkdir(parents=True, exist_ok=False)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"ITER002_PREFLIGHT_OK attempt={args.attempt} features=25 smoke=80/20 "
        "operational=655/164 fixed_test_rejected=true",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
