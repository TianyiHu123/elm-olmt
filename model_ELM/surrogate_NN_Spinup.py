#!/usr/bin/env python
from __future__ import annotations

import hashlib
import json
import math
import pickle
import time
from fnmatch import fnmatch
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

from .surrogate_NN_Forcing import (
    DEFAULT_SPINUP_VARS,
    _load_forcing_matrix,
    _normalize_var_list,
    _restart_file,
    _spinup_state,
)

DEFAULT_CLIM_FORCING_VARS = ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")
DEFAULT_SURFACE_VARS = ("PCT_SAND", "PCT_CLAY", "ORGANIC")
DEFAULT_MONTH_COUNT = 12
OVERFIT_R2_GAP_THRESHOLD = 0.15
OVERFIT_RMSE_RATIO_THRESHOLD = 1.5
DEFAULT_CORR_THRESHOLD = 0.98
DEFAULT_VARIANCE_THRESHOLD = 1.0e-12


@dataclass
class _PreparedSpinupCaseBlock:
    case_name: str
    member_site_labels: np.ndarray
    params: np.ndarray
    surface: np.ndarray
    climatology: np.ndarray
    climatology_feature_names: List[str]
    surface_feature_names: List[str]
    spinup_targets: np.ndarray
    spinup_vars: List[str]

    @property
    def nsamples(self) -> int:
        return int(self.params.shape[0])


def _parse_site_labels(case: Any, nsamples: int) -> np.ndarray:
    if hasattr(case, "site_labels"):
        labels = np.asarray(case.site_labels).astype(str)
        if labels.size == nsamples:
            return labels
    if hasattr(case, "site") and str(case.site).strip() != "":
        return np.asarray([str(case.site)] * nsamples)
    return np.asarray(["site0"] * nsamples)


def _safe_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = np.asarray(y_true).reshape(-1)
    b = np.asarray(y_pred).reshape(-1)
    if a.size == 0:
        return float("nan")
    a_center = a - np.nanmean(a)
    b_center = b - np.nanmean(b)
    denom = float(np.nansum(a_center * a_center) * np.nansum(b_center * b_center))
    if denom <= 0.0:
        return float("nan")
    corr = float(np.nansum(a_center * b_center) / math.sqrt(denom))
    return corr * corr


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = np.asarray(y_true).reshape(-1)
    b = np.asarray(y_pred).reshape(-1)
    if a.size == 0:
        return float("nan")
    return float(np.sqrt(np.nanmean((a - b) ** 2)))


def _format_metric(v: float) -> str:
    return "nan" if not np.isfinite(v) else f"{v:.4f}"


def _log_phase_timing(label: str, started: float, **details: Any) -> None:
    detail_text = " ".join(f"{key}={value}" for key, value in details.items())
    suffix = f" {detail_text}" if detail_text else ""
    print(f"TIMING phase={label} seconds={time.perf_counter() - started:.3f}{suffix}", flush=True)


