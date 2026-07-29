#!/usr/bin/env python
"""Cross-artifact operational validation for the locked Iter012 releases."""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Mapping

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.spinup_surrogate_artifact import (  # noqa: E402
    build_selected_inference_matrix,
    case_inference_components,
    load_spinup_surrogate_artifact,
    normalize_physical_parameters,
    parse_physical_parameter_json,
    predict_versioned_spinup,
    require_exact_feature_order,
    validate_versioned_artifact,
)
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    compose_forcing_surrogate_design_matrix,
)

VARIANTS = ("drop32", "drop21_corr080")
CASE_NAMES = (
    "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC_ppe6_I20TRCNPRDCTCBC",
    "OSBS_ppe6_I20TRCNPRDCTCBC",
    "SOAP_ppe6_I20TRCNPRDCTCBC",
    "RMNP_ppe6_I20TRCNPRDCTCBC",
    "TALL_ppe6_I20TRCNPRDCTCBC",
    "TEAK_ppe6_I20TRCNPRDCTCBC",
    "WREF_ppe6_I20TRCNPRDCTCBC",
    "YELL_ppe6_I20TRCNPRDCTCBC",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop32-artifact", required=True)
    parser.add_argument("--drop21-artifact", required=True)
    parser.add_argument("--summary-root", required=True)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_case(name: str) -> Any:
    path = REPO_ROOT / "pklfiles" / f"{name}.pkl"
    with path.open("rb") as fp:
        return pickle.load(fp)


def _manifest_gate(artifact_path: Path) -> Dict[str, Any]:
    manifest_path = artifact_path.parent / "artifact_manifest.json"
    report_path = artifact_path.parent / "validation_report.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if manifest["artifact_filename"] != artifact_path.name:
        raise ValueError(f"Manifest filename mismatch for {artifact_path}")
    if int(manifest["artifact_size_bytes"]) != artifact_path.stat().st_size:
        raise ValueError(f"Manifest size mismatch for {artifact_path}")
    actual_hash = _sha256(artifact_path)
    if manifest["artifact_sha256"] != actual_hash:
        raise ValueError(f"Manifest hash mismatch for {artifact_path}")
    if not bool(report.get("passed")) or report.get("artifact_sha256") != actual_hash:
        raise ValueError(f"Validation sidecar does not pass/hash-match for {artifact_path}")
    return {
        "artifact": str(artifact_path),
        "artifact_size_bytes": artifact_path.stat().st_size,
        "artifact_sha256": actual_hash,
        "manifest": str(manifest_path),
        "validation_report": str(report_path),
    }


def _fresh_process_gate(path: Path) -> Dict[str, Any]:
    code = (
        "from model_ELM.spinup_surrogate_artifact import "
        "load_spinup_surrogate_artifact,validate_versioned_artifact;"
        f"a,p=load_spinup_surrogate_artifact({str(path)!r},allow_legacy=False);"
        "validate_versioned_artifact(a);"
        "print(a['variant'],a['schema_version'],p)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(
            f"Fresh-process load failed for {path}: stdout={result.stdout!r}, "
            f"stderr={result.stderr!r}"
        )
    return {"returncode": result.returncode, "stdout": result.stdout.strip()}


def _member_prediction(
    artifact: Mapping[str, Any],
    case: Any,
    member: int,
) -> np.ndarray:
    samples = np.asarray(case.samples, dtype=np.float64).transpose()
    components = case_inference_components(
        case, artifact, spinup_case=case, surface_member=member
    )
    X, _ = build_selected_inference_matrix(
        artifact,
        samples[member - 1, :],
        components["surface"],
        components["climatology"],
        artifact["training_layout"]["input_feature_names"],
    )
    pred = predict_versioned_spinup(artifact, X)
    if pred.shape != (1, 2) or pred.dtype != np.float64 or np.any(~np.isfinite(pred)):
        raise ValueError(
            f"Member prediction invariant failed for {case.casename} member {member}: "
            f"shape={pred.shape}, dtype={pred.dtype}"
        )
    return pred


def _empirical_warning_gate(
    artifact: Mapping[str, Any],
    case: Any,
) -> Dict[str, Any]:
    metadata = artifact["parameter_metadata"]
    names = list(metadata["physical_names"])
    aliases = list(metadata["aliases"])
    selected_names = list(artifact["training_layout"]["input_feature_names"])
    ranges = artifact["feature_ranges"]["selected"]
    pmin = np.asarray(metadata["ensemble_pmin"], dtype=np.float64)
    pmax = np.asarray(metadata["ensemble_pmax"], dtype=np.float64)
    midpoint = (pmin + pmax) / 2.0
    chosen = None
    value = None
    for i, alias in enumerate(aliases):
        if alias not in selected_names:
            continue
        lo = float(ranges[alias]["min"])
        hi = float(ranges[alias]["max"])
        if pmin[i] < lo:
            chosen, value = i, float(pmin[i])
            break
        if pmax[i] > hi:
            chosen, value = i, float(pmax[i])
            break
    if chosen is None:
        raise ValueError("Unable to construct in-bounds empirical-range warning")
    midpoint[chosen] = value
    components = case_inference_components(case, artifact, spinup_case=case)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        X, messages = build_selected_inference_matrix(
            artifact,
            midpoint,
            components["surface"],
            components["climatology"],
            selected_names,
        )
    if not messages or not caught:
        raise ValueError("Expected empirical-range warning was not emitted")
    predict_versioned_spinup(artifact, X)
    return {
        "parameter": names[chosen],
        "alias": aliases[chosen],
        "value": value,
        "messages": list(messages),
    }


def _negative_gates(artifact: Mapping[str, Any]) -> Dict[str, bool]:
    required = list(artifact["training_layout"]["input_feature_names"])
    metadata = artifact["parameter_metadata"]
    names = list(metadata["physical_names"])
    pmin = np.asarray(metadata["ensemble_pmin"], dtype=np.float64)
    pmax = np.asarray(metadata["ensemble_pmax"], dtype=np.float64)
    midpoint = (pmin + pmax) / 2.0
    results: Dict[str, bool] = {}

    feature_cases = {
        "feature_order": list(reversed(required)),
        "feature_missing": required[:-1],
        "feature_extra": required + ["not_a_feature"],
        "feature_duplicate": [required[0]] + required,
    }
    for label, supplied in feature_cases.items():
        try:
            require_exact_feature_order(supplied, required)
        except ValueError as exc:
            text = str(exc)
            results[label] = all(
                token in text
                for token in (
                    "supplied=",
                    "required=",
                    "first_mismatch=",
                    "missing=",
                    "unexpected=",
                    "correct --feature-subset value=",
                )
            )
        else:
            results[label] = False

    named = dict(zip(names, midpoint.tolist()))
    missing = dict(named)
    missing.pop(names[0])
    try:
        normalize_physical_parameters(artifact, missing)
    except ValueError:
        results["missing_parameter"] = True
    else:
        results["missing_parameter"] = False

    extra = dict(named)
    extra["not_a_parameter"] = 1.0
    try:
        normalize_physical_parameters(artifact, extra)
    except ValueError:
        results["extra_parameter"] = True
    else:
        results["extra_parameter"] = False

    duplicate_json = (
        "{"
        + f"{json.dumps(names[0])}: 0.0, {json.dumps(names[0])}: 1.0"
        + "}"
    )
    try:
        parse_physical_parameter_json(duplicate_json)
    except ValueError:
        results["duplicate_parameter"] = True
    else:
        results["duplicate_parameter"] = False

    outside = midpoint.copy()
    outside[0] = pmax[0] + max(1.0, abs(pmax[0]) * 0.1)
    try:
        normalize_physical_parameters(artifact, outside)
    except ValueError:
        results["parameter_bounds"] = True
    else:
        results["parameter_bounds"] = False

    broken = dict(artifact)
    broken["schema_version"] = "unsupported"
    try:
        validate_versioned_artifact(broken)
    except ValueError:
        results["schema"] = True
    else:
        results["schema"] = False
    if not all(results.values()):
        raise ValueError(f"Negative validation gate failed: {results}")
    return results


def _operational_gates(
    artifact: Mapping[str, Any],
    cases: Mapping[str, Any],
) -> Dict[str, Any]:
    per_case = {}
    for name in CASE_NAMES:
        pred = _member_prediction(artifact, cases[name], 1)
        per_case[name] = pred.reshape(-1).tolist()
    abby = cases[CASE_NAMES[0]]
    abby_samples = np.asarray(abby.samples, dtype=np.float64).transpose()
    batch_members = (1, 2, 3, 4)
    batch_components = [
        case_inference_components(
            abby, artifact, spinup_case=abby, surface_member=member
        )
        for member in batch_members
    ]
    batch_X, _ = build_selected_inference_matrix(
        artifact,
        abby_samples[[member - 1 for member in batch_members], :],
        np.vstack([component["surface"] for component in batch_components]),
        np.vstack([component["climatology"] for component in batch_components]),
        artifact["training_layout"]["input_feature_names"],
    )
    abby_batch = predict_versioned_spinup(artifact, batch_X)
    if abby_batch.shape != (4, 2):
        raise ValueError(f"True ABBY batch inference shape mismatch: {abby_batch.shape}")
    metadata = artifact["parameter_metadata"]
    pmin = np.asarray(metadata["ensemble_pmin"], dtype=np.float64)
    pmax = np.asarray(metadata["ensemble_pmax"], dtype=np.float64)
    midpoint = (pmin + pmax) / 2.0
    named = dict(zip(metadata["physical_names"], midpoint.tolist()))
    components = case_inference_components(abby, artifact, spinup_case=abby)
    selected_names = artifact["training_layout"]["input_feature_names"]
    X_pos, _ = build_selected_inference_matrix(
        artifact,
        midpoint,
        components["surface"],
        components["climatology"],
        selected_names,
    )
    X_named, _ = build_selected_inference_matrix(
        artifact,
        named,
        components["surface"],
        components["climatology"],
        selected_names,
    )
    pred_pos = predict_versioned_spinup(artifact, X_pos)
    pred_named = predict_versioned_spinup(artifact, X_named)
    if not np.array_equal(X_pos, X_named) or not np.array_equal(pred_pos, pred_named):
        raise ValueError("Named and positional midpoint inference are not identical")
    empirical = _empirical_warning_gate(artifact, abby)
    negative = _negative_gates(artifact)
    return {
        "one_member_each_training_case": per_case,
        "abby_members_1_4_batch_single_call": True,
        "abby_members_1_4_batch_shape": list(abby_batch.shape),
        "abby_members_1_4_predictions": abby_batch.tolist(),
        "midpoint_named_positional_identical": True,
        "midpoint_prediction": pred_pos.reshape(-1).tolist(),
        "empirical_range_warning": empirical,
        "negative_gates": negative,
    }


def _bridge_gate(
    artifact: Mapping[str, Any],
    midpoint_prediction: List[float],
) -> Dict[str, Any]:
    n_params = len(artifact["parameter_metadata"]["physical_names"])
    midpoint = (
        np.asarray(artifact["parameter_metadata"]["ensemble_pmin"], dtype=np.float64)
        + np.asarray(artifact["parameter_metadata"]["ensemble_pmax"], dtype=np.float64)
    ) / 2.0
    forcing = np.arange(15, dtype=np.float64).reshape(3, 5)
    spinup = np.asarray(midpoint_prediction, dtype=np.float64)
    future_layout = {"n_forcing_cols": 5, "n_params": n_params, "n_spinup": 2}
    X = compose_forcing_surrogate_design_matrix(
        forcing, midpoint, spinup, future_layout
    )
    if X.shape != (3, 5 + n_params + 2) or X.dtype != np.float64:
        raise ValueError(f"Forcing bridge shape/dtype mismatch: {X.shape}, {X.dtype}")
    if not np.array_equal(X[:, :5], forcing):
        raise ValueError("Forcing bridge forcing segment mismatch")
    if not np.array_equal(X[:, 5 : 5 + n_params], np.tile(midpoint, (3, 1))):
        raise ValueError("Forcing bridge parameter segment mismatch")
    if not np.array_equal(X[:, -2:], np.tile(spinup, (3, 1))):
        raise ValueError("Forcing bridge spinup segment/order mismatch")
    return {
        "passed": True,
        "interface": "[engineered forcing | parameters | spinup]",
        "ordered_spinup_targets": ["TOTSOMC", "TOTSOMN"],
        "shape": list(X.shape),
        "dtype": str(X.dtype),
        "forcing_columns": 5,
        "parameter_columns": n_params,
        "spinup_columns": 2,
        "scope": (
            "design-matrix compatibility only; no forcing artifact exists, no forcing model "
            "was trained, and no real SR/flux prediction was made"
        ),
    }


def main() -> int:
    args = _parser().parse_args()
    artifact_args = {
        "drop32": Path(args.drop32_artifact).resolve(),
        "drop21_corr080": Path(args.drop21_artifact).resolve(),
    }
    summary_root = Path(args.summary_root).resolve()
    summary_root.mkdir(parents=True, exist_ok=True)
    cases = {name: _load_case(name) for name in CASE_NAMES}
    decision: Dict[str, Any] = {
        "iteration": "iter012",
        "passed": True,
        "release_decision": (
            "release both user-accepted versions; drop32 is recommended for accuracy and "
            "drop21_corr080 is the compact tradeoff with Iter011 gate failures preserved"
        ),
        "variants": {},
    }
    midpoint_predictions = {}
    for variant in VARIANTS:
        artifact, resolved = load_spinup_surrogate_artifact(
            artifact_args[variant], allow_legacy=False
        )
        if resolved != artifact_args[variant] or artifact["variant"] != variant:
            raise ValueError(f"Artifact identity mismatch for {variant}")
        manifest_gate = _manifest_gate(resolved)
        fresh_process = _fresh_process_gate(resolved)
        operational = _operational_gates(artifact, cases)
        midpoint_predictions[variant] = operational["midpoint_prediction"]
        decision["variants"][variant] = {
            "manifest_gate": manifest_gate,
            "fresh_process_gate": fresh_process,
            "operational_gates": operational,
            "passed": True,
        }
        for source_name, target_name in (
            ("artifact_manifest.json", f"{variant}_artifact_manifest.json"),
            ("validation_report.json", f"{variant}_validation_report.json"),
        ):
            source = resolved.parent / source_name
            target = summary_root / target_name
            shutil.copy2(source, target)
            if source.read_bytes() != target.read_bytes():
                raise ValueError(f"Tracked evidence copy is not byte-identical: {target}")
    bridge = {
        variant: _bridge_gate(
            load_spinup_surrogate_artifact(artifact_args[variant], allow_legacy=False)[0],
            midpoint_predictions[variant],
        )
        for variant in VARIANTS
    }
    decision["forcing_bridge"] = bridge
    (summary_root / "iter012_forcing_bridge_validation.json").write_text(
        json.dumps(bridge, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    decision_path = summary_root / "iter012_release_decision.json"
    decision_path.write_text(
        json.dumps(decision, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        f"ITER012_CROSS_VALIDATION_OK variants={','.join(VARIANTS)} "
        f"decision={decision_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
