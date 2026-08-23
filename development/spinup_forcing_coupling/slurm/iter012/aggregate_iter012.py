#!/usr/bin/env python3
"""Aggregate canonical Iter012 evaluations and retain legacy context separately."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def finite_max(values) -> float | None:
    array = np.asarray(values, dtype=float)
    return float(np.max(array[np.isfinite(array)])) if np.any(np.isfinite(array)) else None


def finite_min(values) -> float | None:
    array = np.asarray(values, dtype=float)
    return float(np.min(array[np.isfinite(array)])) if np.any(np.isfinite(array)) else None


def load_evaluation(
    root: Path,
    *,
    site: str,
    resolution: str,
    role: str,
) -> tuple[dict, dict]:
    result_path = root / "evaluation_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    required_artifacts = (
        result_path,
        root / "physical_traces.npz",
        root / "hourly_predictions.csv",
        root / "physical_corner.png",
    )
    if (
        result.get("status") != "pass"
        or result.get("site") != site
        or result.get("resolution") != resolution
        or result.get("evidence_role") != role
        or result.get("seeds") != [9009, 9010, 9011]
        or not all(path.is_file() for path in required_artifacts)
    ):
        raise ValueError(f"{role} {site}: evaluation identity/completeness failure")
    row = {
        "site": site,
        "role": role,
        "label": result["label"],
        "target_sha256": result["target_sha256"],
        "move_matches_contract": bool(result["move_matches_contract"]),
        "mean_acceptance_by_seed": result["mean_acceptance_by_seed"],
        "max_wasserstein": result["max_cross_seed_normalized_wasserstein"],
        "rhat_max": finite_max(result["rank_normalized_split_rhat"]),
        "bulk_ess_min": finite_min(result["rank_normalized_bulk_ess"]),
        "tail_ess_min": finite_min(result["quantile_tail_ess"]),
        "tau_available": bool(result["tau_available"]),
        "diagnostic_window_valid": bool(result["diagnostic_window_valid"]),
    }
    return result, row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-abby", type=Path, required=True)
    parser.add_argument("--canonical-jerc", type=Path, required=True)
    parser.add_argument("--legacy-abby", type=Path, required=True)
    parser.add_argument("--legacy-jerc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    canonical_rows = []
    legacy_rows = []
    for site, resolution, canonical_root, legacy_root in (
        ("ABBY", "daily", args.canonical_abby, args.legacy_abby),
        ("JERC", "hourly", args.canonical_jerc, args.legacy_jerc),
    ):
        canonical, canonical_row = load_evaluation(
            canonical_root, site=site, resolution=resolution, role="canonical"
        )
        legacy, legacy_row = load_evaluation(
            legacy_root, site=site, resolution=resolution, role="legacy"
        )
        if not canonical.get("move_matches_contract"):
            raise ValueError(f"{site}: canonical package did not use locked move configuration")
        if legacy.get("move_matches_contract"):
            raise ValueError(
                f"{site}: legacy package unexpectedly matches the locked move configuration"
            )
        canonical_rows.append(canonical_row)
        legacy_rows.append(legacy_row)

    args.output.mkdir(parents=True, exist_ok=True)
    result_path = args.output / "aggregate_result.json"
    if result_path.exists():
        raise FileExistsError(f"refusing to overwrite completed aggregate: {result_path}")
    payload = {
        "schema": "spinup-forcing-coupling-iter012-aggregate-v2",
        "canonical_sites": canonical_rows,
        "legacy_misconfigured_sampler_sites": legacy_rows,
        "decision_policy": (
            "Canonical Package v2 controls Iter012 conclusions. Package v1 is retained "
            "only as separately labeled misconfigured-sampler context."
        ),
        "status": "pass",
    }
    temporary = result_path.with_name(result_path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(result_path)
    print("AGGREGATE_PASS canonical_sites=2 legacy_sites=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
