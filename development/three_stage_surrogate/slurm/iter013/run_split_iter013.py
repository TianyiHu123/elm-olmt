#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import require
from model_ELM.three_stage_sr import write_json
from model_ELM.three_stage_sr_release import fit_split, validate_split


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--raw-directory", required=True, type=Path)
    parser.add_argument("--split-id", required=True, type=int, choices=range(20))
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = fit_split(config, args.raw_directory, args.split_id, args.output_directory)
    require(report["convergence_warning_count"] == 0, "production convergence warning")
    validate_split(config, args.raw_directory, args.output_directory)
    scaled_x = args.output_directory / "X_scaled_float32.dat"
    require(scaled_x.is_file(), "scaled X scratch missing")
    scaled_x.unlink()
    report = json.loads((args.output_directory / "split_report.json").read_text(encoding="utf-8"))
    report.update(successful_scaled_x_scratch_removed=True, gpp_execution=False, full_chain_robustness=False)
    write_json(args.output_directory / "split_report.json", report)
    print(f"ITER013_SPLIT_OK split={args.split_id} iterations={report['model_iterations']} warnings=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
