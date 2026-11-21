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
from model_ELM.three_stage_gpp_release import preflight, validate_raw
from model_ELM.three_stage_spinup_release import balanced_split_manifest, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    attempt = args.attempt_directory
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot identity mismatch")
    require(sha256_file(Path(config["selection_report"])) == config["selection_report_sha256"], "selection report mismatch")
    selection = json.loads(Path(config["selection_report"]).read_text(encoding="utf-8"))
    require(selection["best_candidate_id"] == 21, "selected candidate mismatch")
    require(selection["decision"] == "configuration_selected_gate_pass", "selection decision mismatch")

    reference_path = Path(config["reference_split_manifest"])
    require(sha256_file(reference_path) == config["reference_split_manifest_sha256"], "reference split hash mismatch")
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    fresh = balanced_split_manifest(snapshot.development_ranked, seed=int(config["repeated_split_seed"]))
    old_validation = {frozenset(item["validation_member_ids"]) for item in reference["splits"]}
    new_validation = [frozenset(item["validation_member_ids"]) for item in fresh["splits"]]
    require(len(set(new_validation)) == 20, "fresh split duplicate")
    require(all(item not in old_validation for item in new_validation), "fresh split matches selection split")
    split_path = attempt / "repeated_split_manifest.json"
    write_json(split_path, fresh)

    resolved = dict(config)
    resolved["repeated_split_manifest_sha256"] = sha256_file(split_path)
    resolved["split_design_sha256"] = fresh["split_design_sha256"]
    resolved_path = attempt / "resolved_config.json"
    write_json(resolved_path, resolved)

    preflight_report = preflight(resolved, attempt / "preflight")
    raw_path = Path(resolved["raw_directory"])
    raw_report = validate_raw(resolved, raw_path, full_hashes=True)
    layout = json.loads((raw_path / "layout.json").read_text(encoding="utf-8"))
    manifest = json.loads((raw_path / "raw_manifest.json").read_text(encoding="utf-8"))
    require(sha256_file(raw_path / "layout.json") == resolved["raw_layout_sha256"], "raw layout hash mismatch")
    require(manifest["x_sha256"] == resolved["raw_x_sha256"], "raw X identity mismatch")
    require(manifest["y_sha256"] == resolved["raw_y_sha256"], "raw y identity mismatch")
    require(manifest["time_sha256"] == resolved["raw_time_sha256"], "raw time identity mismatch")
    require(layout["features"] == 43 and len(layout["development_member_ids"]) == 819, "raw layout scope mismatch")
    write_json(attempt / "raw_validation_report.json", raw_report)
    write_json(attempt / "preflight_identity.json", {
        "schema": "three-stage-gpp-iter008-preflight-identity-v1",
        "result": "pass",
        "resolved_config_sha256": sha256_file(resolved_path),
        "repeated_split_manifest_sha256": sha256_file(split_path),
        "split_design_sha256": fresh["split_design_sha256"],
        "reference_matching_validation_sets": 0,
        "performance_gate_applied": False,
        "release_basis": "iter007_best_configuration",
        "preflight_report": preflight_report,
        "raw_validation": raw_report,
    })
    (attempt / "ELIGIBLE").touch()
    print(
        "ITER008_PREFLIGHT_OK "
        f"splits=20 split_sha256={sha256_file(split_path)} "
        f"config_sha256={sha256_file(resolved_path)} no_training=true",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
