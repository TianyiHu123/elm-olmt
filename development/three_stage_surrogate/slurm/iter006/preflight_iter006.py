#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp_release import preflight
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args(); report = preflight(json.loads(args.config.read_text(encoding="utf-8")), args.output_directory)
    print(f"ITER006_PREFLIGHT_OK splits={report['split_count']} no_training=true", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
