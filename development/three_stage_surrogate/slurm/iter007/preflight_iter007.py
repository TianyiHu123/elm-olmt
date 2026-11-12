#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter007.iter007_common import validate_contract
from model_ELM.three_stage_gpp import write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output_directory.mkdir(parents=True, exist_ok=False)
    report = validate_contract(config, full_raw_hashes=True)
    write_json(args.output_directory / "preflight_report.json", report)
    (args.output_directory / "ELIGIBLE").touch(exist_ok=False)
    print(
        f"ITER007_PREFLIGHT_OK candidates={report['candidate_count']} "
        f"screen_fits={report['screen_fit_count']} finalist_fits={report['finalist_fit_count']} "
        "no_training=true",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
