#!/usr/bin/env python
"""Independent final validation and product staging for Iter015."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter015.full_chain_iter015 import (
    GPP_POLICY,
    SITES,
    TARGETS,
    _target,
    load_config,
    validate_config,
)
from model_ELM.three_stage_data import require, sha256_file


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return bool(np.isclose(left, right, rtol=tolerance, atol=tolerance))


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    left = np.asarray(x, dtype=np.float64).reshape(-1)
    right = np.asarray(y, dtype=np.float64).reshape(-1)
    require(left.size == right.size and left.size > 1, "final correlation size mismatch")
    require(np.all(np.isfinite(left)) and np.all(np.isfinite(right)), "final correlation nonfinite")
    return float(np.corrcoef(left, right)[0, 1])


def basic_metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    observed = np.asarray(truth, dtype=np.float64).reshape(-1)
    modeled = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(observed.size == modeled.size and observed.size > 1, "final metric size mismatch")
    residual = modeled - observed
    denominator = float(np.sum((observed - float(np.mean(observed))) ** 2))
    require(denominator > 0.0, "final metric denominator invalid")
    return {
        "r2": float(1.0 - np.sum(residual * residual) / denominator),
        "rmse": float(np.sqrt(np.mean(residual * residual))),
        "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)),
        "residual_std": float(np.std(residual, ddof=0)),
    }


def split_paths(config: Mapping[str, Any]) -> list[Path]:
    pilot = Path(config["run_directories"]["pilot"]) / "attempt_1" / "split_00"
    production = Path(config["run_directories"]["production"]) / "attempt_1"
    return [pilot] + [production / f"split_{split_id:02d}" for split_id in range(1, 20)]


def validate_identities(snapshot: Any, splits: Mapping[str, Any], paths: Sequence[Path]) -> None:
    require(len(paths) == 20 and all(path.is_dir() for path in paths), "final split path mismatch")
    development = set(snapshot.development_set)
    fixed = set(snapshot.fixed_test_set)
    for split_id, path in enumerate(paths):
        report = json.loads((path / "split_report.json").read_text(encoding="utf-8"))
        layout = json.loads((path / "layout.json").read_text(encoding="utf-8"))
        training = list(layout["train_member_ids"])
        validation = list(layout["validation_member_ids"])
        expected = splits["splits"][split_id]
        require(training == list(expected["train_member_ids"]), "final training order mismatch")
        require(validation == list(expected["validation_member_ids"]), "final validation order mismatch")
        require(len(training) == 655 and len(validation) == 164, "final split size mismatch")
        require(not set(training).intersection(validation), "final train-validation overlap")
        require(set(training).union(validation) == development, "final development coverage mismatch")
        require(not set(training).intersection(fixed) and not set(validation).intersection(fixed), "fixed-test leakage")
        require(report.get("fixed_test_access") is False, "final fixed-test flag mismatch")
        require(report.get("all_development_fit") is False and report.get("release_modified") is False, "final prohibited scope mismatch")


def validate_aggregate_hashes(aggregate: Path) -> dict[str, Any]:
    report = json.loads((aggregate / "aggregate_report.json").read_text(encoding="utf-8"))
    require(report.get("result") == "pass" and report.get("split_count") == 20, "aggregate report mismatch")
    for name, expected in report["output_sha256"].items():
        require(sha256_file(aggregate / name) == expected, f"aggregate output hash mismatch: {name}")
    require(report.get("diagnostic_figures") == ["error_propagation.png", "gpp_gate_comparison.png", "gpp_sr_joint.png"], "figure inventory mismatch")
    require(len(list(aggregate.glob("*.png"))) == 3, "unexpected aggregate figure")
    return report


def validate_concatenation(paths: Sequence[Path], aggregate: Path) -> None:
    mapping = {
        "metric_distribution.csv": "metrics.csv",
        "gpp_gate_distribution.csv": "gpp_gate_comparison.csv",
        "error_propagation_members.csv": "error_propagation.csv",
        "depth_error_distribution.csv": "depth_error_dependence.csv",
    }
    for aggregate_name, source_name in mapping.items():
        expected: list[dict[str, str]] = []
        for path in paths:
            expected.extend(read_csv(path / source_name))
        require(read_csv(aggregate / aggregate_name) == expected, f"aggregate concatenation mismatch: {aggregate_name}")


def validate_gate(snapshot: Any, splits: Mapping[str, Any], paths: Sequence[Path], aggregate: Path) -> int:
    for path in paths:
        raw_path = path / "gpp_predictions_physical_float32.dat"
        gated_path = path / "gpp_gated_physical_float32.dat"
        require(raw_path.stat().st_size == gated_path.stat().st_size, "gate binary size mismatch")
        count = raw_path.stat().st_size // np.dtype(np.float32).itemsize
        raw = np.memmap(raw_path, mode="r", dtype=np.float32, shape=(count,))
        gated = np.memmap(gated_path, mode="r", dtype=np.float32, shape=(count,))
        for start in range(0, count, 2_000_000):
            end = min(start + 2_000_000, count)
            require(np.array_equal(gated[start:end], np.maximum(raw[start:end], np.float32(0.0))), "final hard-zero gate mismatch")

    split_id = 0
    members = list(splits["splits"][split_id]["validation_member_ids"])
    reference = {(row["site"], row["resolution"]): row for row in read_csv(aggregate / "gpp_gate_distribution.csv") if int(row["split_id"]) == split_id}
    by_site: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    with Dataset(str(paths[0] / "heldout_predictions.nc"), "r") as dataset:
        for site_index, site in enumerate(SITES):
            truth = _target(snapshot, site, "GPP", members, 61320).reshape(-1)
            raw = np.asarray(dataset.variables["GPP_raw"][site_index], dtype=np.float32).reshape(-1)
            gated = np.asarray(dataset.variables["GPP_gated"][site_index], dtype=np.float32).reshape(-1)
            require(np.array_equal(gated, np.maximum(raw, np.float32(0.0))), "held-out hard-zero gate mismatch")
            by_site[site] = truth, raw, gated
    for site in (*SITES, "pooled"):
        if site == "pooled":
            truth = np.concatenate([by_site[value][0] for value in SITES])
            raw = np.concatenate([by_site[value][1] for value in SITES])
            gated = np.concatenate([by_site[value][2] for value in SITES])
        else:
            truth, raw, gated = by_site[site]
        for resolution in ("hourly", "daily"):
            if resolution == "daily":
                observed = truth.reshape(-1, 24).mean(axis=1)
                raw_use = raw.reshape(-1, 24).mean(axis=1)
                gated_use = gated.reshape(-1, 24).mean(axis=1)
            else:
                observed, raw_use, gated_use = truth, raw, gated
            raw_metrics = basic_metrics(observed, raw_use)
            gated_metrics = basic_metrics(observed, gated_use)
            row = reference[(site, resolution)]
            for name, value in (("raw_r2", raw_metrics["r2"]), ("gated_r2", gated_metrics["r2"]), ("raw_rmse", raw_metrics["rmse"]), ("gated_rmse", gated_metrics["rmse"])):
                require(close(float(row[name]), value), f"representative gate metric mismatch: {site} {resolution} {name}")
            require(int(row["same_target_count"]) == observed.size, "gate target count mismatch")
    return 6


def validate_representative_metrics(snapshot: Any, splits: Mapping[str, Any], paths: Sequence[Path], aggregate: Path) -> int:
    split_id = 0
    members = list(splits["splits"][split_id]["validation_member_ids"])
    rows = [row for row in read_csv(aggregate / "metric_distribution.csv") if int(row["split_id"]) == 0 and row["partition"] == "validation"]
    lookup = {(row["stage"], row["site"], row["target"], row["scale"], row["resolution"]): row for row in rows}
    with Dataset(str(paths[0] / "heldout_predictions.nc"), "r") as dataset:
        truth_cn = np.asarray(dataset.variables["CN_elm"][:], dtype=np.float64)
        predicted_cn = np.asarray(dataset.variables["CN_predicted"][:], dtype=np.float64)
        for site_index, site in enumerate((*SITES, "pooled")):
            for target_index, target in enumerate(TARGETS):
                for scale in ("physical", "log"):
                    if site == "pooled":
                        truth = truth_cn[:, :, target_index].reshape(-1)
                        predicted = predicted_cn[:, :, target_index].reshape(-1)
                    else:
                        truth = truth_cn[site_index, :, target_index]
                        predicted = predicted_cn[site_index, :, target_index]
                    if scale == "log":
                        truth = np.log(truth)
                        predicted = np.log(predicted)
                    computed = basic_metrics(truth, predicted)
                    row = lookup[("spinup", site, target, scale, "member")]
                    for metric, value in computed.items():
                        require(close(float(row[metric]), value), f"representative C/N metric mismatch: {site} {target} {scale} {metric}")
        for stage, variable, target in (("gpp", "GPP_gated", "GPP"), ("sr", "SR_predicted", "SR")):
            site_data: dict[str, tuple[np.ndarray, np.ndarray]] = {}
            for site_index, site in enumerate(SITES):
                truth = _target(snapshot, site, target, members, 61320).reshape(-1)
                predicted = np.asarray(dataset.variables[variable][site_index], dtype=np.float32).reshape(-1)
                site_data[site] = truth, predicted
            for site in (*SITES, "pooled"):
                if site == "pooled":
                    truth = np.concatenate([site_data[value][0] for value in SITES])
                    predicted = np.concatenate([site_data[value][1] for value in SITES])
                else:
                    truth, predicted = site_data[site]
                for resolution in ("hourly", "daily"):
                    if resolution == "daily":
                        truth_use = truth.reshape(-1, 24).mean(axis=1)
                        predicted_use = predicted.reshape(-1, 24).mean(axis=1)
                    else:
                        truth_use, predicted_use = truth, predicted
                    computed = basic_metrics(truth_use, predicted_use)
                    row = lookup[(stage, site, target, "physical", resolution)]
                    for metric, value in computed.items():
                        require(close(float(row[metric]), value), f"representative flux metric mismatch: {stage} {site} {resolution} {metric}")
    return len(rows)


def validate_covariance(aggregate: Path) -> tuple[int, int]:
    member_rows = read_csv(aggregate / "cn_member_errors.csv")
    covariance_rows = read_csv(aggregate / "cn_log_covariance.csv")
    covariance_lookup = {(int(row["split_id"]), row["site"], row["row_target"], row["column_target"]): row for row in covariance_rows}
    for split_id in range(20):
        for site in SITES:
            active = [row for row in member_rows if int(row["split_id"]) == split_id and row["site"] == site]
            values = np.column_stack(tuple([float(row[f"{target}_log_error"]) for row in active] for target in TARGETS))
            covariance = np.cov(values, rowvar=False, ddof=0)
            correlation = np.corrcoef(values, rowvar=False)
            for row_index, row_target in enumerate(TARGETS):
                for column_index, column_target in enumerate(TARGETS):
                    row = covariance_lookup[(split_id, site, row_target, column_target)]
                    require(close(float(row["log_error_covariance"]), float(covariance[row_index, column_index])), "C/N covariance mismatch")
                    require(close(float(row["log_error_correlation"]), float(correlation[row_index, column_index])), "C/N correlation mismatch")
    balanced = read_csv(aggregate / "cn_member_balanced.csv")
    balanced_covariance = read_csv(aggregate / "cn_member_balanced_covariance.csv")
    for site in SITES:
        active = [row for row in balanced if row["site"] == site]
        appearances = [int(row["validation_appearances"]) for row in active]
        require(len(active) == 819 and appearances.count(4) == 815 and appearances.count(5) == 4, "balanced C/N membership mismatch")
        values = np.column_stack(tuple([float(row[f"{target}_mean_log_error"]) for row in active] for target in TARGETS))
        covariance = np.cov(values, rowvar=False, ddof=0)
        for row_index, row_target in enumerate(TARGETS):
            for column_index, column_target in enumerate(TARGETS):
                row = next(item for item in balanced_covariance if item["site"] == site and item["row_target"] == row_target and item["column_target"] == column_target)
                require(close(float(row["member_balanced_log_error_covariance"]), float(covariance[row_index, column_index])), "balanced covariance mismatch")
    return len(covariance_rows), len(balanced_covariance)


def validate_propagation_correlations(aggregate: Path) -> tuple[int, int]:
    rows = read_csv(aggregate / "error_propagation_members.csv")
    correlations = read_csv(aggregate / "error_propagation_correlations.csv")
    relationships = (
        ("cn_vs_gpp", "cn_rms_log_error", "gpp_hourly_rmse"),
        ("cn_vs_sr", "cn_rms_log_error", "sr_hourly_rmse"),
        ("gpp_vs_sr", "gpp_hourly_rmse", "sr_hourly_rmse"),
    )
    for split_id in range(20):
        split_rows = [row for row in rows if int(row["split_id"]) == split_id]
        for site in (*SITES, "pooled"):
            active = split_rows if site == "pooled" else [row for row in split_rows if row["site"] == site]
            for relationship, x_name, y_name in relationships:
                expected = pearson(np.asarray([float(row[x_name]) for row in active]), np.asarray([float(row[y_name]) for row in active]))
                row = next(item for item in correlations if int(item["split_id"]) == split_id and item["site"] == site and item["relationship"] == relationship)
                require(close(float(row["pearson_correlation"]), expected), "propagation correlation mismatch")
    balanced = read_csv(aggregate / "error_propagation_member_balanced.csv")
    balanced_correlations = read_csv(aggregate / "error_propagation_member_balanced_correlations.csv")
    balanced_relationships = (
        ("cn_vs_gpp", "mean_cn_rms_log_error", "mean_gpp_hourly_rmse"),
        ("cn_vs_sr", "mean_cn_rms_log_error", "mean_sr_hourly_rmse"),
        ("gpp_vs_sr", "mean_gpp_hourly_rmse", "mean_sr_hourly_rmse"),
    )
    for site in (*SITES, "pooled"):
        active = balanced if site == "pooled" else [row for row in balanced if row["site"] == site]
        for relationship, x_name, y_name in balanced_relationships:
            expected = pearson(np.asarray([float(row[x_name]) for row in active]), np.asarray([float(row[y_name]) for row in active]))
            row = next(item for item in balanced_correlations if item["site"] == site and item["relationship"] == relationship)
            require(close(float(row["pearson_correlation"]), expected), "balanced propagation correlation mismatch")
    return len(correlations), len(balanced_correlations)


def validate_gpp_sr_correlations(snapshot: Any, splits: Mapping[str, Any], paths: Sequence[Path], aggregate: Path) -> int:
    reference = {(int(row["split_id"]), row["site"], row["source"]): row for row in read_csv(aggregate / "gpp_sr_correlations.csv")}
    for split_id, path in enumerate(paths):
        members = list(splits["splits"][split_id]["validation_member_ids"])
        pooled: dict[str, list[np.ndarray]] = defaultdict(list)
        with Dataset(str(path / "heldout_predictions.nc"), "r") as dataset:
            for site_index, site in enumerate(SITES):
                elm_gpp = _target(snapshot, site, "GPP", members, 61320)
                elm_sr = _target(snapshot, site, "SR", members, 61320)
                surrogate_gpp = np.asarray(dataset.variables["GPP_gated"][site_index], dtype=np.float32)
                surrogate_sr = np.asarray(dataset.variables["SR_predicted"][site_index], dtype=np.float32)
                for source, x, y in (("ELM", elm_gpp, elm_sr), ("full_chain_surrogate", surrogate_gpp, surrogate_sr)):
                    require(close(float(reference[(split_id, site, source)]["pearson_gpp_sr"]), pearson(x, y)), "GPP-SR correlation mismatch")
                for name, array in (("elm_gpp", elm_gpp), ("elm_sr", elm_sr), ("surrogate_gpp", surrogate_gpp), ("surrogate_sr", surrogate_sr)):
                    pooled[name].append(array.reshape(-1))
        for source, x_name, y_name in (("ELM", "elm_gpp", "elm_sr"), ("full_chain_surrogate", "surrogate_gpp", "surrogate_sr")):
            expected = pearson(np.concatenate(pooled[x_name]), np.concatenate(pooled[y_name]))
            require(close(float(reference[(split_id, "pooled", source)]["pearson_gpp_sr"]), expected), "pooled GPP-SR correlation mismatch")
    return len(reference)


def validate_density(snapshot: Any, splits: Mapping[str, Any], path: Path, aggregate: Path) -> int:
    validation = json.loads((aggregate / "gpp_sr_joint_grid_validation.json").read_text(encoding="utf-8"))
    require(validation.get("grid_shape") == [200, 200] and len(validation.get("panels", [])) == 6, "density validation schema mismatch")
    members = list(splits["splits"][0]["validation_member_ids"])
    joint: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    pooled: dict[str, list[np.ndarray]] = defaultdict(list)
    with Dataset(str(path / "heldout_predictions.nc"), "r") as dataset:
        for site_index, site in enumerate(SITES):
            arrays = (
                _target(snapshot, site, "GPP", members, 61320).reshape(-1),
                _target(snapshot, site, "SR", members, 61320).reshape(-1),
                np.asarray(dataset.variables["GPP_gated"][site_index], dtype=np.float32).reshape(-1),
                np.asarray(dataset.variables["SR_predicted"][site_index], dtype=np.float32).reshape(-1),
            )
            joint[site] = arrays
            for name, array in zip(("elm_gpp", "elm_sr", "surrogate_gpp", "surrogate_sr"), arrays):
                pooled[name].append(array)
    joint["pooled"] = tuple(np.concatenate(pooled[name]) for name in ("elm_gpp", "elm_sr", "surrogate_gpp", "surrogate_sr"))  # type: ignore[assignment]
    for site in (*SITES, "pooled"):
        elm_gpp, elm_sr, surrogate_gpp, surrogate_sr = joint[site]
        panels = {row["source"]: row for row in validation["panels"] if row["site"] == site}
        require(set(panels) == {"ELM", "Gated full-chain surrogate"}, "density panel scope mismatch")
        for source, gpp, sr in (("ELM", elm_gpp, elm_sr), ("Gated full-chain surrogate", surrogate_gpp, surrogate_sr)):
            panel = panels[source]
            x_edges = np.linspace(float(panel["gpp_axis_min"]), float(panel["gpp_axis_max"]), 201)
            y_edges = np.linspace(float(panel["sr_axis_min"]), float(panel["sr_axis_max"]), 201)
            histogram, _, _ = np.histogram2d(gpp, sr, bins=(x_edges, y_edges))
            histogram = histogram.astype(np.float64) / float(np.sum(histogram))
            require(histogram.shape == (200, 200) and abs(float(np.sum(histogram)) - 1.0) <= 1e-12, "density recomputation mismatch")
            require(close(float(panel["unit_mass"]), float(np.sum(histogram)), 1e-12), "density recorded mass mismatch")
    return 6


def stage_products(config: Mapping[str, Any], aggregate: Path, attempt: Path) -> tuple[Path, int]:
    products = Path(config["output_root"]) / "products"
    handoff = Path(config["output_root"]) / "handoff"
    require(products.is_dir() and handoff.is_dir(), "product destination missing")
    require(not any(products.iterdir()) and not any(handoff.iterdir()), "product destination is not empty")
    aggregate_report = json.loads((aggregate / "aggregate_report.json").read_text(encoding="utf-8"))
    names = sorted(["aggregate_report.json", *aggregate_report["output_sha256"].keys()])
    manifest = {
        "schema": "three-stage-iter015-products-manifest-v1",
        "result": "pass",
        "gpp_output_policy": GPP_POLICY,
        "files": {name: {"sha256": sha256_file(aggregate / name), "size_bytes": (aggregate / name).stat().st_size} for name in names},
        "fixed_test_access": False,
        "all_development_fit": False,
        "release_modified": False,
    }
    manifest_path = attempt / "products_manifest.json"
    write_json(manifest_path, manifest)
    for name in names:
        shutil.copy2(aggregate / name, products / name)
        require(sha256_file(products / name) == manifest["files"][name]["sha256"], f"staged product hash mismatch: {name}")
    shutil.copy2(manifest_path, products / "products_manifest.json")
    shutil.copy2(aggregate / "uncertainty_handoff.json", handoff / "uncertainty_handoff.json")
    shutil.copy2(manifest_path, handoff / "products_manifest.json")
    require(sha256_file(products / "products_manifest.json") == sha256_file(manifest_path), "staged product manifest mismatch")
    require(sha256_file(handoff / "uncertainty_handoff.json") == sha256_file(aggregate / "uncertainty_handoff.json"), "staged uncertainty handoff mismatch")
    require(sha256_file(handoff / "products_manifest.json") == sha256_file(manifest_path), "staged handoff manifest mismatch")
    return manifest_path, len(names)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--aggregate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), f"final output exists: {args.output}")
    args.output.mkdir(parents=True)
    config = load_config(args.config)
    snapshot, splits = validate_config(config, verify_snapshot_components=True)
    paths = split_paths(config)
    validate_identities(snapshot, splits, paths)
    aggregate_report = validate_aggregate_hashes(args.aggregate)
    validate_concatenation(paths, args.aggregate)
    gate_rows = validate_gate(snapshot, splits, paths, args.aggregate)
    representative_metric_rows = validate_representative_metrics(snapshot, splits, paths, args.aggregate)
    covariance_rows, balanced_covariance_rows = validate_covariance(args.aggregate)
    propagation_rows, balanced_propagation_rows = validate_propagation_correlations(args.aggregate)
    gpp_sr_rows = validate_gpp_sr_correlations(snapshot, splits, paths, args.aggregate)
    density_panels = validate_density(snapshot, splits, paths[0], args.aggregate)
    manifest_path, staged_files = stage_products(config, args.aggregate, args.output)
    final_report = {
        "schema": "three-stage-iter015-final-validation-v1",
        "result": "pass",
        "split_count": 20,
        "aggregate_report_sha256": sha256_file(args.aggregate / "aggregate_report.json"),
        "products_manifest_sha256": sha256_file(manifest_path),
        "staged_product_files": staged_files,
        "gate_recomputed_rows": gate_rows,
        "representative_metric_rows": representative_metric_rows,
        "cn_covariance_rows": covariance_rows,
        "cn_member_balanced_covariance_rows": balanced_covariance_rows,
        "propagation_correlation_rows": propagation_rows,
        "balanced_propagation_correlation_rows": balanced_propagation_rows,
        "gpp_sr_correlation_rows": gpp_sr_rows,
        "density_panels": density_panels,
        "joint_density_grid_shape": [200, 200],
        "aggregate_output_hash_count": len(aggregate_report["output_sha256"]),
        "diagnostic_figures": ["error_propagation.png", "gpp_gate_comparison.png", "gpp_sr_joint.png"],
        "gpp_output_policy": GPP_POLICY,
        "fixed_test_access": False,
        "all_development_fit": False,
        "cross_fitting": False,
        "release_modified": False,
        "performance_threshold_applied": False,
    }
    write_json(args.output / "final_validation_report.json", final_report)
    handoff = Path(config["output_root"]) / "handoff"
    shutil.copy2(args.output / "final_validation_report.json", handoff / "final_validation_report.json")
    require(sha256_file(handoff / "final_validation_report.json") == sha256_file(args.output / "final_validation_report.json"), "handoff final report mismatch")
    print(
        "ITER015_FINAL_VALIDATE_OK splits=20 products=28 gate=6 metrics=24 covariance=160 "
        "correlations=120 density=6 fixed_test=false",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
