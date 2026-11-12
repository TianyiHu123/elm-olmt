#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter009.iter009_common import fit_leaf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True, type=int)
    parser.add_argument("--split-id", required=True, type=int)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = fit_leaf(config, args.candidate_id, args.split_id, args.output_directory)
    print(
        f"ITER009_LEAF_OK candidate={args.candidate_id} split={args.split_id} "
        f"iterations={report['model_iterations']} warnings={report['convergence_warning_count']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
