#!/usr/bin/env python3
"""Run the locked Iter001–005 MCMC regression inventory on a Puma compute node."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

INVENTORY = (
    ("test_mcmc_three_stage_*.py", 33),
    ("test_mcmc_prior_iter001.py", 6),
    ("test_mcmc_coupled_interface_iter001.py", 2),
)


def main() -> None:
    suite = unittest.TestSuite()
    for pattern, count in INVENTORY:
        selected = unittest.defaultTestLoader.discover(str(REPO_ROOT / "tests"), pattern=pattern)
        if selected.countTestCases() != count:
            raise SystemExit(f"Iter005 inventory mismatch for {pattern}: expected {count}, found {selected.countTestCases()}")
        suite.addTests(selected)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun != 41 or result.skipped or result.failures or result.errors:
        raise SystemExit(
            f"Iter005 unittest gate failed: run={result.testsRun} skipped={len(result.skipped)} "
            f"failures={len(result.failures)} errors={len(result.errors)}"
        )
    print("MCMC_ITER005_UNITTEST_PASS tests=41 skipped=0")


if __name__ == "__main__":
    main()
