from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import TARGETS, ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_spinup_artifact import load_artifact


def validate_package(package: Path, expected_kind: str, expected_train: int, expected_validation: int) -> Dict[str, Any]:
    manifest_path = package / "package_manifest.json"
    require(manifest_path.is_file(), f"package manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["schema"] == "three-stage-spinup-development-package-v1", "package schema mismatch")
    require(manifest["run_kind"] == expected_kind, "package run kind mismatch")
    for relative, identity in manifest["files"].items():
        path = package / relative
        require(path.is_file(), f"package file missing: {relative}")
        require(path.stat().st_size == int(identity["size_bytes"]), f"package size mismatch: {relative}")
        require(sha256_file(path) == identity["sha256"], f"package hash mismatch: {relative}")
    artifact, artifact_path, artifact_manifest = load_artifact(package / "artifact")
    scope = artifact["fit_scope"]
    require(len(scope["train_member_ids"]) == expected_train, "artifact train count mismatch")
    require(len(scope["validation_member_ids"]) == expected_validation, "artifact validation count mismatch")
    metrics = json.loads((package / "metrics.json").read_text(encoding="utf-8"))
    require(metrics["schema"] == "three-stage-spinup-metrics-v1", "metrics schema mismatch")
    require(metrics["target_transform"] == "natural_log", "metrics target transform mismatch")
    require(artifact["target_transform"] == "natural_log", "artifact target transform mismatch")
    require(len(metrics["rows"]) == 24, "metrics row count mismatch")
    gaps = metrics.get("validation_minus_training_gaps", [])
    require(len(gaps) == 12, "metric gap row count mismatch")
    combinations = {
        (row["partition"], row["site"], row["target"], row["scale"])
        for row in metrics["rows"]
    }
    expected = {
        (partition, site, target, scale)
        for partition in ("training", "validation")
        for site in ("pooled", "ABBY", "JERC")
        for target in TARGETS
        for scale in ("physical", "log")
    }
    require(combinations == expected, "metrics combinations mismatch")
    gap_combinations = {(row["site"], row["target"], row["scale"]) for row in gaps}
    expected_gaps = {
        (site, target, scale)
        for site in ("pooled", "ABBY", "JERC")
        for target in TARGETS
        for scale in ("physical", "log")
    }
    require(gap_combinations == expected_gaps, "metric gap combinations mismatch")
    for row in gaps:
        require(row["definition"] == "validation minus training", "metric gap definition mismatch")
        require(int(row["training_n"]) > 0 and int(row["validation_n"]) > 0, "metric gap counts invalid")
        for key in ("r2_gap", "rmse_gap", "mae_gap", "bias_gap", "residual_std_gap"):
            require(np.isfinite(float(row[key])), f"nonfinite metric gap {key}")
    require((package / "metric_gaps.csv").is_file(), "metric gaps CSV missing")
    for row in metrics["rows"]:
        for key in ("r2", "rmse", "mae", "bias", "residual_std"):
            require(np.isfinite(float(row[key])), f"nonfinite metric {key}")
    require(metrics["permutation_importance"]["repeats"] == 8, "permutation repeat mismatch")
    plots = sorted((package / "plots").glob("*.png"))
    require(len(plots) == 4 and all(path.stat().st_size > 0 for path in plots), "plot package mismatch")
    return {
        "artifact": artifact,
        "artifact_path": artifact_path,
        "artifact_manifest": artifact_manifest,
        "metrics": metrics,
    }


def read_cli_prediction(path: Path) -> Dict[str, Any]:
    with Dataset(str(path), "r") as dataset:
        require(dataset.getncattr("schema") == "three-stage-spinup-predictions-v1", "CLI prediction schema mismatch")
        members = [str(v) for v in dataset.variables["member_id"][:]]
        sites = [str(v) for v in dataset.variables["site"][:]]
        values = np.stack([np.asarray(dataset.variables[target][:], dtype=np.float64) for target in TARGETS], axis=-1)
        require(np.all(np.isfinite(values)) and np.all(values > 0.0), "CLI predictions must be positive finite")
        require(not any(name.endswith("_elm") for name in dataset.variables), "CLI output contains ELM truth")
        return {"members": members, "sites": sites, "values": values}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--smoke-attempt", required=True, type=int)
    parser.add_argument("--operational-attempt", required=True, type=int)
    parser.add_argument("--validation-attempt", required=True, type=int)
    parser.add_argument("--validation-dir", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    smoke_package = Path(config["run_directories"]["smoke"]) / f"attempt_{args.smoke_attempt}" / "package"
    operational_package = Path(config["run_directories"]["operational"]) / f"attempt_{args.operational_attempt}" / "package"
    smoke = validate_package(smoke_package, "smoke", 80, 20)
    operational = validate_package(operational_package, "operational", 655, 164)
    require(smoke["artifact"]["artifact_role"] == "non_release_smoke", "smoke artifact role mismatch")
    require(operational["artifact"]["artifact_role"] == "non_release_validation", "operational artifact role mismatch")
    require(
        operational["artifact"]["fit_scope"]["train_member_ids"] == list(snapshot.operational_split()[0]),
        "operational train identities mismatch",
    )
    require(
        operational["artifact"]["fit_scope"]["validation_member_ids"] == list(snapshot.operational_split()[1]),
        "operational validation identities mismatch",
    )
    validation_root = args.validation_dir.resolve() / f"attempt_{args.validation_attempt}"
    cli_outputs = {
        name: read_cli_prediction(validation_root / f"predict_{name}.nc")
        for name in ("single", "subset", "smoke20", "operational164")
    }
    require(len(cli_outputs["single"]["members"]) == 1, "single-member prediction count mismatch")
    require(len(cli_outputs["subset"]["members"]) == 7, "subset prediction count mismatch")
    require(len(cli_outputs["smoke20"]["members"]) == 20, "smoke prediction count mismatch")
    require(len(cli_outputs["operational164"]["members"]) == 164, "operational prediction count mismatch")
    _, operational_validation = snapshot.operational_split()
    require(cli_outputs["operational164"]["members"] == list(operational_validation), "CLI validation identity mismatch")
    with Dataset(str(operational_package / "validation_predictions.nc"), "r") as dataset:
        recorded_members = [str(v) for v in dataset.variables["member_id"][:]]
        require(recorded_members == list(operational_validation), "recorded validation member mismatch")
        recorded = np.stack(
            [np.asarray(dataset.variables[f"{target}_pred"][:], dtype=np.float64) for target in TARGETS],
            axis=-1,
        )
    observed = cli_outputs["operational164"]["values"]
    tolerance = config["reload_tolerance"]
    require(
        np.allclose(recorded, observed, rtol=float(tolerance["rtol"]), atol=float(tolerance["atol"])),
        "fresh-process reload predictions differ",
    )
    fixed = set(snapshot.fixed_test_ranked)
    for package in (smoke, operational):
        scope = package["artifact"]["fit_scope"]
        require(not fixed.intersection(scope["train_member_ids"]), "fixed-test member in train scope")
        require(not fixed.intersection(scope["validation_member_ids"]), "fixed-test member in validation scope")
    report = {
        "schema": "three-stage-spinup-iter002-validation-v1",
        "result": "pass",
        "snapshot_revision": "r0001",
        "snapshot_sha256": snapshot.snapshot_sha256,
        "smoke_attempt": args.smoke_attempt,
        "operational_attempt": args.operational_attempt,
        "validation_attempt": args.validation_attempt,
        "smoke_artifact_sha256": smoke["artifact_manifest"]["artifact_sha256"],
        "operational_artifact_sha256": operational["artifact_manifest"]["artifact_sha256"],
        "flexible_prediction_counts": {name: len(value["members"]) for name, value in cli_outputs.items()},
        "fresh_process_reload_match": True,
        "fixed_test_access": False,
        "all_819_prediction_created": False,
    }
    report_path = validation_root / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ITER002_VALIDATE_OK smoke=80/20 operational=655/164 "
        "predict=1,7,20,164 fixed_test=false all819=false",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
