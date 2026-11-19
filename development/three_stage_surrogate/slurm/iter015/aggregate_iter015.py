#!/usr/bin/env python
"""Aggregate Iter015 held-out full-chain robustness evidence."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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


METRIC_NAMES = ("r2", "rmse", "mae", "bias", "residual_std")
SUMMARY_NAMES = ("mean", "median", "sample_sd", "q10", "q25", "q75", "q90", "minimum", "maximum")
RELATIONSHIPS = (
    ("cn_vs_gpp", "cn_rms_log_error", "gpp_hourly_rmse"),
    ("cn_vs_sr", "cn_rms_log_error", "sr_hourly_rmse"),
    ("gpp_vs_sr", "gpp_hourly_rmse", "sr_hourly_rmse"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"empty aggregate table: {path.name}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stats(values: Iterable[float]) -> dict[str, float]:
    data = np.asarray(list(values), dtype=np.float64)
    require(data.size > 0 and np.all(np.isfinite(data)), "invalid aggregate statistic input")
    return {
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "sample_sd": float(np.std(data, ddof=1)) if data.size > 1 else 0.0,
        "q10": float(np.quantile(data, 0.10, method="linear")),
        "q25": float(np.quantile(data, 0.25, method="linear")),
        "q75": float(np.quantile(data, 0.75, method="linear")),
        "q90": float(np.quantile(data, 0.90, method="linear")),
        "minimum": float(np.min(data)),
        "maximum": float(np.max(data)),
    }


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    left = np.asarray(x, dtype=np.float64).reshape(-1)
    right = np.asarray(y, dtype=np.float64).reshape(-1)
    require(left.size == right.size and left.size > 1, "correlation size mismatch")
    require(np.all(np.isfinite(left)) and np.all(np.isfinite(right)), "correlation nonfinite")
    return float(np.corrcoef(left, right)[0, 1])


def split_directories(config: Mapping[str, Any]) -> list[Path]:
    pilot = Path(config["run_directories"]["pilot"]) / "attempt_1" / "split_00"
    production = Path(config["run_directories"]["production"]) / "attempt_1"
    paths = [pilot] + [production / f"split_{split_id:02d}" for split_id in range(1, 20)]
    require(all(path.is_dir() for path in paths), "Iter015 aggregate split set incomplete")
    return paths


def validate_split_evidence(
    paths: Sequence[Path], splits: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], int]:
    reports: list[dict[str, Any]] = []
    warning_count = 0
    for split_id, path in enumerate(paths):
        report_path = path / "split_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        require(report.get("result") == "pass" and int(report.get("split_id", -1)) == split_id, "split report mismatch")
        require(report.get("smoke") is False and int(report.get("hours", -1)) == 61320, "split coverage mismatch")
        require(int(report.get("train_member_count", -1)) == 655, "training count mismatch")
        require(int(report.get("validation_member_count", -1)) == 164, "validation count mismatch")
        require(report.get("gpp_output_policy") == GPP_POLICY, "GPP policy mismatch")
        require(report.get("artifact_reload_complete") is True, "artifact reload missing")
        require(report.get("scaled_scratch_removed") is True, "scaled scratch not removed")
        for key in ("fixed_test_access", "all_development_fit", "cross_fitting", "published_upstream_training_inputs", "release_modified"):
            require(report.get(key) is False, f"prohibited scope flag: {key}")
        expected_members = list(splits["splits"][split_id]["validation_member_ids"])
        layout = json.loads((path / "layout.json").read_text(encoding="utf-8"))
        require(layout.get("validation_member_ids") == expected_members, "validation member order mismatch")
        require(layout.get("train_member_ids") == list(splits["splits"][split_id]["train_member_ids"]), "training member order mismatch")
        for name, expected in report["file_sha256"].items():
            require(sha256_file(path / name) == expected, f"split file hash mismatch: {split_id} {name}")
        for stage, expected in report["artifact_sha256"].items():
            require(sha256_file(path / "artifacts" / f"{stage}_fold.pkl") == expected, f"artifact hash mismatch: {split_id} {stage}")
        convergence = json.loads((path / "convergence.json").read_text(encoding="utf-8"))
        require(convergence.get("gpp") == [] and convergence.get("sr") == [], "flux convergence warning")
        warning_count += sum(len(item.get("warnings", [])) for item in convergence["spinup"].values())
        reports.append({"split_id": split_id, "path": str(path), "report_sha256": sha256_file(report_path)})
    require(warning_count == 23, "retained spinup warning count mismatch")
    return reports, warning_count


def collect_tables(paths: Sequence[Path], output: Path) -> dict[str, list[dict[str, str]]]:
    mapping = {
        "metric_distribution.csv": "metrics.csv",
        "gpp_gate_distribution.csv": "gpp_gate_comparison.csv",
        "error_propagation_members.csv": "error_propagation.csv",
        "depth_error_distribution.csv": "depth_error_dependence.csv",
    }
    tables: dict[str, list[dict[str, str]]] = {}
    expected_counts = {
        "metric_distribution.csv": 960,
        "gpp_gate_distribution.csv": 120,
        "error_propagation_members.csv": 6560,
        "depth_error_distribution.csv": 640,
    }
    for aggregate_name, source_name in mapping.items():
        rows: list[dict[str, str]] = []
        for split_id, path in enumerate(paths):
            block = read_csv(path / source_name)
            require(all(int(row["split_id"]) == split_id for row in block), "table split mismatch")
            rows.extend(block)
        require(len(rows) == expected_counts[aggregate_name], f"aggregate row count mismatch: {aggregate_name}")
        write_csv(output / aggregate_name, rows)
        tables[aggregate_name] = rows
    return tables


def summarize_metrics(rows: Sequence[Mapping[str, str]], output: Path) -> tuple[int, int, int]:
    grouping_fields = ("stage", "partition", "site", "target", "scale", "resolution")
    grouped: dict[tuple[str, ...], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    indexed: dict[tuple[Any, ...], Mapping[str, str]] = {}
    for row in rows:
        key = tuple(row[field] for field in grouping_fields)
        for metric in METRIC_NAMES:
            grouped[key][metric].append(float(row[metric]))
        indexed[(int(row["split_id"]),) + key] = row
    summary_rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        for metric in METRIC_NAMES:
            summary_rows.append({**dict(zip(grouping_fields, key)), "metric": metric, **stats(grouped[key][metric])})
    write_csv(output / "metric_summary.csv", summary_rows)

    gap_rows: list[dict[str, Any]] = []
    gap_summary: dict[tuple[str, ...], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    base_fields = ("stage", "site", "target", "scale", "resolution")
    for split_id in range(20):
        keys = sorted({tuple(row[field] for field in base_fields) for row in rows if int(row["split_id"]) == split_id})
        for base in keys:
            training_key = (split_id, base[0], "training", *base[1:])
            validation_key = (split_id, base[0], "validation", *base[1:])
            training = indexed[training_key]
            validation = indexed[validation_key]
            values = {
                "r2_train_minus_validation": float(training["r2"]) - float(validation["r2"]),
                "rmse_validation_minus_train": float(validation["rmse"]) - float(training["rmse"]),
                "mae_validation_minus_train": float(validation["mae"]) - float(training["mae"]),
                "absolute_bias_validation_minus_train": abs(float(validation["bias"])) - abs(float(training["bias"])),
                "residual_std_validation_minus_train": float(validation["residual_std"]) - float(training["residual_std"]),
            }
            gap_rows.append({"split_id": split_id, **dict(zip(base_fields, base)), **values})
            for name, value in values.items():
                gap_summary[base][name].append(value)
    write_csv(output / "training_validation_gaps.csv", gap_rows)
    gap_summary_rows: list[dict[str, Any]] = []
    for base in sorted(gap_summary):
        for metric, values in gap_summary[base].items():
            gap_summary_rows.append({**dict(zip(base_fields, base)), "gap_metric": metric, "positive_means_validation_degradation": True, **stats(values)})
    write_csv(output / "training_validation_gap_summary.csv", gap_summary_rows)
    return len(summary_rows), len(gap_rows), len(gap_summary_rows)


def summarize_gate(rows: Sequence[Mapping[str, str]], output: Path) -> int:
    grouped: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        require(int(row["same_target_count"]) > 0 and int(row["negative_raw_count"]) > 0, "gate comparison pairing invalid")
        key = (row["site"], row["resolution"])
        for metric in ("gated_minus_raw_r2", "raw_minus_gated_rmse"):
            grouped[key][metric].append(float(row[metric]))
    summary: list[dict[str, Any]] = []
    for key in sorted(grouped):
        for metric, values in grouped[key].items():
            summary.append({"site": key[0], "resolution": key[1], "paired_difference": metric, **stats(values)})
    write_csv(output / "gpp_gate_summary.csv", summary)
    return len(summary)


def summarize_propagation(rows: Sequence[Mapping[str, str]], output: Path) -> tuple[int, int]:
    correlations: list[dict[str, Any]] = []
    for split_id in range(20):
        split_rows = [row for row in rows if int(row["split_id"]) == split_id]
        for scope in (*SITES, "pooled"):
            active = split_rows if scope == "pooled" else [row for row in split_rows if row["site"] == scope]
            for relationship, x_name, y_name in RELATIONSHIPS:
                correlations.append({
                    "split_id": split_id,
                    "site": scope,
                    "relationship": relationship,
                    "x_metric": x_name,
                    "y_metric": y_name,
                    "pearson_correlation": pearson(
                        np.asarray([float(row[x_name]) for row in active]),
                        np.asarray([float(row[y_name]) for row in active]),
                    ),
                    "member_rows": len(active),
                })
    write_csv(output / "error_propagation_correlations.csv", correlations)
    summaries: list[dict[str, Any]] = []
    for site in (*SITES, "pooled"):
        for relationship, _, _ in RELATIONSHIPS:
            values = [float(row["pearson_correlation"]) for row in correlations if row["site"] == site and row["relationship"] == relationship]
            summaries.append({"site": site, "relationship": relationship, "repetition_count": 20, **stats(values)})
    write_csv(output / "error_propagation_correlation_summary.csv", summaries)
    return len(correlations), len(summaries)


def summarize_depth(rows: Sequence[Mapping[str, str]], output: Path) -> int:
    grouped: dict[tuple[str, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = (row["site"], row["row"], row["column"])
        grouped[key]["covariance"].append(float(row["covariance"]))
        grouped[key]["correlation"].append(float(row["correlation"]))
    summaries: list[dict[str, Any]] = []
    for key in sorted(grouped):
        for statistic, values in grouped[key].items():
            summaries.append({"site": key[0], "row": key[1], "column": key[2], "statistic": statistic, **stats(values)})
    write_csv(output / "depth_error_summary.csv", summaries)
    return len(summaries)


def cn_evidence(paths: Sequence[Path], output: Path) -> tuple[int, int]:
    member_rows: list[dict[str, Any]] = []
    covariance_rows: list[dict[str, Any]] = []
    for split_id, path in enumerate(paths):
        with Dataset(str(path / "heldout_predictions.nc"), "r") as dataset:
            sites = [str(value) for value in dataset.variables["site"][:]]
            members = [str(value) for value in dataset.variables["member_id"][:]]
            targets = [str(value) for value in dataset.variables["target"][:]]
            require(sites == list(SITES) and targets == list(TARGETS) and len(members) == 164, "C/N prediction schema mismatch")
            truth = np.asarray(dataset.variables["CN_elm"][:], dtype=np.float64)
            predicted = np.asarray(dataset.variables["CN_predicted"][:], dtype=np.float64)
        require(np.all(truth > 0.0) and np.all(predicted > 0.0), "C/N values must be positive")
        log_errors = np.log(predicted) - np.log(truth)
        for site_index, site in enumerate(SITES):
            covariance = np.cov(log_errors[site_index], rowvar=False, ddof=0)
            correlation = np.corrcoef(log_errors[site_index], rowvar=False)
            for row_index, row_target in enumerate(TARGETS):
                for column_index, column_target in enumerate(TARGETS):
                    covariance_rows.append({
                        "split_id": split_id,
                        "site": site,
                        "row_target": row_target,
                        "column_target": column_target,
                        "log_error_covariance": float(covariance[row_index, column_index]),
                        "log_error_correlation": float(correlation[row_index, column_index]),
                        "member_count": len(members),
                    })
            for member_index, member in enumerate(members):
                row: dict[str, Any] = {"split_id": split_id, "site": site, "member_id": member}
                for target_index, target in enumerate(TARGETS):
                    observed = float(truth[site_index, member_index, target_index])
                    estimate = float(predicted[site_index, member_index, target_index])
                    row[f"{target}_elm"] = observed
                    row[f"{target}_predicted"] = estimate
                    row[f"{target}_physical_error"] = estimate - observed
                    row[f"{target}_log_error"] = float(log_errors[site_index, member_index, target_index])
                member_rows.append(row)
    require(len(member_rows) == 6560 and len(covariance_rows) == 160, "C/N evidence count mismatch")
    write_csv(output / "cn_member_errors.csv", member_rows)
    write_csv(output / "cn_log_covariance.csv", covariance_rows)
    return len(member_rows), len(covariance_rows)


def member_balanced_uncertainty(output: Path) -> tuple[int, int, int, int, int, int]:
    cn_rows = read_csv(output / "cn_member_errors.csv")
    propagation_rows = read_csv(output / "error_propagation_members.csv")
    cn_grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    propagation_grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in cn_rows:
        cn_grouped[(row["site"], row["member_id"])].append(row)
    for row in propagation_rows:
        propagation_grouped[(row["site"], row["member_id"])].append(row)
    require(set(cn_grouped) == set(propagation_grouped), "member-balanced key mismatch")
    for site in SITES:
        counts = [len(rows) for (active_site, _), rows in cn_grouped.items() if active_site == site]
        require(len(counts) == 819, "member-balanced development count mismatch")
        require(counts.count(4) == 815 and counts.count(5) == 4, "member-balanced appearance count mismatch")

    balanced_cn: list[dict[str, Any]] = []
    balanced_propagation: list[dict[str, Any]] = []
    for key in sorted(cn_grouped):
        site, member = key
        active_cn = cn_grouped[key]
        active_propagation = propagation_grouped[key]
        require(len(active_cn) == len(active_propagation), "member-balanced appearance mismatch")
        cn_row: dict[str, Any] = {"site": site, "member_id": member, "validation_appearances": len(active_cn)}
        for target in TARGETS:
            physical = np.asarray([float(row[f"{target}_physical_error"]) for row in active_cn], dtype=np.float64)
            log_error = np.asarray([float(row[f"{target}_log_error"]) for row in active_cn], dtype=np.float64)
            cn_row[f"{target}_mean_physical_error"] = float(np.mean(physical))
            cn_row[f"{target}_rms_physical_error"] = float(np.sqrt(np.mean(physical * physical)))
            cn_row[f"{target}_mean_log_error"] = float(np.mean(log_error))
            cn_row[f"{target}_rms_log_error"] = float(np.sqrt(np.mean(log_error * log_error)))
        balanced_cn.append(cn_row)
        balanced_propagation.append({
            "site": site,
            "member_id": member,
            "validation_appearances": len(active_propagation),
            "mean_cn_rms_log_error": float(np.mean([float(row["cn_rms_log_error"]) for row in active_propagation])),
            "mean_gpp_hourly_rmse": float(np.mean([float(row["gpp_hourly_rmse"]) for row in active_propagation])),
            "mean_sr_hourly_rmse": float(np.mean([float(row["sr_hourly_rmse"]) for row in active_propagation])),
        })
    require(len(balanced_cn) == len(balanced_propagation) == 1638, "member-balanced row count mismatch")
    write_csv(output / "cn_member_balanced.csv", balanced_cn)
    write_csv(output / "error_propagation_member_balanced.csv", balanced_propagation)

    cn_summary: list[dict[str, Any]] = []
    for site in (*SITES, "pooled"):
        active = balanced_cn if site == "pooled" else [row for row in balanced_cn if row["site"] == site]
        require(len(active) == (1638 if site == "pooled" else 819), "balanced C/N summary count mismatch")
        for target in TARGETS:
            for metric in ("mean_physical_error", "rms_physical_error", "mean_log_error", "rms_log_error"):
                field = f"{target}_{metric}"
                cn_summary.append({"site": site, "target": target, "member_balanced_metric": metric, "equal_weight_member_rows": len(active), **stats(float(row[field]) for row in active)})
    write_csv(output / "cn_member_balanced_summary.csv", cn_summary)

    covariance_rows: list[dict[str, Any]] = []
    for site in SITES:
        active = [row for row in balanced_cn if row["site"] == site]
        values = np.column_stack(tuple([float(row[f"{target}_mean_log_error"]) for row in active] for target in TARGETS))
        covariance = np.cov(values, rowvar=False, ddof=0)
        correlation = np.corrcoef(values, rowvar=False)
        for row_index, row_target in enumerate(TARGETS):
            for column_index, column_target in enumerate(TARGETS):
                covariance_rows.append({
                    "site": site,
                    "row_target": row_target,
                    "column_target": column_target,
                    "member_balanced_log_error_covariance": float(covariance[row_index, column_index]),
                    "member_balanced_log_error_correlation": float(correlation[row_index, column_index]),
                    "equal_weight_members": 819,
                })
    write_csv(output / "cn_member_balanced_covariance.csv", covariance_rows)

    propagation_summary: list[dict[str, Any]] = []
    propagation_correlations: list[dict[str, Any]] = []
    balanced_relationships = (
        ("cn_vs_gpp", "mean_cn_rms_log_error", "mean_gpp_hourly_rmse"),
        ("cn_vs_sr", "mean_cn_rms_log_error", "mean_sr_hourly_rmse"),
        ("gpp_vs_sr", "mean_gpp_hourly_rmse", "mean_sr_hourly_rmse"),
    )
    for site in (*SITES, "pooled"):
        active = balanced_propagation if site == "pooled" else [row for row in balanced_propagation if row["site"] == site]
        require(len(active) == (1638 if site == "pooled" else 819), "balanced propagation summary count mismatch")
        for metric in ("mean_cn_rms_log_error", "mean_gpp_hourly_rmse", "mean_sr_hourly_rmse"):
            propagation_summary.append({"site": site, "member_balanced_metric": metric, "equal_weight_member_rows": len(active), **stats(float(row[metric]) for row in active)})
        for relationship, x_name, y_name in balanced_relationships:
            propagation_correlations.append({
                "site": site,
                "relationship": relationship,
                "x_metric": x_name,
                "y_metric": y_name,
                "pearson_correlation": pearson(
                    np.asarray([float(row[x_name]) for row in active]),
                    np.asarray([float(row[y_name]) for row in active]),
                ),
                "equal_weight_member_rows": len(active),
            })
    write_csv(output / "error_propagation_member_balanced_summary.csv", propagation_summary)
    write_csv(output / "error_propagation_member_balanced_correlations.csv", propagation_correlations)
    return (
        len(balanced_cn), len(cn_summary), len(covariance_rows),
        len(balanced_propagation), len(propagation_summary), len(propagation_correlations),
    )


def flux_correlations_and_joint(
    config: Mapping[str, Any], snapshot: Any, splits: Mapping[str, Any], paths: Sequence[Path], output: Path
) -> tuple[list[dict[str, Any]], dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    rows: list[dict[str, Any]] = []
    joint: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for split_id, path in enumerate(paths):
        members = list(splits["splits"][split_id]["validation_member_ids"])
        pooled: dict[str, list[np.ndarray]] = defaultdict(list)
        with Dataset(str(path / "heldout_predictions.nc"), "r") as dataset:
            for site_index, site in enumerate(SITES):
                elm_gpp = _target(snapshot, site, "GPP", members, 61320)
                elm_sr = _target(snapshot, site, "SR", members, 61320)
                surrogate_gpp = np.asarray(dataset.variables["GPP_gated"][site_index], dtype=np.float32)
                surrogate_sr = np.asarray(dataset.variables["SR_predicted"][site_index], dtype=np.float32)
                require(elm_gpp.shape == surrogate_gpp.shape == elm_sr.shape == surrogate_sr.shape, "joint prediction shape mismatch")
                rows.extend((
                    {"split_id": split_id, "site": site, "source": "ELM", "pearson_gpp_sr": pearson(elm_gpp, elm_sr), "hourly_pairs": elm_gpp.size},
                    {"split_id": split_id, "site": site, "source": "full_chain_surrogate", "pearson_gpp_sr": pearson(surrogate_gpp, surrogate_sr), "hourly_pairs": surrogate_gpp.size},
                ))
                for name, array in (("elm_gpp", elm_gpp), ("elm_sr", elm_sr), ("surrogate_gpp", surrogate_gpp), ("surrogate_sr", surrogate_sr)):
                    pooled[name].append(array.reshape(-1))
                if split_id == 0:
                    joint[site] = (elm_gpp.reshape(-1), elm_sr.reshape(-1), surrogate_gpp.reshape(-1), surrogate_sr.reshape(-1))
        rows.extend((
            {"split_id": split_id, "site": "pooled", "source": "ELM", "pearson_gpp_sr": pearson(np.concatenate(pooled["elm_gpp"]), np.concatenate(pooled["elm_sr"])), "hourly_pairs": sum(item.size for item in pooled["elm_gpp"])},
            {"split_id": split_id, "site": "pooled", "source": "full_chain_surrogate", "pearson_gpp_sr": pearson(np.concatenate(pooled["surrogate_gpp"]), np.concatenate(pooled["surrogate_sr"])), "hourly_pairs": sum(item.size for item in pooled["surrogate_gpp"])},
        ))
        if split_id == 0:
            joint["pooled"] = tuple(np.concatenate(pooled[name]) for name in ("elm_gpp", "elm_sr", "surrogate_gpp", "surrogate_sr"))  # type: ignore[assignment]
    write_csv(output / "gpp_sr_correlations.csv", rows)
    summary_rows: list[dict[str, Any]] = []
    for site in (*SITES, "pooled"):
        for source in ("ELM", "full_chain_surrogate"):
            values = [float(row["pearson_gpp_sr"]) for row in rows if row["site"] == site and row["source"] == source]
            summary_rows.append({"site": site, "source": source, "repetition_count": 20, **stats(values)})
    write_csv(output / "gpp_sr_correlation_summary.csv", summary_rows)
    return rows, joint


def error_propagation_figure(rows: Sequence[Mapping[str, str]], summaries: Path, output: Path) -> None:
    summary_rows = read_csv(summaries)
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), constrained_layout=True)
    colors = {"ABBY": "#1f77b4", "JERC": "#d95f02"}
    labels = {
        "cn_rms_log_error": "C/N RMS log-error",
        "gpp_hourly_rmse": "GPP hourly RMSE",
        "sr_hourly_rmse": "SR hourly RMSE",
    }
    for axis, (relationship, x_name, y_name) in zip(axes, RELATIONSHIPS):
        for site in SITES:
            active = [row for row in rows if row["site"] == site]
            axis.scatter([float(row[x_name]) for row in active], [float(row[y_name]) for row in active], s=8, alpha=0.28, color=colors[site], label=site)
        annotations = []
        for site in (*SITES, "pooled"):
            row = next(item for item in summary_rows if item["site"] == site and item["relationship"] == relationship)
            annotations.append(f"{site} median r={float(row['median']):.3f}")
        axis.text(0.02, 0.98, "\n".join(annotations), transform=axis.transAxes, va="top", fontsize=8, bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"})
        axis.set_xlabel(labels[x_name])
        axis.set_ylabel(labels[y_name])
        axis.grid(alpha=0.2)
    axes[0].legend(frameon=False)
    fig.suptitle("Held-out full-chain member error propagation across 20 repetitions")
    fig.savefig(output / "error_propagation.png", dpi=180)
    plt.close(fig)


def gate_figure(rows: Sequence[Mapping[str, str]], output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), constrained_layout=True)
    colors = {"ABBY": "#1f77b4", "JERC": "#d95f02", "pooled": "#4d4d4d"}
    markers = {"hourly": "o", "daily": "s"}
    for site in (*SITES, "pooled"):
        for resolution in ("hourly", "daily"):
            active = sorted((row for row in rows if row["site"] == site and row["resolution"] == resolution), key=lambda row: int(row["split_id"]))
            x = [int(row["split_id"]) for row in active]
            label = f"{site} {resolution}"
            axes[0].plot(x, [float(row["gated_minus_raw_r2"]) for row in active], marker=markers[resolution], ms=3, lw=0.8, color=colors[site], alpha=0.8, label=label)
            axes[1].plot(x, [float(row["raw_minus_gated_rmse"]) for row in active], marker=markers[resolution], ms=3, lw=0.8, color=colors[site], alpha=0.8, label=label)
    axes[0].axhline(0.0, color="black", lw=0.8)
    axes[1].axhline(0.0, color="black", lw=0.8)
    axes[0].set_ylabel("Gated minus raw R²")
    axes[1].set_ylabel("Raw minus gated RMSE")
    for axis in axes:
        axis.set_xlabel("Repetition")
        axis.set_xticks(range(0, 20, 2))
        axis.grid(alpha=0.2)
    axes[1].legend(frameon=False, fontsize=8, ncol=2)
    fig.suptitle("Paired hard-zero GPP comparison on identical held-out ELM targets")
    fig.savefig(output / "gpp_gate_comparison.png", dpi=180)
    plt.close(fig)


def contour_levels(histogram: np.ndarray) -> list[float]:
    values = np.sort(histogram.reshape(-1))[::-1]
    cumulative = np.cumsum(values)
    require(values.size > 0 and cumulative[-1] > 0.0, "empty density histogram")
    cumulative /= cumulative[-1]
    thresholds = [float(values[min(int(np.searchsorted(cumulative, mass, side="left")), values.size - 1)]) for mass in (0.99, 0.90, 0.75, 0.50)]
    return sorted(set(thresholds))


def joint_figure(joint: Mapping[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]], output: Path) -> list[dict[str, Any]]:
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.0), constrained_layout=True)
    validation: list[dict[str, Any]] = []
    for column, site in enumerate((*SITES, "pooled")):
        elm_gpp, elm_sr, surrogate_gpp, surrogate_sr = joint[site]
        x_values = np.concatenate((elm_gpp, surrogate_gpp))
        y_values = np.concatenate((elm_sr, surrogate_sr))
        x_bounds = np.quantile(x_values, (0.001, 0.999), method="linear")
        y_bounds = np.quantile(y_values, (0.001, 0.999), method="linear")
        x_edges = np.linspace(float(x_bounds[0]), float(x_bounds[1]), 201)
        y_edges = np.linspace(float(y_bounds[0]), float(y_bounds[1]), 201)
        for row_index, (gpp, sr, title, color) in enumerate((
            (elm_gpp, elm_sr, "ELM", "Blues"),
            (surrogate_gpp, surrogate_sr, "Gated full-chain surrogate", "Oranges"),
        )):
            histogram, _, _ = np.histogram2d(gpp, sr, bins=(x_edges, y_edges))
            histogram = histogram.astype(np.float64)
            histogram /= np.sum(histogram)
            require(histogram.shape == (200, 200), "joint density grid shape mismatch")
            require(abs(float(np.sum(histogram)) - 1.0) <= 1e-12, "joint density normalization mismatch")
            validation.append({
                "site": site,
                "source": title,
                "grid_rows": int(histogram.shape[0]),
                "grid_columns": int(histogram.shape[1]),
                "unit_mass": float(np.sum(histogram)),
                "gpp_axis_min": float(x_bounds[0]),
                "gpp_axis_max": float(x_bounds[1]),
                "sr_axis_min": float(y_bounds[0]),
                "sr_axis_max": float(y_bounds[1]),
                "axis_quantile_bounds": [0.001, 0.999],
                "enclosed_mass_contours": [0.50, 0.75, 0.90, 0.99],
            })
            centers_x = 0.5 * (x_edges[:-1] + x_edges[1:])
            centers_y = 0.5 * (y_edges[:-1] + y_edges[1:])
            axis = axes[row_index, column]
            levels = contour_levels(histogram)
            axis.contour(centers_x, centers_y, histogram.T, levels=levels, cmap=color, linewidths=1.2)
            axis.set_xlim(x_bounds)
            axis.set_ylim(y_bounds)
            axis.set_title(f"{site}: {title}")
            axis.set_xlabel("Hourly GPP")
            axis.set_ylabel("Hourly SR")
            axis.grid(alpha=0.15)
    fig.suptitle("Split 0 matched GPP–SR density contours (50/75/90/99% enclosed mass)")
    fig.savefig(output / "gpp_sr_joint.png", dpi=180)
    plt.close(fig)
    require(len(validation) == 6, "joint density validation count mismatch")
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), f"aggregate output exists: {args.output}")
    args.output.mkdir(parents=True)
    config = load_config(args.config)
    snapshot, splits = validate_config(config, verify_snapshot_components=True)
    paths = split_directories(config)
    split_reports, warning_count = validate_split_evidence(paths, splits)
    tables = collect_tables(paths, args.output)
    metric_summary_rows, gap_rows, gap_summary_rows = summarize_metrics(tables["metric_distribution.csv"], args.output)
    gate_summary_rows = summarize_gate(tables["gpp_gate_distribution.csv"], args.output)
    propagation_rows, propagation_summary_rows = summarize_propagation(tables["error_propagation_members.csv"], args.output)
    depth_summary_rows = summarize_depth(tables["depth_error_distribution.csv"], args.output)
    cn_member_rows, cn_covariance_rows = cn_evidence(paths, args.output)
    balanced_counts = member_balanced_uncertainty(args.output)
    gpp_sr_rows, joint = flux_correlations_and_joint(config, snapshot, splits, paths, args.output)
    error_propagation_figure(tables["error_propagation_members.csv"], args.output / "error_propagation_correlation_summary.csv", args.output)
    gate_figure(tables["gpp_gate_distribution.csv"], args.output)
    joint_validation = joint_figure(joint, args.output)
    write_json(args.output / "gpp_sr_joint_grid_validation.json", {
        "schema": "three-stage-iter015-joint-grid-validation-v1",
        "result": "pass",
        "split_id": 0,
        "common_grid_per_scope": True,
        "grid_shape": [200, 200],
        "unit_mass_tolerance": 1e-12,
        "panels": joint_validation,
    })

    cn_target_provenance = {
        "ordered_targets": ["TOTSOMC", "TOTSOMN"],
        "TOTSOMC": {"definition": "soil1-soil4 full-profile integral over the validated active decomposition column", "units": "gC/m^2"},
        "TOTSOMN": {"definition": "soil1-soil4 full-profile integral over the validated active decomposition column", "units": "gN/m^2"},
        "included_pools": ["soil1", "soil2", "soil3", "soil4"],
        "excluded_pools": ["litter", "coarse_woody_debris"],
        "active_layer_mask": "validated ELM active decomposition-column mask; first nlevdecomp=10 soil layers",
        "layer_thickness_source": "ELM initVerticalMod DZSOI layer thicknesses corresponding to the active mask",
        "integration_depth": "full validated active decomposition column through bottom interface ZISOI[10] of the tenth active layer",
        "source_concentrations": "soil pool C and N in gC/m^3 and gN/m^3 multiplied by layer-specific DZSOI",
        "neon_depth_correction_applied_to_surrogate": False,
    }

    provenance = {
        "schema": "three-stage-iter015-aggregate-provenance-v1",
        "plan_sha256": config["plan_sha256"],
        "snapshot_sha256": config["snapshot_sha256"],
        "global_split_sha256": config["global_split_sha256"],
        "repeated_split_manifest_sha256": config["repeated_split_manifest_sha256"],
        "split_design_sha256": config["split_design_sha256"],
        "gpp_configuration_sha256": config["gpp_configuration_sha256"],
        "sr_configuration_sha256": config["sr_configuration_sha256"],
        "gpp_output_policy": GPP_POLICY,
        "cn_target_provenance": cn_target_provenance,
        "split_reports": split_reports,
        "fixed_test_access": False,
        "all_development_fit": False,
        "cross_fitting": False,
        "release_modified": False,
    }
    write_json(args.output / "provenance.json", provenance)
    handoff = {
        "schema": "three-stage-iter015-uncertainty-handoff-v1",
        "basis": "twenty overlapping held-out development repetitions through the complete fold-specific chain",
        "gpp_output_policy": GPP_POLICY,
        "residual_convention": "prediction minus ELM",
        "cn_member_errors": "cn_member_errors.csv",
        "cn_log_covariance": "cn_log_covariance.csv",
        "cn_member_balanced": "cn_member_balanced.csv",
        "cn_member_balanced_summary": "cn_member_balanced_summary.csv",
        "cn_member_balanced_covariance": "cn_member_balanced_covariance.csv",
        "flux_metric_distribution": "metric_distribution.csv",
        "flux_metric_summary": "metric_summary.csv",
        "gpp_gate_distribution": "gpp_gate_distribution.csv",
        "error_propagation": "error_propagation_members.csv",
        "error_propagation_member_balanced": "error_propagation_member_balanced.csv",
        "error_propagation_member_balanced_summary": "error_propagation_member_balanced_summary.csv",
        "error_propagation_member_balanced_correlations": "error_propagation_member_balanced_correlations.csv",
        "depth_dependence": "depth_error_distribution.csv",
        "heldout_prediction_files": [str(path / "heldout_predictions.nc") for path in paths],
        "selection_interface": "select site, target, resolution, metric, and declared summary from the supplied CSV tables without fixed-test access or model replay",
        "member_balancing": "first average each site/member over its four or five held-out appearances, then give all 819 development members equal weight within site summaries",
        "cn_target_provenance": cn_target_provenance,
        "limitations": [
            "hourly errors are serially correlated",
            "GPP and SR errors are cross-correlated",
            "validation sets overlap across the twenty repetitions",
            "ABBY and JERC only",
            "robustness chains train on 655 members rather than a final 819-member fit",
            "surrogate error is not observational uncertainty and is not a likelihood choice",
        ],
        "fixed_test_access": False,
    }
    write_json(args.output / "uncertainty_handoff.json", handoff)
    output_names = [
        "metric_distribution.csv", "metric_summary.csv", "training_validation_gaps.csv",
        "training_validation_gap_summary.csv", "gpp_gate_distribution.csv", "gpp_gate_summary.csv",
        "error_propagation_members.csv", "error_propagation_correlations.csv",
        "error_propagation_correlation_summary.csv", "depth_error_distribution.csv",
        "depth_error_summary.csv", "cn_member_errors.csv", "cn_log_covariance.csv",
        "cn_member_balanced.csv", "cn_member_balanced_summary.csv", "cn_member_balanced_covariance.csv",
        "error_propagation_member_balanced.csv", "error_propagation_member_balanced_summary.csv",
        "error_propagation_member_balanced_correlations.csv",
        "gpp_sr_correlations.csv", "gpp_sr_correlation_summary.csv", "error_propagation.png",
        "gpp_gate_comparison.png", "gpp_sr_joint.png", "gpp_sr_joint_grid_validation.json",
        "provenance.json", "uncertainty_handoff.json",
    ]
    output_hashes = {name: sha256_file(args.output / name) for name in output_names}
    report = {
        "schema": "three-stage-iter015-aggregate-report-v1",
        "result": "pass",
        "split_count": 20,
        "metric_distribution_rows": len(tables["metric_distribution.csv"]),
        "metric_summary_rows": metric_summary_rows,
        "training_validation_gap_rows": gap_rows,
        "training_validation_gap_summary_rows": gap_summary_rows,
        "gate_distribution_rows": len(tables["gpp_gate_distribution.csv"]),
        "gate_summary_rows": gate_summary_rows,
        "propagation_member_rows": len(tables["error_propagation_members.csv"]),
        "propagation_correlation_rows": propagation_rows,
        "propagation_summary_rows": propagation_summary_rows,
        "depth_distribution_rows": len(tables["depth_error_distribution.csv"]),
        "depth_summary_rows": depth_summary_rows,
        "cn_member_rows": cn_member_rows,
        "cn_covariance_rows": cn_covariance_rows,
        "cn_member_balanced_rows": balanced_counts[0],
        "cn_member_balanced_summary_rows": balanced_counts[1],
        "cn_member_balanced_covariance_rows": balanced_counts[2],
        "propagation_member_balanced_rows": balanced_counts[3],
        "propagation_member_balanced_summary_rows": balanced_counts[4],
        "propagation_member_balanced_correlation_rows": balanced_counts[5],
        "gpp_sr_correlation_rows": len(gpp_sr_rows),
        "spinup_diagnostic_warning_count": warning_count,
        "gpp_warning_count": 0,
        "sr_warning_count": 0,
        "diagnostic_figures": ["error_propagation.png", "gpp_gate_comparison.png", "gpp_sr_joint.png"],
        "joint_density_grid_shape": [200, 200],
        "joint_density_unit_mass_validated": True,
        "output_sha256": output_hashes,
        "performance_threshold_applied": False,
        "fixed_test_access": False,
        "all_development_fit": False,
        "release_modified": False,
    }
    write_json(args.output / "aggregate_report.json", report)
    print(
        "ITER015_AGGREGATE_OK splits=20 metrics=960 gate=120 propagation=6560 "
        "depth=640 figures=3 fixed_test=false",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