def _sanitize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_json_value(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_sanitize_json_value(v) for v in value.tolist()]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        fval = float(value)
        return None if not math.isfinite(fval) else fval
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _sanitize_stats_for_json(stats: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for var, dct in stats.items():
        out[var] = {}
        for key, value in dct.items():
            out[var][key] = _sanitize_json_value(value)
    return out


def _normalize_model_type(model_type: str) -> str:
    mt = str(model_type).strip().lower()
    if mt in ("nn", "mlp", "mlpregressor"):
        return "nn"
    if mt in ("random_forest", "rf", "randomforest"):
        return "random_forest"
    raise ValueError(f"Unsupported model_type='{model_type}'. Use 'nn' or 'random_forest'.")


def _build_spinup_estimator_and_grid(model_type: str, quick_grid: bool) -> Tuple[Any, Dict[str, List[Any]]]:
    mt = _normalize_model_type(model_type)
    if mt == "nn":
        # Use a conservative MLP search to reduce overfitting risk on small spinup datasets.
        estimator = MLPRegressor(
            max_iter=800,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=20,
            random_state=42,
        )
        if quick_grid:
            param_grid = {
                "hidden_layer_sizes": [(8,), (16,)],
                "activation": ["tanh"],
                "solver": ["adam"],
                "alpha": [10.0, 50.0, 100.0],
                "learning_rate_init": [1.0e-3],
            }
        else:
            param_grid = {
                "hidden_layer_sizes": [(4,), (8,), (16,)],
                "activation": ["tanh"],
                "solver": ["adam"],
                "alpha": [1.0, 10.0, 50.0, 100.0],
                "learning_rate_init": [5.0e-4, 1.0e-3],
            }
        return estimator, param_grid

    estimator = RandomForestRegressor(random_state=42, n_jobs=1)
    if quick_grid:
        param_grid = {
            "n_estimators": [200, 400],
            "max_depth": [8, 12],
            "min_samples_split": [4, 8],
            "min_samples_leaf": [2, 4],
            "max_features": ["sqrt"],
        }
    else:
        param_grid = {
            "n_estimators": [200, 400, 600],
            "max_depth": [8, 12, 16],
            "min_samples_split": [4, 8],
            "min_samples_leaf": [2, 4, 8],
            "max_features": ["sqrt"],
        }
    return estimator, param_grid


def _random_group_partition(
    group_ids: np.ndarray,
    train_fraction: float,
    rng: np.random.Generator,
    *,
    mode_label: str,
    allow_single_group: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    unique_groups = np.asarray(np.unique(group_ids))
    if unique_groups.size < 2:
        if allow_single_group and unique_groups.size == 1:
            if float(train_fraction) >= 0.5:
                return unique_groups.copy(), np.asarray([], dtype=unique_groups.dtype)
            return np.asarray([], dtype=unique_groups.dtype), unique_groups.copy()
        raise ValueError(f"{mode_label} requires at least 2 unique groups to build train/validation split.")
    shuffled = unique_groups.copy()
    rng.shuffle(shuffled)
    ntrain = int(np.floor(shuffled.size * float(train_fraction)))
    ntrain = max(1, min(int(shuffled.size) - 1, ntrain))
    train_groups = np.sort(shuffled[:ntrain])
    val_groups = np.sort(shuffled[ntrain:])
    return train_groups, val_groups


def _compute_overfitting_diagnostics(
    train_r2: float,
    val_r2: float,
    train_rmse: float,
    val_rmse: float,
) -> Dict[str, Any]:
    r2_gap = float(train_r2 - val_r2) if np.isfinite(train_r2) and np.isfinite(val_r2) else float("nan")
    if np.isfinite(train_rmse) and train_rmse > 0.0 and np.isfinite(val_rmse):
        rmse_ratio = float(val_rmse / train_rmse)
    else:
        rmse_ratio = float("nan")

    reasons: List[str] = []
    if np.isfinite(r2_gap) and r2_gap > OVERFIT_R2_GAP_THRESHOLD and train_r2 > 0.6:
        reasons.append(f"r2_gap={r2_gap:.3f}>{OVERFIT_R2_GAP_THRESHOLD:.2f}")
    if np.isfinite(rmse_ratio) and rmse_ratio > OVERFIT_RMSE_RATIO_THRESHOLD:
        reasons.append(f"rmse_ratio={rmse_ratio:.3f}>{OVERFIT_RMSE_RATIO_THRESHOLD:.2f}")

    return {
        "r2_gap": r2_gap,
        "rmse_ratio": rmse_ratio,
        "overfit_warning": bool(reasons),
        "overfit_reason": "; ".join(reasons),
    }


def _resolve_output_label(case_names: Sequence[str], run_name: Optional[str]) -> str:
    if run_name and str(run_name).strip():
        return str(run_name).strip()
    if len(case_names) == 1:
        return case_names[0]
    digest = hashlib.sha1(",".join(case_names).encode("utf-8")).hexdigest()[:8]
    return f"multicase_spinup_{len(case_names)}cases_{digest}"


def _resolve_stats_run_id(stats_run_id: Optional[str], split_random_state: Optional[int]) -> str:
    if stats_run_id and str(stats_run_id).strip():
        return str(stats_run_id).strip()
    if split_random_state is not None:
        return f"seed{int(split_random_state)}"
    return "default"


def _surface_file_for_member(case: Any, ens_num: int) -> Path:
    ens_dir = _restart_file(case, ens_num).parent
    matches = sorted(ens_dir.glob("surfdata*.nc"))
    if matches:
        return matches[0]
    fallback = Path(getattr(case, "rundir", "")) / "surfdata.nc"
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(f"Unable to locate surface file for ensemble {ens_num} in {ens_dir}")


def _surface_feature_state(
    case: Any,
    ens_num: int,
    surface_vars: Sequence[str],
) -> np.ndarray:
    path = _surface_file_for_member(case, ens_num)
    out = np.zeros(len(surface_vars), dtype=np.float64)
    with Dataset(str(path), "r") as nc:
        for i, var in enumerate(surface_vars):
            if var not in nc.variables:
                raise KeyError(f"Surface variable '{var}' not found in {path}")
            values = np.asarray(nc.variables[var][:], dtype=np.float64)
            if var == "ORGANIC":
                out[i] = float(np.nansum(values))
            else:
                out[i] = float(np.nanmean(values))
    return out


def _extract_month(values: np.ndarray) -> np.ndarray:
    months: List[int] = []
    for t in values.reshape(-1):
        month = getattr(t, "month", None)
        if month is None:
            return np.array([], dtype=np.int32)
        months.append(int(month))
    return np.asarray(months, dtype=np.int32)


def _extract_year(values: np.ndarray) -> np.ndarray:
    if np.issubdtype(values.dtype, np.datetime64):
        return values.astype("datetime64[Y]").astype(np.int32) + 1970
    years: List[int] = []
    for t in values.reshape(-1):
        year = getattr(t, "year", None)
        if year is None:
            return np.array([], dtype=np.int32)
        years.append(int(year))
    return np.asarray(years, dtype=np.int32)


def _spinup_cycle_year_bounds(case: Any, spinup_case: Optional[Any] = None) -> Tuple[int, int]:
    source_case = case if spinup_case is None else spinup_case
    source_name = str(getattr(source_case, "casename", "spinup_case"))
    if not hasattr(source_case, "met_startyear"):
        raise AttributeError("Case is missing 'met_startyear' needed for spinup-cycle climatology.")
    if not hasattr(source_case, "met_endyear_spinup"):
        raise AttributeError("Case is missing 'met_endyear_spinup' needed for spinup-cycle climatology.")
    start_year = int(getattr(source_case, "met_startyear"))
    end_year = int(getattr(source_case, "met_endyear_spinup"))
    if end_year < start_year:
        raise ValueError(
            f"Invalid forcing cycle year range: met_startyear={start_year}, "
            f"met_endyear_spinup={end_year} in '{source_name}'"
        )
    return start_year, end_year


def _subset_forcing_to_spinup_cycle(
    case: Any,
    forcing_raw: np.ndarray,
    forcing_time: np.ndarray,
    spinup_case: Optional[Any] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    start_year, end_year = _spinup_cycle_year_bounds(case, spinup_case=spinup_case)
    years = _extract_year(np.asarray(forcing_time))
    if years.size != forcing_raw.shape[0]:
        raise ValueError(
            "Unable to extract forcing years from forcing time axis for spinup-cycle climatology. "
            f"Time length={forcing_time.shape[0]}, forcing rows={forcing_raw.shape[0]}"
        )
    mask = (years >= start_year) & (years <= end_year)
    if not np.any(mask):
        raise ValueError(
            f"No forcing rows fall within spinup cycle [{start_year}, {end_year}]. "
            "Please verify case.met_startyear / case.met_endyear_spinup."
        )
    return forcing_raw[mask, :], np.asarray(forcing_time).reshape(-1)[mask]


def _climatology_features(
    forcing_raw: np.ndarray,
    forcing_var_names: Sequence[str],
    forcing_time: np.ndarray,
    clim_feature_mode: str = "full",
    month_count: int = DEFAULT_MONTH_COUNT,
) -> Tuple[np.ndarray, List[str]]:
    if forcing_raw.ndim != 2:
        raise ValueError(f"forcing_raw must be 2-D, got {forcing_raw.shape}")
    if forcing_raw.shape[1] != len(forcing_var_names):
        raise ValueError(
            f"forcing_raw column count {forcing_raw.shape[1]} does not match variable count {len(forcing_var_names)}"
        )

    mode = str(clim_feature_mode).strip().lower()
    if mode not in ("full", "compact"):
        raise ValueError(f"Unsupported clim_feature_mode='{clim_feature_mode}'. Use 'full' or 'compact'.")

    months = _extract_month(np.asarray(forcing_time))
    use_monthly = months.size == forcing_raw.shape[0]
    if not use_monthly:
        print(
            "Warning: forcing time axis has no usable month metadata; "
            "skip monthly climatology and seasonal-amplitude features."
        )
    feats: List[float] = []
    names: List[str] = []

    for i, var in enumerate(forcing_var_names):
        x = np.asarray(forcing_raw[:, i], dtype=np.float64).reshape(-1)
        feats.extend([float(np.nanmean(x)), float(np.nanstd(x)), float(np.nanmin(x)), float(np.nanmax(x))])
        names.extend(
            [
                f"{var}_clim_mean",
                f"{var}_clim_std",
                f"{var}_clim_min",
                f"{var}_clim_max",
            ]
        )
        if use_monthly and mode == "full":
            month_means = np.full(month_count, np.nan, dtype=np.float64)
            for m in range(1, month_count + 1):
                mmask = months == m
                if np.any(mmask):
                    month_means[m - 1] = float(np.nanmean(x[mmask]))
                else:
                    month_means[m - 1] = float(np.nanmean(x))
                feats.append(float(month_means[m - 1]))
                names.append(f"{var}_clim_m{m:02d}")
            feats.append(float(np.nanmax(month_means) - np.nanmin(month_means)))
            names.append(f"{var}_clim_seasonal_amp")
        elif use_monthly and mode == "compact":
            month_means = np.full(month_count, np.nan, dtype=np.float64)
            for m in range(1, month_count + 1):
                mmask = months == m
                if np.any(mmask):
                    month_means[m - 1] = float(np.nanmean(x[mmask]))
                else:
                    month_means[m - 1] = float(np.nanmean(x))
            feats.append(float(np.nanmax(month_means) - np.nanmin(month_means)))
            names.append(f"{var}_clim_seasonal_amp")

    return np.asarray(feats, dtype=np.float64), names


def _inference_target_ntime(case: Any) -> int:
    if not hasattr(case, "output") or not isinstance(case.output, dict):
        raise AttributeError("Case must provide output dict to infer target length for climatology forcing load.")
    for key, values in case.output.items():
        if key == "taxis":
            continue
        arr = np.asarray(values).transpose()
        if arr.ndim == 2:
            return int(arr.shape[1])
    raise ValueError("Unable to infer ntarget from case.output.")


def _prepare_case_spinup_block(
    case: Any,
    spinup_vars: Sequence[str],
    surface_vars: Sequence[str],
    forcing_vars: Sequence[str],
    clim_feature_mode: str = "compact",
    spinup_case: Optional[Any] = None,
) -> _PreparedSpinupCaseBlock:
    case_name = str(getattr(case, "casename", "case"))
    if not hasattr(case, "samples"):
        raise AttributeError(f"Case '{case_name}' missing 'samples'")

    params = np.asarray(case.samples).transpose().astype(np.float64)
    if params.ndim != 2:
        raise ValueError(f"Case '{case_name}' samples must be 2-D after transpose, got {params.shape}")
    nsamples = params.shape[0]

    spinup = np.zeros((nsamples, len(spinup_vars)), dtype=np.float64)
    surface = np.zeros((nsamples, len(surface_vars)), dtype=np.float64)
    for ens in range(1, nsamples + 1):
        spinup[ens - 1, :] = _spinup_state(case, ens, spinup_vars)
        surface[ens - 1, :] = _surface_feature_state(case, ens, surface_vars)

    ntime_ref = _inference_target_ntime(case)
    forcing_raw, forcing_vars_used, forcing_time = _load_forcing_matrix(
        Path(case.metdir), forcing_vars, ntime_ref
    )
    forcing_cycle_raw, forcing_cycle_time = _subset_forcing_to_spinup_cycle(
        case, forcing_raw, forcing_time, spinup_case=spinup_case
    )
    clim_vec, clim_names = _climatology_features(
        forcing_cycle_raw,
        forcing_vars_used,
        forcing_cycle_time,
        clim_feature_mode=clim_feature_mode,
    )
    climatology = np.tile(clim_vec.reshape(1, -1), (nsamples, 1))

    return _PreparedSpinupCaseBlock(
        case_name=case_name,
        member_site_labels=_parse_site_labels(case, nsamples),
        params=params,
        surface=surface,
        climatology=climatology,
        climatology_feature_names=list(clim_names),
        surface_feature_names=list(surface_vars),
        spinup_targets=spinup,
        spinup_vars=list(spinup_vars),
    )


def _validate_spinup_blocks(blocks: Sequence[_PreparedSpinupCaseBlock]) -> None:
    if not blocks:
        raise ValueError("No spinup training blocks were prepared.")
    ref = blocks[0]
    for block in blocks:
        if block.params.shape[1] != ref.params.shape[1]:
            raise ValueError(
                f"Case '{block.case_name}' parameter count {block.params.shape[1]} "
                f"does not match reference {ref.params.shape[1]}"
            )
        if block.surface_feature_names != ref.surface_feature_names:
            raise ValueError(
                f"Case '{block.case_name}' surface variable list does not match reference case '{ref.case_name}'"
            )
        if block.climatology_feature_names != ref.climatology_feature_names:
            raise ValueError(
                f"Case '{block.case_name}' climatology features do not match reference case '{ref.case_name}'"
            )
        if block.spinup_vars != ref.spinup_vars:
            raise ValueError(
                f"Case '{block.case_name}' spinup vars {block.spinup_vars} do not match {ref.spinup_vars}"
            )


def _build_split_indices(
    row_case_ids: np.ndarray,
    row_member_ids: np.ndarray,
    row_site_ids: np.ndarray,
    split_mode: str,
    train_fraction: float,
    split_random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    if not (0.0 < float(train_fraction) < 1.0):
        raise ValueError(f"train_fraction must be in (0, 1), got {train_fraction}.")
    nrows = row_case_ids.size
    all_idx = np.arange(nrows)
    train_mask = np.zeros(nrows, dtype=bool)
    rng = np.random.default_rng(split_random_state)
    split_details: Dict[str, Any] = {"mode": split_mode}

    if split_mode == "by_member":
        per_case: Dict[str, Dict[str, List[int]]] = {}
        for case_id in np.unique(row_case_ids):
            case_mask = row_case_ids == case_id
            members = np.unique(row_member_ids[case_mask])
            train_members, val_members = _random_group_partition(
                members,
                train_fraction,
                rng,
                mode_label=f"split_mode={split_mode} (case_id={int(case_id)})",
                allow_single_group=True,
            )
            train_mask[case_mask] = np.isin(row_member_ids[case_mask], train_members)
            per_case[str(int(case_id))] = {
                "train_groups": [int(v) for v in train_members.tolist()],
                "val_groups": [int(v) for v in val_members.tolist()],
            }
        split_details["per_case_group_ids"] = per_case
    elif split_mode == "by_site":
        sites = np.asarray(np.unique(row_site_ids))
        train_sites, val_sites = _random_group_partition(
            sites, train_fraction, rng, mode_label=f"split_mode={split_mode}"
        )
        train_mask = np.isin(row_site_ids, train_sites)
        split_details["train_groups"] = [int(v) for v in train_sites.tolist()]
        split_details["val_groups"] = [int(v) for v in val_sites.tolist()]
    elif split_mode == "by_case":
        cases = np.asarray(np.unique(row_case_ids))
        train_cases, val_cases = _random_group_partition(
            cases, train_fraction, rng, mode_label=f"split_mode={split_mode}"
        )
        train_mask = np.isin(row_case_ids, train_cases)
        split_details["train_groups"] = [int(v) for v in train_cases.tolist()]
        split_details["val_groups"] = [int(v) for v in val_cases.tolist()]
    elif split_mode == "random":
        idx = np.arange(nrows)
        rng.shuffle(idx)
        cutoff = int(np.floor(nrows * float(train_fraction)))
        cutoff = max(1, min(nrows - 1, cutoff))
        train_mask[idx[:cutoff]] = True
        split_details["train_row_count"] = int(cutoff)
        split_details["val_row_count"] = int(nrows - cutoff)
    else:
        raise ValueError(f"Unsupported split_mode: {split_mode}")

    train_idx = all_idx[train_mask]
    val_idx = all_idx[~train_mask]
    if train_idx.size == 0 or val_idx.size == 0:
        raise ValueError(
            f"split_mode={split_mode} with train_fraction={train_fraction} produced empty train/val split."
        )
    return train_idx, val_idx, split_details


def _save_scatter_plot(
    y_train_true: np.ndarray,
    y_train_pred: np.ndarray,
    y_val_true: np.ndarray,
    y_val_pred: np.ndarray,
    outdir: Path,
    var: str,
    train_r2: float,
    val_r2: float,
    train_rmse: float,
    val_rmse: float,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.scatter(y_train_true, y_train_pred, s=12, alpha=0.35, label="Train", color="tab:blue")
    ax.scatter(y_val_true, y_val_pred, s=16, alpha=0.55, label="Validation", color="tab:orange")
    lo = np.nanmin([np.nanmin(y_train_true), np.nanmin(y_train_pred), np.nanmin(y_val_true), np.nanmin(y_val_pred)])
    hi = np.nanmax([np.nanmax(y_train_true), np.nanmax(y_train_pred), np.nanmax(y_val_true), np.nanmax(y_val_pred)])
    if np.isfinite(lo) and np.isfinite(hi) and hi > lo:
        ax.plot([lo, hi], [lo, hi], "--", color="k", lw=1.0, alpha=0.8)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
    ax.set_xlabel(f"{var} (ELM)")
    ax.set_ylabel(f"{var} (Surrogate)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    ax.set_title(
        f"{var} spinup surrogate\n"
        f"R2 train={_format_metric(train_r2)}, val={_format_metric(val_r2)} | "
        f"RMSE train={_format_metric(train_rmse)}, val={_format_metric(val_rmse)}"
    )
    fig.tight_layout()
    fig.savefig(outdir / f"{var}_spinup_scatter.png", dpi=150)
    plt.close(fig)


def _write_stats_json(
    path: Path,
    stats: Dict[str, Dict[str, Any]],
    *,
    model_type: str,
    split_mode: str,
    train_fraction: float,
    split_random_state: Optional[int],
    output_label: str,
    case_names: Sequence[str],
    spinup_vars: Sequence[str],
    stats_run_id: str,
    feature_names: Sequence[str],
    split_details: Optional[Dict[str, Any]] = None,
    feature_diagnostics: Optional[Dict[str, Any]] = None,
    input_feature_names_all: Optional[Sequence[str]] = None,
) -> None:
    payload: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "stats_run_id": stats_run_id,
        "model_type": model_type,
        "split_mode": split_mode,
        "train_fraction": float(train_fraction),
        "split_random_state": split_random_state,
        "output_label": output_label,
        "case_names": list(case_names),
        "spinup_vars": list(spinup_vars),
        "input_feature_names": list(feature_names),
        "by_variable": _sanitize_stats_for_json(stats),
    }
    if input_feature_names_all is not None:
        payload["input_feature_names_all"] = list(input_feature_names_all)
    if split_details is not None:
        payload["split_details"] = _sanitize_json_value(split_details)
    if feature_diagnostics is not None:
        payload["feature_diagnostics"] = _sanitize_json_value(feature_diagnostics)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def _build_design_matrix(
    blocks: Sequence[_PreparedSpinupCaseBlock],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rows = sum(block.nsamples for block in blocks)
    ref = blocks[0]
    nfeatures = ref.params.shape[1] + ref.surface.shape[1] + ref.climatology.shape[1]
    X = np.empty((rows, nfeatures), dtype=np.float64)
    row_case_ids = np.empty(rows, dtype=np.int32)
    row_member_ids = np.empty(rows, dtype=np.int32)
    row_site_ids = np.empty(rows, dtype=np.int32)

    site_name_to_id: Dict[str, int] = {}
    offset = 0
    p_end = ref.params.shape[1]
    s_end = p_end + ref.surface.shape[1]
    for case_id, block in enumerate(blocks):
        for member_id in range(block.nsamples):
            row = offset
            X[row, :p_end] = block.params[member_id, :]
            X[row, p_end:s_end] = block.surface[member_id, :]
            X[row, s_end:] = block.climatology[member_id, :]
            row_case_ids[row] = case_id
            row_member_ids[row] = member_id
            site_label = str(block.member_site_labels[member_id])
            if site_label not in site_name_to_id:
                site_name_to_id[site_label] = len(site_name_to_id)
            row_site_ids[row] = site_name_to_id[site_label]
            offset += 1

    if offset != rows:
        raise RuntimeError(f"Design matrix row mismatch: expected {rows}, populated {offset}")
    return X, row_case_ids, row_member_ids, row_site_ids


def _normalize_feature_set(feature_set: str) -> str:
    mode = str(feature_set).strip().lower()
    allowed = {"all", "params_only", "params_surface", "params_clim"}
    if mode not in allowed:
        raise ValueError(f"Unsupported feature_set='{feature_set}'. Use one of {sorted(allowed)}.")
    return mode


def _normalize_glob_patterns(patterns: Optional[Sequence[str]]) -> List[str]:
    if patterns is None:
        return ["*"]
    out = [str(p).strip() for p in patterns if str(p).strip()]
    return out if out else ["*"]


def _normalize_feature_subset(feature_subset: Optional[Sequence[str]]) -> List[str]:
    if feature_subset is None:
        return []
    out: List[str] = []
    seen = set()
    for raw in feature_subset:
        name = str(raw).strip()
        if not name or name in seen:
            continue
        out.append(name)
        seen.add(name)
    return out


def _collect_corr_pairs(
    X_train: np.ndarray,
    feature_idx: np.ndarray,
    feature_names: Sequence[str],
    *,
    corr_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    if feature_idx.size < 2:
        return []
    corr = np.corrcoef(X_train[:, feature_idx], rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    pairs: List[Dict[str, Any]] = []
    for i in range(corr.shape[0]):
        for j in range(i + 1, corr.shape[1]):
            cval = float(corr[i, j])
            if corr_threshold is not None and abs(cval) < float(corr_threshold):
                continue
            pairs.append(
                {
                    "feature_i": str(feature_names[int(feature_idx[i])]),
                    "feature_j": str(feature_names[int(feature_idx[j])]),
                    "corr": cval,
                }
            )
    pairs.sort(key=lambda d: abs(float(d["corr"])), reverse=True)
    return pairs


def _find_drop_representative(
    dropped_name: str,
    high_corr_pairs: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    for pair in high_corr_pairs:
        name_i = str(pair.get("feature_i", ""))
        name_j = str(pair.get("feature_j", ""))
        if name_j != dropped_name:
            continue
        return {
            "dropped_feature": dropped_name,
            "representative_feature": name_i,
            "corr": float(pair.get("corr", float("nan"))),
        }
    return {
        "dropped_feature": dropped_name,
        "representative_feature": None,
        "corr": None,
    }


def _select_feature_columns(
    X: np.ndarray,
    train_idx: np.ndarray,
    input_feature_names: Sequence[str],
    *,
    n_params: int,
    n_surface: int,
    n_climatology: int,
    feature_set: str,
    clim_feature_include: Optional[Sequence[str]] = None,
    explicit_feature_subset: Optional[Sequence[str]] = None,
    apply_variance_filter: bool = False,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    apply_corr_filter: bool = False,
    corr_threshold: float = DEFAULT_CORR_THRESHOLD,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    mode = _normalize_feature_set(feature_set)
    n_total = X.shape[1]
    names = [str(v) for v in input_feature_names]
    if n_total != len(names):
        raise ValueError(
            f"Feature-name length mismatch: matrix has {n_total} columns, names have {len(names)}."
        )
    if n_total != (n_params + n_surface + n_climatology):
        raise ValueError(
            "Feature block length mismatch: "
            f"n_total={n_total}, n_params={n_params}, n_surface={n_surface}, n_climatology={n_climatology}."
        )
    train_X = X[train_idx, :]
    keep = np.zeros(n_total, dtype=bool)
    p_end = n_params
    s_end = n_params + n_surface
    clim_idx = np.arange(s_end, n_total, dtype=np.int32)

    if mode == "all":
        keep[:] = True
    elif mode == "params_only":
        keep[:p_end] = True
    elif mode == "params_surface":
        keep[:s_end] = True
    elif mode == "params_clim":
        keep[:p_end] = True
        keep[s_end:] = True
    else:
        raise ValueError(f"Unsupported feature_set='{feature_set}'")

    dropped_by_feature_set = [
        str(names[i]) for i in range(n_total) if not keep[i]
    ]

    clim_patterns = _normalize_glob_patterns(clim_feature_include)
    dropped_by_clim_include: List[str] = []
    if keep[clim_idx].any() and not (len(clim_patterns) == 1 and clim_patterns[0] == "*"):
        for idx in clim_idx.tolist():
            if not keep[idx]:
                continue
            fname = str(names[idx])
            matched = any(fnmatch(fname, pattern) for pattern in clim_patterns)
            if not matched:
                keep[idx] = False
                dropped_by_clim_include.append(fname)

    dropped_by_variance: List[Dict[str, Any]] = []
    if apply_variance_filter:
        candidate = np.where(keep)[0]
        variances = np.nanvar(train_X[:, candidate], axis=0)
        for local_i, idx in enumerate(candidate.tolist()):
            v = float(variances[local_i])
            if (not np.isfinite(v)) or (v <= float(variance_threshold)):
                keep[idx] = False
                dropped_by_variance.append({"feature": str(names[idx]), "variance": v})

    explicit_subset_requested = _normalize_feature_subset(explicit_feature_subset)
    eligible_idx_pre_corr = np.where(keep)[0].astype(np.int32)
    full_corr_pairs_pre_prune = _collect_corr_pairs(
        train_X,
        eligible_idx_pre_corr,
        names,
    )

    high_corr_pairs: List[Dict[str, Any]] = []
    dropped_by_correlation: List[str] = []
    dropped_by_correlation_pairs: List[Dict[str, Any]] = []
    if apply_corr_filter:
        candidate = np.where(keep)[0]
        high_corr_pairs = _collect_corr_pairs(
            train_X,
            candidate,
            names,
            corr_threshold=float(corr_threshold),
        )
        name_to_idx = {name: idx for idx, name in enumerate(names)}
        dropped = set()
        for pair in high_corr_pairs:
            name_j = str(pair["feature_j"])
            idx_j = int(name_to_idx[name_j])
            if idx_j in dropped:
                continue
            dropped.add(idx_j)
        for idx in sorted(dropped):
            if keep[idx]:
                keep[idx] = False
                dropped_name = str(names[idx])
                dropped_by_correlation.append(dropped_name)
                dropped_by_correlation_pairs.append(
                    _find_drop_representative(dropped_name, high_corr_pairs)
                )

    selected_idx = np.where(keep)[0].astype(np.int32)
    if selected_idx.size == 0:
        raise ValueError(
            "Feature selection removed all features. "
            "Relax feature_set / clim_feature_include / variance / correlation filters."
        )

    selected_name_set = {str(names[i]) for i in selected_idx.tolist()}
    missing_requested = [name for name in explicit_subset_requested if name not in selected_name_set]
    if missing_requested:
        raise ValueError(
            "Explicit feature subset includes unavailable feature(s) after "
            "feature_set/clim/variance/correlation filtering: "
            + ", ".join(missing_requested)
        )
    explicit_subset_excluded: List[str] = []
    if explicit_subset_requested:
        name_to_idx = {str(name): int(i) for i, name in enumerate(names)}
        selected_idx = np.asarray(
            [name_to_idx[name] for name in explicit_subset_requested],
            dtype=np.int32,
        )
        selected_name_set_subset = set(explicit_subset_requested)
        explicit_subset_excluded = sorted(selected_name_set - selected_name_set_subset)

    selected_names = [str(names[i]) for i in selected_idx.tolist()]
    diagnostics: Dict[str, Any] = {
        "feature_set": mode,
        "n_total_features": int(n_total),
        "n_selected_features": int(selected_idx.size),
        "selected_feature_names": selected_names,
        "selected_feature_indices": [int(v) for v in selected_idx.tolist()],
        "clim_feature_include": list(clim_patterns),
        "apply_variance_filter": bool(apply_variance_filter),
        "variance_threshold": float(variance_threshold),
        "apply_corr_filter": bool(apply_corr_filter),
        "corr_threshold": float(corr_threshold),
        "dropped_by_feature_set": dropped_by_feature_set,
        "dropped_by_clim_include": dropped_by_clim_include,
        "dropped_by_variance": dropped_by_variance,
        "full_corr_pairs_pre_prune": full_corr_pairs_pre_prune,
        "high_corr_pairs": high_corr_pairs,
        "dropped_by_correlation": dropped_by_correlation,
        "dropped_by_correlation_pairs": dropped_by_correlation_pairs,
        "explicit_feature_subset_requested": explicit_subset_requested,
        "explicit_feature_subset_applied": bool(explicit_subset_requested),
        "explicit_feature_subset_missing": missing_requested,
        "excluded_by_explicit_subset": explicit_subset_excluded,
        "n_params": int(n_params),
        "n_surface": int(n_surface),
        "n_climatology": int(n_climatology),
    }
    return selected_idx, diagnostics


def _permutation_importance_rmse(
    model: Any,
    X_val_scaled: np.ndarray,
    y_scaler: preprocessing.StandardScaler,
    y_val_true: np.ndarray,
    feature_names: Sequence[str],
    *,
    n_repeats: int = 5,
    random_state: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if int(n_repeats) <= 0 or X_val_scaled.shape[0] < 2 or X_val_scaled.shape[1] == 0:
        return []
    baseline_pred = y_scaler.inverse_transform(model.predict(X_val_scaled).reshape(-1, 1)).ravel()
    baseline_rmse = _rmse(y_val_true, baseline_pred)
    baseline_r2 = _safe_r2(y_val_true, baseline_pred)
    rng = np.random.default_rng(random_state)
    out: List[Dict[str, Any]] = []
    nrows = X_val_scaled.shape[0]
    for j in range(X_val_scaled.shape[1]):
        rmse_deltas: List[float] = []
        r2_deltas: List[float] = []
        for _ in range(int(n_repeats)):
            X_perm = X_val_scaled.copy()
            perm_idx = rng.permutation(nrows)
            X_perm[:, j] = X_val_scaled[perm_idx, j]
            pred = y_scaler.inverse_transform(model.predict(X_perm).reshape(-1, 1)).ravel()
            rmse_deltas.append(float(_rmse(y_val_true, pred) - baseline_rmse))
            score = _safe_r2(y_val_true, pred)
            r2_deltas.append(float(baseline_r2 - score) if np.isfinite(score) and np.isfinite(baseline_r2) else float("nan"))
        out.append(
            {
                "feature": str(feature_names[j]),
                "mean_rmse_increase": float(np.nanmean(rmse_deltas)),
                "std_rmse_increase": float(np.nanstd(rmse_deltas)),
                "mean_r2_drop": float(np.nanmean(r2_deltas)),
                "std_r2_drop": float(np.nanstd(r2_deltas)),
            }
        )
    out.sort(key=lambda d: float(d["mean_rmse_increase"]), reverse=True)
    return out


def train_surrogate_spinup_from_cases(
    cases: Sequence[Any],
    spinup_cases: Optional[Sequence[Any]] = None,
    *,
    spinup_vars: Optional[Sequence[str]] = None,
    surface_vars: Optional[Sequence[str]] = None,
    forcing_vars: Optional[Sequence[str]] = None,
    clim_feature_mode: str = "compact",
    split_mode: str = "by_member",
    train_fraction: float = 0.8,
    split_random_state: Optional[int] = None,
    n_jobs: int = 8,
    cv_folds: int = 3,
    quick_grid: bool = False,
    model_type: str = "nn",
    dry_run: bool = False,
    outputdir: str = ".",
    run_name: Optional[str] = None,
    minimal_output: bool = False,
    stats_run_id: Optional[str] = None,
    feature_set: str = "all",
    clim_feature_include: Optional[Sequence[str]] = None,
    explicit_feature_subset: Optional[Sequence[str]] = None,
    apply_variance_filter: bool = False,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    apply_corr_filter: bool = False,
    corr_threshold: float = DEFAULT_CORR_THRESHOLD,
    permutation_repeats: int = 5,
    permutation_random_state: Optional[int] = None,
    pre_dispatch: Union[int, str] = "2*n_jobs",
) -> Optional[Dict[str, Any]]:
    if not cases:
        raise ValueError("At least one case object is required.")
    if spinup_cases is None:
        spinup_cases_resolved = [None] * len(cases)
    else:
        spinup_cases_resolved = list(spinup_cases)
        if len(spinup_cases_resolved) != len(cases):
            raise ValueError(
                "spinup_cases must be omitted or have the same length/order as cases. "
                f"Got len(cases)={len(cases)}, len(spinup_cases)={len(spinup_cases_resolved)}."
            )
    spinup_vars_list = list(DEFAULT_SPINUP_VARS if spinup_vars is None else [str(v).strip() for v in spinup_vars if str(v).strip()])
    if not spinup_vars_list:
        spinup_vars_list = list(DEFAULT_SPINUP_VARS)
    surface_vars_list = list(DEFAULT_SURFACE_VARS if surface_vars is None else [str(v).strip() for v in surface_vars if str(v).strip()])
    forcing_vars_list = list(
        DEFAULT_CLIM_FORCING_VARS if forcing_vars is None else [str(v).strip() for v in forcing_vars if str(v).strip()]
    )
    clim_feature_mode_norm = str(clim_feature_mode).strip().lower()
    if clim_feature_mode_norm not in ("full", "compact"):
        raise ValueError(f"Unsupported clim_feature_mode='{clim_feature_mode}'. Use 'full' or 'compact'.")
    if not surface_vars_list:
        raise ValueError("surface_vars must not be empty.")
    if not forcing_vars_list:
        raise ValueError("forcing_vars must not be empty.")
    model_type_norm = _normalize_model_type(model_type)
    feature_set_norm = _normalize_feature_set(feature_set)
    if float(corr_threshold) < 0.0 or float(corr_threshold) > 1.0:
        raise ValueError(f"corr_threshold must be in [0, 1], got {corr_threshold}")
    if int(permutation_repeats) < 0:
        raise ValueError(f"permutation_repeats must be >= 0, got {permutation_repeats}")

    blocks: List[_PreparedSpinupCaseBlock] = []
    for case, spinup_case in zip(cases, spinup_cases_resolved):
        phase_start = time.perf_counter()
        block = _prepare_case_spinup_block(
            case=case,
            spinup_vars=spinup_vars_list,
            surface_vars=surface_vars_list,
            forcing_vars=forcing_vars_list,
            clim_feature_mode=clim_feature_mode_norm,
            spinup_case=spinup_case,
        )
        blocks.append(block)
        _log_phase_timing("prepare_case", phase_start, case=block.case_name, rows=block.nsamples)
    _validate_spinup_blocks(blocks)
    case_names = [b.case_name for b in blocks]
    output_label = _resolve_output_label(case_names, run_name)
    outdir = Path(outputdir).resolve() / "UQ_output" / output_label / "surrogate_spinup"
    outdir.mkdir(parents=True, exist_ok=True)

    phase_start = time.perf_counter()
    X, row_case_ids, row_member_ids, row_site_ids = _build_design_matrix(blocks)
    _log_phase_timing("build_design_matrix", phase_start, shape=X.shape)
    ref = blocks[0]
    all_input_feature_names = (
        [f"parm_{i}" for i in range(ref.params.shape[1])]
        + list(ref.surface_feature_names)
        + list(ref.climatology_feature_names)
    )
    print(f"Final spinup design matrix (full): {X.shape}")
    print(f"Cases: {case_names}")

    train_idx, val_idx, split_details = _build_split_indices(
        row_case_ids=row_case_ids,
        row_member_ids=row_member_ids,
        row_site_ids=row_site_ids,
        split_mode=split_mode,
        train_fraction=train_fraction,
        split_random_state=split_random_state,
    )
    print(f"Train rows: {train_idx.size}, Val rows: {val_idx.size}")

    phase_start = time.perf_counter()
    selected_idx, feature_diagnostics = _select_feature_columns(
        X,
        train_idx,
        all_input_feature_names,
        n_params=int(ref.params.shape[1]),
        n_surface=int(ref.surface.shape[1]),
        n_climatology=int(ref.climatology.shape[1]),
        feature_set=feature_set_norm,
        clim_feature_include=clim_feature_include,
        explicit_feature_subset=explicit_feature_subset,
        apply_variance_filter=apply_variance_filter,
        variance_threshold=float(variance_threshold),
        apply_corr_filter=apply_corr_filter,
        corr_threshold=float(corr_threshold),
    )
    _log_phase_timing("select_features", phase_start, selected=int(selected_idx.size))
    input_feature_names = [all_input_feature_names[i] for i in selected_idx.tolist()]
    X_selected = X[:, selected_idx]
    print(
        f"Feature selection: kept {X_selected.shape[1]}/{X.shape[1]} columns "
        f"(feature_set={feature_set_norm})"
    )

    if dry_run:
        print("Dry-run only. Exiting before model fitting.")
        return None

    model_store: Dict[str, Any] = {}
    x_scaler_store: Dict[str, preprocessing.StandardScaler] = {}
    y_scaler_store: Dict[str, preprocessing.StandardScaler] = {}
    stats: Dict[str, Dict[str, Any]] = {}

    for ivar, var in enumerate(spinup_vars_list):
        print(f"\nTraining spinup variable: {var}")
        y = np.concatenate([block.spinup_targets[:, ivar] for block in blocks]).reshape(-1, 1)
        if np.any(~np.isfinite(y)):
            bad = int(np.sum(~np.isfinite(y)))
            raise ValueError(f"Target {var} contains {bad} non-finite values")

        x_scaler = preprocessing.StandardScaler().fit(X_selected[train_idx, :])
        y_scaler = preprocessing.StandardScaler().fit(y[train_idx, :])
        X_train = x_scaler.transform(X_selected[train_idx, :])
        X_val = x_scaler.transform(X_selected[val_idx, :])
        y_train = y_scaler.transform(y[train_idx, :]).ravel()
        y_val = y_scaler.transform(y[val_idx, :]).ravel()

        estimator, param_grid = _build_spinup_estimator_and_grid(model_type_norm, quick_grid)
        grid = GridSearchCV(
            estimator,
            param_grid,
            n_jobs=n_jobs,
            cv=cv_folds,
            pre_dispatch=pre_dispatch,
        )
        phase_start = time.perf_counter()
        grid.fit(X_train, y_train)
        _log_phase_timing(
            "grid_search_fit",
            phase_start,
            target=var,
            n_jobs=n_jobs,
            pre_dispatch=pre_dispatch,
        )

        yhat_train = y_scaler.inverse_transform(grid.predict(X_train).reshape(-1, 1)).ravel()
        yhat_val = y_scaler.inverse_transform(grid.predict(X_val).reshape(-1, 1)).ravel()
        ytrain_true = y[train_idx, :].ravel()
        yval_true = y[val_idx, :].ravel()

        train_r2 = _safe_r2(ytrain_true, yhat_train)
        val_r2 = _safe_r2(yval_true, yhat_val)
        train_rmse = _rmse(ytrain_true, yhat_train)
        val_rmse = _rmse(yval_true, yhat_val)
        print(
            "Metrics: "
            f"R2(train={_format_metric(train_r2)}, val={_format_metric(val_r2)}), "
            f"RMSE(train={_format_metric(train_rmse)}, val={_format_metric(val_rmse)})"
        )
        overfit = _compute_overfitting_diagnostics(train_r2, val_r2, train_rmse, val_rmse)
        if bool(overfit["overfit_warning"]):
            print(
                f"Warning: potential overfitting for {var} with model={model_type_norm}. "
                f"{overfit['overfit_reason']}"
            )

        perm_seed = (
            int(permutation_random_state)
            if permutation_random_state is not None
            else (int(split_random_state) if split_random_state is not None else 42)
        ) + int(ivar)
        phase_start = time.perf_counter()
        permutation_importance = _permutation_importance_rmse(
            grid,
            X_val,
            y_scaler,
            yval_true,
            input_feature_names,
            n_repeats=int(permutation_repeats),
            random_state=perm_seed,
        )
        _log_phase_timing(
            "permutation_importance",
            phase_start,
            target=var,
            repeats=permutation_repeats,
        )

        stats[var] = {
            "r2_train": train_r2,
            "r2_val": val_r2,
            "rmse_train": train_rmse,
            "rmse_val": val_rmse,
            "r2_gap": overfit["r2_gap"],
            "rmse_ratio": overfit["rmse_ratio"],
            "overfit_warning": overfit["overfit_warning"],
            "overfit_reason": overfit["overfit_reason"],
            "permutation_repeats": int(permutation_repeats),
            "permutation_importance_rmse": permutation_importance,
        }
        model_store[var] = grid
        x_scaler_store[var] = x_scaler
        y_scaler_store[var] = y_scaler

        if not minimal_output:
            _save_scatter_plot(
                y_train_true=ytrain_true,
                y_train_pred=yhat_train,
                y_val_true=yval_true,
                y_val_pred=yhat_val,
                outdir=outdir,
                var=var,
                train_r2=train_r2,
                val_r2=val_r2,
                train_rmse=train_rmse,
                val_rmse=val_rmse,
            )

    training_layout = {
        "input_feature_names": input_feature_names,
        "input_feature_names_all": list(all_input_feature_names),
        "selected_feature_indices": [int(v) for v in selected_idx.tolist()],
        "surface_feature_names": list(ref.surface_feature_names),
        "climatology_feature_names": list(ref.climatology_feature_names),
        "spinup_vars": list(spinup_vars_list),
        "model_type": model_type_norm,
        "feature_set": feature_set_norm,
        "clim_feature_include": _normalize_glob_patterns(clim_feature_include),
        "explicit_feature_subset": _normalize_feature_subset(explicit_feature_subset),
        "apply_variance_filter": bool(apply_variance_filter),
        "variance_threshold": float(variance_threshold),
        "apply_corr_filter": bool(apply_corr_filter),
        "corr_threshold": float(corr_threshold),
        "forcing_vars_for_climatology": list(forcing_vars_list),
        "clim_feature_mode": clim_feature_mode_norm,
        "n_params": int(ref.params.shape[1]),
        "n_surface": int(ref.surface.shape[1]),
        "n_climatology": int(ref.climatology.shape[1]),
        "multi_case": len(blocks) > 1,
        "output_label": output_label,
        "case_names": case_names,
        "spinup_case_names": [
            str(getattr(sc if sc is not None else c, "casename", ""))
            for c, sc in zip(cases, spinup_cases_resolved)
        ],
        "nsamples_per_case": {block.case_name: int(block.nsamples) for block in blocks},
        "feature_diagnostics": feature_diagnostics,
    }

    resolved_stats_id = _resolve_stats_run_id(stats_run_id, split_random_state)
    safe_id = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in resolved_stats_id)
    stats_path = outdir / f"surrogate_spinup_stats_{safe_id}.json"
    _write_stats_json(
        stats_path,
        stats,
        model_type=model_type_norm,
        split_mode=split_mode,
        train_fraction=train_fraction,
        split_random_state=split_random_state,
        output_label=output_label,
        case_names=case_names,
        spinup_vars=spinup_vars_list,
        stats_run_id=resolved_stats_id,
        feature_names=input_feature_names,
        split_details=split_details,
        feature_diagnostics=feature_diagnostics,
        input_feature_names_all=all_input_feature_names,
    )

    if minimal_output:
        print(f"Saved spinup stats JSON to: {stats_path}")
        return {
            "case_names": case_names,
            "spinup_vars": list(spinup_vars_list),
            "model_type": model_type_norm,
            "split_mode": split_mode,
            "train_fraction": train_fraction,
            "split_random_state": split_random_state,
            "stats": stats,
            "split_details": split_details,
            "feature_diagnostics": feature_diagnostics,
            "training_layout": training_layout,
            "stats_path": str(stats_path),
            "minimal_output": True,
        }

    artifact: Dict[str, Any] = {
        "case_names": case_names,
        "spinup_vars": list(spinup_vars_list),
        "model_type": model_type_norm,
        "surface_vars": list(surface_vars_list),
        "forcing_vars_for_climatology": list(forcing_vars_list),
        "clim_feature_mode": clim_feature_mode_norm,
        "split_mode": split_mode,
        "train_fraction": train_fraction,
        "split_random_state": split_random_state,
        "models": model_store,
        "x_scaler": x_scaler_store,
        "y_scaler": y_scaler_store,
        "stats": stats,
        "split_details": split_details,
        "feature_diagnostics": feature_diagnostics,
        "training_layout": training_layout,
        "stats_path": str(stats_path),
    }
    with open(outdir / "surrogate_spinup_artifacts.pkl", "wb") as fp:
        pickle.dump(artifact, fp)
    print(f"Saved spinup surrogate artifacts to: {outdir}")
    return artifact


def load_surrogate_spinup_artifacts(case: Any, artifact_path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(artifact_path).expanduser().resolve()
    if path.is_dir():
        path = path / "surrogate_spinup_artifacts.pkl"
    if not path.is_file():
        raise FileNotFoundError(f"Spinup surrogate artifacts not found: {path}")
    with open(path, "rb") as fp:
        artifact = pickle.load(fp)

    if "models" not in artifact or "x_scaler" not in artifact or "y_scaler" not in artifact:
        raise ValueError(f"Spinup artifact missing required model/scaler keys: {path}")
    layout = dict(artifact.get("training_layout", {}))
    model_type = _normalize_model_type(layout.get("model_type", artifact.get("model_type", "nn")))
    layout.setdefault("model_type", model_type)
    artifact["model_type"] = model_type
    n_params = int(layout.get("n_params", -1))
    if n_params <= 0:
        raise ValueError("Spinup artifact missing training_layout['n_params']")
    if int(case.nparms_ensemble) != n_params:
        raise ValueError(
            f"Parameter count mismatch between case ({case.nparms_ensemble}) and spinup artifact ({n_params})"
        )

    case.surrogate_spinup = artifact["models"]
    case.x_scaler_spinup = artifact["x_scaler"]
    case.y_scaler_spinup = artifact["y_scaler"]
    case.spinup_surrogate_training = layout
    return artifact


def build_spinup_inference_features(
    case: Any,
    training_layout: Dict[str, Any],
    spinup_case: Optional[Any] = None,
    surface_vars: Optional[Sequence[str]] = None,
    forcing_vars: Optional[Sequence[str]] = None,
    clim_feature_mode: Optional[str] = None,
    surface_member: Optional[int] = None,
) -> Dict[str, Any]:
    surface_vars_used = list(
        training_layout.get("surface_feature_names", surface_vars if surface_vars is not None else DEFAULT_SURFACE_VARS)
    )
    forcing_vars_used = list(
        training_layout.get(
            "forcing_vars_for_climatology",
            forcing_vars if forcing_vars is not None else DEFAULT_CLIM_FORCING_VARS,
        )
    )
    n_surface = int(training_layout.get("n_surface", len(surface_vars_used)))
    n_clim = int(training_layout.get("n_climatology", -1))
    mode = (
        str(clim_feature_mode).strip().lower()
        if clim_feature_mode is not None
        else str(training_layout.get("clim_feature_mode", "full")).strip().lower()
    )
    if mode not in ("full", "compact"):
        raise ValueError(f"Unsupported clim_feature_mode='{mode}'. Use 'full' or 'compact'.")

    ntime_ref = _inference_target_ntime(case)
    forcing_raw, forcing_used, forcing_time = _load_forcing_matrix(Path(case.metdir), forcing_vars_used, ntime_ref)
    forcing_cycle_raw, forcing_cycle_time = _subset_forcing_to_spinup_cycle(
        case, forcing_raw, forcing_time, spinup_case=spinup_case
    )
    clim_vec, clim_names = _climatology_features(
        forcing_cycle_raw,
        forcing_used,
        forcing_cycle_time,
        clim_feature_mode=mode,
    )
    if n_clim > 0 and clim_vec.size != n_clim:
        raise ValueError(
            f"Climatology feature count mismatch: expected {n_clim}, built {clim_vec.size}. "
            "Check forcing vars and training layout."
        )
    if surface_member is None:
        if not hasattr(case, "nsamples"):
            raise AttributeError("Case is missing nsamples; required to average surface features.")
        nmembers = int(case.nsamples)
        if nmembers <= 0:
            raise ValueError(f"Invalid nsamples={nmembers} for surface-feature mean.")
        sfc = np.zeros((nmembers, len(surface_vars_used)), dtype=np.float64)
        for ens in range(1, nmembers + 1):
            sfc[ens - 1, :] = _surface_feature_state(case, ens, surface_vars_used)
        surface_vec = np.nanmean(sfc, axis=0)
    else:
        surface_vec = _surface_feature_state(case, int(surface_member), surface_vars_used)

    if surface_vec.size != n_surface:
        raise ValueError(
            f"Surface feature count mismatch: expected {n_surface}, got {surface_vec.size}. "
            "Check surface vars and training layout."
        )

    return {
        "surface": np.asarray(surface_vec, dtype=np.float64).ravel(),
        "climatology": np.asarray(clim_vec, dtype=np.float64).ravel(),
        "surface_feature_names": list(surface_vars_used),
        "climatology_feature_names": list(clim_names),
        "clim_feature_mode": mode,
    }


def predict_spinup_state(
    case: Any,
    parms: np.ndarray,
    spinup_vars: Optional[Union[str, Sequence[str]]] = None,
    X: Optional[np.ndarray] = None,
    surface: Optional[np.ndarray] = None,
    climatology: Optional[np.ndarray] = None,
) -> Dict[str, np.ndarray]:
    if not hasattr(case, "surrogate_spinup") or not hasattr(case, "spinup_surrogate_training"):
        raise AttributeError("Spinup surrogate not attached to case. Load or train spinup surrogate first.")
    myvars = (
        list(case.spinup_surrogate_training.get("spinup_vars", []))
        if spinup_vars is None
        else _normalize_var_list(spinup_vars)
    )
    if not myvars:
        raise ValueError("No spinup variables requested for prediction.")

    meta = case.spinup_surrogate_training
    n_params = int(meta["n_params"])
    n_surface = int(meta["n_surface"])
    n_clim = int(meta["n_climatology"])
    selected_idx_raw = meta.get("selected_feature_indices", None)
    selected_idx: Optional[np.ndarray]
    if selected_idx_raw is None:
        selected_idx = None
    else:
        selected_idx = np.asarray(selected_idx_raw, dtype=np.int32).reshape(-1)
    expected_full_cols = n_params + n_surface + n_clim
    expected_model_cols = int(selected_idx.size) if selected_idx is not None else expected_full_cols

    if X is None:
        pr = np.asarray(parms, dtype=np.float64)
        if pr.ndim == 1:
            pr = pr.reshape(1, -1)
        if pr.ndim != 2 or pr.shape[1] != n_params:
            raise ValueError(f"parms must have shape (n, {n_params}), got {pr.shape}")
        if surface is None or climatology is None:
            raise ValueError("surface and climatology vectors are required when X is not provided.")
        sfc = np.asarray(surface, dtype=np.float64).ravel()
        clim = np.asarray(climatology, dtype=np.float64).ravel()
        if sfc.size != n_surface:
            raise ValueError(f"surface vector must have length {n_surface}, got {sfc.size}")
        if clim.size != n_clim:
            raise ValueError(f"climatology vector must have length {n_clim}, got {clim.size}")
        X = np.empty((pr.shape[0], expected_full_cols), dtype=np.float64)
        X[:, :n_params] = pr
        X[:, n_params : n_params + n_surface] = sfc
        X[:, n_params + n_surface :] = clim
        if selected_idx is not None:
            X = X[:, selected_idx]
    else:
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError(f"X must be 2-D, got {X.shape}")
        if X.shape[1] == expected_full_cols and selected_idx is not None:
            X = X[:, selected_idx]
        elif X.shape[1] not in (expected_full_cols, expected_model_cols):
            raise ValueError(
                f"X must have shape (n, {expected_full_cols}) full features "
                f"or (n, {expected_model_cols}) selected features, got {X.shape}"
            )

    out: Dict[str, np.ndarray] = {}
    for var in myvars:
        if var not in case.surrogate_spinup:
            raise KeyError(f"No trained spinup surrogate for variable '{var}'")
        xnorm = case.x_scaler_spinup[var].transform(X)
        pred = case.surrogate_spinup[var].predict(xnorm)
        y = case.y_scaler_spinup[var].inverse_transform(np.asarray(pred).reshape(-1, 1))
        out[var] = y.ravel()
    return out
