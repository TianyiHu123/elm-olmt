#!/usr/bin/env python
"""Reusable aggregation of seed-stable feature and correlation diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


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


def _as_pair_key(feature_i: str, feature_j: str) -> Tuple[str, str]:
    a = str(feature_i)
    b = str(feature_j)
    return (a, b) if a <= b else (b, a)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--stats-dir", help="Directory containing seed stats JSON files")
    source.add_argument(
        "--compact-report",
        type=Path,
        help="Compact one existing full feature-stability report instead of reading seed stats",
    )
    parser.add_argument("--variant")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument(
        "--detail-level",
        choices=("compact", "full"),
        default="compact",
        help="Output schema when aggregating seed stats (default: compact)",
    )
    parser.add_argument(
        "--full-output-json",
        type=Path,
        help="Optional full-detail copy written before compact output",
    )
    return parser


def _json_bytes(value: Dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def _write_json(path: Path, value: Dict[str, Any]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _compact_output(
    full_output: Dict[str, Any],
    full_report_bytes: bytes,
    full_report_backup: Path | None,
) -> Dict[str, Any]:
    if "correlation_summary" not in full_output:
        raise ValueError("Full report lacks correlation_summary and cannot use compact-v1 schema")

    by_target: Dict[str, Any] = {}
    for target, target_output in full_output["by_target"].items():
        features = []
        for feature in target_output["features"]:
            features.append(
                {
                    "feature": feature["feature"],
                    "selected_frequency": feature["selected_frequency"],
                    "top_k_frequency": feature["top_k_frequency"],
                    "median_rank": feature["median_rank"],
                    "rank_iqr": feature["rank_iqr"],
                    "median_r2_drop": feature["mean_r2_drop"]["median"],
                    "median_rmse_increase": feature["mean_rmse_increase"]["median"],
                    "positive_r2_drop_fraction": feature["positive_r2_drop_fraction"],
                    "positive_rmse_increase_fraction": feature[
                        "positive_rmse_increase_fraction"
                    ],
                    "strong_candidate": feature["strong_candidate"],
                }
            )
        by_target[target] = {
            "metrics": target_output["metrics"],
            "features": features,
        }

    full_selection = full_output["feature_selection_summary"]
    feature_selection = {
        "selected_features": [
            {
                "feature": row["feature"],
                "count": row["selected_count"],
                "frequency": row["selected_frequency"],
            }
            for row in full_selection["selected_features"]
        ],
        "requested_explicit_subset_features": [
            {
                "feature": row["feature"],
                "count": row["requested_count"],
                "frequency": row["requested_frequency"],
            }
            for row in full_selection["requested_explicit_subset_features"]
        ],
    }

    full_correlation = full_output["correlation_summary"]
    thresholded_pairs = {}
    for threshold, rows in full_correlation["thresholded_pair_frequency"].items():
        thresholded_pairs[threshold] = [
            {
                "feature_i": row["feature_i"],
                "feature_j": row["feature_j"],
                "seed_count": row["seed_count_meeting_threshold"],
                "seed_frequency": row["seed_frequency_meeting_threshold"],
                "median_abs_corr": row["abs_corr_summary"]["median"],
            }
            for row in rows
        ]

    compact = {
        "schema_version": "spinup-feature-stability-compact-v1",
        "variant": full_output["variant"],
        "stats_dir": full_output["stats_dir"],
        "file_count": full_output["file_count"],
        "seeds": full_output["seeds"],
        "top_k": full_output["top_k"],
        "corr_thresholds_reported": full_output["corr_thresholds_reported"],
        "full_report": {
            "sha256": hashlib.sha256(full_report_bytes).hexdigest(),
            "size_bytes": len(full_report_bytes),
            "backup_path": (
                str(full_report_backup.expanduser().resolve())
                if full_report_backup is not None
                else None
            ),
        },
        "by_target": by_target,
        "feature_selection_summary": feature_selection,
        "correlation_summary": {
            "thresholded_pair_frequency": thresholded_pairs,
            "surviving_representatives": full_correlation["surviving_representatives"],
        },
        "cross_target_strong_top_k_features": [
            row["feature"]
            for row in full_output["cross_target_agreement"]
            if row["target_agreement_strong_top_k"]
        ],
    }
    return compact


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    output_path = Path(args.output_json).expanduser().resolve()

    if args.compact_report is not None:
        if args.variant is not None:
            parser.error("--variant cannot be used with --compact-report")
        if args.detail_level != "compact":
            parser.error("--compact-report requires --detail-level compact")
        if args.full_output_json is not None:
            parser.error("--full-output-json cannot be used with --compact-report")
        full_path = args.compact_report.expanduser().resolve()
        full_bytes = full_path.read_bytes()
        full_output = json.loads(full_bytes)
        _write_json(
            output_path,
            _compact_output(full_output, full_bytes, full_path),
        )
        print(f"Wrote compact feature stability summary: {output_path}")
        return 0

    if args.variant is None:
        parser.error("--variant is required with --stats-dir")
    stats_dir = Path(args.stats_dir).expanduser().resolve()
    files = sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json"))
    if not files:
        raise FileNotFoundError(f"No stats files found under {stats_dir}")

    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    seeds = [_extract_seed(path) for path in files]
    thresholds = [0.80, 0.90, 0.95, 0.98]
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
        "corr_thresholds_reported": thresholds,
        "by_target": {},
    }

    feature_selection_counts: Dict[str, int] = {}
    requested_subset_counts: Dict[str, int] = {}
    excluded_subset_counts: Dict[str, int] = {}
    representative_counts: Dict[str, Dict[str, Any]] = {}
    pair_abs_corr_values: Dict[Tuple[str, str], List[float]] = {}
    pair_threshold_counts: Dict[str, Dict[Tuple[str, str], int]] = {
        f"{thr:.2f}": {} for thr in thresholds
    }

    top_k_by_target: Dict[str, Dict[str, int]] = {}

    for payload in payloads:
        feature_diag = payload.get("feature_diagnostics", {})
        selected_features = [str(name) for name in feature_diag.get("selected_feature_names", [])]
        for feature in selected_features:
            feature_selection_counts[feature] = feature_selection_counts.get(feature, 0) + 1

        requested_subset = [
            str(name)
            for name in feature_diag.get("explicit_feature_subset_requested", [])
        ]
        for feature in requested_subset:
            requested_subset_counts[feature] = requested_subset_counts.get(feature, 0) + 1

        excluded_subset = [
            str(name)
            for name in feature_diag.get("excluded_by_explicit_subset", [])
        ]
        for feature in excluded_subset:
            excluded_subset_counts[feature] = excluded_subset_counts.get(feature, 0) + 1

        dropped_reps = feature_diag.get("dropped_by_correlation_pairs", [])
        for record in dropped_reps:
            representative = record.get("representative_feature")
            dropped = str(record.get("dropped_feature", ""))
            if not representative or not dropped:
                continue
            key = str(representative)
            entry = representative_counts.setdefault(
                key,
                {
                    "representative_feature": key,
                    "drop_count": 0,
                    "dropped_features": {},
                },
            )
            entry["drop_count"] += 1
            entry["dropped_features"][dropped] = entry["dropped_features"].get(dropped, 0) + 1

        pair_records = feature_diag.get("full_corr_pairs_pre_prune", [])
        for pair in pair_records:
            pair_key = _as_pair_key(pair.get("feature_i", ""), pair.get("feature_j", ""))
            corr_abs = abs(float(pair.get("corr", 0.0)))
            pair_abs_corr_values.setdefault(pair_key, []).append(corr_abs)
            for thr in thresholds:
                if corr_abs >= thr:
                    bucket = pair_threshold_counts[f"{thr:.2f}"]
                    bucket[pair_key] = bucket.get(pair_key, 0) + 1

    selection_rows = []
    for feature, count in feature_selection_counts.items():
        selection_rows.append(
            {
                "feature": feature,
                "selected_count": count,
                "selected_frequency": count / len(files),
                "requested_count": requested_subset_counts.get(feature, 0),
                "requested_frequency": requested_subset_counts.get(feature, 0) / len(files),
                "excluded_by_explicit_subset_count": excluded_subset_counts.get(feature, 0),
                "excluded_by_explicit_subset_frequency": excluded_subset_counts.get(feature, 0) / len(files),
            }
        )
    selection_rows.sort(
        key=lambda item: (-float(item["selected_frequency"]), item["feature"])
    )

    pairwise_rows = []
    for (feature_i, feature_j), abs_corr_values in pair_abs_corr_values.items():
        pairwise_rows.append(
            {
                "feature_i": feature_i,
                "feature_j": feature_j,
                "pair": f"{feature_i}|{feature_j}",
                "abs_corr_summary": _metric_summary(abs_corr_values),
            }
        )
    pairwise_rows.sort(
        key=lambda item: (
            -(item["abs_corr_summary"]["median"] or float("-inf")),
            item["pair"],
        )
    )

    threshold_rows: Dict[str, List[Dict[str, Any]]] = {}
    for key, counts in pair_threshold_counts.items():
        rows: List[Dict[str, Any]] = []
        for (feature_i, feature_j), count in counts.items():
            abs_corr_values = pair_abs_corr_values.get((feature_i, feature_j), [])
            rows.append(
                {
                    "feature_i": feature_i,
                    "feature_j": feature_j,
                    "pair": f"{feature_i}|{feature_j}",
                    "seed_count_meeting_threshold": count,
                    "seed_frequency_meeting_threshold": count / len(files),
                    "abs_corr_summary": _metric_summary(abs_corr_values),
                }
            )
        rows.sort(
            key=lambda item: (
                -int(item["seed_count_meeting_threshold"]),
                -(item["abs_corr_summary"]["median"] or float("-inf")),
                item["pair"],
            )
        )
        threshold_rows[key] = rows

    representative_rows = []
    for representative, record in representative_counts.items():
        representative_rows.append(
            {
                "representative_feature": representative,
                "drop_count": int(record["drop_count"]),
                "drop_frequency": float(record["drop_count"] / len(files)),
                "dropped_features": [
                    {
                        "feature": feature,
                        "count": count,
                        "frequency": count / len(files),
                    }
                    for feature, count in sorted(
                        record["dropped_features"].items(),
                        key=lambda item: (-int(item[1]), item[0]),
                    )
                ],
            }
        )
    representative_rows.sort(
        key=lambda item: (-int(item["drop_count"]), item["representative_feature"])
    )

    for target in targets:
        feature_records: Dict[str, Dict[str, Any]] = {}
        r2_values: List[float] = []
        gap_values: List[float] = []
        rmse_ratio_values: List[float] = []
        warning_count = 0
        top_k_by_target[target] = {}

        for payload in payloads:
            by_variable = payload.get("by_variable", {}).get(target, {})
            r2_values.append(float(by_variable.get("r2_val", float("nan"))))
            gap_values.append(float(by_variable.get("r2_gap", float("nan"))))
            rmse_ratio_values.append(float(by_variable.get("rmse_ratio", float("nan"))))
            warning_count += int(bool(by_variable.get("overfit_warning", False)))

            selected = set(payload.get("feature_diagnostics", {}).get("selected_feature_names", []))
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
            top_k_frequency = record["top_k_count"] / len(files)
            top_k_by_target[target][feature] = int(record["top_k_count"])
            features.append(
                {
                    "feature": feature,
                    "selected_frequency": record["selected_count"] / len(files),
                    "top_k_frequency": top_k_frequency,
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

    cross_target_rows: List[Dict[str, Any]] = []
    if len(top_k_by_target) >= 2:
        target_names = sorted(top_k_by_target.keys())
        all_features = set()
        for target in target_names:
            all_features.update(top_k_by_target[target].keys())
        for feature in sorted(all_features):
            row: Dict[str, Any] = {"feature": feature}
            strong_all = True
            for target in target_names:
                count = int(top_k_by_target[target].get(feature, 0))
                freq = float(count / len(files))
                row[f"{target}_top_k_count"] = count
                row[f"{target}_top_k_frequency"] = freq
                strong_all = strong_all and (count >= 3)
            row["target_agreement_strong_top_k"] = strong_all
            cross_target_rows.append(row)
        cross_target_rows.sort(
            key=lambda item: (
                -int(item["target_agreement_strong_top_k"]),
                -sum(
                    float(item[f"{target}_top_k_frequency"])
                    for target in sorted(top_k_by_target.keys())
                ),
                item["feature"],
            )
        )

    output["feature_selection_summary"] = {
        "selected_features": selection_rows,
        "requested_explicit_subset_features": [
            {
                "feature": feature,
                "requested_count": count,
                "requested_frequency": count / len(files),
            }
            for feature, count in sorted(
                requested_subset_counts.items(),
                key=lambda item: (-int(item[1]), item[0]),
            )
        ],
    }
    output["correlation_summary"] = {
        "pairwise_abs_corr_summary": pairwise_rows,
        "thresholded_pair_frequency": threshold_rows,
        "surviving_representatives": representative_rows,
    }
    output["cross_target_agreement"] = cross_target_rows

    full_bytes = _json_bytes(output)
    full_output_path = None
    if args.full_output_json is not None:
        full_output_path = args.full_output_json.expanduser().resolve()
        if full_output_path == output_path:
            parser.error("--full-output-json must differ from --output-json")
        full_output_path.parent.mkdir(parents=True, exist_ok=True)
        full_output_path.write_bytes(full_bytes)

    if args.detail_level == "compact":
        output = _compact_output(output, full_bytes, full_output_path)
    _write_json(output_path, output)
    print(f"Wrote feature stability summary: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
