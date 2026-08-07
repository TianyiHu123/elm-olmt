#!/usr/bin/env python
"""Iter004 offline vs coupled dual-variant PPE comparison vs ELM SR."""
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
    load_elm_spinup_member,
    load_elm_sr_member,
    predict_coupled_sr,
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
ARMS = ("offline", "drop32", "drop21_corr080")
ALPHA = 0.5


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir", default=str(REPO_ROOT))
    p.add_argument("--cases", default=",".join(DEFAULT_CASES))
    p.add_argument("--members", required=True, help="e.g. 1-5 or 1-100")
    p.add_argument("--spinup-drop32", required=True)
    p.add_argument("--spinup-drop21", required=True)
    p.add_argument("--forcing-artifact", required=True)
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
) -> str:
    """Member-mean ± std shaded band for ELM + three predictors."""
    outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    styles = {
        "ELM": ("C0", "-"),
        "offline": ("C1", "-"),
        "drop32": ("C2", "-"),
        "drop21_corr080": ("C3", "-"),
    }
    for arm, (color, ls) in styles.items():
        arr = np.asarray(sr_by_arm[arm], dtype=float)
        mean = np.nanmean(arr, axis=0)
        std = np.nanstd(arr, axis=0)
        t = np.arange(mean.size)
        ax.plot(t, mean, color=color, linestyle=ls, label=arm, alpha=ALPHA)
        ax.fill_between(t, mean - std, mean + std, color=color, alpha=ALPHA * 0.35, linewidth=0)
    ax.set_xlabel("Time index")
    ax.set_ylabel("SR (absolute)")
    ax.set_title(f"{site}: SR timeseries mean ± std")
    ax.legend(loc="best", fontsize=8)
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
) -> str:
    outdir.mkdir(parents=True, exist_ok=True)
    mem = np.asarray(members, dtype=int)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    markers = {
        "ELM": "o",
        "offline": "s",
        "drop32": "^",
        "drop21_corr080": "D",
    }
    for arm, marker in markers.items():
        ax.errorbar(
            mem,
            means[arm],
            yerr=stds[arm],
            fmt=marker,
            linestyle="none",
            label=arm,
            alpha=ALPHA,
            capsize=2,
            markersize=4,
        )
    ax.set_xlabel("Ensemble member")
    ax.set_ylabel("SR mean ± temporal std")
    ax.set_title(f"{site}: SR vs ensemble member")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    path = outdir / f"{site}_sr_vs_member.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)


