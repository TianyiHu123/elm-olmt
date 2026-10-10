#!/usr/bin/env python3
"""Deterministic Iter013 interface, direct-HR, restart, and artifact fixtures."""

from __future__ import annotations

import argparse
import csv
import pickle
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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
    "livewdcn", "q10_mr", "rf_l1s1", "rf_l2s2", "rf_l3s3", "rf_s1s2",
    "rf_s2s3", "rf_s3s4",
)
LOG_PARAMETERS = frozenset({"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4"})


def interfaces() -> dict[str, object]:
    return oat.parse_interfaces(argparse.Namespace(
        target=["SR", "HR", "GPP", "LITFALL", "DECOMP_C_TOTAL"],
        statistic=["mean"], observation=[], compensation=[],
        spinup_ratio=["DECOMP_CN_RATIO", "DECOMP_CP_RATIO"],
        require_complete_spinup_ratios=True,
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
        site="ABBY", casename="synthetic_iter013", ensemble_parms=["act25"],
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
    legacy = oat.load_spinup_state(summary, root, case_name)
    if set(legacy.spinup_metrics) != set(oat.SPINUP_BASE_TARGETS):
        raise AssertionError("restart-backed no-ratio metrics changed from the Iter012 interface")
    if set(legacy.spinup_metadata["support"]) != set(oat.SPINUP_BASE_TARGETS):
        raise AssertionError("restart-backed no-ratio support metadata changed from Iter012")
    legacy_rows = oat.build_spinup_rows([legacy])
    if tuple(map(len, legacy_rows)) != (100, 3, 330):
        raise AssertionError("restart-backed no-ratio row cardinality changed from Iter012")
    if any(
        key.startswith("DECOMP_CN_RATIO") or key.startswith("DECOMP_CP_RATIO")
        for key in legacy_rows[0][0]
    ):
        raise AssertionError("restart-backed no-ratio primary rows contain ratio fields")
    loaded = oat.load_spinup_state(summary, root, case_name, oat.SPINUP_RATIO_TARGETS)
    expected = {
        "DECOMP_C_TOTAL": 16.0,
        "DECOMP_N_TOTAL": 32.0,
        "DECOMP_P_TOTAL": 48.0,
        "DECOMP_CN_RATIO": 0.5,
        "DECOMP_CP_RATIO": 1.0 / 3.0,
    }
    for target, value in expected.items():
        if not np.array_equal(loaded.spinup_metrics[target], np.full(100, value)):
            raise AssertionError(f"restart sum differs for {target}")
    for target in oat.SPINUP_RATIO_TARGETS:
        if loaded.spinup_metadata["support"][target] != {
            "valid_members": 100, "rejected_members": 0
        }:
            raise AssertionError(f"restart ratio support differs for {target}")
    return loaded


def observation_fixtures(root: Path, summary: oat.CaseSummary) -> None:
    parsed = oat.parse_observations([
        "/synthetic".join(("SR:", "/legacy.nc")),
        "GPP:GPP_DT:NEON daytime-partitioning GPP:/synthetic/gpp.nc",
        "GPP:GPP_NT:NEON nighttime-partitioning GPP:/synthetic/gpp.nc",
    ])
    if parsed[0][:3] != ("SR", "SR", "SR") or [item[0] for item in parsed[1:]] != ["GPP", "GPP"]:
        raise AssertionError("legacy/generalized observation parsing fixture failed")
    try:
        oat.parse_observations([
            "GPP:GPP_DT:duplicate:/synthetic/gpp.nc",
            "GPP:GPP_NT:duplicate:/synthetic/gpp.nc",
        ])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate observation identity fixture failed")

    obs_path = root / "gpp.nc"
    time = np.asarray([
        "2018-01-01T00:00", "2018-01-01T01:00", "2018-01-01T02:00", "2018-01-01T03:00"
    ], dtype="datetime64[m]")
    dataset = xr.Dataset(
        {
            "GPP_DT": ("time", np.asarray([0.0, 1.0, 2.0, np.nan])),
            "GPP_NT": ("time", np.asarray([0.0, -1.0, 3.0, np.nan])),
        },
        coords={"time": time},
    )
    dataset["GPP_DT"].attrs["units"] = "gC/m2/s"
    dataset["GPP_NT"].attrs["units"] = "gC/m2/s"
    dataset.to_netcdf(obs_path)
    observation_rows = oat.load_observation_rows([
        ("GPP", "GPP_DT", "NEON daytime-partitioning GPP", str(obs_path)),
        ("GPP", "GPP_NT", "NEON nighttime-partitioning GPP", str(obs_path)),
    ])
    by_source = {row["source_variable"]: row for row in observation_rows}
    if by_source["GPP_DT"]["valid_count"] != 3 or by_source["GPP_DT"]["minimum"] != 0.0:
        raise AssertionError("zero-GPP retention fixture failed")
    if by_source["GPP_NT"]["valid_count"] != 2 or by_source["GPP_NT"]["post_calendar_negative_rejected_count"] != 1:
        raise AssertionError("negative-GPP rejection fixture failed")
    if not np.isclose(by_source["GPP_DT"]["maximum"], 2.0 * 86400.0):
        raise AssertionError("observation unit-conversion fixture failed")

    soil_path = root / "soil.csv"
    with soil_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("siteID", "totalSoilC_gC_m2", "effectiveDepth_m"))
        writer.writerow(("ABBY", "10", "2"))
    scalar = oat.load_spinup_observation_rows([
        ("DECOMP_C_TOTAL", "totalSoilC_gC_m2", "soil C", str(soil_path))
    ], "ABBY")
    if scalar[0]["retained_count"] != 1 or scalar[0]["coverage_percent"] != 100.0:
        raise AssertionError("scalar observation support fixture failed")
    boundary_warnings: list[str] = []
    def inspect_spinup_savefig(figure, *_args, **_kwargs):
        boundary_warnings.extend(text.get_text() for text in figure.texts)
    with patch.object(oat.plt.Figure, "savefig", inspect_spinup_savefig):
        oat.plot_spinup_atlases(
            root, [summary] * 27, scalar, "ABBY", ("DECOMP_C_TOTAL",)
        )
    if not any("accepted boundary mismatch" in text and "context only" in text for text in boundary_warnings):
        raise AssertionError("spinup figure boundary-warning fixture failed")
    with soil_path.open("a", newline="") as handle:
        csv.writer(handle).writerow(("ABBY", "11", "2"))
    try:
        oat.load_spinup_observation_rows([
            ("DECOMP_C_TOTAL", "totalSoilC_gC_m2", "soil C", str(soil_path))
        ], "ABBY")
    except ValueError:
        pass
    else:
        raise AssertionError("scalar observation site-uniqueness fixture failed")

    legends: list[tuple[list[str], list[str]]] = []
    def inspect_savefig(figure, *_args, **_kwargs):
        legend = figure.legends[0]
        handles = getattr(legend, "legend_handles", getattr(legend, "legendHandles", []))
        legends.append((
            [text.get_text() for text in legend.get_texts()],
            [handle.get_color() for handle in handles],
        ))
    with patch.object(oat.plt.Figure, "savefig", inspect_savefig):
        oat.plot_response_atlases(root, [summary] * 27, ("GPP",), observation_rows, "ABBY", ("mean",))
    if legends != [([
        "NEON daytime-partitioning GPP", "NEON nighttime-partitioning GPP"
    ], ["tab:orange", "tab:purple"])]:
        raise AssertionError(f"GPP figure-level legend/color fixture failed: {legends}")


def ratio_gap_fixture(summary: oat.CaseSummary) -> None:
    metrics = {target: values.copy() for target, values in summary.spinup_metrics.items()}
    metrics["DECOMP_CN_RATIO"][0] = np.nan
    metrics["DECOMP_CP_RATIO"][1] = np.nan
    member_rows, score_rows, curve_rows = oat.build_spinup_rows(
        [replace(summary, spinup_metrics=metrics)], oat.SPINUP_TARGETS
    )
    if member_rows[0]["DECOMP_CN_RATIO"] != "" or member_rows[0]["DECOMP_CN_RATIO_rejection_reason"] != "nonfinite_or_nonpositive_denominator":
        raise AssertionError("C:N explicit-gap fixture failed")
    if member_rows[1]["DECOMP_CP_RATIO"] != "" or member_rows[1]["DECOMP_CP_RATIO_rejection_reason"] != "nonfinite_or_nonpositive_denominator":
        raise AssertionError("C:P explicit-gap fixture failed")
    ratio_scores = [row for row in score_rows if row["target"] in oat.SPINUP_RATIO_TARGETS]
    if any(row["supported"] or row["rejection_reason"] != "nonfinite_or_incomplete_ensemble" for row in ratio_scores):
        raise AssertionError("ratio unsupported-score fixture failed")
    rejected = [row for row in curve_rows if row["point_type"] == "bin_median" and row["rejected_count"]]
    if len(rejected) != 2:
        raise AssertionError("ratio rejected-bin fixture failed")


def main() -> None:
    original_hours = oat.EXPECTED_HOURS
    oat.EXPECTED_HOURS = 2
    try:
        contract = interfaces()
        fixture = oat.fixture_checks(PARAMETERS)
        if fixture["atlas_layout"] != [6, 5] or fixture["omitted_compensation"] != "no_tables_or_figures":
            raise AssertionError("dynamic-layout or optional-compensation fixture failed")
        if oat.response_score_record(np.zeros(100))["rejection_reason"] != "zero_ensemble_median":
            raise AssertionError("unsupported score fixture failed")
        counts = oat.expected_artifact_counts(contract, len(PARAMETERS))
        if counts != {
            "parameter_metadata.csv": 27, "member_metrics.csv": 2700,
            "sensitivity_scores.csv": 135, "response_curves.csv": 14850,
            "hr_pathway_metrics.csv": 72900, "hr_pathway_curves.csv": 810,
            "spinup_member_metrics.csv": 2700, "spinup_sensitivity_scores.csv": 135,
            "spinup_response_curves.csv": 14850,
        }:
            raise AssertionError(f"Iter013 row cardinalities differ: {counts}")
        with tempfile.TemporaryDirectory(prefix="iter013_fixture.") as temporary:
            root = Path(temporary)
            summary = transient_fixture(root, contract)
            summary = restart_fixture(root / "restart", summary)
            spinup_rows = oat.build_spinup_rows([summary], contract["spinup_targets"])
            if tuple(map(len, spinup_rows)) != (100, 5, 550):
                raise AssertionError("spinup row fixture differs")
            member_rows, score_rows, curve_rows = spinup_rows
            if not all(row["DECOMP_CN_RATIO_supported"] and row["DECOMP_CP_RATIO_supported"] for row in member_rows):
                raise AssertionError("spinup ratio support fixture differs")
            if {row["target"] for row in score_rows} != set(oat.SPINUP_TARGETS):
                raise AssertionError("spinup ratio score fixture differs")
            if any(row["valid_count"] != 10 for row in curve_rows if row["point_type"] == "bin_median"):
                raise AssertionError("spinup ratio curve support fixture differs")
            observation_fixtures(root, summary)
            ratio_gap_fixture(summary)
        print("ITER013_FIXTURE_PASS parameters=27 layout=6x5 direct_hr=true restart_ratios=true")
    finally:
        oat.EXPECTED_HOURS = original_hours


if __name__ == "__main__":
    main()

