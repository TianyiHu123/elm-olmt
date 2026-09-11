#!/usr/bin/env python3
"""Validate the complete Iter006 output package without recomputing diagnostics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

EXPECTED_ROWS = {
    "parameter_metadata.csv": 14,
    "member_metrics.csv": 1400,
    "sensitivity_scores.csv": 364,
    "response_curves.csv": 40040,
    "observation_summary.csv": 1,
    "hr_pathway_metrics.csv": 37800,
    "hr_pathway_curves.csv": 420,
    "litter_ratio_member_metrics.csv": 5600,
    "litter_ratio_timeseries.csv": 3433920,
    "litter_ratio_curves.csv": 560,
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    args = parser.parse_args()
    input_manifest = json.loads(args.input_manifest.read_text())
    if input_manifest.get("schema") != "elm_oat_input_manifest_v4" or input_manifest.get("status") != "pass":
        raise ValueError("input manifest is not a passing Iter006 manifest")
    if input_manifest.get("site") != "JERC":
        raise ValueError("input manifest site is not JERC")
    if len(input_manifest.get("parameter_pickles", {})) != 14:
        raise ValueError("input manifest does not contain 14 parameters")
    output_manifest = json.loads((args.results / "output_manifest.json").read_text())
    if output_manifest.get("schema") != "elm_oat_output_manifest_v4" or output_manifest.get("status") != "pass":
        raise ValueError("output manifest is not a passing Iter006 manifest")
    if output_manifest.get("site") != "JERC":
        raise ValueError("output manifest site is not JERC")
    if output_manifest.get("input_manifest_sha256") != digest(args.input_manifest):
        raise ValueError("output manifest does not identify the supplied input manifest")
    observed_rows = {name: row_count(args.results / name) for name in EXPECTED_ROWS}
    if observed_rows != EXPECTED_ROWS or output_manifest.get("row_counts") != EXPECTED_ROWS:
        raise ValueError(f"row-count mismatch: {observed_rows}")
    approved_reasons = {
        "nonfinite_carbon_total",
        "nonfinite_nutrient_total",
        "nonfinite_carbon_and_nutrient_totals",
        "nonpositive_nutrient_total",
    }
    member_support = defaultdict(lambda: {"declared": 0, "valid": 0, "rejected": 0})
    with (args.results / "litter_ratio_member_metrics.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("supported") not in {"True", "False"}:
                raise ValueError("litter member supported must be exactly True or False")
            supported = row["supported"] == "True"
            reason = row.get("rejection_reason", "")
            ratio = row.get("ratio_value", "")
            if supported:
                if reason or not ratio or not math.isfinite(float(ratio)):
                    raise ValueError("supported litter member lacks a finite ratio or has a rejection reason")
            elif ratio or reason not in approved_reasons:
                raise ValueError("unsupported litter member must be a gap with one approved rejection reason")
            key = (row["parameter"], row["ratio"])
            member_support[key]["declared"] += 1
            member_support[key]["valid" if supported else "rejected"] += 1
    if len(member_support) != 56 or any(item["declared"] != 100 for item in member_support.values()):
        raise ValueError("litter member support does not cover 14 parameters x 4 ratios x 100 members")
    curve_support = defaultdict(lambda: {"bins": 0, "declared": 0, "valid": 0, "rejected": 0})
    with (args.results / "litter_ratio_curves.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            declared = int(row["count"])
            valid = int(row["valid_count"])
            rejected = int(row["rejected_count"])
            if valid + rejected != declared:
                raise ValueError("litter curve support counts do not sum to declared count")
            if bool(row["response_median"]) != (valid > 0):
                raise ValueError("litter curve response gap disagrees with valid support")
            if row["response_median"] and not math.isfinite(float(row["response_median"])):
                raise ValueError("litter curve supported median is not finite")
            key = (row["parameter"], row["ratio"])
            curve_support[key]["bins"] += 1
            curve_support[key]["declared"] += declared
            curve_support[key]["valid"] += valid
            curve_support[key]["rejected"] += rejected
    if set(curve_support) != set(member_support):
        raise ValueError("litter curve and member support groups differ")
    for key, counts in member_support.items():
        if curve_support[key] != {"bins": 10, **counts}:
            raise ValueError(f"litter curve/member support totals differ for {key}")
        parameter, ratio = key
        manifest_counts = input_manifest.get("cases", {}).get(parameter, {}).get("litter_ratio_support", {}).get(ratio)
        if manifest_counts != {"supported_members": counts["valid"], "rejected_members": counts["rejected"]}:
            raise ValueError(f"litter manifest/member support totals differ for {key}")
    figures = sorted(args.results.glob("*.png"))
    if any(not path.name.startswith("JERC_") for path in figures):
        raise ValueError("every figure must have a JERC_ prefix")
    if len(figures) != 44 or output_manifest.get("figure_count") != 44:
        raise ValueError(f"expected 44 PNGs, found {len(figures)}")
    expected_names = set(output_manifest.get("artifacts", {}))
    observed_names = {path.name for path in args.results.iterdir() if path.is_file() and path.name != "output_manifest.json"}
    if expected_names != observed_names:
        raise ValueError("output manifest artifact membership mismatch")
    for name, metadata in output_manifest["artifacts"].items():
        path = args.results / name
        if path.stat().st_size != int(metadata["bytes"]) or digest(path) != metadata["sha256"]:
            raise ValueError(f"artifact identity mismatch: {name}")
    for name, expected_hash in input_manifest["regression_sha256"].items():
        if digest(args.results / name) != expected_hash:
            raise ValueError(f"core regression mismatch: {name}")
    print(f"ITER006_ARTIFACT_VALIDATE_PASS rows={sum(observed_rows.values())} figures=44")


if __name__ == "__main__":
    main()
