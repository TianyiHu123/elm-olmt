#!/usr/bin/env python
"""Bounded no-training Iter012 compute preflight."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.spinup_surrogate_artifact import (  # noqa: E402
    normalize_physical_parameters,
    require_exact_feature_order,
    validate_versioned_artifact,
)
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    compose_forcing_surrogate_design_matrix,
)

ITER_DIR = REPO_ROOT / "development/spinup_surrogate/slurm/iter012"
MANIFEST = ITER_DIR / "iter012_releases.tsv"
CANONICAL_RELEASE = ITER_DIR / "case.release_spinup_iter012.slurm"
OUTPUT_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output"
)
EXPECTED_CASES = [
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
]


def _read_config(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 5:
        raise ValueError(f"Expected five config lines in {path}, got {len(lines)}")
    result = {}
    for line in lines:
        if "=" not in line:
            raise ValueError(f"Malformed config line in {path}: {line!r}")
        key, value = line.split("=", 1)
        if key in result:
            raise ValueError(f"Duplicate config key {key} in {path}")
        result[key] = value
    expected = [
        "VARIANT",
        "FEATURE_COUNT",
        "FEATURE_SUBSET",
        "REFERENCE_STATS",
        "OUTPUT_ARTIFACT",
    ]
    if list(result) != expected:
        raise ValueError(f"Config key order mismatch in {path}: {list(result)}")
    return result


def _synthetic_contract_gate() -> None:
    targets = ["TOTSOMC", "TOTSOMN"]
    complete = ["parm_0", "parm_1", "PCT_SAND", "X_clim_mean"]
    selected = ["parm_0", "PCT_SAND"]
    artifact = {
        "schema_version": "spinup-surrogate-v1",
        "target_order": targets,
        "models": {target: object() for target in targets},
        "x_scaler": {target: object() for target in targets},
        "y_scaler": {target: object() for target in targets},
        "training_layout": {
            "input_feature_names": selected,
            "input_feature_names_all": complete,
            "selected_feature_indices": [0, 2],
        },
        "parameter_metadata": {
            "physical_names": ["p0", "p1"],
            "aliases": ["parm_0", "parm_1"],
            "ensemble_pmin": [0.0, -1.0],
            "ensemble_pmax": [1.0, 1.0],
        },
    }
    validate_versioned_artifact(artifact)
    positional = normalize_physical_parameters(artifact, [0.5, 0.0])
    named = normalize_physical_parameters(artifact, {"p0": 0.5, "p1": 0.0})
    if not np.array_equal(positional, named):
        raise ValueError("Synthetic named/positional parameter normalization differs")
    require_exact_feature_order(selected, selected)
    try:
        require_exact_feature_order(list(reversed(selected)), selected)
    except ValueError as exc:
        if "correct --feature-subset value=" not in str(exc):
            raise
    else:
        raise ValueError("Synthetic feature-order negative gate did not fail")
    forcing = np.arange(6, dtype=np.float64).reshape(3, 2)
    X = compose_forcing_surrogate_design_matrix(
        forcing,
        np.array([0.5, 0.0]),
        np.array([100.0, 10.0]),
        {"n_forcing_cols": 2, "n_params": 2, "n_spinup": 2},
    )
    if X.shape != (3, 6) or X.dtype != np.float64:
        raise ValueError("Synthetic forcing bridge shape/dtype gate failed")


def main() -> int:
    with MANIFEST.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp, delimiter="\t"))
    if [row["variant"] for row in rows] != ["drop32", "drop21_corr080"]:
        raise ValueError("Iter012 manifest must contain exact ordered release variants")
    expected_counts = {"drop32": 32, "drop21_corr080": 21}
    for row in rows:
        variant = row["variant"]
        features = row["feature_subset"].split(",")
        if len(features) != expected_counts[variant] or len(set(features)) != len(features):
            raise ValueError(f"Feature cardinality/uniqueness mismatch for {variant}")
        if features[:14] != [f"parm_{i}" for i in range(14)]:
            raise ValueError(f"Physical parameter alias prefix mismatch for {variant}")
        if any(
            name.startswith(("FLDS_", "WIND_", "PSRF_")) for name in features
        ):
            raise ValueError(f"Forbidden forcing family present in {variant}")
        reference = Path(row["reference_stats"])
        reference_payload = json.loads(reference.read_text(encoding="utf-8"))
        if reference_payload["case_names"] != EXPECTED_CASES:
            raise ValueError(f"Reference case order mismatch for {variant}")
        if reference_payload["split_random_state"] != 10001:
            raise ValueError(f"Reference seed mismatch for {variant}")
        if reference_payload["input_feature_names"] != features:
            raise ValueError(f"Reference feature order mismatch for {variant}")
        if list(reference_payload["by_variable"]) != ["TOTSOMC", "TOTSOMN"]:
            raise ValueError(f"Reference target order mismatch for {variant}")
        run_dir = OUTPUT_ROOT / f"spinup_surrogate_iter012_{variant}"
        submitted = run_dir / f"submit_{variant}.slurm"
        config = run_dir / "submission_config.env"
        if submitted.read_bytes() != CANONICAL_RELEASE.read_bytes():
            raise ValueError(f"Submitted release copy differs for {variant}")
        parsed = _read_config(config)
        expected_config = {
            "VARIANT": variant,
            "FEATURE_COUNT": row["feature_count"],
            "FEATURE_SUBSET": row["feature_subset"],
            "REFERENCE_STATS": row["reference_stats"],
            "OUTPUT_ARTIFACT": row["output_artifact"],
        }
        if parsed != expected_config:
            raise ValueError(f"Manifest/config mismatch for {variant}")
        expected_output = (
            run_dir
            / "surrogate_spinup"
            / f"spinup_surrogate_iter012_{variant}.pkl"
        )
        if Path(row["output_artifact"]) != expected_output:
            raise ValueError(f"Output artifact path mismatch for {variant}")
    _synthetic_contract_gate()
    print(
        "ITER012_PREFLIGHT_OK no_training=true variants=drop32,drop21_corr080 "
        "features=32,21 references=seed10001 bridge_shape_dtype=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
