#!/usr/bin/env python3
"""Strict OAT nutrient-stress diagnostics for explicit ELM ensemble pickles."""

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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import model_ELM  # noqa: F401,E402  Required for ELMcase pickle loading.

EXPECTED_HOURS = 7 * 365 * 24
MEMBERS = 100
PARAMETER_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
STATISTICS = ("mean", "temporal_std")
INPUT_SCHEMA = "elm_oat_nutrient_input_manifest_v1"
RECEIPT_SCHEMA = "elm_oat_nutrient_validation_receipt_v1"
OUTPUT_SCHEMA = "elm_oat_nutrient_output_manifest_v1"

RAW_UNITS = {
    "FPI": "1",
    "FPI_P": "1",
    "POTENTIAL_IMMOB": "gN m-2 day-1",
    "ACTUAL_IMMOB": "gN m-2 day-1",
    "POTENTIAL_IMMOB_P": "gP m-2 day-1",
    "ACTUAL_IMMOB_P": "gP m-2 day-1",
    "PLANT_NDEMAND_COL": "gN m-2 day-1",
    "SMINN_TO_PLANT": "gN m-2 day-1",
    "PLANT_PDEMAND_COL": "gP m-2 day-1",
    "SMINP_TO_PLANT": "gP m-2 day-1",
    "GPP": "gC m-2 day-1",
    "SR": "gC m-2 day-1",
    "HR": "gC m-2 day-1",
    "CWDC_HR": "gC m-2 day-1",
    "LITR1_HR": "gC m-2 day-1",
    "LITR2_HR": "gC m-2 day-1",
    "LITR3_HR": "gC m-2 day-1",
    "SOIL1_HR": "gC m-2 day-1",
    "SOIL2_HR": "gC m-2 day-1",
    "SOIL3_HR": "gC m-2 day-1",
    "SOIL4_HR": "gC m-2 day-1",
    "SMINN": "gN m-2",
    "GROSS_NMIN": "gN m-2 day-1",
    "NET_NMIN": "gN m-2 day-1",
    "SOLUTIONP": "gP m-2",
    "GROSS_PMIN": "gP m-2 day-1",
    "NET_PMIN": "gP m-2 day-1",
}
RAW_VARIABLES = tuple(RAW_UNITS)
NONNEGATIVE = frozenset({
    "POTENTIAL_IMMOB", "ACTUAL_IMMOB", "POTENTIAL_IMMOB_P", "ACTUAL_IMMOB_P",
    "PLANT_NDEMAND_COL", "SMINN_TO_PLANT", "PLANT_PDEMAND_COL", "SMINP_TO_PLANT",
})
RATIOS = {
    "microbial_n_satisfaction": ("ACTUAL_IMMOB", "POTENTIAL_IMMOB", "1"),
    "microbial_p_satisfaction": ("ACTUAL_IMMOB_P", "POTENTIAL_IMMOB_P", "1"),
    "plant_n_satisfaction": ("SMINN_TO_PLANT", "PLANT_NDEMAND_COL", "1"),
    "plant_p_satisfaction": ("SMINP_TO_PLANT", "PLANT_PDEMAND_COL", "1"),
}
POOL_HR = ("CWDC_HR", "LITR1_HR", "LITR2_HR", "LITR3_HR", "SOIL1_HR", "SOIL2_HR", "SOIL3_HR", "SOIL4_HR")
FIGURES = (
    "ABBY_fpi_response.png",
    "ABBY_microbial_n_response.png",
    "ABBY_microbial_p_response.png",
    "ABBY_plant_n_response.png",
    "ABBY_plant_p_response.png",
    "ABBY_gpp_response.png",
    "ABBY_sr_response.png",
    "ABBY_hr_response.png",
    "ABBY_pool_hr_response.png",
    "ABBY_n_cycle_response.png",
    "ABBY_p_cycle_response.png",
)


