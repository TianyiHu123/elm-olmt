#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp_release import fit_split
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--raw-directory", required=True, type=Path); parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args(); report = fit_split(json.loads(args.config.read_text(encoding="utf-8")), args.raw_directory, 0, args.output_directory, smoke=True)
    print(f"ITER006_SMOKE_OK train_members={report['train_members']} validation_members={report['validation_members']}", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
