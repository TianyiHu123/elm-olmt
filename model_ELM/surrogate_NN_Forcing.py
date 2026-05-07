#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import pickle
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_SPINUP_VARS = ("TOTSOMC", "TOTSOMN")
SECONDS_PER_HOUR = 3600.0


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
    ds = xr.open_mfdataset([str(p) for p in files], combine="by_coords")

    used_vars: List[str] = []
    features: List[np.ndarray] = []
    for var in forcing_vars:
        if var not in ds.variables:
            continue
        arr = np.asarray(ds[var]).squeeze()
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
        anom = forcing_raw[:, i] - _rolling_mean(forcing_raw[:, i], 24 * 30)
        feat_list.append(anom[:, None])
        names.append(f"{var}_anom_30d")

    out = np.column_stack(feat_list)
    return out, names


def _restart_file(case, ens_num: int) -> Path:
    gst = str(100000 + ens_num)[1:]
    rundir = Path(case.runroot) / "UQ" / case.casename / f"g{gst}"
    yst = str(10000 + case.startyear + case.run_n)[1:]
    return rundir / f"{case.casename}.elm.r.{yst}-01-01-00000.nc"


def _spinup_state(case, ens_num: int, spinup_vars: Sequence[str]) -> np.ndarray:
    fpath = _restart_file(case, ens_num)
    if not fpath.exists():
        raise FileNotFoundError(f"Missing restart file for ensemble {ens_num}: {fpath}")

    vals: List[float] = []
    with Dataset(str(fpath), "r") as nc:
        for var in spinup_vars:
            if var not in nc.variables:
                raise KeyError(f"Spinup variable '{var}' not found in {fpath}")
            arr = np.asarray(nc.variables[var][:], dtype=np.float64)
            vals.append(float(np.nansum(arr)))
    return np.asarray(vals, dtype=np.float64)


