#!/usr/bin/env python
"""Run standard GSA from existing outputs and/or forcing surrogate."""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import model_ELM  # noqa: F401 - required for pickle case loading
import numpy as np

from model_ELM.run_GSA import (
    SUPPORTED_AGG_METRICS,
    _normalize_metric_list,
    _normalize_var_list,
)
from model_ELM.surrogate_NN_Forcing import DEFAULT_SPINUP_VARS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standard GSA CLI driver")
    parser.add_argument("--case", required=True, help="Case name (expects pklfiles/<case>.pkl)")
    parser.add_argument(
        "--mode",
        default="surrogate",
        choices=["existing", "surrogate", "both"],
        help="Run PAWN on existing outputs, Sobol on forcing surrogate, or both",
    )
    parser.add_argument("--vars", required=True, help="Comma-separated output variables for GSA")
    parser.add_argument(
        "--metrics",
        default="mean,accumulated,std",
        help="Comma-separated aggregation metrics for sensitivity indices",
    )
    parser.add_argument(
        "--spinup-vars",
        default=",".join(DEFAULT_SPINUP_VARS),
        help="Comma-separated spinup vars (included by default)",
    )
    parser.add_argument(
        "--include-spinup",
        dest="include_spinup",
        action="store_true",
        default=True,
        help="Include spinup state variables in sampled inputs (default: true)",
    )
    parser.add_argument(
        "--no-include-spinup",
        dest="include_spinup",
        action="store_false",
        help="Disable spinup variables in input dimensions",
    )
    parser.add_argument(
        "--artifact",
        default=None,
        help="Forcing surrogate artifact path (required for surrogate or both modes)",
    )
    parser.add_argument(
        "--output-folder",
        default=None,
        help="Output root folder (default: ./UQ_output/<case>/GSA)",
    )
    parser.add_argument("--saltelli-n", type=int, default=1024, help="Saltelli base sample size for surrogate mode")
    parser.add_argument("--pawn-s", type=int, default=10, help="PAWN conditioning intervals for existing mode")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--n-jobs", type=int, default=1, help="Parallel workers for PAWN/Sobol analysis")
    parser.add_argument("--workdir", default=".", help="OLMT root directory containing pklfiles/")
    return parser


def _parse_csv(value: str) -> List[str]:
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _load_case(workdir: Path, case_name: str) -> Any:
    pkl_path = workdir / "pklfiles" / f"{case_name}.pkl"
    if not pkl_path.is_file():
        raise FileNotFoundError(f"Case pkl not found: {pkl_path}")
    with open(pkl_path, "rb") as fp:
        return pickle.load(fp)


def _resolve_output_root(case: Any, output_folder: str | None) -> Path:
    if output_folder:
        root = Path(output_folder).expanduser().resolve()
    else:
        root = Path(".").resolve() / "UQ_output" / str(case.casename) / "GSA"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _run_existing_output_pawn(
    case: Any,
    myvars: List[str],
    metrics: List[str],
    include_spinup: bool,
    spinup_vars: List[str],
    pawn_s: int,
    n_jobs: int,
    outdir: Path,
) -> Dict[str, Any]:
    case.GSA_given_data_pawn(
        myvars,
        include_spinup=bool(include_spinup),
        spinup_vars=spinup_vars,
        metrics=metrics,
        n_jobs=int(n_jobs),
        pawn_s=int(pawn_s),
        output_dir=str(outdir),
    )

    summary: Dict[str, Any] = {
        "problem_names": list(getattr(case, "sens_pawn_names", [])),
        "metrics": list(getattr(case, "sens_pawn_metrics", metrics)),
        "pawn_s": int(pawn_s),
        "vars": {},
    }

    for var in myvars:
        if var not in getattr(case, "sens_pawn", {}):
            continue
        summary["vars"][var] = {}
        for metric in metrics:
            if metric not in case.sens_pawn[var]:
                continue
            median = np.asarray(case.sens_pawn[var][metric], dtype=np.float64)
            summary["vars"][var][metric] = {
                "median_finite_frac": float(np.isfinite(median).mean()),
            }

    return summary


