#!/usr/bin/env python
"""Independent fresh-process validation of Iter007 metrics and selection."""
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
    load_raw,
    read_csv,
    read_json,
)
from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_gpp import HOURS, write_json
from model_ELM.three_stage_gpp_release import DAY_COUNT, _load_split_manifest, _positions


def _direct_metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    observed = np.asarray(truth, dtype=np.float64).reshape(-1)
    estimated = np.asarray(prediction, dtype=np.float64).reshape(-1)
    require(observed.size == estimated.size and observed.size > 1, "independent metric input mismatch")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(estimated)), "independent metric nonfinite")
    residual = estimated - observed
    centered = observed - float(np.mean(observed))
    denominator = float(np.sum(centered * centered))
    squared = residual * residual
    return {
        "expected_count": int(observed.size),
        "valid_count": int(observed.size),
        "r2": float(1.0 - float(np.sum(squared)) / denominator),
        "rmse": float(np.sqrt(float(np.mean(squared)))),
        "bias": float(np.mean(residual)),
        "coverage_fraction": 1.0,
    }


def _validation_rows(config: Mapping[str, Any], leaf: Path, candidate_id: int, split_id: int, raw: tuple[Any, ...]) -> list[dict[str, Any]]:
    raw_layout, _, y, _ = raw
    split_manifest = _load_split_manifest(config)
    members = list(split_manifest["splits"][split_id]["validation_member_ids"])
    positions = _positions(raw_layout, members)
    prediction_layout = read_json(leaf / "prediction_layout.json")
    predictions = np.memmap(
        leaf / "predictions_physical_float32.dat",
        mode="r",
        dtype=np.float32,
        shape=(int(prediction_layout["rows"]),),
    )
    hourly_truth = []
    hourly_prediction = []
    daily_truth = []
    daily_prediction = []
    for site_index, site in enumerate(config["sites"]):
        offsets = [
            item
            for item in prediction_layout["offsets"]
            if item["partition"] == "validation" and item["site"] == site
        ]
        require(len(offsets) == 1, "independent prediction offset mismatch")
        offset = offsets[0]
        truth = np.asarray(y[site_index, positions], dtype=np.float64).reshape(-1)
        prediction = np.asarray(predictions[int(offset["start"]):int(offset["end"])], dtype=np.float64)
        require(truth.size == prediction.size == len(positions) * HOURS, "independent validation coverage mismatch")
        hourly_truth.append(truth)
        hourly_prediction.append(prediction)
        daily_truth.append(truth.reshape(len(positions), DAY_COUNT, 24).mean(axis=2).reshape(-1))
        daily_prediction.append(prediction.reshape(len(positions), DAY_COUNT, 24).mean(axis=2).reshape(-1))
    rows = []
    for resolution, truth_parts, prediction_parts in (
        ("hourly", hourly_truth, hourly_prediction),
        ("daily", daily_truth, daily_prediction),
    ):
        rows.append(
            {
                "candidate_id": candidate_id,
                "split_id": split_id,
                "partition": "validation",
                "resolution": resolution,
                **_direct_metrics(np.concatenate(truth_parts), np.concatenate(prediction_parts)),
            }
        )
    return rows


def _resolve_leaf(roots: Sequence[Path], candidate_id: int, split_id: int) -> Path:
    matches = []
    for root in roots:
        leaf = leaf_directory(root, candidate_id, split_id)
        report_path = leaf / "leaf_report.json"
        if report_path.is_file() and read_json(report_path).get("result") == "pass":
            matches.append(leaf)
    require(len(matches) == 1, f"independent eligible leaf attempt count mismatch for candidate {candidate_id} split {split_id}")
    return matches[0]


