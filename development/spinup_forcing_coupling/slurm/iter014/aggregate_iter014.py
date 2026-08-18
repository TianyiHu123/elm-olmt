#!/usr/bin/env python3
"""Aggregate Iter014 pool-rule evaluations into repair decision labels."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

POOL_RULES = ("rank_dominated", "hybrid_high_l_maximin")
ACCEPTANCE_CLEAR = 0.25
WASSERSTEIN_GATE = 0.05


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_evaluation(root: Path, pool_rule: str) -> dict:
    artifacts = root / pool_rule / "artifacts"
    result_path = artifacts / "evaluation_result.json"
    require(result_path.is_file(), f"missing {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("status") == "geometry_gate_failed":
        require(result.get("site") == "JERC", f"{pool_rule}: site")
        require(result.get("pool_rule") == pool_rule, f"{pool_rule}: pool_rule field")
        require(result.get("label") == "geometry_gate_failed", f"{pool_rule}: label")
        return result
    required = (
        result_path,
        artifacts / "physical_traces.npz",
        artifacts / "hourly_predictions.csv",
        artifacts / "physical_corner.png",
    )
    require(all(path.is_file() for path in required), f"{pool_rule}: incomplete artifacts")
    require(result.get("status") == "pass", f"{pool_rule}: evaluation status")
    require(result.get("site") == "JERC", f"{pool_rule}: site")
    require(result.get("pool_rule") == pool_rule, f"{pool_rule}: pool_rule field")
    require(result.get("seeds") == [9009, 9010, 9011], f"{pool_rule}: seeds")
    require(result.get("nsteps") == 8000, f"{pool_rule}: nsteps")
    return result


def decide(result: dict) -> str:
    if result.get("status") == "geometry_gate_failed" or result.get("label") == "geometry_gate_failed":
        return "geometry_gate_failed"
    integrity = bool(result.get("integrity_pass"))
    mean_acc = float(result["mean_acceptance"])
    wasserstein = float(result["max_cross_seed_normalized_wasserstein"])
    control = result["control_comparison"]
    acc_improved = bool(control["acceptance_improved"])
    w_improved = bool(control["wasserstein_improved"])
    clearly_acc = mean_acc >= ACCEPTANCE_CLEAR
    clearly_w = wasserstein <= WASSERSTEIN_GATE
    if integrity and clearly_acc and clearly_w:
        return "repair_supported"
    if integrity and (acc_improved or w_improved):
        return "partial_repair"
    return "not_supported"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation-root", required=True, type=Path)
    parser.add_argument("--control-evaluation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    result_path = args.output / "aggregate_result.json"
    table_path = args.output / "variant_table.csv"
    if result_path.exists() or table_path.exists():
        raise FileExistsError("refusing to overwrite completed aggregate outputs")

    control = json.loads(args.control_evaluation.read_text(encoding="utf-8"))
    control_mean = float(sum(control["mean_acceptance_by_seed"]) / 3.0)
    control_w = float(control["max_cross_seed_normalized_wasserstein"])

    rows = []
    variants = {}
    for pool_rule in POOL_RULES:
        evaluation = load_evaluation(args.evaluation_root, pool_rule)
        decision = decide(evaluation)
        if decision == "geometry_gate_failed":
            row = {
                "site": "JERC",
                "pool_rule": pool_rule,
                "integrity_pass": False,
                "label": "geometry_gate_failed",
                "mean_acceptance": "",
                "max_cross_seed_normalized_wasserstein": "",
                "control_mean_acceptance": control_mean,
                "control_max_cross_seed_normalized_wasserstein": control_w,
                "acceptance_improved": False,
                "wasserstein_improved": False,
                "decision": decision,
            }
            rows.append(row)
            variants[pool_rule] = {
                **row,
                "mean_acceptance_by_seed": evaluation.get("mean_acceptance_by_seed"),
                "target_sha256": evaluation.get("target_sha256"),
                "pool_sha256": evaluation.get("pool_sha256"),
                "preflight_error": evaluation.get("preflight_error"),
            }
            continue
        row = {
            "site": "JERC",
            "pool_rule": pool_rule,
            "integrity_pass": bool(evaluation["integrity_pass"]),
            "label": evaluation["label"],
            "mean_acceptance": float(evaluation["mean_acceptance"]),
            "max_cross_seed_normalized_wasserstein": float(
                evaluation["max_cross_seed_normalized_wasserstein"]
            ),
            "control_mean_acceptance": control_mean,
            "control_max_cross_seed_normalized_wasserstein": control_w,
            "acceptance_improved": bool(
                evaluation["control_comparison"]["acceptance_improved"]
            ),
            "wasserstein_improved": bool(
                evaluation["control_comparison"]["wasserstein_improved"]
            ),
            "decision": decision,
        }
        rows.append(row)
        variants[pool_rule] = {
            **row,
            "mean_acceptance_by_seed": evaluation["mean_acceptance_by_seed"],
            "target_sha256": evaluation["target_sha256"],
            "pool_sha256": evaluation["pool_sha256"],
        }

    if any(row["decision"] == "repair_supported" for row in rows):
        overall = "repair_supported"
    elif any(row["decision"] == "partial_repair" for row in rows):
        overall = "partial_repair"
    elif any(row["decision"] == "not_supported" for row in rows):
        overall = "not_supported"
    else:
        overall = "geometry_gate_failed"

    payload = {
        "schema": "spinup-forcing-coupling-iter014-aggregate-v1",
        "site": "JERC",
        "control": {
            "path": str(args.control_evaluation),
            "mean_acceptance": control_mean,
            "max_cross_seed_normalized_wasserstein": control_w,
            "note": (
                "Iter012 JERC canonical evaluation reused as diversity-pool control; "
                "no control MCMC rerun."
            ),
        },
        "decision_policy": {
            "repair_supported": (
                "integrity_pass AND mean_acceptance>=0.25 AND "
                "max_cross_seed_normalized_wasserstein<=0.05"
            ),
            "partial_repair": (
                "integrity_pass AND improvement vs control on acceptance and/or "
                "Wasserstein without clearing both repair_supported thresholds"
            ),
            "not_supported": "otherwise for evaluated MCMC variants",
            "geometry_gate_failed": (
                "variant failed locked pool geometry gates before MCMC; counted as "
                "not a mixing repair"
            ),
            "overall": (
                "best available among MCMC-evaluated variants: repair_supported > "
                "partial_repair > not_supported; geometry_gate_failed only if no "
                "MCMC-evaluated variant exists"
            ),
        },
        "variants": variants,
        "overall_decision": overall,
        "status": "pass",
        "summaries_copy_instructions": (
            f"Copy aggregate_result.json, variant_table.csv, and per-rule "
            f"evaluation_result.json files into {args.summary_dir}"
        ),
    }
    temporary = result_path.with_name(result_path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(result_path)

    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.summary_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(result_path, args.summary_dir / "aggregate_result.json")
    shutil.copy2(table_path, args.summary_dir / "variant_table.csv")
    for pool_rule in POOL_RULES:
        src = (
            args.evaluation_root
            / pool_rule
            / "artifacts"
            / "evaluation_result.json"
        )
        if src.is_file():
            shutil.copy2(src, args.summary_dir / f"{pool_rule}_evaluation_result.json")
    summary_src = args.evaluation_root / "evaluation_summary.json"
    if summary_src.is_file():
        shutil.copy2(summary_src, args.summary_dir / "evaluation_summary.json")

    print(f"AGGREGATE_PASS overall_decision={overall}")
    for row in rows:
        if row["decision"] == "geometry_gate_failed":
            print(f"VARIANT pool_rule={row['pool_rule']} decision=geometry_gate_failed")
            continue
        print(
            f"VARIANT pool_rule={row['pool_rule']} decision={row['decision']} "
            f"mean_acc={row['mean_acceptance']:.4f} "
            f"W={row['max_cross_seed_normalized_wasserstein']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
