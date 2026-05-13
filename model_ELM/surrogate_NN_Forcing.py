#!/usr/bin/env python
from __future__ import annotations

import hashlib
import os
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

DEFAULT_SPINUP_VARS = ("TOTSOMC", "TOTSOMN")
SPINUP_VAR_SUM: Dict[str, List[str]] = {
    "TOTSOMC": ["totsomc"],
    "TOTSOMN": [
        "litr1n",
        "litr2n",
        "litr3n",
        "cwdn",
        "soil1n",
        "soil2n",
        "soil3n",
        "soil4n",
    ],
}


@dataclass
class _PreparedCaseTrainingBlock:
    case_name: str
    member_site_labels: np.ndarray
    params: np.ndarray
    forcing_features: np.ndarray
    forcing_vars_used: List[str]
    forcing_feature_names: List[str]
    spinup: np.ndarray
    spinup_vars: List[str]
    targets: Dict[str, np.ndarray]

    @property
    def nsamples(self) -> int:
        return int(self.params.shape[0])

    @property
    def ntime(self) -> int:
        return int(self.forcing_features.shape[0])


def _normalize_var_list(myvars: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(myvars, str):
        return [s.strip() for s in myvars.split(",") if s.strip()]
    return [str(v).strip() for v in myvars if str(v).strip()]


def _memory_mb(arr: np.ndarray) -> float:
    return float(arr.nbytes) / (1024.0 * 1024.0)


def _estimate_memory(rows: int, cols: int, dtype: str) -> float:
    itemsize = np.dtype(dtype).itemsize
    return (rows * cols * itemsize) / (1024.0 * 1024.0 * 1024.0)


def _rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    out = np.zeros_like(values, dtype=np.float64)
    csum = np.cumsum(np.insert(values.astype(np.float64), 0, 0.0))
    for i in range(values.size):
        start = max(0, i - window + 1)
        count = i - start + 1
        out[i] = (csum[i + 1] - csum[start]) / count
    return out


def _rolling_sum(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    out = np.zeros_like(values, dtype=np.float64)
    csum = np.cumsum(np.insert(values.astype(np.float64), 0, 0.0))
    for i in range(values.size):
        start = max(0, i - window + 1)
        out[i] = csum[i + 1] - csum[start]
    return out


def _time_features(nhours: int) -> np.ndarray:
    hour = np.arange(nhours) % 24
    sin_hour = np.sin(2.0 * np.pi * hour / 24.0)
    cos_hour = np.cos(2.0 * np.pi * hour / 24.0)
    return np.column_stack((sin_hour, cos_hour))


def _collect_forcing_files(metdir: Path) -> List[Path]:
    if not metdir.exists():
        raise FileNotFoundError(f"Forcing directory does not exist: {metdir}")
    files = sorted([p for p in metdir.rglob("*.nc") if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No forcing .nc files found under: {metdir}")
    return files


def _load_forcing_matrix(
    metdir: Path,
    forcing_vars: Sequence[str],
    ntarget: int,
) -> Tuple[np.ndarray, List[str]]:
    files = _collect_forcing_files(metdir)
    print("Find forcing data: ")
    print([p.name for p in files])
    ds = xr.open_mfdataset([str(p) for p in files], combine="by_coords")

    used_vars: List[str] = []
    features: List[np.ndarray] = []
    for var in forcing_vars:
        if var not in ds.variables:
            continue
        var_hourly = (ds[var].coarsen(time=2).mean()).convert_calendar("noleap", dim="time")
        arr = np.asarray(var_hourly).squeeze()
        if arr.ndim > 1:
            arr = np.mean(arr, axis=tuple(range(1, arr.ndim)))
        if arr.ndim != 1:
            continue
        used_vars.append(var)
        features.append(arr.astype(np.float64))

    if not features:
        raise ValueError(
            "None of requested forcing variables were found. "
            f"Requested: {forcing_vars}"
        )

    forcing = np.column_stack(features)
    nhours = min(ntarget, forcing.shape[0])
    if forcing.shape[0] != ntarget:
        print(
            f"Warning: forcing rows ({forcing.shape[0]}) != target rows ({ntarget}); "
            f"truncating to {nhours}"
        )
    ds.close()
    return forcing[:nhours, :], used_vars


def _engineer_forcing_features(
    forcing_raw: np.ndarray,
    forcing_var_names: Sequence[str],
    tair_var: str,
    precip_var: str,
) -> Tuple[np.ndarray, List[str]]:
    nhours, _ = forcing_raw.shape
    tfeat = _time_features(nhours)
    feat_list: List[np.ndarray] = [forcing_raw, tfeat]
    names: List[str] = list(forcing_var_names) + ["sin_hour", "cos_hour"]

    name_to_idx = {name: i for i, name in enumerate(forcing_var_names)}
    if tair_var in name_to_idx:
        tair = forcing_raw[:, name_to_idx[tair_var]]
        for hours in (24, 24 * 7, 24 * 30):
            feat_list.append(_rolling_mean(tair, hours)[:, None])
            names.append(f"{tair_var}_mean_{hours}h")
    else:
        print(f"Warning: temperature variable '{tair_var}' not found; skip T rolling means")

    if precip_var in name_to_idx:
        pr = forcing_raw[:, name_to_idx[precip_var]]
        for hours in (24, 24 * 7, 24 * 30):
            feat_list.append(_rolling_sum(pr, hours)[:, None])
            names.append(f"{precip_var}_sum_{hours}h")
    else:
        print(
            f"Warning: precipitation variable '{precip_var}' not found; "
            "skip precipitation rolling sums"
        )

    for i, var in enumerate(forcing_var_names):
        if var in ["FLDS", "QBOT", "WIND", "PSRF", "RH"]:
            continue
        anom = forcing_raw[:, i] - _rolling_mean(forcing_raw[:, i], 24 * 30)
        feat_list.append(anom[:, None])
        names.append(f"{var}_anom_30d")

    out = np.column_stack(feat_list)
    return out, names


def _restart_file(case: Any, ens_num: int) -> Path:
    gst = str(100000 + ens_num)[1:]
    finidat_file_path = os.path.abspath(case.runroot) + "/UQ/" + case.dependcase + "/g" + gst
    finidat_file_name = case.finidat.split("/")[-1]
    finidat_file_new = finidat_file_path + "/" + finidat_file_name
    return Path(finidat_file_new)


def _spinup_state(case: Any, ens_num: int, spinup_vars: Sequence[str]) -> np.ndarray:
    fpath = _restart_file(case, ens_num)
    if not fpath.exists():
        raise FileNotFoundError(f"Missing restart file for ensemble {ens_num}: {fpath}")

    vals: List[float] = []
    with Dataset(str(fpath), "r") as nc:
        for var in spinup_vars:
            if var in SPINUP_VAR_SUM.keys():
                sum_value = 0.0
                for sum_vars in SPINUP_VAR_SUM[var]:
                    if sum_vars not in nc.variables:
                        raise KeyError(f"Spinup variable '{sum_vars}' not found in {fpath}")
                    sum_value = sum_value + np.nansum(nc.variables[sum_vars][:])
            else:
                if var not in nc.variables:
                    raise KeyError(f"Spinup variable '{var}' not found in {fpath}")
                sum_value = np.nansum(nc.variables[var][:])
            vals.append(float(sum_value))
    return np.asarray(vals, dtype=np.float64)


def _validate_split_indices(
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    split_mode: str,
    train_fraction: float,
) -> None:
    if train_idx.size == 0 or val_idx.size == 0:
        raise ValueError(
            f"split_mode={split_mode} with train_fraction={train_fraction} produced "
            "an empty train or validation set. Adjust train_fraction or provide more "
            "cases/sites/members."
        )


def _build_split_indices(
    row_case_ids: np.ndarray,
    row_member_ids: np.ndarray,
    row_time_ids: np.ndarray,
    row_site_ids: np.ndarray,
    split_mode: str,
    train_fraction: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build train/validation row indices from centralized row metadata.

    The split logic is isolated here so future work can add randomized contiguous
    time-window selection for repeated robustness experiments without changing the
    dataset-assembly or model-fitting code.
    """
    all_idx = np.arange(row_case_ids.size)
    train_mask = np.zeros(row_case_ids.size, dtype=bool)

    if split_mode == "by_member":
        for case_id in np.unique(row_case_ids):
            case_mask = row_case_ids == case_id
            members = np.unique(row_member_ids[case_mask])
            ntrain_m = max(1, int(len(members) * train_fraction))
            train_members = members[:ntrain_m]
            train_mask[case_mask] = np.isin(row_member_ids[case_mask], train_members)
    elif split_mode == "by_time_block":
        for case_id in np.unique(row_case_ids):
            case_mask = row_case_ids == case_id
            time_ids = np.unique(row_time_ids[case_mask])
            cutoff = max(1, int(len(time_ids) * train_fraction))
            train_times = time_ids[:cutoff]
            train_mask[case_mask] = np.isin(row_time_ids[case_mask], train_times)
    elif split_mode == "by_site":
        sites = np.unique(row_site_ids)
        ntrain_s = max(1, int(len(sites) * train_fraction))
        train_sites = sites[:ntrain_s]
        train_mask = np.isin(row_site_ids, train_sites)
    else:
        raise ValueError(f"Unsupported split mode: {split_mode}")

    train_idx = all_idx[train_mask]
    val_idx = all_idx[~train_mask]
    _validate_split_indices(train_idx, val_idx, split_mode, train_fraction)
    return train_idx, val_idx


def _group_time_stats(
    time_ids: np.ndarray,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    ntime: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    true_mean = np.full(ntime, np.nan, dtype=np.float64)
    pred_mean = np.full(ntime, np.nan, dtype=np.float64)
    true_std = np.full(ntime, np.nan, dtype=np.float64)
    pred_std = np.full(ntime, np.nan, dtype=np.float64)

    for t in range(ntime):
        mask = time_ids == t
        if not np.any(mask):
            continue
        true_t = y_true[mask]
        pred_t = y_pred[mask]
        true_mean[t] = np.mean(true_t)
        pred_mean[t] = np.mean(pred_t)
        true_std[t] = np.std(true_t)
        pred_std[t] = np.std(pred_t)
    return true_mean, pred_mean, true_std, pred_std


def _safe_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if y_true.size < 2 or y_pred.size < 2:
        return float("nan")
    corr = np.corrcoef(np.asarray(y_true, dtype=np.float64), np.asarray(y_pred, dtype=np.float64))[0, 1]
    if not np.isfinite(corr):
        return float("nan")
    return float(corr**2)


def _format_metric(value: float) -> str:
    if not np.isfinite(value):
        return "n/a"
    return f"{value:.4f}"


def _save_plot(
    train_true_mean: np.ndarray,
    train_pred_mean: np.ndarray,
    train_true_std: np.ndarray,
    train_pred_std: np.ndarray,
    val_true_mean: np.ndarray,
    val_pred_mean: np.ndarray,
    val_true_std: np.ndarray,
    val_pred_std: np.ndarray,
    var: str,
    outdir: Path,
    r2_train: float,
    r2_val: float,
    plot_label: Optional[str] = None,
) -> None:
    fig, ax = plt.subplots(2, 1, figsize=(15, 5), sharex=True)
    x = np.arange(train_true_mean.size)
    ls_train, ls_val = "None", "--"
    mk_train, mk_val = "o", "v"

    ax[0].plot(
        x,
        train_true_mean,
        color="blue",
        linestyle=ls_train,
        linewidth=1,
        marker=mk_train,
        markersize=0.1,
        label="ELM mean (train)",
        alpha=0.4,
    )
    ax[0].plot(
        x,
        train_pred_mean,
        color="red",
        linestyle=ls_train,
        linewidth=1,
        marker=mk_train,
        markersize=0.1,
        label="Surrogate mean (train)",
        alpha=0.4,
    )
    ax[0].plot(
        x,
        val_true_mean,
        color="blue",
        linestyle=ls_val,
        linewidth=1,
        marker=mk_val,
        markersize=0.1,
        label="ELM mean (val)",
        alpha=0.6,
    )
    ax[0].plot(
        x,
        val_pred_mean,
        color="red",
        linestyle=ls_val,
        linewidth=1,
        marker=mk_val,
        markersize=0.1,
        label="Surrogate mean (val)",
        alpha=0.6,
    )

    m_t_elm = np.isfinite(train_true_mean) & np.isfinite(train_true_std)
    m_t_sur = np.isfinite(train_pred_mean) & np.isfinite(train_pred_std)
    m_v_elm = np.isfinite(val_true_mean) & np.isfinite(val_true_std)
    m_v_sur = np.isfinite(val_pred_mean) & np.isfinite(val_pred_std)
    ax[0].fill_between(
        x,
        train_true_mean - train_true_std,
        train_true_mean + train_true_std,
        where=m_t_elm,
        color="blue",
        alpha=0.2,
        linewidth=0,
        label="ELM ±1 std (train)",
    )
    ax[0].fill_between(
        x,
        train_pred_mean - train_pred_std,
        train_pred_mean + train_pred_std,
        where=m_t_sur,
        color="red",
        alpha=0.2,
        linewidth=0,
        label="Surrogate ±1 std (train)",
    )
    ax[0].fill_between(
        x,
        val_true_mean - val_true_std,
        val_true_mean + val_true_std,
        where=m_v_elm,
        color="blue",
        alpha=0.2,
        linewidth=0,
        label="ELM ±1 std (val)",
    )
    ax[0].fill_between(
        x,
        val_pred_mean - val_pred_std,
        val_pred_mean + val_pred_std,
        where=m_v_sur,
        color="red",
        alpha=0.2,
        linewidth=0,
        label="Surrogate ±1 std (val)",
    )
    ax[0].set_ylabel(var)
    ax[0].grid()
    ax[0].legend(loc="best", fontsize=8, ncol=2)
    ax[0].text(
        0.02,
        0.98,
        f"Train $R^2$ = {_format_metric(r2_train)}\nVal $R^2$ = {_format_metric(r2_val)}",
        transform=ax[0].transAxes,
        va="top",
        ha="left",
        fontsize=10,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.88, "edgecolor": "0.75"},
    )

    diff_train = train_true_mean - train_pred_mean
    diff_val = val_true_mean - val_pred_mean
    diff_train_std = np.sqrt(train_true_std**2 + train_pred_std**2)
    diff_val_std = np.sqrt(val_true_std**2 + val_pred_std**2)
    ax[1].plot(x, diff_train, color="black", linestyle=ls_train, label="ELM-Surrogate (train)",alpha=0.8)
    ax[1].plot(x, diff_val, color="black", linestyle=ls_val, label="ELM-Surrogate (val)",alpha=0.8)
    m_dt = np.isfinite(diff_train) & np.isfinite(diff_train_std)
    m_dv = np.isfinite(diff_val) & np.isfinite(diff_val_std)
    ax[1].fill_between(
        x,
        diff_train - diff_train_std,
        diff_train + diff_train_std,
        where=m_dt,
        color="gray",
        alpha=0.3,
        linewidth=0,
        label="Diff. ±1 std (train)",
    )
    ax[1].fill_between(
        x,
        diff_val - diff_val_std,
        diff_val + diff_val_std,
        where=m_dv,
        color="gray",
        alpha=0.3,
        linewidth=0,
        label="Diff. ±1 std (val)",
    )
    ax[1].set_ylabel(var)
    ax[1].set_xlabel("Time index")
    ax[1].grid()
    ax[1].legend(loc="best", fontsize=8)
    if plot_label:
        fig.suptitle(plot_label)
        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))
    else:
        fig.tight_layout()
    fig.savefig(str(outdir / f"{var}_surrogate_forcing.png"))
    plt.close(fig)


def _parse_site_labels(case: Any, nsamples: int) -> np.ndarray:
    if hasattr(case, "site_labels"):
        labels = np.asarray(case.site_labels).astype(str)
        if labels.size == nsamples:
            return labels
    if hasattr(case, "site") and case.site != "":
        return np.asarray([case.site] * nsamples)
    return np.asarray(["site0"] * nsamples)


def _data_preflight(
    rows: int,
    nfeatures: int,
    dtype: str,
) -> None:
    print(f"Rows: {rows}, Features: {nfeatures}")
    print(f"Estimated X memory (float32): {_estimate_memory(rows, nfeatures, 'float32'):.3f} GB")
    print(f"Estimated X memory (float64): {_estimate_memory(rows, nfeatures, 'float64'):.3f} GB")
    print(f"Configured dtype: {dtype}")


def _ensure_forcing_surrogate_dicts(case: Any) -> None:
    if not hasattr(case, "surrogate_forcing") or case.surrogate_forcing is None:
        case.surrogate_forcing = {}
    if not hasattr(case, "x_scaler_forcing") or case.x_scaler_forcing is None:
        case.x_scaler_forcing = {}
    if not hasattr(case, "y_scaler_forcing") or case.y_scaler_forcing is None:
        case.y_scaler_forcing = {}


def _resolve_output_label(case_names: Sequence[str], run_name: Optional[str]) -> str:
    label = "" if run_name is None else str(run_name).strip()
    if label:
        return label
    if len(case_names) == 1:
        return case_names[0]
    digest = hashlib.sha1(",".join(case_names).encode("utf-8")).hexdigest()[:8]
    return f"multicase_{len(case_names)}cases_{digest}"


def _prepare_case_training_block(
    case: Any,
    outvars: Sequence[str],
    forcing_vars_list: Sequence[str],
    tair_var: str,
    precip_var: str,
    spinup_vars_list: Sequence[str],
) -> _PreparedCaseTrainingBlock:
    case_name = str(getattr(case, "casename", "case"))
    print(f"\nPreparing case block: {case_name}")

    if not hasattr(case, "samples"):
        raise AttributeError(f"Case '{case_name}' missing 'samples'")
    if not hasattr(case, "output"):
        raise AttributeError(f"Case '{case_name}' missing 'output'")

    params = np.asarray(case.samples).transpose().astype(np.float64)
    if params.ndim != 2:
        raise ValueError(f"Case '{case_name}' samples must be 2-D after transpose, got {params.shape}")
    nsamples = params.shape[0]
    print("Load ensemble parameters:")
    print(f"{nsamples} ensemble members")
    print(f"{params.shape[1]} parameters")

    for var in outvars:
        if var not in case.output:
            raise KeyError(f"Requested output variable not in case.output for '{case_name}': {var}")

    print("Load model outputs:")
    y_ref = np.asarray(case.output[outvars[0]]).transpose()
    if y_ref.ndim != 2:
        raise ValueError(
            f"Case '{case_name}' output for '{outvars[0]}' must be 2-D after transpose, got {y_ref.shape}"
        )
    ntime = y_ref.shape[1]
    print("Number of hours:", ntime)

    metdir = Path(case.metdir)
    print(f"Loading forcing data from:\n {metdir}")
    forcing_raw, forcing_used = _load_forcing_matrix(metdir, forcing_vars_list, ntime)
    ntime = forcing_raw.shape[0]
    forcing_features, forcing_feature_names = _engineer_forcing_features(
        forcing_raw,
        forcing_used,
        tair_var,
        precip_var,
    )
    print("Forcing data size:")
    print(forcing_features.shape)
    print(forcing_feature_names)

    print("Loading spinup state")
    spinup = np.zeros((nsamples, len(spinup_vars_list)), dtype=np.float64)
    for ens in range(1, nsamples + 1):
        spinup[ens - 1, :] = _spinup_state(case, ens, spinup_vars_list)
    print("Spinup array size:")
    print(spinup.shape)

    targets: Dict[str, np.ndarray] = {}
    for var in outvars:
        yfull = np.asarray(case.output[var]).transpose()
        if yfull.shape[0] != nsamples:
            raise ValueError(
                f"Case '{case_name}' output '{var}' has {yfull.shape[0]} members, expected {nsamples}"
            )
        targets[var] = yfull[:, :ntime].astype(np.float64, copy=False)

    return _PreparedCaseTrainingBlock(
        case_name=case_name,
        member_site_labels=_parse_site_labels(case, nsamples),
        params=params,
        forcing_features=forcing_features,
        forcing_vars_used=list(forcing_used),
        forcing_feature_names=list(forcing_feature_names),
        spinup=spinup,
        spinup_vars=list(spinup_vars_list),
        targets=targets,
    )


def _validate_prepared_blocks(blocks: Sequence[_PreparedCaseTrainingBlock], outvars: Sequence[str]) -> None:
    if not blocks:
        raise ValueError("No case blocks were prepared for surrogate training.")

    ref = blocks[0]
    for block in blocks:
        if block.member_site_labels.size != block.nsamples:
            raise ValueError(
                f"Case '{block.case_name}' site_labels length {block.member_site_labels.size} "
                f"does not match nsamples={block.nsamples}"
            )
        if block.params.shape[1] != ref.params.shape[1]:
            raise ValueError(
                f"Case '{block.case_name}' parameter count {block.params.shape[1]} does not match "
                f"reference case '{ref.case_name}' ({ref.params.shape[1]})."
            )
        if block.spinup.shape[1] != ref.spinup.shape[1]:
            raise ValueError(
                f"Case '{block.case_name}' spinup feature count {block.spinup.shape[1]} does not match "
                f"reference case '{ref.case_name}' ({ref.spinup.shape[1]})."
            )
        if block.forcing_vars_used != ref.forcing_vars_used:
            raise ValueError(
                f"Case '{block.case_name}' forcing vars {block.forcing_vars_used} do not match "
                f"reference case '{ref.case_name}' ({ref.forcing_vars_used})."
            )
        if block.forcing_feature_names != ref.forcing_feature_names:
            raise ValueError(
                f"Case '{block.case_name}' forcing feature layout does not match reference case "
                f"'{ref.case_name}'."
            )
        if sorted(block.targets.keys()) != sorted(outvars):
            raise ValueError(
                f"Case '{block.case_name}' target vars {sorted(block.targets.keys())} do not match "
                f"requested vars {sorted(outvars)}."
            )


def _flatten_targets_for_blocks(
    blocks: Sequence[_PreparedCaseTrainingBlock],
    var: str,
    dtype_np: np.dtype,
) -> np.ndarray:
    rows = sum(block.nsamples * block.ntime for block in blocks)
    y_rows = np.empty((rows, 1), dtype=dtype_np)
    offset = 0
    for block in blocks:
        flat = block.targets[var].reshape(-1, 1).astype(dtype_np, copy=False)
        end = offset + flat.shape[0]
        y_rows[offset:end, :] = flat
        offset = end
    return y_rows


def _case_plot_label(block: _PreparedCaseTrainingBlock) -> str:
    unique_sites = np.unique(block.member_site_labels.astype(str))
    if unique_sites.size == 1 and unique_sites[0] not in ("", block.case_name):
        return f"{block.case_name} [{unique_sites[0]}]"
    return block.case_name


def _save_case_plots(
    blocks: Sequence[_PreparedCaseTrainingBlock],
    row_case_ids: np.ndarray,
    row_time_ids: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    y_true_full: np.ndarray,
    y_pred_full: np.ndarray,
    uq_out: Path,
    var: str,
) -> None:
    train_mask = np.zeros(row_case_ids.size, dtype=bool)
    val_mask = np.zeros(row_case_ids.size, dtype=bool)
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    single_case = len(blocks) == 1

    for case_id, block in enumerate(blocks):
        case_mask = row_case_ids == case_id
        case_train_mask = case_mask & train_mask
        case_val_mask = case_mask & val_mask

        tr_tm, tr_pm, tr_ts, tr_ps = _group_time_stats(
            row_time_ids[case_train_mask],
            y_true_full[case_train_mask],
            y_pred_full[case_train_mask],
            block.ntime,
        )
        v_tm, v_pm, v_ts, v_ps = _group_time_stats(
            row_time_ids[case_val_mask],
            y_true_full[case_val_mask],
            y_pred_full[case_val_mask],
            block.ntime,
        )

        plot_dir = uq_out if single_case else (uq_out / block.case_name)
        plot_dir.mkdir(parents=True, exist_ok=True)
        _save_plot(
            tr_tm,
            tr_pm,
            tr_ts,
            tr_ps,
            v_tm,
            v_pm,
            v_ts,
            v_ps,
            var,
            plot_dir,
            _safe_r2(y_true_full[case_train_mask], y_pred_full[case_train_mask]),
            _safe_r2(y_true_full[case_val_mask], y_pred_full[case_val_mask]),
            plot_label=_case_plot_label(block),
        )


def _train_surrogate_with_prepared_blocks(
    blocks: Sequence[_PreparedCaseTrainingBlock],
    outvars: Sequence[str],
    tair_var: str,
    precip_var: str,
    split_mode: str,
    train_fraction: float,
    dtype: str,
    n_jobs: int,
    cv_folds: int,
    quick_grid: bool,
    dry_run: bool,
    outputdir: str,
    output_label: str,
    chunk_size: int = 50000,
    attach_case: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    del chunk_size  # reserved for future chunked IO
    _validate_prepared_blocks(blocks, outvars)

    ref = blocks[0]
    rows = sum(block.nsamples * block.ntime for block in blocks)
    nfeatures = ref.forcing_features.shape[1] + ref.params.shape[1] + ref.spinup.shape[1]
    _data_preflight(rows, nfeatures, dtype)
    print(f"Final X will be {rows}x{nfeatures}")
    print(f"Training cases: {[block.case_name for block in blocks]}")

    if dry_run:
        print("Dry-run only. Exiting before training.")
        return None

    if n_jobs * cv_folds > 128:
        print(
            "Warning: n_jobs * cv_folds is large; verify node memory "
            "and consider quick-grid mode."
        )

    dtype_np = np.float32 if dtype == "float32" else np.float64
    outdir = Path(outputdir).resolve()
    uq_out = outdir / "UQ_output" / output_label / "surrogate_forcing"
    uq_out.mkdir(parents=True, exist_ok=True)
    x_memmap_path = uq_out / "X_forcing_memmap.dat"
    print("X forcing path is")
    print(x_memmap_path)
    X = np.memmap(x_memmap_path, mode="w+", dtype=dtype_np, shape=(rows, nfeatures))

    row_case_ids = np.empty(rows, dtype=np.int32)
    row_member_ids = np.empty(rows, dtype=np.int32)
    row_time_ids = np.empty(rows, dtype=np.int32)
    row_site_ids = np.empty(rows, dtype=np.int32)
    site_name_to_id: Dict[str, int] = {}
    site_names: List[str] = []

    print("Building feature matrix...")
    col_force_end = ref.forcing_features.shape[1]
    col_param_end = col_force_end + ref.params.shape[1]
    row_offset = 0
    for case_id, block in enumerate(blocks):
        forcing_block = block.forcing_features.astype(dtype_np, copy=False)
        time_index = np.arange(block.ntime, dtype=np.int32)
        for member_id in range(block.nsamples):
            start = row_offset
            end = row_offset + block.ntime
            X[start:end, :col_force_end] = forcing_block
            X[start:end, col_force_end:col_param_end] = block.params[member_id, :].astype(
                dtype_np, copy=False
            )
            X[start:end, col_param_end:] = block.spinup[member_id, :].astype(dtype_np, copy=False)
            row_case_ids[start:end] = case_id
            row_member_ids[start:end] = member_id
            row_time_ids[start:end] = time_index
            site_label = str(block.member_site_labels[member_id])
            if site_label not in site_name_to_id:
                site_name_to_id[site_label] = len(site_names)
                site_names.append(site_label)
            row_site_ids[start:end] = site_name_to_id[site_label]
            row_offset = end
    print(f"Feature matrix memory (mapped): ~{_memory_mb(np.asarray(X)):.1f} MB")

    train_idx, val_idx = _build_split_indices(
        row_case_ids=row_case_ids,
        row_member_ids=row_member_ids,
        row_time_ids=row_time_ids,
        row_site_ids=row_site_ids,
        split_mode=split_mode,
        train_fraction=train_fraction,
    )
    print(f"Train rows: {train_idx.size}, Val rows: {val_idx.size}")

    if quick_grid:
        param_grid = {
            "hidden_layer_sizes": [(64,), (128,)],
            "activation": ["relu"],
            "solver": ["adam"],
            "alpha": [1e-4, 1e-3],
            "learning_rate": ["adaptive"],
        }
    else:
        param_grid = {
            "hidden_layer_sizes": [(64,), (128,), (128, 64)],
            "activation": ["tanh", "relu"],
            "solver": ["adam", "lbfgs"],
            "alpha": [1e-4, 1e-3, 1e-2],
            "learning_rate": ["constant", "adaptive"],
        }

    model_store: Dict[str, GridSearchCV] = {}
    x_scaler_store: Dict[str, preprocessing.StandardScaler] = {}
    y_scaler_store: Dict[str, preprocessing.StandardScaler] = {}
    stats: Dict[str, Dict[str, float]] = {}

    if attach_case is not None:
        _ensure_forcing_surrogate_dicts(attach_case)

    for var in outvars:
        print(f"\nTraining variable: {var}")
        y_rows = _flatten_targets_for_blocks(blocks, var, dtype_np)

        if np.any(~np.isfinite(y_rows)):
            bad = int(np.sum(~np.isfinite(y_rows)))
            raise ValueError(f"Target {var} contains {bad} non-finite values")

        x_scaler = preprocessing.StandardScaler().fit(X[train_idx, :])
        X_train = x_scaler.transform(X[train_idx, :])
        X_val = x_scaler.transform(X[val_idx, :])

        y_scaler = preprocessing.StandardScaler().fit(y_rows[train_idx, :])
        y_train = y_scaler.transform(y_rows[train_idx, :]).ravel()
        y_val = y_scaler.transform(y_rows[val_idx, :]).ravel()

        clf = MLPRegressor(
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
            random_state=42,
        )
        grid = GridSearchCV(clf, param_grid, n_jobs=n_jobs, cv=cv_folds)
        grid.fit(X_train, y_train)

        yhat_train = y_scaler.inverse_transform(grid.predict(X_train).reshape(-1, 1)).ravel()
        yhat_val = y_scaler.inverse_transform(grid.predict(X_val).reshape(-1, 1)).ravel()
        ytrain_true = y_rows[train_idx, :].ravel()
        yval_true = y_rows[val_idx, :].ravel()

        train_r2 = _safe_r2(ytrain_true, yhat_train)
        val_r2 = _safe_r2(yval_true, yhat_val)
        print(f"R2 train={_format_metric(train_r2)}, val={_format_metric(val_r2)}")

        model_store[var] = grid
        x_scaler_store[var] = x_scaler
        y_scaler_store[var] = y_scaler
        stats[var] = {"r2_train": train_r2, "r2_val": val_r2}

        if attach_case is not None:
            attach_case.surrogate_forcing[var] = grid
            attach_case.x_scaler_forcing[var] = x_scaler
            attach_case.y_scaler_forcing[var] = y_scaler

        y_true_full = y_rows.ravel().astype(np.float64, copy=False)
        y_pred_full = np.full(rows, np.nan, dtype=np.float64)
        y_pred_full[train_idx] = yhat_train
        y_pred_full[val_idx] = yhat_val
        _save_case_plots(blocks, row_case_ids, row_time_ids, train_idx, val_idx, y_true_full, y_pred_full, uq_out, var)

    training_layout = {
        "forcing_feature_names": ref.forcing_feature_names,
        "forcing_vars_used": ref.forcing_vars_used,
        "spinup_vars": ref.spinup_vars,
        "n_forcing_cols": int(ref.forcing_features.shape[1]),
        "n_params": int(ref.params.shape[1]),
        "n_spinup": int(ref.spinup.shape[1]),
        "tair_var": tair_var,
        "precip_var": precip_var,
        "multi_case": len(blocks) > 1,
        "output_label": output_label,
        "case_names": [block.case_name for block in blocks],
        "ntime_per_case": {block.case_name: int(block.ntime) for block in blocks},
        "nsamples_per_case": {block.case_name: int(block.nsamples) for block in blocks},
        "site_labels_per_case": {
            block.case_name: np.unique(block.member_site_labels.astype(str)).tolist()
            for block in blocks
        },
    }

    if attach_case is not None:
        attach_case.forcing_surrogate_training = training_layout

    artifact: Dict[str, Any] = {
        "case": output_label,
        "case_names": [block.case_name for block in blocks],
        "outvars": list(outvars),
        "forcing_vars_used": ref.forcing_vars_used,
        "forcing_feature_names": ref.forcing_feature_names,
        "spinup_vars": ref.spinup_vars,
        "split_mode": split_mode,
        "train_fraction": train_fraction,
        "models": model_store,
        "x_scaler": x_scaler_store,
        "y_scaler": y_scaler_store,
        "stats": stats,
        "training_layout": training_layout,
    }
    with open(uq_out / "surrogate_forcing_artifacts.pkl", "wb") as fp:
        pickle.dump(artifact, fp)
    print(f"\nSaved surrogate artifacts to: {uq_out}")
    return artifact


def train_surrogate_with_forcing(
    self: Any,
    myvars: Union[str, Sequence[str]],
    forcing_vars: Optional[Sequence[str]] = None,
    tair_var: str = "TBOT",
    precip_var: str = "PRECTmms",
    spinup_vars: Optional[Sequence[str]] = None,
    split_mode: str = "by_time_block",
    train_fraction: float = 0.8,
    dtype: str = "float32",
    n_jobs: int = 8,
    cv_folds: int = 3,
    quick_grid: bool = False,
    dry_run: bool = False,
    outputdir: str = ".",
    chunk_size: int = 50000,
    run_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Train MLP surrogates mapping [engineered forcing | parameters | spinup] to hourly outputs.

    Saves plots and ``surrogate_forcing_artifacts.pkl`` under
    ``<outputdir>/UQ_output/<run_name-or-casename>/surrogate_forcing/``. Populates
    ``self.surrogate_forcing``, ``self.x_scaler_forcing``, ``self.y_scaler_forcing``,
    and ``self.forcing_surrogate_training``.

    Returns the artifact dict (or None if ``dry_run``).
    """
    outvars = _normalize_var_list(myvars)
    if forcing_vars is None:
        forcing_vars_list = [
            s.strip()
            for s in "PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF".split(",")
            if s.strip()
        ]
    else:
        forcing_vars_list = [str(v).strip() for v in forcing_vars if str(v).strip()]

    if spinup_vars is None:
        spinup_vars_list = list(DEFAULT_SPINUP_VARS)
    else:
        spinup_vars_list = [str(v).strip() for v in spinup_vars if str(v).strip()]
        if not spinup_vars_list:
            spinup_vars_list = list(DEFAULT_SPINUP_VARS)

    print("Model output variables:", outvars)
    print("Raw forcing variables:", forcing_vars_list)
    print("Spinup vars:", spinup_vars_list)

    block = _prepare_case_training_block(
        self,
        outvars,
        forcing_vars_list,
        tair_var,
        precip_var,
        spinup_vars_list,
    )
    return _train_surrogate_with_prepared_blocks(
        blocks=[block],
        outvars=outvars,
        tair_var=tair_var,
        precip_var=precip_var,
        split_mode=split_mode,
        train_fraction=train_fraction,
        dtype=dtype,
        n_jobs=n_jobs,
        cv_folds=cv_folds,
        quick_grid=quick_grid,
        dry_run=dry_run,
        outputdir=outputdir,
        output_label=_resolve_output_label([block.case_name], run_name),
        chunk_size=chunk_size,
        attach_case=self,
    )


def run_surrogate_forcing(
    self: Any,
    parms: Optional[np.ndarray],
    myvars: Union[str, Sequence[str]],
    X: Optional[np.ndarray] = None,
    forcing_engineered: Optional[np.ndarray] = None,
    spinup: Optional[np.ndarray] = None,
) -> Dict[str, np.ndarray]:
    """
    Apply trained forcing surrogates. Same pattern as ``run_surrogate``: pass ``parms`` (ensemble
    parameters) and ``myvars``. Either pass the full design matrix ``X`` (rows =
    ``[forcing | parms | spinup]``), or pass ``forcing_engineered`` and ``spinup`` together with
    ``parms`` to build ``X`` for a single member trajectory (one row per hour). When ``X`` is given,
    ``parms`` may be ``None``.
    """
    myvars_list = _normalize_var_list(myvars)
    _ensure_forcing_surrogate_dicts(self)

    if X is None:
        meta = getattr(self, "forcing_surrogate_training", None)
        if meta is None:
            raise ValueError(
                "Missing forcing_surrogate_training metadata; train first or pass X explicitly."
            )
        if forcing_engineered is None or spinup is None:
            raise ValueError(
                "When X is not provided, both forcing_engineered and spinup are required."
            )
        if parms is None:
            raise ValueError("parms is required when building X from forcing_engineered and spinup.")
        fe = np.asarray(forcing_engineered, dtype=np.float64)
        pr = np.asarray(parms, dtype=np.float64).ravel()
        sp = np.asarray(spinup, dtype=np.float64).ravel()
        nf = int(meta["n_forcing_cols"])
        nparam = int(meta["n_params"])
        nsp = int(meta["n_spinup"])
        if fe.ndim != 2 or fe.shape[1] != nf:
            raise ValueError(
                f"forcing_engineered must have shape (nhours, {nf}), got {fe.shape}"
            )
        if pr.size != nparam:
            raise ValueError(f"parms must have length {nparam}, got {pr.size}")
        if sp.size != nsp:
            raise ValueError(f"spinup must have length {nsp}, got {sp.size}")
        nh = fe.shape[0]
        X = np.empty((nh, nf + nparam + nsp), dtype=np.float64)
        X[:, :nf] = fe
        X[:, nf : nf + nparam] = pr
        X[:, nf + nparam :] = sp
    else:
        X = np.asarray(X, dtype=np.float64)

    surrogate_output: Dict[str, np.ndarray] = {}
    for var in myvars_list:
        if var not in self.surrogate_forcing:
            raise KeyError(f"No forcing surrogate trained for variable '{var}'")
        xn = self.x_scaler_forcing[var].transform(X)
        pred = self.surrogate_forcing[var].predict(xn)
        y = self.y_scaler_forcing[var].inverse_transform(np.asarray(pred).reshape(-1, 1))
        surrogate_output[var] = y.ravel()
    return surrogate_output
