#!/usr/bin/env python3
"""Validate that each Iter017 path has the required terminal reporting record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted((args.root / "paths").glob("*"))
    if len(paths) != 4:
        raise ValueError(f"expected four path directories, found {len(paths)}")
    result = []
    for path in paths:
        report = path / "reports" / "report_manifest.json"
        stage = path / "postprocess" / "stage_manifest.json"
        table = path / "reports" / "best_parameters" / "parameter_sets.csv"
        corner = path / "reports" / "plots" / "physical_corner.png"
        parameter_nc = sorted((path / "reports" / "best_parameters" / "clm_params").glob("clm_params_seed_*.nc"))
        leaves = sorted((path / "optimization").glob("seed_*"))
        if not all(item.is_file() for item in (report, stage, table, corner)):
            raise FileNotFoundError(f"incomplete report package: {path}")
        if len(leaves) != 3 or len(parameter_nc) != 3:
            raise ValueError(f"expected three seed leaves and three exact CLM files: {path}")
        payload = json.loads(report.read_text())
        if payload.get("status") not in {"pass", "insufficient_retained"}:
            raise ValueError(f"unrecognized report status: {path}")
        result.append({"path": str(path), "status": payload["status"], "seed_leaves": len(leaves)})
    destination = args.root / "handoff_validation.json"
    destination.write_text(json.dumps({"schema": "iter017-handoff-v1", "paths": result}, indent=2) + "\n")
    print("ITER017_HANDOFF_PASS paths=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
