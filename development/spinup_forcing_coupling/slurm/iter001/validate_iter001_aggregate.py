#!/usr/bin/env python
"""Independent structural validator for Iter001 aggregate outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List

REPOSITORY_COMMIT = "2648998d4ceb08ecf72859a7d5200c0e3a5eb41d"
EXPECTED_ARTIFACTS = [
    "seed_metrics.csv",
    "metric_summary.csv",
    "seed_feature_importance.csv",
    "feature_importance_summary.csv",
    "metric_distributions.png",
    "feature_importance.png",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_sha256(names: List[str]) -> str:
    encoded = json.dumps(names, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_aggregate(
    output_dir: Path,
    *,
    source_manifest: Path,
    dependency_manifest: Path,
    production_config: Path,
) -> Dict[str, Any]:
    aggregate_path = output_dir / "iter001_aggregate.json"
    payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
    if payload.get("schema") != "spinup-forcing-coupling-iter001-aggregate-v1":
        raise ValueError("Unexpected aggregate schema")
    if payload.get("repository_commit") != REPOSITORY_COMMIT:
        raise ValueError("Aggregate repository commit mismatch")
    if payload.get("eligible_seed_count") != 100 or payload.get("seeds") != list(
        range(10001, 10101)
    ):
        raise ValueError("Aggregate eligible seed set mismatch")
    if payload.get("target") != "SR":
        raise ValueError("Aggregate target mismatch")
    ordered = [str(name) for name in payload["ordered_feature_names"]]
    if not ordered or len(set(ordered)) != len(ordered):
        raise ValueError("Aggregate ordered schema is empty or duplicated")
    if payload["ordered_feature_schema_sha256"] != schema_sha256(ordered):
        raise ValueError("Aggregate ordered schema hash mismatch")
    expected_hashes = {
        "source_manifest_sha256": sha256(source_manifest),
        "dependency_manifest_sha256": sha256(dependency_manifest),
        "production_config_sha256": sha256(production_config),
    }
    for key, expected in expected_hashes.items():
        if payload.get(key) != expected:
            raise ValueError(f"Aggregate provenance mismatch for {key}")
    finite(payload["pooled_overfitting_warning_fraction"], "warning_fraction")
    if not 0.0 <= float(payload["pooled_overfitting_warning_fraction"]) <= 1.0:
        raise ValueError("Aggregate warning fraction is outside [0, 1]")
    for metric, stats in payload["metric_distributions"].items():
        for key in ("mean", "std", "min", "q25", "median", "q75", "max"):
            finite(stats[key], f"metric_distributions.{metric}.{key}")
    features = payload["feature_importance"]
    if len(features) != len(ordered) or {row["feature"] for row in features} != set(ordered):
        raise ValueError("Aggregate feature-importance schema mismatch")
    for row in features:
        for key in (
            "test_rmse_increase_mean",
            "test_rmse_increase_median",
            "test_r2_decrease_mean",
            "test_r2_decrease_median",
            "median_rank",
            "top10_frequency",
            "positive_importance_frequency",
        ):
            finite(row[key], f"feature_importance.{row['feature']}.{key}")
        for key in ("top10_frequency", "positive_importance_frequency"):
            if not 0.0 <= float(row[key]) <= 1.0:
                raise ValueError(f"{row['feature']} {key} is outside [0, 1]")
    if payload.get("artifacts") != EXPECTED_ARTIFACTS:
        raise ValueError("Aggregate artifact list mismatch")
    for name in EXPECTED_ARTIFACTS:
        path = output_dir / name
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"Missing or empty aggregate artifact: {path}")
        if path.suffix == ".png" and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Invalid PNG signature: {path}")
    seed_metrics = csv_rows(output_dir / "seed_metrics.csv")
    metric_summary = csv_rows(output_dir / "metric_summary.csv")
    seed_importance = csv_rows(output_dir / "seed_feature_importance.csv")
    feature_summary = csv_rows(output_dir / "feature_importance_summary.csv")
    if len(seed_metrics) != 1000:
        raise ValueError(f"Expected 1000 pooled/per-site metric rows, found {len(seed_metrics)}")
    if len(metric_summary) != 60:
        raise ValueError(f"Expected 60 metric-summary rows, found {len(metric_summary)}")
    if len(seed_importance) != 100 * len(ordered):
        raise ValueError("Per-seed importance row count mismatch")
    if len(feature_summary) != len(ordered):
        raise ValueError("Feature-summary row count mismatch")
    if {int(row["seed"]) for row in seed_metrics} != set(range(10001, 10101)):
        raise ValueError("Metric CSV seed set mismatch")
    if {int(row["seed"]) for row in seed_importance} != set(range(10001, 10101)):
        raise ValueError("Importance CSV seed set mismatch")
    return {
        "schema": "spinup-forcing-coupling-iter001-aggregate-validation-v1",
        "gate": "pass",
        "aggregate_path": str(aggregate_path),
        "aggregate_sha256": sha256(aggregate_path),
        "ordered_feature_schema_sha256": payload["ordered_feature_schema_sha256"],
        "artifact_sha256": {name: sha256(output_dir / name) for name in EXPECTED_ARTIFACTS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--dependency-manifest", type=Path, required=True)
    parser.add_argument("--production-config", type=Path, required=True)
    args = parser.parse_args()
    report = validate_aggregate(
        args.output_dir,
        source_manifest=args.source_manifest,
        dependency_manifest=args.dependency_manifest,
        production_config=args.production_config,
    )
    output = args.output_dir / "iter001_aggregate_validation.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(f"AGGREGATE_VALIDATION_PASS output={output} sha256={sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
