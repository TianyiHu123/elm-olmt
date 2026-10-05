#!/usr/bin/env python3
"""Validate the locked Iter011 tables, figures, manifests, and sample restart sums."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

PARAMETER_STEMS = {
    "act25": "act25", "br_mr": "brmr", "cn_s1": "cns1", "cn_s2": "cns2",
    "cn_s3": "cns3", "cn_s4": "cns4", "decomp_depth_efolding": "depthefold",
    "frootcn": "frootcn", "grperc": "grperc", "k_l1": "kl1", "k_l2": "kl2",
    "k_l3": "kl3", "k_s1": "ks1", "k_s2": "ks2", "k_s3": "ks3",
    "k_s4": "ks4", "leafcn": "leafcn", "leaf_long": "leaflong",
    "lflitcn": "lflitcn", "livewdcn": "livewdcn", "q10_mr": "q10mr",
}
PARAMETERS = tuple(PARAMETER_STEMS)
CONFIG_NAMES = {
    parameter: f"ABBY_{parameter}.cfg" for parameter in PARAMETERS
}
CONFIG_NAMES["decomp_depth_efolding"] = "ABBY_depth_efold.cfg"
PARAMETER_FILE_NAMES = {
    parameter: f"{parameter}_paramfile" for parameter in PARAMETERS
}
PARAMETER_FILE_NAMES["decomp_depth_efolding"] = "depth_efold_paramfile.txt"
TARGETS = ("SR", "HR", "GPP", "LITFALL", "DECOMP_C_TOTAL")
SPINUP_TARGETS = ("DECOMP_C_TOTAL", "DECOMP_N_TOTAL", "DECOMP_P_TOTAL")
SPINUP_COMPONENTS = {
    "DECOMP_C_TOTAL": ("cwdc_vr", "litr1c_vr", "litr2c_vr", "litr3c_vr", "soil1c_vr", "soil2c_vr", "soil3c_vr", "soil4c_vr"),
    "DECOMP_N_TOTAL": ("cwdn_vr", "litr1n_vr", "litr2n_vr", "litr3n_vr", "soil1n_vr", "soil2n_vr", "soil3n_vr", "soil4n_vr"),
    "DECOMP_P_TOTAL": ("cwdp_vr", "litr1p_vr", "litr2p_vr", "litr3p_vr", "soil1p_vr", "soil2p_vr", "soil3p_vr", "soil4p_vr"),
}
HR_POOLS = [
    ["CWDC", "K_CWD"], ["LITR1C", "K_LITR1"], ["LITR2C", "K_LITR2"],
    ["LITR3C", "K_LITR3"], ["SOIL1C", "K_SOIL1"], ["SOIL2C", "K_SOIL2"],
    ["SOIL3C", "K_SOIL3"], ["SOIL4C", "K_SOIL4"],
]
FORBIDDEN_COMPONENT_HR = {
    "CWDC_HR", "LITR1_HR", "LITR2_HR", "LITR3_HR",
    "SOIL1_HR", "SOIL2_HR", "SOIL3_HR", "SOIL4_HR",
}
EXPECTED_ROWS = {
    "parameter_metadata.csv": 21,
    "member_metrics.csv": 2100,
    "sensitivity_scores.csv": 105,
    "response_curves.csv": 11550,
    "observation_summary.csv": 1,
    "spinup_member_metrics.csv": 2100,
    "spinup_sensitivity_scores.csv": 63,
    "spinup_response_curves.csv": 6930,
    "hr_pathway_metrics.csv": 56700,
    "hr_pathway_curves.csv": 630,
}
EXPECTED_FIGURES = {
    *(f"ABBY_{target}_mean_response_atlas.png" for target in TARGETS),
    "ABBY_mean_sensitivity_heatmap.png",
    *(f"ABBY_{target}_spinup_response_atlas.png" for target in SPINUP_TARGETS),
    "ABBY_spinup_state_sensitivity_heatmap.png",
    "ABBY_accumulated_hr_pathways.png",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def finite(value: str) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.input_manifest.read_text())
    output = json.loads((args.results / "output_manifest.json").read_text())
    if manifest.get("schema") != "elm_oat_input_manifest_v5" or manifest.get("status") != "pass":
        raise ValueError("input manifest is not a passing v5 OAT manifest")
    if output.get("schema") != "elm_oat_output_manifest_v5" or output.get("status") != "pass":
        raise ValueError("output manifest is not a passing v5 OAT manifest")
    expected_pickles = {
        parameter: f"ABBY_ctrlvertc{stem}_I20TRCNPRDCTCBC.pkl"
        for parameter, stem in PARAMETER_STEMS.items()
    }
    expected_restarts = {
        parameter: f"ABBY_ctrlvertc{stem}_I1850CNPRDCTCBC"
        for parameter, stem in PARAMETER_STEMS.items()
    }
    locked = {
        "site": "ABBY", "parameters": list(PARAMETERS), "parameter_pickles": expected_pickles,
        "parameter_restarts": expected_restarts, "targets": list(TARGETS), "statistics": ["mean"],
        "compensation": [], "litter_ratios": [], "hr_n_limiter": "FPI", "hr_p_limiter": "FPI_P",
        "hr_pools": HR_POOLS,
        "config_dir": "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/config",
        "parameter_dir": "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/params",
        "parameter_configs": CONFIG_NAMES, "parameter_files": PARAMETER_FILE_NAMES,
        "restart_root": "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/restart",
        "expected_hours": 61320, "year_range": [2018, 2024], "member_count_per_parameter": 100,
    }
    for field, expected in locked.items():
        if manifest.get(field) != expected:
            raise ValueError(f"locked input field differs: {field}")
    if manifest.get("spinup_components") != {key: list(value) for key, value in SPINUP_COMPONENTS.items()}:
        raise ValueError("restart component interface differs")
    provenance = manifest.get("provenance_sha256", {})
    if set(provenance) != set(PARAMETERS):
        raise ValueError("config/parameter provenance coverage differs")
    for parameter, identity in provenance.items():
        if not all(identity.get(field) for field in (
            "config_path", "config_sha256", "parameter_file_path", "parameter_file_sha256"
        )):
            raise ValueError(f"config/parameter provenance is incomplete: {parameter}")
    new_ranges = {"leafcn": (30.0, 40.0), "frootcn": (30.0, 50.0), "livewdcn": (35.0, 65.0), "lflitcn": (50.0, 90.0)}
    for parameter, bounds in new_ranges.items():
        identity = provenance[parameter]
        if (float(identity["declared_pmin"]), float(identity["declared_pmax"])) != bounds:
            raise ValueError(f"new parameter range differs: {parameter}")
    required = set(manifest.get("required_raw_variables", []))
    if "HR" not in required or FORBIDDEN_COMPONENT_HR & required:
        raise ValueError("transient HR is not locked to direct case.output['HR']")
    if output.get("input_manifest_sha256") != digest(args.input_manifest):
        raise ValueError("output does not identify the validated input manifest")

    observed_rows = {name: len(rows(args.results / name)) for name in EXPECTED_ROWS}
    if observed_rows != EXPECTED_ROWS or output.get("row_counts") != EXPECTED_ROWS:
        raise ValueError(f"row counts differ: {observed_rows}")
    if sum(observed_rows.values()) != 80200:
        raise ValueError("primary CSV row total is not 80,200")
    for name in EXPECTED_ROWS:
        table = rows(args.results / name)
        if name != "observation_summary.csv" and {row["parameter"] for row in table} != set(PARAMETERS):
            raise ValueError(f"parameter coverage differs in {name}")

    required_columns = {
        "parameter_metadata.csv": {"restart_case", "restart_components", "restart_support"},
        "observation_summary.csv": {"units", "window", "valid_count"},
        "member_metrics.csv": {"endpoint_definitions", "endpoint_units", "model_coverage"},
        "sensitivity_scores.csv": {
            "units", "endpoint_definition", "model_coverage", "score_denominator", "rank_scope",
            "supported", "rejection_reason",
        },
        "response_curves.csv": {"units", "endpoint_definition", "model_coverage"},
        "spinup_member_metrics.csv": {"endpoint_definitions", "endpoint_units", "model_coverage"},
        "spinup_sensitivity_scores.csv": {
            "units", "endpoint_definition", "model_coverage", "score_denominator", "rank_scope",
            "supported", "rejection_reason",
        },
        "spinup_response_curves.csv": {"units", "endpoint_definition", "model_coverage"},
        "hr_pathway_metrics.csv": {"units", "endpoint_definition", "model_coverage"},
        "hr_pathway_curves.csv": {"units", "endpoint_definition", "model_coverage"},
    }
    allowed_blank_columns = {
        "sensitivity_scores.csv": {"rejection_reason"},
        "spinup_sensitivity_scores.csv": {"rejection_reason"},
    }
    for name, columns in required_columns.items():
        table = rows(args.results / name)
        nonempty_columns = columns - allowed_blank_columns.get(name, set())
        if (
            not table
            or not columns.issubset(table[0])
            or any(not row[column] for row in table for column in nonempty_columns)
        ):
            raise ValueError(f"required table metadata is incomplete: {name}")

    scores = rows(args.results / "sensitivity_scores.csv")
    if {row["statistic"] for row in scores} != {"mean"} or {row["target"] for row in scores} != set(TARGETS):
        raise ValueError("transient score endpoint/statistic coverage differs")
    for row in scores + rows(args.results / "spinup_sensitivity_scores.csv"):
        if row["supported"] == "True":
            if row["rejection_reason"] or not finite(row["score_percent"]) or int(row["rank"]) < 1:
                raise ValueError("supported score has invalid value, rank, or rejection reason")
        elif row["supported"] == "False":
            if row["score_percent"] or not row["rejection_reason"] or int(row["rank"]) != 0:
                raise ValueError("unsupported score is not an explicit gap")
        else:
            raise ValueError("score support flag is invalid")

    observation = rows(args.results / "observation_summary.csv")
    if len(observation) != 1 or observation[0]["variable"] != "SR" or not finite(observation[0]["mean"]):
        raise ValueError("observed SR reference is incomplete")
    pathway_metrics = rows(args.results / "hr_pathway_metrics.csv")
    if {row["pathway"] for row in pathway_metrics} != {"potential", "n_limited", "p_limited"}:
        raise ValueError("pathway membership differs")
    if {row["pool"] for row in pathway_metrics} != {
        "CWDC", "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C", "TOTAL"
    }:
        raise ValueError("pathway pool membership differs")
    pathway_counts = Counter((row["parameter"], row["pathway"], row["pool"]) for row in pathway_metrics)
    if set(pathway_counts.values()) != {100}:
        raise ValueError("pathway member coverage differs")

    spinup_members = rows(args.results / "spinup_member_metrics.csv")
    spinup_lookup = {(row["parameter"], int(row["member"])): row for row in spinup_members}
    restart_root = Path(manifest["restart_root"])
    for parameter, case_name in expected_restarts.items():
        restart = restart_root / case_name / "g00001" / f"{case_name}.elm.r.0201-01-01-00000.nc"
        with Dataset(restart, "r") as dataset:
            for target, components in SPINUP_COMPONENTS.items():
                independent = sum(float(np.nansum(np.ma.asarray(dataset.variables[name][:]).filled(np.nan))) for name in components)
                observed = float(spinup_lookup[(parameter, 1)][target])
                if not np.isclose(independent, observed, rtol=1e-12, atol=1e-12):
                    raise ValueError(f"independent restart sum differs for {parameter}/{target}")

    figure_names = {path.name for path in args.results.glob("*.png")}
    if figure_names != EXPECTED_FIGURES or output.get("figure_count") != 11:
        raise ValueError(f"figure membership differs: {sorted(figure_names)}")
    forbidden = ("std", "compensation", "litter_ratio", "flux_weighted")
    if any(token in name for name in output.get("artifacts", {}) for token in forbidden):
        raise ValueError("forbidden standard-deviation, compensation, or litter artifact exists")
    observed_artifacts = {path.name for path in args.results.iterdir() if path.is_file() and path.name != "output_manifest.json"}
    if observed_artifacts != set(output.get("artifacts", {})):
        raise ValueError("output manifest artifact membership differs")
    for name, identity in output["artifacts"].items():
        path = args.results / name
        if path.stat().st_size != identity["bytes"] or digest(path) != identity["sha256"]:
            raise ValueError(f"artifact identity differs: {name}")
    print("ITER011_ARTIFACT_VALIDATE_PASS rows=80200 figures=11 restart_samples=63")


if __name__ == "__main__":
    main()
