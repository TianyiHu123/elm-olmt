#!/usr/bin/env python3
"""Tier-A seed health filter for MAP ensemble workflows."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from ensemble_common import (  # noqa: E402
    DEFAULT_SEEDS,
    SITE_CONFIG,
    load_leaf,
    tier_a_result,
)

SCHEMA = "spinup-forcing-coupling-ensemble-seed-health-v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", choices=sorted(SITE_CONFIG), required=True)
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for seed in args.seeds:
        leaf = load_leaf(args.root, args.site, seed)
        passed, reason = tier_a_result(leaf["mean_acceptance"], leaf["campaign_pass"])
        rows.append(
            {
                "schema": SCHEMA,
                "site": args.site,
                "seed": seed,
                "resolution": leaf["resolution"],
                "de_scale": leaf["de_scale"],
                "leaf": str(leaf["leaf"]),
                "mean_acceptance": leaf["mean_acceptance"],
                "saturation": leaf["saturation"],
                "min_steps_per_tau": leaf["min_steps_per_tau"],
                "max_tau_change": leaf["max_tau_change"],
                "tier_a_pass": passed,
                "tier_a_reason": reason,
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "seed_health.json"
    csv_path = args.output_dir / "seed_health.csv"
    if json_path.exists() and not args.overwrite:
        raise FileExistsError(json_path)
    payload = {"schema": SCHEMA, "site": args.site, "seeds": rows}
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    retained = sum(1 for row in rows if row["tier_a_pass"])
    print(f"SEED_HEALTH_PASS site={args.site} retained={retained} total={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
