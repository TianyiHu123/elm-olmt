#!/usr/bin/env python3
"""Independent, non-destructive reporting for a completed coupled MCMC path.

The optimizer owns its leaf products. This stage reads those products and writes a
portable report package below ``<path-root>/reports``; it never alters a chain,
backend, or leaf-level plot.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_ELM.optimization_config import load_campaign, write_stage_manifest


SCHEMA = "coupled-optimization-report-v3"
TIER_A_MIN = 0.20
TIER_A_MAX = 0.50


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_file(source: Path, destination: Path) -> str | None:
    if not source.is_file():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def _leaf_records(
    root: Path, tier_min: float, tier_max: float, campaign_sha256: str,
) -> list[dict[str, Any]]:
    leaves = sorted((root / "optimization").glob("seed_*"))
    if not leaves:
        raise FileNotFoundError(f"no optimization leaves under {root / 'optimization'}")
    records: list[dict[str, Any]] = []
    for leaf in leaves:
        raw_path = leaf / "raw_chain.npz"
        result_path = leaf / "production_result.json"
        required = (
            "stage_manifest.json", "raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json",
            "backend.h5", "checkpoint_manifest.json", "selection_ledger.json",
            "production_result.json", "best_params.txt", "clm_params_best.nc",
            "plots/corner/corner_plot.png", "diagnostics/skill_table.csv",
            "diagnostics/walker_acceptance.csv", "diagnostics/parameter_chain_health.csv",
            "diagnostics/chain_health.json", "diagnostics/collocation_audit.csv",
            "diagnostics/residual_summary.csv", "diagnostics/delta_logL.csv",
        )
        missing = [name for name in required if not (leaf / name).is_file()]
        if missing:
            raise FileNotFoundError(f"incomplete optimization leaf {leaf}: {', '.join(missing)}")
        if not (leaf / "plots" / "predictions").is_dir():
            raise FileNotFoundError(f"missing site-specific posterior products: {leaf}")
        if not raw_path.is_file() or not result_path.is_file():
            raise FileNotFoundError(f"incomplete optimization leaf: {leaf}")
        receipt = _json(leaf / "stage_manifest.json")
        if receipt.get("stage") != "optimization":
            raise ValueError(f"leaf stage receipt is not optimization: {leaf}")
        if receipt.get("campaign_sha256") != campaign_sha256:
            raise ValueError(f"leaf campaign receipt does not match report campaign: {leaf}")
        if Path(str(receipt.get("output", ""))).resolve() != leaf.resolve():
            raise ValueError(f"leaf stage receipt output does not match its directory: {leaf}")
        raw = np.load(raw_path, allow_pickle=False)
        chain = np.asarray(raw["chain"], dtype=float)
        logp = np.asarray(raw.get("physical_log_prob", raw["log_prob"]), dtype=float)
        if chain.ndim != 3 or logp.shape != chain.shape[:2]:
            raise ValueError(f"invalid raw-chain dimensions in {raw_path}")
        flat_index = int(np.nanargmax(logp.reshape(-1)))
        parameter_names = [str(value) for value in raw["parameter_names"]]
        state = chain.reshape(-1, chain.shape[-1])[flat_index]
        result = _json(result_path)
        acceptance = float(result.get("result", {}).get("mean_acceptance_fraction", np.nan))
        checkpoint = _json(leaf / "checkpoint_manifest.json")
        if int(checkpoint.get("backend_iteration", -1)) != int(result["nsteps"]):
            raise ValueError(f"checkpoint is not terminal for {leaf}")
        if not np.all(np.isfinite(chain)) or not np.all(np.isfinite(logp)):
            raise ValueError(f"non-finite raw chain or posterior values in {leaf}")
        if np.any(chain < np.asarray(raw["pmin"], float)) or np.any(chain > np.asarray(raw["pmax"], float)):
            raise ValueError(f"out-of-bounds physical chain in {leaf}")
        tier_a = bool(np.isfinite(acceptance) and tier_min <= acceptance <= tier_max)
        records.append({
            "seed": leaf.name.removeprefix("seed_"), "leaf": leaf,
            "parameter_names": parameter_names, "map_state": state,
            "map_log_posterior": float(logp.reshape(-1)[flat_index]), "chain": chain,
            "mean_acceptance_fraction": acceptance, "tier_a": tier_a,
            "tier_a_reason": "tier_a_pass" if tier_a else "acceptance_outside_descriptive_range",
            "chain_health": _json(leaf / "diagnostics" / "chain_health.json"),
            "parameter_health": list(csv.DictReader((leaf / "diagnostics" / "parameter_chain_health.csv").open(encoding="utf-8"))),
            "skills": list(csv.DictReader((leaf / "diagnostics" / "skill_table.csv").open(encoding="utf-8"))),
            "delta_log_likelihood": list(csv.DictReader((leaf / "diagnostics" / "delta_logL.csv").open(encoding="utf-8"))),
        })
    first = records[0]["parameter_names"]
    if any(record["parameter_names"] != first for record in records[1:]):
        raise ValueError("parameter names differ across seeds; refusing aggregate report")
    return records


def _write_parameter_tables(report_dir: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = ["seed", "tier_a", "tier_a_reason", "mean_acceptance_fraction", "map_log_posterior"]
    fields += list(records[0]["parameter_names"])
    rows: list[dict[str, Any]] = []
    for record in records:
        row = {key: record[key] for key in fields[:5]}
        row.update(zip(record["parameter_names"], np.asarray(record["map_state"], float).tolist()))
        rows.append(row)
    csv_path = report_dir / "parameter_sets.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    shutil.copy2(csv_path, report_dir / "parameter_sets.txt")
    return rows


def _write_corner(report_dir: Path, records: list[dict[str, Any]]) -> str:
    names = list(records[0]["parameter_names"])
    physical = [index for index, name in enumerate(names) if not name.startswith("sigma_")]
    samples = np.concatenate([record["chain"][:, :, physical].reshape(-1, len(physical)) for record in records])
    if len(samples) > 12000:
        samples = samples[np.linspace(0, len(samples) - 1, 12000, dtype=int)]
    count = len(physical)
    figure, axes = plt.subplots(count, count, figsize=(1.7 * count, 1.7 * count), squeeze=False)
    for row in range(count):
        for column in range(count):
            axis = axes[row, column]
            if row == column:
                axis.hist(samples[:, row], bins=35, color="0.35", density=True)
            elif row > column:
                axis.plot(samples[:, column], samples[:, row], ".", ms=0.25, alpha=0.08, color="0.15")
            else:
                axis.axis("off")
                continue
            if row == count - 1:
                axis.set_xlabel(names[physical[column]], fontsize=7, rotation=45, ha="right")
            else:
                axis.set_xticklabels([])
            if column == 0 and row:
                axis.set_ylabel(names[physical[row]], fontsize=7)
            else:
                axis.set_yticklabels([])
    figure.suptitle("Physical posterior parameter distribution (all seeds)", fontsize=12)
    figure.tight_layout()
    path = report_dir.parent / "plots" / "physical_corner.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return str(path)


def _copy_leaf_products(root: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for record in records:
        seed, leaf = record["seed"], Path(record["leaf"])
        destination = root / "reports" / "per_seed" / f"seed_{seed}"
        entry = {"seed": seed, "clm_params": _copy_file(leaf / "clm_params_best.nc", root / "reports" / "best_parameters" / "clm_params" / f"clm_params_seed_{seed}.nc")}
        for relative in (
            "best_params.txt", "plots/corner/corner_plot.png", "diagnostics/skill_table.csv",
            "diagnostics/walker_acceptance.csv", "diagnostics/collocation_audit.csv",
            "diagnostics/residual_summary.csv", "diagnostics/delta_logL.csv",
        ):
            entry[relative] = _copy_file(leaf / relative, destination / Path(relative).name)
        predictions = leaf / "plots" / "predictions"
        if predictions.is_dir():
            shutil.copytree(predictions, destination / "predictions", dirs_exist_ok=False)
            entry["posterior_timeseries"] = str(destination / "predictions")
        copied.append(entry)
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--path-root", required=True, type=Path)
    args = parser.parse_args()
    contract = load_campaign(args.campaign, "reporting")
    root = args.path_root.resolve()
    reports = root / "reports"
    if reports.exists() or (root / "postprocess" / "stage_manifest.json").exists():
        raise FileExistsError(f"refusing to overwrite reporting outputs under {root}")
    reporting = contract["reporting"]
    tier_range = reporting.get("tier_a_acceptance_range", [TIER_A_MIN, TIER_A_MAX])
    if not isinstance(tier_range, list) or len(tier_range) != 2:
        raise ValueError("reporting.tier_a_acceptance_range must contain two values")
    tier_min, tier_max = (float(value) for value in tier_range)
    records = _leaf_records(root, tier_min, tier_max, str(contract["campaign_sha256"]))
    parameter_dir = reports / "best_parameters"
    parameter_dir.mkdir(parents=True)
    rows = _write_parameter_tables(parameter_dir, records)
    copied = _copy_leaf_products(root, records) if bool(reporting.get("copy_leaf_products", True)) else []
    corner = _write_corner(parameter_dir, records)
    retained = [record["seed"] for record in records if record["tier_a"]]
    status = "pass" if retained else "insufficient_retained"
    evidence = [{"seed": record["seed"], "mean_acceptance_fraction": record["mean_acceptance_fraction"],
                 "chain_health": record["chain_health"], "parameter_health": record["parameter_health"],
                 "skills": record["skills"], "delta_log_likelihood": record["delta_log_likelihood"]}
                for record in records]
    manifest = {"schema": SCHEMA, "status": status, "sites": contract["shared"]["sites"],
                "discovered_seeds": [record["seed"] for record in records],
                "retained_tier_a_seeds": retained, "all_seed_rows": rows,
                "tier_a_acceptance_range": [tier_min, tier_max], "copied_leaf_products": copied, "physical_corner": corner,
                "per_seed_diagnostic_evidence": evidence}
    (reports / "report_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_stage_manifest(root / "postprocess", {**contract, "path_root": str(root), "leaf_count": len(records), "status": status})
    print(f"REPORT_PASS status={status} leaves={len(records)} root={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
