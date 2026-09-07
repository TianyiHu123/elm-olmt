#!/usr/bin/env python3
"""Bounded compute-node input-contract preflight for ELM Diagnose Iter001."""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OBS_ROOT = Path("/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4")
SITES = ("ABBY", "JERC", "OSBS", "RMNP", "SOAP", "TALL", "TEAK", "WREF", "YELL")
TARGET = "SR"
OPTIMIZED_RE = re.compile(r"^(?P<site>[A-Z]+)_ctrlopt(?P<seed>[0-9]+)_I20TRCNPRDCTCBC\.pkl$")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: F401  # register ELMcase for pickle loading
from model_ELM.load_obs_nc import load_observations_with_time_from_nc  # noqa: E402
from model_ELM.load_obs_nc import collocate_obs_to_forcing_time  # noqa: E402
from model_ELM.surrogate_NN_Forcing import _load_forcing_matrix  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_case(path: Path, role: str) -> dict[str, Any]:
    with path.open("rb") as handle:
        case = pickle.load(handle)
    expected = path.stem
    actual = str(getattr(case, "casename", ""))
    if actual != expected:
        raise ValueError(f"{path.name}: casename {actual!r} does not match filename stem {expected!r}")
    if not hasattr(case, "output") or TARGET not in case.output:
        raise ValueError(f"{path.name}: missing case.output[{TARGET!r}]")
    if "taxis" not in case.output:
        raise ValueError(f"{path.name}: missing case.output['taxis']")
    target = np.asarray(case.output[TARGET], dtype=float)
    taxis = np.asarray(case.output["taxis"]).reshape(-1)
    if target.ndim not in (1, 2):
        raise ValueError(f"{path.name}: SR must be 1-D or 2-D, got {target.shape}")
    if taxis.size < 2:
        raise ValueError(f"{path.name}: taxis has fewer than two entries")
    time_axis = 0 if target.ndim == 1 else (0 if target.shape[0] == taxis.size else 1 if target.shape[1] == taxis.size else -1)
    if time_axis < 0 or target.shape[time_axis] != taxis.size:
        raise ValueError(f"{path.name}: SR shape {target.shape} does not align to taxis {taxis.shape}")
    members = 1 if target.ndim == 1 else int(target.shape[1 - time_axis])
    if role == "control" and members < 2:
        raise ValueError(f"{path.name}: Iter001 control must be an ensemble, found {members} member(s)")
    if role == "optimized" and members != 1:
        raise ValueError(f"{path.name}: each optimized ctrlopt file must hold one seed, found {members} members")
    if not np.isfinite(target).any():
        raise ValueError(f"{path.name}: SR contains no finite values")
    return {
        "filename": path.name,
        "role": role,
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
        "casename": actual,
        "sr_shape": list(target.shape),
        "time_axis": time_axis,
        "member_count": members,
        "taxis_length": int(taxis.size),
        "taxis_first": str(taxis[0]),
        "taxis_last": str(taxis[-1]),
        "metdir": str(getattr(case, "metdir", "")),
    }


def _as_time_members(case: Any, path: Path) -> np.ndarray:
    values = np.asarray(case.output[TARGET], dtype=float)
    ntime = int(np.asarray(case.output["taxis"]).size)
    if values.ndim == 1:
        return values.reshape(ntime, 1)
    if values.shape[0] == ntime:
        return values
    if values.shape[1] == ntime:
        return values.T
    raise ValueError(f"{path.name}: cannot orient SR shape {values.shape} to {ntime} timestamps")


