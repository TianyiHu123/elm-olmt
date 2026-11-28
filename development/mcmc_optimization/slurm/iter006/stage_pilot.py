#!/usr/bin/env python3
"""One fresh 128-step Iter006 site pilot after both-site restart validation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import sys
import time

import emcee
import numpy as np

REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')
ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'development/mcmc_optimization/slurm/iter006'))
import stage_c as c

from model_ELM.mcmc_three_stage_artifacts import canonical_json_sha256, sha256_file, write_json_exclusive
from model_ELM.mcmc_three_stage_initialization import geometry_metrics
from model_ELM.mcmc_three_stage_sampler import finalize_sampler_run, run_sampler_block
from model_ELM.mcmc_three_stage_sampler_geometry import _sigmoid


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def audit_counts(path: Path, site: str) -> dict[str, int]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    totals = {'generated': 0, 'examined': 0, 'completed': 0,
              'failed': 0, 'unexamined': 0, 'accepted': 0}
    for step in range(129):
        retained = [row for row in rows if row.get('schema') == 'mcmc-iter006-retained-state-v1'
                    and row.get('global_step') == step]
        require(len(retained) == 64 and {row['walker'] for row in retained} == set(range(64)),
                f'{site} missing retained state at step {step}')
        if step == 0:
            continue
        groups = {kind: [row for row in rows if row.get('global_step') == step
                          and row.get('transition') == kind]
                  for kind in totals if kind != 'accepted'}
        for kind, group in groups.items():
            totals[kind] += len(group)
        require(len(groups['generated']) == len(groups['examined']) ==
                len(groups['completed']) == 64 and not groups['failed'] and
                not groups['unexamined'],
                f'{site} incomplete proposal accounting at step {step}')
        generated_ids = [row['proposal_id'] for row in groups['generated']]
        terminal_ids = [row['proposal_id'] for row in groups['completed']]
        require(len(set(generated_ids)) == 64 and set(generated_ids) == set(terminal_ids),
                f'{site} proposal IDs do not reconcile at step {step}')
        totals['accepted'] += sum(bool(row['accepted']) for row in groups['completed'])
    require(totals['generated'] == totals['examined'] == totals['completed'] == 8192,
            f'{site} incomplete 128-step proposal accounting')
    return totals


def main(site: str) -> None:
    started = time.perf_counter()
    config = c.verify_science_inventory()
    approval_path = ROOT / 'validation/approved_c_gate.json'
    approval = json.loads(approval_path.read_text())
    attempt = int(approval['attempt'])
    job = str(approval['job_id'])
    require(approval['schema'] == 'mcmc-iter006-approved-c-gate-v1' and
            2 <= attempt <= 11 and job.isdecimal(), 'C approval identity malformed')
    gate_path = ROOT / f'validation/c_attempt_{attempt:03d}/validation_report.json'
    c_account = ROOT / f'accounting/c_attempt_{attempt:03d}_{job}.psv'
    require(approval['validation_report_sha256'] == sha256_file(gate_path) and
            approval['accounting_sha256'] == sha256_file(c_account) and
            all(any(line.startswith(job + suffix + '|') and '|COMPLETED|0:0|' in line
                    for line in c_account.read_text().splitlines())
                for suffix in ('', '.batch', '.extern')),
            'C report/accounting approval identity failed')
    c_log = ROOT / f'logs/c{attempt}_{job}.out'
    c_error_log = ROOT / f'logs/c{attempt}_{job}.err'
    c_source_manifest = ROOT / f'submitted/c/attempt_{attempt:03d}/source.sha256'
    require(approval['stdout_sha256'] == sha256_file(c_log) and
            approval['stderr_sha256'] == sha256_file(c_error_log) and
            approval['source_manifest_sha256'] == sha256_file(c_source_manifest) and
            'MCMC_ITER006_COUPLED_RESTART_PASS' in c_log.read_text(),
            'C log/package identity or pass marker missing')
    gate = json.loads(gate_path.read_text())
    require(gate['result'] == 'pass' and gate['attempt'] == attempt and
            gate['job_id'] == job and
            all(gate['sites'][name]['restart']['backend_exact'] and
                gate['sites'][name]['restart']['logical_audit_exact']
                for name in ('ABBY', 'JERC')) and
            gate['synthetic_endpoint']['result'] == 'pass',
            'C both-site restart/endpoint hard gate missing')
    require(gate['numerical_policy_sha256'] == c.POLICY_SHA and
            gate['scientific_inputs_sha256'] == sha256_file(
                REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json'),
            'C science/numerical identity changed')
    site_gate = gate['sites'][site]['initialization']
    coordinate_path = gate_path.parent / site / 'coordinates.npz'
    target_path = gate_path.parent / site / 'physical_target.json'
    require(sha256_file(coordinate_path) == site_gate['coordinate_sha256'] and
            sha256_file(target_path) == site_gate['target_sha256'],
            f'{site} C coordinate/target source changed')
    with np.load(coordinate_path, allow_pickle=False) as saved:
        z = np.asarray(saved['sampler'], dtype=np.float64)
    require(z.shape == (64, 18) and np.all(np.isfinite(z)),
            f'{site} invalid C initial coordinates')
    posterior = c.load_posterior(config, site)
    require(np.all(posterior.prior.support_mask(posterior.sampling_geometry.sampler_to_physical(z))),
            f'{site} current physical support failed')
    seed = {'ABBY': 650041, 'JERC': 650042}[site]
    identity = c.sampler_identity(config, site, seed=seed, role='pilot',
                                  coordinate_sha=site_gate['coordinate_sha256'],
                                  target_sha=site_gate['target_sha256'])
    identity['execution_checksum_manifest_sha256'] = sha256_file(
        ROOT / 'submitted' / ('d' if site == 'ABBY' else 'e') / 'attempt_001/source.sha256')
    run_root = ROOT / 'chains' / site / 'pilot'
    block = run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                              run_directory=run_root, identity=identity,
                              target_iteration=128, checkpoint_interval=64)
    backend = emcee.backends.HDFBackend(str(run_root / 'active_backend.h5'), read_only=True)
    chain = np.asarray(backend.get_chain(), dtype=np.float64)
    final = np.asarray(backend.get_last_sample().coords, dtype=np.float64)
    require(backend.iteration == 128 and chain.shape == (128, 64, 18) and
            np.array_equal(final, chain[-1]) and
            np.all(np.isfinite(chain)), f'{site} pilot chain incomplete')
    counts = audit_counts(run_root / 'proposal_ledger.jsonl', site)
    accepted_by_walker = np.asarray(backend.accepted, dtype=np.int64)
    require(int(np.sum(accepted_by_walker)) == counts['accepted'],
            f'{site} audit/backend acceptance mismatch')
    saved_identity = json.loads((run_root / 'identity.json').read_text())
    require(saved_identity == {**identity, 'schema': 'mcmc-three-stage-sampler-identity-v3'},
            f'{site} pilot identity drift')
    for step in (64, 128):
        checkpoint = run_root / f'checkpoints/step_{step:04d}'
        marker = json.loads((checkpoint / 'manifest.json').read_text())
        require(marker['step'] == step and
                marker['identity_sha256'] == canonical_json_sha256(saved_identity) and
                marker['backend_sha256'] == sha256_file(checkpoint / 'backend.h5'),
                f'{site} pilot checkpoint {step} invalid')
    final_unit = _sigmoid(final)
    initial_unit = _sigmoid(z)
    metrics = geometry_metrics(final_unit)
    acceptance = float(np.sum(accepted_by_walker)) / 8192.0
    zero_move = int(np.sum(accepted_by_walker == 0))
    distinct = int(np.unique(np.asarray(final, dtype='<f8'), axis=0).shape[0])
    displacement = float(np.median(np.linalg.norm(final_unit - initial_unit, axis=1)))
    limitations = []
    if not 0.05 <= acceptance <= 0.80:
        limitations.append('acceptance_outside_descriptive_range')
    if zero_move > 16:
        limitations.append('more_than_16_zero_move_walkers')
    if distinct < 64:
        limitations.append('fewer_than_64_distinct_final_states')
    if metrics.rank < 18:
        limitations.append('final_ensemble_rank_below_18')
    if metrics.condition_number > 1e12:
        limitations.append('final_ensemble_condition_above_1e12')
    if displacement < 0.01:
        limitations.append('median_prior_unit_displacement_below_0.01')
    marker = finalize_sampler_run(run_root, decision=(
        'bounded_pilot_with_mixing_limitations' if limitations else 'bounded_pilot_validated'))
    final_geometry = metrics.to_dict()
    if not np.isfinite(metrics.condition_number):
        final_geometry['condition_number'] = None
        final_geometry['condition_number_classification'] = 'infinite_due_to_rank_deficiency'
    report = {
        'schema': 'mcmc-iter006-site-pilot-v1', 'site': site, 'result': 'pass',
        'job_id': str(os.environ['SLURM_JOB_ID']),
        'seed': seed, 'prior_id': 'ppe1', 'iteration': 128, 'nwalkers': 64,
        'checkpoint_steps': [64, 128], 'proposal_counts': counts,
        'acceptance_fraction': acceptance,
        'acceptance_by_walker': (accepted_by_walker / 128.0).tolist(),
        'zero_move_walkers': zero_move, 'distinct_final_states': distinct,
        'final_geometry': final_geometry,
        'median_net_prior_unit_displacement': displacement,
        'movement_limitations': limitations,
        'convergence': 'unassessed',
        'identity_sha256': sha256_file(run_root / 'identity.json'),
        'backend_sha256': sha256_file(run_root / 'active_backend.h5'),
        'proposal_ledger_sha256': sha256_file(run_root / 'proposal_ledger.jsonl'),
        'completed_marker_sha256': sha256_file(run_root / 'COMPLETED.json'),
        'c_validation_sha256': sha256_file(gate_path),
        'approved_c_gate_sha256': sha256_file(approval_path),
        'numerical_policy_sha256': c.POLICY_SHA,
        'elapsed_seconds': time.perf_counter() - started,
        'peak_rss_gib': float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0**2,
    }
    write_json_exclusive(ROOT / 'chains' / site / 'pilot_report.json', report)
    print(f'MCMC_ITER006_{site}_PILOT_PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', required=True, choices=('ABBY', 'JERC'))
    args = parser.parse_args()
    main(args.site)
