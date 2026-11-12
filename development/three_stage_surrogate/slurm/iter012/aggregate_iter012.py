#!/usr/bin/env python
"""Aggregate Iter012 leaves and apply the frozen GPP-ablation decision rule."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from development.three_stage_surrogate.slurm.iter010.iter010_common import read_csv, write_csv
from model_ELM.three_stage_data import SITES, require, sha256_file
from model_ELM.three_stage_sr import write_json

ARM_IDS = ("A", "B", "C")
PARAMETER_COUNTS = {"A": 8929, "B": 9025, "C": 9025}
METRICS = ("r2", "rmse", "mae", "bias")
QUANTILES = (0.10, 0.90)
PAIRS = (("B_vs_A", "B", "A"), ("C_vs_B", "C", "B"), ("C_vs_A", "C", "A"))


def leaf(root: Path, arm_id: str, split_id: int) -> Path:
    return root / f"arm_{arm_id}" / f"split_{split_id:02d}"


def numeric(row, name):
    return float(row[name])


def summarize(values):
    array = np.asarray(values, dtype=np.float64)
    require(array.size == 20 and np.all(np.isfinite(array)), "summary input invalid")
    q10, q90 = np.quantile(array, QUANTILES, method="linear")
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "sd": float(np.std(array, ddof=1)),
        "q10": float(q10),
        "q90": float(q90),
    }


def load_arms(config):
    manifest = json.loads(Path(config["arm_manifest"]).read_text(encoding="utf-8"))
    require(manifest["schema"] == "three-stage-sr-iter012-arms-v1", "arm schema mismatch")
    arms = {item["arm_id"]: item for item in manifest["arms"]}
    require(tuple(arms) == ARM_IDS and manifest["production_fit_count"] == 60, "arm identity mismatch")
    return arms


def verify_and_collect(config, root):
    arms = load_arms(config)
    rows = []
    expected_keys = {
        (partition, scope, resolution)
        for partition in ("train", "validation")
        for scope in (*SITES, "pooled")
        for resolution in ("hourly", "daily")
    }
    for arm_id in ARM_IDS:
        for split_id in range(20):
            path = leaf(root, arm_id, split_id)
            require(path.is_dir(), f"missing leaf: {path}")
            report = json.loads((path / "leaf_report.json").read_text(encoding="utf-8"))
            require(report["schema"] == "three-stage-sr-iter012-leaf-v1" and report["result"] == "pass", "leaf result mismatch")
            require(report["arm_id"] == arm_id and report["split_id"] == split_id, "leaf identity mismatch")
            require(report["arm"] == arms[arm_id] and report["parameter_count"] == PARAMETER_COUNTS[arm_id], "leaf arm mismatch")
            require(report["convergence_warning_count"] == 0 and report["successful_scaled_scratch_removed"] is True, "leaf technical gate failed")
            require(report["train_member_count"] == 655 and report["validation_member_count"] == 164, "leaf member count mismatch")
            for key in ("fixed_test_access", "spinup_execution", "gpp_execution", "all_development_fit", "release_created"):
                require(report[key] is False, f"leaf boundary mismatch: {key}")
            for filename, field in (
                ("predictions_physical_float32.dat", "predictions_sha256"),
                ("sr_leaf_artifact.pkl", "artifact_sha256"),
                ("metrics.csv", "metrics_sha256"),
                ("scalers.npz", "scalers_sha256"),
                ("serialization_validation.json", "serialization_validation_sha256"),
            ):
                require(sha256_file(path / filename) == report[field], f"leaf hash mismatch: {filename}")
            require(json.loads((path / "arm.json").read_text(encoding="utf-8")) == arms[arm_id], "arm file mismatch")
            serialization = json.loads((path / "serialization_validation.json").read_text(encoding="utf-8"))
            require(serialization["result"] == "pass" and serialization["arm_id"] == arm_id and serialization["split_id"] == split_id, "serialization mismatch")
            metric_rows = read_csv(path / "metrics.csv")
            require(len(metric_rows) == report["metric_rows"] == 12, "metric row count mismatch")
            require({(row["partition"], row["scope"], row["resolution"]) for row in metric_rows} == expected_keys, "metric coverage mismatch")
            for row in metric_rows:
                require(row["arm_id"] == arm_id and int(row["split_id"]) == split_id, "metric identity mismatch")
                require(int(row["convergence_warning_count"]) == 0, "metric warning mismatch")
                require(row["finite_prediction_pass"] == "True" and row["serialization_validation_pass"] == "True", "metric technical gate failed")
                require(int(row["valid_count"]) == int(row["expected_count"]), "metric count mismatch")
                require(all(np.isfinite(numeric(row, metric)) for metric in METRICS), "nonfinite metric")
                rows.append(dict(row))
    require(len(rows) == 720, "aggregate metric count mismatch")
    return rows


def summary_rows(rows):
    result = []
    for arm_id in ARM_IDS:
        for partition in ("train", "validation"):
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    selected = [
                        row for row in rows
                        if row["arm_id"] == arm_id and row["partition"] == partition
                        and row["scope"] == scope and row["resolution"] == resolution
                    ]
                    require(len(selected) == 20, "summary coverage mismatch")
                    output = {"arm_id": arm_id, "partition": partition, "scope": scope, "resolution": resolution}
                    for metric in METRICS:
                        output.update({f"{metric}_{key}": value for key, value in summarize([numeric(row, metric) for row in selected]).items()})
                    result.append(output)
    return result


def raw_index(rows):
    return {
        (row["arm_id"], int(row["split_id"]), row["partition"], row["scope"], row["resolution"]): row
        for row in rows
    }


def improvement(index, candidate, comparator, split_id, scope, resolution, metric):
    candidate_value = numeric(index[(candidate, split_id, "validation", scope, resolution)], metric)
    comparator_value = numeric(index[(comparator, split_id, "validation", scope, resolution)], metric)
    if metric == "r2":
        return candidate_value - comparator_value
    if metric == "bias":
        return abs(comparator_value) - abs(candidate_value)
    return comparator_value - candidate_value


def site_cost(config, index, candidate, comparator):
    details = []
    flagged = False
    for site in SITES:
        candidate_mean = float(np.mean([numeric(index[(candidate, split_id, "validation", site, "daily")], "rmse") for split_id in range(20)]))
        comparator_mean = float(np.mean([numeric(index[(comparator, split_id, "validation", site, "daily")], "rmse") for split_id in range(20)]))
        losses = int(sum(improvement(index, candidate, comparator, split_id, site, "daily", "rmse") < 0 for split_id in range(20)))
        relative_worsening = (candidate_mean - comparator_mean) / comparator_mean
        flag = relative_worsening >= float(config["site_cost_relative_threshold"]) and losses >= int(config["paired_support_wins"])
        flagged = flagged or flag
        details.append({
            "site": site,
            "candidate_mean_rmse": candidate_mean,
            "comparator_mean_rmse": comparator_mean,
            "relative_worsening": float(relative_worsening),
            "loss_count": losses,
            "flag": bool(flag),
        })
    return {"candidate": candidate, "comparator": comparator, "details": details, "flag": bool(flagged)}


def paired_rows(config, index):
    rows = []
    flags = {}
    for label, candidate, comparator in PAIRS:
        flags[label] = site_cost(config, index, candidate, comparator)
        comparator_daily = float(np.mean([numeric(index[(comparator, split_id, "validation", "pooled", "daily")], "rmse") for split_id in range(20)]))
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                for metric in METRICS:
                    values = [improvement(index, candidate, comparator, split_id, scope, resolution, metric) for split_id in range(20)]
                    output = {
                        "comparison": label,
                        "candidate": candidate,
                        "comparator": comparator,
                        "scope": scope,
                        "resolution": resolution,
                        "metric": metric,
                        **summarize(values),
                        "win_count": int(sum(value > 0 for value in values)),
                        "relative_mean_improvement": "",
                        "site_deterioration_flag": flags[label]["flag"],
                    }
                    if scope == "pooled" and resolution == "daily" and metric == "rmse":
                        output["relative_mean_improvement"] = float(output["mean"] / comparator_daily)
                    rows.append(output)
    return rows, flags


def gap_rows(index):
    raw = []
    summary = []
    for arm_id in ARM_IDS:
        for split_id in range(20):
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    train = index[(arm_id, split_id, "train", scope, resolution)]
                    validation = index[(arm_id, split_id, "validation", scope, resolution)]
                    raw.append({
                        "arm_id": arm_id,
                        "split_id": split_id,
                        "scope": scope,
                        "resolution": resolution,
                        "r2_gap": numeric(train, "r2") - numeric(validation, "r2"),
                        "rmse_gap": numeric(validation, "rmse") - numeric(train, "rmse"),
                        "mae_gap": numeric(validation, "mae") - numeric(train, "mae"),
                        "absolute_bias_gap": abs(numeric(validation, "bias")) - abs(numeric(train, "bias")),
                    })
    for arm_id in ARM_IDS:
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                selected = [row for row in raw if row["arm_id"] == arm_id and row["scope"] == scope and row["resolution"] == resolution]
                output = {"arm_id": arm_id, "scope": scope, "resolution": resolution}
                for metric in ("r2_gap", "rmse_gap", "mae_gap", "absolute_bias_gap"):
                    output.update({f"{metric}_{key}": value for key, value in summarize([float(row[metric]) for row in selected]).items()})
                summary.append(output)
    return raw, summary


def consistency(config, index, candidate, comparator, site_flag, minimum_relative):
    values = [improvement(index, candidate, comparator, split_id, "pooled", "daily", "rmse") for split_id in range(20)]
    stats = summarize(values)
    comparator_mean = float(np.mean([numeric(index[(comparator, split_id, "validation", "pooled", "daily")], "rmse") for split_id in range(20)]))
    relative = stats["mean"] / comparator_mean
    wins = int(sum(value > 0 for value in values))
    passed = stats["mean"] > 0 and stats["median"] > 0 and wins >= int(config["paired_support_wins"]) and relative >= minimum_relative and not site_flag
    return {**stats, "win_count": wins, "relative_mean_improvement": float(relative), "minimum_relative_improvement": float(minimum_relative), "site_deterioration_flag": bool(site_flag), "pass": bool(passed)}


def plot_metric(index, metric, output):
    figure, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=False)
    for axis, resolution in zip(axes, ("hourly", "daily")):
        values = [[numeric(index[(arm_id, split_id, "validation", "pooled", resolution)], metric) for split_id in range(20)] for arm_id in ARM_IDS]
        axis.boxplot(values, tick_labels=ARM_IDS, showmeans=True)
        axis.set_title(f"Pooled {resolution}")
        axis.set_xlabel("Arm")
        axis.set_ylabel(metric.upper())
        axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    plt.close(figure)


def write_summary(path, report):
    b = report["comparisons"]["B_vs_A"]
    cb = report["comparisons"]["C_vs_B"]
    ca = report["comparisons"]["C_vs_A"]
    selected = report["selected_deployable_arm"] or "none"
    text = f"""# Iter012 SR GPP-input ablation

