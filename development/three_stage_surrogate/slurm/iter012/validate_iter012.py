#!/usr/bin/env python
"""Independently recompute Iter012 validation metrics and decision evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from model_ELM.three_stage_data import SITES, require, sha256_file
from model_ELM.three_stage_sr import HOURS, write_json
from model_ELM.three_stage_sr_release import DAY_COUNT, _load_split_manifest, _positions, load_raw

ARM_IDS = ("A", "B", "C")
METRICS = ("r2", "rmse", "mae", "bias")
PAIRS = (("B_vs_A", "B", "A"), ("C_vs_B", "C", "B"), ("C_vs_A", "C", "A"))


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def metric(observed, estimated):
    observed = np.asarray(observed, dtype=np.float64).ravel()
    estimated = np.asarray(estimated, dtype=np.float64).ravel()
    require(observed.size == estimated.size and observed.size > 1, "validation metric size mismatch")
    require(np.all(np.isfinite(observed)) and np.all(np.isfinite(estimated)), "validation metric nonfinite")
    residual = estimated - observed
    denominator = np.sum((observed - np.mean(observed)) ** 2)
    return {
        "r2": float(1.0 - np.sum(residual ** 2) / denominator),
        "rmse": float(np.sqrt(np.mean(residual ** 2))),
        "mae": float(np.mean(np.abs(residual))),
        "bias": float(np.mean(residual)),
    }


def recompute(config, production_root):
    layout, _, y, _ = load_raw(Path(config["raw_directory"]))
    splits = _load_split_manifest(config)["splits"]
    rows = []
    for arm_id in ARM_IDS:
        for split_id in range(20):
            path = production_root / f"arm_{arm_id}" / f"split_{split_id:02d}"
            report = json.loads((path / "leaf_report.json").read_text(encoding="utf-8"))
            require(report["result"] == "pass" and report["arm_id"] == arm_id and report["split_id"] == split_id, "leaf identity mismatch")
            for key in ("fixed_test_access", "spinup_execution", "gpp_execution", "all_development_fit", "release_created"):
                require(report[key] is False, f"leaf scope mismatch: {key}")
            positions = _positions(layout, splits[split_id]["validation_member_ids"])
            prediction_layout = json.loads((path / "prediction_layout.json").read_text(encoding="utf-8"))
            predictions = np.memmap(path / "predictions_physical_float32.dat", mode="r", dtype=np.float32, shape=(2 * 164 * HOURS,))
            site_data = {}
            for site_index, site in enumerate(SITES):
                offset = next(item for item in prediction_layout["offsets"] if item["site"] == site)
                observed = np.asarray(y[site_index, positions], dtype=np.float64).reshape(-1)
                estimated = np.asarray(predictions[int(offset["start"]):int(offset["end"])], dtype=np.float64)
                require(observed.size == estimated.size == 164 * HOURS, "prediction coverage mismatch")
                site_data[site] = {
                    "hourly": (observed, estimated),
                    "daily": (
                        observed.reshape(164, DAY_COUNT, 24).mean(axis=2).reshape(-1),
                        estimated.reshape(164, DAY_COUNT, 24).mean(axis=2).reshape(-1),
                    ),
                }
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    if scope == "pooled":
                        observed = np.concatenate([site_data[site][resolution][0] for site in SITES])
                        estimated = np.concatenate([site_data[site][resolution][1] for site in SITES])
                    else:
                        observed, estimated = site_data[scope][resolution]
                    rows.append({"arm_id": arm_id, "split_id": split_id, "scope": scope, "resolution": resolution, **metric(observed, estimated)})
    require(len(rows) == 360, "validation row count mismatch")
    return rows


def close(left, right):
    return np.isclose(float(left), float(right), rtol=1e-10, atol=1e-10)


def stats(values):
    array = np.asarray(values, dtype=np.float64)
    require(array.size == 20 and np.all(np.isfinite(array)), "stats input mismatch")
    q10, q90 = np.quantile(array, (0.10, 0.90), method="linear")
    return {"mean": float(np.mean(array)), "median": float(np.median(array)), "sd": float(np.std(array, ddof=1)), "q10": float(q10), "q90": float(q90)}


def index_rows(rows):
    return {(row["arm_id"], int(row["split_id"]), row["scope"], row["resolution"]): row for row in rows}


def improvement(index, candidate, comparator, split_id, scope, resolution, name):
    candidate_value = float(index[(candidate, split_id, scope, resolution)][name])
    comparator_value = float(index[(comparator, split_id, scope, resolution)][name])
    if name == "r2":
        return candidate_value - comparator_value
    if name == "bias":
        return abs(comparator_value) - abs(candidate_value)
    return comparator_value - candidate_value


def site_cost(config, index, candidate, comparator):
    details = []
    flagged = False
    for site in SITES:
        candidate_mean = float(np.mean([index[(candidate, split_id, site, "daily")]["rmse"] for split_id in range(20)]))
        comparator_mean = float(np.mean([index[(comparator, split_id, site, "daily")]["rmse"] for split_id in range(20)]))
        losses = int(sum(improvement(index, candidate, comparator, split_id, site, "daily", "rmse") < 0 for split_id in range(20)))
        relative = (candidate_mean - comparator_mean) / comparator_mean
        flag = relative >= float(config["site_cost_relative_threshold"]) and losses >= int(config["paired_support_wins"])
        flagged = flagged or flag
        details.append({"site": site, "candidate_mean_rmse": candidate_mean, "comparator_mean_rmse": comparator_mean, "relative_worsening": float(relative), "loss_count": losses, "flag": bool(flag)})
    return {"candidate": candidate, "comparator": comparator, "details": details, "flag": bool(flagged)}


def consistency(config, index, candidate, comparator, flag, minimum_relative):
    values = [improvement(index, candidate, comparator, split_id, "pooled", "daily", "rmse") for split_id in range(20)]
    output = stats(values)
    comparator_mean = float(np.mean([index[(comparator, split_id, "pooled", "daily")]["rmse"] for split_id in range(20)]))
    relative = output["mean"] / comparator_mean
    wins = int(sum(value > 0 for value in values))
    passed = output["mean"] > 0 and output["median"] > 0 and wins >= int(config["paired_support_wins"]) and relative >= minimum_relative and not flag
    return {**output, "win_count": wins, "relative_mean_improvement": float(relative), "minimum_relative_improvement": float(minimum_relative), "site_deterioration_flag": bool(flag), "pass": bool(passed)}


def compare_dict(expected, observed, fields):
    return all(close(expected[field], observed[field]) for field in fields)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    selection = json.loads((args.output_directory / "final_selection_report.json").read_text(encoding="utf-8"))
    recomputed = recompute(config, args.production_root)
    index = index_rows(recomputed)
    stored = [row for row in read_csv(args.output_directory / "metric_distribution.csv") if row["partition"] == "validation"]
    require(len(stored) == 360, "stored validation rows mismatch")
    stored_index = {(row["arm_id"], int(row["split_id"]), row["scope"], row["resolution"]): row for row in stored}
    for key, row in index.items():
        require(key in stored_index and all(close(row[name], stored_index[key][name]) for name in METRICS), "stored validation metric mismatch")
    summary_rows = read_csv(args.output_directory / "overall_comparison.csv") + read_csv(args.output_directory / "site_validation.csv")
    require(len(summary_rows) == 18, "validation table row count mismatch")
    for observed in summary_rows:
        key = (observed["arm_id"], observed["scope"], observed["resolution"])
        selected = [row for row_key, row in index.items() if (row_key[0], row_key[2], row_key[3]) == key]
        require(len(selected) == 20, "validation table coverage mismatch")
        for name in METRICS:
            expected = stats([row[name] for row in selected])
            require(compare_dict(expected, {field: observed[f"{name}_{field}"] for field in expected}, tuple(expected)), "validation table summary mismatch")
    paired = read_csv(args.output_directory / "paired_comparisons.csv")
    require(len(paired) == 72, "paired row count mismatch")
    flags = {}
    for label, candidate, comparator in PAIRS:
        flags[label] = site_cost(config, index, candidate, comparator)
        comparator_daily = float(np.mean([index[(comparator, split_id, "pooled", "daily")]["rmse"] for split_id in range(20)]))
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                for name in METRICS:
                    values = [improvement(index, candidate, comparator, split_id, scope, resolution, name) for split_id in range(20)]
                    expected = stats(values)
                    matches = [row for row in paired if row["comparison"] == label and row["scope"] == scope and row["resolution"] == resolution and row["metric"] == name]
                    require(len(matches) == 1, "paired row identity mismatch")
                    observed = matches[0]
                    require(compare_dict(expected, observed, tuple(expected)), "paired summary mismatch")
                    require(int(observed["win_count"]) == int(sum(value > 0 for value in values)), "paired win mismatch")
                    require(observed["site_deterioration_flag"] == str(flags[label]["flag"]), "paired site flag mismatch")
                    if scope == "pooled" and resolution == "daily" and name == "rmse":
                        require(close(float(observed["relative_mean_improvement"]), expected["mean"] / comparator_daily), "paired relative improvement mismatch")
    b_vs_a = consistency(config, index, "B", "A", flags["B_vs_A"]["flag"], float(config["practical_relative_improvement"]))
    a_flag = site_cost(config, index, "A", "B")
    a_vs_b = consistency(config, index, "A", "B", a_flag["flag"], float(config["practical_relative_improvement"]))
    c_vs_b = consistency(config, index, "C", "B", flags["C_vs_B"]["flag"], float(config["substantial_oracle_relative_improvement"]))
    c_vs_a = consistency(config, index, "C", "A", flags["C_vs_A"]["flag"], float(config["practical_relative_improvement"]))
    if b_vs_a["pass"]:
        decision, selected, retained = "deployable_arm_B_selected", "B", "B"
    elif a_vs_b["pass"]:
        decision, selected, retained = "deployable_arm_A_selected", "A", "A"
    else:
        decision, selected, retained = "deployable_architecture_preference_inconclusive", None, "B"
    require(selection["decision"] == decision and selection["selected_deployable_arm"] == selected and selection["retained_deployable_arm"] == retained, "decision mismatch")
    expected_comparisons = {"B_vs_A": b_vs_a, "A_vs_B": a_vs_b, "C_vs_B": c_vs_b, "C_vs_A": c_vs_a}
    for label, expected in expected_comparisons.items():
        observed = selection["comparisons"][label]
        require(compare_dict(expected, observed, ("mean", "median", "sd", "q10", "q90", "relative_mean_improvement", "minimum_relative_improvement")), "decision comparison mismatch")
        require(expected["win_count"] == observed["win_count"] and expected["pass"] == observed["pass"] and expected["site_deterioration_flag"] == observed["site_deterioration_flag"], "decision comparison flag mismatch")
    require(selection["predicted_gpp_consistent_improvement"] == b_vs_a["pass"], "predicted-GPP conclusion mismatch")
    require(selection["true_gpp_substantially_more_informative"] == c_vs_b["pass"], "true-GPP diagnostic mismatch")
    require(selection["true_gpp_useful_vs_no_gpp"] == c_vs_a["pass"], "true-GPP no-GPP diagnostic mismatch")
    require(selection["fixed_test_access"] is False and selection["release_created"] is False and selection["architecture_change_authorized"] is False, "final scope mismatch")
    require(selection["fixed_upstream_sr_stage_validation"] is True, "fixed-upstream interpretation mismatch")
    require(selection["oracle_is_mathematical_upper_bound"] is False, "oracle interpretation mismatch")
    require(selection["performance_gate_applied"] is False, "performance-gate scope mismatch")
    for filename, field in (
        ("metric_distribution.csv", "metric_distribution_sha256"),
        ("metric_summary.csv", "metric_summary_sha256"),
        ("overall_comparison.csv", "overall_comparison_sha256"),
        ("site_validation.csv", "site_validation_sha256"),
        ("paired_comparisons.csv", "paired_comparisons_sha256"),
        ("train_validation_gap_summary.csv", "gap_summary_sha256"),
        ("validation_r2_distributions.png", "r2_plot_sha256"),
        ("validation_rmse_distributions.png", "rmse_plot_sha256"),
        ("summary.md", "summary_sha256"),
    ):
        require(sha256_file(args.output_directory / filename) == selection[field], f"final hash mismatch: {filename}")
    validation = {
        "schema": "three-stage-sr-iter012-final-validation-v1",
        "result": "pass",
        "decision": decision,
        "selected_deployable_arm": selected,
        "retained_deployable_arm": retained,
        "recomputed_validation_metric_rows": 360,
        "production_fit_count": 60,
        "validation_tables_reproduced": True,
        "paired_comparisons_reproduced": True,
        "decision_reproduced": True,
        "diagnostic_conclusions_reproduced": True,
        "fixed_upstream_sr_stage_validation": True,
        "oracle_is_mathematical_upper_bound": False,
        "performance_gate_applied": False,
        "spinup_execution": False,
        "gpp_execution": False,
        "all_development_fit": False,
        "fixed_test_access": False,
        "release_created": False,
    }
    write_json(args.output_directory / "final_validation.json", validation)
    print(f"ITER012_FINAL_VALIDATE_OK decision={decision} selected={selected} rows=360 fixed_test=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