def _run_surrogate_sobol(
    case: Any,
    myvars: List[str],
    metrics: List[str],
    spinup_vars: List[str],
    n_saltelli: int,
    n_jobs: int,
    artifact_path: str,
    outdir: Path,
) -> Dict[str, Any]:
    case.GSA_forcing_timeseries(
        myvars,
        n_saltelli=int(n_saltelli),
        spinup_vars=spinup_vars,
        metrics=metrics,
        n_jobs=int(n_jobs),
        output_dir=str(outdir),
        artifact_path=artifact_path,
    )
    payload: Dict[str, Any] = {"vars": {}, "problem_names": list(getattr(case, "sens_forcing_names", []))}
    for var in myvars:
        if var not in getattr(case, "sens_forcing_main", {}):
            continue
        payload["vars"][var] = {}
        for metric in metrics:
            if metric not in case.sens_forcing_main[var] or metric not in case.sens_forcing_tot[var]:
                continue
            s1 = np.asarray(case.sens_forcing_main[var][metric], dtype=np.float64)
            st = np.asarray(case.sens_forcing_tot[var][metric], dtype=np.float64)
            payload["vars"][var][metric] = {
                "S1_finite_frac": float(np.isfinite(s1).mean()),
                "ST_finite_frac": float(np.isfinite(st).mean()),
            }
    return payload


def main() -> int:
    args = _build_parser().parse_args()
    np.random.seed(int(args.seed))

    workdir = Path(args.workdir).expanduser().resolve()
    try:
        case = _load_case(workdir, args.case)
    except Exception as exc:
        print(f"Error loading case: {exc}", file=sys.stderr)
        return 1

    myvars = _normalize_var_list(args.vars)
    if not myvars:
        print("Error: --vars resolved to an empty list.", file=sys.stderr)
        return 1

    try:
        metrics = _normalize_metric_list(args.metrics)
    except Exception as exc:
        print(f"Error in --metrics: {exc}", file=sys.stderr)
        return 1

    spinup_vars = _parse_csv(args.spinup_vars)
    if args.include_spinup and not spinup_vars:
        spinup_vars = list(DEFAULT_SPINUP_VARS)

    if args.mode in ("surrogate", "both") and not args.artifact:
        print("Error: --artifact is required for mode 'surrogate' or 'both'.", file=sys.stderr)
        return 1

    out_root = _resolve_output_root(case, args.output_folder)
    existing_out = out_root / "existing"
    surrogate_out = out_root / "surrogate"
    existing_out.mkdir(parents=True, exist_ok=True)
    surrogate_out.mkdir(parents=True, exist_ok=True)

    run_meta: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "case": str(args.case),
        "mode": str(args.mode),
        "vars": myvars,
        "metrics": metrics,
        "spinup_vars": spinup_vars,
        "include_spinup": bool(args.include_spinup),
        "artifact": args.artifact,
        "pawn_s": int(args.pawn_s),
        "saltelli_n": int(args.saltelli_n),
        "seed": int(args.seed),
        "n_jobs": int(args.n_jobs),
        "output_root": str(out_root),
        "supported_metrics": list(SUPPORTED_AGG_METRICS),
    }

    if args.mode in ("existing", "both"):
        try:
            run_meta["existing"] = _run_existing_output_pawn(
                case=case,
                myvars=myvars,
                metrics=metrics,
                include_spinup=bool(args.include_spinup),
                spinup_vars=spinup_vars,
                pawn_s=int(args.pawn_s),
                n_jobs=int(args.n_jobs),
                outdir=existing_out,
            )
        except Exception as exc:
            print(f"Error during existing-output PAWN: {exc}", file=sys.stderr)
            return 2

    if args.mode in ("surrogate", "both"):
        try:
            run_meta["surrogate"] = _run_surrogate_sobol(
                case=case,
                myvars=myvars,
                metrics=metrics,
                spinup_vars=spinup_vars,
                n_saltelli=int(args.saltelli_n),
                n_jobs=int(args.n_jobs),
                artifact_path=str(args.artifact),
                outdir=surrogate_out,
            )
        except Exception as exc:
            print(f"Error during surrogate Sobol: {exc}", file=sys.stderr)
            return 3

    meta_path = out_root / "run_metadata.json"
    meta_path.write_text(json.dumps(run_meta, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Standard GSA finished. Metadata: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
