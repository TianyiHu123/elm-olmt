#!/usr/bin/env python
"""Create the locked member-balanced surrogate uncertainty package."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_spinup_release import aggregate_uncertainty


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--robustness-directory", required=True, type=Path)
    parser.add_argument("--split-manifest", required=True, type=Path)
    parser.add_argument("--split-sha256", required=True)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    require(sha256_file(args.split_manifest) == args.split_sha256, "split file hash mismatch")
    split_manifest = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    aggregate_uncertainty(args.robustness_directory / "paired_robustness_evidence.nc", split_manifest, args.output_directory)
    for name in ("paired_robustness_evidence.nc", "metric_distribution.csv", "depth_error_dependence.csv", "convergence.json", "robustness_report.json"):
        shutil.copy2(args.robustness_directory / name, args.output_directory / name)
    shutil.copy2(args.split_manifest, args.output_directory / "repeated_split_manifest.json")
    print("ITER004_UNCERTAINTY_OK member_balanced=true ddof=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