@dataclass
class Summary:
    parameter: str
    path: Path
    sha256: str
    samples: np.ndarray
    normalized: np.ndarray
    pmin: float
    pmax: float
    selector: int
    native_value: float | None
    native_status: str
    statistics: dict[str, dict[str, np.ndarray]]
    ratios: dict[str, np.ndarray]
    ratio_support: dict[str, np.ndarray]
    ratio_reasons: dict[str, np.ndarray]
    metadata: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_mappings(items: list[str]) -> dict[str, str]:
    mappings: dict[str, str] = {}
    basenames: set[str] = set()
    for item in items:
        if ":" not in item:
            raise ValueError(f"invalid parameter mapping: {item!r}")
        parameter, basename = item.split(":", 1)
        if PARAMETER_NAME.fullmatch(parameter) is None or basename != Path(basename).name:
            raise ValueError(f"mapping must be PARAMETER:EXACT_BASENAME: {item!r}")
        if any(token in basename for token in ("*", "?", "[", "]")):
            raise ValueError("globs are prohibited in parameter mappings")
        if parameter in mappings or basename in basenames:
            raise ValueError(f"duplicate mapping: {item!r}")
        mappings[parameter] = basename
        basenames.add(basename)
    if tuple(mappings) != ("cn_s1", "cn_s2", "cn_s3", "cn_s4"):
        raise ValueError("ordered parameter inventory must be cn_s1,cn_s2,cn_s3,cn_s4")
    return mappings


