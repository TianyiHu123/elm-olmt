#!/usr/bin/env python
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from .surrogate_NN_Forcing import (
    DEFAULT_SPINUP_VARS,
    _normalize_var_list,
    _prepare_case_training_block,
    _resolve_output_label,
    _train_surrogate_with_prepared_blocks,
)


def _normalize_case_names(case_names: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(case_names, str):
        names = [name.strip() for name in case_names.split(",") if name.strip()]
    else:
        names = [str(name).strip() for name in case_names if str(name).strip()]
    if not names:
        raise ValueError("At least one case name is required.")
    return names


def _load_pickled_case(workdir: Path, case_name: str) -> Any:
    pkl_path = workdir / "pklfiles" / f"{case_name}.pkl"
    if not pkl_path.exists():
        raise FileNotFoundError(f"Case pkl not found: {pkl_path}")
    with open(pkl_path, "rb") as fp:
        return pickle.load(fp)


def train_multicase_surrogate_with_forcing(
    case_names: Union[str, Sequence[str]],
    myvars: Union[str, Sequence[str]],
    workdir: str = ".",
    forcing_vars: Optional[Sequence[str]] = None,
    tair_var: str = "TBOT",
    precip_var: str = "PRECTmms",
    spinup_vars: Optional[Sequence[str]] = None,
    split_mode: str = "by_time_block",
    train_fraction: float = 0.8,
    dtype: str = "float32",
    n_jobs: int = 8,
    cv_folds: int = 3,
    quick_grid: bool = False,
    dry_run: bool = False,
    outputdir: str = ".",
    chunk_size: int = 50000,
    run_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Load multiple pickled ELM cases, merge their training rows, and fit a single
    forcing surrogate model across all cases.
    """
    names = _normalize_case_names(case_names)
    if len(names) < 2:
        raise ValueError(
            "Multi-case surrogate training requires at least two cases. "
            "Use train_surrogate_with_forcing() for single-case runs."
        )

    outvars = _normalize_var_list(myvars)
    if forcing_vars is None:
        forcing_vars_list = [
            s.strip()
            for s in "PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF".split(",")
            if s.strip()
        ]
    else:
        forcing_vars_list = [str(v).strip() for v in forcing_vars if str(v).strip()]

    if spinup_vars is None:
        spinup_vars_list = list(DEFAULT_SPINUP_VARS)
    else:
        spinup_vars_list = [str(v).strip() for v in spinup_vars if str(v).strip()]
        if not spinup_vars_list:
            spinup_vars_list = list(DEFAULT_SPINUP_VARS)

    print("Model output variables:", outvars)
    print("Raw forcing variables:", forcing_vars_list)
    print("Spinup vars:", spinup_vars_list)
    print("Requested multi-case training set:", names)

    workdir_path = Path(workdir).resolve()
    print(f"Loading case pickles from: {workdir_path / 'pklfiles'}")
    cases = [_load_pickled_case(workdir_path, case_name) for case_name in names]
    blocks = [
        _prepare_case_training_block(
            case,
            outvars,
            forcing_vars_list,
            tair_var,
            precip_var,
            spinup_vars_list,
        )
        for case in cases
    ]

    return _train_surrogate_with_prepared_blocks(
        blocks=blocks,
        outvars=outvars,
        tair_var=tair_var,
        precip_var=precip_var,
        split_mode=split_mode,
        train_fraction=train_fraction,
        dtype=dtype,
        n_jobs=n_jobs,
        cv_folds=cv_folds,
        quick_grid=quick_grid,
        dry_run=dry_run,
        outputdir=outputdir,
        output_label=_resolve_output_label([block.case_name for block in blocks], run_name),
        chunk_size=chunk_size,
        attach_case=None,
    )
