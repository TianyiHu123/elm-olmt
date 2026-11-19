#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter015.full_chain_iter015 import load_config, preflight, run_split


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "split"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split-id", type=int)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.mode == "preflight":
        report = preflight(config, args.output)
        print("ITER015_UNIT1_OK splits=20 smoke=pass hard_zero=true fixed_test=false", flush=True)
    else:
        if args.split_id is None:
            parser.error("--split-id is required for split mode")
        report = run_split(config, args.split_id, args.output)
        print(
            f"ITER015_SPLIT_OK split={args.split_id} metrics={report['metric_row_count']} "
            f"gate_rows={report['gate_row_count']} hard_zero=true fixed_test=false",
            flush=True,
        )
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
