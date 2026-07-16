#!/usr/bin/env python
"""Aggregate seed-stable feature diagnostics from spinup stats JSON files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _percentile(values: List[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def _extract_seed(path: Path) -> int | None:
    match = re.search(r"seed(\d+)", path.name)
    return int(match.group(1)) if match else None


def _metric_summary(values: Iterable[float]) -> Dict[str, float | int | None]:
    finite = [float(value) for value in values if value == value]
    if not finite:
        return {
            "count": 0,
            "median": None,
            "p25": None,
            "p75": None,
            "min": None,
            "max": None,
        }
    return {
        "count": len(finite),
        "median": _percentile(finite, 0.5),
        "p25": _percentile(finite, 0.25),
        "p75": _percentile(finite, 0.75),
        "min": float(min(finite)),
        "max": float(max(finite)),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats-dir", required=True, help="Directory containing seed stats JSON files")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--top-k", type=int, default=10)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    stats_dir = Path(args.stats_dir).expanduser().resolve()
    files = sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json"))
    if not files:
        raise FileNotFoundError(f"No stats files found under {stats_dir}")

    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    seeds = [_extract_seed(path) for path in files]
    targets = sorted(
        {
            variable
            for payload in payloads
            for variable in payload.get("by_variable", {})
        }
    )
    output: Dict[str, Any] = {
        "variant": args.variant,
        "stats_dir": str(stats_dir),
        "file_count": len(files),
        "seeds": [seed for seed in seeds if seed is not None],
        "top_k": int(args.top_k),
        "by_target": {},
    }

    for target in targets:
        feature_records: Dict[str, Dict[str, Any]] = {}
        r2_values: List[float] = []
        gap_values: List[float] = []
        rmse_ratio_values: List[float] = []
        warning_count = 0

        for payload in payloads:
            by_variable = payload.get("by_variable", {}).get(target, {})
            r2_values.append(float(by_variable.get("r2_val", float("nan"))))
            gap_values.append(float(by_variable.get("r2_gap", float("nan"))))
            rmse_ratio_values.append(float(by_variable.get("rmse_ratio", float("nan"))))
            warning_count += int(bool(by_variable.get("overfit_warning", False)))

            selected = set(
                payload.get("feature_diagnostics", {}).get("selected_feature_names", [])
            )
            ranked = by_variable.get("permutation_importance_rmse", [])
            ranked_names = {
                str(record.get("feature")): rank
                for rank, record in enumerate(ranked, start=1)
            }
            for feature in selected | set(ranked_names):
                record = feature_records.setdefault(
                    feature,
                    {
                        "selected_count": 0,
                        "top_k_count": 0,
                        "ranks": [],
                        "mean_r2_drop": [],
                        "mean_rmse_increase": [],
                    },
                )
                if feature in selected:
                    record["selected_count"] += 1
                rank = ranked_names.get(feature)
                if rank is not None:
                    record["ranks"].append(rank)
                    if rank <= int(args.top_k):
                        record["top_k_count"] += 1
                    importance = next(
                        item for item in ranked if str(item.get("feature")) == feature
                    )
                    record["mean_r2_drop"].append(float(importance.get("mean_r2_drop", float("nan"))))
                    record["mean_rmse_increase"].append(
                        float(importance.get("mean_rmse_increase", float("nan")))
                    )

        features: List[Dict[str, Any]] = []
        for feature, record in feature_records.items():
            ranks = [float(value) for value in record["ranks"]]
            r2_drops = [float(value) for value in record["mean_r2_drop"]]
            rmse_increases = [float(value) for value in record["mean_rmse_increase"]]
            features.append(
                {
                    "feature": feature,
                    "selected_frequency": record["selected_count"] / len(files),
                    "top_k_frequency": record["top_k_count"] / len(files),
                    "median_rank": _percentile(ranks, 0.5),
                    "rank_iqr": (
                        (_percentile(ranks, 0.75) or 0.0)
                        - (_percentile(ranks, 0.25) or 0.0)
                    )
                    if ranks
                    else None,
                    "mean_r2_drop": _metric_summary(r2_drops),
                    "mean_rmse_increase": _metric_summary(rmse_increases),
                    "positive_r2_drop_fraction": (
                        sum(value > 0.0 for value in r2_drops) / len(r2_drops)
                        if r2_drops
                        else None
                    ),
                    "positive_rmse_increase_fraction": (
                        sum(value > 0.0 for value in rmse_increases) / len(rmse_increases)
                        if rmse_increases
                        else None
                    ),
                    "strong_candidate": (
                        record["selected_count"] >= 4
                        and record["top_k_count"] >= 3
                    ),
                }
            )
        features.sort(
            key=lambda item: (
                -float(item["top_k_frequency"]),
                -float(item["selected_frequency"]),
                -(item["mean_r2_drop"]["median"] or float("-inf")),
            )
        )
        output["by_target"][target] = {
            "metrics": {
                "r2_val": _metric_summary(r2_values),
                "r2_gap": _metric_summary(gap_values),
                "rmse_ratio": _metric_summary(rmse_ratio_values),
                "overfit_warning_fraction": warning_count / len(files),
            },
            "features": features,
        }

    output_path = Path(args.output_json).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote feature stability summary: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
