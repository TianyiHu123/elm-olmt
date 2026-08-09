"""Pure tests for the locked Iter008 raw-chain selection contract."""
from __future__ import annotations

import json

import numpy as np

from model_ELM.MCMC_forcing import _adaptive_chain_selection, _write_iter008_raw_chain


def test_selection_falls_back_to_every_eligible_draw_when_short(tmp_path):
    chain = np.zeros((20, 4, 2), dtype=float)
    chain[:, :, 0] = np.arange(20)[:, None]
    log_prob = np.zeros((20, 4), dtype=float)
    result = _adaptive_chain_selection(
        chain=chain,
        log_prob=log_prob,
        pmin=np.array([-1.0, -1.0]),
        pmax=np.array([100.0, 1.0]),
        n_model_parms=2,
        nsteps=20,
        tau_max=None,
    )
    assert result["discard"] == 4
    assert result["thin"] == 5
    assert result["predictive_samples"].shape[0] == result["samples"].shape[0]
    assert len(result["selected_ledger"]) == result["samples"].shape[0]


def test_raw_chain_metadata_and_hashes_are_self_describing(tmp_path):
    chain = np.zeros((20, 4, 2), dtype=float)
    log_prob = np.zeros((20, 4), dtype=float)
    metadata = _write_iter008_raw_chain(
        tmp_path,
        chain=chain,
        log_prob=log_prob,
        initial_state=chain[0],
        parameter_names=["p0", "p1"],
        pmin=np.array([-1.0, -1.0]),
        pmax=np.array([1.0, 1.0]),
        seed=8008,
        sites=["ABBY"],
        nwalkers=4,
        nsteps=20,
    )
    assert metadata["seed"] == 8008
    assert json.loads((tmp_path / "raw_chain_metadata.json").read_text())["chain_shape"] == [20, 4, 2]
    assert json.loads((tmp_path / "raw_chain_hashes.json").read_text())["raw_chain_sha256"]
