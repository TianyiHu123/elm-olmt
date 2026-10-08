#!/usr/bin/env python3
"""Validate the complete Iter005 output package without recomputing diagnostics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
    if input_manifest.get("schema") != "elm_oat_input_manifest_v2" or input_manifest.get("status") != "pass":
        raise ValueError("input manifest is not a passing Iter005 manifest")
    if len(input_manifest.get("parameter_pickles", {})) != 14:
        raise ValueError("input manifest does not contain 14 parameters")
    output_manifest = json.loads((args.results / "output_manifest.json").read_text())
    if output_manifest.get("schema") != "elm_oat_output_manifest_v2" or output_manifest.get("status") != "pass":
        raise ValueError("output manifest is not a passing Iter005 manifest")
    if output_manifest.get("input_manifest_sha256") != digest(args.input_manifest):
        raise ValueError("output manifest does not identify the supplied input manifest")
    observed_rows = {name: row_count(args.results / name) for name in EXPECTED_ROWS}
    if observed_rows != EXPECTED_ROWS or output_manifest.get("row_counts") != EXPECTED_ROWS:
        raise ValueError(f"row-count mismatch: {observed_rows}")
    figures = sorted(args.results.glob("*.png"))
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
    print(f"ITER005_ARTIFACT_VALIDATE_PASS rows={sum(observed_rows.values())} figures=44")


if __name__ == "__main__":
    main()
