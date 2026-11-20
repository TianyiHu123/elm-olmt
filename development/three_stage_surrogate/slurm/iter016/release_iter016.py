"""Assemble and validate the unpublished Iter016 coupled release candidate."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from netCDF4 import Dataset

from development.three_stage_surrogate.slurm.iter016.refit_iter016 import load_config, validate_config
from model_ELM.three_stage_coupled_release import CoupledThreeStageInference, load_artifacts
from model_ELM.three_stage_data import SITES, require, schema_sha256, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES
from model_ELM.three_stage_gpp import feature_names as gpp_feature_names
from model_ELM.three_stage_sr import feature_names as sr_feature_names


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_record(path: Path, expected: str) -> None:
    require(path.is_file() and sha256_file(path) == expected, f"release dependency mismatch: {path}")


def inventory(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.name != "release_manifest.json"):
        rows.append({"path": str(path.relative_to(root)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def assemble(config_path: Path, output: Path) -> dict[str, Any]:
    config = read_json(config_path)
    require(config.get("schema") == "three-stage-iter016-release-config-v1", "release config schema mismatch")
    for key in ("uncertainty_refit_allowed", "fixed_test_tuning_allowed", "historical_release_modification_allowed", "stable_publication_allowed_in_release_job"):
        require(config.get(key) is False, f"release scope mismatch: {key}")
    require(not output.exists(), f"release output exists: {output}")
    require(not Path(config["stable_product_root"]).exists(), "stable coupled product already exists")
    base_path = Path(config["base_config"]); verify_record(base_path, config["base_config_sha256"])
    base = load_config(base_path)
    snapshot = validate_config(base, verify_snapshot_components=True)
    verify_record(Path(config["recovery_report"]), config["recovery_report_sha256"])
    recovery = read_json(Path(config["recovery_report"]))
    require(recovery.get("result") == "pass" and recovery.get("additional_fitting") is False, "recovery acceptance mismatch")
    fixed_root = Path(config["fixed_test_root"])
    verify_record(fixed_root / "fixed_test_report.json", config["fixed_test_report_sha256"])
    verify_record(fixed_root / "fixed_test_predictions.nc", config["fixed_test_predictions_sha256"])
    fixed_report = read_json(fixed_root / "fixed_test_report.json")
    require(fixed_report.get("result") == "pass" and fixed_report.get("performance_threshold_applied") is False, "fixed-test acceptance mismatch")
    require(fixed_report.get("training_or_fitting") is False and fixed_report.get("configuration_selection") is False, "fixed-test scope mismatch")
    require(fixed_report.get("artifact_manifest_sha256") == config["artifact_manifest_sha256"], "fixed-test artifact mismatch")
    for record in fixed_report["files"]:
        path = fixed_root / record["path"]
        require(path.stat().st_size == int(record["size_bytes"]) and sha256_file(path) == record["sha256"], f"fixed-test file mismatch: {path.name}")
    negative_sr_count = 0
    negative_sr_minimum = np.inf
    with Dataset(str(fixed_root / "fixed_test_predictions.nc"), "r") as predictions:
        require(int(predictions.contains_elm_targets) == 0 and int(predictions.training_or_fitting) == 0, "fixed-test prediction scope mismatch")
        require(set(predictions.variables) == {"site", "member_id", "parameter_name", "parameter", "time", "TOTSOMC_predicted", "TOTSOMN_predicted", "GPP_raw", "GPP_gated", "SR_predicted"}, "fixed-test prediction inventory mismatch")
        for site_index in range(len(SITES)):
            for start in range(0, 205, 16):
                values = np.asarray(predictions.variables["SR_predicted"][site_index, start:min(start + 16, 205)], dtype=np.float32)
                negative = values[values < 0.0]
                negative_sr_count += int(negative.size)
                if negative.size:
                    negative_sr_minimum = min(negative_sr_minimum, float(np.min(negative)))
    require(negative_sr_count == 128246 and np.isclose(negative_sr_minimum, -2.2393, rtol=0.0, atol=5e-5), "fixed-test negative-SR limitation mismatch")
    for record in config["uncertainty_files"]:
        verify_record(Path(record["path"]), record["sha256"])
    for record in config["historical_releases"]:
        verify_record(Path(record["manifest"]), record["manifest_sha256"])
        verify_record(Path(record["catalog"]), record["catalog_sha256"])

    release = output / config["release_name"]
    (release / "artifact").mkdir(parents=True)
    shutil.copytree(Path(config["artifact_root"]), release / "artifact" / "coupled_artifacts")
    verify_record(release / "artifact" / "coupled_artifacts" / "artifact_manifest.json", config["artifact_manifest_sha256"])
    shutil.copytree(fixed_root, release / "evaluation" / "fixed_test")
    (release / "uncertainty").mkdir(parents=True)
    for record in config["uncertainty_files"]:
        shutil.copy2(record["path"], release / "uncertainty" / record["name"])
    (release / "provenance").mkdir(parents=True)
    shutil.copy2(base_path, release / "provenance" / "iter016_config.json")
    shutil.copy2(config_path, release / "provenance" / "iter016_release_config.json")
    shutil.copy2(config["recovery_report"], release / "provenance" / "refit_recovery_report.json")

    spinup, gpp, sr, artifact_manifest = load_artifacts(release / "artifact" / "coupled_artifacts", snapshot)
    feature_schema = {
        "schema": "three-stage-coupled-feature-schema-v1",
        "counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "names": {"spinup": list(snapshot.feature_names), "gpp": list(gpp_feature_names(snapshot)), "sr": list(sr_feature_names(snapshot))},
        "sha256": {"spinup": schema_sha256(snapshot.feature_names), "gpp": schema_sha256(gpp_feature_names(snapshot)), "sr": schema_sha256(sr_feature_names(snapshot))},
    }
    write_json(release / "interface" / "feature_schema.json", feature_schema)
    transforms = snapshot.common_manifest["sampling_metadata"]["transforms"]
    constraints = {
        "schema": "three-stage-coupled-parameter-constraints-v1",
        "parameter_order": list(snapshot.parameter_names),
        "parameters": transforms,
        "conditional_cn_constraint": snapshot.common_manifest["sampling_metadata"]["cn_constraint"],
    }
    write_json(release / "interface" / "parameter_constraints.json", constraints)
    interface = {
        "schema": "three-stage-coupled-inference-contract-v1",
        "entry_point": "model_ELM.three_stage_coupled_release.CoupledThreeStageInference",
        "artifact_directory": "artifact/coupled_artifacts",
        "sites": list(SITES),
        "forcing_variables": list(FORCING_NAMES),
        "calendar": "noleap",
        "canonical_origin": "2018-01-01 00:00:00",
        "maximum_hours": 61320,
        "nonzero_window_history_hours": 720,
        "gpp_output_policy": "hard_zero_v1",
        "contains_elm_targets": False,
        "training_or_fitting": False,
        "source_file": "model_ELM/three_stage_coupled_release.py",
        "source_sha256": sha256_file(Path(base["repository_root"]) / "model_ELM/three_stage_coupled_release.py"),
    }
    write_json(release / "interface" / "inference_contract.json", interface)
    write_json(release / "provenance" / "historical_releases.json", {
        "schema": "three-stage-coupled-historical-release-provenance-v1",
        "modified": False, "releases": config["historical_releases"],
    })
    write_json(release / "uncertainty" / "uncertainty_scope.json", {
        "schema": "three-stage-coupled-uncertainty-scope-v1",
        "source_iteration": "iter015", "validation_partition": "development held-out folds",
        "fixed_test_used_for_uncertainty": False, "refitted": False,
        "limitations": [
            "empirical uncertainty is development-only and is not recalibrated on fixed-test results",
            "fold-specific estimates do not constitute full Bayesian posterior uncertainty",
            "hourly errors are serially correlated",
        ],
        "source_files": config["uncertainty_files"],
    })
    write_json(release / "LIMITATIONS.json", {
        "schema": "three-stage-coupled-release-limitations-v1",
        "sites": list(SITES), "configuration_frozen_before_fixed_test": True,
        "performance_threshold_applied": False,
        "negative_sr_fixed_test": {"count": negative_sr_count, "total": 25141200, "fraction": negative_sr_count / 25141200, "minimum_gC_m2_day": negative_sr_minimum, "policy": "disclose_without_post_hoc_gate"},
        "uncertainty": "Iter015 development-only empirical handoff; not refit from fixed test",
        "storage": "temporary unbacked /xdisk operational publication",
    })

    engine = CoupledThreeStageInference(snapshot, spinup, gpp, sr, artifact_manifest)
    parameters = snapshot._parameter_values(snapshot.fixed_test_ranked[:2])
    for site in SITES:
        with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as source:
            forcing = {name: np.asarray(source.variables[name][:768], dtype=np.float64) for name in FORCING_NAMES}
            time = np.asarray(source.variables["time"][:768], dtype=np.int64)
        first = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=1)
        second = engine.predict(parameters, site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=2)
        for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
            require(np.allclose(getattr(first, name), getattr(second, name), rtol=1e-6, atol=1e-6), f"release replay mismatch: {site}/{name}")
        require(np.array_equal(first.gpp, np.maximum(first.gpp_raw, 0.0)), f"release gate mismatch: {site}")

    release_manifest = {
        "schema": "three-stage-coupled-release-manifest-v1", "result": "assembled",
        "release": config["release_name"], "sites": list(SITES),
        "snapshot_sha256": snapshot.snapshot_sha256, "global_split_sha256": sha256_file(snapshot.split_path),
        "artifact_manifest_sha256": config["artifact_manifest_sha256"],
        "training_partition": "development", "training_member_count": 819,
        "fixed_test_partition": "fixed_test", "fixed_test_member_count": 205,
        "fixed_test_report_sha256": config["fixed_test_report_sha256"],
        "fixed_test_predictions_sha256": config["fixed_test_predictions_sha256"],
        "feature_counts": {"spinup": 25, "gpp": 43, "sr": 44},
        "gpp_output_policy": "hard_zero_v1", "upstream_prediction_mode": "direct_in_sample",
        "inference_entry_point": interface["entry_point"], "performance_threshold_applied": False,
        "uncertainty_refit": False, "historical_releases_modified": False,
        "scientific_limitations": [f"{negative_sr_count} of 25141200 fixed-test SR values are negative; minimum {negative_sr_minimum:.8g} gC/m^2/day"],
        "files": inventory(release),
    }
    write_json(release / "release_manifest.json", release_manifest)
    report = {
        "schema": "three-stage-iter016-release-assembly-report-v1", "result": "pass",
        "release_manifest_sha256": sha256_file(release / "release_manifest.json"),
        "file_count": len(release_manifest["files"]), "artifact_reload": True,
        "target_free_direct_chunk_replay": True, "gpp_gate_equal_binary": True,
        "fixed_test_evidence_copied": True, "uncertainty_refit": False,
        "historical_releases_modified": False, "stable_publication_performed": False,
    }
    write_json(output / "release_assembly_report.json", report)
    print(f"ITER016_RELEASE_ASSEMBLED files={report['file_count']} published=false", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return 0 if assemble(args.config, args.output)["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
