#!/usr/bin/env python
"""Iter005 mean-spinup offline baseline vs Iter004 arms (metrics, plots, NetCDF)."""
from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.coupled_surrogate import (  # noqa: E402
    compute_sr_metrics,
    load_elm_sr_member,
    predict_offline_sr,
)

DEFAULT_CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]
METRIC_KEYS = ["r2", "rmse", "bias", "mae", "pearson_r", "kge"]
# New compute arm only; Iter004 arms are loaded for overlays / annotations.
NEW_ARM = "offline_mean_spinup"
ITER004_ARMS = ("offline", "drop32", "drop21_corr080")
PLOT_ARMS = ("ELM", NEW_ARM, "offline", "drop32", "drop21_corr080")
ALPHA = 0.5


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir", default=str(REPO_ROOT))
    p.add_argument("--cases", default=",".join(DEFAULT_CASES))
    p.add_argument("--members", required=True, help="e.g. 1-5 or 1-100")
    p.add_argument("--forcing-artifact", required=True)
    p.add_argument("--iter004-full-dir", required=True)
    p.add_argument("--iter004-medians-csv", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--save-timeseries", action="store_true")
    p.add_argument(
        "--site-index",
        type=int,
        default=None,
        help="1-based index into --cases for Slurm array leaf",
    )
    p.add_argument("--stage-label", default="eval")
    return p


def _parse_members(spec: str) -> List[int]:
    text = spec.strip()
    if "-" in text and "," not in text:
        lo, hi = text.split("-", 1)
        start, stop = int(lo), int(hi)
        if start < 1 or stop < start:
            raise ValueError(f"Invalid member range: {spec}")
        return list(range(start, stop + 1))
    members = [int(v.strip()) for v in text.split(",") if v.strip()]
    if not members or len(set(members)) != len(members):
        raise ValueError(f"Invalid members list: {spec}")
    return members


def _load_case(workdir: Path, name: str) -> Any:
    path = workdir / "pklfiles" / f"{name}.pkl"
    with path.open("rb") as fp:
        return pickle.load(fp)


def _load_iter004_leaf(
    iter004_full_dir: Path, site_index: int, site: str, members: Sequence[int]
) -> Dict[str, np.ndarray]:
    leaf = iter004_full_dir / "results" / f"site_{site_index}"
    nc_path = leaf / "timeseries" / f"{site}_offline_coupled_sr.nc"
    if not nc_path.is_file():
        raise FileNotFoundError(nc_path)
    import netCDF4

    with netCDF4.Dataset(nc_path, "r") as ds:
        nc_members = np.asarray(ds.variables["member"][:], dtype=int)
        expected = np.asarray(members, dtype=int)
        if nc_members.shape != expected.shape or not np.array_equal(nc_members, expected):
            raise ValueError(
                f"Iter004 member axis mismatch at {nc_path}: "
                f"{nc_members[:5]}... vs {expected[:5]}..."
            )
        series = {
            "ELM": np.asarray(ds.variables["SR_elm"][:], dtype=np.float64),
            "offline": np.asarray(ds.variables["SR_offline"][:], dtype=np.float64),
            "drop32": np.asarray(ds.variables["SR_drop32"][:], dtype=np.float64),
            "drop21_corr080": np.asarray(
                ds.variables["SR_drop21_corr080"][:], dtype=np.float64
            ),
        }
    return series


def _load_iter004_site_medians(path: Path, site: str) -> Dict[str, Dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as fp:
        rows = list(csv.DictReader(fp))
    out: Dict[str, Dict[str, float]] = {}
    for row in rows:
        if row["site"] != site:
            continue
        arm = row["arm"]
        out[arm] = {k: float(row[k]) for k in METRIC_KEYS}
    for arm in ITER004_ARMS:
        if arm not in out:
            raise KeyError(f"Missing Iter004 median for site={site} arm={arm} in {path}")
    return out


def _annotation_text(medians: Dict[str, Dict[str, float]]) -> str:
    lines = []
    order = (NEW_ARM, "offline", "drop32", "drop21_corr080")
    labels = {
        NEW_ARM: "mean_spinup",
        "offline": "offline_mbr",
        "drop32": "drop32",
        "drop21_corr080": "drop21",
    }
    for arm in order:
        if arm not in medians:
            continue
        med = medians[arm]
        lines.append(
            f"{labels[arm]}: r={med['pearson_r']:.3f} KGE={med['kge']:.3f}"
        )
    return "\n".join(lines)


def _write_netcdf(
    path: Path,
    members: Sequence[int],
    series: Dict[str, np.ndarray],
    scalars: Dict[str, np.ndarray],
) -> None:
    import netCDF4

    path.parent.mkdir(parents=True, exist_ok=True)
    n_members = len(members)
    ntime = next(iter(series.values())).shape[1]
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("member", n_members)
        ds.createDimension("time", ntime)
        mvar = ds.createVariable("member", "i4", ("member",))
        mvar[:] = np.asarray(members, dtype=np.int32)
        for name, data in series.items():
            var = ds.createVariable(name, "f4", ("member", "time"), zlib=True, complevel=4)
            var[:] = data.astype(np.float32)
        for name, data in scalars.items():
            var = ds.createVariable(name, "f8", ("member",))
            var[:] = data.astype(np.float64)


def _plot_timeseries(
    outdir: Path,
    site: str,
    sr_by_arm: Dict[str, np.ndarray],
    medians: Dict[str, Dict[str, float]],
) -> str:
    outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    styles = {
        "ELM": ("C0", "-"),
        NEW_ARM: ("C1", "-"),
        "offline": ("C4", "--"),
        "drop32": ("C2", "-"),
        "drop21_corr080": ("C3", "-"),
    }
    for arm in PLOT_ARMS:
        color, ls = styles[arm]
        arr = np.asarray(sr_by_arm[arm], dtype=float)
        mean = np.nanmean(arr, axis=0)
        std = np.nanstd(arr, axis=0)
        t = np.arange(mean.size)
        ax.plot(t, mean, color=color, linestyle=ls, label=arm, alpha=ALPHA)
        ax.fill_between(
            t, mean - std, mean + std, color=color, alpha=ALPHA * 0.35, linewidth=0
        )
    ax.set_xlabel("Time index")
    ax.set_ylabel("SR (absolute)")
    ax.set_title(f"{site}: SR timeseries mean ± std")
    ax.legend(loc="upper left", fontsize=7)
    ax.text(
        0.99,
        0.02,
        _annotation_text(medians),
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7,
        family="monospace",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.75, "linewidth": 0.5},
    )
    fig.tight_layout()
    path = outdir / f"{site}_timeseries.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)


def _plot_sr_vs_member(
    outdir: Path,
    site: str,
    members: Sequence[int],
    means: Dict[str, np.ndarray],
    stds: Dict[str, np.ndarray],
    medians: Dict[str, Dict[str, float]],
) -> str:
    outdir.mkdir(parents=True, exist_ok=True)
    mem = np.asarray(members, dtype=int)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    markers = {
        "ELM": "o",
        NEW_ARM: "s",
        "offline": "P",
        "drop32": "^",
        "drop21_corr080": "D",
    }
    for arm in PLOT_ARMS:
        ax.errorbar(
            mem,
            means[arm],
            yerr=stds[arm],
            fmt=markers[arm],
            linestyle="none",
            label=arm,
            alpha=ALPHA,
            capsize=2,
            markersize=4,
        )
    ax.set_xlabel("Ensemble member")
    ax.set_ylabel("SR mean ± temporal std")
    ax.set_title(f"{site}: SR vs ensemble member")
    ax.legend(loc="upper left", fontsize=7)
    ax.text(
        0.99,
        0.02,
        _annotation_text(medians),
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7,
        family="monospace",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.75, "linewidth": 0.5},
    )
    fig.tight_layout()
    path = outdir / f"{site}_sr_vs_member.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)


