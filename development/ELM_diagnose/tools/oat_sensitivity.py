#!/usr/bin/env python3
"""Strict, input-driven OAT sensitivity diagnostics for ELM ensemble pickles."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import pickle
import re
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import model_ELM  # noqa: F401,E402  Required for ELMcase pickle loading.
from model_ELM.load_obs_nc import load_observations_with_time_from_nc  # noqa: E402

PARAMETER_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
TARGETS = (
    "GPP",
    "ER",
    "SR",
    "HR",
    "HR_TOTAL",
    "LITFALL",
    "LITTER_SOIL_C_TOTAL",
    "DECOMP_C_TOTAL",
    "LITR1C",
    "LITR2C",
    "LITR3C",
    "SOIL1C",
    "SOIL2C",
    "SOIL3C",
    "SOIL4C",
)
DIRECT_TARGETS = ("GPP", "ER", "SR", "HR", "LITFALL", "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
HR_COMPONENTS = ("CWDC_HR", "LITR1_HR", "LITR2_HR", "LITR3_HR", "SOIL1_HR", "SOIL2_HR", "SOIL3_HR", "SOIL4_HR")
SOC_COMPONENTS = ("LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
DECOMP_C_COMPONENTS = ("CWDC", *SOC_COMPONENTS)
COMPENSATION = {
    "k_l1": ("LITR1C", "K_LITR1", "LITR1_HR", "LITR1"),
    "k_l2": ("LITR2C", "K_LITR2", "LITR2_HR", "LITR2"),
    "k_l3": ("LITR3C", "K_LITR3", "LITR3_HR", "LITR3"),
    "k_s1": ("SOIL1C", "K_SOIL1", "SOIL1_HR", "SOIL1"),
    "k_s2": ("SOIL2C", "K_SOIL2", "SOIL2_HR", "SOIL2"),
    "k_s3": ("SOIL3C", "K_SOIL3", "SOIL3_HR", "SOIL3"),
    "k_s4": ("SOIL4C", "K_SOIL4", "SOIL4_HR", "SOIL4"),
}
DERIVED_TARGETS = frozenset({"HR_TOTAL", "LITTER_SOIL_C_TOTAL", "DECOMP_C_TOTAL"})
EXPECTED_HOURS = 7 * 365 * 24
STATISTICS = ("mean", "temporal_std")
DISPLAY_NAMES = {"LITTER_SOIL_C_TOTAL": "Total SOC"}
UNITS = {
    "GPP": "gC m-2 day-1",
    "ER": "gC m-2 day-1",
    "SR": "gC m-2 day-1",
    "HR": "gC m-2 day-1",
    "HR_TOTAL": "gC m-2 day-1",
    "LITFALL": "gC m-2 day-1",
    "LITTER_SOIL_C_TOTAL": "gC m-2",
    "DECOMP_C_TOTAL": "gC m-2",
    "LITR1C": "gC m-2",
    "LITR2C": "gC m-2",
    "LITR3C": "gC m-2",
    "SOIL1C": "gC m-2",
    "SOIL2C": "gC m-2",
    "SOIL3C": "gC m-2",
    "SOIL4C": "gC m-2",
}
SPINUP_COMPONENTS = {
    "DECOMP_C_TOTAL": ("cwdc_vr", "litr1c_vr", "litr2c_vr", "litr3c_vr", "soil1c_vr", "soil2c_vr", "soil3c_vr", "soil4c_vr"),
    "DECOMP_N_TOTAL": ("cwdn_vr", "litr1n_vr", "litr2n_vr", "litr3n_vr", "soil1n_vr", "soil2n_vr", "soil3n_vr", "soil4n_vr"),
    "DECOMP_P_TOTAL": ("cwdp_vr", "litr1p_vr", "litr2p_vr", "litr3p_vr", "soil1p_vr", "soil2p_vr", "soil3p_vr", "soil4p_vr"),
}
SPINUP_UNITS = {
    "DECOMP_C_TOTAL": "gC m-2",
    "DECOMP_N_TOTAL": "gN m-2",
    "DECOMP_P_TOTAL": "gP m-2",
}
ENDPOINT_DEFINITIONS = {
    "SR": "direct case.output['SR'] arithmetic temporal mean",
    "HR": "direct case.output['HR'] arithmetic temporal mean",
    "GPP": "direct case.output['GPP'] arithmetic temporal mean",
    "LITFALL": "direct case.output['LITFALL'] arithmetic temporal mean",
    "DECOMP_C_TOTAL": "CWDC + LITR1C + LITR2C + LITR3C + SOIL1C + SOIL2C + SOIL3C + SOIL4C",
}
SPINUP_ENDPOINT_DEFINITIONS = {
    target: " + ".join(components) for target, components in SPINUP_COMPONENTS.items()
}
TRANSIENT_COVERAGE = "declared-site model members; hourly 2018-2024 noleap; 61,320 samples/member"
SPINUP_COVERAGE = "declared-site final restart state at 0201-01-01; all stored vertical elements summed"
INPUT_MANIFEST_SCHEMA = "elm_oat_input_manifest_v5"
OUTPUT_MANIFEST_SCHEMA = "elm_oat_output_manifest_v5"
VALIDATION_RECEIPT_SCHEMA = "elm_oat_validation_receipt_v4"


@dataclass
class CaseSummary:
    parameter: str
    pickle_path: Path
    pickle_sha256: str
    pmin: float
    pmax: float
    coordinate: str
    parameter_values: np.ndarray
    normalized_parameter: np.ndarray
    native_value: float | None
    native_status: str
    member_statistics: dict[str, dict[str, np.ndarray]]
    compensation_statistics: dict[str, dict[str, np.ndarray]]
    hr_pathway_totals: dict[str, dict[str, np.ndarray]]
    litter_ratio_members: dict[str, np.ndarray]
    litter_ratio_support: dict[str, dict[str, np.ndarray]]
    litter_ratio_timeseries: dict[str, dict[str, np.ndarray]]
    spinup_metrics: dict[str, np.ndarray]
    spinup_metadata: dict[str, Any]
    metadata: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def endpoint_definition(target: str) -> str:
    return ENDPOINT_DEFINITIONS.get(target, f"{target} endpoint selected by the explicit diagnostic interface")


def spinup_endpoint_definition(target: str) -> str:
    return SPINUP_ENDPOINT_DEFINITIONS[target]


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def validate_declared_site(site: str) -> str:
    if not site or site != site.upper() or not site.isalnum():
        raise ValueError("--site must be a nonempty uppercase alphanumeric site identifier")
    return site


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_mapping(raw_items: list[str]) -> dict[str, str]:
    mappings: dict[str, str] = {}
    filenames: set[str] = set()
    for item in raw_items:
        if ":" not in item:
            raise ValueError(f"invalid --parameter-pickle mapping: {item!r}")
        parameter, basename = item.split(":", 1)
        if not parameter or not basename or PARAMETER_NAME.fullmatch(parameter) is None:
            raise ValueError(f"unknown or incomplete parameter mapping: {item!r}")
        if parameter in mappings:
            raise ValueError(f"duplicate parameter mapping: {parameter}")
        if basename != Path(basename).name or any(token in basename for token in ("*", "?", "[", "]")):
            raise ValueError(f"pickle mapping must use an exact basename: {basename!r}")
        if basename in filenames:
            raise ValueError(f"duplicate pickle basename: {basename}")
        mappings[parameter] = basename
        filenames.add(basename)
    if not mappings:
        raise ValueError("at least one --parameter-pickle mapping is required")
    if len(mappings) > 36:
        raise ValueError("at most 36 parameter mappings fit the supported atlas layout")
    return mappings


def parse_log_parameters(raw: str, parameters: tuple[str, ...]) -> frozenset[str]:
    items = [item.strip() for item in raw.split(",") if item.strip()]
    if len(items) != len(set(items)):
        raise ValueError("duplicate --log-parameters values are not allowed")
    parsed = frozenset(items)
    unknown = sorted(parsed - set(parameters))
    if unknown:
        raise ValueError(f"--log-parameters must be a subset of mapped parameters; unknown={unknown}")
    return parsed


def parse_statistics(raw_items: list[str]) -> tuple[str, ...]:
    if not raw_items:
        return STATISTICS
    if len(raw_items) != len(set(raw_items)):
        raise ValueError("duplicate --statistic values are not allowed")
    unknown = sorted(set(raw_items) - set(STATISTICS))
    if unknown:
        raise ValueError(f"unknown statistics: {unknown}")
    return tuple(raw_items)


def parse_restart_mapping(raw_items: list[str], parameters: tuple[str, ...]) -> dict[str, str]:
    if not raw_items:
        return {}
    mappings: dict[str, str] = {}
    basenames: set[str] = set()
    for item in raw_items:
        if ":" not in item:
            raise ValueError(f"invalid --parameter-restart mapping: {item!r}")
        parameter, basename = item.split(":", 1)
        if parameter not in parameters or not basename:
            raise ValueError(f"unknown or incomplete restart mapping: {item!r}")
        if parameter in mappings or basename in basenames:
            raise ValueError(f"duplicate restart mapping: {item!r}")
        if basename != Path(basename).name or any(token in basename for token in ("*", "?", "[", "]")):
            raise ValueError(f"restart mapping must use an exact case basename: {basename!r}")
        mappings[parameter] = basename
        basenames.add(basename)
    if tuple(mappings) != parameters:
        raise ValueError("restart mappings must match the ordered parameter mappings exactly")
    return mappings


def parse_provenance_mapping(
    raw_items: list[str], parameters: tuple[str, ...], option: str
) -> dict[str, str]:
    if not raw_items:
        return {}
    mappings: dict[str, str] = {}
    basenames: set[str] = set()
    for item in raw_items:
        if ":" not in item:
            raise ValueError(f"invalid {option} mapping: {item!r}")
        parameter, basename = item.split(":", 1)
        if parameter not in parameters or not basename:
            raise ValueError(f"unknown or incomplete {option} mapping: {item!r}")
        if parameter in mappings or basename in basenames:
            raise ValueError(f"duplicate {option} mapping: {item!r}")
        if basename != Path(basename).name or any(token in basename for token in ("*", "?", "[", "]")):
            raise ValueError(f"{option} mapping must use an exact basename: {basename!r}")
        mappings[parameter] = basename
        basenames.add(basename)
    if tuple(mappings) != parameters:
        raise ValueError(f"{option} mappings must match the ordered parameter mappings exactly")
    return mappings


def parse_targets(raw_items: list[str]) -> tuple[str, ...]:
    if not raw_items:
        raise ValueError("at least one --target is required")
    if len(raw_items) != len(set(raw_items)):
        raise ValueError("duplicate --target values are not allowed")
    unknown = sorted(set(raw_items) - set(TARGETS))
    if unknown:
        raise ValueError(f"unknown targets: {unknown}")
    return tuple(raw_items)


def parse_family(raw_items: list[str], fields: int, option: str) -> list[tuple[str, ...]]:
    parsed: list[tuple[str, ...]] = []
    labels: set[str] = set()
    for raw in raw_items:
        parts = tuple(raw.split(":"))
        if len(parts) != fields or any(not part for part in parts):
            raise ValueError(f"{option} requires {fields} nonempty colon-separated fields: {raw!r}")
        if parts[0] in labels:
            raise ValueError(f"duplicate {option} label: {parts[0]}")
        labels.add(parts[0])
        parsed.append(parts)
    return parsed


def parse_interfaces(args: argparse.Namespace, parameters: tuple[str, ...]) -> dict[str, Any]:
    targets = parse_targets(args.target)
    statistics = parse_statistics(getattr(args, "statistic", []))
    observations = parse_family(args.observation, 2, "--observation")
    if any(variable not in targets for variable, _ in observations):
        raise ValueError("every observation variable must also be a selected target")
    if any(not Path(path).is_absolute() for _, path in observations):
        raise ValueError("observation paths must be absolute")
    compensation = parse_family(args.compensation, 4, "--compensation")
    if any(parameter not in parameters for parameter, *_ in compensation):
        raise ValueError("compensation parameters must be declared OAT parameters")
    hr_pools = parse_family(args.hr_pool, 2, "--hr-pool")
    litter_ratios = parse_family(args.litter_ratio, 3, "--litter-ratio")
    hr_enabled = bool(hr_pools or args.hr_n_limiter or args.hr_p_limiter)
    if hr_enabled and (not hr_pools or not args.hr_n_limiter or not args.hr_p_limiter):
        raise ValueError("HR pathway analysis requires pools plus both N and P limiters")
    restart_root = getattr(args, "restart_root", None)
    restart_mappings = parse_restart_mapping(getattr(args, "parameter_restart", []), parameters)
    if bool(restart_mappings) != bool(restart_root):
        raise ValueError("restart analysis requires both --restart-root and complete --parameter-restart mappings")
    if restart_root is not None and not restart_root.is_absolute():
        raise ValueError("--restart-root must be absolute")
    config_dir = getattr(args, "config_dir", None)
    parameter_dir = getattr(args, "parameter_dir", None)
    config_mappings = parse_provenance_mapping(
        getattr(args, "parameter_config", []), parameters, "--parameter-config"
    )
    parameter_file_mappings = parse_provenance_mapping(
        getattr(args, "parameter_file", []), parameters, "--parameter-file"
    )
    provenance_enabled = any((config_dir, parameter_dir, config_mappings, parameter_file_mappings))
    if provenance_enabled and not all((config_dir, parameter_dir, config_mappings, parameter_file_mappings)):
        raise ValueError("parameter provenance requires both roots and both complete ordered mappings")
    if config_dir is not None and (not config_dir.is_absolute() or not parameter_dir.is_absolute()):
        raise ValueError("parameter provenance roots must be absolute")
    return {
        "targets": targets,
        "statistics": statistics,
        "observations": observations,
        "compensation": compensation,
        "hr_pools": hr_pools,
        "hr_n_limiter": args.hr_n_limiter,
        "hr_p_limiter": args.hr_p_limiter,
        "litter_ratios": litter_ratios,
        "restart_root": restart_root,
        "restart_mappings": restart_mappings,
        "config_dir": config_dir,
        "parameter_dir": parameter_dir,
        "config_mappings": config_mappings,
        "parameter_file_mappings": parameter_file_mappings,
    }


def required_raw_variables(interfaces: dict[str, Any]) -> tuple[str, ...]:
    required: list[str] = []
    for target in interfaces["targets"]:
        if target in DIRECT_TARGETS:
            required.append(target)
        elif target == "HR_TOTAL":
            required.extend(HR_COMPONENTS)
        elif target == "LITTER_SOIL_C_TOTAL":
            required.extend(SOC_COMPONENTS)
        elif target == "DECOMP_C_TOTAL":
            required.extend(DECOMP_C_COMPONENTS)
    for _, pool, rate, respiration in interfaces["compensation"]:
        required.extend((pool, rate, respiration))
    for pool, rate in interfaces["hr_pools"]:
        required.extend((pool, rate))
    if interfaces["hr_n_limiter"]:
        required.append(interfaces["hr_n_limiter"])
    if interfaces["hr_p_limiter"]:
        required.append(interfaces["hr_p_limiter"])
    for _, carbon_flux, nutrient_flux in interfaces["litter_ratios"]:
        required.extend((carbon_flux, nutrient_flux))
    return tuple(dict.fromkeys(required))


def member_matrix(case: Any, variable: str, n_members: int, allow_nonfinite: bool = False) -> np.ndarray:
    output = getattr(case, "output", None)
    if not isinstance(output, dict) or variable not in output:
        raise ValueError(f"missing case.output[{variable!r}]")
    values = np.asarray(output[variable], dtype=np.float64)
    if values.shape == (EXPECTED_HOURS, n_members):
        matrix = values
    elif values.shape == (n_members, EXPECTED_HOURS):
        matrix = values.T
    else:
        raise ValueError(
            f"{variable}: expected unambiguous ({EXPECTED_HOURS}, {n_members}) time x member data, got {values.shape}"
        )
    if not allow_nonfinite and not np.all(np.isfinite(matrix)):
        raise ValueError(f"{variable}: contains non-finite values")
    return matrix


def sum_matrices(case: Any, variables: tuple[str, ...], n_members: int) -> np.ndarray:
    result = np.zeros((EXPECTED_HOURS, n_members), dtype=np.float64)
    for variable in variables:
        result += member_matrix(case, variable, n_members)
    return result


def validate_time(case: Any, reference: np.ndarray | None) -> np.ndarray:
    output = getattr(case, "output", None)
    if not isinstance(output, dict) or "taxis" not in output:
        raise ValueError("missing case.output['taxis']")
    taxis = np.asarray(output["taxis"], dtype=np.float64).reshape(-1)
    if taxis.size != EXPECTED_HOURS or not np.all(np.isfinite(taxis)):
        raise ValueError(f"expected {EXPECTED_HOURS} finite hourly taxis values, got {taxis.size}")
    expected = 2018.0 + np.arange(EXPECTED_HOURS, dtype=np.float64) / 8760.0
    if not np.allclose(taxis, expected, rtol=0.0, atol=1e-11):
        raise ValueError("taxis does not match exact 2018--2024 no-leap hourly coordinates")
    if reference is not None and not np.array_equal(taxis, reference):
        raise ValueError("taxis differs from the first parameter case")
    if int(getattr(case, "postproc_startyear", -1)) != 2018 or int(getattr(case, "postproc_endyear", -1)) != 2024:
        raise ValueError("pickle postprocessing years are not exactly 2018--2024")
    return taxis


def parameter_values(case: Any, parameter: str) -> tuple[np.ndarray, float, float, int]:
    names = [str(item) for item in list(getattr(case, "ensemble_parms", []))]
    if names != [parameter]:
        raise ValueError(f"ensemble_parms must equal [{parameter!r}], got {names}")
    n_members = int(getattr(case, "nsamples", -1))
    if n_members != 100:
        raise ValueError(f"nsamples must be 100, got {n_members}")
    raw_samples = np.asarray(getattr(case, "samples", None), dtype=np.float64)
    if raw_samples.shape == (1, n_members):
        samples = raw_samples[0]
    elif raw_samples.shape in {(n_members,), (n_members, 1)}:
        samples = raw_samples.reshape(-1)
    else:
        raise ValueError(f"samples must encode one parameter x 100 members, got {raw_samples.shape}")
    pmin_values = np.asarray(getattr(case, "ensemble_pmin", []), dtype=np.float64).reshape(-1)
    pmax_values = np.asarray(getattr(case, "ensemble_pmax", []), dtype=np.float64).reshape(-1)
    if pmin_values.size != 1 or pmax_values.size != 1:
        raise ValueError("ensemble_pmin/pmax must each contain exactly one bound")
    pmin, pmax = float(pmin_values[0]), float(pmax_values[0])
    if not np.all(np.isfinite(samples)) or not np.isfinite(pmin) or not np.isfinite(pmax) or pmin >= pmax:
        raise ValueError("parameter samples and bounds must be finite with pmin < pmax")
    tolerance = max(abs(pmin), abs(pmax), 1.0) * 1e-12
    if np.any(samples < pmin - tolerance) or np.any(samples > pmax + tolerance):
        raise ValueError("parameter samples fall outside embedded bounds")
    pft_indices = np.asarray(getattr(case, "ensemble_pfts", []), dtype=int).reshape(-1)
    if pft_indices.size != 1:
        raise ValueError("ensemble_pfts must contain exactly one selector")
    return samples, pmin, pmax, int(pft_indices[0])


def normalize_parameter(values: np.ndarray, pmin: float, pmax: float, coordinate: str) -> np.ndarray:
    if coordinate == "log10":
        if pmin <= 0 or np.any(values <= 0):
            raise ValueError("log10 parameter coordinates require positive values and bounds")
        transformed = np.log10(values)
        lower, upper = np.log10(pmin), np.log10(pmax)
    else:
        transformed = values
        lower, upper = pmin, pmax
    normalized = (transformed - lower) / (upper - lower)
    if np.any(normalized < -1e-10) or np.any(normalized > 1.0 + 1e-10):
        raise ValueError("normalized parameter values fall outside [0, 1]")
    return np.clip(normalized, 0.0, 1.0)


def control_native_value(dataset: xr.Dataset, parameter: str, selector: int) -> tuple[float | None, str]:
    if parameter not in dataset.variables:
        return None, "missing_variable"
    values = np.asarray(dataset[parameter].values, dtype=np.float64)
    try:
        if parameter == "kmax":
            selected = values[:, selector]
        elif selector > 0:
            selected = values[selector]
        else:
            selected = values
    except (IndexError, TypeError):
        return None, "unresolved_selector"
    finite = np.asarray(selected, dtype=np.float64).reshape(-1)
    finite = finite[np.isfinite(finite)]
    if not finite.size:
        return None, "nonfinite"
    if not np.allclose(finite, finite[0], rtol=1e-12, atol=0.0):
        return None, "heterogeneous"
    return float(finite[0]), "available"


def temporal_statistics(matrix: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "mean": np.mean(matrix, axis=0),
        "temporal_std": np.std(matrix, axis=0, ddof=0),
    }


def flux_weighted_ratio_support(carbon: np.ndarray, nutrient: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return member ratios, support flags, and explicit reasons without dropping members."""
    carbon_total = np.sum(carbon / 24.0, axis=0)
    nutrient_total = np.sum(nutrient / 24.0, axis=0)
    supported = np.isfinite(carbon_total) & np.isfinite(nutrient_total) & (nutrient_total > 0.0)
    ratios = np.full(carbon_total.shape, np.nan, dtype=np.float64)
    np.divide(carbon_total, nutrient_total, out=ratios, where=supported)
    reasons = np.full(carbon_total.shape, "", dtype=object)
    reasons[~np.isfinite(carbon_total) & np.isfinite(nutrient_total)] = "nonfinite_carbon_total"
    reasons[np.isfinite(carbon_total) & ~np.isfinite(nutrient_total)] = "nonfinite_nutrient_total"
    reasons[~np.isfinite(carbon_total) & ~np.isfinite(nutrient_total)] = "nonfinite_carbon_and_nutrient_totals"
    reasons[np.isfinite(carbon_total) & np.isfinite(nutrient_total) & (nutrient_total <= 0.0)] = "nonpositive_nutrient_total"
    return ratios, supported, reasons


