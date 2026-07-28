#!/usr/bin/env python
"""Compute paired Iter011 metrics, importance changes, and the locked gate decision."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OUTPUT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")
SUMMARY_ROOT = REPO_ROOT / "development/spinup_surrogate/summaries/iter011"
CONTROL = "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf"
CANDIDATE = "s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop"
TARGETS = ("TOTSOMC", "TOTSOMN")
SEEDS = tuple(range(10001, 10101))
DROP32_COUNT = 32
GATES = {
    "median_r2_delta_min": -0.01,
    "minimum_r2_delta_min": -0.02,
    "r2_iqr_delta_max": 0.02,
    "median_rmse_ratio_delta_max": 0.02,
    "warning_fraction_max": 0.25,
}


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(float(value) for value in values)
    assert ordered and all(math.isfinite(value) for value in ordered)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize(values: list[float]) -> dict[str, float | int]:
    assert values and all(math.isfinite(float(value)) for value in values)
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
        "iqr": percentile(values, 0.75) - percentile(values, 0.25),
    }


def seed_from_path(path: Path) -> int:
    match = re.search(r"seed(\d+)", path.name)
    assert match
    return int(match.group(1))


def load_variant(variant: str) -> dict[int, dict[str, Any]]:
    stats_dir = (
        OUTPUT_ROOT / f"spinup_surrogate_iter011_{variant}" / "surrogate_spinup"
    )
    paths = sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json"))
    assert [seed_from_path(path) for path in paths] == list(SEEDS)
    return {
        seed_from_path(path): json.loads(path.read_text(encoding="utf-8"))
        for path in paths
    }


def importance_by_feature(payload: dict[str, Any], target: str) -> dict[str, dict[str, float]]:
    return {
        item["feature"]: {
            "mean_rmse_increase": float(item["mean_rmse_increase"]),
            "mean_r2_drop": float(item["mean_r2_drop"]),
        }
        for item in payload["by_variable"][target]["permutation_importance_rmse"]
    }


def main() -> None:
    control = load_variant(CONTROL)
    candidate = load_variant(CANDIDATE)
    assert set(control) == set(candidate) == set(SEEDS)

    candidate_schemas = {
        tuple(payload["feature_diagnostics"]["selected_feature_names"])
        for payload in candidate.values()
    }
    assert len(candidate_schemas) == 1
    candidate_schema = next(iter(candidate_schemas))
    schema_gate = len(candidate_schema) < DROP32_COUNT

    output: dict[str, Any] = {
        "iteration": "iter011",
        "control": CONTROL,
        "candidate": CANDIDATE,
        "seed_count": len(SEEDS),
        "gates": GATES,
        "candidate_schema": {
            "feature_count": len(candidate_schema),
            "features": list(candidate_schema),
            "stable_across_seeds": True,
            "smaller_than_drop32": schema_gate,
        },
        "by_target": {},
    }
    all_target_pass = True

    for target in TARGETS:
        target_output: dict[str, Any] = {"metrics": {}, "importance_changes": []}
        metric_values: dict[str, dict[str, list[float]]] = {}
        for metric in ("r2_val", "rmse_val", "rmse_ratio"):
            control_values = [
                float(control[seed]["by_variable"][target][metric]) for seed in SEEDS
            ]
            candidate_values = [
                float(candidate[seed]["by_variable"][target][metric]) for seed in SEEDS
            ]
            deltas = [
                candidate_value - control_value
                for control_value, candidate_value in zip(control_values, candidate_values)
            ]
            metric_values[metric] = {
                "control": control_values,
                "candidate": candidate_values,
                "paired_delta_candidate_minus_control": deltas,
            }
            target_output["metrics"][metric] = {
                "control": summarize(control_values),
                "candidate": summarize(candidate_values),
                "paired_delta_candidate_minus_control": summarize(deltas),
            }

        control_warning_fraction = sum(
            bool(control[seed]["by_variable"][target]["overfit_warning"]) for seed in SEEDS
        ) / len(SEEDS)
        candidate_warning_fraction = sum(
            bool(candidate[seed]["by_variable"][target]["overfit_warning"]) for seed in SEEDS
        ) / len(SEEDS)
        control_r2 = target_output["metrics"]["r2_val"]["control"]
        candidate_r2 = target_output["metrics"]["r2_val"]["candidate"]
        control_ratio = target_output["metrics"]["rmse_ratio"]["control"]
        candidate_ratio = target_output["metrics"]["rmse_ratio"]["candidate"]
        gate_values = {
            "median_r2_delta": candidate_r2["median"] - control_r2["median"],
            "minimum_r2_delta": candidate_r2["min"] - control_r2["min"],
            "r2_iqr_delta": candidate_r2["iqr"] - control_r2["iqr"],
            "median_rmse_ratio_delta": candidate_ratio["median"] - control_ratio["median"],
            "control_warning_fraction": control_warning_fraction,
            "candidate_warning_fraction": candidate_warning_fraction,
        }
        gate_checks = {
            "median_r2": gate_values["median_r2_delta"] >= GATES["median_r2_delta_min"],
            "minimum_r2": gate_values["minimum_r2_delta"] >= GATES["minimum_r2_delta_min"],
            "r2_iqr": gate_values["r2_iqr_delta"] <= GATES["r2_iqr_delta_max"],
            "median_rmse_ratio": gate_values["median_rmse_ratio_delta"]
            <= GATES["median_rmse_ratio_delta_max"],
            "warning_fraction": candidate_warning_fraction
            <= GATES["warning_fraction_max"],
        }
        target_pass = all(gate_checks.values())
        all_target_pass = all_target_pass and target_pass
        target_output["gate_values"] = gate_values
        target_output["gate_checks"] = gate_checks
        target_output["passes_all_target_gates"] = target_pass

        control_importance = {
            seed: importance_by_feature(control[seed], target) for seed in SEEDS
        }
        candidate_importance = {
            seed: importance_by_feature(candidate[seed], target) for seed in SEEDS
        }
        features = sorted(
            set().union(
                *(set(control_importance[seed]) | set(candidate_importance[seed]) for seed in SEEDS)
            )
        )
        for feature in features:
            control_present = all(feature in control_importance[seed] for seed in SEEDS)
            candidate_present = all(feature in candidate_importance[seed] for seed in SEEDS)
            row: dict[str, Any] = {
                "feature": feature,
                "control_present_all_seeds": control_present,
                "candidate_present_all_seeds": candidate_present,
            }
            if control_present:
                row["control"] = {
                    metric: summarize(
                        [control_importance[seed][feature][metric] for seed in SEEDS]
                    )
                    for metric in ("mean_rmse_increase", "mean_r2_drop")
                }
            if candidate_present:
                row["candidate"] = {
                    metric: summarize(
                        [candidate_importance[seed][feature][metric] for seed in SEEDS]
                    )
                    for metric in ("mean_rmse_increase", "mean_r2_drop")
                }
            if control_present and candidate_present:
                row["paired_delta_candidate_minus_control"] = {
                    metric: summarize(
                        [
                            candidate_importance[seed][feature][metric]
                            - control_importance[seed][feature][metric]
                            for seed in SEEDS
                        ]
                    )
                    for metric in ("mean_rmse_increase", "mean_r2_drop")
                }
            target_output["importance_changes"].append(row)

        output["by_target"][target] = target_output

    output["decision"] = {
        "schema_gate_pass": schema_gate,
        "all_targets_pass": all_target_pass,
        "candidate_full_gate_pass": schema_gate and all_target_pass,
        "prospective_selection": CANDIDATE if schema_gate and all_target_pass else CONTROL,
        "historical_retained_baseline_unchanged": "s32_tanh_lbfgs_a50_lr1e3_full45",
    }
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    output_path = SUMMARY_ROOT / "iter011_paired_gate_analysis.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