def _load_case(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def validate_common_support(control_path: Path, optimized_paths: list[Path], obs_payload: dict[str, Any]) -> dict[str, Any]:
    control_case = _load_case(control_path)
    control = _as_time_members(control_case, control_path)
    control_taxis = np.asarray(control_case.output["taxis"]).reshape(-1)
    control_metdir = Path(control_case.metdir).resolve(strict=True)
    _, _, forcing_time = _load_forcing_matrix(
        Path(control_case.metdir), ("FSDS",), control.shape[0]
    )
    aligned_obs, aligned_err, overlap = collocate_obs_to_forcing_time(
        forcing_time=forcing_time,
        obs_time=obs_payload["time"],
        obs=obs_payload["obs"],
        obs_err=obs_payload["obs_err"],
        myvars=[TARGET],
    )
    indices = np.asarray(overlap["forcing_overlap_indices"], dtype=int)
    control_overlap = control[indices, :]
    control_mean = np.nanmean(control_overlap, axis=1)
    control_std = np.nanstd(control_overlap, axis=1)
    optimized = []
    for path in optimized_paths:
        optimized_case = _load_case(path)
        optimized_taxis = np.asarray(optimized_case.output["taxis"]).reshape(-1)
        optimized_metdir = Path(optimized_case.metdir).resolve(strict=True)
        if not np.array_equal(optimized_taxis, control_taxis):
            raise ValueError(f"{path.name}: taxis differs from its control")
        if optimized_metdir != control_metdir:
            raise ValueError(f"{path.name}: metdir differs from its control")
        values = _as_time_members(optimized_case, path)
        if values.shape[0] != control.shape[0]:
            raise ValueError(f"{path.name}: SR timestamp count differs from its control")
        optimized.append(values[indices, 0])
    obs = np.asarray(aligned_obs[TARGET], dtype=float)
    err = np.asarray(aligned_err[TARGET], dtype=float)
    valid = (obs > -9000) & np.isfinite(obs) & (err > 0) & np.isfinite(err)
    valid &= np.isfinite(control_mean) & np.isfinite(control_std)
    for values in optimized:
        valid &= np.isfinite(values) & (values > -9000)
    if not np.any(valid):
        raise ValueError(f"{control_path.name}: no common finite SR/observation timestamp support")
    daily: dict[tuple[int, int, int], set[int]] = {}
    for stamp in np.asarray(forcing_time)[indices][valid]:
        daily.setdefault((int(stamp.year), int(stamp.month), int(stamp.day)), set()).add(int(stamp.hour))
    complete_days = sum(hours == set(range(24)) for hours in daily.values())
    if complete_days == 0:
        raise ValueError(f"{control_path.name}: common support contains no complete UTC day")
    return {
        "forcing_time_length": int(np.asarray(forcing_time).size),
        "overlap_count": int(indices.size),
        "common_finite_count": int(np.count_nonzero(valid)),
        "complete_utc_days": int(complete_days),
        "optimized_taxis_equal_control": True,
        "optimized_metdir_equal_control": True,
        "first_common_time": str(np.asarray(forcing_time)[indices][valid][0]),
        "last_common_time": str(np.asarray(forcing_time)[indices][valid][-1]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"schema": "elm-diagnose-iter001-preflight-v1", "sites": {}}
    try:
        optimized = sorted((REPO_ROOT / "pklfiles").glob("*_ctrlopt*_I20TRCNPRDCTCBC.pkl"))
        if len(optimized) != 60:
            raise ValueError(f"expected exactly 60 ctrlopt historical pickles, found {len(optimized)}")
        parsed = []
        for path in optimized:
            match = OPTIMIZED_RE.fullmatch(path.name)
            if not match or match.group("site") not in SITES:
                raise ValueError(f"unexpected optimized filename {path.name}")
            parsed.append((match.group("site"), int(match.group("seed")), path))
        by_site = {site: [path for candidate_site, _, path in parsed if candidate_site == site] for site in SITES}
        if sum(len(paths) for paths in by_site.values()) != 60 or any(not paths for paths in by_site.values()):
            raise ValueError("ctrlopt membership is not exactly the approved nine-site set")
        for site in SITES:
            seeds = [seed for candidate_site, seed, _ in parsed if candidate_site == site]
            if len(seeds) != len(set(seeds)):
                raise ValueError(f"{site}: duplicate ctrlopt seed identity")
        for site in SITES:
            control = REPO_ROOT / "pklfiles" / f"{site}_ppe6_I20TRCNPRDCTCBC.pkl"
            obs = OBS_ROOT / site / f"{site}_cdo_merge.nc"
            if not control.is_file() or not obs.is_file():
                raise FileNotFoundError(f"{site}: required control or observation file is missing")
            obs_payload = load_observations_with_time_from_nc(str(obs), [TARGET])
            if np.asarray(obs_payload["time"]).size < 2:
                raise ValueError(f"{site}: observation time axis is too short")
            result["sites"][site] = {
                "control": inspect_case(control, "control"),
                "optimized": [
                    {**inspect_case(path, "optimized"), "seed": next(seed for candidate_site, seed, candidate in parsed if candidate == path)}
                    for path in by_site[site]
                ],
                "observation": {
                    "path": str(obs), "sha256": sha256(obs), "size_bytes": obs.stat().st_size,
                    "variable": TARGET, "time_length": int(np.asarray(obs_payload["time"]).size),
                    "time_first": str(np.asarray(obs_payload["time"])[0]),
                    "time_last": str(np.asarray(obs_payload["time"])[-1]),
                },
            }
            result["sites"][site]["common_support"] = validate_common_support(
                control, by_site[site], obs_payload
            )
        result["status"] = "pass"
    except Exception as exc:  # Preserve a diagnostic receipt for an authorized failure stop.
        result["status"] = "fail"
        result["error_type"] = type(exc).__name__
        result["error"] = str(exc)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ELM_DIAG_ITER001_PREFLIGHT_{result['status'].upper()} output={args.output}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
