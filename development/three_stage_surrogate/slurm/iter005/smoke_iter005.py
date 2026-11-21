#!/usr/bin/env python
"""Run the bounded Iter005 integration smoke fit."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_gpp import smoke_fit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    report = smoke_fit(json.loads(args.config.read_text(encoding="utf-8")), args.prepared_directory, args.output_directory)
    print(f"ITER005_SMOKE_OK train_rows={report['train_rows']} validation_rows={report['validation_rows']} iterations={report['iterations']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
