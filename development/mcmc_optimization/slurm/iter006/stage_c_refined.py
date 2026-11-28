#!/usr/bin/env python3
"""Iter006 frozen-target, original-walker and both-site restart validation."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import resource
import sys
import time

import emcee
import numpy as np
from emcee.state import State

REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')
ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
OUT = ROOT / 'validation/c_attempt_003'
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'development/mcmc_optimization/slurm/iter005'))
sys.path.insert(0, str(REPO / 'development/mcmc_optimization/slurm/iter006'))

import run_iter005 as old
from stage_b_continue import verify_science_inventory
from model_ELM.mcmc_prior import PPE1
from model_ELM.mcmc_three_stage_artifacts import (
    canonical_json_sha256, sha256_file, write_json_exclusive, write_npz_exclusive,
)
from model_ELM.mcmc_three_stage_initialization import geometry_metrics
from model_ELM.mcmc_three_stage_posterior import load_three_stage_posterior
from model_ELM.mcmc_three_stage_sampler import (
    finalize_sampler_run, random_state_equal, run_sampler_block,
)
from model_ELM.mcmc_three_stage_sampler_geometry import (
    BOUNDARY_COORDINATE_SYSTEM_ID, PriorUnitLogitBoundaryGeometry, _sigmoid,
)

POLICY_SHA = '931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e'
B_REPORT = ROOT / 'validation/b_attempt_002/numerical_validation.json'
B_JOB = 24841071
REFERENCE_FIELDS = ('log_prior', 'log_likelihood_gpp', 'log_likelihood_sr',
                    'log_likelihood_cn', 'log_posterior')
NORMALIZED_AUDIT_FIELDS = ('chain_role', 'proposal_id_role_segment')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def diagnostic_number(value: float):
    """Keep failure evidence serializable even for nonfinite target output."""
    value = float(value)
    if math.isnan(value):
        return {'nonfinite': 'NaN'}
    if math.isinf(value):
        return {'nonfinite': '+Infinity' if value > 0 else '-Infinity'}
    return value


def rss_gib() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0**2


def b_gate() -> dict:
    require(B_REPORT.is_file(), 'B attempt 002 numerical report missing')
    payload = json.loads(B_REPORT.read_text())
    require(payload['result'] == 'pass' and payload['numerical_policy_sha256'] == POLICY_SHA,
            'B numerical gate failed or policy drifted')
    candidates = sorted((ROOT / 'logs').glob('b2_*.out'))
    require(len(candidates) == 1 and str(B_JOB) in candidates[0].name,
            'B job stdout identity is ambiguous')
    log = candidates[0].read_text()
    require('MCMC_ITER006_UNITTEST_PASS tests=52 skipped=0' in log and
            'MCMC_ITER006_B_ATTEMPT_002_NUMERICAL_VALIDATION_PASS' in log and
            'stage_b2 test_status=0 numerical_status=0' in log,
            'B test and numerical gates did not both pass')
    return payload


def load_posterior(config: dict, site: str):
    return load_three_stage_posterior(
        site=site, prior_id=PPE1, prior_root=config['ppe1_root'],
        surrogate_release=old.release_config(config),
        observation_release=old.observation_config(config),
        gpp_resolution='daily', sr_resolution='daily', cn_observation_cv=0.30,
        include_cn=True, start=720, end=61320, member_chunk=16,
        sampling_coordinate_system=BOUNDARY_COORDINATE_SYSTEM_ID,
    )


def strict_midpoint_references(config: dict, site: str, posterior) -> dict[str, float]:
    reference_path = Path(config['iter003_reference_root']) / 'likelihood_reference_tests.json'
    require(sha256_file(reference_path) == config['iter003_references_sha256'],
            'Iter003 independent reference identity drift')
    cases = json.loads(reference_path.read_text())['cases']
    midpoint = posterior.prior.inverse_unit(np.full(18, 0.5, dtype=np.float64))
    result = posterior.evaluate(midpoint)
    differences = {}
    for kind, field in (('GPP_daily', 'log_likelihood_gpp'),
                        ('SR_daily', 'log_likelihood_sr'),
                        ('joint_cn', 'log_likelihood_cn')):
        matches = [case for case in cases if case['site'] == site and case['kind'] == kind
                   and (kind != 'joint_cn' or case['cn_observation_cv'] == 0.3)]
        require(len(matches) == 1, f'{site} strict reference missing: {kind}')
        actual = float(getattr(result, field))
        expected = float(matches[0]['reference'])
        require(np.isclose(actual, expected, rtol=1e-12, atol=1e-10),
                f'{site} strict scientific reference failed: {kind}')
        differences[kind] = abs(actual - expected)
    require(abs(result.log_posterior - sum(float(getattr(result, name)) for name in
                                                REFERENCE_FIELDS[:-1])) <= 1e-10,
            f'{site} midpoint physical component sum failed')
    return differences


def _physical_component_at(name: str, lower: float, upper: float, z: float) -> float:
    unit = float(_sigmoid(np.asarray([z], dtype=np.float64))[0])
    require(0.0 < unit < 1.0, 'initial-coordinate search reached unit saturation')
    value = PriorUnitLogitBoundaryGeometry._raw_component(name, lower, upper, unit)
    require(math.isfinite(value), 'initial-coordinate search produced nonfinite physical value')
    return value


def _nearest_initial_logit(name: str, lower: float, upper: float,
                           initial_z: float, target: float) -> tuple[float, float, dict]:
    """Select z by the physical forward map alone, with a fixed local search cap."""
    initial_raw = _physical_component_at(name, lower, upper, initial_z)
    best_z, best_raw = initial_z, initial_raw
    def score(raw: float, candidate_z: float) -> tuple[float, float, float]:
        # Lower physical value breaks equal absolute-error ties, then the
        # smallest displacement from the original finite logit wins.
        return abs(raw - target), raw, abs(candidate_z - initial_z)
    record = {'initial_z': initial_z, 'target_physical': target,
              'initial_physical': initial_raw, 'lower': lower, 'upper': upper,
              'search_max_absolute_z_displacement': 1e-12,
              'search_max_doublings': 40, 'search_max_bisections': 80,
              'selection_rule': 'minimum absolute physical reconstruction error; lower physical value then minimum original-z displacement break ties',
              'bracketed': initial_raw == target, 'doublings': 0, 'bisections': 0}
    if initial_raw != target:
        direction = 1.0 if initial_raw < target else -1.0
        step = max(math.ulp(initial_z), math.ulp(1.0))
        trial_z = initial_z
        for doubling in range(40):
            trial_z = initial_z + direction * step
            if trial_z == initial_z:
                trial_z = math.nextafter(initial_z, math.inf if direction > 0 else -math.inf)
            if abs(trial_z - initial_z) > 1e-12:
                break
            trial_raw = _physical_component_at(name, lower, upper, trial_z)
            record['doublings'] = doubling + 1
            if score(trial_raw, trial_z) < score(best_raw, best_z):
                best_z, best_raw = trial_z, trial_raw
            if (direction > 0 and trial_raw >= target) or (direction < 0 and trial_raw <= target):
                record['bracketed'] = True
                left, right = sorted((initial_z, trial_z))
                for bisection in range(80):
                    middle = left + (right - left) * 0.5
                    if middle == left or middle == right:
                        break
                    middle_raw = _physical_component_at(name, lower, upper, middle)
                    record['bisections'] = bisection + 1
                    if score(middle_raw, middle) < score(best_raw, best_z):
                        best_z, best_raw = middle, middle_raw
                    if middle_raw < target:
                        left = middle
                    else:
                        right = middle
                break
            step *= 2.0
    record.update(selected_z=best_z, selected_physical=best_raw,
                  selected_absolute_physical_error=abs(best_raw - target),
                  exact_physical_float_match=best_raw == target,
                  selected_absolute_z_displacement=abs(best_z - initial_z))
    return best_z, best_raw, record


def refine_initial_coordinates(theta: np.ndarray, geometry) -> tuple[np.ndarray, list[dict]]:
    """Refine only initial z from archived theta; never consult a likelihood."""
    z = np.asarray(geometry.physical_to_sampler(theta), dtype=np.float64)
    records = []
    for walker in range(len(theta)):
        sequential_physical = np.empty(18, dtype=np.float64)
        for index, name in enumerate(geometry.prior.names):
            lower = float(geometry.prior.lower[index])
            upper = float(geometry.prior.upper[index])
            if index == 17:
                root_low, root_high = geometry.prior.cn_bounds(sequential_physical[16])
                lower, upper = float(root_low), float(root_high)
            selected_z, selected_physical, record = _nearest_initial_logit(
                name, lower, upper, float(z[walker, index]), float(theta[walker, index]))
            z[walker, index] = selected_z
            sequential_physical[index] = selected_physical
            record.update(walker=walker, index=index, parameter=name,
                          interval_type='conditional' if index == 17 else 'marginal')
            records.append(record)
    return z, records


def site_initialization(config: dict, site: str, posterior) -> tuple[np.ndarray, str, str, dict]:
    source = old.old_site_files(config, site)
    site_config = config['sites'][site]
    for label, key in (('pool', 'old_pool_sha256'), ('walkers', 'old_walker_sha256'),
                       ('ledger', 'old_walker_ledger_sha256'),
                       ('target', 'old_target_manifest_sha256'),
                       ('source', 'old_source_manifest_sha256')):
        require(sha256_file(source[label]) == site_config[key],
                f'{site} Iter004 {label} hash drift')
    target = old.new_target(config, site, posterior)
    archived_target = json.loads(source['target'].read_text())
    for key in old.OLD_TARGET_FIELDS + (
        'site_uncertainty_product', 'site_soil_product', 'site_depth_source',
        'fixed_cn_covariance', 'fixed_cn_bias_correction',
    ):
        require(target[key] == archived_target[key],
                f'{site} frozen physical target changed: {key}')
    archived_ledger = json.loads(source['ledger'].read_text())
    require(archived_ledger['site'] == site and len(archived_ledger['entries']) == 64,
            f'{site} old walker ledger is invalid')
    with np.load(source['walkers'], allow_pickle=False) as archive:
        theta = np.asarray(archive['physical'], dtype=np.float64)
        saved_unit = np.asarray(archive['unit'], dtype=np.float64)
        saved_components = {name: np.asarray(archive[name], dtype=np.float64)
                            for name in REFERENCE_FIELDS}
    require(theta.shape == saved_unit.shape == (64, 18) and
            np.unique(np.asarray(theta, dtype='<f8'), axis=0).shape[0] == 64 and
            np.all(posterior.prior.support_mask(theta)),
            f'{site} archived physical walkers lack source/support/uniqueness')
    geometry = posterior.sampling_geometry
    site_out = OUT / site
    site_out.mkdir()
    z, refinement = refine_initial_coordinates(theta, geometry)
    write_json_exclusive(site_out / 'coordinate_refinement_search.json', {
        'schema': 'mcmc-iter006-initial-coordinate-search-v1',
        'site': site, 'source_walker_sha256': sha256_file(source['walkers']),
        'records': refinement, 'selected_sampler_z': z.tolist(),
    })
    unit = np.asarray(_sigmoid(z), dtype=np.float64)
    mapped_rows = [geometry.map_with_jacobian(row) for row in z]
    mapped = np.asarray([row.physical for row in mapped_rows], dtype=np.float64)
    selected_physical = np.asarray(
        [row['selected_physical'] for row in refinement], dtype=np.float64).reshape(64, 18)
    write_json_exclusive(site_out / 'coordinate_refinement.json', {
        'schema': 'mcmc-iter006-initial-coordinate-refinement-v1',
        'site': site, 'source_walker_sha256': sha256_file(source['walkers']),
        'method': 'monotone bracket and binary search around initial z using only archived physical theta and the locked forward physical map; no likelihood or surrogate feedback',
        'records': refinement,
        'selected_forward_physical': mapped.tolist(),
        'forward_map_events_by_walker': [list(row.events) for row in mapped_rows],
        'raw_search_equals_effective_forward_map_bits': bool(np.array_equal(
            selected_physical.view(np.uint64), mapped.view(np.uint64))),
    })
    require(np.array_equal(selected_physical.view(np.uint64), mapped.view(np.uint64)),
            f'{site} initial coordinate search and full effective map differ')
    require(all(row['bracketed'] for row in refinement),
            f'{site} initial physical-only coordinate search could not bracket every source value')
    require(np.all(np.isfinite(z)) and
            np.allclose(unit, saved_unit, rtol=0, atol=1e-12) and
            np.allclose(mapped, theta, rtol=1e-12, atol=0),
            f'{site} new physical/sampler initialization failed')
    metrics = geometry_metrics(unit)
    require(metrics.rank == 18 and metrics.condition_number <= 1e12 and
            all(span > 0 for span in metrics.range_by_dimension),
            f'{site} initial rank/span/condition failure')
    physical_rows = posterior.evaluate_batch(theta)
    sampling_rows = posterior.evaluate_sampling_batch(z)
    parity_rows = []
    for index, (physical, sampled) in enumerate(zip(physical_rows, sampling_rows)):
        for name in REFERENCE_FIELDS:
            archived = float(saved_components[name][index])
            exact_physical = float(getattr(physical, name))
            reconstructed = float(getattr(sampled.physical, name))
            same_ok = bool(np.isclose(exact_physical, archived, rtol=1e-7, atol=1e-8))
            cross_ok = bool(np.isclose(reconstructed, exact_physical, rtol=1e-7, atol=1e-8))
            parity_rows.append({
                'walker': index, 'component': name,
                'archived': diagnostic_number(archived),
                'exact_physical': diagnostic_number(exact_physical),
                'reconstructed': diagnostic_number(reconstructed),
                'same_vector_absolute_difference': diagnostic_number(abs(exact_physical - archived)),
                'cross_vector_absolute_difference': diagnostic_number(abs(reconstructed - exact_physical)),
                'same_vector_pass': same_ok, 'cross_vector_pass': cross_ok,
                'source_physical': theta[index].tolist() if not (same_ok and cross_ok) else None,
                'mapped_physical': mapped[index].tolist() if not (same_ok and cross_ok) else None,
                'sampler_z': z[index].tolist() if not (same_ok and cross_ok) else None,
                'forward_unit': unit[index].tolist() if not (same_ok and cross_ok) else None,
                'archived_unit': saved_unit[index].tolist() if not (same_ok and cross_ok) else None,
            })
    write_json_exclusive(site_out / 'parity_diagnostics.json', {
        'schema': 'mcmc-iter006-c-attempt-003-parity-diagnostics-v1',
        'site': site, 'rtol': 1e-7, 'atol': 1e-8,
        'source_walker_sha256': sha256_file(source['walkers']),
        'rows': parity_rows,
    })
    residuals = {name: 0.0 for name in REFERENCE_FIELDS}
    max_cancellation = 0.0
    max_component_sum = 0.0
    for index, (physical, sampled) in enumerate(zip(physical_rows, sampling_rows)):
        require(physical.evaluation_error is None and
                sampled.physical.evaluation_error is None,
                f'{site} archived walker target invalid at {index}')
        for name in REFERENCE_FIELDS:
            same_vector = float(getattr(physical, name))
            archived = float(saved_components[name][index])
            reconstructed = float(getattr(sampled.physical, name))
            require(np.isfinite(same_vector) and
                    np.isclose(same_vector, archived, rtol=1e-7, atol=1e-8),
                    f'{site} archived same-vector component parity failed: {name} walker {index}')
            require(np.isclose(reconstructed, same_vector, rtol=1e-7, atol=1e-8),
                    f'{site} reconstructed cross-vector component parity failed: {name} walker {index}')
            residuals[name] = max(residuals[name], abs(reconstructed - same_vector))
        same_sum = sum(float(getattr(sampled.physical, name)) for name in
                       REFERENCE_FIELDS[:-1])
        component_error = abs(float(sampled.physical.log_posterior) - same_sum)
        require(component_error <= 1e-10, f'{site} component sum failed: walker {index}')
        max_component_sum = max(max_component_sum, component_error)
        stable_unit_jacobian = float(np.sum(-np.logaddexp(0.0, -z[index])
                                            - np.logaddexp(0.0, z[index])))
        cancellation = abs(float(sampled.physical.log_prior) +
                           float(sampled.log_abs_det_jacobian) - stable_unit_jacobian)
        require(cancellation <= 1e-9, f'{site} prior/Jacobian cancellation failed: walker {index}')
        max_cancellation = max(max_cancellation, cancellation)
        require(abs(float(sampled.log_sampling_posterior) -
                    (float(sampled.physical.log_posterior) +
                     float(sampled.log_abs_det_jacobian))) <= 1e-9,
                f'{site} sampling density identity failed: walker {index}')
    target['schema'] = 'mcmc-iter006-physical-target-v1'
    target_path = site_out / 'physical_target.json'
    write_json_exclusive(target_path, target)
    coordinate_path = site_out / 'coordinates.npz'
    write_npz_exclusive(coordinate_path, physical=theta, unit=unit, sampler=z)
    report = {
        'source_walker_sha256': sha256_file(source['walkers']),
        'coordinate_sha256': sha256_file(coordinate_path),
        'target_sha256': sha256_file(target_path),
        'geometry': metrics.to_dict(),
        'maximum_cross_vector_component_difference': residuals,
        'maximum_component_sum_residual': max_component_sum,
        'maximum_prior_jacobian_cancellation_residual': max_cancellation,
    }
    return z, sha256_file(coordinate_path), sha256_file(target_path), report


def site_endpoint_target(posterior, z: np.ndarray, site: str) -> dict:
    """Two declared target calls at the same eligible physical endpoint vector."""
    endpoint_z = np.array(z[0], copy=True)
    endpoint_z[4] = -40.0
    mapping = posterior.sampling_geometry.map_with_jacobian(endpoint_z)
    require(any(event['kind'] in ('natural_physical_endpoint', 'physical_repair')
                for event in mapping.events),
            f'{site} declared k_s2 endpoint case did not reach a physical boundary')
    direct = posterior.evaluate(mapping.physical)
    sampled = posterior.evaluate_sampling(endpoint_z)
    require(direct.evaluation_error is None and sampled.physical.evaluation_error is None
            and direct.surrogate_evaluated and sampled.physical.surrogate_evaluated
            and np.isfinite(direct.log_posterior) and
            np.isfinite(sampled.log_sampling_posterior),
            f'{site} eligible endpoint failed finite prior/surrogate evaluation')
    for name in REFERENCE_FIELDS:
        require(np.isclose(float(getattr(direct, name)),
                           float(getattr(sampled.physical, name)),
                           rtol=1e-12, atol=1e-10),
                f'{site} endpoint same-physical-vector component changed: {name}')
    stable_unit_jacobian = float(np.sum(-np.logaddexp(0.0, -endpoint_z)
                                        - np.logaddexp(0.0, endpoint_z)))
    require(abs(sampled.physical.log_prior + sampled.log_abs_det_jacobian -
                stable_unit_jacobian) <= 1e-9 and
            abs(sampled.log_sampling_posterior - (sampled.physical.log_posterior +
                                                 sampled.log_abs_det_jacobian)) <= 1e-9,
            f'{site} endpoint stable z-space density identity failed')
    return {'case': 'archived_walker_0_with_k_s2_logit_minus_40',
            'z': endpoint_z.tolist(), 'physical': mapping.physical.tolist(),
            'events': list(mapping.events), 'same_vector_components_pass': True,
            'stable_z_density_pass': True,
            'log_physical_posterior': float(sampled.physical.log_posterior),
            'log_sampling_posterior': float(sampled.log_sampling_posterior)}


def sampler_identity(config: dict, site: str, *, seed: int, role: str,
                     coordinate_sha: str, target_sha: str) -> dict:
    source = REPO / 'model_ELM'
    return {
        'run_id': f'iter006_{site.lower()}_{seed}', 'site': site, 'chain_role': role,
        'prior_id': PPE1, 'parameter_names': list(old.Prior18.from_directory(PPE1, config['ppe1_root']).names),
        'posterior_target_sha256': target_sha,
        'pool_sha256': config['sites'][site]['old_pool_sha256'],
        'walker_sha256': config['sites'][site]['old_walker_sha256'],
        'emcee_version': emcee.__version__, 'move_configuration':
            json.loads((REPO / 'development/mcmc_optimization/slurm/iter006/iter006_config.json').read_text())['move_configuration'],
        'seed': int(seed), 'nwalkers': 64, 'ndim': 18,
        'coordinate_system_id': BOUNDARY_COORDINATE_SYSTEM_ID,
        'geometry_source_sha256': sha256_file(source / 'mcmc_three_stage_sampler_geometry.py'),
        'sampler_source_sha256': sha256_file(source / 'mcmc_three_stage_sampler.py'),
        'posterior_source_sha256': sha256_file(source / 'mcmc_three_stage_posterior.py'),
        'corrected_move_source_sha256': sha256_file(source / 'mcmc_corrected_de_snooker.py'),
        'numerical_policy_sha256': POLICY_SHA,
        'execution_checksum_manifest_sha256': sha256_file(ROOT / 'submitted/c/attempt_003/source.sha256'),
        'release_manifest_sha256': config['surrogate_release_manifest_sha256'],
        'walker_coordinates_sha256': coordinate_sha,
    }


def _audit_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _normalized_audit(rows: list[dict]) -> list[dict]:
    normalized = []
    for source in rows:
        row = dict(source)
        if 'chain_role' in row:
            row['chain_role'] = 'restart_fixture'
        if 'proposal_id' in row:
            pieces = row['proposal_id'].split('/')
            require(len(pieces) == 7, 'malformed proposal ID')
            pieces[2] = 'restart_fixture'
            row['proposal_id'] = '/'.join(pieces)
        normalized.append(row)
    return normalized


def _audit_completeness(rows: list[dict], site: str) -> dict:
    retained = [row for row in rows if row['schema'] == 'mcmc-iter006-retained-state-v1']
    require(len(retained) == 64 * 17, f'{site} retained step-zero/per-step history incomplete')
    for step in range(17):
        group = [row for row in retained if row['global_step'] == step]
        require(len(group) == 64 and {row['walker'] for row in group} == set(range(64)),
                f'{site} retained state count failed at step {step}')
    totals = {'generated': 0, 'examined': 0, 'completed': 0,
              'failed': 0, 'unexamined': 0, 'accepted': 0}
    for step in range(1, 17):
        by_transition = {kind: [row for row in rows if row.get('global_step') == step
                                      and row.get('transition') == kind]
                         for kind in totals if kind != 'accepted'}
        for kind, group in by_transition.items():
            totals[kind] += len(group)
        require(len(by_transition['generated']) == 64 and
                len(by_transition['completed']) == 64 and
                len(by_transition['examined']) == 64 and
                not by_transition['failed'] and not by_transition['unexamined'],
                f'{site} proposal accounting failure at step {step}')
        ids = [row['proposal_id'] for row in by_transition['generated']]
        require(len(set(ids)) == 64 and {row['walker'] for row in by_transition['generated']} == set(range(64)),
                f'{site} unstable proposal IDs at step {step}')
        totals['accepted'] += sum(bool(row['accepted']) for row in by_transition['completed'])
    require(totals['generated'] == totals['completed'] == totals['examined'] == 1024,
            f'{site} restart proposal totals are wrong')
    return totals


def restart_site(config: dict, site: str, posterior, z: np.ndarray,
                 coordinate_sha: str, target_sha: str) -> dict:
    seed = {'ABBY': 640041, 'JERC': 640042}[site]
    run_root = ROOT / 'chains' / site / 'restart_attempt_003'
    full = run_root / 'uninterrupted'
    split = run_root / 'split'
    full_identity = sampler_identity(config, site, seed=seed, role='restart_uninterrupted',
                                     coordinate_sha=coordinate_sha, target_sha=target_sha)
    split_identity = sampler_identity(config, site, seed=seed, role='restart_split',
                                      coordinate_sha=coordinate_sha, target_sha=target_sha)
    full_block = run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                                   run_directory=full, identity=full_identity,
                                   target_iteration=16, checkpoint_interval=8)
    run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                      run_directory=split, identity=split_identity,
                      target_iteration=8, checkpoint_interval=8)
    split_block = run_sampler_block(posterior=posterior, initial_sampler_coordinates=z,
                                    run_directory=split, identity=split_identity,
                                    target_iteration=16, checkpoint_interval=8, resume=True)
    a = emcee.backends.HDFBackend(str(full / 'active_backend.h5'), read_only=True)
    b = emcee.backends.HDFBackend(str(split / 'active_backend.h5'), read_only=True)
    require(a.iteration == b.iteration == 16 and
            np.array_equal(a.get_chain(), b.get_chain()) and
            np.array_equal(a.get_log_prob(), b.get_log_prob()) and
            np.array_equal(a.get_blobs(), b.get_blobs()) and
            np.array_equal(a.accepted, b.accepted) and
            random_state_equal(a.get_last_sample().random_state, b.get_last_sample().random_state),
            f'{site} backend split/restart state mismatch')
    full_rows = _audit_rows(full / 'proposal_ledger.jsonl')
    split_rows = _audit_rows(split / 'proposal_ledger.jsonl')
    full_counts = _audit_completeness(full_rows, site)
    split_counts = _audit_completeness(split_rows, site)
    require(full_counts == split_counts and
            _normalized_audit(full_rows) == _normalized_audit(split_rows),
            f'{site} logical proposal/event/counter history changed on restart')
    require(sum(int(v) for v in a.accepted) == full_counts['accepted'],
            f'{site} backend and audit acceptance differ')
    for run, identity in ((full, full_identity), (split, split_identity)):
        saved_identity = json.loads((run / 'identity.json').read_text())
        require(saved_identity == {**identity, 'schema': 'mcmc-three-stage-sampler-identity-v3'},
                f'{site} sampler identity drift')
        for step in (8, 16):
            path = run / f'checkpoints/step_{step:04d}'
            marker = json.loads((path / 'manifest.json').read_text())
            require(marker['step'] == step and
                    marker['identity_sha256'] == canonical_json_sha256(saved_identity) and
                    marker['backend_sha256'] == sha256_file(path / 'backend.h5'),
                    f'{site} checkpoint {step} mismatch')
    finalize_sampler_run(full, decision='restart_equivalence_fixture')
    finalize_sampler_run(split, decision='restart_equivalence_pass')
    return {
        'site': site, 'seed': seed, 'result': 'pass',
        'uninterrupted_identity_sha256': sha256_file(full / 'identity.json'),
        'split_identity_sha256': sha256_file(split / 'identity.json'),
        'uninterrupted_backend_sha256': full_block['backend_sha256'],
        'split_backend_sha256': split_block['backend_sha256'],
        'uninterrupted_audit_sha256': full_block['proposal_ledger_sha256'],
        'split_audit_sha256': split_block['proposal_ledger_sha256'],
        'logical_normalization': list(NORMALIZED_AUDIT_FIELDS),
        'proposal_counts': full_counts,
        'backend_iteration': int(a.iteration),
        'backend_exact': True, 'logical_audit_exact': True,
    }


class _EndpointMove(emcee.moves.Move):
    """Deterministic proposal with ordinary MH acceptance for a synthetic fixture."""

    def propose(self, model, state):
        proposed = np.array(state.coords, copy=True)
        proposed[0, 4] = -40.0
        logp, blobs = model.compute_log_prob_fn(proposed)
        accepted = np.zeros(len(proposed), dtype=bool)
        for index in range(len(proposed)):
            if logp[index] - state.log_prob[index] > math.log(model.random.rand()):
                accepted[index] = True
        return self.update(state, State(proposed, log_prob=logp, blobs=blobs), accepted), accepted


def synthetic_endpoint_fixture(prior) -> dict:
    boundary = PriorUnitLogitBoundaryGeometry(prior)
    seed = 660041
    initial = np.random.RandomState(seed).normal(0.0, 0.1, size=(36, 18))
    endpoint = np.array(initial[0], copy=True)
    endpoint[4] = -40.0
    mapped = boundary.map_with_jacobian(endpoint)
    require(any(event['kind'] in ('natural_physical_endpoint', 'physical_repair')
                for event in mapped.events), 'synthetic endpoint did not round to a physical bound')
    require(np.isfinite(prior.log_density(mapped.physical)) and
            np.all(prior.support_mask(mapped.physical)),
            'synthetic endpoint not supported by frozen prior')

    def target(values):
        result = []
        for z in values:
            item = boundary.map_with_jacobian(z)
            bonus = 2000.0 if any(e['kind'] in ('natural_physical_endpoint', 'physical_repair')
                                      for e in item.events) else -2000.0
            result.append(float(prior.log_density(item.physical)) + item.log_abs_det_jacobian + bonus)
        return np.asarray(result, dtype=np.float64)

    fixture_root = OUT / 'synthetic_endpoint'
    fixture_root.mkdir()
    results = {}
    for label in ('uninterrupted', 'split'):
        backend = emcee.backends.HDFBackend(str(fixture_root / f'{label}.h5'))
        backend.reset(36, 18)
        sampler = emcee.EnsembleSampler(36, 18, target, vectorize=True,
                                       moves=_EndpointMove(), backend=backend)
        sampler.random_state = np.random.RandomState(seed + 1).get_state()
        if label == 'uninterrupted':
            sampler.run_mcmc(initial, 2, progress=False)
        else:
            sampler.run_mcmc(initial, 1, progress=False)
            sampler = emcee.EnsembleSampler(36, 18, target, vectorize=True,
                                           moves=_EndpointMove(), backend=backend)
            sampler.run_mcmc(None, 1, progress=False)
        results[label] = backend
    a, b = results['uninterrupted'], results['split']
    require(np.array_equal(a.get_chain(), b.get_chain()) and
            np.array_equal(a.get_log_prob(), b.get_log_prob()) and
            np.array_equal(a.accepted, b.accepted) and
            random_state_equal(a.get_last_sample().random_state, b.get_last_sample().random_state),
            'synthetic endpoint restart differed')
    first_step = a.get_chain()[0, 0]
    require(int(a.accepted[0]) >= 1 and np.array_equal(first_step, endpoint) and
            first_step[4] == -40.0 and
            any(e['kind'] in ('natural_physical_endpoint', 'physical_repair')
                for e in boundary.map_with_jacobian(first_step).events),
            'synthetic physical endpoint did not pass MH and retain original z')
    return {'seed': seed, 'result': 'pass', 'original_z': endpoint.tolist(),
            'accepted_first_step': True, 'restart_exact': True,
            'endpoint_events': list(mapped.events),
            'uninterrupted_backend_sha256': sha256_file(fixture_root / 'uninterrupted.h5'),
            'split_backend_sha256': sha256_file(fixture_root / 'split.h5')}


def main() -> None:
    started = time.perf_counter()
    config = verify_science_inventory()
    b = b_gate()
    require(emcee.__version__ == '3.1.6', 'emcee dependency changed')
    require(not OUT.exists(), 'C output root already exists')
    OUT.mkdir(parents=True)
    reference_sha = sha256_file(Path(config['iter003_reference_root']) / 'posterior_validation.json')
    require(reference_sha == config['iter003_posterior_sha256'],
            'Iter003 posterior validation identity drift')
    reports = {}
    prior = None
    for site in ('ABBY', 'JERC'):
        posterior = load_posterior(config, site)
        prior = posterior.prior
        reference = strict_midpoint_references(config, site, posterior)
        z, coordinate_sha, target_sha, initialization = site_initialization(config, site, posterior)
        endpoint = site_endpoint_target(posterior, z, site)
        restart = restart_site(config, site, posterior, z, coordinate_sha, target_sha)
        reports[site] = {'strict_reference_absolute_differences': reference,
                         'initialization': initialization, 'endpoint_target': endpoint,
                         'restart': restart}
        write_json_exclusive(OUT / site / 'validation_report.json', reports[site])
    require(prior is not None, 'site prior was not loaded')
    synthetic = synthetic_endpoint_fixture(prior)
    report = {
        'schema': 'mcmc-iter006-coupled-restart-validation-v1',
        'result': 'pass', 'prior_id': PPE1,
        'job_id': str(os.environ['SLURM_JOB_ID']), 'attempt': 3,
        'scientific_inputs_sha256': sha256_file(REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json'),
        'numerical_policy_sha256': POLICY_SHA,
        'b_attempt_002_validation_sha256': sha256_file(B_REPORT),
        'b_job_id': B_JOB, 'sites': reports,
        'synthetic_endpoint': synthetic,
        'elapsed_seconds': time.perf_counter() - started, 'peak_rss_gib': rss_gib(),
    }
    write_json_exclusive(OUT / 'validation_report.json', report)
    print('MCMC_ITER006_COUPLED_RESTART_PASS')


if __name__ == '__main__':
    main()
