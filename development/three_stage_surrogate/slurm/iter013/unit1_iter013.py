#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_release import balanced_split_manifest, write_json
from model_ELM.three_stage_sr import FEATURE_COUNT
from model_ELM.three_stage_sr_release import fit_split, preflight, validate_raw


def validation_sets(payload):
    return [frozenset(item["validation_member_ids"]) for item in payload["splits"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.attempt_directory.exists(), f"attempt exists: {args.attempt_directory}")
    args.attempt_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["schema"] == "three-stage-sr-iter013-config-v1", "config schema mismatch")
    for key in ("fixed_test_allowed", "spinup_execution_allowed", "gpp_execution_allowed", "full_chain_robustness_allowed"):
        require(config[key] is False, f"scope boundary mismatch: {key}")
    require(sha256_file(REPO_ROOT / "development/three_stage_surrogate/PLAN.md") == config["plan_sha256"], "plan identity mismatch")
    require(sha256_file(Path(config["sr_configuration_file"])) == config["sr_configuration_sha256"], "SR configuration identity mismatch")
    frozen = json.loads(Path(config["sr_configuration_file"]).read_text(encoding="utf-8"))
    require(frozen["selection_decision"] == "deployable_arm_B_selected", "selection decision mismatch")
    require(frozen["feature_count"] == FEATURE_COUNT == 44, "feature count mismatch")
    require(frozen["gpp_input"] == "published_predicted_same_hour", "GPP input mismatch")
    require(frozen["model_config"] == config["model_config"], "model configuration mismatch")

    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "global split mismatch")
    fresh = balanced_split_manifest(snapshot.development_ranked, seed=int(config["repeated_split_seed"]))
    fresh_sets = validation_sets(fresh)
    require(len(fresh_sets) == len(set(fresh_sets)) == 20, "fresh split uniqueness mismatch")
    prior_sets = set()
    for item in config["prior_split_manifests"]:
        path = Path(item["path"])
        require(sha256_file(path) == item["sha256"], f"prior split identity mismatch: {path}")
        prior_sets.update(validation_sets(json.loads(path.read_text(encoding="utf-8"))))
    require(all(item not in prior_sets for item in fresh_sets), "fresh split exactly matches prior split")
    split_path = args.attempt_directory / "repeated_split_manifest.json"
    write_json(split_path, fresh)

    resolved = dict(config)
    resolved.update(
        repeated_split_manifest=str(split_path.resolve()),
        repeated_split_manifest_sha256=sha256_file(split_path),
        split_design_sha256=fresh["split_design_sha256"],
    )
    resolved_path = args.attempt_directory / "resolved_config.json"
    write_json(resolved_path, resolved)
    preflight_report = preflight(resolved, args.attempt_directory / "preflight")
    raw_report = validate_raw(resolved, Path(resolved["raw_directory"]), full_hashes=True)
    raw_manifest = json.loads((Path(resolved["raw_directory"]) / "raw_manifest.json").read_text(encoding="utf-8"))
    for field, key in (("layout_sha256", "raw_layout_sha256"), ("x_sha256", "raw_x_sha256"), ("y_sha256", "raw_y_sha256"), ("time_sha256", "raw_time_sha256")):
        require(raw_manifest[field] == resolved[key], f"raw identity mismatch: {field}")
    smoke_report = fit_split(resolved, Path(resolved["raw_directory"]), 0, args.attempt_directory / "smoke", smoke=True)
    counts = fresh["validation_appearance_counts"]
    require(sum(int(value) == 4 for value in counts.values()) == 815, "four-appearance balance mismatch")
    require(sum(int(value) == 5 for value in counts.values()) == 4, "five-appearance balance mismatch")
    report = {
        "schema": "three-stage-sr-iter013-unit1-v1", "result": "pass", "no_production_training": True,
        "split_seed": int(config["repeated_split_seed"]), "fresh_splits": 20, "prior_exact_matches": 0,
        "production_fit_count": 20, "feature_count": FEATURE_COUNT,
        "preflight": preflight_report["result"], "raw_validation": raw_report["result"], "smoke": smoke_report["result"],
        "resolved_config_sha256": sha256_file(resolved_path), "split_manifest_sha256": sha256_file(split_path),
        "split_design_sha256": fresh["split_design_sha256"], "raw_full_hashes": True,
        "fixed_test_access": False, "spinup_execution": False, "gpp_execution": False,
        "full_chain_robustness": False, "release_created": False,
    }
    write_json(args.attempt_directory / "unit1_report.json", report)
    (args.attempt_directory / "ELIGIBLE").touch()
    print("ITER013_UNIT1_OK splits=20 production_fits=20 features=44 fixed_test=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
