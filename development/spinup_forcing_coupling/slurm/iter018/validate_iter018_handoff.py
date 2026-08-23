#!/usr/bin/env python3
"""Validate complete Iter018 site reports and write the final handoff receipt."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

SITES = ("ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL")
SEEDS = {f"seed_{seed}" for seed in range(9009, 9018)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for site in SITES:
        path = args.root / "sites" / site.lower()
        report = path / "reports" / "report_manifest.json"
        table = path / "reports" / "best_parameters" / "parameter_sets.csv"
        audit = path / "reports" / "best_parameters" / "all_seed_parameter_sets.csv"
        nc_dir = path / "reports" / "best_parameters" / "clm_params"
        nc_files = sorted(nc_dir.glob("clm_params_seed_*.nc")) if nc_dir.is_dir() else []
        leaves = sorted((path / "optimization").glob("seed_*"))
        if not report.is_file() or not table.is_file() or not audit.is_file():
            raise ValueError(f"incomplete site package: {site}")
        if {item.name for item in leaves} != SEEDS:
            raise ValueError(f"incomplete site package: {site}")
        payload = json.loads(report.read_text())
        if payload.get("status") not in {"pass", "insufficient_retained"}:
            raise ValueError(f"unrecognized report status for {site}: {payload.get('status')}")
        retained = [str(seed) for seed in payload.get("retained_tier_a_seeds", [])]
        with table.open(encoding="utf-8") as handle:
            table_seeds = [row["seed"] for row in csv.DictReader(handle)]
        if table_seeds != retained:
            raise ValueError(
                f"{site}: parameter_sets.csv seeds {table_seeds} != retained Tier-A {retained}"
            )
        expected_nc = {f"clm_params_seed_{seed}.nc" for seed in retained}
        actual_nc = {item.name for item in nc_files}
        if actual_nc != expected_nc:
            raise ValueError(
                f"{site}: clm_params {sorted(actual_nc)} != expected Tier-A {sorted(expected_nc)}"
            )
        if retained:
            for retained_site in [str(value).upper() for value in payload.get("sites", [site])]:
                overlay = (
                    path / "reports" / "plots" / "predictions" / retained_site
                    / "Predictions_SR_MAP_ensemble.png"
                )
                if not overlay.is_file():
                    raise FileNotFoundError(overlay)
            corner = path / "reports" / "plots" / "physical_corner.png"
            if not corner.is_file():
                raise FileNotFoundError(corner)
        rows.append({
            "site": site,
            "status": payload["status"],
            "seed_leaves": len(leaves),
            "retained_tier_a": len(retained),
        })
    aggregate = args.root / "aggregate" / "iter018_operational_summary.json"
    if not aggregate.is_file():
        raise FileNotFoundError(aggregate)
    destination = args.root / "handoff" / "handoff_validation.json"
    destination.write_text(json.dumps({"schema": "iter018-handoff-v2", "sites": rows}, indent=2) + "\n")
    print("ITER018_HANDOFF_PASS sites=9 leaves=81")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
