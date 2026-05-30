from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
import xarray as xr


def _floor_hour(time_da: xr.DataArray) -> xr.DataArray:
    """Floor a time DataArray to the hour, tolerant of xarray/pandas frequency-alias changes.

    Newer xarray/pandas (>= 2.2) use lowercase ``"h"``; older xarray cftime offsets only
    accept uppercase ``"H"``. Try the modern alias first, then fall back.
    """
    try:
        return time_da.dt.floor("h")
    except (ValueError, AttributeError):
        return time_da.dt.floor("H")


def _to_hourly(da: xr.DataArray) -> xr.DataArray:
    if "time" not in da.dims:
        raise ValueError("Observation variable must have a time dimension.")
    if da.sizes["time"] < 2:
        return da

    t = np.asarray(da["time"].values)
    try:
        dt_ns = np.diff(t.astype("datetime64[ns]")).astype("timedelta64[s]").astype(np.int64)
    except Exception:
        dt_ns = np.array([], dtype=np.int64)

    if dt_ns.size == 0:
        return da

    median_seconds = int(np.median(dt_ns))
    if median_seconds <= 0:
        return da
    if median_seconds >= 3600:
        return da

    steps_per_hour = int(round(3600.0 / float(median_seconds)))
    if steps_per_hour <= 1:
        return da
    return da.coarsen(time=steps_per_hour, boundary="trim").mean()


def _obs_err_fallback(obs_values: np.ndarray) -> np.ndarray:
    err = 0.10 * np.abs(obs_values)
    err = np.where(np.isfinite(obs_values), np.maximum(err, 1.0e-6), -9999.0)
    return err


