#!/usr/bin/env python3
"""Validate the complete Iter007 output package without recomputing diagnostics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

PARAMETERS = (
    "act25", "br_mr", "decomp_depth_efolding", "grperc", "k_l1", "k_l2", "k_l3",
    "k_s1", "k_s2", "k_s3", "k_s4", "leaf_long", "q10_mr",
)
PARAMETER_PICKLES = {
    "act25": "ABBY_ctrlvertcact25_I20TRCNPRDCTCBC.pkl",
    "br_mr": "ABBY_ctrlvertcbrmr_I20TRCNPRDCTCBC.pkl",
    "decomp_depth_efolding": "ABBY_ctrlvertcdepthefold_I20TRCNPRDCTCBC.pkl",
    "grperc": "ABBY_ctrlvertcgrperc_I20TRCNPRDCTCBC.pkl",
    "k_l1": "ABBY_ctrlvertckl1_I20TRCNPRDCTCBC.pkl",
    "k_l2": "ABBY_ctrlvertckl2_I20TRCNPRDCTCBC.pkl",
    "k_l3": "ABBY_ctrlvertckl3_I20TRCNPRDCTCBC.pkl",
    "k_s1": "ABBY_ctrlvertcks1_I20TRCNPRDCTCBC.pkl",
    "k_s2": "ABBY_ctrlvertcks2_I20TRCNPRDCTCBC.pkl",
    "k_s3": "ABBY_ctrlvertcks3_I20TRCNPRDCTCBC.pkl",
    "k_s4": "ABBY_ctrlvertcks4_I20TRCNPRDCTCBC.pkl",
    "leaf_long": "ABBY_ctrlvertcleaflong_I20TRCNPRDCTCBC.pkl",
    "q10_mr": "ABBY_ctrlvertcq10mr_I20TRCNPRDCTCBC.pkl",
}
LOG_PARAMETERS = ["k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4"]
TARGETS = [
    "GPP", "ER", "SR", "HR_TOTAL", "LITFALL", "LITTER_SOIL_C_TOTAL",
    "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C",
]
OBSERVATION_PATH = "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc"
CONTROL_PARAMFILE = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc"
COMPENSATION = [
    ["k_l1", "LITR1C", "K_LITR1", "LITR1_HR"],
    ["k_l2", "LITR2C", "K_LITR2", "LITR2_HR"],
    ["k_l3", "LITR3C", "K_LITR3", "LITR3_HR"],
    ["k_s1", "SOIL1C", "K_SOIL1", "SOIL1_HR"],
    ["k_s2", "SOIL2C", "K_SOIL2", "SOIL2_HR"],
    ["k_s3", "SOIL3C", "K_SOIL3", "SOIL3_HR"],
    ["k_s4", "SOIL4C", "K_SOIL4", "SOIL4_HR"],
]
HR_POOLS = [
    ["CWDC", "K_CWD"], ["LITR1C", "K_LITR1"], ["LITR2C", "K_LITR2"],
    ["LITR3C", "K_LITR3"], ["SOIL1C", "K_SOIL1"], ["SOIL2C", "K_SOIL2"],
    ["SOIL3C", "K_SOIL3"], ["SOIL4C", "K_SOIL4"],
]
LITTER_RATIOS = [
    ["leaf_cn", "LEAFC_TO_LITTER", "LEAFN_TO_LITTER"],
    ["leaf_cp", "LEAFC_TO_LITTER", "LEAFP_TO_LITTER"],
    ["froot_cn", "FROOTC_TO_LITTER", "FROOTN_TO_LITTER"],
    ["froot_cp", "FROOTC_TO_LITTER", "FROOTP_TO_LITTER"],
]
EXPECTED_ROWS = {
    "parameter_metadata.csv": 13,
    "member_metrics.csv": 1300,
    "sensitivity_scores.csv": 338,
    "response_curves.csv": 37180,
    "observation_summary.csv": 1,
    "hr_pathway_metrics.csv": 35100,
    "hr_pathway_curves.csv": 390,
    "litter_ratio_member_metrics.csv": 5200,
    "litter_ratio_timeseries.csv": 3188640,
    "litter_ratio_curves.csv": 520,
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
        raise ValueError("input manifest is not a passing OAT manifest")
    if input_manifest.get("site") != "ABBY":
        raise ValueError("input manifest site is not ABBY")
    if tuple(input_manifest.get("parameters", [])) != PARAMETERS:
        raise ValueError("input manifest parameter order differs from the locked Iter007 order")
    if input_manifest.get("parameter_pickles") != PARAMETER_PICKLES:
        raise ValueError("input manifest mappings differ from the locked Iter007 mappings")
    if {"grpnow", "kmax"} & set(input_manifest["parameter_pickles"]):
        raise ValueError("excluded parameters are present")
    locked_fields = {
        "pickle_dir": "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles",
        "control_paramfile": CONTROL_PARAMFILE,
        "log_parameters": LOG_PARAMETERS,
        "targets": TARGETS,
        "observations": [["SR", OBSERVATION_PATH]],
        "compensation": COMPENSATION,
        "hr_pools": HR_POOLS,
        "hr_n_limiter": "FPI",
        "hr_p_limiter": "FPI_P",
        "litter_ratios": LITTER_RATIOS,
        "expected_hours": 61320,
        "year_range": [2018, 2024],
        "member_count_per_parameter": 100,
    }
    for field, expected in locked_fields.items():
        if input_manifest.get(field) != expected:
            raise ValueError(f"input manifest field differs from locked Iter007 contract: {field}")
    if input_manifest.get("control_paramfile_sha256") != "3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9":
        raise ValueError("control parameter hash differs from the locked Iter007 identity")
    if input_manifest.get("observation_sha256") != {
        "SR": "e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2"
    }:
        raise ValueError("observation hash differs from the locked Iter007 identity")
    output_manifest = json.loads((args.results / "output_manifest.json").read_text())
    if output_manifest.get("schema") != "elm_oat_output_manifest_v4" or output_manifest.get("status") != "pass":
        raise ValueError("output manifest is not a passing OAT manifest")
    if output_manifest.get("site") != "ABBY":
        raise ValueError("output manifest site is not ABBY")
    if output_manifest.get("input_manifest_sha256") != digest(args.input_manifest):
        raise ValueError("output manifest does not identify the supplied input manifest")
    observed_rows = {name: row_count(args.results / name) for name in EXPECTED_ROWS}
    if observed_rows != EXPECTED_ROWS or output_manifest.get("row_counts") != EXPECTED_ROWS:
        raise ValueError(f"row-count mismatch: {observed_rows}")
    for name in EXPECTED_ROWS:
        if name == "observation_summary.csv":
            continue
        with (args.results / name).open(newline="") as handle:
            parameters_seen = {row["parameter"] for row in csv.DictReader(handle)}
        if parameters_seen != set(PARAMETERS):
            raise ValueError(f"result table parameter membership differs: {name}")

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
    if len(member_support) != 52 or any(item["declared"] != 100 for item in member_support.values()):
        raise ValueError("litter member support does not cover 13 parameters x 4 ratios x 100 members")

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
    if any(not path.name.startswith("ABBY_") for path in figures):
        raise ValueError("every figure must have an ABBY_ prefix")
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
    print(f"ITER007_ARTIFACT_VALIDATE_PASS rows={sum(observed_rows.values())} figures=44")


if __name__ == "__main__":
    main()