- Decision: `{report['decision']}`; selected deployable arm: `{selected}`; retained operational arm: `{report['retained_deployable_arm']}`.
- Predicted GPP versus no GPP: mean pooled daily RMSE improvement {100.0 * b['relative_mean_improvement']:.3f}%, median paired improvement {b['median']:.6g}, wins {b['win_count']}/20; consistent practical improvement: `{str(b['pass']).lower()}`.
- True GPP versus predicted GPP: mean pooled daily RMSE improvement {100.0 * cb['relative_mean_improvement']:.3f}%, median paired improvement {cb['median']:.6g}, wins {cb['win_count']}/20; substantially more informative: `{str(report['true_gpp_substantially_more_informative']).lower()}`.
- True GPP versus no GPP: mean pooled daily RMSE improvement {100.0 * ca['relative_mean_improvement']:.3f}%, median paired improvement {ca['median']:.6g}, wins {ca['win_count']}/20; useful added explanatory power: `{str(report['true_gpp_useful_vs_no_gpp']).lower()}`.
- Arm C is a non-deployable diagnostic and is not interpreted as a mathematical upper bound.
- Evidence is fixed-upstream SR-stage validation on ABBY/JERC development members; the protected fixed test was not accessed and no release artifact was created.
- Recommendation: {report['recommendation']}
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output_directory.exists(), f"output exists: {args.output_directory}")
    args.output_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    rows = verify_and_collect(config, args.production_root)
    write_csv(args.output_directory / "metric_distribution.csv", rows)
    summaries = summary_rows(rows)
    write_csv(args.output_directory / "metric_summary.csv", summaries)
    validation = [row for row in summaries if row["partition"] == "validation"]
    write_csv(args.output_directory / "overall_comparison.csv", [row for row in validation if row["scope"] == "pooled"])
    write_csv(args.output_directory / "site_validation.csv", [row for row in validation if row["scope"] in SITES])
    index = raw_index(rows)
    paired, flags = paired_rows(config, index)
    write_csv(args.output_directory / "paired_comparisons.csv", paired)
    raw_gaps, gap_summary = gap_rows(index)
    write_csv(args.output_directory / "train_validation_gap_distribution.csv", raw_gaps)
    write_csv(args.output_directory / "train_validation_gap_summary.csv", gap_summary)
    b_vs_a = consistency(config, index, "B", "A", flags["B_vs_A"]["flag"], float(config["practical_relative_improvement"]))
    a_vs_b_flag = site_cost(config, index, "A", "B")
    a_vs_b = consistency(config, index, "A", "B", a_vs_b_flag["flag"], float(config["practical_relative_improvement"]))
    c_vs_b = consistency(config, index, "C", "B", flags["C_vs_B"]["flag"], float(config["substantial_oracle_relative_improvement"]))
    c_vs_a = consistency(config, index, "C", "A", flags["C_vs_A"]["flag"], float(config["practical_relative_improvement"]))
    if b_vs_a["pass"]:
        decision = "deployable_arm_B_selected"
        selected = "B"
        retained = "B"
    elif a_vs_b["pass"]:
        decision = "deployable_arm_A_selected"
        selected = "A"
        retained = "A"
    else:
        decision = "deployable_architecture_preference_inconclusive"
        selected = None
        retained = "B"
    recommendation = "proceed_to_fresh_sr_robustness_testing" if selected is not None or not c_vs_b["pass"] else "investigate_temporal_or_physical_predictors_before_fresh_sr_robustness"
    ranking = []
    for arm_id in ARM_IDS:
        values = [numeric(index[(arm_id, split_id, "validation", "pooled", "daily")], "rmse") for split_id in range(20)]
        ranking.append({"arm_id": arm_id, "deployable": arm_id in ("A", "B"), "mean_pooled_daily_validation_rmse": float(np.mean(values)), "median_pooled_daily_validation_rmse": float(np.median(values)), "sd_pooled_daily_validation_rmse": float(np.std(values, ddof=1))})
    ranking.sort(key=lambda row: row["mean_pooled_daily_validation_rmse"])
    plot_metric(index, "r2", args.output_directory / "validation_r2_distributions.png")
    plot_metric(index, "rmse", args.output_directory / "validation_rmse_distributions.png")
    report = {
        "schema": "three-stage-sr-iter012-final-selection-v1",
        "result": "pass",
        "decision": decision,
        "selected_deployable_arm": selected,
        "retained_deployable_arm": retained,
        "ranking": ranking,
        "comparisons": {"B_vs_A": b_vs_a, "A_vs_B": a_vs_b, "C_vs_B": c_vs_b, "C_vs_A": c_vs_a},
        "site_deterioration": {**flags, "A_vs_B": a_vs_b_flag},
        "predicted_gpp_consistent_improvement": b_vs_a["pass"],
        "true_gpp_substantially_more_informative": c_vs_b["pass"],
        "true_gpp_useful_vs_no_gpp": c_vs_a["pass"],
        "recommendation": recommendation,
        "production_fit_count": 60,
        "metric_rows": 720,
        "validation_metric_rows": 360,
        "fixed_upstream_sr_stage_validation": True,
        "oracle_is_mathematical_upper_bound": False,
        "performance_gate_applied": False,
        "fixed_test_access": False,
        "release_created": False,
        "architecture_change_authorized": False,
    }
    write_summary(args.output_directory / "summary.md", report)
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
        report[field] = sha256_file(args.output_directory / filename)
    write_json(args.output_directory / "final_selection_report.json", report)
    print(f"ITER012_AGGREGATE_OK decision={decision} selected={selected} retained={retained}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
