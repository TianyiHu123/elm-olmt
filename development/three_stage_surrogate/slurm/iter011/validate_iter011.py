#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import SITES, require, sha256_file
from model_ELM.three_stage_sr import HOURS, write_json
from model_ELM.three_stage_sr_release import DAY_COUNT, _load_split_manifest, _positions, load_raw

CANDIDATES = tuple("ABCDE")
PARAMETERS = {"A": 9025, "B": 9025, "C": 14081, "D": 14081, "E": 14081}
METRICS = ("r2", "rmse", "mae", "bias")
PAIRS = (("B_vs_A", "B", "A"), ("D_vs_C", "D", "C"), ("C_vs_A", "C", "A"), ("D_vs_B", "D", "B"), ("E_vs_C", "E", "C"), ("D_vs_E", "D", "E"))


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def metric(observed, estimated):
    observed = np.asarray(observed, dtype=np.float64).ravel()
    estimated = np.asarray(estimated, dtype=np.float64).ravel()
    require(observed.size == estimated.size and observed.size > 1 and np.all(np.isfinite(estimated)), "validation metric input invalid")
    residual = estimated - observed
    denominator = np.sum((observed - np.mean(observed)) ** 2)
    return {"r2": float(1.0 - np.sum(residual ** 2) / denominator), "rmse": float(np.sqrt(np.mean(residual ** 2))), "mae": float(np.mean(np.abs(residual))), "bias": float(np.mean(residual))}


def recompute(config, production_root):
    layout, _, y, _ = load_raw(Path(config["raw_directory"]))
    splits = _load_split_manifest(config)["splits"]
    rows = []
    for candidate in CANDIDATES:
        for split_id in range(20):
            path = production_root / f"candidate_{candidate}" / f"split_{split_id:02d}"
            positions = _positions(layout, splits[split_id]["validation_member_ids"])
            prediction_layout = json.loads((path / "prediction_layout.json").read_text())
            predictions = np.memmap(path / "predictions_physical_float32.dat", mode="r", dtype=np.float32, shape=(2 * 164 * HOURS,))
            site_data = {}
            for site_index, site in enumerate(SITES):
                offset = next(item for item in prediction_layout["offsets"] if item["site"] == site)
                observed = np.asarray(y[site_index, positions], dtype=np.float64).reshape(-1)
                estimated = np.asarray(predictions[int(offset["start"]):int(offset["end"])], dtype=np.float64)
                require(observed.size == estimated.size == 164 * HOURS, "prediction coverage mismatch")
                site_data[site] = {"hourly": (observed, estimated), "daily": (observed.reshape(164, DAY_COUNT, 24).mean(axis=2).reshape(-1), estimated.reshape(164, DAY_COUNT, 24).mean(axis=2).reshape(-1))}
            for scope in (*SITES, "pooled"):
                for resolution in ("hourly", "daily"):
                    if scope == "pooled":
                        observed = np.concatenate([site_data[site][resolution][0] for site in SITES])
                        estimated = np.concatenate([site_data[site][resolution][1] for site in SITES])
                    else:
                        observed, estimated = site_data[scope][resolution]
                    rows.append({"candidate_id": candidate, "split_id": split_id, "scope": scope, "resolution": resolution, **metric(observed, estimated)})
    require(len(rows) == 600, "validation row count mismatch")
    return rows


def index_rows(rows):
    return {(r["candidate_id"], int(r["split_id"]), r["scope"], r["resolution"]): r for r in rows}


def improvement(index, candidate, comparator, split_id, scope, resolution, name):
    c = float(index[(candidate, split_id, scope, resolution)][name])
    b = float(index[(comparator, split_id, scope, resolution)][name])
    if name == "r2":
        return c - b
    if name == "bias":
        return abs(b) - abs(c)
    return b - c


def stats(values):
    a = np.asarray(values, dtype=np.float64)
    q = np.quantile(a, (0.10, 0.25, 0.75, 0.90), method="linear")
    return {"mean": float(np.mean(a)), "median": float(np.median(a)), "sd": float(np.std(a)), "q10": float(q[0]), "q25": float(q[1]), "q75": float(q[2]), "q90": float(q[3]), "win_count": int(np.sum(a > 0))}


def site_cost(config, index, candidate, comparator):
    pooled = np.mean([improvement(index, candidate, comparator, sid, "pooled", "daily", "rmse") for sid in range(20)])
    details, flagged = [], False
    for site in SITES:
        c = np.mean([float(index[(candidate, sid, site, "daily")]["rmse"]) for sid in range(20)])
        b = np.mean([float(index[(comparator, sid, site, "daily")]["rmse"]) for sid in range(20)])
        losses = sum(improvement(index, candidate, comparator, sid, site, "daily", "rmse") < 0 for sid in range(20))
        relative = (c - b) / b
        flag = pooled > 0 and relative >= float(config["site_cost_relative_threshold"]) and losses >= int(config["paired_support_wins"])
        flagged = flagged or flag
        details.append({"site": site, "candidate_mean_rmse": float(c), "comparator_mean_rmse": float(b), "relative_worsening": float(relative), "loss_count": int(losses), "flag": bool(flag)})
    return {"candidate": candidate, "comparator": comparator, "pooled_mean_improvement": float(pooled), "details": details, "flag": bool(flagged)}