def _evaluate_case(
    case_name: str,
    case: Any,
    members: Sequence[int],
    forcing_artifact: str,
    iter004_full_dir: Path,
    iter004_medians_csv: Path,
    site_index: int,
    outdir: Path,
    save_timeseries: bool,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    site = case_name.split("_")[0]
    samples = np.asarray(case.samples, dtype=np.float64).transpose()
    rows: List[Dict[str, Any]] = []

    mean_sr_list: List[np.ndarray] = []
    mean_c: List[float] = []
    mean_n: List[float] = []
    elm_sr_list: List[np.ndarray] = []

    for member in members:
        params = samples[int(member) - 1, :]
        pred = predict_offline_sr(
            case, forcing_artifact=forcing_artifact, parameters=params
        )
        if pred["spinup_source"] != "elm_restart_mean":
            raise ValueError(
                f"Expected spinup_source=elm_restart_mean, got {pred['spinup_source']!r}"
            )
        ntime = int(pred["ntime"])
        elm_sr = load_elm_sr_member(case, int(member), ntime)
        metrics = compute_sr_metrics(elm_sr, pred["SR"])
        rows.append(
            {
                "site": site,
                "case": case_name,
                "arm": NEW_ARM,
                "member": int(member),
                "pred_TOTSOMC": float(pred["TOTSOMC"]),
                "pred_TOTSOMN": float(pred["TOTSOMN"]),
                "pred_sr_mean": float(np.mean(pred["SR"])),
                "pred_sr_std": float(np.std(pred["SR"])),
                "elm_sr_mean": float(np.mean(elm_sr)),
                "elm_sr_std": float(np.std(elm_sr)),
                "ntime": ntime,
                "spinup_source": pred["spinup_source"],
                **metrics,
            }
        )
        mean_sr_list.append(np.asarray(pred["SR"], dtype=np.float64))
        mean_c.append(float(pred["TOTSOMC"]))
        mean_n.append(float(pred["TOTSOMN"]))
        elm_sr_list.append(elm_sr)

    mean_sr = np.vstack(mean_sr_list)
    elm_sr_arr = np.vstack(elm_sr_list)
    iter004 = _load_iter004_leaf(iter004_full_dir, site_index, site, members)
    if iter004["ELM"].shape != elm_sr_arr.shape:
        raise ValueError(
            f"ELM shape mismatch vs Iter004: {elm_sr_arr.shape} vs {iter004['ELM'].shape}"
        )
    # Prefer live ELM load for the new arm; Iter004 ELM should match within float noise.
    if not np.allclose(elm_sr_arr, iter004["ELM"], rtol=1e-4, atol=1e-5, equal_nan=True):
        max_abs = float(np.nanmax(np.abs(elm_sr_arr - iter004["ELM"])))
        raise ValueError(f"Live ELM SR disagrees with Iter004 NetCDF (max abs {max_abs})")

    sr_store = {
        "ELM": elm_sr_arr,
        NEW_ARM: mean_sr,
        "offline": iter004["offline"],
        "drop32": iter004["drop32"],
        "drop21_corr080": iter004["drop21_corr080"],
    }
    means = {k: np.nanmean(v, axis=1) for k, v in sr_store.items()}
    stds = {k: np.nanstd(v, axis=1) for k, v in sr_store.items()}

    new_medians = {
        key: float(np.nanmedian([r[key] for r in rows])) for key in METRIC_KEYS
    }
    iter004_medians = _load_iter004_site_medians(iter004_medians_csv, site)
    plot_medians = {NEW_ARM: new_medians, **iter004_medians}

    plot_dir = outdir / "plots"
    plots = {
        "timeseries": _plot_timeseries(plot_dir, site, sr_store, plot_medians),
        "sr_vs_member": _plot_sr_vs_member(
            plot_dir, site, members, means, stds, plot_medians
        ),
    }

    site_summary: Dict[str, Any] = {
        "site": site,
        "case": case_name,
        "site_index": site_index,
        "n_members": len(members),
        "new_arm": NEW_ARM,
        "iter004_arms": list(ITER004_ARMS),
        "metric_medians": {NEW_ARM: new_medians, **iter004_medians},
        "plots": plots,
    }

    if save_timeseries:
        nc_path = outdir / "timeseries" / f"{site}_mean_spinup_offline_sr.nc"
        _write_netcdf(
            nc_path,
            members,
            {
                "SR_elm": elm_sr_arr,
                "SR_offline_mean_spinup": mean_sr,
                "SR_offline_iter004": iter004["offline"],
                "SR_drop32": iter004["drop32"],
                "SR_drop21_corr080": iter004["drop21_corr080"],
            },
            {
                "TOTSOMC_mean_spinup": np.asarray(mean_c, dtype=float),
                "TOTSOMN_mean_spinup": np.asarray(mean_n, dtype=float),
            },
        )
        site_summary["timeseries"] = str(nc_path)

    return rows, site_summary


def main() -> int:
    args = _parser().parse_args()
    workdir = Path(args.workdir).resolve()
    outdir = Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    site_index = args.site_index
    if site_index is not None:
        idx = int(site_index)
        if idx < 1 or idx > len(cases):
            raise ValueError(f"--site-index {idx} outside 1..{len(cases)}")
        cases = [cases[idx - 1]]
    else:
        idx = 1
    members = _parse_members(args.members)
    forcing = str(Path(args.forcing_artifact).resolve())
    iter004_full = Path(args.iter004_full_dir).resolve()
    iter004_medians = Path(args.iter004_medians_csv).resolve()

    all_rows: List[Dict[str, Any]] = []
    summaries = []
    for offset, case_name in enumerate(cases):
        leaf_index = idx if args.site_index is not None else offset + 1
        print(f"EVAL_CASE_START {case_name} members={members[0]}-{members[-1]}")
        case = _load_case(workdir, case_name)
        rows, site_summary = _evaluate_case(
            case_name,
            case,
            members,
            forcing,
            iter004_full,
            iter004_medians,
            leaf_index,
            outdir,
            bool(args.save_timeseries),
        )
        all_rows.extend(rows)
        summaries.append(site_summary)
        print(f"EVAL_CASE_DONE {case_name}")

    member_csv = outdir / f"{args.stage_label}_member_metrics.csv"
    with member_csv.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    summary = {
        "schema": "spinup-forcing-coupling-iter005-eval-v1",
        "stage": args.stage_label,
        "members": members,
        "cases": cases,
        "new_arm": NEW_ARM,
        "iter004_arms": list(ITER004_ARMS),
        "save_timeseries": bool(args.save_timeseries),
        "sites": summaries,
        "member_metrics_csv": str(member_csv),
        "iter004_full_dir": str(iter004_full),
        "iter004_medians_csv": str(iter004_medians),
    }
    summary_path = outdir / f"{args.stage_label}_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"EVAL_PASS stage={args.stage_label} sites={len(cases)} members={len(members)}")
    print(f"SUMMARY {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
