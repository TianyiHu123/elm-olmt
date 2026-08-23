#!/usr/bin/env python3
"""Aggregate Iter004 full products and write compact summary evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

METRIC_KEYS = ["r2", "rmse", "bias", "mae", "pearson_r", "kge"]
ARMS = ["offline", "drop32", "drop21_corr080"]
SITES = ["ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL"]
PLOT_KEYS = ["timeseries", "sr_vs_member", "sr_vs_totsomc", "sr_vs_totsomn"]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    args = parser.parse_args()
    full_dir = Path(args.full_dir)
    summary_root = Path(args.summary_root)
    summary_root.mkdir(parents=True, exist_ok=True)

    full_rows: List[Dict[str, str]] = []
    site_medians: Dict[str, Dict[str, Dict[str, float]]] = {}
    for idx, site in enumerate(SITES, start=1):
        leaf = full_dir / "results" / f"site_{idx}"
        summary = _load_json(leaf / f"full_site{idx}_summary.json")
        if not summary.get("save_timeseries"):
            raise ValueError(f"Full leaf {idx} must have save_timeseries=true")
        rows = _read_csv(Path(summary["member_metrics_csv"]))
        if len(rows) != 100 * 3:
            raise ValueError(f"Full leaf {idx} expected 300 rows, got {len(rows)}")
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
        for arm in ARMS:
            med = site_entry["metric_medians"][arm]
            site_medians[site][arm] = {k: float(med[k]) for k in METRIC_KEYS}

    summary_csv = summary_root / "iter004_site_metric_medians.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["site", "arm", *METRIC_KEYS])
        for site in SITES:
            for arm in ARMS:
                med = site_medians[site][arm]
                writer.writerow([site, arm, *[med[k] for k in METRIC_KEYS]])

    decision = {
        "schema": "spinup-forcing-coupling-iter004-decision-v1",
        "iteration_id": "iter004",
        "passed": True,
        "full_member_rows": len(full_rows),
        "sites": SITES,
        "arms": ARMS,
        "site_metric_medians_csv": str(summary_csv),
        "notes": (
            "Functional/integrity validation only; metric values are characterization. "
            "Offline = forcing-v1 + ELM restart; coupled = drop32 and drop21_corr080."
        ),
    }
    decision_path = summary_root / "iter004_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATE_PASS sites=9 full_rows={len(full_rows)} decision={decision_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
