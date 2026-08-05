#!/usr/bin/env python
"""Fresh-process operational validation for the Iter002 forcing-surrogate release."""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402,F401
from model_ELM.forcing_surrogate_artifact import (  # noqa: E402
    load_forcing_surrogate_artifact,
    predict_versioned_forcing,
    require_exact_feature_order,
    validate_versioned_forcing_artifact,
)
from model_ELM.surrogate_NN_Forcing import (  # noqa: E402
    _load_forcing_layout_dict,
    _resolve_forcing_memmap_paths,
    build_forcing_inference_inputs,
    compose_forcing_surrogate_design_matrix,
)

ABBY_CASE = "ABBY_ppe6_I20TRCNPRDCTCBC"
PARAM_DRAW_SEED = 10001


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--reuse-x-memmap", required=True)
    parser.add_argument("--importance-json", required=True)
    parser.add_argument("--summary-root", required=True)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_dtype(dtype_str: str) -> np.dtype:
    text = str(dtype_str).strip()
    if text in {"float32", "np.float32", "<class 'numpy.float32'>", "numpy.float32"}:
        return np.dtype(np.float32)
    if text in {"float64", "np.float64", "<class 'numpy.float64'>", "numpy.float64"}:
        return np.dtype(np.float64)
    return np.dtype(text)


def _manifest_gate(artifact_path: Path) -> Dict[str, Any]:
    manifest_path = artifact_path.parent / "artifact_manifest.json"
    report_path = artifact_path.parent / "validation_report.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if manifest["artifact_filename"] != artifact_path.name:
        raise ValueError("Manifest filename mismatch")
    if int(manifest["artifact_size_bytes"]) != artifact_path.stat().st_size:
        raise ValueError("Manifest size mismatch")
    actual_hash = _sha256(artifact_path)
    if manifest["artifact_sha256"] != actual_hash:
        raise ValueError("Manifest hash mismatch")
    if not bool(report.get("passed")) or report.get("artifact_sha256") != actual_hash:
        raise ValueError("Validation sidecar does not pass/hash-match")
    return {
        "artifact_sha256": actual_hash,
        "manifest": str(manifest_path),
        "validation_report": str(report_path),
    }