def load_case_summary(
    parameter: str,
    path: Path,
    pickle_sha256: str,
    coordinate: str,
    control_dataset: xr.Dataset,
    reference_taxis: np.ndarray | None,
    interfaces: dict[str, Any],
    expected_site: str,
) -> tuple[CaseSummary, np.ndarray]:
    with path.open("rb") as handle:
        case = pickle.load(handle)
    if str(getattr(case, "site", "")) != expected_site:
        raise ValueError(f"{path.name}: site must be {expected_site}")
    samples, pmin, pmax, selector = parameter_values(case, parameter)
    taxis = validate_time(case, reference_taxis)
    postproc_vars = set(str(item) for item in getattr(case, "postproc_vars", []))
    required_raw = required_raw_variables(interfaces)
    if not set(required_raw).issubset(postproc_vars):
        missing = sorted(set(required_raw) - postproc_vars)
        raise ValueError(f"{path.name}: postproc_vars missing required variables {missing}")
    litter_variables = {
        variable
        for _, carbon_flux, nutrient_flux in interfaces["litter_ratios"]
        for variable in (carbon_flux, nutrient_flux)
    }
    raw = {
        variable: member_matrix(case, variable, 100, allow_nonfinite=variable in litter_variables)
        for variable in required_raw
    }
    targets = {variable: raw[variable] for variable in interfaces["targets"] if variable in DIRECT_TARGETS}
    if "HR_TOTAL" in interfaces["targets"]:
        targets["HR_TOTAL"] = sum(raw[variable] for variable in HR_COMPONENTS)
    if "LITTER_SOIL_C_TOTAL" in interfaces["targets"]:
        targets["LITTER_SOIL_C_TOTAL"] = sum(raw[variable] for variable in SOC_COMPONENTS)
    if "DECOMP_C_TOTAL" in interfaces["targets"]:
        targets["DECOMP_C_TOTAL"] = sum(raw[variable] for variable in DECOMP_C_COMPONENTS)
    target_statistics = {target: temporal_statistics(targets[target]) for target in interfaces["targets"]}
    compensation_statistics: dict[str, dict[str, np.ndarray]] = {}
    compensation_lookup = {item[0]: item[1:] for item in interfaces["compensation"]}
    if parameter in compensation_lookup:
        pool, rate, respiration = compensation_lookup[parameter]
        compensation_statistics = {
            pool: temporal_statistics(raw[pool]),
            rate: temporal_statistics(raw[rate]),
            respiration: temporal_statistics(raw[respiration]),
        }
    hr_pathway_totals: dict[str, dict[str, np.ndarray]] = {}
    if interfaces["hr_pools"]:
        n_limiter = raw[interfaces["hr_n_limiter"]]
        p_limiter = raw[interfaces["hr_p_limiter"]]
        if np.any((n_limiter < 0.0) | (n_limiter > 1.0)) or np.any((p_limiter < 0.0) | (p_limiter > 1.0)):
            raise ValueError("FPI and FPI_P must remain within [0, 1]")
        pathway_matrices = {
            "potential": {},
            "n_limited": {},
            "p_limited": {},
        }
        for pool, rate in interfaces["hr_pools"]:
            potential = raw[pool] * raw[rate]
            pathway_matrices["potential"][pool] = potential
            pathway_matrices["n_limited"][pool] = n_limiter * potential
            pathway_matrices["p_limited"][pool] = p_limiter * potential
        for pathway, pool_matrices in pathway_matrices.items():
            total = sum(pool_matrices.values())
            hr_pathway_totals[pathway] = {
                **{pool: np.sum(matrix * 3600.0, axis=0) for pool, matrix in pool_matrices.items()},
                "TOTAL": np.sum(total * 3600.0, axis=0),
            }
    litter_ratio_members: dict[str, np.ndarray] = {}
    litter_ratio_support: dict[str, dict[str, np.ndarray]] = {}
    litter_ratio_timeseries: dict[str, dict[str, np.ndarray]] = {}
    for label, carbon_flux, nutrient_flux in interfaces["litter_ratios"]:
        carbon = raw[carbon_flux]
        nutrient = raw[nutrient_flux]
        valid = np.isfinite(carbon) & np.isfinite(nutrient) & (nutrient > 0.0)
        hourly_ratio = np.full(carbon.shape, np.nan, dtype=np.float64)
        np.divide(carbon, nutrient, out=hourly_ratio, where=valid)
        counts = np.sum(np.isfinite(hourly_ratio), axis=1)
        means = np.divide(
            np.nansum(hourly_ratio, axis=1), counts,
            out=np.full(EXPECTED_HOURS, np.nan), where=counts > 0,
        )
        centered = hourly_ratio - means[:, None]
        variances = np.divide(
            np.nansum(centered * centered, axis=1), counts,
            out=np.full(EXPECTED_HOURS, np.nan), where=counts > 0,
        )
        litter_ratio_timeseries[label] = {"mean": means, "std": np.sqrt(variances), "valid_members": counts}
        ratios, supported, reasons = flux_weighted_ratio_support(carbon, nutrient)
        litter_ratio_members[label] = ratios
        litter_ratio_support[label] = {"supported": supported, "rejection_reason": reasons}
    native, native_status = control_native_value(control_dataset, parameter, selector)
    normalized = normalize_parameter(samples, pmin, pmax, coordinate)
    if native is not None and (native < pmin or native > pmax or (coordinate == "log10" and native <= 0)):
        native_status = "outside_ensemble_range"
        native = None
    metadata = {
        "case_name": str(getattr(case, "casename", "")),
        "site": str(getattr(case, "site", "")),
        "nsamples": 100,
        "selector": selector,
        "postproc_startyear": int(getattr(case, "postproc_startyear")),
        "postproc_endyear": int(getattr(case, "postproc_endyear")),
        "frequency": "hourly_inferred_from_exact_taxis",
        "taxis_length": int(taxis.size),
        "taxis_first": float(taxis[0]),
        "taxis_last": float(taxis[-1]),
        "litter_ratio_support": {
            label: {
                "supported_members": int(np.sum(details["supported"])),
                "rejected_members": int(details["supported"].size - np.sum(details["supported"])),
            }
            for label, details in litter_ratio_support.items()
        },
    }
    summary = CaseSummary(
        parameter=parameter,
        pickle_path=path,
        pickle_sha256=pickle_sha256,
        pmin=pmin,
        pmax=pmax,
        coordinate=coordinate,
        parameter_values=samples.copy(),
        normalized_parameter=normalized.copy(),
        native_value=native,
        native_status=native_status,
        member_statistics=target_statistics,
        compensation_statistics=compensation_statistics,
        hr_pathway_totals=hr_pathway_totals,
        litter_ratio_members=litter_ratio_members,
        litter_ratio_support=litter_ratio_support,
        litter_ratio_timeseries=litter_ratio_timeseries,
        spinup_metrics={},
        spinup_metadata={},
        metadata=metadata,
    )
    del raw, targets, case
    gc.collect()
    return summary, taxis


