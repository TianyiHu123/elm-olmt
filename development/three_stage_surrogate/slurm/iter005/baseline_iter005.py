#!/usr/bin/env python
"""Fit the fixed Iter005 655/164 GPP baseline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_gpp import fit_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    report = fit_baseline(json.loads(args.config.read_text(encoding="utf-8")), args.prepared_directory, args.output_directory)
    print(f"ITER005_BASELINE_OK artifact={report['artifact_sha256']} iterations={report['model_iterations']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
