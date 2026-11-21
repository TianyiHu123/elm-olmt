#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp_release import prepare_raw
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--attempt-directory", required=True, type=Path)
    args = parser.parse_args(); config = json.loads(args.config.read_text(encoding="utf-8")); attempt = args.attempt_directory
    prepare_raw(config, attempt / "raw")
    print("ITER006_RAW_PREPARE_OK", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
