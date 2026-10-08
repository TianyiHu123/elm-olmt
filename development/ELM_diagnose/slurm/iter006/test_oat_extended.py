#!/usr/bin/env python3
"""Deterministic calculation-contract fixture for Iter006."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.ELM_diagnose.tools.oat_sensitivity import fixture_checks, paired_site_contract_fixture


def main() -> None:
    result = fixture_checks()
    if result.get("status") != "pass":
        raise RuntimeError(f"unexpected fixture result: {result}")
    required = {"hr_pathways", "hr_limiters", "litter_ratios"}
    if not required.issubset(result):
        raise RuntimeError(f"fixture result lacks Iter006 checks: {sorted(required - set(result))}")
    with tempfile.TemporaryDirectory(prefix="iter006_site_parity.") as temporary:
        site_result = paired_site_contract_fixture(Path(temporary) / "paired")
    if site_result.get("status") != "pass" or not site_result.get("numeric_products_equal"):
        raise RuntimeError(f"unexpected paired-site result: {site_result}")
    print(json.dumps({"calculation_fixture": result, "site_fixture": site_result}, sort_keys=True))
    print("ITER006_FIXTURE_PASS")


if __name__ == "__main__":
    main()