def load_spinup_state(
    summary: CaseSummary,
    restart_root: Path,
    case_basename: str,
) -> CaseSummary:
    case_dir = restart_root / case_basename
    if not case_dir.is_dir() or case_dir.parent.resolve() != restart_root.resolve():
        raise FileNotFoundError(f"missing or out-of-root restart case: {case_dir}")
    observed_members = {path.name for path in case_dir.iterdir() if path.is_dir()}
    expected_members = {f"g{member:05d}" for member in range(1, 101)}
    if observed_members != expected_members:
        raise ValueError(
            f"restart member directories differ for {summary.parameter}: "
            f"missing={sorted(expected_members - observed_members)} extra={sorted(observed_members - expected_members)}"
        )
    metrics = {target: np.empty(100, dtype=np.float64) for target in SPINUP_COMPONENTS}
    schemas: dict[str, dict[str, Any]] = {}
    file_hashes: dict[str, str] = {}
    support: dict[str, dict[str, int]] = {
        target: {"valid_values": 0, "masked_values": 0} for target in SPINUP_COMPONENTS
    }
    for member in range(1, 101):
        member_name = f"g{member:05d}"
        restart = case_dir / member_name / f"{case_basename}.elm.r.0201-01-01-00000.nc"
        if not restart.is_file():
            raise FileNotFoundError(f"missing restart member file: {restart}")
        unexpected = [path.name for path in (case_dir / member_name).iterdir() if path.is_file() and path != restart]
        if unexpected:
            raise ValueError(f"unexpected restart files for {summary.parameter}/{member_name}: {sorted(unexpected)}")
        file_hashes[member_name] = digest(restart)
        with Dataset(str(restart), "r") as dataset:
            for target, components in SPINUP_COMPONENTS.items():
                total = 0.0
                target_shapes: set[tuple[int, ...]] = set()
                target_dimensions: set[tuple[str, ...]] = set()
                target_units: set[str] = set()
                for component in components:
                    if component not in dataset.variables:
                        raise KeyError(f"missing restart component {component!r} in {restart}")
                    variable = dataset.variables[component]
                    raw = np.ma.asarray(variable[:])
                    values = np.asarray(raw.filled(np.nan), dtype=np.float64)
                    valid = np.asarray(raw.compressed(), dtype=np.float64)
                    if not valid.size or not np.all(np.isfinite(valid)):
                        raise ValueError(f"restart component {component} lacks finite valid support in {restart}")
                    units = str(getattr(variable, "units", "")).strip()
                    component_schema = {
                        "dimensions": list(variable.dimensions),
                        "shape": list(values.shape),
                        "units": units,
                    }
                    if component in schemas and schemas[component] != component_schema:
                        raise ValueError(f"restart component schema differs across members: {component}")
                    schemas.setdefault(component, component_schema)
                    target_shapes.add(tuple(values.shape))
                    target_dimensions.add(tuple(variable.dimensions))
                    target_units.add(units)
                    support[target]["valid_values"] += int(valid.size)
                    support[target]["masked_values"] += int(np.ma.count_masked(raw))
                    total += float(np.nansum(values))
                if len(target_shapes) != 1 or len(target_dimensions) != 1 or len(target_units) != 1:
                    raise ValueError(f"restart {target} components have incompatible shape, dimensions, or units in {restart}")
                if not np.isfinite(total):
                    raise ValueError(f"restart {target} total is non-finite in {restart}")
                metrics[target][member - 1] = total
    return replace(
        summary,
        spinup_metrics=metrics,
        spinup_metadata={
            "case_basename": case_basename,
            "case_dir": str(case_dir),
            "members": 100,
            "component_schema": schemas,
            "support": support,
            "restart_sha256": file_hashes,
        },
    )


def equal_count_bins(x: np.ndarray, y: np.ndarray) -> list[dict[str, float | int]]:
    order = np.lexsort((np.arange(x.size), x))
    groups = np.array_split(order, 10)
    result = []
    for bin_index, indices in enumerate(groups, start=1):
        result.append(
            {
                "bin": bin_index,
                "count": int(indices.size),
                "x_median": float(np.median(x[indices])),
                "x_min": float(np.min(x[indices])),
                "x_max": float(np.max(x[indices])),
                "response_median": float(np.median(y[indices])),
            }
        )
    return result


def equal_count_bins_with_gaps(x: np.ndarray, y: np.ndarray) -> list[dict[str, float | int | str]]:
    """Keep ten declared bins while excluding unsupported responses from summaries."""
    order = np.lexsort((np.arange(x.size), x))
    groups = np.array_split(order, 10)
    result: list[dict[str, float | int | str]] = []
    for bin_index, indices in enumerate(groups, start=1):
        finite = np.isfinite(y[indices])
        valid_count = int(np.sum(finite))
        result.append(
            {
                "bin": bin_index,
                "count": int(indices.size),
                "valid_count": valid_count,
                "rejected_count": int(indices.size - valid_count),
                "x_median": float(np.median(x[indices])),
                "x_min": float(np.min(x[indices])),
                "x_max": float(np.max(x[indices])),
                "response_median": float(np.median(y[indices][finite])) if valid_count else "",
            }
        )
    return result


def response_score(values: np.ndarray) -> tuple[float, float, float, float]:
    median = float(np.median(values))
    if not np.isfinite(median) or median == 0.0:
        raise ValueError("response-spread score requires a finite nonzero ensemble median")
    p05, p95 = (float(item) for item in np.percentile(values, (5, 95)))
    score = 100.0 * (p95 - p05) / abs(median)
    if not np.isfinite(score):
        raise ValueError("response-spread score is non-finite")
    return score, median, p05, p95


def response_score_record(values: np.ndarray) -> dict[str, Any]:
    if values.shape != (100,) or not np.all(np.isfinite(values)):
        return {
            "score_percent": "", "median": "", "p05": "", "p95": "",
            "supported": False, "rejection_reason": "nonfinite_or_incomplete_ensemble",
        }
    median = float(np.median(values))
    if median == 0.0:
        return {
            "score_percent": "", "median": median, "p05": "", "p95": "",
            "supported": False, "rejection_reason": "zero_ensemble_median",
        }
    score, median, p05, p95 = response_score(values)
    return {
        "score_percent": score, "median": median, "p05": p05, "p95": p95,
        "supported": True, "rejection_reason": "",
    }


def normalized_response(values: np.ndarray) -> np.ndarray:
    median = float(np.median(values))
    if not np.isfinite(median) or median == 0.0:
        raise ValueError("normalized compensation response requires a finite nonzero median")
    return 100.0 * (values - median) / abs(median)


