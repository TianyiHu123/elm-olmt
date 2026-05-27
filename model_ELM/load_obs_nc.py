from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import xarray as xr


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
    path = Path(obs_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Observation NetCDF not found: {path}")

    obs_err_vars = obs_err_vars or {}
    obs: Dict[str, np.ndarray] = {}
    obs_err: Dict[str, np.ndarray] = {}

    with xr.open_dataset(path) as ds:
        if "time" in ds.coords:
            try:
                ds = ds.convert_calendar("noleap", dim="time")
            except Exception:
                pass

        for var in myvars:
            if var not in ds.variables:
                raise KeyError(f"Observation variable '{var}' not found in {path}")

            da_obs = _to_hourly(ds[var]).squeeze()
            obs_raw = np.asarray(da_obs, dtype=np.float64).reshape(-1)

            err_var = obs_err_vars.get(var)
            if err_var and err_var in ds.variables:
                da_err = _to_hourly(ds[err_var]).squeeze()
                err_raw = np.asarray(da_err, dtype=np.float64).reshape(-1)
            else:
                err_raw = _obs_err_fallback(obs_raw)

            n = min(ntarget, obs_raw.size, err_raw.size)
            if obs_raw.size != ntarget:
                print(
                    f"Warning: obs rows ({obs_raw.size}) != target rows ({ntarget}) for {var}; "
                    f"aligning to {n} valid rows."
                )

            obs_aligned = np.full(ntarget, -9999.0, dtype=np.float64)
            err_aligned = np.full(ntarget, -9999.0, dtype=np.float64)
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

    return obs, obs_err
