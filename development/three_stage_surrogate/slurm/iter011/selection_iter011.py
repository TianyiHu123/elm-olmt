#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter010.iter010_common import read_csv, write_csv
from development.three_stage_surrogate.slurm.iter011.iter011_common import CANDIDATE_IDS, PARAMETER_COUNTS, candidate_by_id, load_candidates
from model_ELM.three_stage_data import SITES, require, sha256_file
from model_ELM.three_stage_sr import write_json

METRICS = ("r2", "rmse", "mae", "bias")
QUANTILES = (0.10, 0.25, 0.75, 0.90)
BASE_PAIRS = (("B_vs_A", "B", "A"), ("D_vs_C", "D", "C"), ("C_vs_A", "C", "A"), ("D_vs_B", "D", "B"), ("E_vs_C", "E", "C"), ("D_vs_E", "D", "E"))


def leaf(root: Path, candidate_id: str, split_id: int) -> Path:
    return root / f"candidate_{candidate_id}" / f"split_{split_id:02d}"


def numeric(row, name):
    return float(row[name])


def summarize(values):
    a = np.asarray(values, dtype=np.float64)
    require(a.size == 20 and np.all(np.isfinite(a)), "summary input invalid")
    q = np.quantile(a, QUANTILES, method="linear")
    return {"mean": float(np.mean(a)), "median": float(np.median(a)), "sd": float(np.std(a)), "q10": float(q[0]), "q25": float(q[1]), "q75": float(q[2]), "q90": float(q[3])}


def verify_and_collect(config, root):
    candidates = load_candidates(config)
    rows = []
    expected_keys = {(p, s, r) for p in ("train", "validation") for s in (*SITES, "pooled") for r in ("hourly", "daily")}
    for candidate_id in CANDIDATE_IDS:
        expected_candidate = candidate_by_id(candidates, candidate_id)
        for split_id in range(20):
            path = leaf(root, candidate_id, split_id)
            require(path.is_dir(), f"missing leaf: {path}")
            report = json.loads((path / "leaf_report.json").read_text())
            require(report["schema"] == "three-stage-sr-iter011-leaf-v1" and report["result"] == "pass", "leaf result mismatch")
            require(report["candidate_id"] == candidate_id and report["split_id"] == split_id and report["candidate"] == expected_candidate, "leaf identity mismatch")
            require(report["parameter_count"] == PARAMETER_COUNTS[candidate_id], "parameter count mismatch")
            require(report["convergence_warning_count"] == 0 and report["successful_scaled_scratch_removed"] is True, "leaf technical gate failed")
            for key in ("fixed_test_access", "spinup_execution", "gpp_execution", "all_development_fit", "release_created"):
                require(report[key] is False, f"leaf boundary mismatch: {key}")
            for filename, field in (("predictions_physical_float32.dat", "predictions_sha256"), ("sr_leaf_artifact.pkl", "artifact_sha256"), ("metrics.csv", "metrics_sha256"), ("scalers.npz", "scalers_sha256"), ("serialization_validation.json", "serialization_validation_sha256")):
                require(sha256_file(path / filename) == report[field], f"leaf hash mismatch: {filename}")
            require(json.loads((path / "candidate.json").read_text()) == expected_candidate, "candidate file mismatch")
            serial = json.loads((path / "serialization_validation.json").read_text())
            require(serial["result"] == "pass" and serial["candidate_id"] == candidate_id and serial["split_id"] == split_id, "serialization mismatch")
            metric_rows = read_csv(path / "metrics.csv")
            require(len(metric_rows) == report["metric_rows"] == 12, "metric row count mismatch")
            require({(x["partition"], x["scope"], x["resolution"]) for x in metric_rows} == expected_keys, "metric coverage mismatch")
            for row in metric_rows:
                require(row["candidate_id"] == candidate_id and int(row["split_id"]) == split_id, "metric identity mismatch")
                require(int(row["convergence_warning_count"]) == 0 and row["finite_prediction_pass"] == "True" and row["serialization_validation_pass"] == "True", "metric gate mismatch")
                require(int(row["valid_count"]) == int(row["expected_count"]), "metric count mismatch")
                require(all(np.isfinite(numeric(row, metric)) for metric in METRICS), "nonfinite metric")
                rows.append(dict(row))
    require(len(rows) == 1200, "aggregate metric count mismatch")
    return rows


def summary_rows(rows):
    result = []
    for candidate_id in CANDIDATE_IDS:
        for partition in ("train", "validation"):
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    selected = [r for r in rows if r["candidate_id"] == candidate_id and r["partition"] == partition and r["scope"] == scope and r["resolution"] == resolution]
                    require(len(selected) == 20, "summary coverage mismatch")
                    out = {"candidate_id": candidate_id, "partition": partition, "scope": scope, "resolution": resolution}
                    for metric in METRICS:
                        out.update({f"{metric}_{key}": value for key, value in summarize([numeric(r, metric) for r in selected]).items()})
                    result.append(out)
    return result


