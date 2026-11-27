#!/usr/bin/env python3
"""Aggregate available Iter006 evidence after the failed Stage B gate.

This job performs no target, surrogate, or sampler evaluation. Its successful
exit means the failed decision is supported, not that Iter006 validated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    policy = REPO / 'development/mcmc_optimization/slurm/iter006/numerical_policy.json'
    inputs = REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json'
    numerical = ROOT / 'validation/numerical_validation.json'
    fatal = ROOT / 'replay/fatal_attribution.json'
    preflight = ROOT / 'results/preflight.json'
    stderr = ROOT / 'logs/b_24840823.err'
    stdout = ROOT / 'logs/b_24840823.out'
    expected = {
        policy: '931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e',
        inputs: 'faae90d71f1d141474c60883eb4cf83436f4211cd96af1fff7b7d390f8f1a90c',
        numerical: 'a37216b7ecfdc1f8f864aa9ec320e9f34077df72c70ac4733b0c4fd1cb9ff4ab',
        fatal: '4fb109dc764276d8f438b5e727e79005e5cf0b9197e0f7413d246087f42e13de',
        preflight: '1a3a5f1cd62ee76298a016a41f59ea7d47737c22628fea97db2dd3122edc9a84',
    }
    for path, digest in expected.items():
        require(path.is_file() and sha(path) == digest, f'evidence identity drift: {path}')
    num = json.loads(numerical.read_text())
    old = json.loads(fatal.read_text())
    require(num['result'] == 'pass' and num['fatal_event_count'] == 1,
            'bounded numerical report changed')
    require(old['classification'] == 'exact_replay_reproduced', 'legacy attribution changed')
    event = old['events'][0]
    require((event['global_step'], event['walker'], event['parameter'], event['side'],
             event['directional_ulp_excursion']) == (3, 40, 'k_s2', 'lower', 2.0),
            'legacy event identity changed')
    require('MCMC_ITER006_NUMERICAL_VALIDATION_PASS' in stdout.read_text(),
            'numerical pass marker missing')
    log = stderr.read_text()
    require('Ran 50 tests' in log and 'FAILED (errors=2)' in log,
            'test failure inventory changed')
    require("'Fixture' object has no attribute '_evaluate_sampling_batch_impl'" in log,
            'legacy fixture compatibility failure missing')
    require('FileNotFoundError' in log and
            'iter006_sampler_boundary_diagnostics/model_ELM/three_stage_coupled_release.py' in log,
            'test launch workdir failure missing')
    jobs = (24840516, 24840555, 24840587, 24840823)
    accounting = (ROOT / 'accounting/a_attempt_001_24840516.psv',
                  ROOT / 'accounting/a_attempt_002_24840555.psv',
                  ROOT / 'accounting/a_attempt_003_24840587.psv',
                  ROOT / 'accounting/b_24840823.psv')
    for job, path in zip(jobs, accounting):
        require(path.is_file() and str(job) in path.read_text() and
                'FAILED' in path.read_text(), f'missing terminal accounting for {job}')
    require(not any((ROOT / 'chains' / site).glob('*.h5') for site in ('ABBY', 'JERC')),
            'pilot backend exists after blocked gate')
    result = {
        'schema': 'mcmc-iter006-available-evidence-validation-v1',
        'evidence_result': 'pass',
        'iteration_decision': 'iter006_validation_failed',
        'reason': 'Stage B explicit unittest gate failed with two errors; correction budget exhausted',
        'numerical_reference_result': 'pass',
        'legacy_failure_attribution': 'exact_replay_reproduced',
        'legacy_event': {key: event[key] for key in
                         ('global_step', 'move', 'split', 'walker', 'parameter', 'index',
                          'side', 'bound', 'raw_value', 'directional_ulp_excursion')},
        'tests_run': 50,
        'test_errors': 2,
        'stages_not_launched': ['C', 'D', 'E'],
        'submitted_jobs_before_f': list(jobs),
        'accounting_before_f': {str(job): sha(path) for job, path in zip(jobs, accounting)},
        'scientific_inputs_sha256': sha(inputs),
        'numerical_policy_sha256': sha(policy),
        'numerical_validation_sha256': sha(numerical),
        'fatal_attribution_sha256': sha(fatal),
        'boundary_history_status': 'no corrected restart or pilot histories; no movement or convergence assessment',
        'f_terminal_accounting_pending': True,
    }
    target = ROOT / 'validation/final_available_evidence.json'
    with target.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print('ITER006_FAILED_CLOSEOUT_EVIDENCE_PASS')


if __name__ == '__main__':
    main()
