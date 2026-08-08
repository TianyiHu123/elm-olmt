#!/usr/bin/env python3
"""Iter007 validate: campaign product layout + suggested diagnostics integrity."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_FILES = [
    "best_params.txt",
    "clm_params_best.nc",
    "plots/corner/corner_plot.png",
    "plots/predictions/ABBY/Predictions_SR_posterior.png",
    "plots/predictions/JERC/Predictions_SR_posterior.png",
    "diagnostics/diagnostics_index.json",
    "diagnostics/collocation_audit.csv",
    "diagnostics/chain_health.json",
    "diagnostics/skill_table.csv",
    "diagnostics/delta_logL.csv",
    "diagnostics/residual_summary.csv",
    "diagnostics/posterior_summary.csv",
    "diagnostics/prior_edge_occupancy.csv",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-run-dir", required=True)
    parser.add_argument("--campaign-run-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    args = parser.parse_args()

    campaign = Path(args.campaign_run_dir)
    summary = Path(args.summary_root)
    summary.mkdir(parents=True, exist_ok=True)

    missing = []
    for rel in REQUIRED_FILES:
        path = campaign / rel
        if not path.is_file():
            missing.append(str(path))
    pdf_dir = campaign / "plots" / "pdfs"
    if not pdf_dir.is_dir() or not any(pdf_dir.glob("*.png")):
        missing.append(str(pdf_dir / "*.png"))
    if missing:
        raise FileNotFoundError("Missing required campaign products:\n" + "\n".join(missing))

    # Fail closed: no UQ_output nesting under campaign root.
    uq = campaign / "UQ_output"
    if uq.exists():
        raise AssertionError(f"Unexpected UQ_output under campaign root: {uq}")

    index = json.loads((campaign / "diagnostics" / "diagnostics_index.json").read_text())
    chain = json.loads((campaign / "diagnostics" / "chain_health.json").read_text())

    accounting_rows = [
        {
            "work_unit": "campaign",
            "product_root": str(campaign),
            "best_params": str(campaign / "best_params.txt"),
            "clm_params_best": str(campaign / "clm_params_best.nc"),
            "diagnostics_index": str(campaign / "diagnostics" / "diagnostics_index.json"),
            "mean_acceptance_fraction": chain.get("mean_acceptance_fraction"),
            "approx_ess": chain.get("approx_ess"),
            "gate_result": "pass",
        }
    ]
    accounting_path = summary / "iter007_accounting.csv"
    with accounting_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(accounting_rows[0].keys()))
        writer.writeheader()
        writer.writerows(accounting_rows)

    decision = {
        "schema": "spinup-forcing-coupling-iter007-decision-v1",
        "iteration_id": "iter007",
        "status": "completed",
        "work_type": "implementation",
        "objective": (
            "Joint ABBY+JERC coupled/drop21_corr080 SR MCMC campaign"
        ),
        "bounded_scope": (
            "ABBY+JERC joint; coupled drop21_corr080; SR; 64x500; flat campaign layout; "
            "suggested diagnostics; integrity-only"
        ),
        "acceptance_result": "pass",
        "decision": (
            "Joint ABBY+JERC production MCMC campaign executed successfully through the "
            "locked coupled interface and wrote required products; diagnostic contents are "
            "characterization only; calibrated scientific adequacy not claimed"
        ),
        "campaign_run_dir": str(campaign),
        "diagnostics_files": index.get("files"),
        "chain_health": chain,
        "output_root": str(campaign.parent),
        "summary_path": "development/spinup_forcing_coupling/summaries/iter007",
        "passed": True,
        "notes": "Integrity validation only; no numeric skill floors.",
    }
    decision_path = summary / "iter007_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    # Copy compact diagnostics pointers into summary.
    for name in [
        "collocation_audit.csv",
        "skill_table.csv",
        "delta_logL.csv",
        "chain_health.json",
        "posterior_summary.csv",
    ]:
        src = campaign / "diagnostics" / name
        dst = summary / f"iter007_{name}"
        dst.write_bytes(src.read_bytes())

    print(f"VALIDATE_PASS accounting={accounting_path} decision={decision_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