def _check_leaf(config: Mapping[str, Any], roots: Sequence[Path], candidate_id: int, split_id: int, raw: tuple[Any, ...]) -> list[dict[str, Any]]:
    leaf = _resolve_leaf(roots, candidate_id, split_id)
    report = read_json(leaf / "leaf_report.json")
    require(report["result"] == "pass", "independent leaf result mismatch")
    require(int(report["candidate_id"]) == candidate_id and int(report["split_id"]) == split_id, "independent leaf identity mismatch")
    require(report["fixed_test_access"] is False and report["spinup_execution"] is False, "independent leaf boundary mismatch")
    require(report["all_development_fit"] is False and report["release_created"] is False, "independent prohibited output mismatch")
    require(sha256_file(leaf / "pooled_metrics.csv") == report["metrics_sha256"], "independent metric hash mismatch")
    recorded = [row for row in read_csv(leaf / "pooled_metrics.csv") if row["partition"] == "validation"]
    rebuilt = _validation_rows(config, leaf, candidate_id, split_id, raw)
    require(len(recorded) == len(rebuilt) == 2, "independent validation row count mismatch")
    result = []
    for expected in rebuilt:
        matches = [row for row in recorded if row["resolution"] == expected["resolution"]]
        require(len(matches) == 1, "independent resolution row mismatch")
        observed = matches[0]
        for field in ("expected_count", "valid_count"):
            require(int(observed[field]) == int(expected[field]), f"independent {field} mismatch")
        for field in ("r2", "rmse", "bias", "coverage_fraction"):
            require(
                np.isclose(float(observed[field]), float(expected[field]), rtol=1e-12, atol=1e-12),
                f"independent {field} mismatch",
            )
        result.append({**expected})
    return result


def _thresholds(config: Mapping[str, Any], resolution: str) -> tuple[float, float, float]:
    row = config["gate"][resolution]
    return float(row["r2_q10_floor"]), float(row["rmse_q90_ceiling"]), float(row["median_absolute_bias_ceiling"])


def _composites(rows: Sequence[Mapping[str, Any]], config: Mapping[str, Any]) -> dict[int, float]:
    values = {}
    for split_id in sorted({int(row["split_id"]) for row in rows}):
        margins = []
        for resolution in RESOLUTIONS:
            matches = [row for row in rows if int(row["split_id"]) == split_id and row["resolution"] == resolution]
            require(len(matches) == 1, "independent composite coverage mismatch")
            row = matches[0]
            r2_floor, rmse_ceiling, bias_ceiling = _thresholds(config, resolution)
            margins.extend(
                (
                    (float(row["r2"]) - r2_floor) / r2_floor,
                    (rmse_ceiling - float(row["rmse"])) / rmse_ceiling,
                    (bias_ceiling - abs(float(row["bias"]))) / bias_ceiling,
                )
            )
        values[split_id] = float(np.mean(margins))
    return values


def _parameter_count(candidate: Mapping[str, Any]) -> int:
    sizes = [43, *[int(value) for value in candidate["hidden_layer_sizes"]], 1]
    return sum((left + 1) * right for left, right in zip(sizes[:-1], sizes[1:]))


