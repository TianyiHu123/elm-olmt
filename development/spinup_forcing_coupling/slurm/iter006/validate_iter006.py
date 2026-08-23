#!/usr/bin/env python3
"""Iter006 ABBY smoke: collocation dry-run + <=10 likelihood evals for all three modes."""
from __future__ import annotations

import argparse
import json
import pickle
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import xarray as xr

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
FORCING_ARTIFACT = (
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/"
    "spinup_forcing_coupling_iter002_release/surrogate_forcing/"
    "forcing_surrogate_iter002_sr.pkl"
)
CASE_NAME = "ABBY_ppe6_I20TRCNPRDCTCBC"
MODES = ("mean_spinup", "member_restart", "coupled")
SMOKE_EVALS = 10


def _load_case(workdir: Path, case_name: str) -> Any:
    path = workdir / "pklfiles" / f"{case_name}.pkl"
    with path.open("rb") as fp:
        return pickle.load(fp)


def _write_smoke_obs(obs_path: Path, forcing_time: np.ndarray, sr: np.ndarray) -> None:
    """Write a tiny collocatable SR obs NetCDF for wiring smoke."""
    n = min(int(forcing_time.size), int(sr.size), 48)
    if n < 2:
        raise ValueError(f"Need >=2 overlap hours for smoke obs, got n={n}")
    # Take a contiguous mid-window slice for stable overlap.
    start = max(0, (int(forcing_time.size) // 2) - (n // 2))
    times = np.asarray(forcing_time).reshape(-1)[start : start + n]
    values = np.asarray(sr, dtype=np.float64).reshape(-1)[start : start + n]
    values = np.where(np.isfinite(values), values, 0.0)
    ds = xr.Dataset(
        {
            "SR": ("time", values),
            "SR_SE": ("time", np.maximum(0.1 * np.abs(values), 1.0e-3)),
        },
        coords={"time": times},
    )
    ds["SR"].attrs["units"] = "gC/m^2/day"
    ds["SR_SE"].attrs["units"] = "gC/m^2/day"
    obs_path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(obs_path)
    print(f"SMOKE_OBS_WRITTEN path={obs_path} n={n}")


def _run(cmd: List[str]) -> None:
    print("RUN", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-run-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    parser.add_argument("--workdir", default=str(REPO_ROOT))
    args = parser.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    from model_ELM.mcmc_spinup_modes import DEFAULT_COUPLED_VARIANT, resolve_coupled_variant
    from model_ELM.surrogate_NN_Forcing import (
        build_forcing_inference_inputs,
        load_surrogate_forcing_artifacts,
    )

    workdir = Path(args.workdir).resolve()
    validate_dir = Path(args.validate_run_dir).resolve()
    summary_root = Path(args.summary_root).resolve()
    summary_root.mkdir(parents=True, exist_ok=True)
    validate_dir.mkdir(parents=True, exist_ok=True)

    assert resolve_coupled_variant(None) == "drop21_corr080"
    assert DEFAULT_COUPLED_VARIANT == "drop21_corr080"

    case = _load_case(workdir, CASE_NAME)
    artifact = load_surrogate_forcing_artifacts(case, FORCING_ARTIFACT)
    finputs = build_forcing_inference_inputs(case, artifact["training_layout"])
    # Prefer ELM SR member-1 as synthetic obs signal when available.
    if "SR" in getattr(case, "output", {}):
        elm_sr = np.asarray(case.output["SR"]).transpose()
        sr_series = elm_sr[0, : int(finputs["ntime"])]
    else:
        sr_series = np.zeros(int(finputs["ntime"]), dtype=np.float64)
    obs_path = validate_dir / "abby_smoke_obs.nc"
    _write_smoke_obs(obs_path, finputs["forcing_time"], sr_series)

    py = sys.executable
    optimize = str(REPO_ROOT / "optimize_surrogate_forcing.py")
    mode_results: Dict[str, Any] = {}

    for mode in MODES:
        outdir = validate_dir / f"smoke_{mode}"
        outdir.mkdir(parents=True, exist_ok=True)
        base = [
            py,
            optimize,
            "--workdir",
            str(workdir),
            "--outputdir",
            str(outdir),
            "--case",
            CASE_NAME,
            "--artifact",
            FORCING_ARTIFACT,
            "--vars",
            "SR",
            "--obs",
            str(obs_path),
            "--obs-err-vars",
            "SR:SR_SE",
            "--spinup-mode",
            mode,
            "--no-fit-error",
            "--n-processes",
            "1",
        ]
        if mode == "member_restart":
            base.extend(["--spinup-member", "1"])
        if mode == "coupled":
            base.extend(["--coupled-spinup-variant", "drop21_corr080"])

        # Collocation dry-run
        _run(base + ["--dry-run-collocation"])
        # Tiny likelihood budget
        _run(base + ["--smoke-likelihood-evals", str(SMOKE_EVALS)])
        mode_results[mode] = {
            "dry_run": True,
            "smoke_likelihood_evals": SMOKE_EVALS,
            "outdir": str(outdir),
        }
        print(f"MODE_PASS {mode}")

    # Coupled also accepts drop32 (identity/path only; one dry-run + 1 eval).
    outdir_drop32 = validate_dir / "smoke_coupled_drop32"
    outdir_drop32.mkdir(parents=True, exist_ok=True)
    drop32_base = [
        py,
        optimize,
        "--workdir",
        str(workdir),
        "--outputdir",
        str(outdir_drop32),
        "--case",
        CASE_NAME,
        "--artifact",
        FORCING_ARTIFACT,
        "--vars",
        "SR",
        "--obs",
        str(obs_path),
        "--obs-err-vars",
        "SR:SR_SE",
        "--spinup-mode",
        "coupled",
        "--coupled-spinup-variant",
        "drop32",
        "--no-fit-error",
        "--n-processes",
        "1",
    ]
    _run(drop32_base + ["--dry-run-collocation"])
    _run(drop32_base + ["--smoke-likelihood-evals", "1"])
    mode_results["coupled_drop32_accept"] = {
        "dry_run": True,
        "smoke_likelihood_evals": 1,
        "outdir": str(outdir_drop32),
    }
    print("MODE_PASS coupled_drop32_accept")

    # Negative gate: missing forcing artifact fails closed.
    bad = [
        py,
        optimize,
        "--workdir",
        str(workdir),
        "--outputdir",
        str(validate_dir / "negative_missing_artifact"),
        "--case",
        CASE_NAME,
        "--artifact",
        str(validate_dir / "missing_forcing_artifact.pkl"),
        "--vars",
        "SR",
        "--obs",
        str(obs_path),
        "--spinup-mode",
        "mean_spinup",
        "--dry-run-collocation",
    ]
    neg = subprocess.run(bad, check=False, capture_output=True, text=True)
    if neg.returncode == 0:
        raise AssertionError("missing forcing artifact did not fail closed")
    print("NEGATIVE_GATE_OK missing_forcing_artifact")

    decision = {
        "schema": "spinup-forcing-coupling-iter006-decision-v1",
        "iteration_id": "iter006",
        "site": "ABBY",
        "case": CASE_NAME,
        "forcing_artifact": FORCING_ARTIFACT,
        "forcing_artifact_sha256": (
            "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
        ),
        "default_coupled_variant": DEFAULT_COUPLED_VARIANT,
        "modes": list(MODES),
        "smoke_likelihood_evals_per_mode": SMOKE_EVALS,
        "mode_results": mode_results,
        "negative_gates": ["missing_forcing_artifact"],
        "passed": True,
    }
    decision_path = summary_root / "iter006_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    identity = {
        "iteration_id": "iter006",
        "site": "ABBY",
        "modes_exercised": list(MODES) + ["coupled_drop32_accept"],
        "smoke_likelihood_evals_per_mode": SMOKE_EVALS,
        "default_coupled_variant": DEFAULT_COUPLED_VARIANT,
        "forcing_artifact_sha256": decision["forcing_artifact_sha256"],
        "obs_fixture": str(obs_path),
        "passed": True,
    }
    identity_path = summary_root / "iter006_smoke_identity.json"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATE_PASS decision={decision_path} identity={identity_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
