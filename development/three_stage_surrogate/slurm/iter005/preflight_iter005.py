#!/usr/bin/env python
"""No-training Iter005 dependency and synthetic contract checks."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.three_stage_data import ThreeStageSnapshot, require, sha256_file
from model_ELM.three_stage_gpp import FEATURE_COUNT, MODEL_CONFIG, engineer_forcing, engineer_forcing_window, feature_names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    require(config["fixed_test_allowed"] is False, "fixed-test contract drift")
    require(config["spinup_execution_allowed"] is False, "spinup-execution contract drift")
    require(config["temporal_subsampling_allowed"] is False, "temporal contract drift")
    require(config["clipping_allowed"] is False, "clipping contract drift")
    require(config["model_config"] == MODEL_CONFIG, "model configuration drift")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=True)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot identity mismatch")
    require(sha256_file(snapshot.split_path) == config["global_split_sha256"], "split identity mismatch")
    require(sha256_file(Path(config["predicted_cn_handoff"])) == config["predicted_cn_sha256"], "handoff identity mismatch")
    require(len(feature_names(snapshot)) == FEATURE_COUNT == config["feature_count"], "feature count mismatch")
    hours = np.arange(1440, dtype=np.int64)
    raw = {name: np.linspace(1.0, 2.0, hours.size) for name in ("PRECTmms", "FSDS", "FLDS", "TBOT", "RH", "WIND", "PSRF")}
    engineered = engineer_forcing(raw, hours)
    require(engineered.shape == (1440, 20) and np.all(np.isfinite(engineered)), "synthetic forcing contract failed")
    window = engineer_forcing_window(raw, hours, 720, 1440)
    require(window.shape == (720, 20) and np.array_equal(window, engineered[720:]), "history-aware window contract failed")
    print("ITER005_PREFLIGHT_OK no_training=true features=43 rows=100442160", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
