#!/usr/bin/env python3
"""Iter016 analysis: ensemble tools orchestration and aggregate packaging."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
TOOLS = REPO_ROOT / "development" / "spinup_forcing_coupling" / "tools"
SLURM = REPO_ROOT / "development" / "spinup_forcing_coupling" / "slurm" / "iter016"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from ensemble_common import DEFAULT_SEEDS, SITE_CONFIG, load_leaf, tier_a_result  # noqa: E402

PYTHON = sys.executable
SITES = ("ABBY", "JERC")


def run_tool(script: Path, args: list[str]) -> None:
    command = [PYTHON, str(script), *args]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{script.name} failed\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


def count_campaign_pass(root: Path) -> int:
    count = 0
    for site in SITES:
        cfg = SITE_CONFIG[site]
        for seed in DEFAULT_SEEDS:
            leaf = root / "production" / site.lower() / cfg["config_dir"] / f"seed_{seed}"
            if (leaf / "raw_chain.npz").is_file() and (leaf / "production_result.json").is_file():
                count += 1
    return count


def write_report(path: Path, aggregate: dict, site_dirs: dict[str, Path]) -> None:
    lines = [
        "# Iter016 aggregate and decision report",
        "",
        "## Closeout identity",
        "",
        "- Iteration ID: `iter016`",
        "- Status: `in_progress`",
        "- Work type: `implementation`",
        "- Objective: multi-seed MAP ensemble operational experiment",
        "- Bounded scope: `1 preflight; 2 hybrid rebuilds; 2 production arrays (18 tasks); 1 analysis; 1 handoff validation`",
        f"- Overall acceptance result: `{aggregate['status']}`",
        "",
        "## Integrity and provenance",
        "",
        f"- Production leaves with immutable packages: `{aggregate['leaves']}`",
        "- Tier A retention uses mean acceptance in [0.20, 0.50] only.",
        "",
        "## Per-site ensemble summary",
        "",
    ]
    for site in SITES:
        diagnosis = json.loads((site_dirs[site] / "equifinality_diagnosis.json").read_text(encoding="utf-8"))
        inventory = json.loads((site_dirs[site] / "map_inventory.json").read_text(encoding="utf-8"))
        retained = [entry for entry in inventory["entries"] if entry["tier_a_pass"]]
        lines.extend(
            [
                f"### {site}",
                "",
                f"- Diagnostic label: `{diagnosis['map_label']}` (cloud `{diagnosis['cloud_confirmation']}`)",
                f"- Tier-A-retained seeds: `{', '.join(str(entry['seed']) for entry in retained) or 'none'}`",
                f"- MAP SR RMSE spread: `{diagnosis['map_sr_rmse_spread']:.6g}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Integrated conclusion (analysis-stage draft)",
            "",
            "This report draft is generated at analysis time. Final integrated conclusion,",
            "limitations, and next-experiment routing are completed at authorized closeout.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--forcing-artifact", type=Path, required=True)
    parser.add_argument("--spinup-artifact", type=Path, required=True)
    parser.add_argument("--analysis-output", type=Path, required=True)
    parser.add_argument("--summary-dir", type=Path, required=True)
    args = parser.parse_args()

    leaves = count_campaign_pass(args.root)
    if leaves != 18:
        raise RuntimeError(f"expected 18 production leaves, found {leaves}")

    args.analysis_output.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    site_dirs: dict[str, Path] = {}
    site_results = []
    for site in SITES:
        site_dir = args.analysis_output / site.lower()
        site_dir.mkdir(parents=True, exist_ok=True)
        site_dirs[site] = site_dir
        common = ["--root", str(args.root), "--site", site, "--output-dir", str(site_dir), "--overwrite"]
        run_tool(TOOLS / "ensemble_seed_health.py", common)
        run_tool(TOOLS / "ensemble_map_inventory.py", common)
        run_tool(TOOLS / "ensemble_equifinality_diagnostics.py", common + ["--subsample", "1000", "--rng-seed", "16016"])
        run_tool(
            TOOLS / "plot_ensemble_sr_overlay.py",
            common
            + [
                "--forcing-artifact",
                str(args.forcing_artifact),
                "--spinup-artifact",
                str(args.spinup_artifact),
            ],
        )
        run_tool(
            TOOLS / "plot_ensemble_physical_corner.py",
            common + ["--subsample", "1000", "--rng-seed", "16016"],
        )
        diagnosis = json.loads((site_dir / "equifinality_diagnosis.json").read_text(encoding="utf-8"))
        health = json.loads((site_dir / "seed_health.json").read_text(encoding="utf-8"))
        site_results.append(
            {
                "site": site,
                "integrity_pass": True,
                "tier_a_retained": diagnosis["retained_tier_a_seeds"],
                "diagnostic_label": diagnosis["map_label"],
                "cloud_confirmation": diagnosis["cloud_confirmation"],
                "excluded_seeds": [
                    row["seed"] for row in health["seeds"] if not row["tier_a_pass"]
                ],
            }
        )
        for name in site_dir.iterdir():
            if name.is_file():
                shutil.copy2(name, args.summary_dir / f"{site.lower()}_{name.name}")

    aggregate = {
        "schema": "spinup-forcing-coupling-iter016-aggregate-v1",
        "status": "pass",
        "leaves": leaves,
        "sites": site_results,
    }
    aggregate_path = args.analysis_output / "aggregate_result.json"
    aggregate_path.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(aggregate_path, args.summary_dir / "aggregate_result.json")
    write_report(args.summary_dir / "ITER016_REPORT.md", aggregate, site_dirs)
    print(f"ANALYSIS_PASS leaves={leaves}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