def _statistics(candidate: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], baseline: Sequence[Mapping[str, Any]], config: Mapping[str, Any]) -> dict[str, Any]:
    split_ids = sorted({int(row["split_id"]) for row in rows})
    components = {}
    margins = []
    for resolution in RESOLUTIONS:
        selected = [row for row in rows if row["resolution"] == resolution]
        require(len(selected) == len(split_ids), "independent candidate coverage mismatch")
        r2_q10 = float(np.quantile([float(row["r2"]) for row in selected], 0.10, method="linear"))
        rmse_q90 = float(np.quantile([float(row["rmse"]) for row in selected], 0.90, method="linear"))
        median_abs_bias = float(np.median(np.abs([float(row["bias"]) for row in selected])))
        r2_floor, rmse_ceiling, bias_ceiling = _thresholds(config, resolution)
        local = {
            "r2": (r2_q10 - r2_floor) / r2_floor,
            "rmse": (rmse_ceiling - rmse_q90) / rmse_ceiling,
            "bias": (bias_ceiling - median_abs_bias) / bias_ceiling,
        }
        margins.extend(local.values())
        components[resolution] = {
            "r2_q10": r2_q10,
            "rmse_q90": rmse_q90,
            "median_absolute_bias": median_abs_bias,
            "pass": all(value >= 0.0 for value in local.values()),
        }
    candidate_composite = _composites(rows, config)
    baseline_composite = _composites(baseline, config)
    require(set(candidate_composite) == set(baseline_composite), "independent paired baseline mismatch")
    paired = [candidate_composite[key] - baseline_composite[key] for key in sorted(candidate_composite)]
    return {
        "candidate_id": int(candidate["candidate_id"]),
        "gate_pass": all(value >= 0.0 for value in margins),
        "worst_normalized_margin": float(np.min(margins)),
        "mean_normalized_margin": float(np.mean(margins)),
        "median_paired_composite_improvement": float(np.median(paired)),
        "composite_variability": float(np.std(list(candidate_composite.values()), ddof=0)),
        "parameter_count": _parameter_count(candidate),
        "components": components,
    }


def _rank(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -int(bool(row["gate_pass"])),
            -float(row["worst_normalized_margin"]),
            -float(row["mean_normalized_margin"]),
            -float(row["median_paired_composite_improvement"]),
            float(row["composite_variability"]),
            int(row["parameter_count"]),
            int(row["candidate_id"]),
        ),
    )


def _baseline_rows(config: Mapping[str, Any], split_ids: Sequence[int]) -> list[dict[str, Any]]:
    require(sha256_file(Path(config["baseline_metrics"])) == config["baseline_metrics_sha256"], "independent baseline metric hash mismatch")
    result = []
    for row in read_csv(Path(config["baseline_metrics"])):
        if row["partition"] != "validation" or row["site"] != "pooled" or int(row["split_id"]) not in split_ids:
            continue
        result.append(
            {
                "candidate_id": 0,
                "split_id": int(row["split_id"]),
                "partition": "validation",
                "resolution": row["resolution"],
                "r2": float(row["r2"]),
                "rmse": float(row["rmse"]),
                "bias": float(row["bias"]),
            }
        )
    require(len(result) == len(split_ids) * 2, "independent baseline coverage mismatch")
    return result


def validate_screen(config: Mapping[str, Any], screen_roots: Sequence[Path], output: Path) -> dict[str, Any]:
    candidates = load_candidates(config)
    raw = load_raw(Path(config["raw_directory"]))
    rebuilt = {}
    for candidate_id in range(24):
        rows = []
        for split_id in SCREEN_SPLITS:
            rows.extend(_check_leaf(config, screen_roots, candidate_id, split_id, raw))
        rebuilt[candidate_id] = rows
    baseline = rebuilt[0]
    ranked = _rank(
        [_statistics(candidate_by_id(candidates, candidate_id), rebuilt[candidate_id], baseline, config) for candidate_id in range(24)]
    )
    expected_ids = [int(row["candidate_id"]) for row in ranked[:6]]
    manifest = read_json(output / "finalist_manifest.json")
    require(manifest["finalist_candidate_ids"] == expected_ids, "independent screen finalist mismatch")
    require(sha256_file(output / "screen_ranking.csv") == manifest["screen_ranking_sha256"], "screen ranking hash mismatch")
    finalist_manifest_sha256 = sha256_file(output / "finalist_manifest.json")
    screen_report = read_json(output / "screen_aggregate_report.json")
    require(finalist_manifest_sha256 == screen_report["finalist_manifest_sha256"], "independent finalist manifest hash mismatch")
    report = {
        "schema": "three-stage-gpp-iter007-screen-validation-v1",
        "result": "pass",
        "independently_recomputed_leaf_count": 192,
        "finalist_candidate_ids": expected_ids,
        "finalist_manifest_sha256": finalist_manifest_sha256,
        "fixed_test_access": False,
    }
    write_json(output / "screen_validation.json", report)
    return report


