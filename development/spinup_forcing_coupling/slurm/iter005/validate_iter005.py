#!/usr/bin/env python3
"""Aggregate Iter005 full products and write joined summary evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

METRIC_KEYS = ["r2", "rmse", "bias", "mae", "pearson_r", "kge"]
NEW_ARM = "offline_mean_spinup"
ITER004_ARMS = ["offline", "drop32", "drop21_corr080"]
ALL_ARMS = [NEW_ARM, *ITER004_ARMS]
SITES = ["ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL"]
PLOT_KEYS = ["timeseries", "sr_vs_member"]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    parser.add_argument("--iter004-medians-csv", required=True)
    args = parser.parse_args()
    full_dir = Path(args.full_dir)
    summary_root = Path(args.summary_root)
    summary_root.mkdir(parents=True, exist_ok=True)
    iter004_medians_path = Path(args.iter004_medians_csv)
    iter004_rows = _read_csv(iter004_medians_path)
    iter004_lookup = {(r["site"], r["arm"]): r for r in iter004_rows}

    full_rows: List[Dict[str, str]] = []
    site_medians: Dict[str, Dict[str, Dict[str, float]]] = {}
    for idx, site in enumerate(SITES, start=1):
        leaf = full_dir / "results" / f"site_{idx}"
        summary = _load_json(leaf / f"full_site{idx}_summary.json")
        if not summary.get("save_timeseries"):
            raise ValueError(f"Full leaf {idx} must have save_timeseries=true")
        rows = _read_csv(Path(summary["member_metrics_csv"]))
        if len(rows) != 100:
            raise ValueError(f"Full leaf {idx} expected 100 mean-spinup rows, got {len(rows)}")
        if any(r["arm"] != NEW_ARM for r in rows):
            raise ValueError(f"Full leaf {idx} has unexpected arm labels")
        full_rows.extend(rows)
        site_entry = summary["sites"][0]
        if site_entry["site"] != site:
            raise ValueError(f"Site mismatch leaf {idx}: {site_entry['site']} != {site}")
        for plot_key in PLOT_KEYS:
            plot_path = Path(site_entry["plots"][plot_key])
            if not plot_path.is_file():
                raise FileNotFoundError(f"Missing plot {plot_key}: {plot_path}")
        ts = Path(site_entry["timeseries"])
        if not ts.is_file():
            raise FileNotFoundError(f"Missing timeseries: {ts}")

        site_medians[site] = {}
        new_med = site_entry["metric_medians"][NEW_ARM]
        site_medians[site][NEW_ARM] = {k: float(new_med[k]) for k in METRIC_KEYS}
        for arm in ITER004_ARMS:
            key = (site, arm)
            if key not in iter004_lookup:
                raise KeyError(f"Missing Iter004 median {key}")
            # Prefer medians embedded in leaf summary (already joined at eval), but
            # cross-check against locked Iter004 CSV.
            leaf_med = site_entry["metric_medians"][arm]
            locked = iter004_lookup[key]
            for k in METRIC_KEYS:
                if abs(float(leaf_med[k]) - float(locked[k])) > 1e-12:
                    raise ValueError(
                        f"Leaf/Iter004 median drift site={site} arm={arm} key={k}"
                    )
            site_medians[site][arm] = {k: float(locked[k]) for k in METRIC_KEYS}

    summary_csv = summary_root / "iter005_site_metric_medians.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["site", "arm", *METRIC_KEYS])
        for site in SITES:
            for arm in ALL_ARMS:
                med = site_medians[site][arm]
                writer.writerow([site, arm, *[med[k] for k in METRIC_KEYS]])

    decision = {
        "schema": "spinup-forcing-coupling-iter005-decision-v1",
        "iteration_id": "iter005",
        "passed": True,
        "full_member_rows": len(full_rows),
        "sites": SITES,
        "arms": ALL_ARMS,
        "new_arm": NEW_ARM,
        "site_metric_medians_csv": str(summary_csv),
        "notes": (
            "Functional/integrity validation only; metric values are characterization. "
            "New arm = forcing-v1 + mean ELM restart spinup; Iter004 arms joined read-only."
        ),
    }
    decision_path = summary_root / "iter005_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATE_PASS sites=9 full_rows={len(full_rows)} decision={decision_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
