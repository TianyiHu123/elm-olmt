#!/usr/bin/env python3
"""Iter007 compute-node preflight: hashes, imports, dry-run collocation, negatives."""
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
OBS_ABBY = Path(
    "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc"
)
OBS_JERC = Path(
    "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_manifest(manifest: Path, *, relative_to: Path | None = None) -> int:
    n = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, path_s = line.split(None, 1)
        path = Path(path_s) if relative_to is None else relative_to / path_s
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"Hash mismatch for {path}: {actual} != {expected}")
        print(f"HASH_OK {path.name} {actual}")
        n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-hashes", required=True)
    parser.add_argument("--case-hashes", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    n_art = _check_manifest(Path(args.artifact_hashes))
    n_case = _check_manifest(Path(args.case_hashes), relative_to=REPO_ROOT)

    sys.path.insert(0, str(REPO_ROOT))
    from model_ELM.mcmc_spinup_modes import (  # noqa: F401
        DEFAULT_COUPLED_VARIANT,
        resolve_coupled_spinup_artifact,
        resolve_spinup_mode,
    )
    from model_ELM.mcmc_diagnostics import write_mcmc_diagnostics  # noqa: F401

    print("IMPORT_OK mcmc_spinup_modes + mcmc_diagnostics")
    assert DEFAULT_COUPLED_VARIANT == "drop21_corr080"
    drop21 = resolve_coupled_spinup_artifact(variant="drop21_corr080")
    print(f"COUPLED_PATH_OK drop21={drop21}")

    # Fail-closed negatives.
    try:
        resolve_coupled_spinup_artifact(
            spinup_artifact=str(REPO_ROOT / "does_not_exist_iter007.pkl")
        )
        raise AssertionError("missing spinup artifact did not fail closed")
    except FileNotFoundError as exc:
        print(f"NEGATIVE_GATE_OK missing_spinup_artifact: {exc}")

    from model_ELM.load_obs_nc import load_observations_with_time_from_nc

    try:
        load_observations_with_time_from_nc(
            obs_path=str(REPO_ROOT / "does_not_exist_obs_iter007.nc"),
            myvars=["SR"],
            obs_err_vars={"SR": "SR_err"},
        )
        raise AssertionError("missing obs did not fail closed")
    except FileNotFoundError as exc:
        print(f"NEGATIVE_GATE_OK missing_obs: {exc}")

    # Dry-run collocation for both sites under coupled mode.
    cmd = [
        sys.executable,
        str(REPO_ROOT / "optimize_surrogate_forcing.py"),
        "--workdir",
        str(REPO_ROOT),
        "--outputdir",
        str(Path(args.output).resolve().parent),
        "--case",
        "ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC",
        "--artifact",
        str(FORCING),
        "--vars",
        "SR",
        "--obs",
        f"ABBY:{OBS_ABBY},JERC:{OBS_JERC}",
        "--obs-err-vars",
        "SR:SR_err",
        "--spinup-mode",
        "coupled",
        "--coupled-spinup-variant",
        "drop21_corr080",
        "--dry-run-collocation",
    ]
    print("DRY_RUN_CMD", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"dry-run collocation failed with code {proc.returncode}")
    print("DRY_RUN_COLLOCATION_OK")

    payload = {
        "schema": "spinup-forcing-coupling-iter007-preflight-v1",
        "passed": True,
        "artifact_hash_count": n_art,
        "case_hash_count": n_case,
        "default_coupled_variant": DEFAULT_COUPLED_VARIANT,
        "drop21_corr080_path": str(drop21),
        "dry_run_collocation": True,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS cases={n_case} artifacts={n_art} manifest={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
