#!/usr/bin/env python3
"""Validate the locked Iter008 nutrient-diagnostic artifact contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_ROWS = {
    "parameter_metadata.csv": 4,
    "metric_definitions.csv": 31,
    "member_metrics.csv": 400,
    "response_curves.csv": 25520,
    "ratio_support.csv": 1600,
}
EXPECTED_FIGURES = {
    "ABBY_fpi_response.png", "ABBY_microbial_n_response.png", "ABBY_microbial_p_response.png",
    "ABBY_plant_n_response.png", "ABBY_plant_p_response.png", "ABBY_gpp_response.png",
    "ABBY_sr_response.png", "ABBY_hr_response.png", "ABBY_pool_hr_response.png",
    "ABBY_n_cycle_response.png", "ABBY_p_cycle_response.png",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    args = parser.parse_args()
    if not args.input_manifest.is_absolute() or not args.input_manifest.is_file():
        raise ValueError("--input-manifest must be an existing absolute file")
    if not args.results.is_absolute() or not args.results.is_dir():
        raise ValueError("--results must be an existing absolute directory")
    input_manifest = json.loads(args.input_manifest.read_text())
    if input_manifest.get("schema") != "elm_oat_nutrient_input_manifest_v1" or input_manifest.get("status") != "pass":
        raise ValueError("input manifest does not have the passing Iter008 schema")
    if input_manifest.get("parameters") != ["cn_s1", "cn_s2", "cn_s3", "cn_s4"]:
        raise ValueError("input parameter inventory differs from the locked order")
    output_path = args.results / "output_manifest.json"
    if not output_path.is_file():
        raise FileNotFoundError("missing output_manifest.json")
    output = json.loads(output_path.read_text())
    if output.get("schema") != "elm_oat_nutrient_output_manifest_v1" or output.get("status") != "pass":
        raise ValueError("output manifest does not have the passing Iter008 schema")
    if output.get("input_manifest_sha256") != digest(args.input_manifest):
        raise ValueError("output manifest does not pin the supplied input manifest")
    if output.get("row_counts") != EXPECTED_ROWS:
        raise ValueError(f"manifest row counts differ: {output.get('row_counts')}")
    if output.get("figure_count") != 11 or set(output.get("figure_names", [])) != EXPECTED_FIGURES:
        raise ValueError("manifest figure contract differs")
    observed_files = {path.name for path in args.results.iterdir() if path.is_file()}
    expected_files = set(EXPECTED_ROWS) | EXPECTED_FIGURES | {"output_manifest.json"}
    if observed_files != expected_files:
        raise ValueError(f"artifact membership differs; missing={sorted(expected_files - observed_files)} extra={sorted(observed_files - expected_files)}")
    expected_payload = expected_files - {"output_manifest.json"}
    if set(output.get("artifacts", {})) != expected_payload:
        raise ValueError("output manifest artifact map does not cover the complete payload")
    for name, expected in EXPECTED_ROWS.items():
        rows = csv_rows(args.results / name)
        if len(rows) != expected:
            raise ValueError(f"{name}: expected {expected} rows, found {len(rows)}")
    parameters = csv_rows(args.results / "parameter_metadata.csv")
    if [row["parameter"] for row in parameters] != ["cn_s1", "cn_s2", "cn_s3", "cn_s4"]:
        raise ValueError("parameter metadata order differs")
    definitions = csv_rows(args.results / "metric_definitions.csv")
    if len({row["metric"] for row in definitions}) != 31:
        raise ValueError("metric definitions are not unique")
    support = csv_rows(args.results / "ratio_support.csv")
    if {row["ratio"] for row in support} != {"microbial_n_satisfaction", "microbial_p_satisfaction", "plant_n_satisfaction", "plant_p_satisfaction"}:
        raise ValueError("ratio support labels differ")
    curves = csv_rows(args.results / "response_curves.csv")
    if {row["statistic"] for row in curves} != {"mean", "temporal_std", "integrated_ratio"}:
        raise ValueError("response statistic inventory differs")
    for name, evidence in output.get("artifacts", {}).items():
        path = args.results / name
        if not path.is_file() or path.stat().st_size != evidence.get("bytes") or digest(path) != evidence.get("sha256"):
            raise ValueError(f"artifact identity mismatch: {name}")
    total = sum(EXPECTED_ROWS.values())
    print(f"ITER008_ARTIFACT_VALIDATE_PASS rows={total} figures={len(EXPECTED_FIGURES)}")


if __name__ == "__main__":
    main()
