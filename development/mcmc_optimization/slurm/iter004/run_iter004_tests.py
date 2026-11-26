#!/usr/bin/env python3
"""Run the exact Iter003/004 three-stage unittest inventory."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXPECTED_TESTS = 27


def main() -> None:
    suite = unittest.defaultTestLoader.discover(
        str(REPO_ROOT / "tests"), pattern="test_mcmc_three_stage_*.py"
    )
    if suite.countTestCases() != EXPECTED_TESTS:
        raise SystemExit(
            f"Iter004 test inventory mismatch: expected {EXPECTED_TESTS}, found {suite.countTestCases()}"
        )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun != EXPECTED_TESTS or result.skipped or result.failures or result.errors:
        raise SystemExit(
            "Iter004 unittest gate failed: "
            f"run={result.testsRun} skipped={len(result.skipped)} "
            f"failures={len(result.failures)} errors={len(result.errors)}"
        )
    print(f"MCMC_ITER004_UNITTEST_PASS tests={EXPECTED_TESTS} skipped=0")


if __name__ == "__main__":
    main()
