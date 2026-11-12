#!/usr/bin/env python
"""Run one Iter012 arm/split leaf."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from development.three_stage_surrogate.slurm.iter012.iter012_common import ARM_IDS, fit_leaf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--arm-id", required=True, choices=ARM_IDS)
    parser.add_argument("--split-id", required=True, type=int, choices=range(20))
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = fit_leaf(config, args.arm_id, args.split_id, args.output_directory)
    print(f"ITER012_LEAF_OK arm={args.arm_id} split={args.split_id} iterations={report['model_iterations']} warnings={report['convergence_warning_count']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
