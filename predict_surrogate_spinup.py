#!/usr/bin/env python
"""Strict inference CLI for versioned spinup-surrogate release artifacts."""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from model_ELM.spinup_surrogate_artifact import (
    build_selected_inference_matrix,
    case_inference_components,
    load_spinup_surrogate_artifact,
    normalize_physical_parameters,
    parse_physical_parameter_json,
    predict_versioned_spinup,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--case", required=True)
    parser.add_argument("--spinup-case", default=None)
    parser.add_argument("--artifact", required=True)
    parser.add_argument(
        "--feature-subset",
        required=True,
        help="Exact comma-separated selected-feature order stored by the artifact",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--members", help="Comma-separated one-based existing case member IDs")
    mode.add_argument(
        "--parameters",
        help="Comma-separated positional values in artifact physical-parameter order",
    )
    mode.add_argument(
        "--parameters-json",
        help="JSON object/path with exact physical names, or JSON list/list-of-lists",
    )
    parser.add_argument(
        "--surface-member",
        type=int,
        default=None,
        help="Surface member for new parameters; default uses the case-member mean",
    )
    parser.add_argument("--output-json", default=None)
    return parser


def _load_case(workdir: Path, name: str) -> Any:
    import model_ELM  # noqa: F401 - register ELMcase for trusted case pickle

    path = workdir / "pklfiles" / f"{name}.pkl"
    if not path.is_file():
        raise FileNotFoundError(f"Case pickle not found: {path}")
    with path.open("rb") as fp:
        return pickle.load(fp)


def _parse_json_argument(raw: str) -> Any:
    path = Path(raw).expanduser()
    if path.is_file():
        return parse_physical_parameter_json(path.read_text(encoding="utf-8"))
    return parse_physical_parameter_json(raw)


def _prediction_record(
    artifact: Mapping[str, Any],
    parameters: Any,
    components: Mapping[str, Any],
    feature_subset: list[str],
) -> tuple[np.ndarray, list[str]]:
    X, warning_messages = build_selected_inference_matrix(
        artifact,
        parameters,
        components["surface"],
        components["climatology"],
        feature_subset,
    )
    return predict_versioned_spinup(artifact, X), list(warning_messages)


def main() -> int:
    args = _parser().parse_args()
    workdir = Path(args.workdir).resolve()
    case = _load_case(workdir, args.case)
    spinup_case = _load_case(workdir, args.spinup_case or args.case)
    artifact, artifact_path = load_spinup_surrogate_artifact(
        args.artifact, allow_legacy=False
    )
    feature_subset = [v.strip() for v in args.feature_subset.split(",") if v.strip()]
    predictions = []
    warnings_seen: list[str] = []
    if args.members is not None:
        members = [int(v.strip()) for v in args.members.split(",") if v.strip()]
        if not members or len(set(members)) != len(members):
            raise ValueError("--members must contain unique one-based member IDs")
        samples = np.asarray(case.samples, dtype=np.float64).transpose()
        for member in members:
            if member < 1 or member > samples.shape[0]:
                raise ValueError(
                    f"Member {member} outside valid range 1..{samples.shape[0]}"
                )
            components = case_inference_components(
                case,
                artifact,
                spinup_case=spinup_case,
                surface_member=member,
            )
            pred, messages = _prediction_record(
                artifact, samples[member - 1, :], components, feature_subset
            )
            predictions.append(
                {
                    "member": member,
                    "parameters_physical_order": samples[member - 1, :].tolist(),
                    "prediction": dict(
                        zip(artifact["target_order"], pred.reshape(-1).tolist())
                    ),
                }
            )
            warnings_seen.extend(messages)
        mode = "existing_members"
    else:
        if args.parameters is not None:
            supplied: Any = [
                float(v.strip()) for v in args.parameters.split(",") if v.strip()
            ]
        else:
            supplied = _parse_json_argument(args.parameters_json)
        normalized = normalize_physical_parameters(artifact, supplied)
        components = case_inference_components(
            case,
            artifact,
            spinup_case=spinup_case,
            surface_member=args.surface_member,
        )
        pred, messages = _prediction_record(
            artifact, supplied, components, feature_subset
        )
        for row in range(normalized.shape[0]):
            predictions.append(
                {
                    "row": row,
                    "parameters_physical_order": normalized[row, :].tolist(),
                    "prediction": dict(
                        zip(artifact["target_order"], pred[row, :].tolist())
                    ),
                }
            )
        warnings_seen.extend(messages)
        mode = "new_parameters"
    payload = {
        "artifact": str(artifact_path),
        "release_version": artifact["release_version"],
        "schema_version": artifact["schema_version"],
        "variant": artifact["variant"],
        "case": args.case,
        "spinup_case": args.spinup_case or args.case,
        "mode": mode,
        "target_order": artifact["target_order"],
        "feature_subset": feature_subset,
        "warnings": warnings_seen,
        "predictions": predictions,
    }
    text = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        output_path = Path(args.output_json).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