def close(a, b):
    return np.isclose(float(a), float(b), rtol=1e-10, atol=1e-10)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--production-root", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    selection = json.loads((args.output_directory / "final_selection_report.json").read_text())
    recomputed = recompute(config, args.production_root)
    index = index_rows(recomputed)
    stored = [r for r in read_csv(args.output_directory / "metric_distribution.csv") if r["partition"] == "validation"]
    require(len(stored) == 600, "stored validation rows mismatch")
    stored_index = {(r["candidate_id"], int(r["split_id"]), r["scope"], r["resolution"]): r for r in stored}
    for key, row in index.items():
        require(key in stored_index, "stored validation identity missing")
        require(all(close(row[name], stored_index[key][name]) for name in METRICS), "stored validation metric mismatch")
    ranking = []
    for candidate in CANDIDATES:
        daily = [index[(candidate, sid, "pooled", "daily")] for sid in range(20)]
        hourly = [index[(candidate, sid, "pooled", "hourly")] for sid in range(20)]
        ranking.append({"candidate_id": candidate, "mean_pooled_daily_validation_rmse": float(np.mean([r["rmse"] for r in daily])), "mean_pooled_hourly_validation_rmse": float(np.mean([r["rmse"] for r in hourly])), "mean_absolute_pooled_daily_validation_bias": float(np.mean([abs(r["bias"]) for r in daily])), "parameter_count": PARAMETERS[candidate]})
    key = lambda r: (r["mean_pooled_daily_validation_rmse"], r["mean_pooled_hourly_validation_rmse"], r["mean_absolute_pooled_daily_validation_bias"], r["parameter_count"])
    ranking.sort(key=key)
    selected = None if key(ranking[0]) == key(ranking[1]) else ranking[0]["candidate_id"]
    require(selected == selection["selected_candidate_id"], "independent selection mismatch")
    for expected, observed in zip(ranking, selection["ranking"]):
        require(expected["candidate_id"] == observed["candidate_id"] and all(close(expected[name], observed[name]) for name in ("mean_pooled_daily_validation_rmse", "mean_pooled_hourly_validation_rmse", "mean_absolute_pooled_daily_validation_bias")) and expected["parameter_count"] == observed["parameter_count"], "ranking mismatch")
    pairs = list(PAIRS)
    if selected is not None:
        pairs.extend(((f"{selected}_vs_A_selected", selected, "A"), (f"{selected}_vs_D_selected", selected, "D")))
    paired = read_csv(args.output_directory / "paired_comparisons.csv")
    flags = {}
    for label, candidate, comparator in pairs:
        flags[label] = site_cost(config, index, candidate, comparator)
        for scope in (*SITES, "pooled"):
            for resolution in ("hourly", "daily"):
                for name in METRICS:
                    expected = stats([improvement(index, candidate, comparator, sid, scope, resolution, name) for sid in range(20)])
                    matches = [r for r in paired if r["comparison"] == label and r["scope"] == scope and r["resolution"] == resolution and r["metric"] == name]
                    require(len(matches) == 1, "paired row identity mismatch")
                    observed = matches[0]
                    require(all(close(expected[field], observed[field]) for field in ("mean", "median", "sd", "q10", "q25", "q75", "q90")) and expected["win_count"] == int(observed["win_count"]), "paired summary mismatch")
    require(flags == selection["site_cost_flags"], "site-cost flags mismatch")
    daily_sd = {candidate: float(np.std([index[(candidate, sid, "pooled", "daily")]["rmse"] for sid in range(20)])) for candidate in CANDIDATES}
    median_sd = float(np.median(list(daily_sd.values())))
    stability = {candidate: {"daily_rmse_sd": value, "median_candidate_sd": median_sd, "flag": bool(value >= float(config["poor_stability_multiplier"]) * median_sd)} for candidate, value in daily_sd.items()}
    require(stability == selection["stability"], "stability flags mismatch")
    def supported(label):
        row = next(r for r in paired if r["comparison"] == label and r["scope"] == "pooled" and r["resolution"] == "daily" and r["metric"] == "rmse")
        return float(row["mean"]) > 0 and float(row["median"]) > 0 and int(row["win_count"]) >= int(config["paired_support_wins"]) and not flags[label]["flag"]
    capacity = supported("C_vs_A") and supported("D_vs_B")
    regularization = supported("B_vs_A") and supported("D_vs_C")
    intermediate = supported("E_vs_C") and supported("D_vs_E")
    require(capacity == selection["capacity_effect_supported"] and regularization == selection["regularization_effect_supported"] and intermediate == selection["intermediate_regularization_monotonic_supported"], "effect support mismatch")
    for filename, field in (("metric_distribution.csv", "metric_distribution_sha256"), ("candidate_comparison.csv", "candidate_comparison_sha256"), ("site_performance.csv", "site_performance_sha256"), ("paired_comparisons.csv", "paired_comparisons_sha256"), ("train_validation_gap_summary.csv", "gap_summary_sha256"), ("validation_r2_distributions.png", "r2_plot_sha256"), ("validation_rmse_distributions.png", "rmse_plot_sha256")):
        require(sha256_file(args.output_directory / filename) == selection[field], f"final hash mismatch: {filename}")
    validation = {"schema": "three-stage-sr-iter011-final-validation-v1", "result": "pass", "selected_candidate_id": selected, "decision": selection["decision"], "recomputed_validation_metric_rows": 600, "production_fit_count": 100, "ranking_reproduced": True, "paired_comparisons_reproduced": True, "diagnostic_flags_reproduced": True, "effect_support_reproduced": True, "fixed_test_access": False, "release_created": False}
    write_json(args.output_directory / "final_validation.json", validation)
    print(f"ITER011_FINAL_VALIDATE_OK selected={selected} rows=600 fixed_test=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
