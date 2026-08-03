#!/usr/bin/env python3
"""
Smoke test for the standard GSA CLI.

Usage:
1) Copy and edit user settings below.
2) Run:
   python examples/gsa_standard_smoke_test.py
"""

from pathlib import Path
import json
import os
import subprocess
import sys

import numpy as np


# User settings
repo = Path("/pscratch/sd/t/tianyihu/elm-olmt")
case_name = "JERC_ppe1_I20TRCNPRDCTCBC"
surrogate_artifact = (
    "/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/multisite_test1/surrogate_forcing"
)
test_vars = ["SR"]  # Keep 1-2 vars for quick smoke test
metrics = ["mean", "accumulated", "std"]
saltelli_n = 256

# Optional: use Slurm-provided CPU count
n_jobs = int(os.environ.get("SLURM_GSA_NJOBS", "2"))
forcing_executor = os.environ.get("SLURM_GSA_FORCING_EXECUTOR", "thread")
sobol_executor = os.environ.get("SLURM_GSA_SOBOL_EXECUTOR", "thread")
pawn_executor = os.environ.get("SLURM_GSA_PAWN_EXECUTOR", "thread")
pawn_var_executor = os.environ.get("SLURM_GSA_PAWN_VAR_EXECUTOR", "serial")
forcing_chunk_size = int(os.environ.get("SLURM_GSA_CHUNK", "128"))

home_out = Path("/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/GSA/standard_smktest")
home_out.mkdir(parents=True, exist_ok=True)

cmd = [
    sys.executable,
    str(repo / "run_standard_gsa.py"),
    "--workdir",
    str(repo),
    "--case",
    case_name,
    "--vars",
    ",".join(test_vars),
    "--metrics",
    ",".join(metrics),
    "--mode",
    "both",
    "--artifact",
    surrogate_artifact,
    "--saltelli-n",
    str(saltelli_n),
    "--n-jobs",
    str(n_jobs),
    "--forcing-executor",
    forcing_executor,
    "--sobol-executor",
    sobol_executor,
    "--pawn-executor",
    pawn_executor,
    "--pawn-var-executor",
    pawn_var_executor,
    "--forcing-chunk-size",
    str(forcing_chunk_size),
    "--output-folder",
    str(home_out),
]

print("Running command:")
print(" ".join(cmd))
subprocess.run(cmd, check=True)
print("CLI run complete")

meta_path = home_out / "run_metadata.json"
if not meta_path.exists():
    raise FileNotFoundError(f"Missing metadata output: {meta_path}")

meta = json.loads(meta_path.read_text(encoding="utf-8"))
print(f"Loaded metadata from: {meta_path}")
print(f"Modes captured: {', '.join([k for k in ('existing', 'surrogate') if k in meta])}")

for var in test_vars:
    existing_npz = home_out / "existing" / f"pawn_{var}.npz"
    surrogate_npz = home_out / "surrogate" / f"forcing_sobol_{var}.npz"
    if not existing_npz.exists():
        raise FileNotFoundError(f"Missing existing-output PAWN file: {existing_npz}")
    if not surrogate_npz.exists():
        raise FileNotFoundError(f"Missing surrogate Sobol file: {surrogate_npz}")

    existing_data = np.load(existing_npz, allow_pickle=True)
    surrogate_data = np.load(surrogate_npz, allow_pickle=True)
    print(f"Existing NPZ keys for {var}: {sorted(existing_data.files)}")
    print(f"Surrogate NPZ keys for {var}: {sorted(surrogate_data.files)}")
    for metric in metrics:
        pawn_key = f"median_{metric}"
        s1_key = f"S1_{metric}"
        st_key = f"ST_{metric}"
        if pawn_key in existing_data:
            pawn_idx = np.asarray(existing_data[pawn_key], dtype=float)
            print(
                f"Existing PAWN {var} [{metric}] shape={pawn_idx.shape} "
                f"finite={np.isfinite(pawn_idx).mean():.3f}"
            )
        if s1_key in surrogate_data and st_key in surrogate_data:
            s1 = np.asarray(surrogate_data[s1_key], dtype=float)
            st = np.asarray(surrogate_data[st_key], dtype=float)
            print(
                f"Surrogate {var} [{metric}] S1 shape={s1.shape} finite={np.isfinite(s1).mean():.3f}; "
                f"ST shape={st.shape} finite={np.isfinite(st).mean():.3f}"
            )

print("Standard GSA smoke test complete.")
