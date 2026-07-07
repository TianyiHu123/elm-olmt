#!/usr/bin/env python
"""Load one or more pickled ELM cases and run standalone spinup-surrogate training."""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

from model_ELM.surrogate_NN_Spinup import train_surrogate_spinup_from_cases


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone spinup surrogate trainer")
    parser.add_argument(
        "--case",
        required=True,
        help="Case name or comma-separated case list (pklfiles/<case>.pkl)",
    )
    parser.add_argument(
        "--spinup-case",
        default=None,
        help=(
            "Optional spinup case name(s) for forcing-cycle years. "
            "Provide one name to reuse for all --case entries, or a comma-separated list "
            "matching --case order."
        ),
    )
    parser.add_argument(
        "--spinup-vars",
        default="TOTSOMC,TOTSOMN",
        help="Comma-separated spinup target variables (default: TOTSOMC,TOTSOMN)",
    )
    parser.add_argument(
        "--surface-vars",
        default="PCT_SAND,PCT_CLAY,ORGANIC",
        help="Comma-separated surface variables for features",
    )
    parser.add_argument(
        "--forcing-vars",
        default="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF",
        help="Comma-separated forcing variables used to build spinup climatology features",
    )
    parser.add_argument(
        "--clim-feature-mode",
        default="compact",
        choices=["full", "compact"],
        help="Climatology feature mode: full (with monthly features) or compact (no monthly features).",
    )
    parser.add_argument(
        "--split-mode",
        default="by_member",
        choices=["by_member", "by_site", "by_case", "random"],
        help="Train/validation split strategy for member-level spinup targets",
    )
    parser.add_argument("--train-fraction", type=float, default=0.8)
    parser.add_argument(
        "--split-random-state",
        type=int,
        default=None,
        help="RNG seed for split_mode=random",
    )
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--cv-folds", type=int, default=3)
    parser.add_argument("--quick-grid", action="store_true", help="Smaller hyperparameter grid")
    parser.add_argument("--dry-run", action="store_true", help="Print data dimensions and exit before training")
    parser.add_argument("--workdir", default=".", help="OLMT root directory (for pklfiles path)")
    parser.add_argument(
        "--outputdir",
        default=".",
        help="Base directory for UQ_output/<case-or-run-name>/surrogate_spinup/",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional output subfolder name under UQ_output/",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Skip plots/artifacts and only write surrogate_spinup_stats_*.json",
    )
    parser.add_argument(
        "--stats-run-id",
        default=None,
        help="Optional suffix for stats JSON filename",
    )
    return parser


def _load_cases(workdir: Path, case_names: list[str]) -> list[object]:
    # Register ELMcase class for pickle.load only when we actually load case files.
    import model_ELM  # noqa: F401

    cases: list[object] = []
    for case_name in case_names:
        pkl_path = workdir / "pklfiles" / f"{case_name}.pkl"
        if not pkl_path.exists():
            raise FileNotFoundError(f"Case pkl not found: {pkl_path}")
        with open(pkl_path, "rb") as fp:
            cases.append(pickle.load(fp))
    return cases


def _resolve_spinup_case_names(case_names: list[str], spinup_case_arg: str | None) -> list[str]:
    if spinup_case_arg is None:
        return list(case_names)
    names = [name.strip() for name in spinup_case_arg.split(",") if name.strip()]
    if not names:
        return list(case_names)
    if len(names) == 1:
        return names * len(case_names)
    if len(names) != len(case_names):
        raise ValueError(
            "--spinup-case must be a single case name or match the number of --case entries. "
            f"Got len(--case)={len(case_names)}, len(--spinup-case)={len(names)}."
        )
    return names


def main() -> int:
    args = _build_parser().parse_args()
    case_names = [name.strip() for name in args.case.split(",") if name.strip()]
    if not case_names:
        print("Error: at least one case name is required", file=sys.stderr)
        return 1

    spinup_vars = [s.strip() for s in args.spinup_vars.split(",") if s.strip()]
    surface_vars = [s.strip() for s in args.surface_vars.split(",") if s.strip()]
    forcing_vars = [s.strip() for s in args.forcing_vars.split(",") if s.strip()]
    if not spinup_vars:
        print("Error: --spinup-vars cannot be empty", file=sys.stderr)
        return 1
    if not surface_vars:
        print("Error: --surface-vars cannot be empty", file=sys.stderr)
        return 1
    if not forcing_vars:
        print("Error: --forcing-vars cannot be empty", file=sys.stderr)
        return 1

    workdir = Path(args.workdir).resolve()
    try:
        cases = _load_cases(workdir, case_names)
        spinup_case_names = _resolve_spinup_case_names(case_names, args.spinup_case)
        spinup_cases = _load_cases(workdir, spinup_case_names)
    except Exception as exc:
        print(f"Error while loading cases: {exc}", file=sys.stderr)
        return 1

    train_surrogate_spinup_from_cases(
        cases,
        spinup_cases=spinup_cases,
        spinup_vars=spinup_vars,
        surface_vars=surface_vars,
        forcing_vars=forcing_vars,
        clim_feature_mode=args.clim_feature_mode,
        split_mode=args.split_mode,
        train_fraction=args.train_fraction,
        split_random_state=args.split_random_state,
        n_jobs=args.n_jobs,
        cv_folds=args.cv_folds,
        quick_grid=args.quick_grid,
        dry_run=args.dry_run,
        outputdir=args.outputdir,
        run_name=args.run_name,
        minimal_output=args.stats_only,
        stats_run_id=args.stats_run_id,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