def _plot_sr_vs_totsom(
    outdir: Path,
    site: str,
    varname: str,
    elm_x: np.ndarray,
    elm_mean: np.ndarray,
    elm_std: np.ndarray,
    arm_payload: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> str:
    """Three subplots: offline | drop32 | drop21_corr080, each vs ELM."""
    outdir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
    order = ("offline", "drop32", "drop21_corr080")
    for ax, arm in zip(axes, order):
        x_arm, y_mean, y_std = arm_payload[arm]
        ax.errorbar(
            elm_x,
            elm_mean,
            yerr=elm_std,
            fmt="o",
            linestyle="none",
            label="ELM",
            alpha=ALPHA,
            capsize=2,
            markersize=4,
        )
        ax.errorbar(
            x_arm,
            y_mean,
            yerr=y_std,
            fmt="s",
            linestyle="none",
            label=arm,
            alpha=ALPHA,
            capsize=2,
            markersize=4,
        )
        ax.set_xlabel(varname)
        ax.set_title(arm)
        ax.legend(loc="best", fontsize=7)
    axes[0].set_ylabel("SR mean ± temporal std")
    fig.suptitle(f"{site}: SR vs {varname}")
    fig.tight_layout()
    tag = varname.lower()
    path = outdir / f"{site}_sr_vs_{tag}.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)


def _evaluate_case(
    case_name: str,
    case: Any,
    members: Sequence[int],
    spinup_paths: Dict[str, str],
    forcing_artifact: str,
    outdir: Path,
    save_timeseries: bool,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    site = case_name.split("_")[0]
    rows: List[Dict[str, Any]] = []

    sr_store: Dict[str, List[np.ndarray]] = {
        "ELM": [],
        "offline": [],
        "drop32": [],
        "drop21_corr080": [],
    }
    mean_store: Dict[str, List[float]] = {k: [] for k in sr_store}
    std_store: Dict[str, List[float]] = {k: [] for k in sr_store}
    elm_c: List[float] = []
    elm_n: List[float] = []
    arm_c: Dict[str, List[float]] = {a: [] for a in ARMS}
    arm_n: Dict[str, List[float]] = {a: [] for a in ARMS}

    for member in members:
        elm_spin = load_elm_spinup_member(case, int(member))
        offline = predict_offline_sr(
            case, forcing_artifact=forcing_artifact, member=int(member)
        )
        ntime = int(offline["ntime"])
        elm_sr = load_elm_sr_member(case, int(member), ntime)

        coupled = {}
        for variant, path in spinup_paths.items():
            coupled[variant] = predict_coupled_sr(
                case,
                spinup_artifact=path,
                forcing_artifact=forcing_artifact,
                member=int(member),
            )

        # Store series
        sr_store["ELM"].append(elm_sr)
        sr_store["offline"].append(offline["SR"])
        mean_store["ELM"].append(float(np.mean(elm_sr)))
        std_store["ELM"].append(float(np.std(elm_sr)))
        mean_store["offline"].append(float(np.mean(offline["SR"])))
        std_store["offline"].append(float(np.std(offline["SR"])))
        elm_c.append(float(elm_spin[0]))
        elm_n.append(float(elm_spin[1]))
        arm_c["offline"].append(float(offline["TOTSOMC"]))
        arm_n["offline"].append(float(offline["TOTSOMN"]))

        for variant in ("drop32", "drop21_corr080"):
            pred = coupled[variant]
            sr_store[variant].append(pred["SR"])
            mean_store[variant].append(float(np.mean(pred["SR"])))
            std_store[variant].append(float(np.std(pred["SR"])))
            arm_c[variant].append(float(pred["TOTSOMC"]))
            arm_n[variant].append(float(pred["TOTSOMN"]))

        # Metrics rows
        arm_preds = {
            "offline": offline["SR"],
            "drop32": coupled["drop32"]["SR"],
            "drop21_corr080": coupled["drop21_corr080"]["SR"],
        }
        arm_spin = {
            "offline": (float(offline["TOTSOMC"]), float(offline["TOTSOMN"])),
            "drop32": (float(coupled["drop32"]["TOTSOMC"]), float(coupled["drop32"]["TOTSOMN"])),
            "drop21_corr080": (
                float(coupled["drop21_corr080"]["TOTSOMC"]),
                float(coupled["drop21_corr080"]["TOTSOMN"]),
            ),
        }
        for arm, pred_sr in arm_preds.items():
            metrics = compute_sr_metrics(elm_sr, pred_sr)
            rows.append(
                {
                    "site": site,
                    "case": case_name,
                    "arm": arm,
                    "member": int(member),
                    "pred_TOTSOMC": arm_spin[arm][0],
                    "pred_TOTSOMN": arm_spin[arm][1],
                    "elm_TOTSOMC": float(elm_spin[0]),
                    "elm_TOTSOMN": float(elm_spin[1]),
                    "pred_sr_mean": float(np.mean(pred_sr)),
                    "pred_sr_std": float(np.std(pred_sr)),
                    "elm_sr_mean": float(np.mean(elm_sr)),
                    "elm_sr_std": float(np.std(elm_sr)),
                    "ntime": ntime,
                    **metrics,
                }
            )

    # Arrays
    sr_arr = {k: np.vstack(v) for k, v in sr_store.items()}
    means = {k: np.asarray(v, dtype=float) for k, v in mean_store.items()}
    stds = {k: np.asarray(v, dtype=float) for k, v in std_store.items()}
    elm_c_a = np.asarray(elm_c, dtype=float)
    elm_n_a = np.asarray(elm_n, dtype=float)

    plot_dir = outdir / "plots"
    plots = {
        "timeseries": _plot_timeseries(plot_dir, site, sr_arr),
        "sr_vs_member": _plot_sr_vs_member(plot_dir, site, members, means, stds),
        "sr_vs_totsomc": _plot_sr_vs_totsom(
            plot_dir,
            site,
            "TOTSOMC",
            elm_c_a,
            means["ELM"],
            stds["ELM"],
            {
                arm: (
                    elm_c_a if arm == "offline" else np.asarray(arm_c[arm], dtype=float),
                    means[arm],
                    stds[arm],
                )
                for arm in ARMS
            },
        ),
        "sr_vs_totsomn": _plot_sr_vs_totsom(
            plot_dir,
            site,
            "TOTSOMN",
            elm_n_a,
            means["ELM"],
            stds["ELM"],
            {
                arm: (
                    elm_n_a if arm == "offline" else np.asarray(arm_n[arm], dtype=float),
                    means[arm],
                    stds[arm],
                )
                for arm in ARMS
            },
        ),
    }

    medians = {}
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        medians[arm] = {
            key: float(np.nanmedian([r[key] for r in arm_rows])) for key in METRIC_KEYS
        }

    site_summary: Dict[str, Any] = {
        "site": site,
        "case": case_name,
        "n_members": len(members),
        "arms": list(ARMS),
        "metric_medians": medians,
        "plots": plots,
    }

    if save_timeseries:
        nc_path = outdir / "timeseries" / f"{site}_offline_coupled_sr.nc"
        _write_netcdf(
            nc_path,
            members,
            {
                "SR_elm": sr_arr["ELM"],
                "SR_offline": sr_arr["offline"],
                "SR_drop32": sr_arr["drop32"],
                "SR_drop21_corr080": sr_arr["drop21_corr080"],
            },
            {
                "TOTSOMC_elm": elm_c_a,
                "TOTSOMN_elm": elm_n_a,
                "TOTSOMC_offline": np.asarray(arm_c["offline"], dtype=float),
                "TOTSOMN_offline": np.asarray(arm_n["offline"], dtype=float),
                "TOTSOMC_drop32": np.asarray(arm_c["drop32"], dtype=float),
                "TOTSOMN_drop32": np.asarray(arm_n["drop32"], dtype=float),
                "TOTSOMC_drop21_corr080": np.asarray(arm_c["drop21_corr080"], dtype=float),
                "TOTSOMN_drop21_corr080": np.asarray(arm_n["drop21_corr080"], dtype=float),
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
    if args.site_index is not None:
        idx = int(args.site_index)
        if idx < 1 or idx > len(cases):
            raise ValueError(f"--site-index {idx} outside 1..{len(cases)}")
        cases = [cases[idx - 1]]
    members = _parse_members(args.members)
    spinup_paths = {
        "drop32": str(Path(args.spinup_drop32).resolve()),
        "drop21_corr080": str(Path(args.spinup_drop21).resolve()),
    }
    forcing = str(Path(args.forcing_artifact).resolve())

    all_rows: List[Dict[str, Any]] = []
    summaries = []
    for case_name in cases:
        print(f"EVAL_CASE_START {case_name} members={members[0]}-{members[-1]}")
        case = _load_case(workdir, case_name)
        rows, site_summary = _evaluate_case(
            case_name,
            case,
            members,
            spinup_paths,
            forcing,
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
        "schema": "spinup-forcing-coupling-iter004-eval-v1",
        "stage": args.stage_label,
        "members": members,
        "cases": cases,
        "arms": list(ARMS),
        "save_timeseries": bool(args.save_timeseries),
        "sites": summaries,
        "member_metrics_csv": str(member_csv),
    }
    summary_path = outdir / f"{args.stage_label}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"EVAL_PASS stage={args.stage_label} sites={len(cases)} members={len(members)}")
    print(f"SUMMARY {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
