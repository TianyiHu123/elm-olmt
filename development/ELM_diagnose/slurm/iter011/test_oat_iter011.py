#!/usr/bin/env python3
"""Deterministic Iter011 interface, direct-HR, restart, and artifact fixtures."""

from __future__ import annotations

import argparse
import pickle
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import xarray as xr
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.ELM_diagnose.tools import oat_sensitivity as oat

PARAMETERS = (
    "act25", "br_mr", "cn_s1", "cn_s2", "cn_s3", "cn_s4",
    "decomp_depth_efolding", "frootcn", "grperc", "k_l1", "k_l2", "k_l3",
    "k_s1", "k_s2", "k_s3", "k_s4", "leafcn", "leaf_long", "lflitcn",
    "livewdcn", "q10_mr",
)
LOG_PARAMETERS = frozenset({"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4"})


def interfaces() -> dict[str, object]:
    return oat.parse_interfaces(argparse.Namespace(
        target=["SR", "HR", "GPP", "LITFALL", "DECOMP_C_TOTAL"],
        statistic=["mean"], observation=[], compensation=[],
        hr_pool=[
            "CWDC:K_CWD", "LITR1C:K_LITR1", "LITR2C:K_LITR2", "LITR3C:K_LITR3",
            "SOIL1C:K_SOIL1", "SOIL2C:K_SOIL2", "SOIL3C:K_SOIL3", "SOIL4C:K_SOIL4",
        ],
        hr_n_limiter="FPI", hr_p_limiter="FPI_P", litter_ratio=[],
        restart_root=Path("/synthetic/restart"),
        parameter_restart=[f"{parameter}:case_{parameter}" for parameter in PARAMETERS],
    ), PARAMETERS)


def transient_fixture(root: Path, contract: dict[str, object]) -> oat.CaseSummary:
    hours = np.arange(2, dtype=float)[:, None]
    members = np.arange(100, dtype=float)[None, :]
    base = 1.0 + hours + members / 100.0
    raw = {name: base.copy() for name in oat.required_raw_variables(contract)}
    raw["HR"] = np.full((2, 100), 7.0)
    for component in oat.HR_COMPONENTS:
        raw[component] = np.full((2, 100), 99.0)
    raw["FPI"] = np.full((2, 100), 0.5)
    raw["FPI_P"] = np.full((2, 100), 0.25)
    raw["taxis"] = 2018.0 + np.arange(2, dtype=float) / 8760.0
    case = SimpleNamespace(
        site="ABBY", casename="synthetic_iter011", ensemble_parms=["act25"],
        ensemble_pfts=[-1], ensemble_pmin=[1.0], ensemble_pmax=[2.0], nsamples=100,
        samples=np.linspace(1.0, 2.0, 100).reshape(1, -1),
        postproc_startyear=2018, postproc_endyear=2024,
        postproc_vars=list(oat.required_raw_variables(contract)), output=raw,
    )
    pickle_path = root / "synthetic.pkl"
    with pickle_path.open("wb") as handle:
        pickle.dump(case, handle)
    with xr.Dataset() as control:
        summary, _ = oat.load_case_summary(
            "act25", pickle_path, oat.digest(pickle_path), "linear", control, None, contract, "ABBY"
        )
    if not np.array_equal(summary.member_statistics["HR"]["mean"], np.full(100, 7.0)):
        raise AssertionError("HR endpoint was not taken directly from case.output['HR']")
    if summary.compensation_statistics:
        raise AssertionError("omitted compensation interface produced calculations")
    return summary


def restart_fixture(root: Path, summary: oat.CaseSummary) -> oat.CaseSummary:
    case_name = "case_act25"
    case_dir = root / case_name
    for member in range(1, 101):
        member_dir = case_dir / f"g{member:05d}"
        member_dir.mkdir(parents=True)
        path = member_dir / f"{case_name}.elm.r.0201-01-01-00000.nc"
        with Dataset(path, "w") as dataset:
            dataset.createDimension("lev", 2)
            for target_index, components in enumerate(oat.SPINUP_COMPONENTS.values(), start=1):
                for component in components:
                    variable = dataset.createVariable(component, "f8", ("lev",))
                    variable[:] = float(target_index)
    loaded = oat.load_spinup_state(summary, root, case_name)
    expected = {"DECOMP_C_TOTAL": 16.0, "DECOMP_N_TOTAL": 32.0, "DECOMP_P_TOTAL": 48.0}
    for target, value in expected.items():
        if not np.array_equal(loaded.spinup_metrics[target], np.full(100, value)):
            raise AssertionError(f"restart sum differs for {target}")
    return loaded


def main() -> None:
    original_hours = oat.EXPECTED_HOURS
    oat.EXPECTED_HOURS = 2
    try:
        contract = interfaces()
        fixture = oat.fixture_checks(PARAMETERS)
        if fixture["atlas_layout"] != [5, 5] or fixture["omitted_compensation"] != "no_tables_or_figures":
            raise AssertionError("dynamic-layout or optional-compensation fixture failed")
        if oat.response_score_record(np.zeros(100))["rejection_reason"] != "zero_ensemble_median":
            raise AssertionError("unsupported score fixture failed")
        counts = oat.expected_artifact_counts(contract, len(PARAMETERS))
        if counts != {
            "parameter_metadata.csv": 21, "member_metrics.csv": 2100,
            "sensitivity_scores.csv": 105, "response_curves.csv": 11550,
            "hr_pathway_metrics.csv": 56700, "hr_pathway_curves.csv": 630,
            "spinup_member_metrics.csv": 2100, "spinup_sensitivity_scores.csv": 63,
            "spinup_response_curves.csv": 6930,
        }:
            raise AssertionError(f"Iter011 row cardinalities differ: {counts}")
        with tempfile.TemporaryDirectory(prefix="iter011_fixture.") as temporary:
            root = Path(temporary)
            summary = transient_fixture(root, contract)
            summary = restart_fixture(root / "restart", summary)
            spinup_rows = oat.build_spinup_rows([summary])
            if tuple(map(len, spinup_rows)) != (100, 3, 330):
                raise AssertionError("spinup row fixture differs")
        print("ITER011_FIXTURE_PASS parameters=21 layout=5x5 direct_hr=true restart_totals=true")
    finally:
        oat.EXPECTED_HOURS = original_hours


if __name__ == "__main__":
    main()
