#!/usr/bin/env python3
"""Validate the locked Iter009 nutrient-diagnostic artifact contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_ROWS = {
    "parameter_metadata.csv": 4,
    "metric_definitions.csv": 47,
    "member_metrics.csv": 400,
    "response_curves.csv": 32560,
    "ratio_support.csv": 4800,
    "observation_summary.csv": 1,
}
EXPECTED_FIGURES = {
    "ABBY_fpi_response.png", "ABBY_microbial_n_response.png", "ABBY_microbial_p_response.png",
    "ABBY_plant_n_response.png", "ABBY_plant_p_response.png", "ABBY_gpp_response.png",
    "ABBY_sr_response.png", "ABBY_hr_mean_response.png", "ABBY_hr_temporal_std_response.png",
    "ABBY_pool_hr_mean_response.png", "ABBY_pool_hr_temporal_std_response.png",
    "ABBY_n_cycle_mean_response.png", "ABBY_n_cycle_temporal_std_response.png",
    "ABBY_p_cycle_mean_response.png", "ABBY_p_cycle_temporal_std_response.png",
    "ABBY_pool_c_mean_response.png", "ABBY_pool_hr_per_c_response.png",
}
POOLS = ("CWDC", "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
POOL_HR = ("CWDC_HR", "LITR1_HR", "LITR2_HR", "LITR3_HR", "SOIL1_HR", "SOIL2_HR", "SOIL3_HR", "SOIL4_HR")
POOL_RATIOS = tuple(f"{name}_per_pool_C" for name in POOL_HR)
SATISFACTION = ("microbial_n_satisfaction", "microbial_p_satisfaction", "plant_n_satisfaction", "plant_p_satisfaction")
RAW_METRICS = (
    "FPI", "FPI_P", "POTENTIAL_IMMOB", "ACTUAL_IMMOB", "POTENTIAL_IMMOB_P", "ACTUAL_IMMOB_P",
    "PLANT_NDEMAND_COL", "SMINN_TO_PLANT", "PLANT_PDEMAND_COL", "SMINP_TO_PLANT", "GPP", "SR", "HR",
    *POOL_HR, *POOLS, "SMINN", "GROSS_NMIN", "NET_NMIN", "SOLUTIONP", "GROSS_PMIN", "NET_PMIN",
)
HEADERS = {
    "parameter_metadata.csv": ["parameter", "pickle_path", "pickle_sha256", "coordinate", "pmin", "pmax", "native_value", "native_status", "selector", "members"],
    "metric_definitions.csv": ["metric", "kind", "numerator", "denominator", "units", "statistics"],
    "member_metrics.csv": [
        "parameter", "member", "parameter_value", "normalized_parameter", "model_hours",
        *[f"{name}_{statistic}" for name in RAW_METRICS for statistic in (("mean",) if name in POOLS else ("mean", "temporal_std"))],
        *[field for name in SATISFACTION + POOL_RATIOS for field in (name, f"{name}_supported", f"{name}_rejection_reason")],
    ],
    "response_curves.csv": ["parameter", "metric", "statistic", "point_type", "member", "bin", "parameter_value", "normalized_parameter", "response", "units", "bin_count", "valid_count", "rejected_count", "bin_x_min", "bin_x_max"],
    "ratio_support.csv": ["parameter", "member", "ratio", "numerator", "denominator", "supported", "rejection_reason", "value"],
    "observation_summary.csv": ["variable", "path", "sha256", "units", "window", "valid_count", "model_window_hours", "coverage_percent_of_model_window", "minimum", "maximum", "mean", "temporal_std"],
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


def csv_header(path: Path) -> list[str]:
    with path.open(newline="") as handle:
        return next(csv.reader(handle))


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
    if input_manifest.get("schema") != "elm_oat_nutrient_input_manifest_v2" or input_manifest.get("status") != "pass":
        raise ValueError("input manifest does not have the passing Iter009 schema")
    if input_manifest.get("parameters") != ["cn_s1", "cn_s2", "cn_s3", "cn_s4"]:
        raise ValueError("input parameter inventory differs")
    if input_manifest.get("pool_c_variables") != list(POOLS) or input_manifest.get("pool_hr_variables") != list(POOL_HR):
        raise ValueError("pool mapping inventory differs")
    observation = input_manifest.get("observation_summary", {})
    if observation.get("variable") != "SR" or observation.get("model_window_hours") != 61320 or observation.get("valid_count", 0) <= 0:
        raise ValueError("SR observation contract differs")
    output_path = args.results / "output_manifest.json"
    if not output_path.is_file():
        raise FileNotFoundError("missing output_manifest.json")
    output = json.loads(output_path.read_text())
    if output.get("schema") != "elm_oat_nutrient_output_manifest_v2" or output.get("status") != "pass":
        raise ValueError("output manifest does not have the passing Iter009 schema")
    if output.get("input_manifest_sha256") != digest(args.input_manifest) or output.get("row_counts") != EXPECTED_ROWS:
        raise ValueError("output manifest input identity or row counts differ")
    if output.get("figure_count") != 17 or set(output.get("figure_names", [])) != EXPECTED_FIGURES:
        raise ValueError("figure contract differs")
    observed_files = {path.name for path in args.results.iterdir() if path.is_file()}
    expected_files = set(EXPECTED_ROWS) | EXPECTED_FIGURES | {"output_manifest.json"}
    if observed_files != expected_files:
        raise ValueError(f"artifact membership differs; missing={sorted(expected_files - observed_files)} extra={sorted(observed_files - expected_files)}")
    if set(output.get("artifacts", {})) != expected_files - {"output_manifest.json"}:
        raise ValueError("output artifact map does not cover the complete payload")
    tables = {name: csv_rows(args.results / name) for name in EXPECTED_ROWS}
    for name, expected in EXPECTED_ROWS.items():
        if csv_header(args.results / name) != HEADERS[name]:
            raise ValueError(f"{name}: exact header contract differs")
        if len(tables[name]) != expected:
            raise ValueError(f"{name}: expected {expected} rows, found {len(tables[name])}")
    if [row["parameter"] for row in tables["parameter_metadata.csv"]] != ["cn_s1", "cn_s2", "cn_s3", "cn_s4"]:
        raise ValueError("parameter metadata order differs")
    definitions = tables["metric_definitions.csv"]
    if len({row["metric"] for row in definitions}) != 47:
        raise ValueError("metric definitions are not unique")
    definition_lookup = {row["metric"]: row for row in definitions}
    if set(definition_lookup) != set(RAW_METRICS + SATISFACTION + POOL_RATIOS):
        raise ValueError("metric definition inventory differs")
    if any(definition_lookup[name]["statistics"] != "mean" for name in POOLS):
        raise ValueError("pool C metrics must be mean-only")
    if any(definition_lookup[name]["kind"] != "realized_pool_respiration_ratio" for name in POOL_RATIOS):
        raise ValueError("pool HR/C definitions differ")
    support = tables["ratio_support.csv"]
    if {row["ratio"] for row in support} != set(SATISFACTION + POOL_RATIOS):
        raise ValueError("ratio support inventory differs")
    support_groups = Counter((row["parameter"], row["ratio"]) for row in support)
    if len(support_groups) != 48 or set(support_groups.values()) != {100}:
        raise ValueError("ratio support multiplicity differs")
    curves = tables["response_curves.csv"]
    endpoints = {(row["metric"], row["statistic"]) for row in curves}
    if len(endpoints) != 74:
        raise ValueError(f"expected 74 response endpoints, found {len(endpoints)}")
    if any((name, "temporal_std") in endpoints for name in POOLS) or any((name, "integrated_ratio") not in endpoints for name in POOL_RATIOS):
        raise ValueError("pool endpoint statistic contract differs")
    endpoint_groups = Counter((row["parameter"], row["metric"], row["statistic"]) for row in curves)
    member_groups = Counter((row["parameter"], row["metric"], row["statistic"]) for row in curves if row["point_type"] == "member")
    bin_groups = Counter((row["parameter"], row["metric"], row["statistic"]) for row in curves if row["point_type"] == "bin_median")
    if len(endpoint_groups) != 296 or set(endpoint_groups.values()) != {110} or set(member_groups.values()) != {100} or set(bin_groups.values()) != {10}:
        raise ValueError("per-parameter endpoint multiplicity differs")
    if {row["point_type"] for row in curves} != {"member", "bin_median"}:
        raise ValueError("response point-type inventory differs")
    for row in curves:
        if row["units"] != definition_lookup[row["metric"]]["units"]:
            raise ValueError(f"response unit differs for {row['metric']}")
    observation_rows = tables["observation_summary.csv"]
    if observation_rows[0]["variable"] != "SR" or int(observation_rows[0]["model_window_hours"]) != 61320:
        raise ValueError("observation summary differs")
    if observation_rows[0]["sha256"] != observation["sha256"] or int(observation_rows[0]["valid_count"]) != observation["valid_count"]:
        raise ValueError("observation summary does not reproduce input manifest")
    for name, evidence in output.get("artifacts", {}).items():
        path = args.results / name
        if not path.is_file() or path.stat().st_size != evidence.get("bytes") or digest(path) != evidence.get("sha256"):
            raise ValueError(f"artifact identity mismatch: {name}")
    print(f"ITER009_ARTIFACT_VALIDATE_PASS rows={sum(EXPECTED_ROWS.values())} figures={len(EXPECTED_FIGURES)} endpoints={len(endpoints)}")


if __name__ == "__main__":
    main()
