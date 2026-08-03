#!/usr/bin/env python
"""Validate and aggregate the 100 Iter001 forcing-surrogate production records."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]
SEEDS = list(range(10001, 10101))
METRICS = ["r2_train", "r2_test", "rmse_train", "rmse_test", "r2_gap", "rmse_ratio"]
REPOSITORY_COMMIT = "2648998d4ceb08ecf72859a7d5200c0e3a5eb41d"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_sha256(names: Sequence[str]) -> str:
    encoded = json.dumps(list(names), ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def validate_diagnostics(value: Mapping[str, Any], label: str) -> None:
    for population in ("train", "test"):
        metrics = value[population]
        finite_number(metrics["r2"], f"{label}.{population}.r2")
        finite_number(metrics["rmse"], f"{label}.{population}.rmse")
        if int(metrics["n_rows"]) <= 0:
            raise ValueError(f"{label}.{population}.n_rows must be positive")
    finite_number(value["r2_gap"], f"{label}.r2_gap")
    finite_number(value["rmse_ratio"], f"{label}.rmse_ratio")
    if not isinstance(value["overfitting_warning"], bool):
        raise ValueError(f"{label}.overfitting_warning must be boolean")


def validate_record(
    payload: Mapping[str, Any],
    *,
    source_sha: str,
    dependency_sha: str,
    config_sha: str,
) -> Tuple[int, List[str]]:
    if payload.get("schema") != "olmt-forcing-surrogate-stats-v2":
        raise ValueError("Unexpected stats schema")
    seed = int(payload["split_random_state"])
    if seed not in SEEDS:
        raise ValueError(f"Seed outside Iter001 range: {seed}")
    if payload["split_mode"] != "random_time_window" or payload["train_fraction"] != 0.8:
        raise ValueError(f"Seed {seed} split contract mismatch")
    if payload["output_label"] != "spinup_forcing_coupling_iter001_baseline":
        raise ValueError(f"Seed {seed} output label mismatch")
    if payload["case_names"] != CASES or payload["outvars"] != ["SR"]:
        raise ValueError(f"Seed {seed} cases/target mismatch")
    provenance = payload["provenance"]
    expected_provenance = {
        "source_manifest_sha256": source_sha,
        "dependency_manifest_sha256": dependency_sha,
        "submission_config_sha256": config_sha,
    }
    for key, expected in expected_provenance.items():
        if provenance.get(key) != expected:
            raise ValueError(f"Seed {seed} provenance mismatch for {key}")
    if provenance.get("repository_commit") != REPOSITORY_COMMIT:
        raise ValueError(f"Seed {seed} repository commit mismatch")
    ordered = [str(name) for name in payload["ordered_feature_names"]]
    if not ordered or len(set(ordered)) != len(ordered):
        raise ValueError(f"Seed {seed} ordered feature schema is empty or duplicated")
    if payload["ordered_feature_schema_sha256"] != schema_sha256(ordered):
        raise ValueError(f"Seed {seed} ordered feature schema hash mismatch")
    stats = payload["by_variable"]["SR"]
    validate_diagnostics(stats["pooled"], f"seed{seed}.pooled")
    if list(stats["by_site"]) != CASES:
        raise ValueError(f"Seed {seed} per-site case order mismatch")
    for case in CASES:
        validate_diagnostics(stats["by_site"][case], f"seed{seed}.{case}")
    importance = stats["permutation_importance"]
    if importance["n_repeats"] != 8 or importance["random_state"] != seed:
        raise ValueError(f"Seed {seed} permutation configuration mismatch")
    features = importance["features"]
    if importance["feature_count"] != len(ordered) or [row["feature"] for row in features] != ordered:
        raise ValueError(f"Seed {seed} importance/schema mismatch")
    for row in features:
        for metric in ("test_r2_decrease", "test_rmse_increase"):
            values = row[metric]
            if len(values) != 8:
                raise ValueError(f"Seed {seed} {row['feature']} {metric} repeat count mismatch")
            for index, value in enumerate(values):
                finite_number(value, f"seed{seed}.{row['feature']}.{metric}[{index}]")
    return seed, ordered


def distribution(values: Sequence[float]) -> Dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "std": float(np.std(array)),
        "min": float(np.min(array)),
        "q25": float(np.quantile(array, 0.25)),
        "median": float(np.median(array)),
        "q75": float(np.quantile(array, 0.75)),
        "max": float(np.max(array)),
    }


def validate_seed_set(seeds: Sequence[int]) -> None:
    if len(seeds) != 100 or sorted(seeds) != SEEDS:
        raise ValueError("Production seed set must contain each seed 10001-10100 exactly once")


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--dependency-manifest", type=Path, required=True)
    parser.add_argument("--production-config", type=Path, required=True)
    args = parser.parse_args()
    source_sha = sha256(args.source_manifest)
    dependency_sha = sha256(args.dependency_manifest)
    config_sha = sha256(args.production_config)
    files = sorted(args.input_dir.glob("surrogate_forcing_stats_*.json"))
    if len(files) != 100:
        raise ValueError(f"Expected exactly 100 production records, found {len(files)}")
    records: Dict[int, Mapping[str, Any]] = {}
    ordered_schema: List[str] = []
    schema_hash = ""
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        seed, ordered = validate_record(
            payload, source_sha=source_sha, dependency_sha=dependency_sha, config_sha=config_sha
        )
        if seed in records:
            raise ValueError(f"Duplicate production seed {seed}")
        if not ordered_schema:
            ordered_schema = ordered
            schema_hash = str(payload["ordered_feature_schema_sha256"])
        elif ordered != ordered_schema or payload["ordered_feature_schema_sha256"] != schema_hash:
            raise ValueError(f"Seed {seed} ordered schema differs from the reference")
        records[seed] = payload
    validate_seed_set(list(records))

    metric_rows: List[Dict[str, Any]] = []
    warning_count = 0
    importance_rows: List[Dict[str, Any]] = []
    ranks_by_feature: Dict[str, List[int]] = {name: [] for name in ordered_schema}
    top10_counts: Counter[str] = Counter()
    positive_counts: Counter[str] = Counter()
    for seed in SEEDS:
        stats = records[seed]["by_variable"]["SR"]
        scopes = [("pooled", stats["pooled"])] + [
            (case, stats["by_site"][case]) for case in CASES
        ]
        for scope, diag in scopes:
            metric_rows.append(
                {
                    "seed": seed,
                    "scope": scope,
                    "r2_train": diag["train"]["r2"],
                    "r2_test": diag["test"]["r2"],
                    "rmse_train": diag["train"]["rmse"],
                    "rmse_test": diag["test"]["rmse"],
                    "r2_gap": diag["r2_gap"],
                    "rmse_ratio": diag["rmse_ratio"],
                    "overfitting_warning": diag["overfitting_warning"],
                }
            )
        warning_count += int(stats["pooled"]["overfitting_warning"])
        feature_values = stats["permutation_importance"]["features"]
        rmse_means = np.asarray([row["test_rmse_increase_mean"] for row in feature_values])
        order = np.argsort(-rmse_means, kind="stable")
        ranks = np.empty(len(order), dtype=int)
        ranks[order] = np.arange(1, len(order) + 1)
        for index, row in enumerate(feature_values):
            feature = str(row["feature"])
            rank = int(ranks[index])
            ranks_by_feature[feature].append(rank)
            top10_counts[feature] += int(rank <= 10)
            positive_counts[feature] += int(float(row["test_rmse_increase_mean"]) > 0.0)
            importance_rows.append(
                {
                    "seed": seed,
                    "feature": feature,
                    "test_rmse_increase_mean": row["test_rmse_increase_mean"],
                    "test_r2_decrease_mean": row["test_r2_decrease_mean"],
                    "rmse_rank": rank,
                }
            )

    summary_rows: List[Dict[str, Any]] = []
    for scope in ["pooled", *CASES]:
        rows = [row for row in metric_rows if row["scope"] == scope]
        for metric in METRICS:
            summary_rows.append({"scope": scope, "metric": metric, **distribution([row[metric] for row in rows])})
    importance_summary: List[Dict[str, Any]] = []
    for feature in ordered_schema:
        rows = [row for row in importance_rows if row["feature"] == feature]
        rmse = [float(row["test_rmse_increase_mean"]) for row in rows]
        r2 = [float(row["test_r2_decrease_mean"]) for row in rows]
        importance_summary.append(
            {
                "feature": feature,
                "test_rmse_increase_mean": float(np.mean(rmse)),
                "test_rmse_increase_median": float(np.median(rmse)),
                "test_r2_decrease_mean": float(np.mean(r2)),
                "test_r2_decrease_median": float(np.median(r2)),
                "median_rank": float(np.median(ranks_by_feature[feature])),
                "top10_frequency": top10_counts[feature] / 100.0,
                "positive_importance_frequency": positive_counts[feature] / 100.0,
            }
        )
    importance_summary.sort(key=lambda row: (-row["test_rmse_increase_mean"], row["feature"]))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "seed_metrics.csv", list(metric_rows[0]), metric_rows)
    write_csv(args.output_dir / "metric_summary.csv", list(summary_rows[0]), summary_rows)
    write_csv(args.output_dir / "seed_feature_importance.csv", list(importance_rows[0]), importance_rows)
    write_csv(
        args.output_dir / "feature_importance_summary.csv",
        list(importance_summary[0]),
        importance_summary,
    )
    pooled_rows = [row for row in metric_rows if row["scope"] == "pooled"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for axis, metric in zip(axes.ravel(), ["r2_test", "rmse_test", "r2_gap", "rmse_ratio"]):
        axis.hist([row[metric] for row in pooled_rows], bins=15)
        axis.set_title(metric)
        axis.set_ylabel("seed count")
    fig.tight_layout()
    fig.savefig(args.output_dir / "metric_distributions.png", dpi=150)
    plt.close(fig)
    top = importance_summary[: min(20, len(importance_summary))]
    fig, axis = plt.subplots(figsize=(10, 8))
    axis.barh([row["feature"] for row in reversed(top)], [row["test_rmse_increase_mean"] for row in reversed(top)])
    axis.set_xlabel("Mean held-out RMSE increase")
    axis.set_title("Iter001 forcing-surrogate feature importance")
    fig.tight_layout()
    fig.savefig(args.output_dir / "feature_importance.png", dpi=150)
    plt.close(fig)
    aggregate = {
        "schema": "spinup-forcing-coupling-iter001-aggregate-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "eligible_seed_count": 100,
        "seeds": SEEDS,
        "case_order": CASES,
        "target": "SR",
        "repository_commit": REPOSITORY_COMMIT,
        "ordered_feature_names": ordered_schema,
        "ordered_feature_schema_sha256": schema_hash,
        "source_manifest_sha256": source_sha,
        "dependency_manifest_sha256": dependency_sha,
        "production_config_sha256": config_sha,
        "pooled_overfitting_warning_count": warning_count,
        "pooled_overfitting_warning_fraction": warning_count / 100.0,
        "metric_distributions": {
            row["metric"]: {key: row[key] for key in ("mean", "std", "min", "q25", "median", "q75", "max")}
            for row in summary_rows
            if row["scope"] == "pooled"
        },
        "feature_importance": importance_summary,
        "artifacts": [
            "seed_metrics.csv",
            "metric_summary.csv",
            "seed_feature_importance.csv",
            "feature_importance_summary.csv",
            "metric_distributions.png",
            "feature_importance.png",
        ],
    }
    output_json = args.output_dir / "iter001_aggregate.json"
    output_json.write_text(json.dumps(aggregate, indent=2, allow_nan=False), encoding="utf-8")
    print(
        f"AGGREGATION_PASS seeds=100 warning_fraction={warning_count / 100.0:.6f} "
        f"output={output_json} sha256={sha256(output_json)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
