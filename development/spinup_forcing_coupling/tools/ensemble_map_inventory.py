#!/usr/bin/env python3
"""Extract MAP inventory for Tier-A-healthy seeds."""
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

from ensemble_common import DEFAULT_SEEDS, SITE_CONFIG, load_leaf, tier_a_result  # noqa: E402

SCHEMA = "spinup-forcing-coupling-ensemble-map-inventory-v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--site", choices=sorted(SITE_CONFIG), required=True)
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    entries: list[dict[str, Any]] = []
    for seed in args.seeds:
        leaf = load_leaf(args.root, args.site, seed)
        passed, reason = tier_a_result(leaf["mean_acceptance"], leaf["campaign_pass"])
        entry: dict[str, Any] = {
            "site": args.site,
            "seed": seed,
            "tier_a_pass": passed,
            "tier_a_reason": reason,
            "mean_acceptance": leaf["mean_acceptance"],
            "map_log_posterior": leaf["map_log_posterior"],
            "map_rmse": leaf["map_rmse"],
            "map_bias": leaf["map_bias"],
            "map_r2": leaf["map_r2"],
            "elm_rmse": leaf["elm_rmse"],
            "elm_bias": leaf["elm_bias"],
            "elm_r2": leaf["elm_r2"],
            "leaf": str(leaf["leaf"]),
        }
        if passed:
            entry["parameter_names"] = leaf["parameter_names"]
            entry["map_state"] = leaf["map_state"].tolist()
        entries.append(entry)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "map_inventory.json"
    csv_path = args.output_dir / "map_inventory.csv"
    if json_path.exists() and not args.overwrite:
        raise FileExistsError(json_path)
    payload = {"schema": SCHEMA, "site": args.site, "entries": entries}
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    csv_rows = []
    for entry in entries:
        row = {k: v for k, v in entry.items() if k not in {"parameter_names", "map_state"}}
        csv_rows.append(row)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    retained = sum(1 for entry in entries if entry["tier_a_pass"])
    print(f"MAP_INVENTORY_PASS site={args.site} retained={retained} total={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
