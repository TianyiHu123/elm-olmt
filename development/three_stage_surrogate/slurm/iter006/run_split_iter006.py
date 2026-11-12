#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp_release import fit_split, validate_split
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--raw-directory", required=True, type=Path); parser.add_argument("--split-id", required=True, type=int); parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args(); config = json.loads(args.config.read_text(encoding="utf-8")); report = fit_split(config, args.raw_directory, args.split_id, args.output_directory); validate_split(config, args.raw_directory, args.output_directory)
    print(f"ITER006_SPLIT_OK split={args.split_id} iterations={report['model_iterations']} warnings={report['convergence_warning_count']}", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
