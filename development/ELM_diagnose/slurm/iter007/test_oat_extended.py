#!/usr/bin/env python3
"""Deterministic calculation and dynamic-input contract fixture for Iter007."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from development.ELM_diagnose.tools.oat_sensitivity import (
    fixture_checks,
    paired_site_contract_fixture,
    parse_log_parameters,
    parse_mapping,
)

PARAMETERS = (
    "act25",
    "br_mr",
    "decomp_depth_efolding",
    "grperc",
    "k_l1",
    "k_l2",
    "k_l3",
    "k_s1",
    "k_s2",
    "k_s3",
    "k_s4",
    "leaf_long",
    "q10_mr",
)
LOG_PARAMETERS = frozenset({"k_l1", "k_l2", "k_l3", "k_s1", "k_s2", "k_s3", "k_s4"})


def require_rejection(callable_object, expected_text: str) -> None:
    try:
        callable_object()
    except ValueError as exc:
        if expected_text not in str(exc):
            raise AssertionError(f"unexpected rejection: {exc}") from exc
    else:
        raise AssertionError(f"expected rejection containing {expected_text!r}")


def main() -> None:
    declared = [f"{parameter}:synthetic_{parameter}.pkl" for parameter in PARAMETERS]
    mappings = parse_mapping(declared)
    if tuple(mappings) != PARAMETERS:
        raise RuntimeError("explicit parameter order was not preserved")
    logs = parse_log_parameters(",".join(parameter for parameter in PARAMETERS if parameter in LOG_PARAMETERS), PARAMETERS)
    if logs != LOG_PARAMETERS:
        raise RuntimeError("explicit log-parameter subset changed")
    require_rejection(lambda: parse_mapping([*declared, declared[0]]), "duplicate parameter mapping")
    require_rejection(lambda: parse_mapping(["bad-name:bad.pkl"]), "unknown or incomplete")
    require_rejection(lambda: parse_mapping(["act25:*.pkl"]), "exact basename")
    require_rejection(lambda: parse_mapping(["act25:a.pkl", "br_mr:a.pkl"]), "duplicate pickle basename")
    require_rejection(lambda: parse_log_parameters("k_l1,k_l1", PARAMETERS), "duplicate")
    require_rejection(lambda: parse_log_parameters("grpnow", PARAMETERS), "subset of mapped parameters")

    result = fixture_checks(PARAMETERS)
    if result.get("status") != "pass":
        raise RuntimeError(f"unexpected calculation fixture result: {result}")
    required = {"hr_pathways", "hr_limiters", "litter_ratios"}
    if not required.issubset(result):
        raise RuntimeError(f"fixture result lacks Iter007 checks: {sorted(required - set(result))}")
    with tempfile.TemporaryDirectory(prefix="iter007_site_parity.") as temporary:
        site_result = paired_site_contract_fixture(Path(temporary) / "paired", PARAMETERS, LOG_PARAMETERS)
    if site_result.get("status") != "pass" or not site_result.get("numeric_products_equal"):
        raise RuntimeError(f"unexpected paired-site result: {site_result}")
    if site_result.get("unsupported_member_rows_retained") != 208:
        raise RuntimeError(f"unexpected explicit-gap cardinality: {site_result}")
    print(json.dumps({"calculation_fixture": result, "site_fixture": site_result}, sort_keys=True))
    print("ITER007_FIXTURE_PASS parameters=13 figures_per_site=44")


if __name__ == "__main__":
    main()
