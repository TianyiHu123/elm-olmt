"""Spinup-mode selection for forcing MCMC (mean / member-restart / coupled)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union

import numpy as np

from .coupled_surrogate import predict_coupled_sr, predict_offline_sr

SPINUP_MODES = ("mean_spinup", "member_restart", "coupled")
COUPLED_VARIANTS = ("drop32", "drop21_corr080")
DEFAULT_COUPLED_VARIANT = "drop21_corr080"

DEFAULT_COUPLED_SPINUP_PATHS = {
    "drop32": (
        "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
        "spinup_surrogate_iter012_drop32/surrogate_spinup/"
        "spinup_surrogate_iter012_drop32.pkl"
    ),
    "drop21_corr080": (
        "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
        "spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/"
        "spinup_surrogate_iter012_drop21_corr080.pkl"
    ),
}


def resolve_spinup_mode(
    *,
    spinup_mode: Optional[str],
    spinup_member: Optional[int],
) -> str:
    """Resolve CLI mode with historical defaults.

    - No mode and no member → ``mean_spinup``
    - No mode and member set → ``member_restart`` (legacy ``--spinup-member``)
    - Explicit mode must be one of ``SPINUP_MODES``
    """
    if spinup_mode is None or str(spinup_mode).strip() == "":
        return "member_restart" if spinup_member is not None else "mean_spinup"
    mode = str(spinup_mode).strip()
    if mode not in SPINUP_MODES:
        raise ValueError(
            f"Invalid --spinup-mode={mode!r}; expected one of {SPINUP_MODES}"
        )
    if mode == "mean_spinup" and spinup_member is not None:
        raise ValueError(
            "--spinup-mode=mean_spinup is incompatible with --spinup-member"
        )
    if mode == "member_restart" and spinup_member is None:
        raise ValueError("--spinup-mode=member_restart requires --spinup-member")
    if mode == "coupled" and spinup_member is not None:
        raise ValueError(
            "--spinup-mode=coupled is incompatible with --spinup-member "
            "(parameters drive predicted spinup)"
        )
    return mode


def resolve_coupled_variant(variant: Optional[str]) -> str:
    if variant is None or str(variant).strip() == "":
        return DEFAULT_COUPLED_VARIANT
    name = str(variant).strip()
    if name not in COUPLED_VARIANTS:
        raise ValueError(
            f"Invalid --coupled-spinup-variant={name!r}; expected one of {COUPLED_VARIANTS}"
        )
    return name


def resolve_coupled_spinup_artifact(
    *,
    variant: Optional[str] = None,
    spinup_artifact: Optional[Union[str, Path]] = None,
) -> Path:
    if spinup_artifact is not None and str(spinup_artifact).strip():
        path = Path(spinup_artifact).expanduser().resolve()
    else:
        resolved = resolve_coupled_variant(variant)
        path = Path(DEFAULT_COUPLED_SPINUP_PATHS[resolved]).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Coupled spinup artifact not found: {path}")
    return path


def predict_sr_for_mode(
    case: Any,
    *,
    mode: str,
    forcing_artifact: Union[str, Path, Mapping[str, Any]],
    parameters: Optional[Union[Sequence[float], np.ndarray]] = None,
    spinup_member: Optional[int] = None,
    spinup_artifact: Optional[Union[str, Path, Mapping[str, Any]]] = None,
    coupled_variant: Optional[str] = None,
) -> Dict[str, Any]:
    """Invoke the locked offline/coupled primitive for one MCMC spinup mode."""
    mode_resolved = resolve_spinup_mode(spinup_mode=mode, spinup_member=spinup_member)
    if mode_resolved == "mean_spinup":
        if parameters is None:
            raise ValueError("mean_spinup mode requires parameters=")
        out = predict_offline_sr(
            case, forcing_artifact=forcing_artifact, parameters=parameters
        )
        out["spinup_mode"] = mode_resolved
        return out
    if mode_resolved == "member_restart":
        # Historical MCMC member-restart: fixed member ELM restart spinup with
        # caller-supplied MCMC parameters (not the PPE member parameter vector).
        if parameters is None:
            raise ValueError("member_restart MCMC path requires parameters=")
        if spinup_member is None:
            raise ValueError("member_restart mode requires spinup_member=")
        from .forcing_surrogate_artifact import (
            load_forcing_surrogate_artifact,
            predict_versioned_forcing,
        )
        from .surrogate_NN_Forcing import (
            build_forcing_inference_inputs,
            compose_forcing_surrogate_design_matrix,
        )

        if isinstance(forcing_artifact, Mapping):
            forcing_art = forcing_artifact
            forcing_path = None
        else:
            forcing_art, forcing_path = load_forcing_surrogate_artifact(
                forcing_artifact, allow_legacy=False
            )
        layout = dict(forcing_art["training_layout"])
        finputs = build_forcing_inference_inputs(
            case, layout, spinup_member=int(spinup_member)
        )
        params = np.asarray(parameters, dtype=np.float64).reshape(-1)
        n_params = int(layout.get("n_params", -1))
        if n_params > 0 and params.size != n_params:
            raise ValueError(f"Expected {n_params} parameters, got {params.size}")
        spinup_elm = np.asarray(finputs["spinup"], dtype=np.float64).ravel()
        X = compose_forcing_surrogate_design_matrix(
            finputs["forcing_engineered"], params, spinup_elm, layout
        )
        sr = predict_versioned_forcing(forcing_art, X)[:, 0]
        return {
            "TOTSOMC": float(spinup_elm[0]),
            "TOTSOMN": float(spinup_elm[1]),
            "SR": np.asarray(sr, dtype=np.float64),
            "time": finputs["forcing_time"],
            "ntime": int(finputs["ntime"]),
            "forcing_time_source": finputs.get("forcing_time_source"),
            "spinup_warnings": [],
            "member": int(spinup_member),
            "parameters": params,
            "spinup_artifact_path": None,
            "forcing_artifact_path": None if forcing_path is None else str(forcing_path),
            "spinup_variant": None,
            "feature_subset": None,
            "spinup_source": "elm_restart",
            "spinup_mode": mode_resolved,
        }
    # coupled
    if parameters is None:
        raise ValueError("coupled mode requires parameters=")
    if spinup_artifact is None:
        spinup_artifact = resolve_coupled_spinup_artifact(variant=coupled_variant)
    out = predict_coupled_sr(
        case,
        spinup_artifact=spinup_artifact,
        forcing_artifact=forcing_artifact,
        parameters=parameters,
    )
    out["spinup_mode"] = "coupled"
    if out.get("spinup_variant") is None and coupled_variant is not None:
        out["spinup_variant"] = resolve_coupled_variant(coupled_variant)
    return out
