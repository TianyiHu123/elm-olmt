#!/usr/bin/env python3
"""Iter006 forensic replay of the frozen, uncorrected Iter005 ABBY fixture.

This intentionally imports baseline repository code. The Slurm wrapper verifies every
baseline source hash before launch; no corrected implementation can impersonate it.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
from decimal import Decimal, localcontext
from pathlib import Path
import sys

REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')
ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
LEGACY = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot')
sys.path.insert(0, str(REPO))
import numpy as np
import emcee
from emcee.state import State
from model_ELM.mcmc_prior import LOG_PARAMETERS
from model_ELM.mcmc_three_stage_sampler import AuditedDEMove, AuditedDESnookerMove, run_sampler_block, random_state_equal
from model_ELM.mcmc_three_stage_artifacts import sha256_file
from model_ELM.mcmc_three_stage_sampler_geometry import _sigmoid

spec = importlib.util.spec_from_file_location('frozen_iter005_driver', ROOT / 'submitted/a/attempt_003/legacy/run_iter005.py')
assert spec is not None and spec.loader is not None
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def tagged(value):
    if isinstance(value, dict):
        return {key: tagged(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [tagged(item) for item in value]
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        if math.isnan(number):
            return {'nonfinite': 'NaN'}
        if math.isinf(number):
            return {'nonfinite': '+Infinity' if number > 0 else '-Infinity'}
        return number
    return value


def durable(row: dict) -> None:
    path = ROOT / 'replay/generated.jsonl'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, 'a', encoding='utf-8') as handle:
        handle.write(json.dumps(tagged(row), allow_nan=False, sort_keys=True) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def capture_propose(self, model, state):
    """Old red-blue sequence with only a pre-target durable observation inserted."""
    nwalkers, ndim = state.coords.shape
    if nwalkers < 2 * ndim and not self.live_dangerously:
        raise RuntimeError('too few walkers')
    self.setup(state.coords)
    accepted = np.zeros(nwalkers, dtype=bool)
    all_inds = np.arange(nwalkers)
    inds = all_inds % self.nsplits
    if self.randomize_split:
        model.random.shuffle(inds)
    for split in range(self.nsplits):
        subset = inds == split
        sets = [state.coords[inds == value] for value in range(self.nsplits)]
        sample = sets[split]
        complement = sets[:split] + sets[split + 1:]
        proposal, factors = self.get_proposal(sample, complement, model.random)
        durable({
            'schema': 'iter006-legacy-generated-v1',
            'source': 'frozen_iter005_uncorrected',
            'global_step': int(self.audit_ledger.current_step),
            'move': self.audit_move_name,
            'split': int(split),
            'walkers': all_inds[subset].tolist(),
            'z': proposal,
            'u': _sigmoid(proposal),
            'factors': factors,
        })
        new_log_probs, new_blobs = model.compute_log_prob_fn(proposal)
        for walker, factor, new_log_prob in zip(all_inds[subset], factors, new_log_probs):
            if factor + new_log_prob - state.log_prob[walker] > np.log(model.random.rand()):
                accepted[walker] = True
        self.audit_ledger.record(
            move=self.audit_move_name, walker_indices=all_inds[subset],
            sampler_coordinates=proposal, log_probabilities=new_log_probs,
            blobs=new_blobs, accepted=accepted,
        )
        state = self.update(state, State(proposal, log_prob=new_log_probs, blobs=new_blobs), accepted, subset)
    return state, accepted


def reference_component(name, low, high, unit):
    # 800 digits also resolves selected near-subnormal unit displacements.
    with localcontext() as context:
        context.prec = 800
        lo = Decimal.from_float(float(low))
        hi = Decimal.from_float(float(high))
        u = Decimal.from_float(float(unit))
        if name in LOG_PARAMETERS:
            value = (lo.ln() + u * (hi / lo).ln()).exp()
        else:
            value = lo + u * (hi - lo)
        return str(value), str(value - lo), str(hi - value)


def fatal_diagnostics(prior, generated):
    row = generated[-1]
    events = []
    for local, z_values in enumerate(row['z']):
        z = np.asarray(z_values, dtype=np.float64)
        if not np.all(np.isfinite(z)):
            continue
        u = _sigmoid(z)
        if np.any((u <= 0) | (u >= 1)):
            continue
        raw = np.asarray(prior.inverse_unit(u), dtype=np.float64)
        for index, name in enumerate(prior.names):
            low = float(prior.lower[index])
            high = float(prior.upper[index])
            interval_type = 'marginal'
            if index == 17:
                low, high = prior.cn_bounds(raw[16])
                low = float(low)
                interval_type = 'conditional_cn'
            value = float(raw[index])
            if not (value < low or value > high):
                continue
            bound = low if value < low else high
            side = 'lower' if value < low else 'upper'
            ulp = abs(math.nextafter(bound, -math.inf if side == 'lower' else math.inf) - bound)
            ref, ref_from_low, ref_from_high = reference_component(name, low, high, u[index])
            events.append({
                'global_step': row['global_step'], 'move': row['move'],
                'split': row['split'], 'walker': row['walkers'][local],
                'parameter': name, 'index': index, 'interval_type': interval_type,
                'side': side, 'z': z.tolist(), 'u': u.tolist(),
                'raw_physical': raw.tolist(), 'raw_value': value,
                'lower': low, 'upper': high, 'bound': bound,
                'absolute_excursion': abs(value-bound),
                'relative_excursion': abs(value-bound)/max(abs(bound), 1e-300),
                'directional_ulp_excursion': abs(value-bound)/ulp,
                'reference_physical': ref, 'reference_minus_lower': ref_from_low,
                'upper_minus_reference': ref_from_high,
                'intermediate': {
                    'log_low': math.log(low) if name in LOG_PARAMETERS else None,
                    'log_high_over_low': math.log(high/low) if name in LOG_PARAMETERS else None,
                    'log_argument': math.log(low)+float(u[index])*math.log(high/low) if name in LOG_PARAMETERS else None,
                    'linear_span': high-low if name not in LOG_PARAMETERS else None,
                    'linear_product': float(u[index])*(high-low) if name not in LOG_PARAMETERS else None,
                },
            })
    return events


def main() -> None:
    config = json.loads((LEGACY / 'submitted/iter005_config.json').read_text())
    assert sha256_file(LEGACY / 'submitted/iter005_config.json') == '4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021'
    assert sha256_file(LEGACY / 'sites/ABBY/walkers/iter005_coordinates.npz') == '572a31c92960bcd88a54eeb12cb7d2ad6d079d6895dbe79c50a2fc3b0cf4cd4e'
    old_ledger = LEGACY / 'sites/ABBY/restart/uninterrupted/proposal_ledger.jsonl'
    old_backend = LEGACY / 'sites/ABBY/restart/uninterrupted/active_backend.h5'
    old_traceback = (LEGACY / 'logs/density_24838627.err').read_text()
    assert 'RuntimeError: prior inverse unit mapping escaped PPE1 marginal bounds' in old_traceback
    old_rows = [json.loads(line) for line in old_ledger.read_text().splitlines()]
    assert len(old_rows) == 128
    old_hdf = emcee.backends.HDFBackend(str(old_backend), read_only=True)
    assert 0 < old_hdf.iteration < 16
    assert len(old_rows) == old_hdf.iteration * 64
    assert set(row['step'] for row in old_rows) == set(range(1, old_hdf.iteration + 1))
    forensic_initial = {
        'ledger_sha256': sha256_file(old_ledger),
        'backend_sha256': sha256_file(old_backend),
        'traceback_sha256': sha256_file(LEGACY / 'logs/density_24838627.err'),
        'old_iteration': old_hdf.iteration,
        'old_rng_state': tagged(old_hdf.get_last_sample().random_state),
        'old_ledger_rows': len(old_rows),
    }
    durable({'schema': 'iter006-legacy-preinspect-v1', **forensic_initial})
    (ROOT / 'results').mkdir(exist_ok=True)
    config['runtime_root'] = str(ROOT)
    old.preflight(config)
    assert json.loads((ROOT / 'results/preflight.json').read_text())['result'] == 'pass'
    frozen = np.load(LEGACY / 'sites/ABBY/walkers/iter005_coordinates.npz')
    z = frozen['sampler']
    assert z.shape == (64, 18)
    identity = json.loads((LEGACY / 'sites/ABBY/restart/uninterrupted/identity.json').read_text())
    identity.pop('schema')
    assert identity['seed'] == 540041
    AuditedDEMove.propose = capture_propose
    AuditedDESnookerMove.propose = capture_propose
    posterior = old.load_posterior(config, 'ABBY')
    status = {'schema': 'iter006-legacy-replay-v1', 'source': 'frozen_iter005_uncorrected', 'maximum_steps': 16}
    try:
        result = run_sampler_block(
            posterior=posterior, initial_sampler_coordinates=z,
            run_directory=ROOT / 'replay/legacy_abby', identity=identity,
            target_iteration=16, checkpoint_interval=8,
        )
    except RuntimeError as exc:
        if str(exc) != 'prior inverse unit mapping escaped PPE1 marginal bounds':
            status.update(result='unexpected_runtime_error', exception=str(exc))
            (ROOT / 'replay/status.json').write_text(json.dumps(status, indent=2, sort_keys=True) + '\n')
            raise
        generated = [json.loads(line) for line in (ROOT / 'replay/generated.jsonl').read_text().splitlines()]
        batches = [row for row in generated if row.get('schema') == 'iter006-legacy-generated-v1']
        events = fatal_diagnostics(posterior.prior, batches)
        replay_ledger = ROOT / 'replay/legacy_abby/proposal_ledger.jsonl'
        replay_hdf = emcee.backends.HDFBackend(str(ROOT / 'replay/legacy_abby/active_backend.h5'), read_only=True)
        exact = (batches[-1]['global_step'] == old_hdf.iteration + 1 and len(events) > 0
                 and sha256_file(replay_ledger) == forensic_initial['ledger_sha256']
                 and replay_hdf.iteration == old_hdf.iteration
                 and np.array_equal(replay_hdf.get_chain(), old_hdf.get_chain())
                 and np.array_equal(replay_hdf.get_log_prob(), old_hdf.get_log_prob())
                 and np.array_equal(replay_hdf.get_blobs(), old_hdf.get_blobs())
                 and random_state_equal(replay_hdf.get_last_sample().random_state,
                                        old_hdf.get_last_sample().random_state))
        status.update(result='exact_replay_reproduced' if exact else 'event_recovered_without_exact_state_replay',
                      exception_type=type(exc).__name__, exception=str(exc),
                      fatal_batch=batches[-1], fatal_events=events,
                      comparison={'ledger_exact': sha256_file(replay_ledger) == forensic_initial['ledger_sha256'],
                                  'hdf_iteration_equal': replay_hdf.iteration == old_hdf.iteration,
                                  'rng_equal': random_state_equal(replay_hdf.get_last_sample().random_state,
                                                                  old_hdf.get_last_sample().random_state)},
                      old_evidence=forensic_initial)
    else:
        status.update(result='sixteen_steps_without_failure', sampler_result=result)
    (ROOT / 'replay/status.json').write_text(json.dumps(status, indent=2, sort_keys=True) + '\n')
    print(json.dumps(status, sort_keys=True))


if __name__ == '__main__':
    main()
