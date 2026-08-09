#!/usr/bin/env python3
"""Iter008 compute-node preflight: identity, collocation, and bounded smoke chain."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
FORCING = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/"
    "spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
)
SPINUP = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
    "spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/"
    "spinup_surrogate_iter012_drop21_corr080.pkl"
)
OBS_ABBY = Path(
    "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/"
    "eval_files/v4/ABBY/ABBY_cdo_merge.nc"
)
OBS_JERC = Path(
    "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/"
    "eval_files/v4/JERC/JERC_cdo_merge.nc"
)


def check_manifest(path: Path, *, relative_to: Path | None = None) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, raw = line.split(None, 1)
        target = Path(raw) if relative_to is None else relative_to / raw
        if not target.is_file():
            raise FileNotFoundError(target)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"hash mismatch {target}: {actual} != {expected}")
        print(f"HASH_OK {target} {actual}")


def run(command: list[str]) -> None:
    print("RUN", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-hashes", required=True)
    parser.add_argument("--case-hashes", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--preflight-run-dir", required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args()
    run_python = args.python
    check_manifest(Path(args.source_manifest), relative_to=REPO_ROOT)
    check_manifest(Path(args.artifact_hashes))
    check_manifest(Path(args.case_hashes), relative_to=REPO_ROOT)
    for path in (FORCING, SPINUP, OBS_ABBY, OBS_JERC):
        if not path.is_file():
            raise FileNotFoundError(path)

    common = [
        run_python,
        str(REPO_ROOT / "optimize_surrogate_forcing.py"),
        "--workdir", str(REPO_ROOT),
        "--case", "ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC",
        "--artifact", str(FORCING),
        "--vars", "SR",
        "--obs", f"ABBY:{OBS_ABBY},JERC:{OBS_JERC}",
        "--obs-err-vars", "SR:SR_err",
        "--spinup-mode", "coupled",
        "--coupled-spinup-variant", "drop21_corr080",
        "--dry-run-collocation",
    ]
    run(common)

    smoke_root = Path(args.preflight_run_dir) / "abby_smoke"
    smoke_root.mkdir(parents=True, exist_ok=True)
    run([
        run_python,
        str(REPO_ROOT / "optimize_surrogate_forcing.py"),
        "--workdir", str(REPO_ROOT),
        "--outputdir", str(smoke_root),
        "--flat-output", "--write-diagnostics",
        "--case", "ABBY_ppe6_I20TRCNPRDCTCBC",
        "--artifact", str(FORCING), "--vars", "SR",
        "--obs", f"{OBS_ABBY}", "--obs-err-vars", "SR:SR_err",
        "--spinup-mode", "coupled", "--coupled-spinup-variant", "drop21_corr080",
        "--nwalkers", "32", "--nsteps", "20", "--n-processes", "1",
        "--seed", "8008", "--fit-error",
    ])
    required = [
        "raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json",
        "selection_ledger.json", "diagnostic_report.md", "best_params.txt",
        "clm_params_best.nc", "diagnostics/diagnostics_index.json",
    ]
    missing = [str(smoke_root / rel) for rel in required if not (smoke_root / rel).is_file()]
    if missing:
        raise FileNotFoundError("smoke missing:\n" + "\n".join(missing))
    payload = {
        "schema": "spinup-forcing-coupling-iter008-preflight-v1",
        "passed": True,
        "smoke": "ABBY 32x20",
        "raw_chain": str(smoke_root / "raw_chain.npz"),
        "collocation": ["ABBY", "JERC"],
    }
    out = Path(args.preflight_run_dir) / "dependency_manifest.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS manifest={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