def validate_final(config: Mapping[str, Any], screen_roots: Sequence[Path], screen_aggregate: Path, finalist_roots: Sequence[Path], output: Path) -> dict[str, Any]:
    candidates = load_candidates(config)
    raw = load_raw(Path(config["raw_directory"]))
    finalist_manifest = read_json(screen_aggregate / "finalist_manifest.json")
    finalist_manifest_hash = sha256_file(screen_aggregate / "finalist_manifest.json")
    screen_report = read_json(screen_aggregate / "screen_aggregate_report.json")
    screen_validation = read_json(screen_aggregate / "screen_validation.json")
    require(finalist_manifest_hash == screen_report["finalist_manifest_sha256"], "independent frozen finalist manifest mismatch")
    require(finalist_manifest_hash == screen_validation["finalist_manifest_sha256"], "independent validated finalist manifest mismatch")
    finalist_ids = [int(value) for value in finalist_manifest["finalist_candidate_ids"]]
    baseline = _baseline_rows(config, range(20))
    statistics = []
    for candidate_id in finalist_ids:
        rows = []
        for split_id in SCREEN_SPLITS:
            rows.extend(_check_leaf(config, screen_roots, candidate_id, split_id, raw))
        for split_id in FINALIST_SPLITS:
            rows.extend(_check_leaf(config, finalist_roots, candidate_id, split_id, raw))
        require(len(rows) == 40, "independent finalist metric coverage mismatch")
        statistics.append(_statistics(candidate_by_id(candidates, candidate_id), rows, baseline, config))
    ranked = _rank(statistics)
    selection = read_json(output / "selection_report.json")
    best = ranked[0]
    expected_decision = "configuration_selected_gate_pass" if best["gate_pass"] else "search_insufficient_best_candidate_recorded"
    require(int(selection["best_candidate_id"]) == int(best["candidate_id"]), "independent best candidate mismatch")
    require(selection["selection_gate_result"] == ("pass" if best["gate_pass"] else "fail"), "independent gate mismatch")
    require(selection["decision"] == expected_decision, "independent decision mismatch")
    recorded_ranking = read_csv(output / "final_ranking.csv")
    require([int(row["candidate_id"]) for row in recorded_ranking] == [int(row["candidate_id"]) for row in ranked], "independent ranking order mismatch")
    numeric_fields = (
        "worst_normalized_margin",
        "mean_normalized_margin",
        "median_paired_composite_improvement",
        "composite_variability",
    )
    for expected, observed in zip(ranked, recorded_ranking):
        for field in numeric_fields:
            require(np.isclose(float(observed[field]), float(expected[field]), rtol=1e-12, atol=1e-12), f"independent ranking {field} mismatch")
    report = {
        "schema": "three-stage-gpp-iter007-final-validation-v1",
        "result": "pass",
        "independently_recomputed_leaf_count": 120,
        "finalist_candidate_ids": finalist_ids,
        "best_candidate_id": int(best["candidate_id"]),
        "selection_gate_result": "pass" if best["gate_pass"] else "fail",
        "decision": expected_decision,
        "fixed_test_access": False,
        "release_authorized": False,
    }
    write_json(output / "final_validation.json", report)
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
        report = validate_screen(config, args.screen_root, args.output_directory)
        print(f"ITER007_SCREEN_VALIDATE_OK finalists={report['finalist_candidate_ids']}", flush=True)
    else:
        require(args.screen_aggregate is not None and args.finalist_root is not None, "final validation paths required")
        report = validate_final(config, args.screen_root, args.screen_aggregate, args.finalist_root, args.output_directory)
        print(
            f"ITER007_FINAL_VALIDATE_OK best={report['best_candidate_id']} "
            f"gate={report['selection_gate_result']} decision={report['decision']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