def parse_parameter_paths(items: list[str], option: str, parameters: tuple[str, ...]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for item in items:
        if ":" not in item:
            raise ValueError(f"{option} requires PARAMETER:ABSOLUTE_PATH: {item!r}")
        parameter, raw_path = item.split(":", 1)
        path = Path(raw_path)
        if parameter in parsed or parameter not in parameters or not path.is_absolute():
            raise ValueError(f"invalid or duplicate {option} mapping: {item!r}")
        parsed[parameter] = path
    if tuple(parsed) != parameters:
        raise ValueError(f"{option} must map the exact ordered parameter inventory")
    return parsed


def member_matrix(case: Any, variable: str) -> np.ndarray:
    output = getattr(case, "output", None)
    if not isinstance(output, dict) or variable not in output:
        raise ValueError(f"missing case.output[{variable!r}]")
    values = np.asarray(output[variable], dtype=np.float64)
    if values.shape == (EXPECTED_HOURS, MEMBERS):
        matrix = values
    elif values.shape == (MEMBERS, EXPECTED_HOURS):
        matrix = values.T
    else:
        raise ValueError(f"{variable}: expected ({EXPECTED_HOURS}, {MEMBERS}) time x member, got {values.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{variable}: contains non-finite values")
    return matrix


def validate_time(case: Any, reference: np.ndarray | None) -> np.ndarray:
    output = getattr(case, "output", None)
    if not isinstance(output, dict) or "taxis" not in output:
        raise ValueError("missing case.output['taxis']")
    taxis = np.asarray(output["taxis"], dtype=np.float64).reshape(-1)
    expected = 2018.0 + np.arange(EXPECTED_HOURS, dtype=np.float64) / 8760.0
    if taxis.size != EXPECTED_HOURS or not np.allclose(taxis, expected, rtol=0.0, atol=1e-11):
        raise ValueError("time axis is not exact 2018--2024 no-leap hourly support")
    if reference is not None and not np.array_equal(taxis, reference):
        raise ValueError("time axis differs across parameter cases")
    if int(getattr(case, "postproc_startyear", -1)) != 2018 or int(getattr(case, "postproc_endyear", -1)) != 2024:
        raise ValueError("postprocessing years are not exactly 2018--2024")
    return taxis


def parameter_values(case: Any, parameter: str) -> tuple[np.ndarray, float, float, int]:
    if [str(item) for item in getattr(case, "ensemble_parms", [])] != [parameter]:
        raise ValueError(f"ensemble_parms does not identify only {parameter}")
    if int(getattr(case, "nsamples", -1)) != MEMBERS:
        raise ValueError("nsamples must equal 100")
    values = np.asarray(getattr(case, "samples", None), dtype=np.float64)
    if values.shape == (1, MEMBERS):
        samples = values[0]
    elif values.shape in {(MEMBERS,), (MEMBERS, 1)}:
        samples = values.reshape(-1)
    else:
        raise ValueError(f"unexpected parameter sample shape: {values.shape}")
    pmin_values = np.asarray(getattr(case, "ensemble_pmin", []), dtype=np.float64).reshape(-1)
    pmax_values = np.asarray(getattr(case, "ensemble_pmax", []), dtype=np.float64).reshape(-1)
    selectors = np.asarray(getattr(case, "ensemble_pfts", []), dtype=int).reshape(-1)
    if pmin_values.size != 1 or pmax_values.size != 1 or selectors.size != 1:
        raise ValueError("parameter bounds and selector must each contain one value")
    pmin, pmax = float(pmin_values[0]), float(pmax_values[0])
    expected_bounds = {"cn_s1": (9.0, 18.0), "cn_s2": (9.0, 18.0), "cn_s3": (7.0, 16.0), "cn_s4": (7.0, 16.0)}
    if (pmin, pmax) != expected_bounds[parameter]:
        raise ValueError(f"{parameter}: embedded bounds {(pmin, pmax)} differ from {expected_bounds[parameter]}")
    if not np.all(np.isfinite(samples)) or np.any(samples < pmin) or np.any(samples > pmax):
        raise ValueError(f"{parameter}: samples are non-finite or out of range")
    selector = int(selectors[0])
    if selector != 0:
        raise ValueError(f"{parameter}: selector must equal declared selector 0, got {selector}")
    return samples, pmin, pmax, selector


def native_value(dataset: xr.Dataset, parameter: str, selector: int, pmin: float, pmax: float) -> tuple[float | None, str]:
    if parameter not in dataset.variables:
        return None, "missing_variable"
    values = np.asarray(dataset[parameter].values, dtype=np.float64)
    try:
        selected = values[selector] if selector > 0 else values
    except (IndexError, TypeError):
        return None, "unresolved_selector"
    finite = selected.reshape(-1)[np.isfinite(selected.reshape(-1))]
    if not finite.size or not np.allclose(finite, finite[0], rtol=1e-12, atol=0.0):
        return None, "nonfinite_or_heterogeneous"
    value = float(finite[0])
    if not pmin <= value <= pmax:
        return None, "outside_ensemble_range"
    return value, "available"


def accumulated_ratio(numerator: np.ndarray, denominator: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    numerator_total = np.sum(numerator, axis=0)
    denominator_total = np.sum(denominator, axis=0)
    support = np.isfinite(numerator_total) & np.isfinite(denominator_total) & (denominator_total > 0.0)
    ratio = np.full(MEMBERS, np.nan, dtype=np.float64)
    np.divide(numerator_total, denominator_total, out=ratio, where=support)
    reasons = np.full(MEMBERS, "", dtype=object)
    reasons[~np.isfinite(numerator_total) & np.isfinite(denominator_total)] = "nonfinite_numerator_total"
    reasons[np.isfinite(numerator_total) & ~np.isfinite(denominator_total)] = "nonfinite_denominator_total"
    reasons[~np.isfinite(numerator_total) & ~np.isfinite(denominator_total)] = "nonfinite_numerator_and_denominator_totals"
    reasons[np.isfinite(numerator_total) & np.isfinite(denominator_total) & (denominator_total <= 0.0)] = "nonpositive_denominator_total"
    return ratio, support, reasons


def load_summary(parameter: str, path: Path, file_hash: str, control: xr.Dataset, reference: np.ndarray | None, site: str) -> tuple[Summary, np.ndarray]:
    with path.open("rb") as handle:
        case = pickle.load(handle)
    if str(getattr(case, "site", "")) != site:
        raise ValueError(f"{path.name}: site must be {site}")
    samples, pmin, pmax, selector = parameter_values(case, parameter)
    taxis = validate_time(case, reference)
    postproc = {str(item) for item in getattr(case, "postproc_vars", [])}
    missing = sorted(set(RAW_VARIABLES) - postproc)
    if missing:
        raise ValueError(f"{path.name}: postproc_vars missing {missing}")
    raw = {variable: member_matrix(case, variable) for variable in RAW_VARIABLES}
    for variable in NONNEGATIVE:
        if np.any(raw[variable] < 0.0):
            raise ValueError(f"{variable}: negative values violate the locked ratio semantics")
    for variable in ("FPI", "FPI_P"):
        if np.any((raw[variable] < 0.0) | (raw[variable] > 1.0)):
            raise ValueError(f"{variable}: values must remain within [0,1]")
    statistics = {
        variable: {"mean": np.mean(matrix, axis=0), "temporal_std": np.std(matrix, axis=0, ddof=0)}
        for variable, matrix in raw.items()
    }
    ratios: dict[str, np.ndarray] = {}
    supports: dict[str, np.ndarray] = {}
    reasons: dict[str, np.ndarray] = {}
    for label, (numerator, denominator, _) in RATIOS.items():
        ratios[label], supports[label], reasons[label] = accumulated_ratio(raw[numerator], raw[denominator])
    native, native_status = native_value(control, parameter, selector, pmin, pmax)
    normalized = (samples - pmin) / (pmax - pmin)
    summary = Summary(
        parameter=parameter,
        path=path,
        sha256=file_hash,
        samples=samples.copy(),
        normalized=normalized,
        pmin=pmin,
        pmax=pmax,
        selector=selector,
        native_value=native,
        native_status=native_status,
        statistics=statistics,
        ratios=ratios,
        ratio_support=supports,
        ratio_reasons=reasons,
        metadata={
            "case_name": str(getattr(case, "casename", "")),
            "site": site,
            "members": MEMBERS,
            "hours": EXPECTED_HOURS,
            "postproc_startyear": int(getattr(case, "postproc_startyear")),
            "postproc_endyear": int(getattr(case, "postproc_endyear")),
        },
    )
    del raw, case
    gc.collect()
    return summary, taxis


def bins(x: np.ndarray, y: np.ndarray) -> tuple[list[dict[str, Any]], np.ndarray]:
    order = np.argsort(x, kind="stable")
    groups = np.array_split(order, 10)
    membership = np.empty(MEMBERS, dtype=int)
    rows: list[dict[str, Any]] = []
    for index, indices in enumerate(groups, start=1):
        membership[indices] = index
        finite = np.isfinite(y[indices])
        rows.append({
            "bin": index,
            "count": int(indices.size),
            "valid_count": int(np.sum(finite)),
            "rejected_count": int(indices.size - np.sum(finite)),
            "x_median": float(np.median(x[indices])),
            "x_min": float(np.min(x[indices])),
            "x_max": float(np.max(x[indices])),
            "response_median": float(np.median(y[indices][finite])) if np.any(finite) else "",
        })
    return rows, membership


def fixture_checks() -> dict[str, Any]:
    numerator = np.tile(np.arange(1.0, 101.0), (24, 1))
    denominator = numerator * 2.0
    ratio, support, reasons = accumulated_ratio(numerator, denominator)
    if not np.allclose(ratio, 0.5) or not np.all(support) or np.any(reasons != ""):
        raise AssertionError("accumulated-ratio fixture failed")
    denominator[:, -1] = 0.0
    ratio, support, reasons = accumulated_ratio(numerator, denominator)
    if support[-1] or np.isfinite(ratio[-1]) or reasons[-1] != "nonpositive_denominator_total":
        raise AssertionError("explicit-gap fixture failed")
    test_bins, membership = bins(np.linspace(0.0, 1.0, MEMBERS), np.linspace(1.0, 2.0, MEMBERS))
    if len(test_bins) != 10 or sorted(np.bincount(membership)[1:].tolist()) != [10] * 10:
        raise AssertionError("equal-count-bin fixture failed")
    return {"status": "pass", "ratio_order": "sum_numerator_then_sum_denominator_then_divide", "gap_contract": "explicit", "bins": 10}


def contract(args: argparse.Namespace, mappings: dict[str, str], config_files: dict[str, Path], parameter_files: dict[str, Path]) -> dict[str, Any]:
    return {
        "schema": INPUT_SCHEMA,
        "site": args.site,
        "pickle_dir": str(args.pickle_dir),
        "parameter_pickles": mappings,
        "parameters": list(mappings),
        "control_paramfile": str(args.control_paramfile),
        "config_files": {key: str(value) for key, value in config_files.items()},
        "parameter_files": {key: str(value) for key, value in parameter_files.items()},
        "raw_variables": list(RAW_VARIABLES),
        "raw_units": RAW_UNITS,
        "ratios": {key: list(value) for key, value in RATIOS.items()},
        "statistics": list(STATISTICS),
        "expected_hours": EXPECTED_HOURS,
        "members_per_parameter": MEMBERS,
        "figure_names": list(FIGURES),
        "expected_rows": {"parameter_metadata.csv": 4, "metric_definitions.csv": 31, "member_metrics.csv": 400, "response_curves.csv": 25520, "ratio_support.csv": 1600},
        "input_membership": "consume_only_explicit_mappings; ignore_unrelated_directory_files",
    }


def validate_inputs(args: argparse.Namespace, mappings: dict[str, str], config_files: dict[str, Path], parameter_files: dict[str, Path], expected: dict[str, Any] | None = None) -> tuple[list[Summary], dict[str, Any]]:
    if args.site != "ABBY":
        raise ValueError("Iter008 contract requires --site ABBY")
    if not args.pickle_dir.is_absolute() or not args.pickle_dir.is_dir():
        raise ValueError("--pickle-dir must be an existing absolute directory")
    if not args.control_paramfile.is_absolute() or not args.control_paramfile.is_file():
        raise ValueError("--control-paramfile must be an existing absolute file")
    current_contract = contract(args, mappings, config_files, parameter_files)
    control_hash = digest(args.control_paramfile)
    tool_hash = digest(Path(__file__).resolve())
    dependency_files: dict[str, dict[str, Any]] = {}
    for family, paths in (("config", config_files), ("parameter", parameter_files)):
        for parameter, path in paths.items():
            if not path.is_file():
                raise FileNotFoundError(f"missing {family} provenance file for {parameter}: {path}")
            dependency_files[f"{family}:{parameter}"] = {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
    if expected is not None:
        for field, value in current_contract.items():
            if expected.get(field) != value:
                raise ValueError(f"validated manifest field changed: {field}")
        if expected.get("status") != "pass" or expected.get("control_paramfile_sha256") != control_hash or expected.get("tool_sha256") != tool_hash:
            raise ValueError("validated manifest identity changed")
        if expected.get("dependency_files") != dependency_files:
            raise ValueError("config or parameter-file provenance changed")
    summaries: list[Summary] = []
    hashes: dict[str, str] = {}
    reference: np.ndarray | None = None
    with xr.open_dataset(args.control_paramfile) as control:
        for parameter, basename in mappings.items():
            path = args.pickle_dir / basename
            if not path.is_file() or path.parent.resolve() != args.pickle_dir.resolve():
                raise FileNotFoundError(f"missing or out-of-root pickle: {path}")
            file_hash = digest(path)
            hashes[parameter] = file_hash
            if expected is not None and expected.get("pickle_sha256", {}).get(parameter) != file_hash:
                raise ValueError(f"pickle hash changed for {parameter}")
            print(f"loading parameter={parameter} pickle={basename}", flush=True)
            summary, taxis = load_summary(parameter, path, file_hash, control, reference, args.site)
            if reference is None:
                reference = taxis.copy()
            summaries.append(summary)
            print(f"validated parameter={parameter}", flush=True)
    manifest = {
        **current_contract,
        "status": "pass",
        "created_at_utc": utc_now(),
        "tool_path": str(Path(__file__).resolve()),
        "tool_sha256": tool_hash,
        "control_paramfile_sha256": control_hash,
        "pickle_sha256": hashes,
        "pickle_files": {
            item.parameter: {"path": str(item.path), "bytes": item.path.stat().st_size, "sha256": item.sha256}
            for item in summaries
        },
        "dependency_files": dependency_files,
        "fixture": fixture_checks(),
        "cases": {item.parameter: item.metadata for item in summaries},
        "native_markers": {item.parameter: {"status": item.native_status, "value": item.native_value} for item in summaries},
    }
    return summaries, manifest


def metric_definitions() -> list[dict[str, Any]]:
    rows = [{"metric": name, "kind": "raw", "numerator": "", "denominator": "", "units": units, "statistics": "mean;temporal_std"} for name, units in RAW_UNITS.items()]
    rows.extend({"metric": label, "kind": "accumulated_ratio", "numerator": numerator, "denominator": denominator, "units": units, "statistics": "integrated_ratio"} for label, (numerator, denominator, units) in RATIOS.items())
    return rows


def build_tables(summaries: list[Summary]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    parameter_rows: list[dict[str, Any]] = []
    member_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    for summary in summaries:
        parameter_rows.append({
            "parameter": summary.parameter, "pickle_path": str(summary.path), "pickle_sha256": summary.sha256,
            "coordinate": "linear", "pmin": summary.pmin, "pmax": summary.pmax,
            "native_value": "" if summary.native_value is None else summary.native_value,
            "native_status": summary.native_status, "selector": summary.selector, "members": MEMBERS,
        })
        for member in range(MEMBERS):
            row: dict[str, Any] = {"parameter": summary.parameter, "member": member + 1, "parameter_value": float(summary.samples[member]), "normalized_parameter": float(summary.normalized[member]), "model_hours": EXPECTED_HOURS}
            for variable in RAW_VARIABLES:
                for statistic in STATISTICS:
                    row[f"{variable}_{statistic}"] = float(summary.statistics[variable][statistic][member])
            for label in RATIOS:
                row[label] = "" if not summary.ratio_support[label][member] else float(summary.ratios[label][member])
                row[f"{label}_supported"] = bool(summary.ratio_support[label][member])
                row[f"{label}_rejection_reason"] = str(summary.ratio_reasons[label][member])
                support_rows.append({
                    "parameter": summary.parameter, "member": member + 1, "ratio": label,
                    "numerator": RATIOS[label][0], "denominator": RATIOS[label][1],
                    "supported": bool(summary.ratio_support[label][member]),
                    "rejection_reason": str(summary.ratio_reasons[label][member]),
                    "value": "" if not summary.ratio_support[label][member] else float(summary.ratios[label][member]),
                })
            member_rows.append(row)
        endpoints = [(variable, statistic, summary.statistics[variable][statistic], RAW_UNITS[variable]) for variable in RAW_VARIABLES for statistic in STATISTICS]
        endpoints.extend((label, "integrated_ratio", summary.ratios[label], "1") for label in RATIOS)
        for metric, statistic, values, units in endpoints:
            bin_rows, membership = bins(summary.samples, values)
            for member in range(MEMBERS):
                curve_rows.append({
                    "parameter": summary.parameter, "metric": metric, "statistic": statistic,
                    "point_type": "member", "member": member + 1, "bin": int(membership[member]),
                    "parameter_value": float(summary.samples[member]), "normalized_parameter": float(summary.normalized[member]),
                    "response": "" if not np.isfinite(values[member]) else float(values[member]), "units": units,
                    "bin_count": "", "valid_count": "", "rejected_count": "", "bin_x_min": "", "bin_x_max": "",
                })
            for item in bin_rows:
                curve_rows.append({
                    "parameter": summary.parameter, "metric": metric, "statistic": statistic,
                    "point_type": "bin_median", "member": "", "bin": item["bin"],
                    "parameter_value": item["x_median"], "normalized_parameter": (item["x_median"] - summary.pmin) / (summary.pmax - summary.pmin),
                    "response": item["response_median"], "units": units, "bin_count": item["count"],
                    "valid_count": item["valid_count"], "rejected_count": item["rejected_count"],
                    "bin_x_min": item["x_min"], "bin_x_max": item["x_max"],
                })
    return parameter_rows, member_rows, curve_rows, support_rows


def plot_curve(axis: Any, summary: Summary, metric: str, statistic: str, color: str, label: str) -> None:
    values = summary.ratios[metric] if statistic == "integrated_ratio" else summary.statistics[metric][statistic]
    finite = np.isfinite(values)
    axis.scatter(summary.samples[finite], values[finite], s=8, alpha=0.20, color=color)
    bin_rows, _ = bins(summary.samples, values)
    valid = [item for item in bin_rows if item["response_median"] != ""]
    axis.plot([item["x_median"] for item in valid], [item["response_median"] for item in valid], "o-", ms=3, lw=1.1, color=color, label=label)
    if summary.native_value is not None:
        axis.axvline(summary.native_value, color="tab:red", ls="--", lw=0.7)
    axis.set_xlabel(summary.parameter)


def plot_parameter_grid(path: Path, summaries: list[Summary], rows: list[list[tuple[str, str, str, str]]], title: str, ylabels: list[str]) -> None:
    figure, axes = plt.subplots(len(rows), len(summaries), figsize=(15, max(4.0, 3.0 * len(rows))), squeeze=False)
    for column, summary in enumerate(summaries):
        for row_index, specifications in enumerate(rows):
            axis = axes[row_index, column]
            for metric, statistic, color, label in specifications:
                plot_curve(axis, summary, metric, statistic, color, label)
            axis.set_title(summary.parameter if row_index == 0 else "")
            axis.set_ylabel(ylabels[row_index] if column == 0 else "")
            axis.legend(fontsize=6)
    figure.suptitle(title)
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    figure.savefig(path, dpi=150)
    plt.close(figure)


def make_figures(output: Path, summaries: list[Summary]) -> None:
    plot_parameter_grid(output / FIGURES[0], summaries, [
        [("FPI", "mean", "tab:blue", "FPI mean"), ("FPI_P", "mean", "tab:orange", "FPI_P mean")],
        [("FPI", "temporal_std", "tab:blue", "FPI temporal SD"), ("FPI_P", "temporal_std", "tab:orange", "FPI_P temporal SD")],
    ], "ABBY nutrient limitation responses", ["fraction", "fraction"])
    paired = [
        (FIGURES[1], "POTENTIAL_IMMOB", "ACTUAL_IMMOB", "microbial_n_satisfaction", "ABBY microbial N response"),
        (FIGURES[2], "POTENTIAL_IMMOB_P", "ACTUAL_IMMOB_P", "microbial_p_satisfaction", "ABBY microbial P response"),
        (FIGURES[3], "PLANT_NDEMAND_COL", "SMINN_TO_PLANT", "plant_n_satisfaction", "ABBY plant N response"),
        (FIGURES[4], "PLANT_PDEMAND_COL", "SMINP_TO_PLANT", "plant_p_satisfaction", "ABBY plant P response"),
    ]
    for filename, demand, actual, ratio, title in paired:
        plot_parameter_grid(output / filename, summaries, [
            [(demand, "mean", "tab:orange", f"{demand} mean"), (actual, "mean", "tab:blue", f"{actual} mean")],
            [(demand, "temporal_std", "tab:orange", f"{demand} temporal SD"), (actual, "temporal_std", "tab:blue", f"{actual} temporal SD")],
            [(ratio, "integrated_ratio", "black", "accumulated satisfaction")],
        ], title, [RAW_UNITS[demand], RAW_UNITS[demand], "ratio"])
    for filename, metric, title in ((FIGURES[5], "GPP", "ABBY GPP response"), (FIGURES[6], "SR", "ABBY SR response"), (FIGURES[7], "HR", "ABBY direct HR response")):
        plot_parameter_grid(output / filename, summaries, [
            [(metric, "mean", "tab:blue", "mean")],
            [(metric, "temporal_std", "tab:orange", "temporal SD")],
        ], title, [RAW_UNITS[metric], RAW_UNITS[metric]])
    pool_rows = [[(metric, "mean", "tab:blue", "mean"), (metric, "temporal_std", "tab:orange", "temporal SD")] for metric in POOL_HR]
    plot_parameter_grid(output / FIGURES[8], summaries, pool_rows, "ABBY direct pool HR responses", [f"{metric}\n{RAW_UNITS[metric]}" for metric in POOL_HR])
    for filename, metrics, title in ((FIGURES[9], ("SMINN", "GROSS_NMIN", "NET_NMIN"), "ABBY N-cycle context"), (FIGURES[10], ("SOLUTIONP", "GROSS_PMIN", "NET_PMIN"), "ABBY P-cycle context")):
        rows = []
        labels = []
        for metric in metrics:
            rows.append([(metric, "mean", "tab:blue", "mean"), (metric, "temporal_std", "tab:orange", "temporal SD")])
            labels.append(f"{metric}\n{RAW_UNITS[metric]}")
        plot_parameter_grid(output / filename, summaries, rows, title, labels)


def run_preflight(args: argparse.Namespace, mappings: dict[str, str], config_files: dict[str, Path], parameter_files: dict[str, Path]) -> None:
    if args.output.exists():
        raise FileExistsError(f"refusing to replace existing preflight output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        summaries, manifest = validate_inputs(args, mappings, config_files, parameter_files)
        args.output.mkdir()
        write_json(args.output / "input_manifest.json", manifest)
        write_json(args.output / "validation_receipt.json", {
            "schema": RECEIPT_SCHEMA, "status": "pass", "created_at_utc": utc_now(),
            "input_manifest": str(args.output / "input_manifest.json"), "parameters": len(summaries),
            "members": len(summaries) * MEMBERS, "hours": EXPECTED_HOURS, "fixture": manifest["fixture"],
        })
        print(f"NUTRIENT_OAT_PREFLIGHT_PASS parameters={len(summaries)} members={len(summaries) * MEMBERS} hours={EXPECTED_HOURS}", flush=True)
    except Exception as exc:
        args.output.mkdir(exist_ok=True)
        write_json(args.output / "validation_receipt.json", {"schema": RECEIPT_SCHEMA, "status": "fail", "created_at_utc": utc_now(), "error_type": type(exc).__name__, "error": str(exc)})
        raise


def run_diagnostic(args: argparse.Namespace, mappings: dict[str, str], config_files: dict[str, Path], parameter_files: dict[str, Path]) -> None:
    if args.output.exists():
        raise FileExistsError(f"refusing to replace existing result staging: {args.output}")
    manifest = json.loads(args.manifest.read_text())
    summaries, current = validate_inputs(args, mappings, config_files, parameter_files, manifest)
    args.output.mkdir(parents=True)
    parameter_rows, member_rows, curve_rows, support_rows = build_tables(summaries)
    definitions = metric_definitions()
    write_csv(args.output / "parameter_metadata.csv", list(parameter_rows[0]), parameter_rows)
    write_csv(args.output / "metric_definitions.csv", list(definitions[0]), definitions)
    write_csv(args.output / "member_metrics.csv", list(member_rows[0]), member_rows)
    write_csv(args.output / "response_curves.csv", list(curve_rows[0]), curve_rows)
    write_csv(args.output / "ratio_support.csv", list(support_rows[0]), support_rows)
    make_figures(args.output, summaries)
    artifacts = {}
    for path in sorted(args.output.iterdir()):
        artifacts[path.name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    output_manifest = {
        "schema": OUTPUT_SCHEMA, "status": "pass", "created_at_utc": utc_now(),
        "input_manifest_sha256": digest(args.manifest), "tool_sha256": current["tool_sha256"],
        "row_counts": {"parameter_metadata.csv": len(parameter_rows), "metric_definitions.csv": len(definitions), "member_metrics.csv": len(member_rows), "response_curves.csv": len(curve_rows), "ratio_support.csv": len(support_rows)},
        "figure_count": len(FIGURES), "figure_names": list(FIGURES), "artifacts": artifacts,
    }
    write_json(args.output / "output_manifest.json", output_manifest)
    print(f"NUTRIENT_OAT_DIAGNOSTIC_PASS parameters={len(summaries)} csv_rows={sum(output_manifest['row_counts'].values())} figures={len(FIGURES)}", flush=True)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--site", required=True)
    result.add_argument("--pickle-dir", required=True, type=Path)
    result.add_argument("--parameter-pickle", required=True, action="append", default=[])
    result.add_argument("--config-file", required=True, action="append", default=[])
    result.add_argument("--parameter-file", required=True, action="append", default=[])
    result.add_argument("--control-paramfile", required=True, type=Path)
    result.add_argument("--output", required=True, type=Path)
    mode = result.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--manifest", type=Path)
    return result


def main() -> None:
    args = parser().parse_args()
    mappings = parse_mappings(args.parameter_pickle)
    config_files = parse_parameter_paths(args.config_file, "--config-file", tuple(mappings))
    parameter_files = parse_parameter_paths(args.parameter_file, "--parameter-file", tuple(mappings))
    if not args.output.is_absolute():
        raise ValueError("--output must be absolute")
    if args.validate_only:
        run_preflight(args, mappings, config_files, parameter_files)
    else:
        if args.manifest is None or not args.manifest.is_absolute() or not args.manifest.is_file():
            raise ValueError("--manifest must be an existing absolute input manifest")
        run_diagnostic(args, mappings, config_files, parameter_files)


if __name__ == "__main__":
    main()
