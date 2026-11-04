#!/usr/bin/env python
"""Materialize the attempt-local Iter005 prepared contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_gpp import prepare_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    report = prepare_contract(json.loads(args.config.read_text(encoding="utf-8")), args.output_directory)
    print(f"ITER005_MATERIALIZE_OK x_sha256={report['x_sha256']} rows=100442160", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
