#!/usr/bin/env python
"""Deterministic Iter007 screening and final selection aggregation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter007.iter007_common import (
    FINALIST_SPLITS,
    RESOLUTIONS,
    SCREEN_SPLITS,
    candidate_by_id,
    leaf_directory,
    load_candidates,
    read_csv,
    read_json,
    write_csv,
)
from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_gpp import write_json


def _parameter_count(candidate: Mapping[str, Any]) -> int:
    sizes = [43, *[int(value) for value in candidate["hidden_layer_sizes"]], 1]
    return sum((left + 1) * right for left, right in zip(sizes[:-1], sizes[1:]))


def _thresholds(config: Mapping[str, Any], resolution: str) -> tuple[float, float, float]:
    gate = config["gate"][resolution]
    return float(gate["r2_q10_floor"]), float(gate["rmse_q90_ceiling"]), float(gate["median_absolute_bias_ceiling"])


def _split_composites(rows: Sequence[Mapping[str, Any]], config: Mapping[str, Any]) -> dict[int, float]:
    result = {}
    split_ids = sorted({int(row["split_id"]) for row in rows})
    for split_id in split_ids:
        margins = []
        for resolution in RESOLUTIONS:
            matches = [
                row
                for row in rows
                if int(row["split_id"]) == split_id
                and row["partition"] == "validation"
                and row["resolution"] == resolution
            ]
            require(len(matches) == 1, "split composite metric coverage mismatch")
            row = matches[0]
            r2_floor, rmse_ceiling, bias_ceiling = _thresholds(config, resolution)
            margins.extend(
                (
                    (float(row["r2"]) - r2_floor) / r2_floor,
                    (rmse_ceiling - float(row["rmse"])) / rmse_ceiling,
                    (bias_ceiling - abs(float(row["bias"]))) / bias_ceiling,
                )
            )
        result[split_id] = float(np.mean(margins))
    return result


def candidate_statistics(
    candidate: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    baseline_rows: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    validation = [row for row in rows if row["partition"] == "validation"]
    split_ids = sorted({int(row["split_id"]) for row in validation})
    require(len(validation) == len(split_ids) * len(RESOLUTIONS), "candidate validation row coverage mismatch")
    components = {}
    margins = []
    for resolution in RESOLUTIONS:
        selected = [row for row in validation if row["resolution"] == resolution]
        require(len(selected) == len(split_ids), "candidate resolution coverage mismatch")
        r2 = np.asarray([float(row["r2"]) for row in selected], dtype=np.float64)
        rmse = np.asarray([float(row["rmse"]) for row in selected], dtype=np.float64)
        bias = np.asarray([float(row["bias"]) for row in selected], dtype=np.float64)
        r2_q10 = float(np.quantile(r2, 0.10, method="linear"))
        rmse_q90 = float(np.quantile(rmse, 0.90, method="linear"))
        median_absolute_bias = float(np.median(np.abs(bias)))
        r2_floor, rmse_ceiling, bias_ceiling = _thresholds(config, resolution)
        component_margins = {
            "r2": (r2_q10 - r2_floor) / r2_floor,
            "rmse": (rmse_ceiling - rmse_q90) / rmse_ceiling,
            "bias": (bias_ceiling - median_absolute_bias) / bias_ceiling,
        }
        margins.extend(component_margins.values())
        components[resolution] = {
            "r2_q10": r2_q10,
            "r2_floor": r2_floor,
            "rmse_q90": rmse_q90,
            "rmse_ceiling": rmse_ceiling,
            "median_absolute_bias": median_absolute_bias,
            "bias_ceiling": bias_ceiling,
            "margins": component_margins,
            "pass": all(value >= 0.0 for value in component_margins.values()),
        }
    candidate_composite = _split_composites(validation, config)
    baseline_composite = _split_composites(baseline_rows, config)
    require(set(candidate_composite) == set(baseline_composite), "paired baseline split mismatch")
    paired = np.asarray(
        [candidate_composite[split_id] - baseline_composite[split_id] for split_id in sorted(candidate_composite)],
        dtype=np.float64,
    )
    composite_values = np.asarray(list(candidate_composite.values()), dtype=np.float64)
    gate_pass = all(value >= 0.0 for value in margins)
    return {
        "candidate_id": int(candidate["candidate_id"]),
        "candidate": dict(candidate),
        "split_count": len(split_ids),
        "split_ids": split_ids,
        "gate_pass": bool(gate_pass),
        "worst_normalized_margin": float(np.min(margins)),
        "mean_normalized_margin": float(np.mean(margins)),
        "median_paired_composite_improvement": float(np.median(paired)),
        "composite_variability": float(np.std(composite_values, ddof=0)),
        "parameter_count": _parameter_count(candidate),
        "components": components,
    }


def _rank_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        -int(bool(row["gate_pass"])),
        -float(row["worst_normalized_margin"]),
        -float(row["mean_normalized_margin"]),
        -float(row["median_paired_composite_improvement"]),
        float(row["composite_variability"]),
        int(row["parameter_count"]),
        int(row["candidate_id"]),
    )


def rank_candidates(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted((dict(row) for row in rows), key=_rank_key)
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank
    return ranked


def _resolve_leaf(roots: Sequence[Path], candidate_id: int, split_id: int) -> Path:
    matches = []
    for root in roots:
        leaf = leaf_directory(root, candidate_id, split_id)
        report_path = leaf / "leaf_report.json"
        if report_path.is_file() and read_json(report_path).get("result") == "pass":
            matches.append(leaf)
    require(len(matches) == 1, f"eligible leaf attempt count mismatch for candidate {candidate_id} split {split_id}")
    return matches[0]


def _leaf_rows(roots: Sequence[Path], candidate_id: int, split_ids: Sequence[int]) -> list[dict[str, str]]:
    rows = []
    for split_id in split_ids:
        leaf = _resolve_leaf(roots, candidate_id, split_id)
        report = read_json(leaf / "leaf_report.json")
        require(report["schema"] == "three-stage-gpp-iter007-leaf-v1", "leaf schema mismatch")
        require(report["result"] == "pass", "leaf result mismatch")
        require(int(report["candidate_id"]) == candidate_id and int(report["split_id"]) == split_id, "leaf identity mismatch")
        require(report["fixed_test_access"] is False and report["spinup_execution"] is False, "leaf boundary mismatch")
        require(report["all_development_fit"] is False and report["release_created"] is False, "leaf prohibited output mismatch")
        require(sha256_file(leaf / "pooled_metrics.csv") == report["metrics_sha256"], "leaf metric hash mismatch")
        metric_rows = read_csv(leaf / "pooled_metrics.csv")
        require(len(metric_rows) == 4, "leaf pooled metric row count mismatch")
        require({row["partition"] for row in metric_rows} == {"train", "validation"}, "leaf partition mismatch")
        require({row["resolution"] for row in metric_rows} == set(RESOLUTIONS), "leaf resolution mismatch")
        require(all(int(row["candidate_id"]) == candidate_id and int(row["split_id"]) == split_id for row in metric_rows), "leaf metric identity mismatch")
        rows.extend(metric_rows)
    return rows


def _flatten_ranking(ranked: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in ranked:
        row = {
            "rank": item["rank"],
            "candidate_id": item["candidate_id"],
            "gate_pass": item["gate_pass"],
            "worst_normalized_margin": item["worst_normalized_margin"],
            "mean_normalized_margin": item["mean_normalized_margin"],
            "median_paired_composite_improvement": item["median_paired_composite_improvement"],
            "composite_variability": item["composite_variability"],
            "parameter_count": item["parameter_count"],
        }
        for resolution in RESOLUTIONS:
            component = item["components"][resolution]
            row[f"{resolution}_r2_q10"] = component["r2_q10"]
            row[f"{resolution}_rmse_q90"] = component["rmse_q90"]
            row[f"{resolution}_median_absolute_bias"] = component["median_absolute_bias"]
            row[f"{resolution}_pass"] = component["pass"]
        rows.append(row)
    return rows


def aggregate_screen(config: Mapping[str, Any], screen_roots: Sequence[Path], output: Path) -> dict[str, Any]:
    require(not output.exists(), f"screen aggregate output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    all_rows = []
    by_candidate = {}
    for candidate_id in range(24):
        rows = _leaf_rows(screen_roots, candidate_id, SCREEN_SPLITS)
        by_candidate[candidate_id] = rows
        all_rows.extend(rows)
    write_csv(output / "screen_metric_distribution.csv", all_rows)
    baseline_rows = [row for row in by_candidate[0] if row["partition"] == "validation"]
    statistics = [
        candidate_statistics(candidate_by_id(candidates, candidate_id), by_candidate[candidate_id], baseline_rows, config)
        for candidate_id in range(24)
    ]
    ranked = rank_candidates(statistics)
    write_csv(output / "screen_ranking.csv", _flatten_ranking(ranked))
    finalist_ids = [int(row["candidate_id"]) for row in ranked[:6]]
    manifest = {
        "schema": "three-stage-gpp-iter007-finalists-v1",
        "result": "pass",
        "candidate_manifest_sha256": config["candidate_manifest_sha256"],
        "screen_split_ids": list(SCREEN_SPLITS),
        "finalist_split_ids": list(FINALIST_SPLITS),
        "finalist_candidate_ids": finalist_ids,
        "ranking_rule": [
            "overall_gate_pass",
            "largest_worst_normalized_margin",
            "largest_mean_normalized_margin",
            "largest_median_paired_composite_improvement",
            "lower_composite_variability",
            "lower_parameter_count",
            "lower_candidate_id",
        ],
        "screen_ranking_sha256": sha256_file(output / "screen_ranking.csv"),
        "screen_metric_distribution_sha256": sha256_file(output / "screen_metric_distribution.csv"),
        "fixed_test_access": False,
    }
    write_json(output / "finalist_manifest.json", manifest)
    report = {
        "schema": "three-stage-gpp-iter007-screen-aggregate-v1",
        "result": "pass",
        "screen_leaf_count": 192,
        "screen_metric_rows": len(all_rows),
        "finalist_candidate_ids": finalist_ids,
        "finalist_manifest_sha256": sha256_file(output / "finalist_manifest.json"),
        "fixed_test_access": False,
    }
    write_json(output / "screen_aggregate_report.json", report)
    return report


def aggregate_final(
    config: Mapping[str, Any],
    screen_roots: Sequence[Path],
    screen_aggregate: Path,
    finalist_roots: Sequence[Path],
    output: Path,
) -> dict[str, Any]:
    require(not output.exists(), f"final aggregate output exists: {output}")
    output.mkdir(parents=True)
    candidates = load_candidates(config)
    manifest = read_json(screen_aggregate / "finalist_manifest.json")
    require(manifest["schema"] == "three-stage-gpp-iter007-finalists-v1" and manifest["result"] == "pass", "finalist manifest invalid")
    screen_report = read_json(screen_aggregate / "screen_aggregate_report.json")
    screen_validation = read_json(screen_aggregate / "screen_validation.json")
    manifest_hash = sha256_file(screen_aggregate / "finalist_manifest.json")
    require(manifest_hash == screen_report["finalist_manifest_sha256"], "frozen finalist manifest hash mismatch")
    require(manifest_hash == screen_validation["finalist_manifest_sha256"], "validated finalist manifest hash mismatch")
    finalist_ids = [int(value) for value in manifest["finalist_candidate_ids"]]
    require(len(finalist_ids) == len(set(finalist_ids)) == 6, "finalist candidate count mismatch")
    require(sha256_file(Path(config["baseline_metrics"])) == config["baseline_metrics_sha256"], "baseline metric hash mismatch")
    baseline_all = [
        row
        for row in read_csv(Path(config["baseline_metrics"]))
        if row["partition"] == "validation" and row["site"] == "pooled"
    ]
    all_rows = []
    statistics = []
    for candidate_id in finalist_ids:
        rows = _leaf_rows(screen_roots, candidate_id, SCREEN_SPLITS)
        rows.extend(_leaf_rows(finalist_roots, candidate_id, FINALIST_SPLITS))
        require(len(rows) == 20 * 4, "finalist full metric coverage mismatch")
        all_rows.extend(rows)
        statistics.append(candidate_statistics(candidate_by_id(candidates, candidate_id), rows, baseline_all, config))
    write_csv(output / "final_metric_distribution.csv", all_rows)
    ranked = rank_candidates(statistics)
    write_csv(output / "final_ranking.csv", _flatten_ranking(ranked))
    best = ranked[0]
    decision = "configuration_selected_gate_pass" if best["gate_pass"] else "search_insufficient_best_candidate_recorded"
    selection = {
        "schema": "three-stage-gpp-iter007-selection-v1",
        "result": "pass",
        "selection_gate_result": "pass" if best["gate_pass"] else "fail",
        "decision": decision,
        "best_candidate_id": int(best["candidate_id"]),
        "best_candidate": best["candidate"],
        "best_candidate_statistics": best,
        "finalist_candidate_ids": finalist_ids,
        "candidate_manifest_sha256": config["candidate_manifest_sha256"],
        "finalist_manifest_sha256": sha256_file(screen_aggregate / "finalist_manifest.json"),
        "final_metric_distribution_sha256": sha256_file(output / "final_metric_distribution.csv"),
        "final_ranking_sha256": sha256_file(output / "final_ranking.csv"),
        "fixed_test_access": False,
        "release_authorized": False,
    }
    write_json(output / "selection_report.json", selection)
    report = {
        "schema": "three-stage-gpp-iter007-final-aggregate-v1",
        "result": "pass",
        "finalist_count": 6,
        "fit_count_per_finalist": 20,
        "metric_rows": len(all_rows),
        "best_candidate_id": selection["best_candidate_id"],
        "selection_gate_result": selection["selection_gate_result"],
        "decision": decision,
        "selection_report_sha256": sha256_file(output / "selection_report.json"),
        "fixed_test_access": False,
    }
    write_json(output / "final_aggregate_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("screen", "final"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--screen-root", required=True, type=Path, action="append")
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--screen-aggregate", type=Path)
    parser.add_argument("--finalist-root", type=Path, action="append")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.mode == "screen":
        report = aggregate_screen(config, args.screen_root, args.output_directory)
        print(f"ITER007_SCREEN_AGGREGATE_OK finalists={report['finalist_candidate_ids']}", flush=True)
    else:
        require(args.screen_aggregate is not None and args.finalist_root is not None, "final paths required")
        report = aggregate_final(config, args.screen_root, args.screen_aggregate, args.finalist_root, args.output_directory)
        print(
            f"ITER007_FINAL_AGGREGATE_OK best={report['best_candidate_id']} "
            f"gate={report['selection_gate_result']} decision={report['decision']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