def _build_member_time_index(
    nmembers: int,
    ntime: int,
    split_mode: str,
    train_fraction: float,
    site_labels: np.ndarray | None,
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


def _save_plot(y_true: np.ndarray, y_pred: np.ndarray, var: str, outdir: Path) -> None:
    fig, ax = plt.subplots(2, 1, figsize=(12, 5), sharex=True)
    ax[0].plot(np.mean(y_true, axis=0), color="blue", label="ELM")
    ax[0].plot(np.mean(y_pred, axis=0), color="red", label="Surrogate")
    ax[0].set_ylabel(var)
    ax[0].grid()
    ax[0].legend()

    diff = np.mean(y_true, axis=0) - np.mean(y_pred, axis=0)
    ax[1].plot(diff, color="black", label="ELM-Surrogate")
    ax[1].set_ylabel(var)
    ax[1].set_xlabel("Time index")
    ax[1].grid()
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(str(outdir / f"{var}_surrogate_forcing.png"))
    plt.close(fig)


def _parse_site_labels(case, nsamples: int) -> np.ndarray:
    # For now default to one-site label unless user stored site labels in case metadata.
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone OLMT hybrid forcing surrogate trainer")
    parser.add_argument("--case", required=True, help="Case name (pklfiles/<case>.pkl)")
    parser.add_argument(
        "--vars",
        required=True,
        help="Comma-separated output variables (must exist in case.output)",
    )
    parser.add_argument(
        "--forcing-vars",
        default="PRECTmms,FSDS,TBOT,QBOT,WIND,PSRF",
        help="Comma-separated forcing variable names in met nc files",
    )
    parser.add_argument("--tair-var", default="TBOT", help="Temperature forcing variable name")
    parser.add_argument("--precip-var", default="PRECTmms", help="Precip forcing variable name")
    parser.add_argument("--spinup-vars", default="TOTSOMC,TOTSOMN", help="Restart variables for spinup state")
    parser.add_argument("--split-mode", default="by_time_block", choices=["by_member", "by_site", "by_time_block"])
    parser.add_argument("--train-fraction", type=float, default=0.8)
    parser.add_argument("--dtype", default="float32", choices=["float32", "float64"])
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--cv-folds", type=int, default=3)
    parser.add_argument("--quick-grid", action="store_true", help="Smaller parameter grid for faster tests")
    parser.add_argument("--chunk-size", type=int, default=50000)
    parser.add_argument("--dry-run", action="store_true", help="Print dimensions and exit before training")
    parser.add_argument("--workdir", default=".", help="OLMT root directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    workdir = Path(args.workdir).resolve()
    pkl_path = workdir / "pklfiles" / f"{args.case}.pkl"
    if not pkl_path.exists():
        raise FileNotFoundError(f"Case pkl not found: {pkl_path}")

    with open(pkl_path, "rb") as fp:
        case = pickle.load(fp)

    outvars = [s.strip() for s in args.vars.split(",") if s.strip()]
    forcing_vars = [s.strip() for s in args.forcing_vars.split(",") if s.strip()]
    spinup_vars = [s.strip() for s in args.spinup_vars.split(",") if s.strip()]
    if not spinup_vars:
        spinup_vars = list(DEFAULT_SPINUP_VARS)

    if not hasattr(case, "samples"):
        raise AttributeError("Case object missing 'samples'")
    if not hasattr(case, "output"):
        raise AttributeError("Case object missing 'output'")

    params = np.asarray(case.samples).transpose().astype(np.float64)
    nsamples = params.shape[0]

    for var in outvars:
        if var not in case.output:
            raise KeyError(f"Requested output variable not in case.output: {var}")

    y_ref = np.asarray(case.output[outvars[0]]).transpose()
    ntime = y_ref.shape[1]
    metdir = Path(case.metdir)
    forcing_raw, forcing_used = _load_forcing_matrix(metdir, forcing_vars, ntime)
    ntime = forcing_raw.shape[0]
    forcing_features, forcing_feature_names = _engineer_forcing_features(
        forcing_raw,
        forcing_used,
        args.tair_var,
        args.precip_var,
    )

    spinup = np.zeros((nsamples, len(spinup_vars)), dtype=np.float64)
    for ens in range(1, nsamples + 1):
        spinup[ens - 1, :] = _spinup_state(case, ens, spinup_vars)

    nfeatures = forcing_features.shape[1] + params.shape[1] + spinup.shape[1]
    _data_preflight(nsamples, ntime, nfeatures, args.dtype)
    if args.dry_run:
        print("Dry-run only. Exiting before training.")
        return 0

    if args.n_jobs * args.cv_folds > 128:
        print(
            "Warning: n_jobs * cv_folds is large; verify Perlmutter node memory "
            "and consider quick-grid mode."
        )

    rows = nsamples * ntime
    dtype = np.float32 if args.dtype == "float32" else np.float64
    uq_out = workdir / "UQ_output" / case.casename / "surrogate_forcing"
    uq_out.mkdir(parents=True, exist_ok=True)
    x_memmap_path = uq_out / "X_forcing_memmap.dat"
    X = np.memmap(x_memmap_path, mode="w+", dtype=dtype, shape=(rows, nfeatures))

    print("Building feature matrix in chunks...")
    col_force_end = forcing_features.shape[1]
    col_param_end = col_force_end + params.shape[1]
    for m in range(nsamples):
        start = m * ntime
        end = (m + 1) * ntime
        X[start:end, :col_force_end] = forcing_features.astype(dtype, copy=False)
        X[start:end, col_force_end:col_param_end] = params[m, :].astype(dtype, copy=False)
        X[start:end, col_param_end:] = spinup[m, :].astype(dtype, copy=False)
    print(f"Feature matrix memory (mapped): ~{_memory_mb(np.asarray(X)):.1f} MB")

    site_labels = _parse_site_labels(case, nsamples)
    train_idx, val_idx = _build_member_time_index(
        nmembers=nsamples,
        ntime=ntime,
        split_mode=args.split_mode,
        train_fraction=args.train_fraction,
        site_labels=site_labels,
    )
    print(f"Train rows: {train_idx.size}, Val rows: {val_idx.size}")

    if args.quick_grid:
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

    for var in outvars:
        print(f"\nTraining variable: {var}")
        yfull = np.asarray(case.output[var]).transpose()[:, :ntime]
        y_rows = yfull.reshape(-1, 1).astype(dtype)

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
        grid = GridSearchCV(clf, param_grid, n_jobs=args.n_jobs, cv=args.cv_folds)
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

        # Plot mean-by-time diagnostics from validation rows grouped by time index.
        val_time = val_idx % ntime
        y_true_by_t = np.zeros((1, ntime), dtype=np.float64)
        y_pred_by_t = np.zeros((1, ntime), dtype=np.float64)
        for t in range(ntime):
            mask = val_time == t
            if np.any(mask):
                y_true_by_t[0, t] = np.mean(yval_true[mask])
                y_pred_by_t[0, t] = np.mean(yhat_val[mask])
        _save_plot(y_true_by_t, y_pred_by_t, var, uq_out)

    artifact = {
        "case": case.casename,
        "outvars": outvars,
        "forcing_vars_used": forcing_used,
        "forcing_feature_names": forcing_feature_names,
        "spinup_vars": spinup_vars,
        "split_mode": args.split_mode,
        "train_fraction": args.train_fraction,
        "models": model_store,
        "x_scaler": x_scaler_store,
        "y_scaler": y_scaler_store,
        "stats": stats,
    }
    with open(uq_out / "surrogate_forcing_artifacts.pkl", "wb") as fp:
        pickle.dump(artifact, fp)
    print(f"\nSaved surrogate artifacts to: {uq_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())