#!/usr/bin/env python3
"""
Perlmutter smoke test template for new GSA workflows.

Usage:
1) Copy to your home directory:
   cp examples/gsa_smoke_test.py ~/gsa_smoke_test.py
2) Edit repo path, case_name, and test_vars below.
3) Run:
   python ~/gsa_smoke_test.py
"""

from pathlib import Path
import os
import pickle

import numpy as np


# User edits
repo = Path("/pscratch/sd/t/tianyihu/elm-olmt")
case_name = "JERC_ppe1_I20TRCNPRDCTCBC"
surrogate_artifact = "/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/multisite_test1/surrogate_forcing"
test_vars = ["SR"]  # Keep 1-2 vars for quick smoke test
saltelli_n = 256
metrics = ["mean", "accumulated", "std"]

# Optional: use Slurm-provided CPU count
n_jobs = int(os.environ.get("SLURM_GSA_NJOBS", "2"))

# home_out = Path.home() / "gsa_test_output" / case_name
# home_out.mkdir(parents=True, exist_ok=True)
home_out = Path("/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/GSA/smktest")
home_out.mkdir(parents=True, exist_ok=True)

pkl_path = repo / "pklfiles" / f"{case_name}.pkl"
with open(pkl_path, "rb") as f:
    case = pickle.load(f)

print(f"Loaded case: {case_name}")
print(f"Output dir: {home_out}")

# 1) Given-data PAWN (no spinup)
#case.GSA_given_data_pawn(
#    test_vars,
#    include_spinup=False,
#    metrics=metrics,
#    n_jobs=n_jobs,
#    output_dir=str(home_out / "given_data_pawn_no_spinup"),
#)
#print("PAWN no-spinup done")

# 2) Given-data PAWN (with spinup)
case.GSA_given_data_pawn(
    test_vars,
    include_spinup=True,
    spinup_vars=["TOTSOMC", "TOTSOMN"],
    metrics=metrics,
    n_jobs=n_jobs,
    output_dir=str(home_out / "given_data_pawn_with_spinup"),
)
print("PAWN with-spinup done")

# 3) Forcing-surrogate Sobol (fixed forcing; params+spinup sampled)
case.GSA_forcing_timeseries(
    test_vars,
    n_saltelli=saltelli_n,
    spinup_vars=["TOTSOMC", "TOTSOMN"],
    metrics=metrics,
    n_jobs=n_jobs,
    output_dir=str(home_out / "forcing_sobol"),
    artifact_path=surrogate_artifact,
)

print("Forcing Sobol done")

# 4) Minimal checks
for v in test_vars:
    if hasattr(case, "sens_pawn") and v in case.sens_pawn:
        for metric in metrics:
            if metric not in case.sens_pawn[v]:
                continue
            arr = np.asarray(case.sens_pawn[v][metric])
            print(
                f"PAWN {v} [{metric}] shape={arr.shape}, ndim={arr.ndim}, finite={np.isfinite(arr).mean():.3f}"
            )
    if hasattr(case, "sens_forcing_main") and v in case.sens_forcing_main:
        for metric in metrics:
            if metric not in case.sens_forcing_main[v]:
                continue
            arr = np.asarray(case.sens_forcing_main[v][metric])
            print(
                f"Forcing S1 {v} [{metric}] shape={arr.shape}, ndim={arr.ndim}, finite={np.isfinite(arr).mean():.3f}"
            )
    if hasattr(case, "sens_forcing_tot") and v in case.sens_forcing_tot:
        for metric in metrics:
            if metric not in case.sens_forcing_tot[v]:
                continue
            arr = np.asarray(case.sens_forcing_tot[v][metric])
            print(
                f"Forcing ST {v} [{metric}] shape={arr.shape}, ndim={arr.ndim}, finite={np.isfinite(arr).mean():.3f}"
            )

print("Smoke test complete.")