def raw_index(rows):
    return {(r["candidate_id"], int(r["split_id"]), r["partition"], r["scope"], r["resolution"]): r for r in rows}


def improvement(index, candidate, comparator, split_id, scope, resolution, metric):
    c = numeric(index[(candidate, split_id, "validation", scope, resolution)], metric)
    b = numeric(index[(comparator, split_id, "validation", scope, resolution)], metric)
    if metric == "r2":
        return c - b
    if metric == "bias":
        return abs(b) - abs(c)
    return b - c


def site_cost(config, index, candidate, comparator):
    pooled = np.mean([improvement(index, candidate, comparator, sid, "pooled", "daily", "rmse") for sid in range(20)])
    details = []
    flagged = False
    for site in SITES:
        c = np.mean([numeric(index[(candidate, sid, "validation", site, "daily")], "rmse") for sid in range(20)])
        b = np.mean([numeric(index[(comparator, sid, "validation", site, "daily")], "rmse") for sid in range(20)])
        losses = sum(improvement(index, candidate, comparator, sid, site, "daily", "rmse") < 0 for sid in range(20))
        relative_worsening = (c - b) / b
        site_flag = pooled > 0 and relative_worsening >= float(config["site_cost_relative_threshold"]) and losses >= int(config["paired_support_wins"])
        flagged = flagged or site_flag
        details.append({"site": site, "candidate_mean_rmse": float(c), "comparator_mean_rmse": float(b), "relative_worsening": float(relative_worsening), "loss_count": int(losses), "flag": bool(site_flag)})
    return {"candidate": candidate, "comparator": comparator, "pooled_mean_improvement": float(pooled), "details": details, "flag": bool(flagged)}


def paired_rows(config, index, pairs):
    rows, flags = [], {}
    for label, candidate, comparator in pairs:
        flag = site_cost(config, index, candidate, comparator)
        flags[label] = flag
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                for metric in METRICS:
                    values = [improvement(index, candidate, comparator, sid, scope, resolution, metric) for sid in range(20)]
                    out = {"comparison": label, "candidate": candidate, "comparator": comparator, "scope": scope, "resolution": resolution, "metric": metric, **summarize(values), "win_count": int(sum(value > 0 for value in values))}
                    rows.append(out)
    return rows, flags


def gap_rows(index):
    raw, summary = [], []
    for candidate_id in CANDIDATE_IDS:
        for split_id in range(20):
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    train = index[(candidate_id, split_id, "train", scope, resolution)]
                    validation = index[(candidate_id, split_id, "validation", scope, resolution)]
                    raw.append({"candidate_id": candidate_id, "split_id": split_id, "scope": scope, "resolution": resolution, "r2_gap": numeric(train, "r2") - numeric(validation, "r2"), "rmse_gap": numeric(validation, "rmse") - numeric(train, "rmse"), "mae_gap": numeric(validation, "mae") - numeric(train, "mae"), "absolute_bias_gap": abs(numeric(validation, "bias")) - abs(numeric(train, "bias"))})
    for candidate_id in CANDIDATE_IDS:
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                selected = [r for r in raw if r["candidate_id"] == candidate_id and r["scope"] == scope and r["resolution"] == resolution]
                out = {"candidate_id": candidate_id, "scope": scope, "resolution": resolution}
                for metric in ("r2_gap", "rmse_gap", "mae_gap", "absolute_bias_gap"):
                    out.update({f"{metric}_{key}": value for key, value in summarize([float(r[metric]) for r in selected]).items()})
                summary.append(out)
    return raw, summary


def select(config, index):
    ranking = []
    for candidate_id in CANDIDATE_IDS:
        daily = [index[(candidate_id, sid, "validation", "pooled", "daily")] for sid in range(20)]
        hourly = [index[(candidate_id, sid, "validation", "pooled", "hourly")] for sid in range(20)]
        ranking.append({"candidate_id": candidate_id, "mean_pooled_daily_validation_rmse": float(np.mean([numeric(r, "rmse") for r in daily])), "mean_pooled_hourly_validation_rmse": float(np.mean([numeric(r, "rmse") for r in hourly])), "mean_absolute_pooled_daily_validation_bias": float(np.mean([abs(numeric(r, "bias")) for r in daily])), "parameter_count": PARAMETER_COUNTS[candidate_id]})
    keys = lambda r: (r["mean_pooled_daily_validation_rmse"], r["mean_pooled_hourly_validation_rmse"], r["mean_absolute_pooled_daily_validation_bias"], r["parameter_count"])
    ranking.sort(key=keys)
    tied = len(ranking) > 1 and keys(ranking[0]) == keys(ranking[1])
    return ranking, None if tied else ranking[0]["candidate_id"]


