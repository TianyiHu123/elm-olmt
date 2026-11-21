#!/usr/bin/env python
"""Aggregate compact Iter003 candidate results and apply the locked ranking rule."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import median, pstdev
from typing import Any, Dict, List, Mapping


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_results(screen_root: Path, count: int) -> List[Mapping[str, Any]]:
    results = []
    for candidate_id in range(count):
        matches = sorted(screen_root.glob(f"attempt_*/candidate_{candidate_id:03d}/result.json"))
        require(bool(matches), f"missing candidate result {candidate_id}")
        payload = json.loads(matches[-1].read_text(encoding="utf-8"))
        require(payload.get("status") == "complete", f"candidate {candidate_id} incomplete")
        require(int(payload["candidate_id"]) == candidate_id, "candidate identity mismatch")
        require(int(payload["split_count"]) == 20, "candidate split count mismatch")
        require(len(payload["metrics"]) == 480, "candidate metric count mismatch")
        require(len(payload["convergence"]) == 40, "candidate convergence count mismatch")
        results.append(payload)
    return results


def selected_metric(rows: List[Mapping[str, Any]], split_id: int, site: str, target: str) -> float:
    matches = [
        float(row["r2"]) for row in rows
        if int(row["split_id"]) == split_id and row["partition"] == "validation"
        and row["site"] == site and row["target"] == target and row["scale"] == "log"
    ]
    require(len(matches) == 1 and math.isfinite(matches[0]), "R2 metric lookup mismatch")
    return matches[0]


def pooled_rmse(rows: List[Mapping[str, Any]], split_id: int, target: str) -> float:
    matches = [
        float(row["rmse"]) for row in rows
        if int(row["split_id"]) == split_id and row["partition"] == "validation"
        and row["site"] == "pooled" and row["target"] == target and row["scale"] == "log"
    ]
    require(len(matches) == 1 and math.isfinite(matches[0]), "RMSE metric lookup mismatch")
    return matches[0]


def summarize(result: Mapping[str, Any]) -> Dict[str, Any]:
    rows = list(result["metrics"])
    split_scores = [
        sum(selected_metric(rows, split_id, "pooled", target) for target in ("TOTSOMC", "TOTSOMN")) / 2.0
        for split_id in range(20)
    ]
    split_rmse = [
        sum(pooled_rmse(rows, split_id, target) for target in ("TOTSOMC", "TOTSOMN")) / 2.0
        for split_id in range(20)
    ]
    site_target_medians = {
        f"{site}:{target}": median(selected_metric(rows, split_id, site, target) for split_id in range(20))
        for site in ("ABBY", "JERC") for target in ("TOTSOMC", "TOTSOMN")
    }
    warning_count = sum(int(bool(row["has_convergence_warning"])) for row in result["convergence"])
    sorted_scores = sorted(split_scores)
    q1 = median(sorted_scores[:10])
    q3 = median(sorted_scores[10:])
    return {
        "candidate_id": int(result["candidate_id"]),
        "config": result["config"],
        "config_sha256": result["config_sha256"],
        "is_iter002_baseline": bool(result["is_iter002_baseline"]),
        "median_mean_pooled_log_r2": median(split_scores),
        "mean_mean_pooled_log_r2": sum(split_scores) / len(split_scores),
        "std_mean_pooled_log_r2": pstdev(split_scores),
        "iqr_mean_pooled_log_r2": q3 - q1,
        "worst_mean_pooled_log_r2": min(split_scores),
        "median_mean_pooled_log_rmse": median(split_rmse),
        "site_target_median_log_r2": site_target_medians,
        "convergence_warning_count": warning_count,
        "split_scores": split_scores,
    }


def aggregate(screen_root: Path, candidate_count: int) -> Dict[str, Any]:
    summaries = [summarize(result) for result in resolve_results(screen_root, candidate_count)]
    baseline_matches = [row for row in summaries if row["is_iter002_baseline"]]
    require(len(baseline_matches) == 1, "baseline summary mismatch")
    baseline = baseline_matches[0]
    for row in summaries:
        regressions = {
            key: float(row["site_target_median_log_r2"][key]) - float(baseline["site_target_median_log_r2"][key])
            for key in baseline["site_target_median_log_r2"]
        }
        row["site_target_r2_delta_from_baseline"] = regressions
        row["paired_primary_delta_mean"] = sum(
            value - baseline["split_scores"][index] for index, value in enumerate(row["split_scores"])
        ) / 20.0
        row["eligible"] = min(regressions.values()) >= -0.02
        row["ineligibility_reason"] = None if row["eligible"] else "site_target_median_log_r2_regression"
    eligible = [row for row in summaries if row["eligible"]]
    require(bool(eligible), "no eligible candidates")
    best_score = max(float(row["median_mean_pooled_log_r2"]) for row in eligible)
    near = [row for row in eligible if best_score - float(row["median_mean_pooled_log_r2"]) <= 0.005]
    near.sort(key=lambda row: (
        float(row["median_mean_pooled_log_rmse"]),
        float(row["std_mean_pooled_log_r2"]),
        int(row["candidate_id"]),
    ))
    winner = near[0]
    summaries.sort(key=lambda row: (
        not bool(row["eligible"]),
        -float(row["median_mean_pooled_log_r2"]),
        float(row["median_mean_pooled_log_rmse"]),
        float(row["std_mean_pooled_log_r2"]),
        int(row["candidate_id"]),
    ))
    for rank, row in enumerate(summaries, start=1):
        row["rank"] = rank if row["eligible"] else None
        row.pop("split_scores")
    return {
        "schema": "three-stage-spinup-iter003-aggregate-v1",
        "candidate_count": candidate_count,
        "eligible_count": len(eligible),
        "selected_candidate_id": int(winner["candidate_id"]),
        "selected_config": winner["config"],
        "baseline_candidate_id": int(baseline["candidate_id"]),
        "ranking": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen-root", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--candidate-count", type=int, default=96)
    args = parser.parse_args()
    payload = aggregate(args.screen_root, args.candidate_count)
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=False)
    aggregate_path = output / "aggregate.json"
    aggregate_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ranking_path = output / "candidate_ranking.csv"
    fields = [
        "rank", "candidate_id", "eligible", "ineligibility_reason", "config_sha256",
        "median_mean_pooled_log_r2", "mean_mean_pooled_log_r2", "std_mean_pooled_log_r2",
        "median_mean_pooled_log_rmse", "convergence_warning_count", "paired_primary_delta_mean",
        "iqr_mean_pooled_log_r2", "worst_mean_pooled_log_r2",
    ]
    with ranking_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in payload["ranking"])
    report = {
        "schema": "three-stage-spinup-iter003-aggregate-report-v1",
        "result": "pass",
        "selected_candidate_id": payload["selected_candidate_id"],
        "aggregate_sha256": file_hash(aggregate_path),
        "ranking_sha256": file_hash(ranking_path),
    }
    (output / "aggregate_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ITER003_AGGREGATE_OK selected={payload['selected_candidate_id']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
