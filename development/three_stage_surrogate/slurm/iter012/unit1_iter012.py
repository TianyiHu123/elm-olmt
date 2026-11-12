#!/usr/bin/env python
"""Iter012 identity preflight, split preparation, true-GPP alignment, and smoke."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from development.three_stage_surrogate.slurm.iter012.iter012_common import (
    expected_feature_schemas,
    load_arms,
    smoke,
    validate_contract,
)
from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_sr import HOURS, write_json
from model_ELM.three_stage_sr_release import DEVELOPMENT_MEMBERS, load_raw
from model_ELM.three_stage_spinup_release import balanced_split_manifest


def validation_sets(path: Path) -> list[frozenset[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [frozenset(item["validation_member_ids"]) for item in payload["splits"]]


def prepare_true_gpp(config, snapshot, raw_times, output):
    path = output / "true_gpp_float32.dat"
    values = np.memmap(path, mode="w+", dtype=np.float32, shape=(len(SITES), DEVELOPMENT_MEMBERS, HOURS))
    source_rows = []
    for site_index, site in enumerate(SITES):
        source = snapshot.root / "sites" / site / "input_data_v1.nc"
        require(sha256_file(source) == config["snapshot_site_input_sha256"][site], f"{site} source hash mismatch")
        with Dataset(str(source), "r") as dataset:
            require(str(dataset.variables["GPP"].units) == "gC/m^2/day", f"{site} GPP units mismatch")
            require(dataset.variables["GPP"].shape == (1024, HOURS), f"{site} GPP shape mismatch")
            time = np.asarray(dataset.variables["time"][:], dtype=np.int64)
            require(np.array_equal(time, raw_times[site_index]), f"{site} time alignment mismatch")
            for member_position, member in enumerate(snapshot.development_ranked):
                source_index = int(member[1:]) - 1
                row = np.asarray(dataset.variables["GPP"][source_index, :], dtype=np.float32)
                require(row.shape == (HOURS,) and np.all(np.isfinite(row)), f"{site}/{member} GPP invalid")
                values[site_index, member_position] = row
            source_rows.append({"site": site, "source": str(source), "sha256": config["snapshot_site_input_sha256"][site], "units": "gC/m^2/day", "members": DEVELOPMENT_MEMBERS, "hours": HOURS})
    values.flush()
    true_hash = sha256_file(path)
    write_json(output / "true_gpp_manifest.json", {"schema": "three-stage-sr-iter012-true-gpp-v1", "file": path.name, "sha256": true_hash, "dtype": "float32", "shape": [len(SITES), DEVELOPMENT_MEMBERS, HOURS], "member_order": list(snapshot.development_ranked), "sources": source_rows, "fixed_test_access": False})
    return true_hash


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output_directory.exists(), "Unit1 output exists")
    args.output_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    load_arms(config)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split mismatch")
    fresh = balanced_split_manifest(snapshot.development_ranked, seed=int(config["repeated_split_seed"]))
    fresh_sets = validation_sets_payload = [frozenset(item["validation_member_ids"]) for item in fresh["splits"]]
    require(len(fresh_sets) == len(set(fresh_sets)) == 20, "fresh splits not unique")
    prior_sets = []
    for item in config["prior_split_manifests"]:
        path = Path(item["path"])
        require(sha256_file(path) == item["sha256"], f"prior split hash mismatch: {path}")
        prior_sets.extend(validation_sets(path))
    require(all(item not in set(prior_sets) for item in validation_sets_payload), "fresh split exactly matches prior SR split")
    counts = {member: 0 for member in snapshot.development_ranked}
    for item in fresh["splits"]:
        train = item["train_member_ids"]
        validation = item["validation_member_ids"]
        require(len(train) == 655 and len(validation) == 164, "split size mismatch")
        require(not set(train).intersection(validation), "split overlap")
        require(set(train).union(validation) == snapshot.development_set, "split coverage mismatch")
        require(not set(validation).intersection(snapshot.fixed_test_set), "fixed-test overlap")
        for member in validation:
            counts[member] += 1
    require(set(counts.values()).issubset({4, 5}), "split balance mismatch")
    split_path = args.output_directory / "repeated_split_manifest.json"
    write_json(split_path, fresh)
    schemas_path = args.output_directory / "feature_schemas.json"
    write_json(schemas_path, expected_feature_schemas(snapshot))
    _, _, _, raw_times = load_raw(Path(config["raw_directory"]))
    true_hash = prepare_true_gpp(config, snapshot, raw_times, args.output_directory)
    resolved = dict(config)
    resolved.update(
        repeated_split_manifest=str(split_path.resolve()),
        repeated_split_manifest_sha256=sha256_file(split_path),
        split_design_sha256=fresh["split_design_sha256"],
        true_gpp_file=str((args.output_directory / "true_gpp_float32.dat").resolve()),
        true_gpp_sha256=true_hash,
        feature_schemas=str(schemas_path.resolve()),
        feature_schemas_sha256=sha256_file(schemas_path),
    )
    resolved_path = args.output_directory / "resolved_config.json"
    write_json(resolved_path, resolved)
    contract = validate_contract(resolved, full_raw_hashes=True, full_true_gpp_hash=True)
    write_json(args.output_directory / "contract_validation.json", contract)
    smoke_report = smoke(resolved, args.output_directory / "smoke")
    report = {"schema": "three-stage-sr-iter012-unit1-v1", "result": "pass", "preflight": "pass", "no_production_training": True, "split_seed": int(config["repeated_split_seed"]), "fresh_splits": 20, "prior_exact_matches": 0, "validation_appearance_values": sorted(set(counts.values())), "arm_count": 3, "production_fit_count": 60, "contract_validation": contract["result"], "smoke": smoke_report["result"], "raw_full_hashes": True, "true_gpp_full_hash": True, "resolved_config_sha256": sha256_file(resolved_path), "split_manifest_sha256": sha256_file(split_path), "split_design_sha256": fresh["split_design_sha256"], "true_gpp_sha256": true_hash, "feature_schemas_sha256": sha256_file(schemas_path), "fixed_test_access": False, "release_created": False}
    write_json(args.output_directory / "unit1_report.json", report)
    (args.output_directory / "ELIGIBLE").touch()
    print("ITER012_UNIT1_OK arms=3 splits=20 production_fits=60 fixed_test=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