def build_rows(
    summaries: list[CaseSummary],
    targets: tuple[str, ...],
    statistics: tuple[str, ...] = STATISTICS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    parameter_rows: list[dict[str, Any]] = []
    member_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    for summary in summaries:
        parameter_rows.append(
            {
                "parameter": summary.parameter,
                "pickle_path": str(summary.pickle_path),
                "pickle_sha256": summary.pickle_sha256,
                "coordinate": summary.coordinate,
                "pmin": summary.pmin,
                "pmax": summary.pmax,
                "native_value": "" if summary.native_value is None else summary.native_value,
                "native_status": summary.native_status,
                "selector": summary.metadata["selector"],
                "members": 100,
                "restart_case": summary.spinup_metadata.get("case_basename", ""),
                "restart_components": (
                    json.dumps(summary.spinup_metadata.get("component_schema", {}), sort_keys=True)
                    if summary.spinup_metadata else ""
                ),
                "restart_support": (
                    json.dumps(summary.spinup_metadata.get("support", {}), sort_keys=True)
                    if summary.spinup_metadata else ""
                ),
            }
        )
        for member in range(100):
            row: dict[str, Any] = {
                "parameter": summary.parameter,
                "member": member + 1,
                "parameter_value": float(summary.parameter_values[member]),
                "normalized_parameter": float(summary.normalized_parameter[member]),
                "endpoint_definitions": json.dumps(
                    {target: endpoint_definition(target) for target in targets}, sort_keys=True
                ),
                "endpoint_units": json.dumps({target: UNITS[target] for target in targets}, sort_keys=True),
                "model_coverage": TRANSIENT_COVERAGE,
            }
            for target in targets:
                for statistic in statistics:
                    row[f"{target}_{statistic}"] = float(summary.member_statistics[target][statistic][member])
            member_rows.append(row)
        for target in targets:
            for statistic in statistics:
                values = summary.member_statistics[target][statistic]
                score_record = response_score_record(values)
                score_rows.append(
                    {
                        "parameter": summary.parameter,
                        "target": target,
                        "statistic": statistic,
                        **score_record,
                        "rank": 0,
                        "units": UNITS[target],
                        "endpoint_definition": endpoint_definition(target),
                        "model_coverage": TRANSIENT_COVERAGE,
                        "score_denominator": "absolute ensemble median",
                        "rank_scope": f"within endpoint={target} and statistic={statistic} across declared parameters",
                    }
                )
                bins = equal_count_bins(summary.normalized_parameter, values)
                member_bins = np.empty(100, dtype=int)
                for bin_record, indices in zip(bins, np.array_split(np.argsort(summary.normalized_parameter, kind="stable"), 10)):
                    member_bins[indices] = int(bin_record["bin"])
                for member in range(100):
                    curve_rows.append(
                        {
                            "parameter": summary.parameter,
                            "target": target,
                            "statistic": statistic,
                            "point_type": "member",
                            "member": member + 1,
                            "bin": int(member_bins[member]),
                            "parameter_value": float(summary.parameter_values[member]),
                            "normalized_parameter": float(summary.normalized_parameter[member]),
                            "response": float(values[member]),
                            "units": UNITS[target],
                            "endpoint_definition": endpoint_definition(target),
                            "model_coverage": TRANSIENT_COVERAGE,
                            "bin_count": "",
                            "bin_x_min": "",
                            "bin_x_max": "",
                        }
                    )
                for item in bins:
                    curve_rows.append(
                        {
                            "parameter": summary.parameter,
                            "target": target,
                            "statistic": statistic,
                            "point_type": "bin_median",
                            "member": "",
                            "bin": item["bin"],
                            "parameter_value": "",
                            "normalized_parameter": item["x_median"],
                            "response": item["response_median"],
                            "units": UNITS[target],
                            "endpoint_definition": endpoint_definition(target),
                            "model_coverage": TRANSIENT_COVERAGE,
                            "bin_count": item["count"],
                            "bin_x_min": item["x_min"],
                            "bin_x_max": item["x_max"],
                        }
                    )
    for target in targets:
        for statistic in statistics:
            selected = [row for row in score_rows if row["target"] == target and row["statistic"] == statistic]
            selected = [row for row in selected if row["supported"]]
            selected.sort(key=lambda row: (-float(row["score_percent"]), str(row["parameter"])))
            for rank, row in enumerate(selected, start=1):
                row["rank"] = rank
    return parameter_rows, member_rows, score_rows, curve_rows


def atlas_layout(parameter_count: int) -> tuple[int, int, tuple[float, float]]:
    if parameter_count < 1 or parameter_count > 36:
        raise ValueError("atlas layout requires between 1 and 36 parameters")
    columns = min(5, max(1, int(np.ceil(np.sqrt(parameter_count)))))
    rows = int(np.ceil(parameter_count / columns))
    return rows, columns, (3.75 * columns, 3.2 * rows + 1.0)


def build_spinup_rows(
    summaries: list[CaseSummary],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    member_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    for summary in summaries:
        if set(summary.spinup_metrics) != set(SPINUP_COMPONENTS):
            raise ValueError(f"missing spinup metrics for {summary.parameter}")
        member_bins = np.empty(100, dtype=int)
        sorted_groups = np.array_split(np.argsort(summary.normalized_parameter, kind="stable"), 10)
        for bin_index, indices in enumerate(sorted_groups, start=1):
            member_bins[indices] = bin_index
        for member in range(100):
            member_rows.append({
                "parameter": summary.parameter,
                "member": member + 1,
                "parameter_value": float(summary.parameter_values[member]),
                "normalized_parameter": float(summary.normalized_parameter[member]),
                "endpoint_definitions": json.dumps(
                    {target: spinup_endpoint_definition(target) for target in SPINUP_COMPONENTS}, sort_keys=True
                ),
                "endpoint_units": json.dumps(SPINUP_UNITS, sort_keys=True),
                "model_coverage": SPINUP_COVERAGE,
                **{target: float(summary.spinup_metrics[target][member]) for target in SPINUP_COMPONENTS},
            })
        for target in SPINUP_COMPONENTS:
            values = summary.spinup_metrics[target]
            score_record = response_score_record(values)
            score_rows.append({
                "parameter": summary.parameter,
                "target": target,
                "statistic": "spinup_state",
                **score_record,
                "rank": 0,
                "units": SPINUP_UNITS[target],
                "endpoint_definition": spinup_endpoint_definition(target),
                "model_coverage": SPINUP_COVERAGE,
                "score_denominator": "absolute ensemble median",
                "rank_scope": f"within final-spinup endpoint={target} across declared parameters",
            })
            for member in range(100):
                curve_rows.append({
                    "parameter": summary.parameter,
                    "target": target,
                    "point_type": "member",
                    "member": member + 1,
                    "bin": int(member_bins[member]),
                    "parameter_value": float(summary.parameter_values[member]),
                    "normalized_parameter": float(summary.normalized_parameter[member]),
                    "response": float(values[member]),
                    "units": SPINUP_UNITS[target],
                    "endpoint_definition": spinup_endpoint_definition(target),
                    "model_coverage": SPINUP_COVERAGE,
                    "bin_count": "",
                    "bin_x_min": "",
                    "bin_x_max": "",
                })
            for item in equal_count_bins(summary.normalized_parameter, values):
                curve_rows.append({
                    "parameter": summary.parameter,
                    "target": target,
                    "point_type": "bin_median",
                    "member": "",
                    "bin": item["bin"],
                    "parameter_value": "",
                    "normalized_parameter": item["x_median"],
                    "response": item["response_median"],
                    "units": SPINUP_UNITS[target],
                    "endpoint_definition": spinup_endpoint_definition(target),
                    "model_coverage": SPINUP_COVERAGE,
                    "bin_count": item["count"],
                    "bin_x_min": item["x_min"],
                    "bin_x_max": item["x_max"],
                })
    for target in SPINUP_COMPONENTS:
        selected = [row for row in score_rows if row["target"] == target]
        selected = [row for row in selected if row["supported"]]
        selected.sort(key=lambda row: (-float(row["score_percent"]), str(row["parameter"])))
        for rank, row in enumerate(selected, start=1):
            row["rank"] = rank
    return member_rows, score_rows, curve_rows


def plot_spinup_atlases(output: Path, summaries: list[CaseSummary], site: str) -> list[Path]:
    paths: list[Path] = []
    rows, columns, size = atlas_layout(len(summaries))
    for target in SPINUP_COMPONENTS:
        figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False)
        for axis, summary in zip(axes.flat, summaries):
            values = summary.spinup_metrics[target]
            axis.scatter(summary.normalized_parameter, values, s=9, alpha=0.25, color="tab:blue")
            bins = equal_count_bins(summary.normalized_parameter, values)
            axis.plot(
                [item["x_median"] for item in bins],
                [item["response_median"] for item in bins],
                "o-", color="black", lw=1.2, ms=3,
            )
            if summary.native_value is not None:
                native_x = normalize_parameter(
                    np.asarray([summary.native_value]), summary.pmin, summary.pmax, summary.coordinate
                )[0]
                axis.axvline(native_x, color="tab:red", ls="--", lw=0.9)
            axis.set(
                title=summary.parameter,
                xlim=(-0.03, 1.03),
                xlabel=f"normalized {summary.coordinate}",
                ylabel=SPINUP_UNITS[target],
            )
        for axis in axes.flat[len(summaries):]:
            axis.set_visible(False)
        figure.suptitle(f"{site} final spinup {target} OAT responses")
        figure.tight_layout(rect=(0, 0, 1, 0.97))
        path = output / f"{site}_{target}_spinup_response_atlas.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def plot_spinup_heatmap(
    output: Path,
    score_rows: list[dict[str, Any]],
    site: str,
    parameters: tuple[str, ...],
) -> Path:
    targets = tuple(SPINUP_COMPONENTS)
    lookup = {(row["parameter"], row["target"]): row for row in score_rows}
    matrix = np.asarray([
        [float(lookup[(parameter, target)]["score_percent"]) if lookup[(parameter, target)]["supported"] else np.nan
         for target in targets]
        for parameter in parameters
    ])
    figure, axis = plt.subplots(figsize=(10, 10))
    image = axis.imshow(matrix, aspect="auto", cmap="viridis")
    axis.set_xticks(range(len(targets)), list(targets), rotation=30, ha="right")
    axis.set_yticks(range(len(parameters)), parameters)
    for row_index, parameter in enumerate(parameters):
        for column_index, target in enumerate(targets):
            row = lookup[(parameter, target)]
            color = "white" if matrix[row_index, column_index] > np.nanmedian(matrix) else "black"
            label = f"{float(row['score_percent']):.1f}\n#{row['rank']}" if row["supported"] else "NA"
            axis.text(column_index, row_index, label, ha="center", va="center", fontsize=6, color=color)
    axis.set_title(f"{site} final-spinup OAT response spread")
    figure.colorbar(image, ax=axis, label="response spread (%)")
    figure.tight_layout()
    path = output / f"{site}_spinup_state_sensitivity_heatmap.png"
    figure.savefig(path, dpi=150)
    plt.close(figure)
    return path


def plot_response_atlases(
    output: Path,
    summaries: list[CaseSummary],
    targets: tuple[str, ...],
    observation_rows: list[dict[str, Any]],
    site: str,
    statistics: tuple[str, ...] = STATISTICS,
) -> list[Path]:
    paths: list[Path] = []
    observation_lookup = {row["variable"]: row for row in observation_rows}
    for target in targets:
        for statistic in statistics:
            rows, columns, size = atlas_layout(len(summaries))
            figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False)
            for axis, summary in zip(axes.flat, summaries):
                x = summary.normalized_parameter
                y = summary.member_statistics[target][statistic]
                axis.scatter(x, y, s=9, alpha=0.25, color="tab:blue")
                bins = equal_count_bins(x, y)
                axis.plot([item["x_median"] for item in bins], [item["response_median"] for item in bins], "o-", color="black", lw=1.2, ms=3)
                if summary.native_value is not None:
                    native_x = normalize_parameter(np.asarray([summary.native_value]), summary.pmin, summary.pmax, summary.coordinate)[0]
                    axis.axvline(native_x, color="tab:red", ls="--", lw=0.9)
                if target in observation_lookup:
                    reference = observation_lookup[target]["mean" if statistic == "mean" else "temporal_std"]
                    axis.axhline(reference, color="tab:purple", ls=":", lw=1.0, label="observation")
                axis.set_title(summary.parameter)
                axis.set_xlim(-0.03, 1.03)
                axis.set_xlabel(f"normalized {summary.coordinate}")
                axis.set_ylabel(UNITS[target])
            for axis in axes.flat[len(summaries) :]:
                axis.set_visible(False)
            figure.suptitle(f"{site} {DISPLAY_NAMES.get(target, target)} member {statistic.replace('_', ' ')} OAT responses")
            figure.tight_layout(rect=(0, 0, 1, 0.97))
            path = output / f"{site}_{target}_{statistic}_response_atlas.png"
            figure.savefig(path, dpi=150)
            plt.close(figure)
            paths.append(path)
    return paths


