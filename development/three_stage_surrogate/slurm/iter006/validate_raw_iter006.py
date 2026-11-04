#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp import write_json
from model_ELM.three_stage_gpp_release import validate_raw
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--raw-directory", required=True, type=Path); parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(); report = validate_raw(json.loads(args.config.read_text(encoding="utf-8")), args.raw_directory, full_hashes=True); write_json(args.output, report); args.output.parent.joinpath("ELIGIBLE").touch()
    print(f"ITER006_RAW_VALIDATE_OK rows={report['rows']} features={report['features']}", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