def _fresh_process_gate(path: Path) -> Dict[str, Any]:
    code = (
        "from model_ELM.forcing_surrogate_artifact import "
        "load_forcing_surrogate_artifact,validate_versioned_forcing_artifact;"
        f"a,p=load_forcing_surrogate_artifact({str(path)!r},allow_legacy=False);"
        "validate_versioned_forcing_artifact(a);"
        "print(a['release_version'],a['schema_version'],p)"
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
            f"Fresh-process load failed: stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    return {"returncode": result.returncode, "stdout": result.stdout.strip()}


def _negative_gates(artifact: Mapping[str, Any]) -> Dict[str, bool]:
    """Fail-closed checks: invalid inputs must raise, not succeed."""
    results: Dict[str, bool] = {}
    bad = dict(artifact)
    bad["schema_version"] = "not-a-real-schema"
    try:
        validate_versioned_forcing_artifact(bad)
        results["bad_schema"] = False
    except ValueError:
        results["bad_schema"] = True

    required = list(artifact["training_layout"]["ordered_feature_names"])
    try:
        require_exact_feature_order(required[1:] + required[:1], required)
        results["feature_order"] = False
    except ValueError:
        results["feature_order"] = True

    X = np.zeros((2, len(required) + 1), dtype=np.float64)
    try:
        predict_versioned_forcing(artifact, X)
        results["feature_width"] = False
    except ValueError:
        results["feature_width"] = True

    with tempfile.TemporaryDirectory() as tmp:
        legacy = Path(tmp) / "surrogate_forcing_artifacts.pkl"
        with legacy.open("wb") as fp:
            pickle.dump(
                {
                    "models": artifact["models"],
                    "x_scaler": artifact["x_scaler"],
                    "y_scaler": artifact["y_scaler"],
                    "training_layout": artifact["training_layout"],
                },
                fp,
            )
        try:
            load_forcing_surrogate_artifact(legacy, allow_legacy=False)
            results["legacy_reject"] = False
        except ValueError:
            results["legacy_reject"] = True

    if not all(results.values()):
        raise ValueError(f"Negative gates failed: {results}")
    return results


def _abby_operational_predict(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    case_path = REPO_ROOT / "pklfiles" / f"{ABBY_CASE}.pkl"
    with case_path.open("rb") as fp:
        case = pickle.load(fp)
    metadata = artifact["parameter_metadata"]
    pmin = np.asarray(metadata["ensemble_pmin"], dtype=np.float64)
    pmax = np.asarray(metadata["ensemble_pmax"], dtype=np.float64)
    rng = np.random.default_rng(PARAM_DRAW_SEED)
    params = rng.uniform(pmin, pmax)
    if np.any(params < pmin) or np.any(params > pmax) or np.any(~np.isfinite(params)):
        raise ValueError("Random parameter draw left bounds or produced non-finite values")

    components = build_forcing_inference_inputs(
        case,
        dict(artifact["training_layout"]),
        spinup_member=1,
    )
    X = compose_forcing_surrogate_design_matrix(
        components["forcing_engineered"],
        params,
        components["spinup"],
        artifact["training_layout"],
    )
    pred = predict_versioned_forcing(artifact, X)
    expected_rows = int(components["ntime"])
    if pred.shape != (expected_rows, 1) or np.any(~np.isfinite(pred)):
        raise ValueError(
            f"ABBY operational predict failed: shape={pred.shape}, "
            f"finite={bool(np.all(np.isfinite(pred)))}"
        )
    return {
        "case": ABBY_CASE,
        "spinup_member": 1,
        "parameter_draw_seed": PARAM_DRAW_SEED,
        "n_params": int(params.size),
        "n_rows": expected_rows,
        "prediction_shape": list(pred.shape),
        "prediction_finite": True,
        "prediction_sha256": hashlib.sha256(pred.tobytes()).hexdigest(),
        "parameter_sha256": hashlib.sha256(params.astype(np.float64).tobytes()).hexdigest(),
    }


def main() -> int:
    args = _parser().parse_args()
    artifact_path = Path(args.artifact).resolve()
    manifest_info = _manifest_gate(artifact_path)
    fresh = _fresh_process_gate(artifact_path)
    artifact, _ = load_forcing_surrogate_artifact(artifact_path, allow_legacy=False)
    validate_versioned_forcing_artifact(artifact)

    memmap_path, layout_path = _resolve_forcing_memmap_paths(Path(args.reuse_x_memmap))
    layout = _load_forcing_layout_dict(layout_path)
    dtype_np = _normalize_dtype(layout["dtype_str"])
    X = np.memmap(
        memmap_path,
        mode="r",
        dtype=dtype_np,
        shape=(int(layout["rows"]), int(layout["nfeatures"])),
    )
    sample = np.asarray(X[:64, :], dtype=np.float64)
    pred = predict_versioned_forcing(artifact, sample)
    if pred.shape != (64, 1) or np.any(~np.isfinite(pred)):
        raise ValueError(f"Batch inference invariant failed: shape={pred.shape}")

    importance_path = Path(args.importance_json).resolve()
    importance = json.loads(importance_path.read_text(encoding="utf-8"))
    require_exact_feature_order(
        importance.get("ordered_feature_names", []),
        artifact["training_layout"]["ordered_feature_names"],
    )
    negatives = _negative_gates(artifact)
    abby = _abby_operational_predict(artifact)

    summary_root = Path(args.summary_root).resolve()
    summary_root.mkdir(parents=True, exist_ok=True)
    decision = {
        "schema": "spinup-forcing-coupling-iter002-validate-v1",
        "passed": True,
        "manifest": manifest_info,
        "fresh_process": fresh,
        "batch_inference": {
            "rows": 64,
            "shape": list(pred.shape),
            "prediction_sha256": hashlib.sha256(pred.tobytes()).hexdigest(),
        },
        "negative_gates": negatives,
        "abby_operational_predict": abby,
        "importance_json": str(importance_path),
        "importance_json_sha256": _sha256(importance_path),
        "artifact_sha256": manifest_info["artifact_sha256"],
    }
    out = summary_root / "iter002_inference_validation.json"
    out.write_text(json.dumps(decision, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        f"ITER002_VALIDATE_OK artifact={artifact_path} "
        f"sha256={manifest_info['artifact_sha256']} summary={out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
