#!/usr/bin/env python3
"""Deterministic calculation-contract fixture for Iter004."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.ELM_diagnose.tools.oat_sensitivity import fixture_checks


def main() -> None:
    result = fixture_checks()
    if result.get("status") != "pass":
        raise RuntimeError(f"unexpected fixture result: {result}")
    print(json.dumps(result, sort_keys=True))
    print("ITER004_FIXTURE_PASS")


if __name__ == "__main__":
    main()
