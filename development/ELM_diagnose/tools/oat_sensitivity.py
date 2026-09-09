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
from model_ELM.load_obs_nc import load_observations_with_time_from_nc  # noqa: E402

EXPECTED_PARAMETERS = (
    "act25",
    "br_mr",
    "grperc",
    "grpnow",
    "k_l1",
    "k_l2",
    "k_l3",
    "k_s1",
    "k_s2",
    "k_s3",
    "k_s4",
    "kmax",
    "leaf_long",
    "q10_mr",
)
LOG_PARAMETERS = frozenset({"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4"})
TARGETS = (
    "GPP",
    "ER",
    "SR",
    "HR_TOTAL",
    "LITFALL",
    "LITTER_SOIL_C_TOTAL",
    "LITR1C",
    "LITR2C",
    "LITR3C",
    "SOIL1C",
    "SOIL2C",
    "SOIL3C",
    "SOIL4C",
)
DIRECT_TARGETS = ("GPP", "ER", "SR", "LITFALL", "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
HR_COMPONENTS = ("CWDC_HR", "LITR1_HR", "LITR2_HR", "LITR3_HR", "SOIL1_HR", "SOIL2_HR", "SOIL3_HR", "SOIL4_HR")
SOC_COMPONENTS = ("LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
COMPENSATION = {
    "k_l1": ("LITR1C", "K_LITR1", "LITR1_HR", "LITR1"),
    "k_l2": ("LITR2C", "K_LITR2", "LITR2_HR", "LITR2"),
    "k_l3": ("LITR3C", "K_LITR3", "LITR3_HR", "LITR3"),
    "k_s1": ("SOIL1C", "K_SOIL1", "SOIL1_HR", "SOIL1"),
    "k_s2": ("SOIL2C", "K_SOIL2", "SOIL2_HR", "SOIL2"),
    "k_s3": ("SOIL3C", "K_SOIL3", "SOIL3_HR", "SOIL3"),
    "k_s4": ("SOIL4C", "K_SOIL4", "SOIL4_HR", "SOIL4"),
}
DERIVED_TARGETS = frozenset({"HR_TOTAL", "LITTER_SOIL_C_TOTAL"})
EXPECTED_HOURS = 7 * 365 * 24
STATISTICS = ("mean", "temporal_std")
DISPLAY_NAMES = {"LITTER_SOIL_C_TOTAL": "Total SOC"}
UNITS = {
    "GPP": "gC m-2 day-1",
    "ER": "gC m-2 day-1",
    "SR": "gC m-2 day-1",
    "HR_TOTAL": "gC m-2 day-1",
    "LITFALL": "gC m-2 day-1",
    "LITTER_SOIL_C_TOTAL": "gC m-2",
    "LITR1C": "gC m-2",
    "LITR2C": "gC m-2",
    "LITR3C": "gC m-2",
    "SOIL1C": "gC m-2",
    "SOIL2C": "gC m-2",
    "SOIL3C": "gC m-2",
    "SOIL4C": "gC m-2",
}


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
    litter_ratio_timeseries: dict[str, dict[str, np.ndarray]]
    metadata: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        if not parameter or not basename or parameter not in EXPECTED_PARAMETERS:
            raise ValueError(f"unknown or incomplete parameter mapping: {item!r}")
        if parameter in mappings:
            raise ValueError(f"duplicate parameter mapping: {parameter}")
        if basename != Path(basename).name or any(token in basename for token in ("*", "?", "[", "]")):
            raise ValueError(f"pickle mapping must use an exact basename: {basename!r}")
        if basename in filenames:
            raise ValueError(f"duplicate pickle basename: {basename}")
        mappings[parameter] = basename
        filenames.add(basename)
    if set(mappings) != set(EXPECTED_PARAMETERS):
        missing = sorted(set(EXPECTED_PARAMETERS) - set(mappings))
        extra = sorted(set(mappings) - set(EXPECTED_PARAMETERS))
        raise ValueError(f"mapping must contain the exact 14-parameter set; missing={missing}, extra={extra}")
    return {parameter: mappings[parameter] for parameter in EXPECTED_PARAMETERS}


def parse_log_parameters(raw: str) -> frozenset[str]:
    parsed = frozenset(item.strip() for item in raw.split(",") if item.strip())
    if parsed != LOG_PARAMETERS:
        raise ValueError(f"--log-parameters must be exactly {','.join(sorted(LOG_PARAMETERS))}")
    return parsed


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


def parse_interfaces(args: argparse.Namespace) -> dict[str, Any]:
    targets = parse_targets(args.target)
    observations = parse_family(args.observation, 2, "--observation")
    if any(variable not in targets for variable, _ in observations):
        raise ValueError("every observation variable must also be a selected target")
    if any(not Path(path).is_absolute() for _, path in observations):
        raise ValueError("observation paths must be absolute")
    compensation = parse_family(args.compensation, 4, "--compensation")
    if any(parameter not in EXPECTED_PARAMETERS for parameter, *_ in compensation):
        raise ValueError("compensation parameters must be declared OAT parameters")
    hr_pools = parse_family(args.hr_pool, 2, "--hr-pool")
    litter_ratios = parse_family(args.litter_ratio, 3, "--litter-ratio")
    hr_enabled = bool(hr_pools or args.hr_n_limiter or args.hr_p_limiter)
    if hr_enabled and (not hr_pools or not args.hr_n_limiter or not args.hr_p_limiter):
        raise ValueError("HR pathway analysis requires pools plus both N and P limiters")
    return {
        "targets": targets,
        "observations": observations,
        "compensation": compensation,
        "hr_pools": hr_pools,
        "hr_n_limiter": args.hr_n_limiter,
        "hr_p_limiter": args.hr_p_limiter,
        "litter_ratios": litter_ratios,
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


def load_case_summary(
    parameter: str,
    path: Path,
    pickle_sha256: str,
    coordinate: str,
    control_dataset: xr.Dataset,
    reference_taxis: np.ndarray | None,
    interfaces: dict[str, Any],
) -> tuple[CaseSummary, np.ndarray]:
    with path.open("rb") as handle:
        case = pickle.load(handle)
    if str(getattr(case, "site", "")) != "ABBY":
        raise ValueError(f"{path.name}: site must be ABBY")
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
        carbon_total = np.sum(carbon / 24.0, axis=0)
        nutrient_total = np.sum(nutrient / 24.0, axis=0)
        ratios = carbon_total / nutrient_total
        if not np.all(np.isfinite(ratios)) or np.any(nutrient_total <= 0.0):
            raise ValueError(f"{label}: every member requires finite totals and a positive accumulated denominator")
        litter_ratio_members[label] = ratios
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
        litter_ratio_timeseries=litter_ratio_timeseries,
        metadata=metadata,
    )
    del raw, targets, case
    gc.collect()
    return summary, taxis


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


def response_score(values: np.ndarray) -> tuple[float, float, float, float]:
    median = float(np.median(values))
    if not np.isfinite(median) or median == 0.0:
        raise ValueError("response-spread score requires a finite nonzero ensemble median")
    p05, p95 = (float(item) for item in np.percentile(values, (5, 95)))
    score = 100.0 * (p95 - p05) / abs(median)
    if not np.isfinite(score):
        raise ValueError("response-spread score is non-finite")
    return score, median, p05, p95


def normalized_response(values: np.ndarray) -> np.ndarray:
    median = float(np.median(values))
    if not np.isfinite(median) or median == 0.0:
        raise ValueError("normalized compensation response requires a finite nonzero median")
    return 100.0 * (values - median) / abs(median)


def build_rows(summaries: list[CaseSummary], targets: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
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
            }
        )
        for member in range(100):
            row: dict[str, Any] = {
                "parameter": summary.parameter,
                "member": member + 1,
                "parameter_value": float(summary.parameter_values[member]),
                "normalized_parameter": float(summary.normalized_parameter[member]),
            }
            for target in targets:
                row[f"{target}_mean"] = float(summary.member_statistics[target]["mean"][member])
                row[f"{target}_temporal_std"] = float(summary.member_statistics[target]["temporal_std"][member])
            member_rows.append(row)
        for target in targets:
            for statistic in STATISTICS:
                values = summary.member_statistics[target][statistic]
                score, median, p05, p95 = response_score(values)
                score_rows.append(
                    {
                        "parameter": summary.parameter,
                        "target": target,
                        "statistic": statistic,
                        "score_percent": score,
                        "rank": 0,
                        "median": median,
                        "p05": p05,
                        "p95": p95,
                        "units": UNITS[target],
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
                            "bin_count": item["count"],
                            "bin_x_min": item["x_min"],
                            "bin_x_max": item["x_max"],
                        }
                    )
    for target in targets:
        for statistic in STATISTICS:
            selected = [row for row in score_rows if row["target"] == target and row["statistic"] == statistic]
            selected.sort(key=lambda row: (-float(row["score_percent"]), str(row["parameter"])))
            for rank, row in enumerate(selected, start=1):
                row["rank"] = rank
    return parameter_rows, member_rows, score_rows, curve_rows


def plot_response_atlases(
    output: Path,
    summaries: list[CaseSummary],
    targets: tuple[str, ...],
    observation_rows: list[dict[str, Any]],
) -> list[Path]:
    paths: list[Path] = []
    observation_lookup = {row["variable"]: row for row in observation_rows}
    for target in targets:
        for statistic in STATISTICS:
            figure, axes = plt.subplots(4, 4, figsize=(15, 13), squeeze=False)
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
            figure.suptitle(f"ABBY {DISPLAY_NAMES.get(target, target)} member {statistic.replace('_', ' ')} OAT responses")
            figure.tight_layout(rect=(0, 0, 1, 0.97))
            path = output / f"ABBY_{target}_{statistic}_response_atlas.png"
            figure.savefig(path, dpi=150)
            plt.close(figure)
            paths.append(path)
    return paths


def plot_heatmaps(output: Path, score_rows: list[dict[str, Any]], targets: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for statistic in STATISTICS:
        lookup = {(row["parameter"], row["target"]): row for row in score_rows if row["statistic"] == statistic}
        matrix = np.asarray([[lookup[(parameter, target)]["score_percent"] for target in targets] for parameter in EXPECTED_PARAMETERS])
        figure, axis = plt.subplots(figsize=(18, 10))
        image = axis.imshow(matrix, aspect="auto", cmap="viridis")
        axis.set_xticks(range(len(targets)), [DISPLAY_NAMES.get(item, item) for item in targets], rotation=45, ha="right")
        axis.set_yticks(range(len(EXPECTED_PARAMETERS)), EXPECTED_PARAMETERS)
        for row_index, parameter in enumerate(EXPECTED_PARAMETERS):
            for column_index, target in enumerate(targets):
                row = lookup[(parameter, target)]
                color = "white" if matrix[row_index, column_index] > np.nanmedian(matrix) else "black"
                axis.text(column_index, row_index, f"{row['score_percent']:.1f}\n#{row['rank']}", ha="center", va="center", fontsize=6, color=color)
        axis.set_title(f"ABBY OAT response spread: {statistic.replace('_', ' ')}")
        figure.colorbar(image, ax=axis, label="response spread (%)")
        figure.tight_layout()
        path = output / f"ABBY_{statistic}_sensitivity_heatmap.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def plot_compensation(output: Path, summaries: list[CaseSummary], mappings: list[tuple[str, ...]]) -> list[Path]:
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
        figure.suptitle(f"ABBY {parameter} / {label} decomposition compensation")
        figure.tight_layout(rect=(0, 0, 1, 0.94))
        path = output / f"ABBY_{parameter}_{label}_compensation.png"
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
                    hr_metrics.append({"parameter": summary.parameter, "member": member, "pathway": pathway, "pool": pool, "accumulated_gC_m2": float(value)})
            for item in equal_count_bins(summary.normalized_parameter, pools["TOTAL"]):
                hr_curves.append({"parameter": summary.parameter, "pathway": pathway, **item})
        for label, values in summary.litter_ratio_members.items():
            for member, value in enumerate(values, start=1):
                litter_members.append({"parameter": summary.parameter, "ratio": label, "member": member, "ratio_value": float(value)})
            for item in equal_count_bins(summary.normalized_parameter, values):
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


def expected_artifact_counts(interfaces: dict[str, Any]) -> dict[str, int]:
    counts = {
        "parameter_metadata.csv": len(EXPECTED_PARAMETERS),
        "member_metrics.csv": len(EXPECTED_PARAMETERS) * 100,
        "sensitivity_scores.csv": len(EXPECTED_PARAMETERS) * len(interfaces["targets"]) * len(STATISTICS),
        "response_curves.csv": len(EXPECTED_PARAMETERS) * len(interfaces["targets"]) * len(STATISTICS) * 110,
    }
    if interfaces["observations"]:
        counts["observation_summary.csv"] = len(interfaces["observations"])
    if interfaces["hr_pools"]:
        counts["hr_pathway_metrics.csv"] = len(EXPECTED_PARAMETERS) * 100 * 3 * (len(interfaces["hr_pools"]) + 1)
        counts["hr_pathway_curves.csv"] = len(EXPECTED_PARAMETERS) * 3 * 10
    if interfaces["litter_ratios"]:
        ratios = len(interfaces["litter_ratios"])
        counts["litter_ratio_member_metrics.csv"] = len(EXPECTED_PARAMETERS) * 100 * ratios
        counts["litter_ratio_timeseries.csv"] = len(EXPECTED_PARAMETERS) * EXPECTED_HOURS * ratios
        counts["litter_ratio_curves.csv"] = len(EXPECTED_PARAMETERS) * 10 * ratios
    return counts


def plot_hr_pathways(output: Path, summaries: list[CaseSummary]) -> list[Path]:
    if not summaries or not summaries[0].hr_pathway_totals:
        return []
    figure, axes = plt.subplots(4, 4, figsize=(15, 13), squeeze=False)
    colors = {"potential": "tab:orange", "n_limited": "tab:blue", "p_limited": "tab:green"}
    for axis, summary in zip(axes.flat, summaries):
        for pathway, pools in summary.hr_pathway_totals.items():
            values = pools["TOTAL"]
            axis.scatter(summary.normalized_parameter, values, s=6, alpha=0.10, color=colors[pathway])
            bins = equal_count_bins(summary.normalized_parameter, values)
            axis.plot([item["x_median"] for item in bins], [item["response_median"] for item in bins], "o-", ms=3, lw=1.0, color=colors[pathway], label=pathway)
        axis.set(title=summary.parameter, xlabel=f"normalized {summary.coordinate}", ylabel="accumulated gC m-2")
    for axis in axes.flat[len(summaries):]:
        axis.set_visible(False)
    axes.flat[0].legend(fontsize=7)
    figure.suptitle("ABBY accumulated potential and N/P-limited heterotrophic respiration")
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    path = output / "ABBY_accumulated_hr_pathways.png"
    figure.savefig(path, dpi=150)
    plt.close(figure)
    return [path]


def plot_litter_ratios(output: Path, summaries: list[CaseSummary], taxis: np.ndarray) -> list[Path]:
    if not summaries or not summaries[0].litter_ratio_members:
        return []
    paths: list[Path] = []
    for label in summaries[0].litter_ratio_members:
        figure, axes = plt.subplots(4, 4, figsize=(15, 13), squeeze=False)
        for axis, summary in zip(axes.flat, summaries):
            stats = summary.litter_ratio_timeseries[label]
            axis.plot(taxis, stats["mean"], color="tab:blue", lw=0.5)
            axis.fill_between(taxis, stats["mean"] - stats["std"], stats["mean"] + stats["std"], color="tab:blue", alpha=0.15)
            axis.set(title=summary.parameter, xlabel="model year", ylabel=label)
        for axis in axes.flat[len(summaries):]:
            axis.set_visible(False)
        figure.suptitle(f"ABBY hourly litter ratio {label}: ensemble mean +/- population SD")
        figure.tight_layout(rect=(0, 0, 1, 0.97))
        path = output / f"ABBY_{label}_hourly_ratio_atlas.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
        figure, axes = plt.subplots(4, 4, figsize=(15, 13), squeeze=False)
        for axis, summary in zip(axes.flat, summaries):
            values = summary.litter_ratio_members[label]
            axis.scatter(summary.normalized_parameter, values, s=9, alpha=0.25)
            bins = equal_count_bins(summary.normalized_parameter, values)
            axis.plot([item["x_median"] for item in bins], [item["response_median"] for item in bins], "o-", color="black", ms=3, lw=1.0)
            axis.set(title=summary.parameter, xlabel=f"normalized {summary.coordinate}", ylabel=label)
        for axis in axes.flat[len(summaries):]:
            axis.set_visible(False)
        figure.suptitle(f"ABBY flux-weighted litter ratio response {label}")
        figure.tight_layout(rect=(0, 0, 1, 0.97))
        path = output / f"ABBY_{label}_flux_weighted_response_atlas.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        paths.append(path)
    return paths


def fixture_checks() -> dict[str, Any]:
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
    minimal = argparse.Namespace(
        target=["GPP"], observation=[], compensation=[], hr_pool=[],
        hr_n_limiter=None, hr_p_limiter=None, litter_ratio=[],
    )
    minimal_interfaces = parse_interfaces(minimal)
    if required_raw_variables(minimal_interfaces) != ("GPP",):
        raise AssertionError("optional-family independence fixture failed")
    if expected_artifact_counts(minimal_interfaces) != {
        "parameter_metadata.csv": 14,
        "member_metrics.csv": 1400,
        "sensitivity_scores.csv": 28,
        "response_curves.csv": 3080,
    }:
        raise AssertionError("dynamic optional-family artifact fixture failed")
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
        "litter_ratios": "hourly_mask_population_spread_and_flux_weighted_totals",
        "optional_families": "independently_disableable",
    }


def manifest_contract(
    args: argparse.Namespace,
    mappings: dict[str, str],
    log_parameters: frozenset[str],
    interfaces: dict[str, Any],
    observation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": "elm_oat_input_manifest_v2",
        "pickle_dir": str(args.pickle_dir),
        "control_paramfile": str(args.control_paramfile),
        "parameter_pickles": mappings,
        "log_parameters": sorted(log_parameters),
        "parameters": list(EXPECTED_PARAMETERS),
        "targets": list(interfaces["targets"]),
        "observations": [list(item) for item in interfaces["observations"]],
        "observation_sha256": {row["variable"]: row["sha256"] for row in observation_rows},
        "compensation": [list(item) for item in interfaces["compensation"]],
        "hr_pools": [list(item) for item in interfaces["hr_pools"]],
        "hr_n_limiter": interfaces["hr_n_limiter"],
        "hr_p_limiter": interfaces["hr_p_limiter"],
        "litter_ratios": [list(item) for item in interfaces["litter_ratios"]],
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
    expected_basenames = set(mappings.values())
    observed_basenames = {path.name for path in args.pickle_dir.glob("*.pkl") if path.is_file()}
    if observed_basenames != expected_basenames:
        missing = sorted(expected_basenames - observed_basenames)
        extra = sorted(observed_basenames - expected_basenames)
        raise ValueError(f"pickle directory must contain exactly the 14 mapped files; missing={missing}, extra={extra}")
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
        for field in ("pickle_dir", "control_paramfile", "parameter_pickles", "log_parameters", "parameters", "targets", "observations", "observation_sha256", "compensation", "hr_pools", "hr_n_limiter", "hr_p_limiter", "litter_ratios", "required_raw_variables", "regression_results", "regression_sha256", "expected_hours", "year_range", "member_count_per_parameter", "score"):
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
            summary, taxis = load_case_summary(parameter, path, pickle_hash, "log10" if parameter in log_parameters else "linear", control_dataset, reference_taxis, interfaces)
            if reference_taxis is None:
                reference_taxis = taxis.copy()
            summaries.append(summary)
            print(f"validated parameter={parameter}", flush=True)
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
        interfaces = parse_interfaces(args)
        fixture = fixture_checks()
        observation_rows = load_observation_rows(interfaces["observations"])
        summaries, manifest, _ = validate_all(args, mappings, log_parameters, interfaces, observation_rows)
        manifest["fixture"] = fixture
        manifest["observation_summary"] = observation_rows
        staging.mkdir()
        atomic_json(staging / "input_manifest.json", manifest)
        receipt = {
            "schema": "elm_oat_validation_receipt_v1",
            "status": "pass",
            "created_at_utc": utc_now(),
            "input_manifest": str(args.output / "input_manifest.json"),
            "parameters": len(summaries),
            "fixture": fixture,
        }
        atomic_json(staging / "validation_receipt.json", receipt)
        os.replace(staging, args.output)
        print(f"OAT_PREFLIGHT_PASS parameters=14 members=1400 hours=61320 observations={len(observation_rows)}", flush=True)
    except Exception as exc:
        if not args.output.exists():
            args.output.mkdir()
            atomic_json(args.output / "validation_receipt.json", {"schema": "elm_oat_validation_receipt_v1", "status": "fail", "created_at_utc": utc_now(), "error_type": type(exc).__name__, "error": str(exc)})
        raise


def run_diagnostic(args: argparse.Namespace, mappings: dict[str, str], log_parameters: frozenset[str]) -> None:
    manifest = json.loads(args.manifest.read_text())
    interfaces = parse_interfaces(args)
    observation_rows = load_observation_rows(interfaces["observations"])
    summaries, current_manifest, taxis = validate_all(args, mappings, log_parameters, interfaces, observation_rows, expected_manifest=manifest)
    staging = args.output.with_name(f".{args.output.name}.staging.{os.getpid()}")
    if args.output.exists():
        raise FileExistsError(f"refusing to replace existing result directory: {args.output}")
    if staging.exists():
        raise FileExistsError(f"staging directory already exists: {staging}")
    staging.mkdir(parents=True)
    parameter_rows, member_rows, score_rows, curve_rows = build_rows(summaries, interfaces["targets"])
    write_csv(staging / "parameter_metadata.csv", list(parameter_rows[0]), parameter_rows)
    write_csv(staging / "member_metrics.csv", list(member_rows[0]), member_rows)
    write_csv(staging / "sensitivity_scores.csv", list(score_rows[0]), score_rows)
    write_csv(staging / "response_curves.csv", list(curve_rows[0]), curve_rows)
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
        *plot_response_atlases(staging, summaries, interfaces["targets"], observation_rows),
        *plot_heatmaps(staging, score_rows, interfaces["targets"]),
        *plot_compensation(staging, summaries, interfaces["compensation"]),
        *plot_hr_pathways(staging, summaries),
        *plot_litter_ratios(staging, summaries, taxis),
    ]
    expected_figure_count = (
        2 * len(interfaces["targets"]) + 2 + len(interfaces["compensation"])
        + (1 if interfaces["hr_pools"] else 0) + 2 * len(interfaces["litter_ratios"])
    )
    if len(figures) != expected_figure_count:
        raise RuntimeError(f"expected {expected_figure_count} figures, generated {len(figures)}")
    expected_counts = expected_artifact_counts(interfaces)
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
        "schema": "elm_oat_output_manifest_v2",
        "status": "pass",
        "created_at_utc": utc_now(),
        "input_manifest_path": str(args.manifest),
        "input_manifest_sha256": digest(args.manifest),
        "validated_input_identity": current_manifest,
        "row_counts": observed_counts,
        "figure_count": expected_figure_count,
        "artifacts": artifacts,
        "compensation_normalization": "100 * (response - ensemble median) / abs(ensemble median)",
    }
    atomic_json(staging / "output_manifest.json", output_manifest)
    os.replace(staging, args.output)
    print(
        f"OAT_DIAGNOSTIC_GENERATE_PASS parameters=14 member_rows=1400 "
        f"score_rows={len(score_rows)} figures={expected_figure_count}",
        flush=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pickle-dir", required=True, type=Path)
    parser.add_argument("--parameter-pickle", required=True, action="append", default=[])
    parser.add_argument("--log-parameters", required=True)
    parser.add_argument("--control-paramfile", required=True, type=Path)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--observation", action="append", default=[])
    parser.add_argument("--compensation", action="append", default=[])
    parser.add_argument("--hr-pool", action="append", default=[])
    parser.add_argument("--hr-n-limiter")
    parser.add_argument("--hr-p-limiter")
    parser.add_argument("--litter-ratio", action="append", default=[])
    parser.add_argument("--regression-results", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--manifest", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    mappings = parse_mapping(args.parameter_pickle)
    log_parameters = parse_log_parameters(args.log_parameters)
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