def plot_metric(index, metric, output):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=False)
    for axis, resolution in zip(axes, ("hourly", "daily")):
        values = [[numeric(index[(candidate, sid, "validation", "pooled", resolution)], metric) for sid in range(20)] for candidate in CANDIDATE_IDS]
        axis.boxplot(values, tick_labels=CANDIDATE_IDS, showmeans=True)
        axis.set_title(f"Pooled {resolution}")
        axis.set_xlabel("Candidate")
        axis.set_ylabel(metric.upper())
        axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(not args.output_directory.exists(), f"output exists: {args.output_directory}")
    args.output_directory.mkdir(parents=True)
    config = json.loads(args.config.read_text())
    rows = verify_and_collect(config, args.production_root)
    write_csv(args.output_directory / "metric_distribution.csv", rows)
    summaries = summary_rows(rows)
    write_csv(args.output_directory / "metric_summary.csv", summaries)
    write_csv(args.output_directory / "candidate_comparison.csv", [r for r in summaries if r["scope"] == "pooled"])
    write_csv(args.output_directory / "site_performance.csv", [r for r in summaries if r["scope"] in SITES])
    index = raw_index(rows)
    ranking, selected = select(config, index)
    pairs = list(BASE_PAIRS)
    if selected is not None:
        pairs.extend(((f"{selected}_vs_A_selected", selected, "A"), (f"{selected}_vs_D_selected", selected, "D")))
    paired, flags = paired_rows(config, index, pairs)
    write_csv(args.output_directory / "paired_comparisons.csv", paired)
    raw_gaps, summarized_gaps = gap_rows(index)
    write_csv(args.output_directory / "train_validation_gap_distribution.csv", raw_gaps)
    write_csv(args.output_directory / "train_validation_gap_summary.csv", summarized_gaps)
    daily_sd = {candidate: float(np.std([numeric(index[(candidate, sid, "validation", "pooled", "daily")], "rmse") for sid in range(20)])) for candidate in CANDIDATE_IDS}
    median_sd = float(np.median(list(daily_sd.values())))
    stability = {candidate: {"daily_rmse_sd": value, "median_candidate_sd": median_sd, "flag": bool(value >= float(config["poor_stability_multiplier"]) * median_sd)} for candidate, value in daily_sd.items()}
    def supported(label):
        row = next(r for r in paired if r["comparison"] == label and r["scope"] == "pooled" and r["resolution"] == "daily" and r["metric"] == "rmse")
        return row["mean"] > 0 and row["median"] > 0 and row["win_count"] >= int(config["paired_support_wins"]) and not flags[label]["flag"]
    capacity = supported("C_vs_A") and supported("D_vs_B")
    regularization = supported("B_vs_A") and supported("D_vs_C")
    intermediate = supported("E_vs_C") and supported("D_vs_E")
    if capacity and regularization:
        attribution = "both_capacity_and_weaker_regularization_supported"
    elif capacity:
        attribution = "capacity_supported_regularization_not_supported"
    elif regularization:
        attribution = "weaker_regularization_supported_capacity_not_supported"
    else:
        attribution = "mixed_or_unsupported"
    plot_metric(index, "r2", args.output_directory / "validation_r2_distributions.png")
    plot_metric(index, "rmse", args.output_directory / "validation_rmse_distributions.png")
    decision = "sr_capacity_regularization_selection_unresolved" if selected is None else "sr_capacity_regularization_configuration_selected"
    report = {"schema": "three-stage-sr-iter011-final-selection-v1", "result": "pass", "decision": decision, "selected_candidate_id": selected, "ranking": ranking, "site_cost_flags": flags, "stability": stability, "capacity_effect_supported": capacity, "regularization_effect_supported": regularization, "intermediate_regularization_monotonic_supported": intermediate, "effect_attribution": attribution, "production_fit_count": 100, "metric_rows": 1200, "validation_metric_rows": 600, "performance_gate_applied": False, "fixed_test_access": False, "release_created": False, "metric_distribution_sha256": sha256_file(args.output_directory / "metric_distribution.csv"), "candidate_comparison_sha256": sha256_file(args.output_directory / "candidate_comparison.csv"), "site_performance_sha256": sha256_file(args.output_directory / "site_performance.csv"), "paired_comparisons_sha256": sha256_file(args.output_directory / "paired_comparisons.csv"), "gap_summary_sha256": sha256_file(args.output_directory / "train_validation_gap_summary.csv"), "r2_plot_sha256": sha256_file(args.output_directory / "validation_r2_distributions.png"), "rmse_plot_sha256": sha256_file(args.output_directory / "validation_rmse_distributions.png")}
    write_json(args.output_directory / "final_selection_report.json", report)
    print(f"ITER011_SELECTION_OK selected={selected} decision={decision}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
