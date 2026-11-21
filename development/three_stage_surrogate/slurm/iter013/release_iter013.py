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
from model_ELM.three_stage_sr_release import fit_release


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--raw-directory", required=True, type=Path)
    parser.add_argument("--aggregate-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = fit_release(config, args.raw_directory, args.aggregate_directory, args.output_directory)
    require(report["convergence_warning_count"] == 0, "release convergence warning")
    require(report["scaled_replay_complete"] is True and report["successful_scaled_scratch_removed"] is True, "release replay/cleanup mismatch")
    print(f"ITER013_RELEASE_OK artifact={report['artifact_sha256']} predictions={report['handoff_sha256']} warnings=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