def plot_heatmaps(
    output: Path,
    score_rows: list[dict[str, Any]],
    targets: tuple[str, ...],
    site: str,
    parameters: tuple[str, ...],
    statistics: tuple[str, ...] = STATISTICS,
    filename_prefix: str = "",
) -> list[Path]:
    paths: list[Path] = []
    for statistic in statistics:
        lookup = {(row["parameter"], row["target"]): row for row in score_rows if row["statistic"] == statistic}
        matrix = np.asarray([
            [float(lookup[(parameter, target)]["score_percent"]) if lookup[(parameter, target)]["supported"] else np.nan
             for target in targets]
            for parameter in parameters
        ])
        figure, axis = plt.subplots(figsize=(18, 10))
        image = axis.imshow(matrix, aspect="auto", cmap="viridis")
        axis.set_xticks(range(len(targets)), [DISPLAY_NAMES.get(item, item) for item in targets], rotation=45, ha="right")
        axis.set_yticks(range(len(parameters)), parameters)
        for row_index, parameter in enumerate(parameters):
            for column_index, target in enumerate(targets):
                row = lookup[(parameter, target)]
                color = "white" if matrix[row_index, column_index] > np.nanmedian(matrix) else "black"
                label = f"{float(row['score_percent']):.1f}\n#{row['rank']}" if row["supported"] else "NA"
                axis.text(column_index, row_index, label, ha="center", va="center", fontsize=6, color=color)
        axis.set_title(f"{site} OAT response spread: {statistic.replace('_', ' ')}")
        figure.colorbar(image, ax=axis, label="response spread (%)")
        figure.tight_layout()
        prefix = f"{filename_prefix}_" if filename_prefix else ""
        path = output / f"{site}_{prefix}{statistic}_sensitivity_heatmap.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def plot_compensation(output: Path, summaries: list[CaseSummary], mappings: list[tuple[str, ...]], site: str) -> list[Path]:
    paths: list[Path] = []
    by_parameter = {summary.parameter: summary for summary in summaries}
    for parameter, pool, rate, respiration in mappings:
        label = pool.removesuffix("C")
        summary = by_parameter[parameter]
        figure, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        for axis, statistic in zip(axes, STATISTICS):
            for variable, color in ((pool, "tab:green"), (rate, "tab:orange"), (respiration, "tab:blue")):
                values = normalized_response(summary.compensation_statistics[variable][statistic])
                bins = equal_count_bins(summary.normalized_parameter, values)
                axis.plot([item["x_median"] for item in bins], [item["response_median"] for item in bins], "o-", label=variable, color=color)
            axis.axhline(0.0, color="black", lw=0.6)
            axis.set(xlabel=f"normalized {summary.coordinate} {parameter}", ylabel="departure from ensemble median (%)", title=statistic.replace("_", " "))
            axis.legend(fontsize=8)
        figure.suptitle(f"{site} {parameter} / {label} decomposition compensation")
        figure.tight_layout(rect=(0, 0, 1, 0.94))
        path = output / f"{site}_{parameter}_{label}_compensation.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def load_observation_rows(observations: list[tuple[str, ...]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for variable, raw_path in observations:
        path = Path(raw_path)
        if not path.is_absolute() or not path.is_file():
            raise FileNotFoundError(f"invalid observation path: {path}")
        payload = load_observations_with_time_from_nc(str(path), [variable])
        times = np.asarray(payload["time"]).reshape(-1)
        keys = [str(value) for value in times]
        if len(keys) != len(set(keys)):
            raise ValueError(f"{variable}: observation timestamps are not unique")
        in_window = np.asarray([2018 <= int(value.year) <= 2024 for value in times], dtype=bool)
        values = np.asarray(payload["obs"][variable], dtype=np.float64)
        valid = in_window & np.isfinite(values) & (values > -9000.0)
        selected = values[valid]
        if not selected.size:
            raise ValueError(f"{variable}: no finite valid observations in 2018--2024")
        rows.append({
            "variable": variable,
            "path": str(path),
            "sha256": digest(path),
            "units": "gC m-2 day-1",
            "window": "2018-2024 noleap hourly overlap",
            "valid_count": int(selected.size),
            "minimum": float(np.min(selected)),
            "maximum": float(np.max(selected)),
            "mean": float(np.mean(selected)),
            "temporal_std": float(np.std(selected, ddof=0)),
        })
    return rows


def build_specialized_rows(
    summaries: list[CaseSummary], taxis: np.ndarray
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hr_metrics: list[dict[str, Any]] = []
    hr_curves: list[dict[str, Any]] = []
    litter_members: list[dict[str, Any]] = []
    litter_timeseries: list[dict[str, Any]] = []
    litter_curves: list[dict[str, Any]] = []
    for summary in summaries:
        for pathway, pools in summary.hr_pathway_totals.items():
            for pool, values in pools.items():
                for member, value in enumerate(values, start=1):
                    hr_metrics.append({
                        "parameter": summary.parameter, "member": member, "pathway": pathway,
                        "pool": pool, "accumulated_gC_m2": float(value), "units": "gC m-2",
                        "endpoint_definition": "sum over hourly pool_C * K_pool * limiter * 3600 seconds; limiter=1 for potential",
                        "model_coverage": TRANSIENT_COVERAGE,
                    })
            for item in equal_count_bins(summary.normalized_parameter, pools["TOTAL"]):
                hr_curves.append({
                    "parameter": summary.parameter, "pathway": pathway, **item,
                    "units": "gC m-2",
                    "endpoint_definition": "TOTAL across the eight declared decomposition pools",
                    "model_coverage": TRANSIENT_COVERAGE,
                })
        for label, values in summary.litter_ratio_members.items():
            support = summary.litter_ratio_support[label]
            for member, value in enumerate(values, start=1):
                supported = bool(support["supported"][member - 1])
                litter_members.append({
                    "parameter": summary.parameter,
                    "ratio": label,
                    "member": member,
                    "ratio_value": float(value) if supported else "",
                    "supported": supported,
                    "rejection_reason": str(support["rejection_reason"][member - 1]),
                })
            for item in equal_count_bins_with_gaps(summary.normalized_parameter, values):
                litter_curves.append({"parameter": summary.parameter, "ratio": label, **item})
        for label, statistics in summary.litter_ratio_timeseries.items():
            for hour in range(EXPECTED_HOURS):
                litter_timeseries.append({
                    "parameter": summary.parameter,
                    "ratio": label,
                    "hour_index": hour,
                    "model_time": float(taxis[hour]),
                    "mean": float(statistics["mean"][hour]),
                    "population_std": float(statistics["std"][hour]),
                    "valid_members": int(statistics["valid_members"][hour]),
                })
    return hr_metrics, hr_curves, litter_members, litter_timeseries, litter_curves


def expected_artifact_counts(interfaces: dict[str, Any], parameter_count: int) -> dict[str, int]:
    counts = {
        "parameter_metadata.csv": parameter_count,
        "member_metrics.csv": parameter_count * 100,
        "sensitivity_scores.csv": parameter_count * len(interfaces["targets"]) * len(interfaces["statistics"]),
        "response_curves.csv": parameter_count * len(interfaces["targets"]) * len(interfaces["statistics"]) * 110,
    }
    if interfaces["observations"]:
        counts["observation_summary.csv"] = len(interfaces["observations"])
    if interfaces["hr_pools"]:
        counts["hr_pathway_metrics.csv"] = parameter_count * 100 * 3 * (len(interfaces["hr_pools"]) + 1)
        counts["hr_pathway_curves.csv"] = parameter_count * 3 * 10
    if interfaces["litter_ratios"]:
        ratios = len(interfaces["litter_ratios"])
        counts["litter_ratio_member_metrics.csv"] = parameter_count * 100 * ratios
        counts["litter_ratio_timeseries.csv"] = parameter_count * EXPECTED_HOURS * ratios
        counts["litter_ratio_curves.csv"] = parameter_count * 10 * ratios
    if interfaces["restart_mappings"]:
        counts["spinup_member_metrics.csv"] = parameter_count * 100
        counts["spinup_sensitivity_scores.csv"] = parameter_count * len(SPINUP_COMPONENTS)
        counts["spinup_response_curves.csv"] = parameter_count * len(SPINUP_COMPONENTS) * 110
    return counts


def plot_hr_pathways(output: Path, summaries: list[CaseSummary], site: str) -> list[Path]:
    if not summaries or not summaries[0].hr_pathway_totals:
        return []
    rows, columns, size = atlas_layout(len(summaries))
    figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False)
    colors = {"potential": "tab:orange", "n_limited": "tab:blue", "p_limited": "tab:green"}
    for axis, summary in zip(axes.flat, summaries):
        for pathway, pools in summary.hr_pathway_totals.items():
            values = pools["TOTAL"]
            axis.scatter(summary.normalized_parameter, values, s=6, alpha=0.10, color=colors[pathway])
            bins = equal_count_bins_with_gaps(summary.normalized_parameter, values)
            axis.plot([item["x_median"] for item in bins], [item["response_median"] for item in bins], "o-", ms=3, lw=1.0, color=colors[pathway], label=pathway)
        axis.set(title=summary.parameter, xlabel=f"normalized {summary.coordinate}", ylabel="accumulated gC m-2")
    for axis in axes.flat[len(summaries):]:
        axis.set_visible(False)
    axes.flat[0].legend(fontsize=7)
    figure.suptitle(f"{site} accumulated potential and N/P-limited heterotrophic respiration")
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    path = output / f"{site}_accumulated_hr_pathways.png"
    figure.savefig(path, dpi=150)
    plt.close(figure)
    return [path]


