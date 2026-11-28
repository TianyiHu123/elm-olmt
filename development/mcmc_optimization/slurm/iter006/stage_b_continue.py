#!/usr/bin/env python3
"""Iter006 continued numerical validation; preserve Stage B attempt 001 evidence."""
from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys

REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')
ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
OUT = ROOT / 'validation/b_attempt_002'
LEGACY = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot')
sys.path.insert(0, str(REPO))
import numpy as np
from model_ELM.mcmc_prior import LOG_PARAMETERS, PPE1, Prior18
from model_ELM.mcmc_three_stage_artifacts import sha256_file, write_json_exclusive
from model_ELM.mcmc_three_stage_sampler_geometry import (
    CoordinateSaturation, PriorUnitLogitBoundaryGeometry, PriorUnitLogitGeometry, _sigmoid,
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify_science_inventory():
    inventory_path = REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json'
    require(sha256_file(inventory_path) == 'faae90d71f1d141474c60883eb4cf83436f4211cd96af1fff7b7d390f8f1a90c',
            'scientific input inventory identity drift')
    cfg = json.loads(inventory_path.read_text())
    root = Path(cfg['ppe1_root'])
    surrogate = Path(cfg['surrogate_release_root'])
    parent = surrogate.parent
    snapshot = Path(cfg['snapshot_root'])
    uncertainty = Path(cfg['uncertainty_root'])
    observation = Path(cfg['observation_release_root'])
    references = Path(cfg['iter003_reference_root'])
    checks = {
        'ppe1_parameter_sha256': root / 'NEON_ppe_vertc_parmfile',
        'ppe1_generator_sha256': root / 'generate_scramble_sobol.py',
        'ppe1_metadata_sha256': root / 'sobol18_1024_meta.json',
        'surrogate_release_manifest_sha256': surrogate / 'release_manifest.json',
        'surrogate_catalog_sha256': parent / 'catalog.json',
        'surrogate_parameter_constraints_sha256': surrogate / 'interface/parameter_constraints.json',
        'snapshot_sha256': snapshot / 'manifests/dataset_snapshot_r0001.json',
        'snapshot_common_source_sha256': snapshot / 'manifests/sources/common_v1.json',
        'member_split_sha256': snapshot / 'splits/member_split_1024_v1.json',
        'uncertainty_handoff_sha256': uncertainty / 'uncertainty_handoff.json',
        'uncertainty_manifest_sha256': uncertainty / 'products_manifest.json',
        'uncertainty_validation_sha256': uncertainty / 'final_validation_report.json',
        'observation_catalog_sha256': observation / 'catalog.json',
        'observation_manifest_sha256': observation / 'release_manifest.json',
        'observation_validation_sha256': observation / 'validation_report.json',
        'iter003_posterior_sha256': references / 'posterior_validation.json',
        'iter003_references_sha256': references / 'likelihood_reference_tests.json',
    }
    for key, path in checks.items():
        require(sha256_file(path) == cfg[key], f'frozen scientific dependency drift: {key}')
    for site in ('ABBY', 'JERC'):
        site_root = Path(cfg['iter004_root']) / 'sites' / site
        site_checks = {
            'old_pool_sha256': site_root / 'pool/pool.npz',
            'old_walker_sha256': site_root / 'walkers/walkers.npz',
            'old_walker_ledger_sha256': site_root / 'walkers/walker_selection_ledger.json',
            'old_target_manifest_sha256': site_root / 'candidates/target_manifest.json',
            'old_source_manifest_sha256': site_root / 'candidates/source_manifest.json',
        }
        for key, path in site_checks.items():
            require(sha256_file(path) == cfg['sites'][site][key],
                    f'frozen Iter004 {site} dependency drift: {key}')
    require(cfg['prior_id'] == 'ppe1' and cfg['full_window_start'] == 720 and
            cfg['full_window_end'] == 61320 and cfg['gpp_resolution'] == 'daily' and
            cfg['sr_resolution'] == 'daily' and cfg['include_cn'] is True and
            cfg['cn_observation_cv'] == 0.3, 'frozen science settings drift')
    return cfg


def independent_reference(prior, u):
    with localcontext() as context:
        context.prec = 800
        values = []
        intervals = []
        for index, name in enumerate(prior.names):
            low = Decimal.from_float(float(prior.lower[index]))
            high = Decimal.from_float(float(prior.upper[index]))
            if index == 17:
                low = max(low, values[16] + Decimal('0.5'))
                high = min(high, Decimal('49.5'))
            unit = u[index] if isinstance(u[index], Decimal) else Decimal.from_float(float(u[index]))
            value = ((low.ln() + unit*(high/low).ln()).exp()
                     if name in LOG_PARAMETERS else low + unit*(high-low))
            values.append(value)
            intervals.append((low, high))
        return values, intervals


def decimal_sigmoid(z):
    with localcontext() as context:
        context.prec = 800
        value = Decimal.from_float(float(z))
        return Decimal(1) / (Decimal(1) + (-value).exp())


def fatal_attribution(prior):
    generated_path = ROOT / 'replay/generated.jsonl'
    rows = [json.loads(line) for line in generated_path.read_text().splitlines()]
    require(rows[0]['schema'] == 'iter006-legacy-preinspect-v1', 'missing preinspection record')
    batches = [row for row in rows if row.get('schema') == 'iter006-legacy-generated-v1']
    require(len(batches) == 7, 'unexpected legacy generated subbatch count')
    fatal = batches[-1]
    require(fatal['global_step'] == 3 and fatal['move'] == 'DESnookerMove' and fatal['split'] == 0,
            'legacy fatal subbatch identity mismatch')
    old_ledger = LEGACY / 'sites/ABBY/restart/uninterrupted/proposal_ledger.jsonl'
    new_ledger = ROOT / 'replay/legacy_abby/proposal_ledger.jsonl'
    old_hdf = LEGACY / 'sites/ABBY/restart/uninterrupted/active_backend.h5'
    new_hdf = ROOT / 'replay/legacy_abby/active_backend.h5'
    require(sha256_file(old_ledger) == sha256_file(new_ledger) ==
            'b1d746892b85626682005eb61af56d59d7c07bdce6f54c0800d747f626431fd9',
            'legacy ledger is not byte-identical')
    require(sha256_file(old_hdf) == sha256_file(new_hdf) ==
            '6a3b751b3dc3fb1fdcd6314f20388fa4cf51fd1c9d36a15e5898495aa53ca4c2',
            'legacy HDF state is not byte-identical')
    events = []
    first_failing_local = None
    old_geometry = PriorUnitLogitGeometry(prior)
    for local, (z_values, u_values) in enumerate(zip(fatal['z'], fatal['u'])):
        if any(isinstance(value, dict) for value in z_values + u_values):
            continue
        z = np.asarray(z_values, dtype=np.float64)
        u = np.asarray(u_values, dtype=np.float64)
        require(np.array_equal(_sigmoid(z), u), 'stored fatal z/u mapping mismatch')
        try:
            old_geometry.sampler_to_physical(z)
        except CoordinateSaturation:
            continue
        except RuntimeError as exc:
            require(str(exc) == 'prior inverse unit mapping escaped PPE1 marginal bounds',
                    'earlier legacy error differs from archived marginal failure')
            first_failing_local = local
        if first_failing_local is None:
            continue
        raw = np.asarray(prior.inverse_unit(u), dtype=np.float64)
        exact_units = [decimal_sigmoid(value) for value in z]
        full_reference, _ = independent_reference(prior, exact_units)
        for index, name in enumerate(prior.names):
            low = float(prior.lower[index])
            high = float(prior.upper[index])
            interval_type = 'marginal'
            if index == 17:
                low_arr, high = prior.cn_bounds(raw[16])
                low = float(low_arr)
                interval_type = 'conditional_cn'
            value = float(raw[index])
            side = 'lower' if value < low else 'upper' if value > high else None
            if side is None or interval_type != 'marginal':
                continue
            bound = low if side == 'lower' else high
            ulp = abs(math.nextafter(bound, -math.inf if side == 'lower' else math.inf)-bound)
            reference, reference_intervals = independent_reference(prior, u)
            with localcontext() as context:
                context.prec = 800
                full_error = abs(Decimal.from_float(value)-reference[index])/Decimal.from_float(ulp)
                full_z_error = abs(Decimal.from_float(value)-full_reference[index])/Decimal.from_float(ulp)
                ref_distance = abs(reference[index]-Decimal.from_float(bound))/Decimal.from_float(ulp)
            if name in LOG_PARAMETERS:
                log_low = math.log(low)
                log_ratio = math.log(high/low)
                intermediate = {'log_low': log_low, 'log_high_over_low': log_ratio,
                                'u_times_log_ratio': float(u[index])*log_ratio,
                                'log_sum': log_low+float(u[index])*log_ratio,
                                'exp_log_sum': math.exp(log_low+float(u[index])*log_ratio)}
            else:
                intermediate = {'span': high-low, 'u_times_span': float(u[index])*(high-low),
                                'low_plus_product': low+float(u[index])*(high-low)}
            events.append({
                'global_step': 3, 'move': fatal['move'], 'split': fatal['split'],
                'walker': int(fatal['walkers'][local]), 'parameter': name, 'index': index,
                'z': z.tolist(), 'u': u.tolist(), 'raw_physical': raw.tolist(),
                'raw_value': value, 'lower': low, 'upper': high, 'bound': bound,
                'side': side, 'interval_type': interval_type,
                'absolute_excursion': abs(value-bound),
                'relative_excursion': abs(value-bound)/abs(bound),
                'directional_ulp_excursion': abs(value-bound)/ulp,
                'reference_physical': str(reference[index]),
                'reference_true_lower': str(reference_intervals[index][0]),
                'reference_true_upper': str(reference_intervals[index][1]),
                'reference_distance_from_float_bound_ulp': str(ref_distance),
                'full_mapping_error_ulp': str(full_error),
                'full_z_to_physical_reference': str(full_reference[index]),
                'full_z_to_physical_error_ulp': str(full_z_error),
                'unit_reference_from_exact_z': str(exact_units[index]),
                'rounded_unit_reference_matches_stored_u': float(exact_units[index]) == float(u[index]),
                'intermediate': intermediate,
            })
        break
    require(events and first_failing_local is not None,
            'exact replay yielded no first marginal physical escape')
    result = {
        'schema': 'mcmc-iter006-fatal-attribution-v1', 'classification': 'exact_replay_reproduced',
        'source': 'frozen_iter005_uncorrected', 'seed': 540041,
        'generated_sha256': sha256_file(generated_path),
        'old_and_replay_ledger_sha256': sha256_file(new_ledger),
        'old_and_replay_hdf_sha256': sha256_file(new_hdf),
        'fatal_batch': {'global_step': 3, 'move': fatal['move'], 'split': fatal['split'],
                        'walkers': fatal['walkers'],
                        'first_failing_local_index': first_failing_local,
                        'first_failing_walker': fatal['walkers'][first_failing_local],
                        'generated_but_unexamined_walkers': fatal['walkers'][first_failing_local+1:]},
        'events': events,
        'earlier_saturation_events_do_not_identify_fatal_event': True,
    }
    write_json_exclusive(OUT / 'fatal_attribution.json', result)
    return result


def _unit_token(token):
    if token == 'nextafter(0,1)':
        return float(np.nextafter(0.0, 1.0))
    if token == 'nextafter(1,0)':
        return float(np.nextafter(1.0, 0.0))
    if token.startswith('2^-'):
        return math.ldexp(1.0, -int(token[3:]))
    if token.startswith('1-2^-'):
        return 1.0 - math.ldexp(1.0, -int(token[5:]))
    return float(token)


def numerical_reference_grid(prior, geometry, policy):
    cases = []
    maxima = {}
    k_table = policy['allowance_by_branch_and_side']
    for label, grid_key in (('derivation', 'derivation_grid_declared_before_results'),
                            ('verification', 'verification_fixtures_declared_before_results')):
        declared = policy[grid_key]
        for unit_token in declared['unit_values']:
            unit = _unit_token(unit_token)
            require(0.0 < unit < 1.0, f'invalid declared unit fixture {unit_token}')
            side = 'lower' if unit <= 0.5 else 'upper'
            for index, name in enumerate(prior.names):
                leaf_values = declared['conditional_leaf_values'] if index == 17 else [None]
                for leaf in leaf_values:
                    low = float(prior.lower[index])
                    high = float(prior.upper[index])
                    if index == 17:
                        low = max(low, float(leaf) + 0.5)
                        high = min(high, 49.5)
                    require(low < high, 'declared conditional reference interval is empty')
                    raw = geometry._raw_component(name, low, high, unit)
                    require(math.isfinite(raw), 'nonfinite declared-grid physical value')
                    with localcontext() as context:
                        context.prec = 800
                        dlow = Decimal.from_float(low)
                        dhigh = Decimal.from_float(high)
                        du = Decimal.from_float(unit)
                        reference = ((dlow.ln() + du*(dhigh/dlow).ln()).exp()
                                     if name in LOG_PARAMETERS else dlow + du*(dhigh-dlow))
                        bound = low if side == 'lower' else high
                        ulp = geometry._directional_ulp(bound, side)
                        error_ulp = abs(Decimal.from_float(raw)-reference)/Decimal.from_float(ulp)
                        distance_ulp = abs(reference-Decimal.from_float(bound))/Decimal.from_float(ulp)
                    branch = geometry._branch(name, index, side)
                    regime = (geometry._regime_displacement(name, low, high, unit, side)
                              <= 8.0*ulp and distance_ulp <= Decimal(8))
                    if regime:
                        require(error_ulp <= Decimal(int(k_table[branch])),
                                f'{label} {branch} error exceeds locked K at {unit_token}')
                        maxima[(label, branch)] = max(maxima.get((label, branch), 0.0), float(error_ulp))
                    else:
                        require(abs(raw-float(reference)) <= 1e-10 + 1e-12*abs(float(reference)),
                                f'{label} interior arithmetic parity failed: {name}')
                    cases.append({'fixture': label, 'kind': 'direct_unit', 'unit_token': unit_token,
                                  'parameter': name, 'index': index, 'leaf_fixture': leaf,
                                  'branch': branch, 'side': side, 'raw': raw,
                                  'reference': str(reference), 'reference_distance_from_bound_ulp': str(distance_ulp),
                                  'full_mapping_error_ulp': str(error_ulp), 'directional_ulp': ulp,
                                  'boundary_regime': bool(regime), 'allowance_ulp': int(k_table[branch])})
        for z_value in declared['logit_values']:
            z = float(z_value)
            exact_unit = decimal_sigmoid(z)
            stored_unit = float(_sigmoid(np.asarray([z]))[0])
            rounded_unit = float(exact_unit)
            unit_ulp = math.ulp(rounded_unit)
            unit_error = abs(stored_unit-rounded_unit)/unit_ulp
            require(unit_error <= 1.0, f'{label} sigmoid exceeds one rounded-unit ULP at z={z}')
            case = {'fixture': label, 'kind': 'complete_logit', 'z': z,
                    'stored_u': stored_unit, 'decimal_unit': str(exact_unit),
                    'rounded_unit': rounded_unit, 'unit_error_ulp': unit_error}
            if stored_unit in (0.0, 1.0):
                try:
                    geometry.map_with_jacobian(np.full(18, z))
                except CoordinateSaturation:
                    case['result'] = 'unit_saturation_rejected'
                else:
                    raise RuntimeError('exact unit saturation was not rejected')
            else:
                mapped = geometry.map_with_jacobian(np.full(18, z))
                full_reference, intervals = independent_reference(prior, [exact_unit]*18)
                component_errors = []
                for index, name in enumerate(prior.names):
                    actual = float(mapped.physical[index])
                    reference = full_reference[index]
                    require(abs(actual-float(reference)) <= 1e-10 + 1e-12*abs(float(reference)),
                            f'{label} full z-to-physical reference failed: {name} z={z}')
                    side = 'lower' if stored_unit <= 0.5 else 'upper'
                    bound = float(prior.lower[index] if side == 'lower' else prior.upper[index])
                    if index == 17:
                        bound = float(prior.cn_bounds(mapped.physical[16])[0] if side == 'lower' else 49.5)
                    ulp = geometry._directional_ulp(bound, side)
                    with localcontext() as context:
                        context.prec = 800
                        error = abs(Decimal.from_float(actual)-reference)/Decimal.from_float(ulp)
                        distance = abs(reference-Decimal.from_float(bound))/Decimal.from_float(ulp)
                    branch = geometry._branch(name, index, side)
                    component_errors.append({'parameter': name, 'branch': branch,
                                             'full_mapping_error_ulp': str(error),
                                             'reference_distance_from_bound_ulp': str(distance),
                                             'reference_true_interval': [str(v) for v in intervals[index]]})
                    if distance <= Decimal(8):
                        require(error <= Decimal(int(k_table[branch])),
                                f'{label} full z-to-physical boundary error exceeds K: {name}')
                case['result'] = 'mapped'
                case['component_reference'] = component_errors
                case['events'] = list(mapped.events)
                for event in mapped.events:
                    require(event['eligible'] and event['input_displacement_ulp'] <= 8.0 and
                            float(event['full_mapping_error_ulp']) <= event['allowance_ulp'],
                            'natural endpoint or repair lacks locked eligibility')
            cases.append(case)
    write_json_exclusive(OUT / 'numerical_reference_cases.json', {
        'schema': 'mcmc-iter006-numerical-reference-cases-v1',
        'policy_sha256': sha256_file(REPO / 'development/mcmc_optimization/slurm/iter006/numerical_policy.json'),
        'precision_digits': 800, 'cases': cases,
    })
    return {f'{fixture}/{branch}': value for (fixture, branch), value in sorted(maxima.items())}


def main():
    verify_science_inventory()
    if OUT.exists():
        raise FileExistsError(f'continuation validation output already exists: {OUT}')
    OUT.mkdir(parents=True)
    preflight = json.loads((ROOT / 'results/preflight.json').read_text())
    require(preflight['result'] == 'pass', 'frozen Stage A in-job preflight missing')
    policy_path = REPO / 'development/mcmc_optimization/slurm/iter006/numerical_policy.json'
    policy_sha = sha256_file(policy_path)
    require(policy_sha == '931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e',
            'numerical policy identity drift')
    policy = json.loads(policy_path.read_text())
    require(policy['directional_ulp_ceiling'] == 8 and
            policy['allowance_by_branch_and_side'] == {
                'linear_lower': 2, 'linear_upper': 2,
                'log_uniform_lower': 3, 'log_uniform_upper': 3,
                'conditional_root_lower': 3, 'conditional_root_upper': 3,
            }, 'locked K table mismatch')
    prior = Prior18.from_directory(PPE1,
        '/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params')
    geometry = PriorUnitLogitBoundaryGeometry(prior)
    fatal = fatal_attribution(prior)
    max_error = numerical_reference_grid(prior, geometry, policy)
    require(all(f'{fixture}/{branch}' in max_error
                for fixture in ('derivation', 'verification')
                for branch in policy['allowance_by_branch_and_side']),
            'a declared K branch/side lacks near-boundary reference evidence')
    report = {
        'schema': 'mcmc-iter006-numerical-validation-v1', 'result': 'pass',
        'numerical_policy_sha256': policy_sha,
        'allowance_by_branch_and_side': policy['allowance_by_branch_and_side'],
        'reference_precision_digits': 800, 'maximum_boundary_branch_error_ulp': max_error,
        'numerical_reference_cases_sha256': sha256_file(OUT / 'numerical_reference_cases.json'),
        'fatal_attribution_sha256': sha256_file(OUT / 'fatal_attribution.json'),
        'fatal_event_count': len(fatal['events']),
        'corrected_move_sha256': sha256_file(REPO / 'model_ELM/mcmc_corrected_de_snooker.py'),
        'geometry_sha256': sha256_file(REPO / 'model_ELM/mcmc_three_stage_sampler_geometry.py'),
    }
    write_json_exclusive(OUT / 'numerical_validation.json', report)
    print('MCMC_ITER006_B_ATTEMPT_002_NUMERICAL_VALIDATION_PASS')


if __name__ == '__main__':
    main()