def load_observations_with_time_from_nc(
    obs_path: str,
    myvars: Sequence[str],
    obs_err_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Load observations and uncertainty arrays and preserve hourly time axis.
    """
    path = Path(obs_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Observation NetCDF not found: {path}")

    obs_err_vars = obs_err_vars or {}
    obs: Dict[str, np.ndarray] = {}
    obs_err: Dict[str, np.ndarray] = {}
    obs_time: Optional[np.ndarray] = None

    with xr.open_dataset(path) as ds:
        if "time" in ds.coords:
            try:
                ds = ds.convert_calendar("noleap", dim="time")
            except Exception:
                pass

        for var in myvars:
            print("Load Obs variable:", var, "from ", path)
            
            if var not in ds.variables:
                raise KeyError(f"Observation variable '{var}' not found in {path}")

            da_obs = _to_hourly(ds[var]).squeeze() * 3600 * 24 # temporally convert unit
            obs_raw = np.asarray(da_obs, dtype=np.float64).reshape(-1)
            if obs_time is None and "time" in da_obs.coords:
                obs_time = np.asarray(_floor_hour(da_obs["time"]).values).reshape(-1)

            err_var = obs_err_vars.get(var)
            if err_var and err_var in ds.variables:
                print("Obs error variable exist:", err_var)
                da_err = _to_hourly(ds[err_var]).squeeze() * 3600 * 24 # temporally convert unit
                err_raw = np.asarray(da_err, dtype=np.float64).reshape(-1)
            else:
                print("Obs error variable not exist, use 10% error")
                err_raw = _obs_err_fallback(obs_raw)

            n = min(obs_raw.size, err_raw.size)
            if err_raw.size != obs_raw.size:
                print(
                    f"Warning: obs err rows ({err_raw.size}) != obs rows ({obs_raw.size}) for {var}; "
                    f"truncating both to {n}."
                )

            obs_aligned = np.full(n, -9999.0, dtype=np.float64)
            err_aligned = np.full(n, -9999.0, dtype=np.float64)
            obs_aligned[:n] = obs_raw[:n]
            err_aligned[:n] = err_raw[:n]

            invalid = ~np.isfinite(obs_aligned)
            obs_aligned[invalid] = -9999.0
            err_aligned[invalid] = -9999.0

            invalid_err = ~np.isfinite(err_aligned) | (err_aligned <= 0)
            fallback = _obs_err_fallback(obs_aligned)
            err_aligned[invalid_err & (obs_aligned > -9000)] = fallback[invalid_err & (obs_aligned > -9000)]
            err_aligned[obs_aligned <= -9000] = -9999.0

            obs[var] = obs_aligned
            obs_err[var] = err_aligned

    if obs_time is None:
        raise ValueError(f"Observation file {path} does not expose a usable time axis.")
    ntime = min(len(obs_time), *(len(obs[v]) for v in myvars))
    return {
        "time": np.asarray(obs_time[:ntime]).reshape(-1),
        "obs": {v: np.asarray(obs[v][:ntime], dtype=np.float64) for v in myvars},
        "obs_err": {v: np.asarray(obs_err[v][:ntime], dtype=np.float64) for v in myvars},
    }


def collocate_obs_to_forcing_time(
    forcing_time: Sequence[Any],
    obs_time: Sequence[Any],
    obs: Dict[str, np.ndarray],
    obs_err: Dict[str, np.ndarray],
    myvars: Sequence[str],
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, Any]]:
    """
    Align observation vectors onto forcing timestamps by hourly overlap.
    """
    ftime = np.asarray(forcing_time).reshape(-1)
    otime = np.asarray(obs_time).reshape(-1)
    obs_idx_by_key = {t: i for i, t in enumerate(otime)}
    overlap_idx = np.asarray([i for i, t in enumerate(ftime) if t in obs_idx_by_key], dtype=np.int64)
    obs_match_idx = np.asarray([obs_idx_by_key[ftime[i]] for i in overlap_idx], dtype=np.int64)

    if overlap_idx.size == 0:
        raise ValueError(
            "No overlapping timestamps between forcing and observations. "
            f"forcing range: {str(ftime[0]) if ftime.size else 'NA'} -> {str(ftime[-1]) if ftime.size else 'NA'}, "
            f"obs range: {str(otime[0]) if otime.size else 'NA'} -> {str(otime[-1]) if otime.size else 'NA'}"
        )

    collocated_obs: Dict[str, np.ndarray] = {}
    collocated_err: Dict[str, np.ndarray] = {}
    for v in myvars:
        obs_arr = np.asarray(obs[v], dtype=np.float64).reshape(-1)
        err_arr = np.asarray(obs_err[v], dtype=np.float64).reshape(-1)
        if obs_arr.size != otime.size or err_arr.size != otime.size:
            n = min(obs_arr.size, err_arr.size, otime.size)
            if n <= 0:
                raise ValueError(f"No valid observation rows available for variable '{v}'.")
            obs_arr = obs_arr[:n]
            err_arr = err_arr[:n]
            obs_local_idx = np.clip(obs_match_idx, 0, n - 1)
        else:
            obs_local_idx = obs_match_idx
        collocated_obs[v] = obs_arr[obs_local_idx]
        collocated_err[v] = err_arr[obs_local_idx]

    diagnostics = {
        "n_forcing": int(ftime.size),
        "n_obs": int(otime.size),
        "n_overlap": int(overlap_idx.size),
        "first_overlap_time": str(ftime[overlap_idx[0]]),
        "last_overlap_time": str(ftime[overlap_idx[-1]]),
        "forcing_overlap_indices": overlap_idx,
    }
    return collocated_obs, collocated_err, diagnostics


def load_observations_from_nc(
    obs_path: str,
    myvars: Sequence[str],
    ntarget: int,
    obs_err_vars: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Load observations and uncertainties from a NetCDF file and align to model target length.

    - Observation variable names must match model variable names in ``myvars``.
    - ``obs_err_vars`` maps model variable -> uncertainty variable in the same file.
    - If uncertainty mapping is missing or variable is absent, use 10% absolute observation.
    """
    payload = load_observations_with_time_from_nc(
        obs_path=obs_path,
        myvars=myvars,
        obs_err_vars=obs_err_vars,
    )
    obs_raw = payload["obs"]
    obs_err_raw = payload["obs_err"]

    obs: Dict[str, np.ndarray] = {}
    obs_err: Dict[str, np.ndarray] = {}
    for var in myvars:
        obs_arr = np.asarray(obs_raw[var], dtype=np.float64).reshape(-1)
        err_arr = np.asarray(obs_err_raw[var], dtype=np.float64).reshape(-1)
        n = min(ntarget, obs_arr.size, err_arr.size)
        if obs_arr.size != ntarget:
            print(
                f"Warning: obs rows ({obs_arr.size}) != target rows ({ntarget}) for {var}; "
                f"aligning to {n} valid rows."
            )
        obs_aligned = np.full(ntarget, -9999.0, dtype=np.float64)
        err_aligned = np.full(ntarget, -9999.0, dtype=np.float64)
        obs_aligned[:n] = obs_arr[:n]
        err_aligned[:n] = err_arr[:n]
        obs[var] = obs_aligned
        obs_err[var] = err_aligned
    return obs, obs_err