def plot_litter_ratios(output: Path, summaries: list[CaseSummary], taxis: np.ndarray, site: str) -> list[Path]:
    if not summaries or not summaries[0].litter_ratio_members:
        return []
    paths: list[Path] = []
    for label in summaries[0].litter_ratio_members:
        rows, columns, size = atlas_layout(len(summaries))
        figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False)
        for axis, summary in zip(axes.flat, summaries):
            stats = summary.litter_ratio_timeseries[label]
            axis.plot(taxis, stats["mean"], color="tab:blue", lw=0.5)
            axis.fill_between(taxis, stats["mean"] - stats["std"], stats["mean"] + stats["std"], color="tab:blue", alpha=0.15)
            axis.set(title=summary.parameter, xlabel="model year", ylabel=label)
        for axis in axes.flat[len(summaries):]:
            axis.set_visible(False)
        figure.suptitle(f"{site} hourly litter ratio {label}: ensemble mean +/- population SD")
        figure.tight_layout(rect=(0, 0, 1, 0.97))
        path = output / f"{site}_{label}_hourly_ratio_atlas.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
        rows, columns, size = atlas_layout(len(summaries))
        figure, axes = plt.subplots(rows, columns, figsize=size, squeeze=False)
        for axis, summary in zip(axes.flat, summaries):
            values = summary.litter_ratio_members[label]
            axis.scatter(summary.normalized_parameter, values, s=9, alpha=0.25)
            bins = equal_count_bins_with_gaps(summary.normalized_parameter, values)
            supported_bins = [item for item in bins if item["response_median"] != ""]
            axis.plot([item["x_median"] for item in supported_bins], [item["response_median"] for item in supported_bins], "o-", color="black", ms=3, lw=1.0)
            axis.set(title=summary.parameter, xlabel=f"normalized {summary.coordinate}", ylabel=label)
        for axis in axes.flat[len(summaries):]:
            axis.set_visible(False)
        figure.suptitle(f"{site} flux-weighted litter ratio response {label}")
        figure.tight_layout(rect=(0, 0, 1, 0.97))
        path = output / f"{site}_{label}_flux_weighted_response_atlas.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def fixture_checks(parameters: tuple[str, ...]) -> dict[str, Any]:
    if not parameters or len(parameters) != len(set(parameters)):
        raise AssertionError("fixture parameters must be nonempty and unique")
    taxis = 2018.0 + np.arange(EXPECTED_HOURS, dtype=np.float64) / 8760.0
    matrix = np.column_stack((np.arange(EXPECTED_HOURS), np.arange(EXPECTED_HOURS) + 2.0))
    if matrix.shape != (EXPECTED_HOURS, 2) or taxis.size != EXPECTED_HOURS:
        raise AssertionError("orientation fixture failed")
    components = [np.full((4, 2), index, dtype=float) for index in range(1, 9)]
    if not np.array_equal(sum(components), np.full((4, 2), 36.0)):
        raise AssertionError("hourly sum-before-aggregation fixture failed")
    values = np.asarray([[1.0, 3.0], [5.0, 7.0]])
    if not np.array_equal(np.std(values, axis=0, ddof=0), np.asarray([2.0, 2.0])):
        raise AssertionError("ddof=0 fixture failed")
    if not np.allclose(normalize_parameter(np.asarray([1.0, 5.5, 10.0]), 1.0, 10.0, "linear"), (0.0, 0.5, 1.0)):
        raise AssertionError("linear normalization fixture failed")
    if not np.allclose(normalize_parameter(np.asarray([0.01, 0.1, 1.0]), 0.01, 1.0, "log10"), (0.0, 0.5, 1.0)):
        raise AssertionError("log normalization fixture failed")
    bins = equal_count_bins(np.arange(100, dtype=float), np.arange(100, dtype=float))
    if len(bins) != 10 or any(item["count"] != 10 for item in bins):
        raise AssertionError("equal-count bin fixture failed")
    score, _, p05, p95 = response_score(np.arange(1, 101, dtype=float))
    if not (score > 0 and p95 > p05):
        raise AssertionError("quantile/score direction fixture failed")
    lower_score = response_score(np.linspace(90.0, 110.0, 100))[0]
    higher_score = response_score(np.linspace(50.0, 150.0, 100))[0]
    if sorted((lower_score, higher_score), reverse=True) != [higher_score, lower_score]:
        raise AssertionError("descending rank direction fixture failed")
    expected_compensation = {
        "k_l1": ("LITR1C", "K_LITR1", "LITR1_HR", "LITR1"),
        "k_l2": ("LITR2C", "K_LITR2", "LITR2_HR", "LITR2"),
        "k_l3": ("LITR3C", "K_LITR3", "LITR3_HR", "LITR3"),
        "k_s1": ("SOIL1C", "K_SOIL1", "SOIL1_HR", "SOIL1"),
        "k_s2": ("SOIL2C", "K_SOIL2", "SOIL2_HR", "SOIL2"),
        "k_s3": ("SOIL3C", "K_SOIL3", "SOIL3_HR", "SOIL3"),
        "k_s4": ("SOIL4C", "K_SOIL4", "SOIL4_HR", "SOIL4"),
    }
    if COMPENSATION != expected_compensation:
        raise AssertionError("seven compensation mappings fixture failed")
    pool = np.asarray([[2.0, 3.0], [4.0, 5.0]])
    rate = np.asarray([[0.5, 0.25], [0.25, 0.2]])
    n_limiter = np.asarray([[0.5, 0.5], [0.25, 0.25]])
    p_limiter = np.asarray([[0.2, 0.2], [0.1, 0.1]])
    potential = pool * rate
    if not np.allclose(np.sum(potential * 3600.0, axis=0), (7200.0, 6300.0)):
        raise AssertionError("potential pathway multiplication/integration fixture failed")
    if not np.allclose(np.sum(n_limiter * potential * 3600.0, axis=0), (2700.0, 2250.0)):
        raise AssertionError("N-limited pathway fixture failed")
    if not np.allclose(np.sum(p_limiter * potential * 3600.0, axis=0), (1080.0, 900.0)):
        raise AssertionError("P-limited pathway fixture failed")
    eight_pools = [potential * float(index) for index in range(1, 9)]
    exact_total = sum(eight_pools)
    if not np.allclose(exact_total, potential * 36.0):
        raise AssertionError("exact eight-pool HR total fixture failed")
    if not np.allclose(np.sum(exact_total * 3600.0, axis=0), np.sum(potential * 36.0 * 3600.0, axis=0)):
        raise AssertionError("eight-pool integration-order fixture failed")
    carbon = np.asarray([[24.0, 48.0], [48.0, 96.0]])
    nutrient = np.asarray([[12.0, 0.0], [24.0, 48.0]])
    valid = nutrient > 0.0
    hourly = np.full(carbon.shape, np.nan)
    np.divide(carbon, nutrient, out=hourly, where=valid)
    if not np.array_equal(np.sum(np.isfinite(hourly), axis=1), (1, 2)):
        raise AssertionError("litter-ratio support fixture failed")
    flux_weighted = np.sum(carbon / 24.0, axis=0) / np.sum(np.where(nutrient > 0, nutrient, 0.0) / 24.0, axis=0)
    if not np.allclose(flux_weighted, (2.0, 3.0)):
        raise AssertionError("flux-weighted litter-ratio fixture failed")
    gap_carbon = np.asarray([[24.0, np.nan, 24.0], [48.0, 48.0, 48.0]])
    gap_nutrient = np.asarray([[12.0, 12.0, 0.0], [24.0, 24.0, 0.0]])
    gap_values, gap_support, gap_reasons = flux_weighted_ratio_support(gap_carbon, gap_nutrient)
    if not np.array_equal(gap_support, (True, False, False)):
        raise AssertionError("flux-weighted litter-ratio member support fixture failed")
    if not np.isclose(gap_values[0], 2.0) or not np.all(np.isnan(gap_values[1:])):
        raise AssertionError("flux-weighted litter-ratio explicit gap fixture failed")
    if tuple(gap_reasons) != ("", "nonfinite_carbon_total", "nonpositive_nutrient_total"):
        raise AssertionError("flux-weighted litter-ratio rejection-reason fixture failed")
    gap_bins = equal_count_bins_with_gaps(np.arange(100, dtype=float), np.r_[np.nan, np.arange(99, dtype=float)])
    if len(gap_bins) != 10 or gap_bins[0]["valid_count"] != 9 or gap_bins[0]["rejected_count"] != 1:
        raise AssertionError("flux-weighted litter-ratio gap-support fixture failed")
    minimal = argparse.Namespace(
        target=["GPP"], observation=[], compensation=[], hr_pool=[],
        hr_n_limiter=None, hr_p_limiter=None, litter_ratio=[],
    )
    minimal_interfaces = parse_interfaces(minimal, parameters)
    if required_raw_variables(minimal_interfaces) != ("GPP",):
        raise AssertionError("optional-family independence fixture failed")
    if expected_artifact_counts(minimal_interfaces, len(parameters)) != {
        "parameter_metadata.csv": len(parameters),
        "member_metrics.csv": len(parameters) * 100,
        "sensitivity_scores.csv": len(parameters) * 2,
        "response_curves.csv": len(parameters) * 220,
    }:
        raise AssertionError("dynamic optional-family artifact fixture failed")
    if plot_compensation(Path("."), [], minimal_interfaces["compensation"], "TEST"):
        raise AssertionError("omitted compensation fixture generated figures")
    if len(parameters) == 21 and atlas_layout(len(parameters))[:2] != (5, 5):
        raise AssertionError("21-parameter dynamic atlas fixture failed")
    return {
        "status": "pass",
        "orientation": "time_x_member",
        "hourly_sum_before_aggregation": True,
        "ddof": 0,
        "linear_and_log_normalization": True,
        "equal_count_bins": 10,
        "quantile_and_rank_direction": "descending_score",
        "compensation_mappings": COMPENSATION,
        "hr_pathways": "pool_times_rate_then_3600_second_integration",
        "hr_limiters": "N_and_P_applied_before_pool_and_time_summation",
        "exact_hr_pool_count": 8,
        "litter_ratios": "hourly_mask_population_spread_and_flux_weighted_totals_with_explicit_member_gaps",
        "optional_families": "independently_disableable",
        "omitted_compensation": "no_tables_or_figures",
        "atlas_layout": list(atlas_layout(len(parameters))[:2]),
    }


