#!/usr/bin/env python
from __future__ import annotations

import os
import pickle
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


def _build_member_time_index(
    nmembers: int,
    ntime: int,
    split_mode: str,
    train_fraction: float,
    site_labels: Optional[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    all_idx = np.arange(nmembers * ntime)
    member_ids = np.repeat(np.arange(nmembers), ntime)
    time_ids = np.tile(np.arange(ntime), nmembers)

    if split_mode == "by_member":
        ntrain_m = max(1, int(nmembers * train_fraction))
        train_mask = member_ids < ntrain_m
    elif split_mode == "by_time_block":
        cutoff = max(1, int(ntime * train_fraction))
        train_mask = time_ids < cutoff
    elif split_mode == "by_site":
        if site_labels is None:
            raise ValueError("split_mode=by_site requires site labels")
        uniq = np.unique(site_labels)
        ntrain_s = max(1, int(len(uniq) * train_fraction))
        train_sites = set(uniq[:ntrain_s])
        train_mask = np.isin(site_labels[member_ids], list(train_sites))
    else:
        raise ValueError(f"Unsupported split mode: {split_mode}")

    return all_idx[train_mask], all_idx[~train_mask]


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
) -> None:
    fig, ax = plt.subplots(2, 1, figsize=(12, 5), sharex=True)
    x = np.arange(train_true_mean.size)
    ls_train, ls_val = "-", "--"

    ax[0].plot(x, train_true_mean, color="blue", linestyle=ls_train, label="ELM mean (train)")
    ax[0].plot(x, train_pred_mean, color="red", linestyle=ls_train, label="Surrogate mean (train)")
    ax[0].plot(x, val_true_mean, color="blue", linestyle=ls_val, label="ELM mean (val)")
    ax[0].plot(x, val_pred_mean, color="red", linestyle=ls_val, label="Surrogate mean (val)")

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
        alpha=0.15,
        linewidth=0,
        label="ELM ±1 std (train)",
    )
    ax[0].fill_between(
        x,
        train_pred_mean - train_pred_std,
        train_pred_mean + train_pred_std,
        where=m_t_sur,
        color="red",
        alpha=0.15,
        linewidth=0,
        label="Surrogate ±1 std (train)",
    )
    ax[0].fill_between(
        x,
        val_true_mean - val_true_std,
        val_true_mean + val_true_std,
        where=m_v_elm,
        color="blue",
        alpha=0.08,
        linewidth=0,
        label="ELM ±1 std (val)",
    )
    ax[0].fill_between(
        x,
        val_pred_mean - val_pred_std,
        val_pred_mean + val_pred_std,
        where=m_v_sur,
        color="red",
        alpha=0.08,
        linewidth=0,
        label="Surrogate ±1 std (val)",
    )
    ax[0].set_ylabel(var)
    ax[0].grid()
    ax[0].legend(loc="best", fontsize=8, ncol=2)
    ax[0].text(
        0.02,
        0.98,
        f"Train $R^2$ = {r2_train:.4f}\nVal $R^2$ = {r2_val:.4f}",
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
    ax[1].plot(x, diff_train, color="black", linestyle=ls_train, label="ELM-Surrogate (train)")
    ax[1].plot(x, diff_val, color="black", linestyle=ls_val, label="ELM-Surrogate (val)")
    m_dt = np.isfinite(diff_train) & np.isfinite(diff_train_std)
    m_dv = np.isfinite(diff_val) & np.isfinite(diff_val_std)
    ax[1].fill_between(
        x,
        diff_train - diff_train_std,
        diff_train + diff_train_std,
        where=m_dt,
        color="gray",
        alpha=0.18,
        linewidth=0,
        label="Diff. ±1 std (train)",
    )
    ax[1].fill_between(
        x,
        diff_val - diff_val_std,
        diff_val + diff_val_std,
        where=m_dv,
        color="gray",
        alpha=0.1,
        linewidth=0,
        label="Diff. ±1 std (val)",
    )
    ax[1].set_ylabel(var)
    ax[1].set_xlabel("Time index")
    ax[1].grid()
    ax[1].legend(loc="best", fontsize=8)
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
    nsamples: int,
    ntime: int,
    nfeatures: int,
    dtype: str,
) -> None:
    rows = nsamples * ntime
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
) -> Optional[Dict[str, Any]]:
    """
    Train MLP surrogates mapping [engineered forcing | parameters | spinup] to hourly outputs.

    Saves plots and ``surrogate_forcing_artifacts.pkl`` under
    ``<outputdir>/UQ_output/<casename>/surrogate_forcing/``. Populates ``self.surrogate_forcing``,
    ``self.x_scaler_forcing``, ``self.y_scaler_forcing``, and ``self.forcing_surrogate_training``.

    Returns the artifact dict (or None if ``dry_run``).
    """
    del chunk_size  # reserved for chunked IO; training uses memmap as in the original script

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

    if not hasattr(self, "samples"):
        raise AttributeError("Case object missing 'samples'")
    if not hasattr(self, "output"):
        raise AttributeError("Case object missing 'output'")

    params = np.asarray(self.samples).transpose().astype(np.float64)
    nsamples = params.shape[0]
    print("Load ensemble parameters:")
    print(f"{nsamples} ensemble members")
    print(f"{params.shape[1]} parameters")

    for var in outvars:
        if var not in self.output:
            raise KeyError(f"Requested output variable not in case.output: {var}")

    print("Load model outputs:")
    y_ref = np.asarray(self.output[outvars[0]]).transpose()
    ntime = y_ref.shape[1]
    print("Number of hours:", ntime)

    metdir = Path(self.metdir)
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
        spinup[ens - 1, :] = _spinup_state(self, ens, spinup_vars_list)
    print("Spinup array size:")
    print(spinup.shape)

    nfeatures = forcing_features.shape[1] + params.shape[1] + spinup.shape[1]
    _data_preflight(nsamples, ntime, nfeatures, dtype)
    print(f"Final X will be {nsamples * ntime}x{nfeatures}")

    if dry_run:
        print("Dry-run only. Exiting before training.")
        return None

    if n_jobs * cv_folds > 128:
        print(
            "Warning: n_jobs * cv_folds is large; verify node memory "
            "and consider quick-grid mode."
        )

    rows = nsamples * ntime
    dtype_np = np.float32 if dtype == "float32" else np.float64
    outdir = Path(outputdir).resolve()
    uq_out = outdir / "UQ_output" / self.casename / "surrogate_forcing"
    uq_out.mkdir(parents=True, exist_ok=True)
    x_memmap_path = uq_out / "X_forcing_memmap.dat"
    X = np.memmap(x_memmap_path, mode="w+", dtype=dtype_np, shape=(rows, nfeatures))

    print("Building feature matrix...")
    col_force_end = forcing_features.shape[1]
    col_param_end = col_force_end + params.shape[1]
    for m in range(nsamples):
        start = m * ntime
        end = (m + 1) * ntime
        X[start:end, :col_force_end] = forcing_features.astype(dtype_np, copy=False)
        X[start:end, col_force_end:col_param_end] = params[m, :].astype(dtype_np, copy=False)
        X[start:end, col_param_end:] = spinup[m, :].astype(dtype_np, copy=False)
    print(f"Feature matrix memory (mapped): ~{_memory_mb(np.asarray(X)):.1f} MB")

    site_labels = _parse_site_labels(self, nsamples)
    train_idx, val_idx = _build_member_time_index(
        nmembers=nsamples,
        ntime=ntime,
        split_mode=split_mode,
        train_fraction=train_fraction,
        site_labels=site_labels,
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

    _ensure_forcing_surrogate_dicts(self)

    for var in outvars:
        print(f"\nTraining variable: {var}")
        yfull = np.asarray(self.output[var]).transpose()[:, :ntime]
        y_rows = yfull.reshape(-1, 1).astype(dtype_np)

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

        train_r2 = float(np.corrcoef(ytrain_true, yhat_train)[0, 1] ** 2)
        val_r2 = float(np.corrcoef(yval_true, yhat_val)[0, 1] ** 2)
        print(f"R2 train={train_r2:.4f}, val={val_r2:.4f}")

        model_store[var] = grid
        x_scaler_store[var] = x_scaler
        y_scaler_store[var] = y_scaler
        stats[var] = {"r2_train": train_r2, "r2_val": val_r2}

        self.surrogate_forcing[var] = grid
        self.x_scaler_forcing[var] = x_scaler
        self.y_scaler_forcing[var] = y_scaler

        train_time = train_idx % ntime
        tr_tm, tr_pm, tr_ts, tr_ps = _group_time_stats(train_time, ytrain_true, yhat_train, ntime)
        val_time = val_idx % ntime
        v_tm, v_pm, v_ts, v_ps = _group_time_stats(val_time, yval_true, yhat_val, ntime)
        _save_plot(tr_tm, tr_pm, tr_ts, tr_ps, v_tm, v_pm, v_ts, v_ps, var, uq_out, train_r2, val_r2)

    self.forcing_surrogate_training = {
        "forcing_feature_names": forcing_feature_names,
        "forcing_vars_used": forcing_used,
        "spinup_vars": spinup_vars_list,
        "n_forcing_cols": int(forcing_features.shape[1]),
        "n_params": int(params.shape[1]),
        "n_spinup": int(spinup.shape[1]),
        "tair_var": tair_var,
        "precip_var": precip_var,
        "ntime": int(ntime),
    }

    artifact: Dict[str, Any] = {
        "case": self.casename,
        "outvars": outvars,
        "forcing_vars_used": forcing_used,
        "forcing_feature_names": forcing_feature_names,
        "spinup_vars": spinup_vars_list,
        "split_mode": split_mode,
        "train_fraction": train_fraction,
        "models": model_store,
        "x_scaler": x_scaler_store,
        "y_scaler": y_scaler_store,
        "stats": stats,
        "training_layout": self.forcing_surrogate_training,
    }
    with open(uq_out / "surrogate_forcing_artifacts.pkl", "wb") as fp:
        pickle.dump(artifact, fp)
    print(f"\nSaved surrogate artifacts to: {uq_out}")
    return artifact


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
