#!/usr/bin/env python
"""Aggregate per-seed permutation importance into per-target and combined rankings."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import median
from typing import Any


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(float(value) for value in values)
    assert ordered
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize(values: list[float]) -> dict[str, float | int]:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    assert len(finite) == len(values)
    return {
        "count": len(finite),
        "median": median(finite),
        "min": min(finite),
        "max": max(finite),
        "p25": percentile(finite, 0.25),
        "p75": percentile(finite, 0.75),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats-dir", required=True, type=Path)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--permutation-repeats", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = sorted(args.stats_dir.glob("surrogate_spinup_stats_seed*.json"))
    assert len(files) == args.seed_count
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    targets = ("TOTSOMC", "TOTSOMN")
    by_target: dict[str, list[dict[str, Any]]] = {}

    for target in targets:
        features: dict[str, dict[str, list[float]]] = {}
        for data in payloads:
            variable = data["by_variable"][target]
            assert variable["permutation_repeats"] == args.permutation_repeats
            ranking = variable["permutation_importance_rmse"]
            for rank, item in enumerate(ranking, start=1):
                row = features.setdefault(item["feature"], {"ranks": [], "rmse": [], "r2": []})
                row["ranks"].append(float(rank))
                row["rmse"].append(float(item["mean_rmse_increase"]))
                row["r2"].append(float(item["mean_r2_drop"]))
        rows: list[dict[str, Any]] = []
        for feature, values in features.items():
            assert len(values["ranks"]) == args.seed_count
            rows.append(
                {
                    "feature": feature,
                    "median_seed_rank": median(values["ranks"]),
                    "rank_spread": {
                        "min": min(values["ranks"]),
                        "max": max(values["ranks"]),
                        "iqr": percentile(values["ranks"], 0.75)
                        - percentile(values["ranks"], 0.25),
                    },
                    "median_rmse_increase": median(values["rmse"]),
                    "rmse_increase": summarize(values["rmse"]),
                    "r2_drop": summarize(values["r2"]),
                }
            )
        rows.sort(
            key=lambda row: (
                row["median_seed_rank"],
                -row["median_rmse_increase"],
                row["feature"],
            )
        )
        by_target[target] = rows

    all_features = sorted(
        set().union(*(set(row["feature"] for row in rows) for rows in by_target.values()))
    )
    combined: list[dict[str, Any]] = []
    for feature in all_features:
        per_target = {
            target: next(row for row in by_target[target] if row["feature"] == feature)
            for target in targets
        }
        combined.append(
            {
                "feature": feature,
                "median_seed_rank": median(
                    [per_target[target]["median_seed_rank"] for target in targets]
                ),
                "median_rmse_increase": median(
                    [per_target[target]["median_rmse_increase"] for target in targets]
                ),
                "by_target": per_target,
            }
        )
    combined.sort(
        key=lambda row: (
            row["median_seed_rank"],
            -row["median_rmse_increase"],
            row["feature"],
        )
    )

    output = {
        "variant": args.variant,
        "seed_count": args.seed_count,
        "permutation_repeats": args.permutation_repeats,
        "ranking_rule": "median_seed_rank ascending, then median_rmse_increase descending",
        "by_target": by_target,
        "combined_cross_target": combined,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(args.output_json)


if __name__ == "__main__":
    main()
