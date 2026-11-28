#!/usr/bin/env python3
"""Evidence-only Iter006 boundary histories, figures and final gate aggregation."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path
import sys

import emcee
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

REPO = Path('/xdisk/chopinsong/tianyihu/elm-olmt-mcmc')
ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics')
POLICY_SHA = '931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e'
OUT = ROOT / 'diagnostics/attempt_002'
sys.path.insert(0, str(REPO))
from model_ELM.mcmc_three_stage_artifacts import sha256_file, write_json_exclusive
from model_ELM.mcmc_three_stage_sampler_geometry import _sigmoid

COUNT_FIELDS = ('generated', 'examined', 'completed', 'accepted', 'rejected',
                'failed', 'unexamined', 'repaired_vectors', 'repaired_components',
                'completed_repaired', 'accepted_repaired', 'natural_endpoint_vectors',
                'unit_saturation_vectors', 'material_violation_vectors',
                'other_mapping_failure_vectors', 'accepted_endpoint_vectors',
                'retained_exact_endpoint_vectors', 'retained_near_boundary_vectors',
                'retained_near_lower_components', 'retained_near_upper_components',
                'retained_states')
EVENT_KINDS = ('physical_repair', 'natural_physical_endpoint', 'unit_saturation',
               'material_physical_violation', 'other_numerical_mapping_failure')
GROUP_FIELDS = ('site', 'chain_role', 'step', 'block_start', 'block_end', 'block_partial',
                'move', 'parameter', 'side', 'bound_type', 'walker', 'event_kind',
                'count', 'accepted_count')
RATE_FIELDS = ('repair_rate', 'natural_endpoint_rate', 'unit_saturation_rate',
               'material_violation_rate', 'other_mapping_failure_rate',
               'acceptance_among_repaired', 'repaired_fraction_of_accepted',
               'retained_endpoint_rate', 'retained_near_boundary_rate')
STEP_FIELDS = ('site', 'chain_role', 'step', 'block_start', 'block_end', 'block_partial',
               *COUNT_FIELDS, *RATE_FIELDS,
               *(f'cumulative_{key}' for key in COUNT_FIELDS),
               *(f'cumulative_{key}' for key in RATE_FIELDS),
               'max_outward_ulp_excursion', 'max_absolute_correction',
               'cumulative_max_outward_ulp_excursion',
               'cumulative_max_absolute_correction')
BLOCK_FIELDS = ('site', 'chain_role', 'block_start', 'block_end', 'block_partial',
                *COUNT_FIELDS, *RATE_FIELDS,
                'max_outward_ulp_excursion', 'max_absolute_correction')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rate(numerator: int, denominator: int):
    return None if denominator == 0 else float(numerator) / float(denominator)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for source in rows:
            row = {key: ('NA' if source.get(key) is None else source.get(key, 'NA'))
                   for key in fields}
            writer.writerow(row)


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _block(step: int, total_steps: int) -> tuple[int, int, bool]:
    if step == 0:
        return 0, 0, True
    start = ((step - 1) // 16) * 16 + 1
    end = min(start + 15, total_steps)
    return start, end, end - start + 1 < 16


def _add_rates(row: dict) -> None:
    examined = row['examined']
    row['repair_rate'] = rate(row['repaired_vectors'], examined)
    row['natural_endpoint_rate'] = rate(row['natural_endpoint_vectors'], examined)
    row['unit_saturation_rate'] = rate(row['unit_saturation_vectors'], examined)
    row['material_violation_rate'] = rate(row['material_violation_vectors'], examined)
    row['other_mapping_failure_rate'] = rate(row['other_mapping_failure_vectors'], examined)
    row['acceptance_among_repaired'] = rate(row['accepted_repaired'], row['completed_repaired'])
    row['repaired_fraction_of_accepted'] = rate(row['accepted_repaired'], row['accepted'])
    row['retained_endpoint_rate'] = rate(row['retained_exact_endpoint_vectors'], row['retained_states'])
    row['retained_near_boundary_rate'] = rate(row['retained_near_boundary_vectors'], row['retained_states'])


def aggregate_chain(*, site: str, role: str, run_root: Path, steps: int,
                    destination: Path) -> dict:
    require(not destination.exists(), f'diagnostic destination already exists: {destination}')
    destination.mkdir(parents=True)
    identity = json.loads((run_root / 'identity.json').read_text())
    require(identity['site'] == site and identity['chain_role'] == role and
            identity['numerical_policy_sha256'] == POLICY_SHA and
            len(identity['parameter_names']) == 18,
            f'{site}/{role} sampler identity changed')
    names = tuple(identity['parameter_names'])
    rows = read_rows(run_root / 'proposal_ledger.jsonl')
    by_step: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        require(row['site'] == site and row['chain_role'] == role and
                row['numerical_policy_sha256'] == POLICY_SHA,
                f'{site}/{role} audit identity changed')
        by_step[int(row['global_step'])].append(row)
    require(set(by_step) == set(range(steps + 1)),
            f'{site}/{role} step-zero/every-step audit missing')
    step_rows: list[dict] = []
    group_counter: Counter[tuple] = Counter()
    group_accepted: Counter[tuple] = Counter()
    near_matrix = np.zeros((18, steps + 1), dtype=np.float64)
    cumulative = Counter()
    max_ulp = 0.0
    max_correction = 0.0
    component_counts = Counter()
    move_counts = Counter()
    for step in range(steps + 1):
        block_start, block_end, partial = _block(step, steps)
        item = {key: 0 for key in COUNT_FIELDS}
        item.update(site=site, chain_role=role, step=step, block_start=block_start,
                    block_end=block_end, block_partial=partial)
        step_max_ulp = 0.0
        step_max_correction = 0.0
        transitions: dict[str, list[dict]] = defaultdict(list)
        for row in by_step[step]:
            transitions[str(row['transition'])].append(row)
        retained = transitions['initialization'] + transitions['retained']
        require(len(retained) == 64 and {int(r['walker']) for r in retained} == set(range(64)),
                f'{site}/{role} retained state incomplete at step {step}')
        item['retained_states'] = len(retained)
        for row in retained:
            z = np.asarray(row['z'], dtype=np.float64)
            unit = _sigmoid(z)
            require(z.shape == unit.shape == (18,) and np.array_equal(unit, np.asarray(row['u'])),
                    f'{site}/{role} retained original-z/unit mismatch')
            lower = unit <= 0.01
            upper = unit >= 0.99
            near_matrix[:, step] += (lower | upper).astype(float) / 64.0
            item['retained_near_lower_components'] += int(np.sum(lower))
            item['retained_near_upper_components'] += int(np.sum(upper))
            item['retained_near_boundary_vectors'] += int(np.any(lower | upper))
            exact = row['physical_endpoint_parameters']
            item['retained_exact_endpoint_vectors'] += int(bool(exact))
            for index, name in enumerate(names):
                for side, active in (('lower', lower[index]), ('upper', upper[index])):
                    if active:
                        group_counter[(step, 'retained_near_boundary', 'RETAINED', name,
                                       side, 'prior_unit', int(row['walker']))] += 1
            for name in exact:
                index = names.index(name)
                side = 'lower' if unit[index] <= 0.5 else 'upper'
                bound_type = 'conditional' if index == 17 else 'marginal'
                group_counter[(step, 'retained_exact_endpoint', 'RETAINED', name,
                               side, bound_type, int(row['walker']))] += 1
        generated = transitions['generated']
        examined = transitions['examined']
        completed = transitions['completed']
        failed = transitions['failed']
        unexamined = transitions['unexamined']
        for kind, group in (('generated', generated), ('examined', examined),
                            ('completed', completed), ('failed', failed),
                            ('unexamined', unexamined)):
            item[kind] = len(group)
        if step == 0:
            require(not generated and not completed and not failed and not unexamined,
                    f'{site}/{role} step-zero has proposals')
        else:
            ids = [row['proposal_id'] for row in generated]
            terminal = completed + failed + unexamined
            require(len(ids) == len(set(ids)) == 64 and
                    len(terminal) == 64 and
                    {row['proposal_id'] for row in terminal} == set(ids),
                    f'{site}/{role} step {step} generated/terminal accounting mismatch')
            item['examined'] += sum(row.get('stage') == 'physical_map' for row in failed)
            require(item['examined'] + item['unexamined'] == item['generated'],
                    f'{site}/{role} step {step} examination accounting mismatch')
        completed_by_id = {row['proposal_id']: row for row in completed}
        event_flags: dict[str, set[str]] = defaultdict(set)
        for row in examined:
            proposal_id = row['proposal_id']
            for event in row.get('events', []):
                kind = event['kind']
                require(kind in EVENT_KINDS, f'unknown event kind: {kind}')
                event_flags[proposal_id].add(kind)
                parameter = str(event.get('parameter', 'NA'))
                side = str(event.get('side', 'NA'))
                bound_type = str(event.get('bound_type', 'unit' if kind == 'unit_saturation' else 'NA'))
                walker = int(row['walker'])
                group_key = (step, kind, str(row['move']), parameter, side, bound_type, walker)
                group_counter[group_key] += 1
                group_accepted[group_key] += int(bool(completed_by_id.get(proposal_id, {}).get('accepted')))
                if kind == 'physical_repair':
                    item['repaired_components'] += 1
                    component_counts[(parameter, side, bound_type)] += 1
                    outward = float(event['outward_ulp_excursion'])
                    correction = abs(float(event['raw']) - float(event['repaired']))
                    max_ulp = max(max_ulp, outward)
                    max_correction = max(max_correction, correction)
                    step_max_ulp = max(step_max_ulp, outward)
                    step_max_correction = max(step_max_correction, correction)
        for row in failed:
            details = row.get('details', {})
            kind = ('material_physical_violation' if row.get('stage') == 'physical_map'
                    and isinstance(details, dict) and 'bound' in details
                    else 'other_numerical_mapping_failure')
            event_flags[row['proposal_id']].add(kind)
            group_counter[(step, kind, str(row['move']), str(details.get('parameter', 'NA')),
                           str(details.get('side', 'NA')), str(details.get('bound_type', 'NA')),
                           int(row['walker']))] += 1
        item['accepted'] = sum(bool(row['accepted']) for row in completed)
        item['rejected'] = len(completed) - item['accepted']
        item['repaired_vectors'] = sum('physical_repair' in flags for flags in event_flags.values())
        item['completed_repaired'] = sum('physical_repair' in event_flags[row['proposal_id']]
                                         for row in completed)
        item['natural_endpoint_vectors'] = sum('natural_physical_endpoint' in flags
                                               for flags in event_flags.values())
        item['unit_saturation_vectors'] = sum('unit_saturation' in flags
                                              for flags in event_flags.values())
        item['material_violation_vectors'] = sum('material_physical_violation' in flags
                                                 for flags in event_flags.values())
        item['other_mapping_failure_vectors'] = sum('other_numerical_mapping_failure' in flags
                                                    for flags in event_flags.values())
        item['accepted_repaired'] = sum(bool(row['accepted']) and
                                        'physical_repair' in event_flags[row['proposal_id']]
                                        for row in completed)
        item['accepted_endpoint_vectors'] = sum(bool(row['accepted']) and
                                               bool(event_flags[row['proposal_id']] &
                                                    {'physical_repair', 'natural_physical_endpoint'})
                                               for row in completed)
        for row in generated:
            move_counts[(str(row['move']), 'generated')] += 1
            group_counter[(step, 'proposal_generated', str(row['move']), 'ALL', 'NA',
                           'NA', int(row['walker']))] += 1
        for row in completed:
            move_counts[(str(row['move']), 'completed')] += 1
            move_counts[(str(row['move']), 'accepted')] += int(bool(row['accepted']))
            key = (step, 'proposal_completed', str(row['move']), 'ALL', 'NA', 'NA',
                   int(row['walker']))
            group_counter[key] += 1
            group_accepted[key] += int(bool(row['accepted']))
        _add_rates(item)
        for key in COUNT_FIELDS:
            cumulative[key] += int(item[key])
        for key in COUNT_FIELDS:
            item['cumulative_' + key] = int(cumulative[key])
        cumulative_rates = dict(cumulative)
        _add_rates(cumulative_rates)
        for key in RATE_FIELDS:
            item['cumulative_' + key] = cumulative_rates[key]
        item['max_outward_ulp_excursion'] = step_max_ulp
        item['max_absolute_correction'] = step_max_correction
        item['cumulative_max_outward_ulp_excursion'] = max_ulp
        item['cumulative_max_absolute_correction'] = max_correction
        step_rows.append(item)
    block_rows = []
    for start in range(1, steps + 1, 16):
        end = min(start + 15, steps)
        block = {key: sum(row[key] for row in step_rows[start:end + 1]) for key in COUNT_FIELDS}
        block.update(site=site, chain_role=role, block_start=start, block_end=end,
                     block_partial=end - start + 1 < 16)
        _add_rates(block)
        block['max_outward_ulp_excursion'] = max(
            row['max_outward_ulp_excursion'] for row in step_rows[start:end + 1])
        block['max_absolute_correction'] = max(
            row['max_absolute_correction'] for row in step_rows[start:end + 1])
        block_rows.append(block)
    group_rows = []
    for (step, kind, move, parameter, side, bound_type, walker), count in sorted(group_counter.items()):
        start, end, partial = _block(step, steps)
        key = (step, kind, move, parameter, side, bound_type, walker)
        group_rows.append({'site': site, 'chain_role': role, 'step': step,
                           'block_start': start, 'block_end': end, 'block_partial': partial,
                           'move': move, 'parameter': parameter, 'side': side,
                           'bound_type': bound_type, 'walker': walker, 'event_kind': kind,
                           'count': count, 'accepted_count': group_accepted[key]})
    write_csv(destination / 'boundary_counts_by_step.csv', STEP_FIELDS, step_rows)
    write_csv(destination / 'boundary_counts_by_block.csv', BLOCK_FIELDS, block_rows)
    write_csv(destination / 'boundary_counts_by_group.csv', GROUP_FIELDS, group_rows)
    overall = {key: int(cumulative[key]) for key in COUNT_FIELDS}
    require(overall['generated'] == steps * 64 and
            overall['generated'] == overall['completed'] + overall['failed'] + overall['unexamined'],
            f'{site}/{role} cumulative proposal accounting failed')
    summary = {
        'schema': 'mcmc-iter006-boundary-diagnostics-v1',
        'site': site, 'chain_role': role, 'steps': steps,
        'numerical_policy_sha256': POLICY_SHA,
        'categories': {
            'A': 'raw physical overshoot repaired within locked K and input regime',
            'B': 'natural physical endpoint reached without raw overshoot',
            'C': 'unit sigmoid saturation at exactly zero or one; rejected',
            'D': 'material or unexplained physical violation',
            'E': 'other numerical or mapping failure',
            'vector_flags_may_overlap': True,
        },
        'denominators': {
            'proposal_event_rate': 'examined proposals, including a failed physical-map attempt',
            'acceptance_among_repaired': 'completed repaired proposals',
            'repaired_fraction_of_accepted': 'all accepted proposals',
            'retained_occupancy': 'all 64 retained walker states after each step, including held states; step zero included',
            'near_boundary_bands': 'original saved z passed through sigmoid; u<=0.01 or u>=0.99, descriptive only',
            'zero_denominator': 'NA',
            'partial_block': 'block with fewer than 16 completed step indices',
        },
        'overall_counts': overall,
        'overall_repair_rate': rate(overall['repaired_vectors'], overall['examined']),
        'acceptance_among_repaired': rate(overall['accepted_repaired'], overall['completed_repaired']),
        'repaired_fraction_of_accepted': rate(overall['accepted_repaired'], overall['accepted']),
        'natural_endpoint_rate': rate(overall['natural_endpoint_vectors'], overall['examined']),
        'unit_saturation_rate': rate(overall['unit_saturation_vectors'], overall['examined']),
        'maximum_outward_ulp_excursion': max_ulp,
        'maximum_absolute_correction': max_correction,
        'final_retained_endpoint_rate': step_rows[-1]['retained_endpoint_rate'],
        'maximum_step_retained_endpoint_rate': max(row['retained_endpoint_rate'] or 0.0 for row in step_rows),
        'initial_retained_near_boundary_rate': step_rows[0]['retained_near_boundary_rate'],
        'final_retained_near_boundary_rate': step_rows[-1]['retained_near_boundary_rate'],
        'repaired_components_by_parameter_bound': [
            {'parameter': name, 'side': side, 'bound_type': bound_type, 'count': count}
            for (name, side, bound_type), count in sorted(component_counts.items())
        ],
        'move_counts': [
            {'move': move, 'status': status, 'count': count}
            for (move, status), count in sorted(move_counts.items())
        ],
        'retained_endpoint_side_rule': 'for a recorded endpoint parameter, original sigmoid(z) <= 0.5 means lower, otherwise upper; conditional type only for frootcn',
        'endpoint_sensitivity_assessment_recommended_if_accepted_occupancy_is_material': True,
        'convergence': 'unassessed',
        'ledger_sha256': sha256_file(run_root / 'proposal_ledger.jsonl'),
        'step_csv_sha256': sha256_file(destination / 'boundary_counts_by_step.csv'),
        'block_csv_sha256': sha256_file(destination / 'boundary_counts_by_block.csv'),
        'group_csv_sha256': sha256_file(destination / 'boundary_counts_by_group.csv'),
    }
    write_json_exclusive(destination / 'boundary_diagnostics.json', summary)
    if role == 'pilot':
        fig, axes = plt.subplots(3, 1, figsize=(12, 9), constrained_layout=True)
        x = [row['block_end'] for row in block_rows]
        for key, label in (('repair_rate', 'repaired'),
                           ('natural_endpoint_rate', 'natural endpoint'),
                           ('unit_saturation_rate', 'unit saturation')):
            axes[0].plot(x, [np.nan if row[key] is None else row[key] for row in block_rows],
                         marker='o', label=label)
        axes[0].set_ylabel('examined proposal rate')
        axes[0].set_xlabel('16-step block end')
        axes[0].legend(loc='best')
        axes[1].plot([row['step'] for row in step_rows],
                     [np.nan if row['repaired_fraction_of_accepted'] is None else
                      row['repaired_fraction_of_accepted'] for row in step_rows],
                     label='accepted moves with repair / accepted moves')
        axes[1].plot([row['step'] for row in step_rows],
                     [row['retained_endpoint_rate'] for row in step_rows],
                     label='retained exact physical endpoint occupancy')
        axes[1].set_ylabel('rate')
        axes[1].set_xlabel('global step; includes held states')
        axes[1].legend(loc='best')
        plot = axes[2].imshow(near_matrix, aspect='auto', origin='lower',
                              extent=(0, steps, -0.5, 17.5), vmin=0, vmax=1,
                              interpolation='nearest')
        axes[2].set_yticks(range(18))
        axes[2].set_yticklabels(names, fontsize=7)
        axes[2].set_xlabel('global step; original prior-unit coordinate')
        axes[2].set_ylabel('parameter')
        fig.colorbar(plot, ax=axes[2], label='walkers with u<=0.01 or u>=0.99 / 64')
        fig.suptitle(f'{site} Iter006 boundary events and retained states; convergence unassessed')
        fig.savefig(destination / 'boundary_history.png', dpi=160)
        plt.close(fig)
    return summary


def legacy_replay_history(destination: Path) -> dict:
    """Separate old-source partial replay; never mix old events with corrected chains."""
    destination.mkdir(parents=True)
    legacy_inputs = {
        ROOT / 'replay/generated.jsonl': '9aa3d6d554fd63627dc6af7f9707c8d25668c4c442f434d0c9e8234a74e49845',
        ROOT / 'replay/legacy_abby/proposal_ledger.jsonl': 'b1d746892b85626682005eb61af56d59d7c07bdce6f54c0800d747f626431fd9',
        ROOT / 'replay/legacy_abby/active_backend.h5': '6a3b751b3dc3fb1fdcd6314f20388fa4cf51fd1c9d36a15e5898495aa53ca4c2',
        ROOT / 'replay/fatal_attribution.json': '4fb109dc764276d8f438b5e727e79005e5cf0b9197e0f7413d246087f42e13de',
    }
    require(all(sha256_file(path) == expected for path, expected in legacy_inputs.items()),
            'frozen legacy replay identity drift')
    generated = [json.loads(line) for line in (ROOT / 'replay/generated.jsonl').read_text().splitlines()]
    batches = [row for row in generated if row.get('schema') == 'iter006-legacy-generated-v1']
    ledger = read_rows(ROOT / 'replay/legacy_abby/proposal_ledger.jsonl')
    fatal = json.loads((ROOT / 'replay/fatal_attribution.json').read_text())
    require(len(batches) == 7 and len(ledger) == 128 and
            fatal['classification'] == 'exact_replay_reproduced',
            'legacy replay evidence changed')
    old_root = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot')
    old_coordinates = old_root / 'sites/ABBY/walkers/iter005_coordinates.npz'
    require(sha256_file(old_coordinates) ==
            '572a31c92960bcd88a54eeb12cb7d2ad6d079d6895dbe79c50a2fc3b0cf4cd4e',
            'frozen legacy initial coordinate identity drift')
    with np.load(old_coordinates, allow_pickle=False) as saved:
        initial_z = np.asarray(saved['sampler'], dtype=np.float64)
    backend = emcee.backends.HDFBackend(str(ROOT / 'replay/legacy_abby/active_backend.h5'), read_only=True)
    chain = np.asarray(backend.get_chain(), dtype=np.float64)
    require(initial_z.shape == (64, 18) and chain.shape == (2, 64, 18),
            'legacy retained-state source changed')
    rows = []
    cumulative = Counter()
    group_rows = []
    for step in (0, 1, 2, 3):
        gen = sum(len(row['walkers']) for row in batches if row['global_step'] == step)
        complete = [row for row in ledger if row['step'] == step]
        require(gen == (0 if step == 0 else 64 if step < 3 else 16),
                'legacy generated step count changed')
        examined = len(complete) if step < 3 else fatal['fatal_batch']['first_failing_local_index'] + 1
        # The first ten vectors in the fatal subbatch reached the old map, but
        # none reached a target/MH outcome. The eleventh vector raised; the
        # remaining five were generated and never mapped.
        failed = 1 if step == 3 else 0
        unexamined = gen - failed if step == 3 else 0
        mapped_without_target = examined - failed if step == 3 else 0
        never_mapped = gen - examined if step == 3 else 0
        accepted = sum(bool(row['accepted']) for row in complete)
        retained_z = initial_z if step == 0 else chain[step - 1] if step <= 2 else None
        near_vectors = None
        retained_states = 0
        if retained_z is not None:
            unit = _sigmoid(retained_z)
            near_vectors = int(np.sum(np.any((unit <= 0.01) | (unit >= 0.99), axis=1)))
            retained_states = 64
        values = {'step': step, 'generated': gen,
                  'map_examined': examined, 'map_unexamined': gen - examined,
                  'target_evaluated': len(complete),
                  'target_unevaluated': gen - len(complete),
                  'completed': len(complete), 'accepted': accepted,
                  'rejected': len(complete) - accepted, 'failed': failed,
                  'unexamined': unexamined,
                  'retained_states': retained_states,
                  'retained_near_boundary_vectors': near_vectors,
                  'retained_near_boundary_rate': rate(near_vectors, retained_states)
                  if near_vectors is not None else None,
                  'legacy_coordinate_saturation_rejections_unclassified': sum(
                      row['blob'] is not None and row['blob']['reason_code'] == 5
                      for row in complete),
                  'legacy_fatal_physical_overshoot': int(step == 3),
                  'mapped_without_target': mapped_without_target,
                  'never_mapped': never_mapped,
                  'block_start': 0 if step == 0 else 1,
                  'block_end': 0 if step == 0 else 3,
                  'block_partial': True}
        cumulative.update({key: values[key] for key in
                           ('generated', 'map_examined', 'map_unexamined',
                            'target_evaluated', 'target_unevaluated',
                            'completed', 'accepted', 'rejected', 'failed', 'unexamined')})
        for key in ('generated', 'map_examined', 'map_unexamined',
                    'target_evaluated', 'target_unevaluated',
                    'completed', 'accepted', 'rejected', 'failed', 'unexamined'):
            values['cumulative_' + key] = cumulative[key]
        values['legacy_fatal_rate'] = rate(values['legacy_fatal_physical_overshoot'], examined)
        rows.append(values)
        for row in complete:
            if row['blob'] is not None and row['blob']['reason_code'] == 5:
                group_rows.append({'site': 'ABBY', 'chain_role': 'legacy_replay',
                                   'step': step, 'move': row['move'], 'walker': row['walker'],
                                   'parameter': 'unknown', 'side': 'unknown',
                                   'event_kind': 'legacy_coordinate_saturation_rejection_unclassified',
                                   'count': 1, 'accepted_count': 0})
    event = fatal['events'][0]
    group_rows.append({'site': 'ABBY', 'chain_role': 'legacy_replay',
                       'step': 3, 'move': event['move'], 'walker': event['walker'],
                       'parameter': event['parameter'], 'side': event['side'],
                       'event_kind': 'legacy_fatal_unrepaired_overshoot',
                       'count': 1, 'accepted_count': 0})
    fatal_batch = next(row for row in batches if row['global_step'] == 3)
    require(fatal_batch['move'] == event['move'] and
            fatal_batch['walkers'][10] == event['walker'],
            'legacy fatal subbatch identity changed')
    for kind, walkers in (('legacy_mapped_without_target', fatal_batch['walkers'][:10]),
                          ('legacy_generated_never_mapped', fatal_batch['walkers'][11:])):
        for walker in walkers:
            group_rows.append({'site': 'ABBY', 'chain_role': 'legacy_replay',
                               'step': 3, 'move': fatal_batch['move'], 'walker': walker,
                               'parameter': 'NA', 'side': 'NA', 'event_kind': kind,
                               'count': 1, 'accepted_count': 0})
    fields = tuple(rows[0])
    write_csv(destination / 'boundary_counts_by_step.csv', fields, rows)
    block = {key: sum(row[key] for row in rows[1:]) for key in
             ('generated', 'map_examined', 'map_unexamined',
              'target_evaluated', 'target_unevaluated',
              'completed', 'accepted', 'rejected',
              'failed', 'unexamined', 'mapped_without_target', 'never_mapped',
              'legacy_coordinate_saturation_rejections_unclassified',
              'legacy_fatal_physical_overshoot')}
    block.update(block_start=1, block_end=3, block_partial=True,
                 legacy_fatal_rate=rate(block['legacy_fatal_physical_overshoot'], block['map_examined']))
    write_csv(destination / 'boundary_counts_by_block.csv', tuple(block), [block])
    write_csv(destination / 'boundary_counts_by_group.csv',
              ('site', 'chain_role', 'step', 'move', 'walker', 'parameter', 'side',
               'event_kind', 'count', 'accepted_count'), group_rows)
    summary = {'schema': 'mcmc-iter006-legacy-replay-history-v1',
               'source': 'frozen_iter005_uncorrected',
               'scope': 'two complete old steps plus partial fatal step 3; no corrected-chain inference',
               'partial_step_3': {'generated': 16, 'mapping_examined': 11,
                                  'target_evaluated': 0, 'failed': 1,
                                  'unexamined': 15, 'mapped_without_target': 10,
                                  'never_mapped': 5},
               'denominators': {'map_examined': 'generated proposals whose old physical mapper was invoked',
                                'map_unexamined': 'generated proposals never passed to the old mapper',
                                'target_evaluated': 'proposals with a completed old target/MH outcome',
                                'unexamined': 'generated proposals without a completed target/MH outcome or fatal mapping exception',
                                'legacy_fatal_rate': 'fatal mapping events / map_examined; descriptive only'},
               'legacy_reason_code_5': 'CoordinateSaturation conflates unit sigmoid saturation and rounded physical endpoints; component classification was not retained',
               'initial_retained_near_boundary_rate': rows[0]['retained_near_boundary_rate'],
               'legacy_exact_physical_endpoint_occupancy': 'unassessed_under_old_rejecting_policy',
               'old_fatal_event': fatal['events'][0],
               'step_csv_sha256': sha256_file(destination / 'boundary_counts_by_step.csv'),
               'block_csv_sha256': sha256_file(destination / 'boundary_counts_by_block.csv'),
               'group_csv_sha256': sha256_file(destination / 'boundary_counts_by_group.csv')}
    write_json_exclusive(destination / 'boundary_diagnostics.json', summary)
    return summary


def terminal_accounting(prefix: str, job_id: str) -> str:
    path = ROOT / 'accounting' / f'{prefix}_{job_id}.psv'
    require(path.is_file() and all(
        any(line.startswith(job_id + suffix + '|') and
            f'|{state}|{code}|' in line for line in path.read_text().splitlines())
        for suffix, state, code in (('', 'COMPLETED', '0:0'),
                                    ('.batch', 'COMPLETED', '0:0'),
                                    ('.extern', 'COMPLETED', '0:0'))),
            f'{prefix} job {job_id} lacks terminal success accounting')
    return sha256_file(path)


def main() -> None:
    require(not OUT.exists(), 'Stage F continuation diagnostics already exist')
    old_account = ROOT / 'accounting/final_iter006_jobs.psv'
    old_jobs = (24840516, 24840555, 24840587, 24840823, 24840903)
    old_lines = old_account.read_text().splitlines()
    require(all(all(any(line.startswith(f'{job}{suffix}|') and
                        f'|{state}|{code}|' in line for line in old_lines)
                    for suffix, state, code in (('', 'FAILED', '1:0'),
                                                ('.batch', 'FAILED', '1:0'),
                                                ('.extern', 'COMPLETED', '0:0')))
                for job in old_jobs),
            'historical five-job terminal accounting changed')
    b_account_sha = terminal_accounting('b_attempt_002', '24841071')
    approval_path = ROOT / 'validation/approved_c_gate.json'
    approval = json.loads(approval_path.read_text())
    attempt = int(approval['attempt'])
    c_job = str(approval['job_id'])
    require(approval['schema'] == 'mcmc-iter006-approved-c-gate-v1' and
            2 <= attempt <= 11 and c_job.isdecimal(),
            'approved C gate identity malformed')
    c_path = ROOT / f'validation/c_attempt_{attempt:03d}/validation_report.json'
    c_account_path = ROOT / f'accounting/c_attempt_{attempt:03d}_{c_job}.psv'
    require(approval['validation_report_sha256'] == sha256_file(c_path) and
            approval['accounting_sha256'] == sha256_file(c_account_path),
            'approved C report/accounting hashes changed')
    c_stdout = ROOT / f'logs/c{attempt}_{c_job}.out'
    c_stderr = ROOT / f'logs/c{attempt}_{c_job}.err'
    c_source_manifest = ROOT / f'submitted/c/attempt_{attempt:03d}/source.sha256'
    require(approval['stdout_sha256'] == sha256_file(c_stdout) and
            approval['stderr_sha256'] == sha256_file(c_stderr) and
            approval['source_manifest_sha256'] == sha256_file(c_source_manifest) and
            'MCMC_ITER006_COUPLED_RESTART_PASS' in c_stdout.read_text(),
            'approved C log/package identity or pass marker missing')
    c_report = json.loads(c_path.read_text())
    require(c_report['result'] == 'pass' and c_report['attempt'] == attempt and
            c_report['job_id'] == c_job and
            c_report['numerical_policy_sha256'] == POLICY_SHA and
            c_report['scientific_inputs_sha256'] == sha256_file(
                REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json') and
            c_report['synthetic_endpoint']['result'] == 'pass' and
            all(c_report['sites'][site]['restart']['backend_exact'] and
                c_report['sites'][site]['restart']['logical_audit_exact']
                for site in ('ABBY', 'JERC')),
            'C hard gate is absent')
    account = {'historical_five_jobs': sha256_file(old_account),
               '24841071': b_account_sha,
               c_job: terminal_accounting(f'c_attempt_{attempt:03d}', c_job)}
    prior_failed = approval['prior_failed_attempts']
    require(isinstance(prior_failed, list) and
            [int(row['attempt']) for row in prior_failed] == list(range(1, attempt)),
            'prior failed C attempt inventory is incomplete')
    for row in prior_failed:
        old_attempt = int(row['attempt'])
        old_job = str(row['job_id'])
        path = ROOT / f'accounting/c_attempt_{old_attempt:03d}_{old_job}.psv'
        old_log_prefix = 'c' if old_attempt == 1 else f'c{old_attempt}'
        lines = path.read_text().splitlines()
        require(row['accounting_sha256'] == sha256_file(path) and
                row['stdout_sha256'] == sha256_file(
                    ROOT / f'logs/{old_log_prefix}_{old_job}.out') and
                row['stderr_sha256'] == sha256_file(
                    ROOT / f'logs/{old_log_prefix}_{old_job}.err') and
                row['source_manifest_sha256'] == sha256_file(
                    ROOT / f'submitted/c/attempt_{old_attempt:03d}/source.sha256') and
                all(any(line.startswith(old_job + suffix + '|') and
                        f'|{state}|{code}|' in line for line in lines)
                    for suffix, state, code in (('', 'FAILED', '1:0'),
                                                ('.batch', 'FAILED', '1:0'),
                                                ('.extern', 'COMPLETED', '0:0'))),
                f'failed C attempt {old_attempt} accounting changed')
        account[old_job] = sha256_file(path)
    pilots = {}
    for site, prefix in (('ABBY', 'd'), ('JERC', 'e')):
        path = ROOT / 'chains' / site / 'pilot_report.json'
        report = json.loads(path.read_text())
        require(report['result'] == 'pass' and report['site'] == site and
                report['iteration'] == 128 and report['nwalkers'] == 64 and
                report['checkpoint_steps'] == [64, 128] and
                report['numerical_policy_sha256'] == POLICY_SHA and
                report['c_validation_sha256'] == sha256_file(c_path) and
                report['approved_c_gate_sha256'] == sha256_file(approval_path) and
                report['convergence'] == 'unassessed', f'{site} pilot report invalid')
        job = str(report['job_id'])
        account[job] = terminal_accounting(prefix, job)
        run = ROOT / 'chains' / site / 'pilot'
        for name, file in (('identity_sha256', 'identity.json'),
                           ('backend_sha256', 'active_backend.h5'),
                           ('proposal_ledger_sha256', 'proposal_ledger.jsonl'),
                           ('completed_marker_sha256', 'COMPLETED.json')):
            require(report[name] == sha256_file(run / file),
                    f'{site} pilot {name} identity drift')
        backend = emcee.backends.HDFBackend(str(run / 'active_backend.h5'), read_only=True)
        require(backend.iteration == 128 and
                np.asarray(backend.get_chain()).shape == (128, 64, 18),
                f'{site} pilot backend shape drift')
        pilots[site] = report
    OUT.mkdir(parents=True)
    legacy = legacy_replay_history(OUT / 'legacy_replay')
    results = {}
    for site in ('ABBY', 'JERC'):
        reports = {}
        for role in ('restart_uninterrupted', 'restart_split', 'pilot'):
            run = (ROOT / 'chains' / site / 'pilot' if role == 'pilot' else
                   ROOT / 'chains' / site / f'restart_attempt_{attempt:03d}' /
                   ('uninterrupted' if role == 'restart_uninterrupted' else 'split'))
            reports[role] = aggregate_chain(
                site=site, role=role, run_root=run,
                steps=128 if role == 'pilot' else 16,
                destination=OUT / site / role,
            )
            require(reports[role]['overall_counts']['failed'] == 0 and
                    reports[role]['overall_counts']['unexamined'] == 0 and
                    reports[role]['overall_counts']['material_violation_vectors'] == 0 and
                    reports[role]['overall_counts']['other_mapping_failure_vectors'] == 0,
                    f'{site}/{role} corrected-run material failure')
        require(reports['restart_uninterrupted']['overall_counts'] ==
                reports['restart_split']['overall_counts'],
                f'{site} restart aggregate histories disagree')
        require(reports['pilot']['overall_counts']['generated'] == 8192 and
                reports['pilot']['overall_counts']['completed'] == 8192 and
                reports['pilot']['overall_counts']['accepted'] ==
                pilots[site]['proposal_counts']['accepted'],
                f'{site} pilot diagnostics/proposal accounting disagree')
        results[site] = reports
    limitations = {site: pilots[site]['movement_limitations'] for site in pilots}
    decision = ('bounded_sampler_pilot_validated_with_mixing_limitations'
                if any(limitations.values()) else 'bounded_sampler_pilot_validated')
    report = {
        'schema': 'mcmc-iter006-final-evidence-v2', 'result': 'pass',
        'decision_candidate': decision, 'pre_f_hard_gates_passed': True,
        'terminal_f_and_four_record_gates_pending': True,
        'scientific_inputs_sha256': sha256_file(REPO / 'development/mcmc_optimization/slurm/iter006/scientific_inputs.json'),
        'numerical_policy_sha256': POLICY_SHA,
        'b_attempt_002_sha256': sha256_file(ROOT / 'validation/b_attempt_002/numerical_validation.json'),
        'c_validation_sha256': sha256_file(c_path),
        'approved_c_gate_sha256': sha256_file(approval_path),
        'pilot_report_sha256': {site: sha256_file(ROOT / 'chains' / site / 'pilot_report.json')
                                for site in pilots},
        'terminal_accounting_before_f': account,
        'sites': {site: {'movement_limitations': limitations[site],
                         'pilot_boundary_summary_sha256': sha256_file(
                             OUT / site / 'pilot/boundary_diagnostics.json'),
                         'restart_boundary_summary_sha256': {
                             role: sha256_file(OUT / site / role / 'boundary_diagnostics.json')
                             for role in ('restart_uninterrupted', 'restart_split')},
                         'pilot_figure_sha256': sha256_file(OUT / site / 'pilot/boundary_history.png')}
                  for site in pilots},
        'legacy_replay_summary_sha256': sha256_file(OUT / 'legacy_replay/boundary_diagnostics.json'),
        'boundary_findings': {site: {
            'initial_near_boundary_rate': results[site]['pilot']['initial_retained_near_boundary_rate'],
            'final_near_boundary_rate': results[site]['pilot']['final_retained_near_boundary_rate'],
            'overall_repair_rate': results[site]['pilot']['overall_repair_rate'],
            'accepted_repair_fraction': results[site]['pilot']['repaired_fraction_of_accepted'],
            'final_exact_endpoint_rate': results[site]['pilot']['final_retained_endpoint_rate'],
        } for site in pilots},
        'convergence': 'unassessed',
        'f_terminal_accounting_pending': True,
    }
    write_json_exclusive(OUT / 'final_validation.json', report)
    print('ITER006_CONTINUATION_EVIDENCE_PASS')


if __name__ == '__main__':
    main()
