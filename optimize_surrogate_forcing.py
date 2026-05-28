#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import pickle
import sys
from pathlib import Path
from typing import Dict, List

import model_ELM  # noqa: F401 - needed for pickle.load to resolve ELMcase
import numpy as np
from model_ELM.load_obs_nc import (
    collocate_obs_to_forcing_time,
    load_observations_with_time_from_nc,
)
from model_ELM.surrogate_NN_Forcing import (
    build_forcing_inference_inputs,
    load_surrogate_forcing_artifacts,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optimize forcing surrogate parameters with MCMC")
    parser.add_argument(
        "--case",
        required=True,
        help="Primary case name (or comma-separated case list for validation only) in pklfiles/<case>.pkl",
    )
    parser.add_argument(
        "--artifact",
        required=True,
        help="Path to surrogate_forcing_artifacts.pkl or its containing directory",
    )
    parser.add_argument("--vars", required=True, help="Comma-separated output variables")
    parser.add_argument(
        "--obs",
        required=True,
        help="Obs NetCDF path for all sites, or comma-separated key:path pairs (key=site or case)",
    )
    parser.add_argument(
        "--obs-err-vars",
        default="",
        help="Comma-separated var:err_var mapping, e.g. GPP:GPP_SE,NEE:NEE_SE",
    )
    parser.add_argument("--spinup-member", type=int, default=None, help="Optional restart ensemble member")
    parser.add_argument("--nwalkers", type=int, default=32)
    parser.add_argument("--nsteps", type=int, default=100)
    parser.add_argument("--fit-error", dest="fit_error", action="store_true", default=True)
    parser.add_argument("--no-fit-error", dest="fit_error", action="store_false")
    parser.add_argument(
        "--n-processes",
        type=int,
        default=None,
        help="Number of worker processes for emcee (defaults to SLURM_CPUS_PER_TASK or cpu_count).",
    )
    parser.add_argument("--workdir", default=".", help="OLMT root directory with pklfiles/")
    parser.add_argument(
        "--outputdir",
        default=".",
        help="Base directory where UQ_output will be written (script changes cwd to this path).",
    )
    parser.add_argument(
        "--dry-run-collocation",
        action="store_true",
        help="Load forcing/spinup/obs for each site, run time-overlap collocation, print diagnostics, and exit without MCMC.",
    )
    return parser


def _parse_obs_err_vars(raw: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise ValueError(f"Invalid --obs-err-vars item '{item}', expected var:err_var")
        k, v = item.split(":", 1)
        mapping[k.strip()] = v.strip()
    return mapping


def _parse_obs_spec(raw: str):
    spec = [s.strip() for s in raw.split(",") if s.strip()]
    if len(spec) == 1 and ":" not in spec[0]:
        return {"*": spec[0]}
    mapping = {}
    for item in spec:
        if ":" not in item:
            raise ValueError(f"Invalid --obs item '{item}', expected key:path")
        k, v = item.split(":", 1)
        mapping[k.strip()] = v.strip()
    return mapping


def _resolve_obs_path(obs_map: Dict[str, str], site: str, case_name: str) -> str:
    if "*" in obs_map:
        return obs_map["*"]
    if case_name in obs_map:
        return obs_map[case_name]
    if site in obs_map:
        return obs_map[site]
    raise KeyError(f"No obs path provided for site '{site}' or case '{case_name}'")


def _load_case(workdir: Path, case_name: str):
    pkl_path = workdir / "pklfiles" / f"{case_name}.pkl"
    if not pkl_path.is_file():
        raise FileNotFoundError(f"Case pkl not found: {pkl_path}")
    with open(pkl_path, "rb") as fp:
        return pickle.load(fp)


def _resolve_site_case_name(primary, site: str, case_names: List[str]) -> str:
    primary_case = str(getattr(primary, "casename", case_names[0]))
    primary_site = str(getattr(primary, "site", site))
    if site == primary_site:
        return primary_case

    explicit_guess = primary_case.replace(primary_site, site)
    if explicit_guess in case_names:
        return explicit_guess

    candidates = [name for name in case_names if site in name]
    if len(candidates) == 1:
        return candidates[0]

    if len(case_names) > 1:
        raise ValueError(
            f"Unable to resolve case name for site '{site}'. "
            f"Provide an explicit --case list including this site. Candidates: {candidates}"
        )
    return explicit_guess


def main() -> int:
    args = _build_parser().parse_args()
    workdir = Path(args.workdir).expanduser().resolve()
    outputdir = Path(args.outputdir).expanduser().resolve()
    outputdir.mkdir(parents=True, exist_ok=True)
    os.chdir(outputdir)

    case_names = [name.strip() for name in args.case.split(",") if name.strip()]
    if not case_names:
        print("Error: at least one case name is required", file=sys.stderr)
        return 1

    myvars = [s.strip() for s in args.vars.split(",") if s.strip()]
    if not myvars:
        print("Error: --vars cannot be empty", file=sys.stderr)
        return 1
    obs_map = _parse_obs_spec(args.obs)
    obs_err_vars = _parse_obs_err_vars(args.obs_err_vars)

    primary = _load_case(workdir, case_names[0])
    artifact = load_surrogate_forcing_artifacts(primary, args.artifact)
    training_layout = artifact["training_layout"]
    artifact_case_names = set(str(c) for c in artifact.get("case_names", []))
    if training_layout.get("multi_case") and artifact_case_names:
        missing = sorted([c for c in case_names if c not in artifact_case_names])
        if missing:
            raise ValueError(f"Cases missing from artifact case_names: {missing}")

    sites: List[str] = list(getattr(primary, "all_sites", []))
    if not sites:
        sites = [str(getattr(primary, "site", case_names[0]))]
        primary.all_sites = sites

    forcing_context = {}
    overlap_report = {}
    for s in sites:
        site_case_name = _resolve_site_case_name(primary, s, case_names)
        case_obj = primary if s == sites[0] else _load_case(workdir, site_case_name)
        if s != sites[0]:
            load_surrogate_forcing_artifacts(case_obj, args.artifact)

        finputs = build_forcing_inference_inputs(
            case_obj,
            training_layout=training_layout,
            spinup_member=args.spinup_member,
        )
        obs_path = _resolve_obs_path(obs_map, s, site_case_name)
        obs_payload = load_observations_with_time_from_nc(
            obs_path=obs_path,
            myvars=myvars,
            obs_err_vars=obs_err_vars,
        )
        obs, obs_err, overlap = collocate_obs_to_forcing_time(
            forcing_time=finputs["forcing_time"],
            obs_time=obs_payload["time"],
            obs=obs_payload["obs"],
            obs_err=obs_payload["obs_err"],
            myvars=myvars,
        )
        overlap_idx = overlap["forcing_overlap_indices"]
        forcing_overlap = np.asarray(finputs["forcing_engineered"], dtype=float)[overlap_idx, :]
        forcing_time_overlap = np.asarray(finputs["forcing_time"]).reshape(-1)[overlap_idx]
        print(
            f"Site '{s}': forcing rows={overlap['n_forcing']}, obs rows={overlap['n_obs']}, "
            f"overlap rows={overlap['n_overlap']}, "
            f"window={overlap['first_overlap_time']} -> {overlap['last_overlap_time']}"
        )
        overlap_report[s] = {
            "forcing_rows": int(overlap["n_forcing"]),
            "obs_rows": int(overlap["n_obs"]),
            "overlap_rows": int(overlap["n_overlap"]),
            "first_overlap_time": overlap["first_overlap_time"],
            "last_overlap_time": overlap["last_overlap_time"],
            "forcing_time_source": finputs.get("forcing_time_source", "unknown"),
        }
        forcing_context[s] = {
            "forcing_engineered": forcing_overlap,
            "spinup": finputs["spinup"],
            "obs": obs,
            "obs_err": obs_err,
            "forcing_time": forcing_time_overlap,
            "forcing_time_source": finputs.get("forcing_time_source", "unknown"),
            "overlap_diagnostics": {
                k: v for k, v in overlap.items() if k != "forcing_overlap_indices"
            },
        }

    if args.dry_run_collocation:
        print("\nDry-run collocation summary:")
        for s in sites:
            info = overlap_report[s]
            print(
                f"  - {s}: forcing={info['forcing_rows']}, obs={info['obs_rows']}, "
                f"overlap={info['overlap_rows']}, source={info['forcing_time_source']}, "
                f"window={info['first_overlap_time']} -> {info['last_overlap_time']}"
            )
        print("\nDry-run requested; skipping MCMC sampling.")
        return 0

    primary.MCMC_forcing(
        myvars=myvars,
        forcing_context=forcing_context,
        nwalkers=args.nwalkers,
        nsteps=args.nsteps,
        fit_error=args.fit_error,
        n_processes=args.n_processes,
    )
    print(f"Saved optimization outputs under: {outputdir / 'UQ_output' / primary.casename / 'MCMC_forcing_output'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
