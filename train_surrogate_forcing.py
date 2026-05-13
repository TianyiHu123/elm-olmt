#!/usr/bin/env python
"""Load one or more pickled ELM cases and run forcing-surrogate training."""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import model_ELM  # noqa: F401 — registers ELMcase for pickle.load
from model_ELM.surrogate_forcing_multicase import train_multicase_surrogate_with_forcing


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OLMT hybrid forcing surrogate trainer (CLI driver)")
    parser.add_argument(
        "--case",
        required=True,
        help="Case name or comma-separated case list (pklfiles/<case>.pkl)",
    )
    parser.add_argument(
        "--vars",
        required=True,
        help="Comma-separated output variables (must exist in case.output)",
    )
    parser.add_argument(
        "--forcing-vars",
        default="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF",
        help="Comma-separated forcing variable names in met nc files",
    )
    parser.add_argument("--tair-var", default="TBOT", help="Temperature forcing variable name")
    parser.add_argument("--precip-var", default="PRECTmms", help="Precip forcing variable name")
    parser.add_argument(
        "--spinup-vars",
        default="TOTSOMC,TOTSOMN",
        help="Restart variables for spinup state",
    )
    parser.add_argument(
        "--split-mode",
        default="by_time_block",
        choices=["by_member", "by_site", "by_time_block", "random_time_window"],
    )
    parser.add_argument("--train-fraction", type=float, default=0.8)
    parser.add_argument(
        "--split-random-state",
        type=int,
        default=None,
        help="RNG seed for split_mode=random_time_window (recommended for array jobs)",
    )
    parser.add_argument("--dtype", default="float32", choices=["float32", "float64"])
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--cv-folds", type=int, default=3)
    parser.add_argument("--quick-grid", action="store_true", help="Smaller parameter grid for faster tests")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=50000,
        help="Reserved for future chunked IO (passed through to training)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print dimensions and exit before training")
    parser.add_argument("--workdir", default=".", help="OLMT root directory (for pklfiles path)")
    parser.add_argument(
        "--outputdir",
        default=".",
        help="Base directory for UQ_output/<case-or-run-name>/surrogate_forcing/",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional output subfolder name under UQ_output/ (recommended for multi-case runs)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Skip plots and surrogate_forcing_artifacts.pkl; write surrogate_forcing_stats_*.json only",
    )
    parser.add_argument(
        "--stats-run-id",
        default=None,
        help="Optional basename fragment for stats JSON; default uses SLURM/job env + split-random-state",
    )
    parser.add_argument(
        "--reuse-x-memmap",
        type=str,
        default=None,
        metavar="PATH",
        help="Directory containing X_forcing_memmap.dat + layout .npz, or path to the .dat file (skip forcing/spinup IO)",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    workdir = Path(args.workdir).resolve()
    case_names = [name.strip() for name in args.case.split(",") if name.strip()]
    if not case_names:
        print("Error: at least one case name is required", file=sys.stderr)
        return 1

    forcing_vars = [s.strip() for s in args.forcing_vars.split(",") if s.strip()]
    spinup_vars = [s.strip() for s in args.spinup_vars.split(",") if s.strip()]

    if len(case_names) == 1:
        pkl_path = workdir / "pklfiles" / f"{case_names[0]}.pkl"
        if not pkl_path.exists():
            print(f"Error: Case pkl not found: {pkl_path}", file=sys.stderr)
            return 1

        with open(pkl_path, "rb") as fp:
            case = pickle.load(fp)

        case.train_surrogate_with_forcing(
            args.vars,
            forcing_vars=forcing_vars,
            tair_var=args.tair_var,
            precip_var=args.precip_var,
            spinup_vars=spinup_vars,
            split_mode=args.split_mode,
            train_fraction=args.train_fraction,
            dtype=args.dtype,
            n_jobs=args.n_jobs,
            cv_folds=args.cv_folds,
            quick_grid=args.quick_grid,
            dry_run=args.dry_run,
            outputdir=args.outputdir,
            chunk_size=args.chunk_size,
            run_name=args.run_name,
            split_random_state=args.split_random_state,
            minimal_output=args.stats_only,
            stats_run_id=args.stats_run_id,
            reuse_x_memmap_path=args.reuse_x_memmap,
        )
    else:
        train_multicase_surrogate_with_forcing(
            case_names,
            args.vars,
            workdir=str(workdir),
            forcing_vars=forcing_vars,
            tair_var=args.tair_var,
            precip_var=args.precip_var,
            spinup_vars=spinup_vars,
            split_mode=args.split_mode,
            train_fraction=args.train_fraction,
            dtype=args.dtype,
            n_jobs=args.n_jobs,
            cv_folds=args.cv_folds,
            quick_grid=args.quick_grid,
            dry_run=args.dry_run,
            outputdir=args.outputdir,
            chunk_size=args.chunk_size,
            run_name=args.run_name,
            split_random_state=args.split_random_state,
            minimal_output=args.stats_only,
            stats_run_id=args.stats_run_id,
            reuse_x_memmap_path=args.reuse_x_memmap,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
