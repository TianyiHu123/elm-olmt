#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def _summary(values: List[float]) -> Dict[str, Any]:
    arr = np.asarray(values, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "min": None,
            "max": None,
            "p25": None,
            "p75": None,
        }
    return {
        "count": int(arr.size),
        "mean": float(np.nanmean(arr)),
        "median": float(np.nanmedian(arr)),
        "std": float(np.nanstd(arr)),
        "min": float(np.nanmin(arr)),
        "max": float(np.nanmax(arr)),
        "p25": float(np.nanpercentile(arr, 25)),
        "p75": float(np.nanpercentile(arr, 75)),
    }


def _extract_seed(path: Path) -> int | None:
    m = re.search(r"seed(\d+)", path.name)
    if m:
        return int(m.group(1))
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate surrogate_spinup_stats_*.json outputs")
    parser.add_argument("--stats-dir", required=True, help="Directory containing surrogate_spinup_stats_*.json files")
    parser.add_argument("--glob", default="surrogate_spinup_stats_seed*.json", help="Glob pattern under --stats-dir")
    parser.add_argument("--output-json", default=None, help="Optional output JSON path")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    stats_dir = Path(args.stats_dir).expanduser().resolve()
    files = sorted([p for p in stats_dir.glob(args.glob) if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No files found with pattern '{args.glob}' under {stats_dir}")

    per_var: Dict[str, Dict[str, List[float]]] = {}
    warning_counts: Dict[str, int] = {}
    seeds: List[int] = []
    metadata: Dict[str, Any] = {}

    metric_keys = ("r2_train", "r2_val", "r2_gap", "rmse_train", "rmse_val", "rmse_ratio")
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        metadata = {
            "model_type": payload.get("model_type"),
            "split_mode": payload.get("split_mode"),
            "train_fraction": payload.get("train_fraction"),
            "output_label": payload.get("output_label"),
            "case_names": payload.get("case_names"),
        }
        maybe_seed = _extract_seed(path)
        if maybe_seed is not None:
            seeds.append(maybe_seed)
        by_var = payload.get("by_variable", {})
        for var, dct in by_var.items():
            if var not in per_var:
                per_var[var] = {k: [] for k in metric_keys}
                warning_counts[var] = 0
            for key in metric_keys:
                per_var[var][key].append(float(dct.get(key, np.nan)))
            if bool(dct.get("overfit_warning", False)):
                warning_counts[var] += 1

    summary: Dict[str, Any] = {
        "stats_dir": str(stats_dir),
        "file_count": int(len(files)),
        "seed_count": int(len(seeds)),
        "seed_min": int(min(seeds)) if seeds else None,
        "seed_max": int(max(seeds)) if seeds else None,
        "metadata": metadata,
        "by_variable": {},
    }
    for var, metrics in per_var.items():
        var_summary: Dict[str, Any] = {}
        for key, values in metrics.items():
            var_summary[key] = _summary(values)
        var_summary["overfit_warning_fraction"] = float(warning_counts[var] / len(files))
        summary["by_variable"][var] = var_summary

    text = json.dumps(summary, indent=2, allow_nan=False)
    if args.output_json:
        outpath = Path(args.output_json).expanduser().resolve()
        outpath.write_text(text, encoding="utf-8")
        print(f"Wrote summary JSON: {outpath}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
