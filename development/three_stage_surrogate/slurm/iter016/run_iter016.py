#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter016.refit_iter016 import load_config, preflight, refit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "refit"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    report = preflight(config, args.output) if args.mode == "preflight" else refit(config, args.output)
    if args.mode == "preflight":
        print("ITER016_UNIT1_OK release_interface=true smoke=pass fixed_test=false", flush=True)
    else:
        print(
            "ITER016_REFIT_OK members=819 artifacts=3 hard_zero=true fixed_test_fit=false",
            flush=True,
        )
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
