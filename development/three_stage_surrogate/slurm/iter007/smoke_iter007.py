#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.three_stage_surrogate.slurm.iter007.iter007_common import smoke


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    report = smoke(json.loads(args.config.read_text(encoding="utf-8")), args.output_directory)
    print(f"ITER007_SMOKE_OK candidates={len(report['candidates'])}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
