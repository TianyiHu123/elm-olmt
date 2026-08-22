#!/usr/bin/env python3
"""Validate complete Iter018 site reports and write the final handoff receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SITES = ("ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for site in SITES:
        path = args.root / "sites" / site.lower()
        report = path / "reports" / "report_manifest.json"
        table = path / "reports" / "best_parameters" / "parameter_sets.csv"
        nc_files = sorted((path / "reports" / "best_parameters" / "clm_params").glob("clm_params_seed_*.nc"))
        leaves = sorted((path / "optimization").glob("seed_*"))
        if not report.is_file() or not table.is_file() or len(leaves) != 9 or len(nc_files) != 9:
            raise ValueError(f"incomplete site package: {site}")
        payload = json.loads(report.read_text())
        if payload.get("status") not in {"pass", "insufficient_retained"}:
            raise ValueError(f"unrecognized report status for {site}: {payload.get('status')}")
        rows.append({"site": site, "status": payload["status"], "seed_leaves": len(leaves)})
    aggregate = args.root / "aggregate" / "iter018_operational_summary.json"
    if not aggregate.is_file():
        raise FileNotFoundError(aggregate)
    destination = args.root / "handoff" / "handoff_validation.json"
    destination.write_text(json.dumps({"schema": "iter018-handoff-v1", "sites": rows}, indent=2) + "\n")
    print("ITER018_HANDOFF_PASS sites=9 leaves=81")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
