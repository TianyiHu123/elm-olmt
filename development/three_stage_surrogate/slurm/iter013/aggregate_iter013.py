#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_sr import write_json
from model_ELM.three_stage_sr_release import aggregate, validate_aggregate

METRICS = ("r2", "rmse", "mae", "bias", "residual_std", "q0_01", "q0_025", "q0_05", "q0_25", "q0_5", "q0_75", "q0_95", "q0_975", "q0_99")


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows):
    require(rows, f"empty table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def stats(values):
    data = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(data)), "median": float(np.median(data)), "sample_sd": float(np.std(data, ddof=1)),
        "q10": float(np.quantile(data, 0.10, method="linear")), "q25": float(np.quantile(data, 0.25, method="linear")),
        "q75": float(np.quantile(data, 0.75, method="linear")), "q90": float(np.quantile(data, 0.90, method="linear")),
    }


def summarize(metric_path: Path, output: Path):
    rows = read_rows(metric_path)
    grouped = defaultdict(list)
    by_key = {}
    for row in rows:
        key = (int(row["split_id"]), row["site"], row["resolution"], row["partition"])
        by_key[key] = row
        for metric in METRICS:
            grouped[(row["partition"], row["site"], row["resolution"], metric)].append(float(row[metric]))
    summary = []
    for (partition, site, resolution, metric), values in sorted(grouped.items()):
        summary.append({"partition": partition, "site": site, "resolution": resolution, "metric": metric, **stats(values)})
    write_rows(output / "metric_summary.csv", summary)
    gaps = defaultdict(list)
    for split_id in range(20):
        for site in ("ABBY", "JERC", "pooled"):
            for resolution in ("hourly", "daily"):
                train = by_key[(split_id, site, resolution, "train")]
                validation = by_key[(split_id, site, resolution, "validation")]
                gaps[(site, resolution, "r2_train_minus_validation")].append(float(train["r2"]) - float(validation["r2"]))
                for metric in ("rmse", "mae", "residual_std"):
                    gaps[(site, resolution, f"{metric}_validation_minus_train")].append(float(validation[metric]) - float(train[metric]))
                gaps[(site, resolution, "absolute_bias_validation_minus_train")].append(abs(float(validation["bias"])) - abs(float(train["bias"])))
    gap_rows = []
    for (site, resolution, gap), values in sorted(gaps.items()):
        gap_rows.append({"site": site, "resolution": resolution, "gap": gap, "positive_means_degradation": True, **stats(values)})
    write_rows(output / "train_validation_gap_summary.csv", gap_rows)
    return len(summary), len(gap_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--robustness-directory", required=True, type=Path)
    parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = aggregate(config, args.robustness_directory, args.attempt_directory)
    require(report["gate"]["result"] == "not_applicable", "performance gate unexpectedly applied")
    summary_rows, gap_rows = summarize(args.attempt_directory / "metric_distribution.csv", args.attempt_directory)
    validation = validate_aggregate(config, args.robustness_directory, args.attempt_directory)
    require(validation["result"] == "pass" and validation["metric_rows"] == 240, "aggregate validation failed")
    final = {
        "schema": "three-stage-sr-iter013-aggregate-v1", "result": "pass",
        "metric_rows": validation["metric_rows"], "uncertainty_rows": validation["uncertainty_rows"],
        "summary_rows": summary_rows, "gap_rows": gap_rows, "performance_gate_applied": False,
        "release_basis": config["release_basis"], "fixed_test_access": False,
        "aggregate_validation_sha256": sha256_file(args.attempt_directory / "aggregate_validation.json"),
    }
    write_json(args.attempt_directory / "iter013_aggregate_report.json", final)
    print(f"ITER013_AGGREGATE_OK metrics={final['metric_rows']} uncertainty={final['uncertainty_rows']} summaries={summary_rows} gaps={gap_rows}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
