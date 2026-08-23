#!/usr/bin/env python
"""PPE batch evaluation client for coupled spinup→forcing vs ELM SR."""
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


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir", default=str(REPO_ROOT))
    p.add_argument("--cases", default=",".join(DEFAULT_CASES))
    p.add_argument("--members", required=True, help="e.g. 1-5 or 1,2,3 or 1-100")
    p.add_argument("--spinup-drop32", required=True)
    p.add_argument("--spinup-drop21", required=True)
    p.add_argument("--forcing-artifact", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--save-timeseries", action="store_true")
    p.add_argument(
        "--site-index",
        type=int,
        default=None,
        help="1-based index into --cases for Slurm array leaf (selects one case)",
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
    sr_coupled: np.ndarray,
    sr_elm: np.ndarray,
    totsomc_pred: np.ndarray,
    totsomn_pred: np.ndarray,
    totsomc_elm: np.ndarray,
    totsomn_elm: np.ndarray,
) -> None:
    import netCDF4

    path.parent.mkdir(parents=True, exist_ok=True)
    n_members, ntime = sr_coupled.shape
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("member", n_members)
        ds.createDimension("time", ntime)
        mvar = ds.createVariable("member", "i4", ("member",))
        mvar[:] = np.asarray(members, dtype=np.int32)
        for name, data in (
            ("SR_coupled", sr_coupled),
            ("SR_elm", sr_elm),
        ):
            var = ds.createVariable(name, "f4", ("member", "time"), zlib=True, complevel=4)
            var[:] = data.astype(np.float32)
        for name, data in (
            ("TOTSOMC_pred", totsomc_pred),
            ("TOTSOMN_pred", totsomn_pred),
            ("TOTSOMC_elm", totsomc_elm),
            ("TOTSOMN_elm", totsomn_elm),
        ):
            var = ds.createVariable(name, "f8", ("member",))
            var[:] = data.astype(np.float64)


def _plot_feedback(
    outdir: Path,
    site: str,
    variant: str,
    members: Sequence[int],
    rows: List[Dict[str, Any]],
) -> Dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    mem = np.asarray(members, dtype=int)
    elm_mean = np.asarray([r["elm_sr_mean"] for r in rows], dtype=float)
    elm_std = np.asarray([r["elm_sr_std"] for r in rows], dtype=float)
    cpl_mean = np.asarray([r["coupled_sr_mean"] for r in rows], dtype=float)
    cpl_std = np.asarray([r["coupled_sr_std"] for r in rows], dtype=float)
    elm_c = np.asarray([r["elm_TOTSOMC"] for r in rows], dtype=float)
    elm_n = np.asarray([r["elm_TOTSOMN"] for r in rows], dtype=float)
    pred_c = np.asarray([r["pred_TOTSOMC"] for r in rows], dtype=float)
    pred_n = np.asarray([r["pred_TOTSOMN"] for r in rows], dtype=float)

    paths = {}
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(mem, elm_mean, yerr=elm_std, fmt="o-", label="ELM", capsize=2)
    ax.errorbar(mem, cpl_mean, yerr=cpl_std, fmt="s-", label="Coupled", capsize=2)
    ax.set_xlabel("Ensemble member")
    ax.set_ylabel("SR mean ± temporal std")
    ax.set_title(f"{site} {variant}: SR vs member")
    ax.legend()
    fig.tight_layout()
    p1 = outdir / f"{site}_{variant}_sr_vs_member.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    paths["sr_vs_member"] = str(p1)

    for xlab, xe, xp, tag in (
        ("TOTSOMC", elm_c, pred_c, "totsomc"),
        ("TOTSOMN", elm_n, pred_n, "totsomn"),
    ):
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.errorbar(xe, elm_mean, yerr=elm_std, fmt="o", label="ELM", capsize=2)
        ax.errorbar(xp, cpl_mean, yerr=cpl_std, fmt="s", label="Coupled", capsize=2)
        ax.set_xlabel(xlab)
        ax.set_ylabel("SR mean ± temporal std")
        ax.set_title(f"{site} {variant}: SR vs {xlab}")
        ax.legend()
        fig.tight_layout()
        p = outdir / f"{site}_{variant}_sr_vs_{tag}.png"
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths[f"sr_vs_{tag}"] = str(p)
    return paths


def _evaluate_case(
    case_name: str,
    case: Any,
    members: Sequence[int],
    variants: Dict[str, str],
    forcing_artifact: str,
    outdir: Path,
    save_timeseries: bool,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    site = case_name.split("_")[0]
    all_rows: List[Dict[str, Any]] = []
    site_summary: Dict[str, Any] = {"site": site, "case": case_name, "variants": {}}

    for variant, spinup_path in variants.items():
        rows = []
        sr_c_list = []
        sr_e_list = []
        pred_c = []
        pred_n = []
        elm_c = []
        elm_n = []
        for member in members:
            pred = predict_coupled_sr(
                case,
                spinup_artifact=spinup_path,
                forcing_artifact=forcing_artifact,
                member=int(member),
            )
            elm_sr = load_elm_sr_member(case, int(member), int(pred["ntime"]))
            elm_spin = load_elm_spinup_member(case, int(member))
            metrics = compute_sr_metrics(elm_sr, pred["SR"])
            row = {
                "site": site,
                "case": case_name,
                "variant": variant,
                "member": int(member),
                "pred_TOTSOMC": pred["TOTSOMC"],
                "pred_TOTSOMN": pred["TOTSOMN"],
                "elm_TOTSOMC": float(elm_spin[0]),
                "elm_TOTSOMN": float(elm_spin[1]),
                "coupled_sr_mean": float(np.mean(pred["SR"])),
                "coupled_sr_std": float(np.std(pred["SR"])),
                "elm_sr_mean": float(np.mean(elm_sr)),
                "elm_sr_std": float(np.std(elm_sr)),
                "ntime": int(pred["ntime"]),
                **metrics,
            }
            rows.append(row)
            all_rows.append(row)
            sr_c_list.append(pred["SR"])
            sr_e_list.append(elm_sr)
            pred_c.append(pred["TOTSOMC"])
            pred_n.append(pred["TOTSOMN"])
            elm_c.append(float(elm_spin[0]))
            elm_n.append(float(elm_spin[1]))

        plot_paths = _plot_feedback(
            outdir / "plots", site, variant, members, rows
        )
        medians = {
            key: float(np.nanmedian([r[key] for r in rows])) for key in METRIC_KEYS
        }
        site_summary["variants"][variant] = {
            "n_members": len(rows),
            "metric_medians": medians,
            "plots": plot_paths,
        }
        if save_timeseries:
            nc_path = outdir / "timeseries" / f"{site}_{variant}_sr.nc"
            _write_netcdf(
                nc_path,
                members,
                np.vstack(sr_c_list),
                np.vstack(sr_e_list),
                np.asarray(pred_c, dtype=float),
                np.asarray(pred_n, dtype=float),
                np.asarray(elm_c, dtype=float),
                np.asarray(elm_n, dtype=float),
            )
            site_summary["variants"][variant]["timeseries"] = str(nc_path)
    return all_rows, site_summary


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
    variants = {
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
            variants,
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
        "schema": "spinup-forcing-coupling-iter003-eval-v1",
        "stage": args.stage_label,
        "members": members,
        "cases": cases,
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
