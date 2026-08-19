#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import model_ELM  # noqa: F401 - needed for pickle.load to resolve ELMcase
import numpy as np
from model_ELM.load_obs_nc import (
    collocate_obs_to_forcing_time,
    load_observations_with_time_from_nc,
)
from model_ELM.coupling_pipeline import build_coupling_target, run_fixed_production_chain
from model_ELM.mcmc_spinup_modes import (
    DEFAULT_COUPLED_VARIANT,
    resolve_coupled_spinup_artifact,
    resolve_coupled_variant,
    resolve_spinup_mode,
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
        help=(
            "Case name(s) in pklfiles/<case>.pkl used for optimization targets. "
            "Provide a comma-separated list to optimize multiple explicit cases/sites."
        ),
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
        help="Comma-separated var:err_var mapping, e.g. GPP:GPP_SE,SR:SR_SE",
    )
    parser.add_argument(
        "--spinup-mode",
        default=None,
        choices=["mean_spinup", "member_restart", "coupled"],
        help=(
            "Spinup mode for the MCMC forward model. Default when omitted: mean_spinup, "
            "or member_restart when --spinup-member is set (historical behavior)."
        ),
    )
    parser.add_argument(
        "--spinup-member",
        type=int,
        default=None,
        help="Optional restart ensemble member (member_restart mode / legacy flag)",
    )
    parser.add_argument(
        "--coupled-spinup-variant",
        default=DEFAULT_COUPLED_VARIANT,
        choices=["drop32", "drop21_corr080"],
        help="Coupled spinup artifact variant (default drop21_corr080)",
    )
    parser.add_argument(
        "--spinup-artifact",
        default=None,
        help="Optional explicit coupled spinup artifact path (overrides variant default)",
    )
    parser.add_argument(
        "--smoke-likelihood-evals",
        type=int,
        default=0,
        help=(
            "If >0, after collocation run this many likelihood evaluations and exit "
            "without a production MCMC campaign (wiring smoke)."
        ),
    )
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
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Deterministic NumPy/emcee initialization seed for reproducible campaigns.",
    )
    parser.add_argument(
        "--sampler-coordinates",
        choices=["physical", "transformed"],
        default="physical",
        help="Iter009 sampler coordinates; transformed runs preserve the physical target via Jacobian.",
    )
    parser.add_argument(
        "--move-configuration",
        choices=["stretch", "de_mixture"],
        default="stretch",
        help="Iter009 proposal configuration.",
    )
    parser.add_argument(
        "--de-move-scale",
        type=float,
        default=1.0,
        help=(
            "Iter011 multiplier for DEMove's default gamma; valid only with "
            "--move-configuration de_mixture."
        ),
    )
    parser.add_argument(
        "--likelihood-resolution",
        choices=["hourly", "daily"],
        default="hourly",
        help=(
            "Iter011 likelihood target. Daily retains only complete 24-hour paired "
            "SR/error days while prediction products remain hourly."
        ),
    )
    parser.add_argument(
        "--initial-state",
        default=None,
        help="Optional .npz bundle containing a physical `initial_state` array.",
    )
    parser.add_argument(
        "--candidate-pool",
        default=None,
        help=(
            "Frozen candidate_pool.npz for provenance-checked fixed production. "
            "When set, this CLI selects and records walkers through the reusable pipeline."
        ),
    )
    parser.add_argument("--repository-commit", default=None)
    parser.add_argument("--source-manifest", default=None)
    parser.add_argument("--dependency-manifest", default=None)
    parser.add_argument("--expected-physical-parameter-count", type=int, default=None)
    parser.add_argument("--target-schema", default="coupled-target-v1")
    parser.add_argument("--daily-map-schema", default="coupled-daily-map-v1")
    parser.add_argument("--selection-schema", default="coupling-selection-ledger-v1")
    parser.add_argument("--production-schema", default="coupling-production-v1")
    parser.add_argument(
        "--pool-reuse-policy",
        choices=["exact_target", "site_hybrid_pool_reuse_v1"],
        default="exact_target",
        help=(
            "exact_target requires frozen-pool and campaign target identity equality. "
            "site_hybrid_pool_reuse_v1 allows a site hybrid pool from the ledger "
            "resolution to initialize a different likelihood resolution."
        ),
    )
    parser.add_argument(
        "--backend",
        default=None,
        help="Optional emcee HDF backend path for checkpointed continuation to --nsteps.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=0,
        help="Optional checkpoint interval; Iter009 requires 2000 for production chains.",
    )
    parser.add_argument("--workdir", default=".", help="OLMT root directory with pklfiles/")
    parser.add_argument(
        "--outputdir",
        default=".",
        help=(
            "Working/output directory (script changes cwd to this path). "
            "With --flat-output, MCMC products are written here directly "
            "(no UQ_output nesting)."
        ),
    )
    parser.add_argument(
        "--flat-output",
        action="store_true",
        help=(
            "Write MCMC products at --outputdir root "
            "(best_params.txt, clm_params_best.nc, plots/, diagnostics/) "
            "instead of ./UQ_output/<casename>/MCMC_forcing_output/."
        ),
    )
    parser.add_argument(
        "--write-diagnostics",
        action="store_true",
        help="Write suggested MCMC diagnostics under <output>/diagnostics/ (requires --flat-output).",
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


def _complete_day_groups(time_axis, obs, obs_err) -> dict:
    """Build the immutable Iter011 complete-day SR aggregation map."""
    times = np.asarray(time_axis).reshape(-1)
    values = np.asarray(obs["SR"], dtype=float).reshape(-1)
    errors = np.asarray(obs_err["SR"], dtype=float).reshape(-1)
    if not (times.size == values.size == errors.size):
        raise ValueError("daily likelihood requires aligned time, SR, and SR_err arrays")
    by_day: Dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    for index, timestamp in enumerate(times):
        if not all(hasattr(timestamp, field) for field in ("year", "month", "day", "hour")):
            raise ValueError("daily likelihood requires absolute hourly model-calendar timestamps")
        if values[index] <= -9000 or not np.isfinite(errors[index]) or errors[index] <= 0:
            continue
        by_day.setdefault((int(timestamp.year), int(timestamp.month), int(timestamp.day)), []).append(
            (int(timestamp.hour), index)
        )
    groups, included, excluded = [], [], []
    for key in sorted(by_day):
        rows = by_day[key]
        if len(rows) == 24 and sorted(hour for hour, _ in rows) == list(range(24)):
            groups.append([index for _, index in sorted(rows)])
            included.append(f"{key[0]:04d}-{key[1]:02d}-{key[2]:02d}")
        else:
            excluded.append(f"{key[0]:04d}-{key[1]:02d}-{key[2]:02d}")
    if not groups:
        raise ValueError("daily likelihood retained zero complete valid 24-hour SR days")
    payload = {
        "schema": "spinup-forcing-coupling-iter011-daily-index-map-v1",
        "aggregation": "arithmetic_mean_of_same_24_hourly_indices",
        "included_dates": included,
        "excluded_dates": excluded,
        "hourly_count": int(times.size),
        "daily_count": len(groups),
        "groups": groups,
    }
    payload["sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload


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


def _site_key_from_case(case_obj: Any) -> str:
    site = str(getattr(case_obj, "site", "")).strip()
    if site:
        return site
    return str(getattr(case_obj, "casename", "unknown_case"))


def main() -> int:
    args = _build_parser().parse_args()
    workdir = Path(args.workdir).expanduser().resolve()
    outputdir = Path(args.outputdir).expanduser().resolve()
    outputdir.mkdir(parents=True, exist_ok=True)
    os.chdir(outputdir)

    spinup_mode = resolve_spinup_mode(
        spinup_mode=args.spinup_mode, spinup_member=args.spinup_member
    )
    coupled_variant = resolve_coupled_variant(args.coupled_spinup_variant)
    spinup_artifact_path = None
    if spinup_mode == "coupled":
        spinup_artifact_path = resolve_coupled_spinup_artifact(
            variant=coupled_variant, spinup_artifact=args.spinup_artifact
        )
        print(
            f"SPINUP_MODE=coupled variant={coupled_variant} "
            f"spinup_artifact={spinup_artifact_path}"
        )
    else:
        print(
            f"SPINUP_MODE={spinup_mode} spinup_member={args.spinup_member}"
        )

    case_names = [name.strip() for name in args.case.split(",") if name.strip()]
    if not case_names:
        print("Error: at least one case name is required", file=sys.stderr)
        return 1

    myvars = [s.strip() for s in args.vars.split(",") if s.strip()]
    if not myvars:
        print("Error: --vars cannot be empty", file=sys.stderr)
        return 1
    if spinup_mode == "coupled" and myvars != ["SR"]:
        print(
            "Error: coupled spinup mode requires --vars SR (forcing-surrogate-v1 is SR-only)",
            file=sys.stderr,
        )
        return 1
    obs_map = _parse_obs_spec(args.obs)
    obs_err_vars = _parse_obs_err_vars(args.obs_err_vars)

    if args.candidate_pool:
        if spinup_mode != "coupled":
            raise ValueError("--candidate-pool production requires --spinup-mode coupled")
        if myvars != ["SR"]:
            raise ValueError("--candidate-pool production currently requires --vars SR")
        if not args.flat_output:
            raise ValueError("--candidate-pool production requires --flat-output")
        required_provenance = {
            "--repository-commit": args.repository_commit,
            "--source-manifest": args.source_manifest,
            "--dependency-manifest": args.dependency_manifest,
        }
        missing = [name for name, value in required_provenance.items() if not value]
        if missing:
            raise ValueError(
                "candidate-pool production requires provenance arguments: "
                + ", ".join(missing)
            )
        if args.initial_state:
            raise ValueError("--initial-state and --candidate-pool are mutually exclusive")
        if args.backend and Path(args.backend).resolve() != outputdir / "backend.h5":
            raise ValueError(
                "--backend must be omitted or equal <outputdir>/backend.h5 "
                "for candidate-pool production"
            )
        if "*" in obs_map:
            if len(case_names) != 1:
                raise ValueError(
                    "a shared --obs path is ambiguous for multi-site candidate-pool production; "
                    "use SITE:path mappings"
                )
            case_for_site = _load_case(workdir, case_names[0])
            observation_paths = {
                _site_key_from_case(case_for_site): obs_map["*"],
            }
        else:
            observation_paths = obs_map
        target = build_coupling_target(
            repo_root=workdir,
            cases=case_names,
            resolution=args.likelihood_resolution,
            forcing_artifact=args.artifact,
            spinup_artifact=spinup_artifact_path,
            observation_paths=observation_paths,
            fit_error=args.fit_error,
            expected_physical_parameter_count=args.expected_physical_parameter_count,
            target_schema=args.target_schema,
            daily_map_schema=args.daily_map_schema,
        )
        site_label = target["sites"][0] if len(target["sites"]) == 1 else ",".join(target["sites"])
        run_fixed_production_chain(
            target=target,
            site=site_label,
            resolution=args.likelihood_resolution,
            seed=int(args.seed) if args.seed is not None else -1,
            pool_path=args.candidate_pool,
            output=outputdir,
            repository_commit=str(args.repository_commit),
            source_manifest=args.source_manifest,
            dependency_manifest=args.dependency_manifest,
            cases=case_names,
            nwalkers=args.nwalkers,
            nsteps=args.nsteps,
            checkpoint_interval=args.checkpoint_interval,
            n_processes=(
                args.n_processes
                if args.n_processes is not None
                else int(os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count() or 1))
            ),
            sampler_coordinates=args.sampler_coordinates,
            move_configuration=args.move_configuration,
            de_move_scale=args.de_move_scale,
            write_diagnostics=bool(args.write_diagnostics),
            selection_schema=args.selection_schema,
            production_schema=args.production_schema,
            daily_map_schema=args.daily_map_schema,
            pool_reuse_policy=args.pool_reuse_policy,
        )
        print(
            f"FIXED_PRODUCTION_PASS sites={site_label} "
            f"resolution={args.likelihood_resolution} seed={args.seed}"
        )
        return 0

    case_objs: List[Tuple[str, Any]] = []
    for cname in case_names:
        case_objs.append((cname, _load_case(workdir, cname)))
    primary = case_objs[0][1]
    artifact = load_surrogate_forcing_artifacts(primary, args.artifact)
    training_layout = artifact["training_layout"]
    for _, case_obj in case_objs[1:]:
        load_surrogate_forcing_artifacts(case_obj, args.artifact)

    cases_by_site: Dict[str, Tuple[str, Any]] = {}
    for cname, case_obj in case_objs:
        skey = _site_key_from_case(case_obj)
        if skey in cases_by_site:
            raise ValueError(
                f"Duplicate site key '{skey}' from cases "
                f"'{cases_by_site[skey][0]}' and '{cname}'. "
                "Provide cases with unique site labels."
            )
        cases_by_site[skey] = (cname, case_obj)
    sites: List[str] = list(cases_by_site.keys())
    primary.all_sites = sites

    # Offline modes: mean uses no member; member_restart uses --spinup-member.
    offline_spinup_member = (
        args.spinup_member if spinup_mode == "member_restart" else None
    )

    forcing_context = {}
    overlap_report = {}
    for s in sites:
        site_case_name, case_obj = cases_by_site[s]
        print("**************************************************")
        print("Site: ", s)
        print("Case: ", site_case_name)

        finputs = build_forcing_inference_inputs(
            case_obj,
            training_layout=training_layout,
            spinup_member=offline_spinup_member,
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
            "spinup_mode": spinup_mode,
        }
        forcing_context[s] = {
            "case_name": site_case_name,
            "case": case_obj,
            "spinup_mode": spinup_mode,
            "forcing_engineered": forcing_overlap,
            "spinup": finputs["spinup"],
            "forcing_feature_names": list(finputs.get("forcing_feature_names", [])),
            "obs": obs,
            "obs_err": obs_err,
            "forcing_time": forcing_time_overlap,
            "forcing_time_source": finputs.get("forcing_time_source", "unknown"),
            "surrogate_forcing": case_obj.surrogate_forcing,
            "x_scaler_forcing": case_obj.x_scaler_forcing,
            "y_scaler_forcing": case_obj.y_scaler_forcing,
            "training_layout": dict(case_obj.forcing_surrogate_training),
            "overlap_diagnostics": {
                k: v for k, v in overlap.items()  # if k != "forcing_overlap_indices"
            },
            "baseline_output": case_obj.output,
        }
        if args.likelihood_resolution == "daily":
            forcing_context[s]["daily_index_map"] = _complete_day_groups(
                forcing_time_overlap, obs, obs_err
            )
        if spinup_mode == "coupled":
            forcing_context[s]["spinup_artifact"] = str(spinup_artifact_path)
            forcing_context[s]["forcing_artifact"] = str(
                Path(args.artifact).expanduser().resolve()
            )
            forcing_context[s]["coupled_spinup_variant"] = coupled_variant
        print("baseline output variables are:", forcing_context[s]["baseline_output"].keys())
        print("**************************************************")
    if args.dry_run_collocation and int(args.smoke_likelihood_evals or 0) <= 0:
        print("\nDry-run collocation summary:")
        for s in sites:
            info = overlap_report[s]
            print(
                f"  - {s}: forcing={info['forcing_rows']}, obs={info['obs_rows']}, "
                f"overlap={info['overlap_rows']}, source={info['forcing_time_source']}, "
                f"mode={info['spinup_mode']}, "
                f"window={info['first_overlap_time']} -> {info['last_overlap_time']}"
            )
            print(
                f"Overlap idx are "
                f"{forcing_context[s]['overlap_diagnostics']['forcing_overlap_indices'][[0, -1]]}"
            )
            print("baseline output variables are:", forcing_context[s]["baseline_output"].keys())
        print("\nDry-run requested; skipping MCMC sampling.")
        return 0

    if args.write_diagnostics and not args.flat_output:
        print("Error: --write-diagnostics requires --flat-output", file=sys.stderr)
        return 1

    smoke_n = int(args.smoke_likelihood_evals or 0)
    mcmc_output_root = str(outputdir) if args.flat_output else None
    initial_state = None
    if args.initial_state:
        bundle = np.load(args.initial_state, allow_pickle=False)
        if "initial_state" not in bundle:
            raise ValueError("--initial-state bundle must contain an initial_state array")
        initial_state = np.asarray(bundle["initial_state"], dtype=float)
    result = primary.MCMC_forcing(
        myvars=myvars,
        forcing_context=forcing_context,
        workdir=workdir,
        nwalkers=args.nwalkers,
        nsteps=args.nsteps,
        fit_error=args.fit_error,
        n_processes=args.n_processes,
        smoke_likelihood_evals=smoke_n,
        output_root=mcmc_output_root,
        write_diagnostics=bool(args.write_diagnostics),
        seed=args.seed,
        sampler_coordinates=args.sampler_coordinates,
        move_configuration=args.move_configuration,
        de_move_scale=args.de_move_scale,
        likelihood_resolution=args.likelihood_resolution,
        initial_state=initial_state,
        backend_path=args.backend,
        checkpoint_interval=args.checkpoint_interval,
    )
    if smoke_n > 0:
        print(
            f"Smoke likelihood complete for mode={spinup_mode}: "
            f"evals={result['smoke_likelihood_evals']}"
        )
        return 0
    if args.flat_output:
        print(f"Saved optimization outputs under: {outputdir}")
    else:
        print(
            f"Saved optimization outputs under: "
            f"{outputdir / 'UQ_output' / primary.casename / 'MCMC_forcing_output'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
