#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter011.iter011_common import load_candidates, smoke, validate_contract
from model_ELM.three_stage_data import ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_release import balanced_split_manifest
from model_ELM.three_stage_sr import write_json


def validation_sets(payload):
    return [frozenset(item["validation_member_ids"]) for item in payload["splits"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output_directory.exists(), f"output exists: {args.output_directory}")
    args.output_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split mismatch")
    load_candidates(config)
    fresh = balanced_split_manifest(snapshot.development_ranked, seed=int(config["repeated_split_seed"]))
    fresh_sets = validation_sets(fresh)
    require(len(fresh_sets) == len(set(fresh_sets)) == 20, "fresh splits not unique")
    prior_sets = []
    for path_key, hash_key in (("iter009_split_manifest", "iter009_split_manifest_sha256"), ("iter010_split_manifest", "iter010_split_manifest_sha256")):
        path = Path(config[path_key])
        require(sha256_file(path) == config[hash_key], f"prior split mismatch: {path_key}")
        prior_sets.extend(validation_sets(json.loads(path.read_text(encoding="utf-8"))))
    require(all(item not in set(prior_sets) for item in fresh_sets), "fresh split exactly matches prior SR split")
    split_path = args.output_directory / "repeated_split_manifest.json"
    write_json(split_path, fresh)
    resolved = dict(config)
    resolved.update(repeated_split_manifest=str(split_path.resolve()), repeated_split_manifest_sha256=sha256_file(split_path), split_design_sha256=fresh["split_design_sha256"])
    resolved_path = args.output_directory / "resolved_config.json"
    write_json(resolved_path, resolved)
    contract = validate_contract(resolved, full_raw_hashes=True)
    smoke_report = smoke(resolved, args.output_directory / "smoke")
    counts = {member: 0 for member in snapshot.development_ranked}
    for item in fresh["splits"]:
        require(len(item["train_member_ids"]) == 655 and len(item["validation_member_ids"]) == 164, "split size mismatch")
        for member in item["validation_member_ids"]:
            counts[member] += 1
    require(set(counts.values()).issubset({4, 5}), "split balance mismatch")
    report = {"schema": "three-stage-sr-iter011-unit1-v1", "result": "pass", "preflight": "pass", "no_production_training": True, "split_seed": int(config["repeated_split_seed"]), "fresh_splits": 20, "prior_exact_matches": 0, "candidate_count": 5, "production_fit_count": 100, "contract_validation": contract["result"], "smoke": smoke_report["result"], "raw_full_hashes": True, "resolved_config_sha256": sha256_file(resolved_path), "split_manifest_sha256": sha256_file(split_path), "split_design_sha256": fresh["split_design_sha256"], "fixed_test_access": False, "release_created": False}
    write_json(args.output_directory / "unit1_report.json", report)
    (args.output_directory / "ELIGIBLE").touch()
    print("ITER011_UNIT1_OK candidates=5 splits=20 production_fits=100 fixed_test=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
