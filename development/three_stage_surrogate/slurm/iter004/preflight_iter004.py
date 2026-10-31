#!/usr/bin/env python
"""No-training Iter004 preflight and immutable split materialization."""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, schema_sha256, sha256_file
from model_ELM.three_stage_spinup_release import MODEL_CONFIG, RELEASE_SCHEMA, balanced_split_manifest, split_design_sha256, validate_release_artifact, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    require(1 <= args.attempt <= 4, "attempt must be in 1..4")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-spinup-iter004-config-v1", "config schema mismatch")
    require(config["fixed_test_allowed"] is False, "fixed-test boundary mismatch")
    require(config["model_config"] == MODEL_CONFIG, "model configuration mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split hash mismatch")
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=False)
    split_manifest = balanced_split_manifest(snapshot.development_ranked)
    split_path = output / "repeated_split_manifest.json"
    write_json(split_path, split_manifest)
    # Lightweight schema and pickle fixtures; no estimator is fit.
    fixture = {
        "schema": RELEASE_SCHEMA, "artifact_role": "published_spinup_inference",
        "target_order": ["TOTSOMC", "TOTSOMN"], "target_transform": "natural_log",
        "models": {"TOTSOMC": object(), "TOTSOMN": object()},
        "x_scalers": {"TOTSOMC": object(), "TOTSOMN": object()},
        "y_scalers": {"TOTSOMC": object(), "TOTSOMN": object()},
        "model_config": MODEL_CONFIG, "sites": ["ABBY", "JERC"],
        "feature_names": list(snapshot.feature_names), "feature_schema_sha256": schema_sha256(snapshot.feature_names),
        "fit_scope": {"development_member_ids": list(snapshot.development_ranked), "training_rows": 1638, "fixed_test_access": False},
        "snapshot_sha256": snapshot.snapshot_sha256,
    }
    validate_release_artifact(fixture)
    fixture_path = output / "serialization_fixture.pkl"
    with fixture_path.open("xb") as handle:
        pickle.dump(fixture, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with fixture_path.open("rb") as handle:
        validate_release_artifact(pickle.load(handle))
    nc_path = output / "netcdf_contract_fixture.nc"
    with Dataset(str(nc_path), "w", clobber=False, format="NETCDF4") as dataset:
        dataset.createDimension("site", 2)
        dataset.createDimension("member", 2)
        dataset.createVariable("site", str, ("site",))[:] = np.asarray(["ABBY", "JERC"], dtype=object)
        dataset.createVariable("member_id", str, ("member",))[:] = np.asarray(snapshot.development_ranked[:2], dtype=object)
        for target in ("TOTSOMC", "TOTSOMN"):
            variable = dataset.createVariable(f"{target}_predicted", "f8", ("site", "member"))
            variable[:] = np.ones((2, 2))
    with Dataset(str(nc_path), "r") as dataset:
        require(set(dataset.variables) == {"site", "member_id", "TOTSOMC_predicted", "TOTSOMN_predicted"}, "NetCDF fixture mismatch")
    report = {
        "schema": "three-stage-spinup-iter004-preflight-v1", "result": "pass", "attempt": args.attempt,
        "no_training": True, "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": sha256_file(snapshot.split_path), "split_manifest_sha256": sha256_file(split_path),
        "split_design_sha256": split_design_sha256(split_manifest), "split_count": 20,
        "serialization_fixture_sha256": sha256_file(fixture_path), "netcdf_fixture_sha256": sha256_file(nc_path),
    }
    write_json(output / "preflight_report.json", report)
    print(f"ITER004_PREFLIGHT_OK splits=20 split_sha256={report['split_manifest_sha256']} no_training=true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
