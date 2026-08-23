#!/usr/bin/env python3
"""Iter016 makeup: replot MAP ensemble SR overlays with likelihood-valid mask."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
TOOL = REPO_ROOT / "development/spinup_forcing_coupling/tools/plot_ensemble_sr_overlay.py"
SITES = ("ABBY", "JERC")


def sync_summary(site: str, site_dir: Path, summary_dir: Path) -> None:
    prefix = site.lower()
    mapping = {
        "Predictions_SR_MAP_ensemble.png": f"{prefix}_Predictions_SR_MAP_ensemble.png",
        "sr_overlay_manifest.json": f"{prefix}_sr_overlay_manifest.json",
    }
    for src_name, dst_name in mapping.items():
        src = site_dir / src_name
        dst = summary_dir / dst_name
        if dst.is_file():
            backup = dst.with_name(f"{dst.stem}_pre_valid_mask_makeup{dst.suffix}")
            if not backup.is_file():
                shutil.copy2(dst, backup)
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--forcing-artifact", type=Path, required=True)
    parser.add_argument("--spinup-artifact", type=Path, required=True)
    parser.add_argument("--analysis-output", type=Path, required=True)
    parser.add_argument("--summary-dir", type=Path, required=True)
    args = parser.parse_args()

    args.analysis_output.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    command_base = [sys.executable, str(TOOL), "--root", str(args.root), "--overwrite"]
    for site in SITES:
        site_dir = args.analysis_output / site.lower()
        site_dir.mkdir(parents=True, exist_ok=True)
        command = [
            *command_base,
            "--site",
            site,
            "--forcing-artifact",
            str(args.forcing_artifact),
            "--spinup-artifact",
            str(args.spinup_artifact),
            "--output-dir",
            str(site_dir),
        ]
        subprocess.run(command, check=True)
        sync_summary(site, site_dir, args.summary_dir)
        print(f"REPLOT_SR_OVERLAY site={site} summary={args.summary_dir}")
    print("REPLOT_SR_OVERLAY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
