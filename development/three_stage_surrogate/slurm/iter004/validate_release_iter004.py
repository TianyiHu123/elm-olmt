#!/usr/bin/env python
"""Independent gate validation for the complete staged Iter004 release."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import SITES, TARGETS, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_release import MODEL_CONFIG, load_release_artifact, package_files, predict_release, split_design_sha256, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--fit-package", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=False)
    staging = output / "release_0001"
    shutil.copytree(args.fit_package.resolve(), staging)
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot hash mismatch")
    artifact, artifact_manifest = load_release_artifact(staging / "artifact")
    require(artifact["model_config"] == MODEL_CONFIG == config["model_config"], "model configuration drift")
    fit_members = artifact["fit_scope"]["development_member_ids"]
    require(fit_members == list(snapshot.development_ranked), "all-development fit identity/order mismatch")
    require(not set(fit_members).intersection(snapshot.fixed_test_set), "fixed-test identity in release fit")
    split_path = staging / "uncertainty" / "repeated_split_manifest.json"
    split_manifest = json.loads(split_path.read_text(encoding="utf-8"))
    require(split_manifest["seed"] == 20261031 and split_manifest["seed"] != 20261030, "fresh split seed mismatch")
    require(len(split_manifest["splits"]) == 20, "split count mismatch")
    require(split_manifest["split_design_sha256"] == split_design_sha256(split_manifest), "split design hash mismatch")
    recorded_counts = {str(key): int(value) for key, value in split_manifest["validation_appearance_counts"].items()}
    counts = {member: 0 for member in snapshot.development_ranked}
    for split in split_manifest["splits"]:
        train = list(split["train_member_ids"])
        validation = list(split["validation_member_ids"])
        require(len(train) == len(set(train)) == 655, "training split mismatch")
        require(len(validation) == len(set(validation)) == 164, "validation split mismatch")
        require(not set(train).intersection(validation), "split overlap")
        require(set(train).union(validation) == snapshot.development_set, "split membership mismatch")
        require(not set(validation).intersection(snapshot.fixed_test_set), "fixed-test split access")
        for member in validation:
            counts[member] += 1
    require(counts == recorded_counts, "recorded appearance counts differ from split rows")
    require(sum(value == 4 for value in counts.values()) == 815 and sum(value == 5 for value in counts.values()) == 4, "appearance balance mismatch")
    evidence_path = staging / "uncertainty" / "paired_robustness_evidence.nc"
    with Dataset(str(evidence_path), "r") as evidence:
        require(evidence.getncattr("schema") == "three-stage-spinup-iter004-robustness-v1", "robustness schema mismatch")
        require(evidence.getncattr("residual_convention") == "prediction minus ELM", "residual convention mismatch")
        required = {"split_id", "site", "member_id"}
        for target in TARGETS:
            required.update({f"{target}_{suffix}" for suffix in ("elm", "predicted", "residual", "log_elm", "log_predicted", "log_residual")})
        require(required.issubset(evidence.variables), "robustness variables missing")
        sites = np.asarray(evidence.variables["site"][:], dtype=str)
        members = np.asarray(evidence.variables["member_id"][:], dtype=str)
        split_ids = np.asarray(evidence.variables["split_id"][:], dtype=np.int16)
        require(sites.size == 20 * 2 * 164, "robustness observation count mismatch")
        errors = np.column_stack([np.asarray(evidence.variables[f"{target}_log_residual"][:], dtype=np.float64) for target in TARGETS])
        for target in TARGETS:
            truth = np.asarray(evidence.variables[f"{target}_elm"][:], dtype=np.float64)
            prediction = np.asarray(evidence.variables[f"{target}_predicted"][:], dtype=np.float64)
            residual = np.asarray(evidence.variables[f"{target}_residual"][:], dtype=np.float64)
            log_residual = np.asarray(evidence.variables[f"{target}_log_residual"][:], dtype=np.float64)
            require(np.all(np.isfinite(truth)) and np.all(truth > 0.0), f"{target} truth invalid")
            require(np.all(np.isfinite(prediction)) and np.all(prediction > 0.0), f"{target} prediction invalid")
            require(np.allclose(residual, prediction - truth, rtol=0.0, atol=1e-10), f"{target} residual mismatch")
            require(np.allclose(log_residual, np.log(prediction) - np.log(truth), rtol=0.0, atol=1e-12), f"{target} log residual mismatch")
    with (staging / "uncertainty" / "metric_distribution.csv").open(encoding="utf-8", newline="") as handle:
        metrics = list(csv.DictReader(handle))
    require(len(metrics) == 20 * 2 * 2 * 2 + 2 * 2 * 2, "metric distribution row count mismatch")
    require({row["record_type"] for row in metrics} == {"repetition", "cross_repetition"}, "metric record types mismatch")
    for row in metrics:
        for field in ("r2", "rmse", "mae", "bias", "residual_std", "q0_01", "q0_025", "q0_05", "q0_25", "q0_5", "q0_75", "q0_95", "q0_975", "q0_99"):
            require(np.isfinite(float(row[field])), f"nonfinite metric {field}")
    with (staging / "uncertainty" / "depth_error_dependence.csv").open(encoding="utf-8", newline="") as handle:
        depth = list(csv.DictReader(handle))
    require(len(depth) == 20 * 2 * 2, "depth diagnostic row count mismatch")
    require(all(np.isfinite(float(row["pearson_correlation"])) for row in depth), "nonfinite depth diagnostic")
    uncertainty_path = staging / "uncertainty" / "surrogate_uncertainty.nc"
    with Dataset(str(uncertainty_path), "r") as uncertainty:
        require(uncertainty.getncattr("schema") == "three-stage-spinup-surrogate-uncertainty-v1", "uncertainty schema mismatch")
        generic_forbidden = {"target", "target_name", "totsomc", "totsomn"}
        require(not generic_forbidden.intersection(uncertainty.variables), "generic target coordinate present")
        required = {
            "TOTSOMC_log_error_bias", "TOTSOMN_log_error_bias",
            "TOTSOMC_log_error_variance", "TOTSOMN_log_error_variance",
            "TOTSOMC_TOTSOMN_log_error_covariance", "TOTSOMC_TOTSOMN_log_error_correlation",
        }
        require(required.issubset(uncertainty.variables), "uncertainty variables missing")
        for site_index, site in enumerate(SITES):
            mask = sites == site
            values = errors[mask]
            weights = np.asarray([1.0 / counts[member] for member in members[mask]], dtype=np.float64)
            weights /= np.sum(weights)
            bias = np.sum(values * weights[:, None], axis=0)
            centered = values - bias
            covariance = (centered * weights[:, None]).T @ centered
            require(np.allclose(covariance, covariance.T, rtol=0.0, atol=config["covariance_symmetry_atol"]), "covariance asymmetric")
            require(float(np.min(np.linalg.eigvalsh(covariance))) >= config["covariance_minimum_eigenvalue"], "covariance not PSD")
            observed_bias = np.asarray([uncertainty.variables[f"{target}_log_error_bias"][site_index] for target in TARGETS])
            observed_covariance = np.asarray([
                [uncertainty.variables["TOTSOMC_log_error_variance"][site_index], uncertainty.variables["TOTSOMC_TOTSOMN_log_error_covariance"][site_index]],
                [uncertainty.variables["TOTSOMC_TOTSOMN_log_error_covariance"][site_index], uncertainty.variables["TOTSOMN_log_error_variance"][site_index]],
            ], dtype=np.float64)
            require(np.allclose(observed_bias, bias, rtol=1e-12, atol=1e-12), "uncertainty bias mismatch")
            require(np.allclose(observed_covariance, covariance, rtol=1e-12, atol=1e-12), "uncertainty covariance mismatch")
    loaded = snapshot.load_rows(snapshot.development_ranked, include_targets=False)
    full_prediction = predict_release(artifact, loaded.X).reshape(2, 819, 2)
    for count in (1, 17, 1638):
        repeat = predict_release(artifact, loaded.X[:count])
        require(repeat.shape == (count, 2), "flexible prediction shape mismatch")
        require(np.allclose(repeat, predict_release(artifact, loaded.X[:count]), rtol=config["reload_rtol"], atol=config["reload_atol"]), "reload prediction mismatch")
    handoff_path = staging / "handoff" / "spinup_predicted_cn.nc"
    with Dataset(str(handoff_path), "r") as handoff:
        require(handoff.getncattr("schema") == "three-stage-spinup-predicted-cn-handoff-v1", "handoff schema mismatch")
        require(set(handoff.variables) == {"site", "member_id", "TOTSOMC_predicted", "TOTSOMN_predicted"}, "handoff variable scope mismatch")
        require(np.asarray(handoff.variables["site"][:], dtype=str).tolist() == list(SITES), "handoff site order mismatch")
        require(np.asarray(handoff.variables["member_id"][:], dtype=str).tolist() == list(snapshot.development_ranked), "handoff member order mismatch")
        for target_index, target in enumerate(TARGETS):
            observed = np.asarray(handoff.variables[f"{target}_predicted"][:], dtype=np.float64)
            require(np.all(np.isfinite(observed)) and np.all(observed > 0.0), "handoff prediction invalid")
            require(np.allclose(observed, full_prediction[:, :, target_index], rtol=config["reload_rtol"], atol=config["reload_atol"]), "handoff prediction mismatch")
    handoff_manifest = json.loads((staging / "handoff" / "handoff_manifest.json").read_text(encoding="utf-8"))
    require(handoff_manifest["contains_elm_truth"] is False and handoff_manifest["contains_features_or_parameters"] is False, "handoff contents mismatch")
    require(handoff_manifest["sha256"] == sha256_file(handoff_path), "handoff hash mismatch")
    validation_report = {
        "schema": "three-stage-spinup-iter004-validation-v1", "result": "pass",
        "snapshot_sha256": snapshot.snapshot_sha256, "split_manifest_sha256": sha256_file(split_path),
        "split_design_sha256": split_design_sha256(split_manifest), "artifact_sha256": artifact_manifest["artifact_sha256"],
        "handoff_sha256": handoff_manifest["sha256"], "fixed_test_access": False,
        "fit_member_count": 819, "robustness_observation_count": int(sites.size),
        "reload_rtol": config["reload_rtol"], "reload_atol": config["reload_atol"],
        "covariance_symmetry_atol": config["covariance_symmetry_atol"],
        "covariance_minimum_eigenvalue": config["covariance_minimum_eigenvalue"],
    }
    write_json(output / "validation_report.json", validation_report)
    write_json(staging / "validation" / "validation_report.json", validation_report)
    release_manifest = {
        "schema": "three-stage-spinup-release-package-manifest-v1", "release": "release_0001",
        "created_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "result": "validated", "snapshot_sha256": snapshot.snapshot_sha256,
        "artifact_sha256": artifact_manifest["artifact_sha256"], "handoff_sha256": handoff_manifest["sha256"],
        "split_manifest_sha256": sha256_file(split_path), "fixed_test_access": False,
        "files": package_files(staging, exclude={"release_manifest.json"}),
    }
    write_json(staging / "release_manifest.json", release_manifest)
    print(f"ITER004_VALIDATE_OK artifact={artifact_manifest['artifact_sha256']} files={len(release_manifest['files'])}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
