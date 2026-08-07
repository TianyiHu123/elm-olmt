"""Coupled spinup→forcing surrogate primitive (MCMC-ready)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Union

import numpy as np

from .forcing_surrogate_artifact import (
    load_forcing_surrogate_artifact,
    predict_versioned_forcing,
)
from .spinup_surrogate_artifact import (
    build_selected_inference_matrix,
    case_inference_components,
    load_spinup_surrogate_artifact,
    normalize_physical_parameters,
    predict_versioned_spinup,
)
from .surrogate_NN_Forcing import (
    DEFAULT_SPINUP_VARS,
    _spinup_state,
    build_forcing_inference_inputs,
    compose_forcing_surrogate_design_matrix,
)


def load_elm_sr_member(case: Any, member: int, ntime: int) -> np.ndarray:
    if "SR" not in getattr(case, "output", {}):
        raise KeyError(f"SR not in case.output for {getattr(case, 'casename', case)}")
    yfull = np.asarray(case.output["SR"]).transpose()
    if member < 1 or member > yfull.shape[0]:
        raise ValueError(f"member {member} outside 1..{yfull.shape[0]}")
    if ntime <= 0 or ntime > yfull.shape[1]:
        raise ValueError(f"ntime={ntime} invalid for ELM SR width {yfull.shape[1]}")
    series = yfull[member - 1, :ntime].astype(np.float64)
    if np.any(~np.isfinite(series)):
        raise ValueError(f"Non-finite ELM SR for member {member}")
    return series


def load_elm_spinup_member(case: Any, member: int) -> np.ndarray:
    return np.asarray(
        _spinup_state(case, int(member), DEFAULT_SPINUP_VARS), dtype=np.float64
    ).ravel()


def metric_r2(obs: np.ndarray, pred: np.ndarray) -> float:
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - np.mean(obs)) ** 2))
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return 1.0 - ss_res / ss_tot


def metric_rmse(obs: np.ndarray, pred: np.ndarray) -> float:
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    return float(np.sqrt(np.mean((obs - pred) ** 2)))


def metric_bias(obs: np.ndarray, pred: np.ndarray) -> float:
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    return float(np.mean(pred - obs))


def metric_mae(obs: np.ndarray, pred: np.ndarray) -> float:
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    return float(np.mean(np.abs(pred - obs)))


def metric_pearson_r(obs: np.ndarray, pred: np.ndarray) -> float:
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    if obs.size < 2:
        return float("nan")
    if np.std(obs) == 0.0 or np.std(pred) == 0.0:
        return float("nan")
    return float(np.corrcoef(obs, pred)[0, 1])


def metric_kge(obs: np.ndarray, pred: np.ndarray) -> float:
    """Kling-Gupta Efficiency (2009): 1 - sqrt((r-1)^2 + (alpha-1)^2 + (beta-1)^2)."""
    obs = np.asarray(obs, dtype=np.float64).ravel()
    pred = np.asarray(pred, dtype=np.float64).ravel()
    if obs.size < 2:
        return float("nan")
    r = metric_pearson_r(obs, pred)
    mean_o = float(np.mean(obs))
    mean_p = float(np.mean(pred))
    std_o = float(np.std(obs, ddof=0))
    std_p = float(np.std(pred, ddof=0))
    if not np.isfinite(r) or mean_o == 0.0 or std_o == 0.0:
        return float("nan")
    alpha = std_p / std_o
    beta = mean_p / mean_o
    return float(1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2))


def compute_sr_metrics(obs: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    return {
        "r2": metric_r2(obs, pred),
        "rmse": metric_rmse(obs, pred),
        "bias": metric_bias(obs, pred),
        "mae": metric_mae(obs, pred),
        "pearson_r": metric_pearson_r(obs, pred),
        "kge": metric_kge(obs, pred),
    }


def _resolve_spinup_artifact(
    spinup_artifact: Union[str, Path, Mapping[str, Any]],
) -> tuple[Mapping[str, Any], Optional[Path]]:
    if isinstance(spinup_artifact, Mapping):
        return spinup_artifact, None
    artifact, path = load_spinup_surrogate_artifact(spinup_artifact, allow_legacy=False)
    return artifact, path


def _resolve_forcing_artifact(
    forcing_artifact: Union[str, Path, Mapping[str, Any]],
) -> tuple[Mapping[str, Any], Optional[Path]]:
    if isinstance(forcing_artifact, Mapping):
        return forcing_artifact, None
    artifact, path = load_forcing_surrogate_artifact(forcing_artifact, allow_legacy=False)
    return artifact, path


def predict_coupled_sr(
    case: Any,
    *,
    spinup_artifact: Union[str, Path, Mapping[str, Any]],
    forcing_artifact: Union[str, Path, Mapping[str, Any]],
    parameters: Optional[Union[Sequence[float], Mapping[str, float], np.ndarray]] = None,
    member: Optional[int] = None,
    spinup_case: Optional[Any] = None,
    surface_member: Optional[int] = None,
) -> Dict[str, Any]:
    """Predict spinup state then SR through the coupled forcing bridge.

    Exactly one of ``member`` (1-based PPE index) or ``parameters`` must be supplied.
    Predicted TOTSOMC/TOTSOMN replace ELM restart spinup in the forcing design matrix.
    """
    if (member is None) == (parameters is None):
        raise ValueError("Provide exactly one of member= or parameters=")

    spinup_art, spinup_path = _resolve_spinup_artifact(spinup_artifact)
    forcing_art, forcing_path = _resolve_forcing_artifact(forcing_artifact)
    feature_subset = list(spinup_art["training_layout"]["input_feature_names"])

    if member is not None:
        member_i = int(member)
        samples = np.asarray(case.samples, dtype=np.float64).transpose()
        if member_i < 1 or member_i > samples.shape[0]:
            raise ValueError(f"member {member_i} outside 1..{samples.shape[0]}")
        params = samples[member_i - 1, :]
        surf_member = member_i if surface_member is None else int(surface_member)
    else:
        member_i = None
        params = normalize_physical_parameters(spinup_art, parameters).reshape(-1)
        surf_member = None if surface_member is None else int(surface_member)

    components = case_inference_components(
        case,
        spinup_art,
        spinup_case=spinup_case if spinup_case is not None else case,
        surface_member=surf_member,
    )
    X_spinup, warnings = build_selected_inference_matrix(
        spinup_art,
        params,
        components["surface"],
        components["climatology"],
        feature_subset,
    )
    spinup_pred = predict_versioned_spinup(spinup_art, X_spinup).reshape(-1)
    if spinup_pred.size != 2:
        raise ValueError(f"Expected 2 spinup targets, got shape {spinup_pred.shape}")

    forcing_layout = dict(forcing_art["training_layout"])
    forcing_inputs = build_forcing_inference_inputs(case, forcing_layout)
    # Critical: use predicted spinup, not forcing_inputs["spinup"] (ELM restart).
    X_forcing = compose_forcing_surrogate_design_matrix(
        forcing_inputs["forcing_engineered"],
        params,
        spinup_pred,
        forcing_layout,
    )
    sr_pred = predict_versioned_forcing(forcing_art, X_forcing)[:, 0]
    ntime = int(forcing_inputs["ntime"])
    if sr_pred.shape[0] != ntime:
        raise ValueError(
            f"SR length {sr_pred.shape[0]} does not match forcing ntime {ntime}"
        )

    return {
        "TOTSOMC": float(spinup_pred[0]),
        "TOTSOMN": float(spinup_pred[1]),
        "SR": np.asarray(sr_pred, dtype=np.float64),
        "time": forcing_inputs["forcing_time"],
        "ntime": ntime,
        "forcing_time_source": forcing_inputs.get("forcing_time_source"),
        "spinup_warnings": list(warnings),
        "member": member_i,
        "parameters": np.asarray(params, dtype=np.float64),
        "spinup_artifact_path": None if spinup_path is None else str(spinup_path),
        "forcing_artifact_path": None if forcing_path is None else str(forcing_path),
        "spinup_variant": spinup_art.get("variant"),
        "feature_subset": feature_subset,
        "spinup_source": "predicted",
    }


def predict_offline_sr(
    case: Any,
    *,
    forcing_artifact: Union[str, Path, Mapping[str, Any]],
    parameters: Optional[Union[Sequence[float], Mapping[str, float], np.ndarray]] = None,
    member: Optional[int] = None,
) -> Dict[str, Any]:
    """Predict SR with forcing-surrogate-v1 using ELM restart spinup (offline arm).

    Exactly one of ``member`` (1-based PPE index) or ``parameters`` must be supplied.
    When ``member`` is set, ELM restart TOTSOMC/TOTSOMN for that member enter the design
    matrix. When ``parameters`` is set without a member, mean ELM restart spinup is used.
    """
    if (member is None) == (parameters is None):
        raise ValueError("Provide exactly one of member= or parameters=")

    forcing_art, forcing_path = _resolve_forcing_artifact(forcing_artifact)
    forcing_layout = dict(forcing_art["training_layout"])

    if member is not None:
        member_i = int(member)
        samples = np.asarray(case.samples, dtype=np.float64).transpose()
        if member_i < 1 or member_i > samples.shape[0]:
            raise ValueError(f"member {member_i} outside 1..{samples.shape[0]}")
        params = samples[member_i - 1, :]
        forcing_inputs = build_forcing_inference_inputs(
            case, forcing_layout, spinup_member=member_i
        )
    else:
        member_i = None
        # Offline parameter mode still needs a parameter vector length match; reuse
        # coupled normalizer only when a spinup artifact is unavailable by reading
        # n_params from the forcing layout.
        n_params = int(forcing_layout.get("n_params", -1))
        params = np.asarray(parameters, dtype=np.float64).reshape(-1)
        if n_params > 0 and params.size != n_params:
            raise ValueError(f"Expected {n_params} parameters, got {params.size}")
        forcing_inputs = build_forcing_inference_inputs(case, forcing_layout)

    spinup_elm = np.asarray(forcing_inputs["spinup"], dtype=np.float64).ravel()
    if spinup_elm.size != 2:
        raise ValueError(f"Expected 2 ELM spinup values, got shape {spinup_elm.shape}")

    X_forcing = compose_forcing_surrogate_design_matrix(
        forcing_inputs["forcing_engineered"],
        params,
        spinup_elm,
        forcing_layout,
    )
    sr_pred = predict_versioned_forcing(forcing_art, X_forcing)[:, 0]
    ntime = int(forcing_inputs["ntime"])
    if sr_pred.shape[0] != ntime:
        raise ValueError(
            f"SR length {sr_pred.shape[0]} does not match forcing ntime {ntime}"
        )

    return {
        "TOTSOMC": float(spinup_elm[0]),
        "TOTSOMN": float(spinup_elm[1]),
        "SR": np.asarray(sr_pred, dtype=np.float64),
        "time": forcing_inputs["forcing_time"],
        "ntime": ntime,
        "forcing_time_source": forcing_inputs.get("forcing_time_source"),
        "spinup_warnings": [],
        "member": member_i,
        "parameters": np.asarray(params, dtype=np.float64),
        "spinup_artifact_path": None,
        "forcing_artifact_path": None if forcing_path is None else str(forcing_path),
        "spinup_variant": None,
        "feature_subset": None,
        "spinup_source": "elm_restart",
    }
