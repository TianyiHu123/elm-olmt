"""Pure invariants for the Iter009 sampler geometry contract."""
from __future__ import annotations

import numpy as np
import pytest
import importlib

from model_ELM.mcmc_geometry import CoordinateTransform


def _transform():
    return CoordinateTransform.from_parameters(
        ["k_l1", "rf_leaf", "parm_0", "sigma_SR"],
        [0.01, 0.0, -1.0, 0.0],
        [10.0, 1.0, 1.0, 5.0],
        enabled=True,
    )


def test_round_trip_preserves_strict_physical_coordinates():
    transform = _transform()
    physical = np.array([[0.1, 0.2, 0.0, 1.0], [2.0, 0.8, 0.7, 3.0]])
    recovered = transform.sampler_to_physical(transform.physical_to_sampler(physical))
    assert np.allclose(recovered, physical, rtol=0, atol=1e-12)
    assert transform.metadata()["transform_kinds"] == ["log", "logit", "physical", "logit"]


def test_logit_jacobian_matches_finite_difference():
    transform = _transform()
    sampler = transform.physical_to_sampler(np.array([[0.2, 0.3, 0.1, 2.0]]))[0]
    eps = 1.0e-6
    numerical = []
    for i in range(sampler.size):
        plus = sampler.copy(); plus[i] += eps
        minus = sampler.copy(); minus[i] -= eps
        numerical.append(np.log(abs((transform.sampler_to_physical(plus)[i] - transform.sampler_to_physical(minus)[i]) / (2 * eps))))
    expected = transform.log_abs_det_dphysical_dsampler(sampler)
    assert np.isclose(sum(numerical), expected, rtol=0, atol=1e-6)


def test_invalid_coordinates_are_not_silently_clipped():
    transform = _transform()
    with pytest.raises(ValueError, match="strictly within bounds"):
        transform.physical_to_sampler(np.array([0.01, 0.2, 0.0, 1.0]))
    with pytest.raises(ValueError, match="finite"):
        transform.sampler_to_physical(np.array([np.nan, 0.0, 0.0, 0.0]))


def test_real_sampler_target_recovers_physical_target_after_jacobian(monkeypatch):
    forcing_module = importlib.import_module("model_ELM.MCMC_forcing")
    transform = _transform()
    physical = np.array([0.2, 0.3, 0.1, 2.0])
    sampler = transform.physical_to_sampler(physical)
    monkeypatch.setattr(
        forcing_module,
        "log_posterior_forcing",
        lambda values: -float(np.dot(values, values)),
    )
    monkeypatch.setattr(forcing_module, "_WORKER_STATE", {"coordinate_transform": transform})
    physical_log_target = forcing_module.log_posterior_forcing(physical)
    sampler_log_target = forcing_module.log_posterior_forcing_sampler(sampler)
    assert np.isclose(
        sampler_log_target - transform.log_abs_det_dphysical_dsampler(sampler),
        physical_log_target,
    )