def paired_site_contract_fixture(
    output_root: Path,
    parameters: tuple[str, ...],
    log_parameters: frozenset[str],
) -> dict[str, Any]:
    """Exercise the complete numeric and presentation paths with paired synthetic sites."""
    global EXPECTED_HOURS
    original_expected_hours = EXPECTED_HOURS
    EXPECTED_HOURS = 4
    try:
        interfaces = parse_interfaces(argparse.Namespace(
            target=list(TARGETS),
            observation=[],
            compensation=[
                "k_l1:LITR1C:K_LITR1:LITR1_HR",
                "k_l2:LITR2C:K_LITR2:LITR2_HR",
                "k_l3:LITR3C:K_LITR3:LITR3_HR",
                "k_s1:SOIL1C:K_SOIL1:SOIL1_HR",
                "k_s2:SOIL2C:K_SOIL2:SOIL2_HR",
                "k_s3:SOIL3C:K_SOIL3:SOIL3_HR",
                "k_s4:SOIL4C:K_SOIL4:SOIL4_HR",
            ],
            hr_pool=[
                "CWDC:K_CWD", "LITR1C:K_LITR1", "LITR2C:K_LITR2", "LITR3C:K_LITR3",
                "SOIL1C:K_SOIL1", "SOIL2C:K_SOIL2", "SOIL3C:K_SOIL3", "SOIL4C:K_SOIL4",
            ],
            hr_n_limiter="FPI",
            hr_p_limiter="FPI_P",
            litter_ratio=[
                "leaf_cn:LEAFC_TO_LITTER:LEAFN_TO_LITTER",
                "leaf_cp:LEAFC_TO_LITTER:LEAFP_TO_LITTER",
                "froot_cn:FROOTC_TO_LITTER:FROOTN_TO_LITTER",
                "froot_cp:FROOTC_TO_LITTER:FROOTP_TO_LITTER",
            ],
        ), parameters)
        hours = np.arange(EXPECTED_HOURS, dtype=np.float64)[:, None]
        members = np.arange(100, dtype=np.float64)[None, :]
        base = 1.0 + 0.1 * hours + 0.01 * members
        raw: dict[str, np.ndarray] = {}
        for variable in required_raw_variables(interfaces):
            if variable == "FPI":
                raw[variable] = np.full(base.shape, 0.5)
            elif variable == "FPI_P":
                raw[variable] = np.full(base.shape, 0.25)
            elif variable.startswith("K_"):
                raw[variable] = base * 1.0e-6
            elif variable in {"LEAFN_TO_LITTER", "FROOTN_TO_LITTER"}:
                raw[variable] = base / 10.0
            elif variable in {"LEAFP_TO_LITTER", "FROOTP_TO_LITTER"}:
                raw[variable] = base / 100.0
            else:
                raw[variable] = base.copy()
        for _, carbon_flux, nutrient_flux in interfaces["litter_ratios"]:
            raw[nutrient_flux][:, 0] = 0.0
            raw[carbon_flux][:, 1] = np.nan
            raw[nutrient_flux][:, 2] = np.nan
            raw[carbon_flux][:, 3] = np.nan
            raw[nutrient_flux][:, 3] = np.nan
        raw["taxis"] = 2018.0 + np.arange(EXPECTED_HOURS, dtype=np.float64) / 8760.0
        samples = np.geomspace(0.01, 1.0, 100)
        output_root.mkdir(parents=True, exist_ok=False)
        loaded: dict[str, CaseSummary] = {}
        manifests: dict[str, dict[str, Any]] = {}
        figure_names: dict[str, list[str]] = {}
        numeric_rows: dict[str, Any] = {}
        with xr.Dataset() as control_dataset:
            for site in ("ABBY", "JERC"):
                site = validate_declared_site(site)
                case = SimpleNamespace(
                    site=site,
                    casename="synthetic_site_parity",
                    ensemble_parms=["k_l1"],
                    ensemble_pfts=[-1],
                    ensemble_pmin=[0.01],
                    ensemble_pmax=[1.0],
                    nsamples=100,
                    samples=samples.reshape(1, -1),
                    postproc_startyear=2018,
                    postproc_endyear=2024,
                    postproc_vars=list(required_raw_variables(interfaces)),
                    output=raw,
                )
                pickle_path = output_root / f"{site}_synthetic.pkl"
                with pickle_path.open("wb") as handle:
                    pickle.dump(case, handle)
                summary, taxis = load_case_summary(
                    "k_l1", pickle_path, digest(pickle_path), "log10", control_dataset,
                    None, interfaces, site,
                )
                summary.compensation_statistics = {
                    variable: temporal_statistics(raw[variable])
                    for _, pool, rate, respiration in interfaces["compensation"]
                    for variable in (pool, rate, respiration)
                }
                summaries = [
                    replace(
                        summary,
                        parameter=parameter,
                        coordinate="log10" if parameter in log_parameters else "linear",
                        metadata={**summary.metadata, "site": site},
                    )
                    for parameter in parameters
                ]
                loaded[site] = summary
                parameter_rows, member_rows, score_rows, curve_rows = build_rows(summaries, interfaces["targets"])
                for row in parameter_rows:
                    row.pop("pickle_path")
                    row.pop("pickle_sha256")
                specialized = build_specialized_rows(summaries, taxis)
                litter_member_rows = specialized[2]
                litter_curve_rows = specialized[4]
                if len(litter_member_rows) != len(parameters) * 400 or len(litter_curve_rows) != len(parameters) * 40:
                    raise AssertionError("paired-site gap fixture did not preserve litter row cardinality")
                rejected_rows = [row for row in litter_member_rows if not row["supported"]]
                if len(rejected_rows) != len(parameters) * 16 or any(row["ratio_value"] != "" for row in rejected_rows):
                    raise AssertionError("paired-site gap fixture did not retain explicit member gaps")
                approved_reasons = {
                    "nonfinite_carbon_total", "nonfinite_nutrient_total",
                    "nonfinite_carbon_and_nutrient_totals", "nonpositive_nutrient_total",
                }
                if {row["rejection_reason"] for row in rejected_rows} != approved_reasons:
                    raise AssertionError("paired-site gap fixture rejection reasons differ")
                for row in litter_curve_rows:
                    if row["valid_count"] + row["rejected_count"] != row["count"]:
                        raise AssertionError("paired-site gap fixture curve support totals differ")
                numeric_rows[site] = (parameter_rows, member_rows, score_rows, curve_rows, *specialized)
                mappings = {parameter: f"synthetic_{parameter}.pkl" for parameter in parameters}
                manifest_args = argparse.Namespace(
                    site=site,
                    pickle_dir=output_root,
                    control_paramfile=output_root / "synthetic_control.nc",
                    regression_results=None,
                )
                manifests[site] = manifest_contract(manifest_args, mappings, log_parameters, interfaces, [])
                site_output = output_root / site
                site_output.mkdir()
                figures = [
                    *plot_response_atlases(site_output, summaries, interfaces["targets"], [], site),
                    *plot_heatmaps(site_output, score_rows, interfaces["targets"], site, parameters),
                    *plot_compensation(site_output, summaries, interfaces["compensation"], site),
                    *plot_hr_pathways(site_output, summaries, site),
                    *plot_litter_ratios(site_output, summaries, taxis, site),
                ]
                figure_names[site] = sorted(path.name.removeprefix(f"{site}_") for path in figures)
                if len(figures) != 44:
                    raise AssertionError(f"{site}: paired-site fixture expected 44 figures, got {len(figures)}")
        if numeric_rows["ABBY"] != numeric_rows["JERC"]:
            raise AssertionError("paired-site complete numerical rows differ")
        abby_manifest = {key: value for key, value in manifests["ABBY"].items() if key != "site"}
        jerc_manifest = {key: value for key, value in manifests["JERC"].items() if key != "site"}
        if abby_manifest != jerc_manifest:
            raise AssertionError("paired-site manifest contracts differ beyond site")
        if manifests["ABBY"]["site"] != "ABBY" or manifests["JERC"]["site"] != "JERC":
            raise AssertionError("paired-site manifest site identity failed")
        if figure_names["ABBY"] != figure_names["JERC"]:
            raise AssertionError("paired-site figure membership differs beyond site prefix")
        if loaded["ABBY"].metadata["site"] != "ABBY" or loaded["JERC"].metadata["site"] != "JERC":
            raise AssertionError("paired synthetic embedded-site validation failed")
        return {
            "status": "pass",
            "sites": ["ABBY", "JERC"],
            "numeric_products_equal": True,
            "manifest_difference": "site_only",
            "figure_membership_equal_after_site_prefix": True,
            "figure_count_per_site": 44,
            "unsupported_member_rows_retained": len(parameters) * 16,
            "gap_rows_and_plots_exercised": True,
        }
    finally:
        EXPECTED_HOURS = original_expected_hours


def manifest_contract(
    args: argparse.Namespace,
    mappings: dict[str, str],
    log_parameters: frozenset[str],
    interfaces: dict[str, Any],
    observation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": INPUT_MANIFEST_SCHEMA,
        "site": args.site,
        "pickle_dir": str(args.pickle_dir),
        "control_paramfile": str(args.control_paramfile),
        "parameter_pickles": mappings,
        "log_parameters": sorted(log_parameters),
        "parameters": list(mappings),
        "targets": list(interfaces["targets"]),
        "statistics": list(interfaces["statistics"]),
        "observations": [list(item) for item in interfaces["observations"]],
        "observation_sha256": {row["variable"]: row["sha256"] for row in observation_rows},
        "compensation": [list(item) for item in interfaces["compensation"]],
        "hr_pools": [list(item) for item in interfaces["hr_pools"]],
        "hr_n_limiter": interfaces["hr_n_limiter"],
        "hr_p_limiter": interfaces["hr_p_limiter"],
        "litter_ratios": [list(item) for item in interfaces["litter_ratios"]],
        "litter_ratio_support_contract": "retain_all_members; blank_ratio_for_unsupported_total; record_supported_and_rejection_reason; omit_invalid_plot_points",
        "restart_root": None if interfaces["restart_root"] is None else str(interfaces["restart_root"]),
        "parameter_restarts": interfaces["restart_mappings"],
        "config_dir": None if interfaces["config_dir"] is None else str(interfaces["config_dir"]),
        "parameter_dir": None if interfaces["parameter_dir"] is None else str(interfaces["parameter_dir"]),
        "parameter_configs": interfaces["config_mappings"],
        "parameter_files": interfaces["parameter_file_mappings"],
        "spinup_components": {target: list(components) for target, components in SPINUP_COMPONENTS.items()},
        "spinup_units": SPINUP_UNITS,
        "spinup_scalar_definition": "sum numpy.nansum(component[:]) across the eight declared vertical components",
        "score_support_contract": "finite complete 100-member ensemble and nonzero ensemble median; otherwise explicit unsupported reason",
        "required_raw_variables": list(required_raw_variables(interfaces)),
        "regression_results": None if args.regression_results is None else str(args.regression_results),
        "expected_hours": EXPECTED_HOURS,
        "year_range": [2018, 2024],
        "member_count_per_parameter": 100,
        "score": "100 * (P95 - P05) / abs(ensemble median)",
    }


