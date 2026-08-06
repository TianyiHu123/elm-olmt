#!/usr/bin/env python3
"""Aggregate Iter003 pilot/full products and write compact summary evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

METRIC_KEYS = ["r2", "rmse", "bias", "mae", "pearson_r", "kge"]
VARIANTS = ["drop32", "drop21_corr080"]
SITES = ["ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL"]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--full-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    args = parser.parse_args()
    pilot_dir = Path(args.pilot_dir)
    full_dir = Path(args.full_dir)
    summary_root = Path(args.summary_root)
    summary_root.mkdir(parents=True, exist_ok=True)

    pilot_summary = _load_json(pilot_dir / "results" / "pilot_summary.json")
    if not pilot_summary.get("save_timeseries"):
        raise ValueError("Pilot must have save_timeseries=true")
    pilot_csv = Path(pilot_summary["member_metrics_csv"])
    if not pilot_csv.is_file():
        raise FileNotFoundError(pilot_csv)
    pilot_rows = _read_csv(pilot_csv)
    if len(pilot_rows) != 5 * 2:
        raise ValueError(f"Pilot expected 10 member-rows, got {len(pilot_rows)}")

    full_rows: List[Dict[str, str]] = []
    site_medians: Dict[str, Dict[str, Dict[str, float]]] = {}
    for idx, site in enumerate(SITES, start=1):
        leaf = full_dir / "results" / f"site_{idx}"
        summary = _load_json(leaf / f"full_site{idx}_summary.json")
        if summary.get("save_timeseries"):
            raise ValueError(f"Full leaf {idx} must have save_timeseries=false")
        rows = _read_csv(Path(summary["member_metrics_csv"]))
        if len(rows) != 100 * 2:
            raise ValueError(f"Full leaf {idx} expected 200 rows, got {len(rows)}")
        full_rows.extend(rows)
        site_entry = summary["sites"][0]
        if site_entry["site"] != site:
            raise ValueError(f"Site mismatch leaf {idx}: {site_entry['site']} != {site}")
        site_medians[site] = {}
        for variant in VARIANTS:
            med = site_entry["variants"][variant]["metric_medians"]
            site_medians[site][variant] = {k: float(med[k]) for k in METRIC_KEYS}
            for plot_key, plot_path in site_entry["variants"][variant]["plots"].items():
                if not Path(plot_path).is_file():
                    raise FileNotFoundError(f"Missing plot {plot_key}: {plot_path}")

    # Write compact per-site median summary table
    summary_csv = summary_root / "iter003_site_metric_medians.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["site", "variant", *METRIC_KEYS])
        for site in SITES:
            for variant in VARIANTS:
                med = site_medians[site][variant]
                writer.writerow([site, variant, *[med[k] for k in METRIC_KEYS]])

    decision = {
        "schema": "spinup-forcing-coupling-iter003-decision-v1",
        "iteration_id": "iter003",
        "passed": True,
        "pilot_member_rows": len(pilot_rows),
        "full_member_rows": len(full_rows),
        "sites": SITES,
        "variants": VARIANTS,
        "site_metric_medians_csv": str(summary_csv),
        "notes": (
            "Functional/integrity validation only; metric values are characterization. "
            "Summary reports per-site medians over members."
        ),
    }
    decision_path = summary_root / "iter003_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATE_PASS sites=9 full_rows={len(full_rows)} decision={decision_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
