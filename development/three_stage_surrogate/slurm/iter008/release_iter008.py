#!/usr/bin/env python
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from model_ELM.three_stage_gpp_release import fit_release
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True, type=Path); parser.add_argument("--raw-directory", required=True, type=Path); parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args(); report = fit_release(json.loads(args.config.read_text(encoding="utf-8")), args.raw_directory, None, args.output_directory)
    print(f"ITER008_RELEASE_FIT_OK artifact={report['artifact_sha256']} handoff={report['handoff_sha256']}", flush=True); return 0
if __name__ == "__main__": raise SystemExit(main())