def validate_all(
    args: argparse.Namespace,
    mappings: dict[str, str],
    log_parameters: frozenset[str],
    interfaces: dict[str, Any],
    observation_rows: list[dict[str, Any]],
    expected_manifest: dict[str, Any] | None = None,
) -> tuple[list[CaseSummary], dict[str, Any], np.ndarray]:
    if not args.pickle_dir.is_absolute() or not args.pickle_dir.is_dir():
        raise ValueError("--pickle-dir must be an existing absolute directory")
    if not args.control_paramfile.is_absolute() or not args.control_paramfile.is_file():
        raise ValueError("--control-paramfile must be an existing absolute file")
    if interfaces["restart_root"] is not None:
        restart_root = interfaces["restart_root"]
        if not restart_root.is_dir():
            raise ValueError("--restart-root must be an existing absolute directory")
        observed_cases = {path.name for path in restart_root.iterdir() if path.is_dir()}
        expected_cases = set(interfaces["restart_mappings"].values())
        if observed_cases != expected_cases:
            raise ValueError(
                "restart root must contain exactly the mapped cases; "
                f"missing={sorted(expected_cases - observed_cases)} extra={sorted(observed_cases - expected_cases)}"
            )
    if interfaces["config_dir"] is not None:
        for root, mapped, label in (
            (interfaces["config_dir"], interfaces["config_mappings"], "config"),
            (interfaces["parameter_dir"], interfaces["parameter_file_mappings"], "parameter file"),
        ):
            if not root.is_dir():
                raise ValueError(f"{label} root must be an existing absolute directory: {root}")
            observed = {path.name for path in root.iterdir() if path.is_file()}
            expected = set(mapped.values())
            if observed != expected:
                raise ValueError(
                    f"{label} root must contain exactly the mapped files; "
                    f"missing={sorted(expected - observed)} extra={sorted(observed - expected)}"
                )
    expected_basenames = set(mappings.values())
    observed_basenames = {path.name for path in args.pickle_dir.glob("*.pkl") if path.is_file()}
    if observed_basenames != expected_basenames:
        missing = sorted(expected_basenames - observed_basenames)
        extra = sorted(observed_basenames - expected_basenames)
        raise ValueError(f"pickle directory must contain exactly the mapped files; missing={missing}, extra={extra}")
    regression_names = ("parameter_metadata.csv", "member_metrics.csv", "sensitivity_scores.csv", "response_curves.csv")
    regression_hashes: dict[str, str] = {}
    if args.regression_results is not None:
        if not args.regression_results.is_absolute() or not args.regression_results.is_dir():
            raise ValueError("--regression-results must identify an existing absolute directory")
        regression_hashes = {name: digest(args.regression_results / name) for name in regression_names}
    contract = manifest_contract(args, mappings, log_parameters, interfaces, observation_rows)
    contract["regression_sha256"] = regression_hashes
    control_hash = digest(args.control_paramfile)
    tool_hash = digest(Path(__file__).resolve())
    pickle_hashes: dict[str, str] = {}
    if expected_manifest is not None:
        for field in (
            "schema", "site", "pickle_dir", "control_paramfile", "parameter_pickles",
            "log_parameters", "parameters", "targets", "statistics", "observations",
            "observation_sha256", "compensation", "hr_pools", "hr_n_limiter",
            "hr_p_limiter", "litter_ratios", "litter_ratio_support_contract",
            "restart_root", "parameter_restarts", "config_dir", "parameter_dir",
            "parameter_configs", "parameter_files", "spinup_components", "spinup_units",
            "spinup_scalar_definition", "score_support_contract", "required_raw_variables",
            "regression_results", "regression_sha256", "expected_hours", "year_range",
            "member_count_per_parameter", "score",
        ):
            if expected_manifest.get(field) != contract[field]:
                raise ValueError(f"validated manifest field changed: {field}")
        if expected_manifest.get("status") != "pass":
            raise ValueError("validated manifest status is not pass")
        if expected_manifest.get("control_paramfile_sha256") != control_hash:
            raise ValueError("control parameter file hash differs from validated manifest")
        if expected_manifest.get("tool_sha256") != tool_hash:
            raise ValueError("tool hash differs from validated manifest")
    summaries: list[CaseSummary] = []
    reference_taxis: np.ndarray | None = None
    with xr.open_dataset(args.control_paramfile) as control_dataset:
        for parameter, basename in mappings.items():
            path = args.pickle_dir / basename
            if not path.is_file() or path.parent.resolve() != args.pickle_dir.resolve():
                raise FileNotFoundError(f"missing or out-of-root pickle for {parameter}: {path}")
            pickle_hash = digest(path)
            pickle_hashes[parameter] = pickle_hash
            if expected_manifest is not None:
                expected_hash = expected_manifest.get("pickle_sha256", {}).get(parameter)
                if expected_hash != pickle_hash:
                    raise ValueError(f"pickle hash changed for {parameter}")
            print(f"loading parameter={parameter} pickle={path.name}", flush=True)
            summary, taxis = load_case_summary(
                parameter,
                path,
                pickle_hash,
                "log10" if parameter in log_parameters else "linear",
                control_dataset,
                reference_taxis,
                interfaces,
                args.site,
            )
            if interfaces["restart_mappings"]:
                summary = load_spinup_state(
                    summary,
                    interfaces["restart_root"],
                    interfaces["restart_mappings"][parameter],
                )
            if interfaces["config_mappings"]:
                config_path = interfaces["config_dir"] / interfaces["config_mappings"][parameter]
                parameter_path = interfaces["parameter_dir"] / interfaces["parameter_file_mappings"][parameter]
                config_text = config_path.read_text()
                if re.search(r"^use_vertsoilc\s*=\s*\.true\.\s*$", config_text, re.MULTILINE) is None:
                    raise ValueError(f"vertical soil carbon is not active in {config_path}")
                if interfaces["parameter_file_mappings"][parameter] not in config_text:
                    raise ValueError(f"config does not bind the mapped parameter file: {config_path}")
                records = [line.split() for line in parameter_path.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")]
                if len(records) != 1 or len(records[0]) < 4:
                    raise ValueError(f"parameter file must contain one four-field declaration: {parameter_path}")
                declared_name, declared_selector, declared_min, declared_max = records[0][:4]
                if declared_name != parameter:
                    raise ValueError(f"parameter name differs from pickle: {parameter_path}")
                if not np.allclose(
                    [float(declared_min), float(declared_max)], [summary.pmin, summary.pmax],
                    rtol=0.0, atol=max(abs(summary.pmin), abs(summary.pmax), 1.0) * 1e-12,
                ):
                    raise ValueError(f"parameter bounds differ from pickle: {parameter_path}")
                summary.metadata["provenance"] = {
                    "config_path": str(config_path), "config_sha256": digest(config_path),
                    "parameter_file_path": str(parameter_path), "parameter_file_sha256": digest(parameter_path),
                    "parameter_file_second_field": int(declared_selector),
                    "declared_pmin": float(declared_min), "declared_pmax": float(declared_max),
                }
            if reference_taxis is None:
                reference_taxis = taxis.copy()
            summaries.append(summary)
            print(f"validated parameter={parameter}", flush=True)
    restart_cases = {
        summary.parameter: summary.spinup_metadata for summary in summaries if summary.spinup_metadata
    }
    provenance_identity = {
        summary.parameter: summary.metadata.get("provenance", {}) for summary in summaries
    }
    if expected_manifest is not None:
        if expected_manifest.get("restart_cases") != restart_cases:
            raise ValueError("restart file identity or component support differs from validated manifest")
        if expected_manifest.get("provenance_sha256") != provenance_identity:
            raise ValueError("config or parameter provenance differs from validated manifest")
    manifest = {
        **contract,
        "status": "pass",
        "created_at_utc": utc_now(),
        "tool_path": str(Path(__file__).resolve()),
        "tool_sha256": tool_hash,
        "control_paramfile_sha256": control_hash,
        "regression_sha256": regression_hashes,
        "pickle_sha256": pickle_hashes,
        "cases": {summary.parameter: summary.metadata for summary in summaries},
        "restart_cases": restart_cases,
        "provenance_sha256": provenance_identity,
        "native_parameter_markers": {
            summary.parameter: {"status": summary.native_status, "value": summary.native_value}
            for summary in summaries
        },
    }
    if reference_taxis is None:
        raise RuntimeError("no parameter cases were validated")
    return summaries, manifest, reference_taxis


def run_preflight(args: argparse.Namespace, mappings: dict[str, str], log_parameters: frozenset[str]) -> None:
    if args.output.exists():
        raise FileExistsError(f"refusing to replace existing preflight artifacts: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = args.output.with_name(f".{args.output.name}.staging.{os.getpid()}")
    if staging.exists():
        raise FileExistsError(f"preflight staging directory already exists: {staging}")
    try:
        parameters = tuple(mappings)
        interfaces = parse_interfaces(args, parameters)
        fixture = fixture_checks(parameters)
        observation_rows = load_observation_rows(interfaces["observations"])
        summaries, manifest, _ = validate_all(args, mappings, log_parameters, interfaces, observation_rows)
        manifest["fixture"] = fixture
        manifest["observation_summary"] = observation_rows
        staging.mkdir()
        atomic_json(staging / "input_manifest.json", manifest)
        receipt = {
            "schema": VALIDATION_RECEIPT_SCHEMA,
            "status": "pass",
            "created_at_utc": utc_now(),
            "input_manifest": str(args.output / "input_manifest.json"),
            "parameters": len(summaries),
            "fixture": fixture,
        }
        atomic_json(staging / "validation_receipt.json", receipt)
        os.replace(staging, args.output)
        print(
            f"OAT_PREFLIGHT_PASS parameters={len(summaries)} members={len(summaries) * 100} "
            f"hours={EXPECTED_HOURS} observations={len(observation_rows)}",
            flush=True,
        )
    except Exception as exc:
        if not args.output.exists():
            args.output.mkdir()
            atomic_json(args.output / "validation_receipt.json", {"schema": VALIDATION_RECEIPT_SCHEMA, "status": "fail", "created_at_utc": utc_now(), "error_type": type(exc).__name__, "error": str(exc)})
        raise


def run_diagnostic(args: argparse.Namespace, mappings: dict[str, str], log_parameters: frozenset[str]) -> None:
    manifest = json.loads(args.manifest.read_text())
    interfaces = parse_interfaces(args, tuple(mappings))
    observation_rows = load_observation_rows(interfaces["observations"])
    summaries, current_manifest, taxis = validate_all(args, mappings, log_parameters, interfaces, observation_rows, expected_manifest=manifest)
    staging = args.output.with_name(f".{args.output.name}.staging.{os.getpid()}")
    if args.output.exists():
        raise FileExistsError(f"refusing to replace existing result directory: {args.output}")
    if staging.exists():
        raise FileExistsError(f"staging directory already exists: {staging}")
    staging.mkdir(parents=True)
    parameter_rows, member_rows, score_rows, curve_rows = build_rows(
        summaries, interfaces["targets"], interfaces["statistics"]
    )
    write_csv(staging / "parameter_metadata.csv", list(parameter_rows[0]), parameter_rows)
    write_csv(staging / "member_metrics.csv", list(member_rows[0]), member_rows)
    write_csv(staging / "sensitivity_scores.csv", list(score_rows[0]), score_rows)
    write_csv(staging / "response_curves.csv", list(curve_rows[0]), curve_rows)
    spinup_member_rows: list[dict[str, Any]] = []
    spinup_score_rows: list[dict[str, Any]] = []
    spinup_curve_rows: list[dict[str, Any]] = []
    if interfaces["restart_mappings"]:
        spinup_member_rows, spinup_score_rows, spinup_curve_rows = build_spinup_rows(summaries)
        write_csv(staging / "spinup_member_metrics.csv", list(spinup_member_rows[0]), spinup_member_rows)
        write_csv(staging / "spinup_sensitivity_scores.csv", list(spinup_score_rows[0]), spinup_score_rows)
        write_csv(staging / "spinup_response_curves.csv", list(spinup_curve_rows[0]), spinup_curve_rows)
    if observation_rows:
        write_csv(staging / "observation_summary.csv", list(observation_rows[0]), observation_rows)
    hr_metrics, hr_curves, litter_members, litter_timeseries, litter_curves = build_specialized_rows(summaries, taxis)
    if hr_metrics:
        write_csv(staging / "hr_pathway_metrics.csv", list(hr_metrics[0]), hr_metrics)
        write_csv(staging / "hr_pathway_curves.csv", list(hr_curves[0]), hr_curves)
    if litter_members:
        write_csv(staging / "litter_ratio_member_metrics.csv", list(litter_members[0]), litter_members)
        write_csv(staging / "litter_ratio_timeseries.csv", list(litter_timeseries[0]), litter_timeseries)
        write_csv(staging / "litter_ratio_curves.csv", list(litter_curves[0]), litter_curves)
    figures = [
        *plot_response_atlases(
            staging, summaries, interfaces["targets"], observation_rows, args.site,
            interfaces["statistics"],
        ),
        *plot_heatmaps(
            staging, score_rows, interfaces["targets"], args.site, tuple(mappings),
            interfaces["statistics"],
        ),
        *plot_compensation(staging, summaries, interfaces["compensation"], args.site),
        *plot_hr_pathways(staging, summaries, args.site),
        *plot_litter_ratios(staging, summaries, taxis, args.site),
        *(plot_spinup_atlases(staging, summaries, args.site) if interfaces["restart_mappings"] else []),
        *([plot_spinup_heatmap(staging, spinup_score_rows, args.site, tuple(mappings))]
          if interfaces["restart_mappings"] else []),
    ]
    expected_figure_count = (
        len(interfaces["statistics"]) * len(interfaces["targets"])
        + len(interfaces["statistics"]) + len(interfaces["compensation"])
        + (1 if interfaces["hr_pools"] else 0) + 2 * len(interfaces["litter_ratios"])
        + (len(SPINUP_COMPONENTS) + 1 if interfaces["restart_mappings"] else 0)
    )
    if len(figures) != expected_figure_count:
        raise RuntimeError(f"expected {expected_figure_count} figures, generated {len(figures)}")
    expected_counts = expected_artifact_counts(interfaces, len(mappings))
    observed_counts = {name: sum(1 for _ in (staging / name).open()) - 1 for name in expected_counts}
    if observed_counts != expected_counts:
        raise RuntimeError(f"artifact row counts differ: expected={expected_counts}, observed={observed_counts}")
    for name, expected_hash in manifest["regression_sha256"].items():
        observed_hash = digest(staging / name)
        if observed_hash != expected_hash:
            raise RuntimeError(f"core regression hash mismatch for {name}: {observed_hash} != {expected_hash}")
    artifacts = {}
    for path in sorted(staging.iterdir()):
        if path.is_file() and path.name != "output_manifest.json":
            artifacts[path.name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    output_manifest = {
        "schema": OUTPUT_MANIFEST_SCHEMA,
        "status": "pass",
        "site": args.site,
        "created_at_utc": utc_now(),
        "input_manifest_path": str(args.manifest),
        "input_manifest_sha256": digest(args.manifest),
        "validated_input_identity": current_manifest,
        "row_counts": observed_counts,
        "figure_count": expected_figure_count,
        "artifacts": artifacts,
        "compensation_normalization": "100 * (response - ensemble median) / abs(ensemble median)",
        "spinup_scalar_definition": current_manifest["spinup_scalar_definition"],
    }
    atomic_json(staging / "output_manifest.json", output_manifest)
    os.replace(staging, args.output)
    print(
        f"OAT_DIAGNOSTIC_GENERATE_PASS parameters={len(summaries)} member_rows={len(member_rows)} "
        f"score_rows={len(score_rows)} figures={expected_figure_count}",
        flush=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True)
    parser.add_argument("--pickle-dir", required=True, type=Path)
    parser.add_argument("--parameter-pickle", required=True, action="append", default=[])
    parser.add_argument("--log-parameters", required=True)
    parser.add_argument("--control-paramfile", required=True, type=Path)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--statistic", action="append", default=[])
    parser.add_argument("--observation", action="append", default=[])
    parser.add_argument("--compensation", action="append", default=[])
    parser.add_argument("--hr-pool", action="append", default=[])
    parser.add_argument("--hr-n-limiter")
    parser.add_argument("--hr-p-limiter")
    parser.add_argument("--litter-ratio", action="append", default=[])
    parser.add_argument("--restart-root", type=Path)
    parser.add_argument("--parameter-restart", action="append", default=[])
    parser.add_argument("--config-dir", type=Path)
    parser.add_argument("--parameter-dir", type=Path)
    parser.add_argument("--parameter-config", action="append", default=[])
    parser.add_argument("--parameter-file", action="append", default=[])
    parser.add_argument("--regression-results", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--manifest", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.site = validate_declared_site(args.site)
    mappings = parse_mapping(args.parameter_pickle)
    log_parameters = parse_log_parameters(args.log_parameters, tuple(mappings))
    if not args.output.is_absolute():
        raise ValueError("--output must be absolute")
    if args.validate_only:
        run_preflight(args, mappings, log_parameters)
    else:
        if args.manifest is None or not args.manifest.is_absolute() or not args.manifest.is_file():
            raise ValueError("--manifest must identify an existing absolute input manifest")
        run_diagnostic(args, mappings, log_parameters)


if __name__ == "__main__":
    main()
