#!/usr/bin/env python3
"""Write an auditable Iter018 cross-site report inventory."""
from __future__ import annotations
import argparse
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
        root = args.root / "sites" / site.lower()
        report = root / "reports" / "report_manifest.json"
        if not report.is_file():
            raise FileNotFoundError(report)
        payload = json.loads(report.read_text())
        names = {item.name for item in (root / "optimization").glob("seed_*")}
        if names != SEEDS:
            raise ValueError(f"unexpected seed set for {site}: {sorted(names)}")
        retained = payload.get("retained_tier_a_seeds") or []
        rows.append({
            "site": site,
            "status": payload.get("status"),
            "leaves": len(names),
            "retained_tier_a": len(retained),
            "retained_tier_a_seeds": list(retained),
        })
    destination = args.root / "aggregate" / "iter018_operational_summary.json"
    destination.write_text(json.dumps({"schema": "iter018-operational-v2", "sites": rows}, indent=2) + "\n")
    print("ITER018_AGGREGATE_PASS sites=9 leaves=81")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
