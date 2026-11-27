"""Independent numerical and corrected-move fixtures for Iter006."""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, localcontext
import math
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import emcee
import numpy as np

from model_ELM.mcmc_corrected_de_snooker import CorrectedDESnookerMove, DegenerateSnookerProposal
from model_ELM.mcmc_prior import LOG_PARAMETERS, PPE1, Prior18
from model_ELM.mcmc_three_stage_sampler_geometry import (
    BOUNDARY_COORDINATE_SYSTEM_ID, CoordinateSaturation, PhysicalMappingError,
    PriorUnitLogitBoundaryGeometry, _sigmoid,
)
from model_ELM.mcmc_three_stage_sampler import BoundaryProposalAuditLedger
from model_ELM.mcmc_three_stage_posterior import ThreeStagePosterior

PRIOR_ROOT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params')


class FixedRandom:
    def randint(self, count):
        assert count == 1
        return 0

    def shuffle(self, array):
        pass


class Iter006NumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = Prior18.from_directory(PPE1, PRIOR_ROOT)
        cls.geometry = PriorUnitLogitBoundaryGeometry(cls.prior)

    def test_coordinate_and_interior_density(self):
        self.assertEqual(self.geometry.coordinate_system_id, BOUNDARY_COORDINATE_SYSTEM_ID)
        for seed in (660041, 660042):
            rng = np.random.default_rng(seed)
            for z in rng.uniform(-12.0, 12.0, size=(16, 18)):
                result = self.geometry.map_with_jacobian(z)
                self.assertTrue(bool(self.prior.support_mask(result.physical)))
                expected = np.sum(-np.logaddexp(0.0, -z) - np.logaddexp(0.0, z))
                observed = self.prior.log_density(result.physical) + result.log_abs_det_jacobian
                self.assertLessEqual(abs(observed - expected), 1e-9)
                np.testing.assert_allclose(self.geometry.sampler_to_physical(z), result.physical, rtol=0, atol=0)
                np.testing.assert_allclose(self.geometry.log_abs_det_dphysical_dsampler(z),
                                           result.log_abs_det_jacobian, rtol=0, atol=0)

    def test_independent_decimal_reference_all_parameters(self):
        # The reference constructs Decimal transforms independently from the mapper.
        units = [np.nextafter(0.0, 1.0), 2.0**-60, 2.0**-48, 0.123456789,
                 0.5000000000000001, 0.876543211, np.nextafter(1.0, 0.0)]
        with localcontext() as context:
            context.prec = 800
            for u_scalar in units:
                if u_scalar == np.nextafter(0.0, 1.0):
                    # A finite logit cannot produce the smallest subnormal unit;
                    # verify that inverse arithmetic directly, not via logit.
                    continue
                z = math.log(u_scalar) - math.log1p(-u_scalar)
                row = np.full(18, z)
                if np.any(_sigmoid(row) >= 1.0):
                    continue
                result = self.geometry.map_with_jacobian(row)
                u = _sigmoid(row)
                reference = []
                for index, name in enumerate(self.prior.names):
                    low = Decimal.from_float(float(self.prior.lower[index]))
                    high = Decimal.from_float(float(self.prior.upper[index]))
                    if index == 17:
                        low = max(low, reference[16] + Decimal('0.5'))
                        high = min(high, Decimal('49.5'))
                    unit = Decimal.from_float(float(u[index]))
                    expected = ((low.ln() + unit * (high/low).ln()).exp()
                                if name in LOG_PARAMETERS else low + unit*(high-low))
                    reference.append(expected)
                    error = abs(Decimal.from_float(float(result.physical[index])) - expected)
                    ulp = Decimal.from_float(math.ulp(float(result.physical[index])))
                    self.assertLessEqual(error/ulp, Decimal(3), (name, u_scalar, str(error/ulp)))

    def test_natural_endpoint_and_unit_saturation(self):
        row = np.full(18, -40.0)
        result = self.geometry.map_with_jacobian(row)
        self.assertTrue(any(event['kind'] == 'natural_physical_endpoint' for event in result.events))
        self.assertTrue(math.isfinite(float(self.prior.log_density(result.physical))))
        self.assertTrue(math.isfinite(result.log_abs_det_jacobian))
        with self.assertRaises(CoordinateSaturation):
            self.geometry.map_with_jacobian(np.full(18, 40.0))

    def test_eligible_one_ulp_repair_and_wrong_regime_rejection(self):
        original = PriorUnitLogitBoundaryGeometry._raw_component
        def injected(name, low, high, unit):
            if name == 'k_l1':
                return math.nextafter(low, -math.inf)
            return original(name, low, high, unit)
        with patch.object(PriorUnitLogitBoundaryGeometry, '_raw_component', staticmethod(injected)):
            result = self.geometry.map_with_jacobian(np.full(18, -40.0))
            repairs = [event for event in result.events if event['kind'] == 'physical_repair']
            self.assertEqual(len(repairs), 1)
            self.assertEqual(repairs[0]['parameter'], 'k_l1')
            self.assertEqual(result.physical[0], self.prior.lower[0])
            with self.assertRaises(PhysicalMappingError):
                self.geometry.map_with_jacobian(np.zeros(18))

    def test_nonfinite_and_malformed(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.assertRaises(ValueError):
                self.geometry.map_with_jacobian(np.full(18, value))
        lower = self.prior.lower.copy()
        upper = self.prior.upper.copy()
        upper[0] = lower[0]
        malformed = replace(self.prior, lower=lower, upper=upper)
        with self.assertRaises(PhysicalMappingError):
            PriorUnitLogitBoundaryGeometry(malformed).map_with_jacobian(np.zeros(18))

    def test_direct_subnormal_unit_and_conditional_branch(self):
        with localcontext() as context:
            context.prec = 800
            unit = np.nextafter(0.0, 1.0)
            for index, name in enumerate(self.prior.names):
                low = float(self.prior.lower[index])
                high = float(self.prior.upper[index])
                if index == 17:
                    high = 49.5
                raw = self.geometry._raw_component(name, low, high, unit)
                dlow = Decimal.from_float(low); dhigh = Decimal.from_float(high)
                du = Decimal.from_float(float(unit))
                reference = ((dlow.ln()+du*(dhigh/dlow).ln()).exp()
                             if name in LOG_PARAMETERS else dlow+du*(dhigh-dlow))
                ulp = Decimal.from_float(math.nextafter(low, math.inf)-low)
                self.assertLessEqual(abs(Decimal.from_float(raw)-reference)/ulp, Decimal(3))
        base = np.full(18, -2.0)
        for leaf_unit in ((39.5-15.0)/25.0, 1.0-2.0**-40):
            base[16] = math.log(leaf_unit)-math.log1p(-leaf_unit)
            result = self.geometry.map_with_jacobian(base)
            low, high = self.prior.cn_bounds(result.physical[16])
            self.assertGreaterEqual(result.physical[17], low)
            self.assertLessEqual(result.physical[17], high)

    def test_parent_repair_then_child_and_material_negative(self):
        original = PriorUnitLogitBoundaryGeometry._raw_component
        def upper_leaf(name, low, high, unit):
            if name == 'leafcn':
                return math.nextafter(high, math.inf)
            return original(name, low, high, unit)
        row = np.full(18, -2.0)
        row[16] = 36.0
        row[17] = -40.0
        with patch.object(PriorUnitLogitBoundaryGeometry, '_raw_component', staticmethod(upper_leaf)):
            result = self.geometry.map_with_jacobian(row)
            self.assertEqual(result.physical[16], self.prior.upper[16])
            self.assertEqual(self.prior.cn_bounds(result.physical[16])[0], 40.5)
            self.assertTrue(any(event['parameter'] == 'leafcn' and event['kind'] == 'physical_repair'
                                for event in result.events))
        def nine_ulp(name, low, high, unit):
            if name == 'k_l1':
                value = low
                for _ in range(9):
                    value = math.nextafter(value, -math.inf)
                return value
            return original(name, low, high, unit)
        with patch.object(PriorUnitLogitBoundaryGeometry, '_raw_component', staticmethod(nine_ulp)):
            with self.assertRaises(PhysicalMappingError):
                self.geometry.map_with_jacobian(np.full(18, -40.0))

    def test_batch_equivalence_and_prior_ratio(self):
        rows = np.array([np.full(18, -3.0), np.full(18, 0.1), np.full(18, 2.0)])
        batch = self.geometry.sampler_to_physical(rows)
        for index, row in enumerate(rows):
            np.testing.assert_array_equal(batch[index], self.geometry.map_with_jacobian(row).physical)
        first, second = batch[0], batch[1]
        expected = 0.0
        for index, name in enumerate(self.prior.names):
            if name in LOG_PARAMETERS:
                expected += math.log(first[index]/second[index])
        low_first, high_first = self.prior.cn_bounds(first[16])
        low_second, high_second = self.prior.cn_bounds(second[16])
        expected += math.log((high_first-low_first)/(high_second-low_second))
        observed = self.prior.log_density(second)-self.prior.log_density(first)
        self.assertAlmostEqual(observed, expected, places=11)

    def test_audit_survives_mapping_and_degenerate_generation_error(self):
        identity = {'run_id': 'synthetic', 'site': 'ABBY', 'chain_role': 'audit_fixture',
                    'numerical_policy_sha256': 'fixture'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'audit.jsonl'
            ledger = BoundaryProposalAuditLedger(path, geometry=self.geometry,
                                                 identity=identity, resume=False)
            ledger.current_step = 1
            proposal = np.stack([np.zeros(18), np.full(18, np.nan), np.ones(18)])
            bases = ledger.record_generated(move='DEMove', split=0,
                                            walker_indices=np.array([0, 1, 2]),
                                            sampler_coordinates=proposal)
            with self.assertRaises(ValueError):
                ledger.record_examined(bases, proposal)
            records = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(sum(row['transition'] == 'generated' for row in records), 3)
            self.assertTrue(any(row['transition'] == 'failed' and row['walker'] == 1 for row in records))
            self.assertTrue(any(row['transition'] == 'unexamined' and row['walker'] == 2 for row in records))
            self.assertTrue(any(isinstance(value, dict) and value.get('nonfinite') == 'NaN'
                                for value in records[1]['z']))
            error = DegenerateSnookerProposal('degenerate', details={
                'partial_q': np.stack([np.zeros(18)]), 'failed_local_index': 1,
                'current_q': np.full(18, np.inf)})
            ledger.record_generation_error(move='DESnookerMove', split=1,
                                           walker_indices=np.array([3, 4, 5]), exc=error)
            records = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertTrue(any(row.get('stage') == 'move_generation' and row.get('walker') == 4
                                for row in records))
            bases = ledger.record_generated(move='DEMove', split=0,
                                            walker_indices=np.array([6, 7, 8]),
                                            sampler_coordinates=np.zeros((3, 18)))
            ledger.record_target_error(bases, RuntimeError('synthetic target failure'), progress={
                'phase': 'physical_likelihood_loop', 'current_position': 1,
                'physical_completed_positions': [0],
            })
            terminal = [row for row in (json.loads(line) for line in path.read_text().splitlines())
                        if row.get('walker') in (6, 7, 8) and row['transition'] != 'generated']
            self.assertEqual([(row['walker'], row['transition'], row['stage']) for row in terminal],
                             [(6, 'failed', 'target_evaluated_no_mh'),
                              (7, 'failed', 'target_current_failure'),
                              (8, 'unexamined', 'target_likelihood_after_failure')])

    def test_failed_sampling_progress_is_inactive_for_direct_physical_call(self):
        posterior = object.__new__(ThreeStagePosterior)
        posterior.sampling_coordinate_system = BOUNDARY_COORDINATE_SYSTEM_ID
        posterior._boundary_sampling_active = False
        posterior._boundary_target_progress = {}
        posterior._boundary_last_failure_progress = {}
        def fail_impl(_self, _values):
            _self._boundary_target_progress = {
                'phase': 'physical_likelihood_loop', 'current_position': 1,
                'physical_completed_positions': [0],
            }
            raise RuntimeError('synthetic target failure')
        with patch.object(ThreeStagePosterior, '_evaluate_sampling_batch_impl', fail_impl):
            with self.assertRaises(RuntimeError):
                posterior.evaluate_sampling_batch(np.zeros((2, 18)))
        self.assertFalse(posterior._boundary_sampling_active)
        self.assertEqual(posterior._boundary_last_failure_progress['current_position'], 1)
        def direct_timed(_self, values):
            self.assertFalse(_self._boundary_sampling_active)
            self.assertEqual(np.asarray(values).shape, (1, 18))
            return ['direct-physical-result'], {}
        with patch.object(ThreeStagePosterior, 'evaluate_batch_timed', direct_timed):
            self.assertEqual(posterior.evaluate_batch(np.zeros((1, 18))), ['direct-physical-result'])

    def test_corrected_snooker_projection_and_hastings(self):
        s = np.zeros((1, 18))
        s[0, :2] = [3.0, 4.0]
        z = np.zeros(18)
        z1 = np.zeros(18); z1[:2] = [1.0, 2.0]
        z2 = np.zeros(18); z2[:2] = [-1.0, 0.0]
        complement = [np.array([z]), np.array([z1]), np.array([z2])]
        corrected = CorrectedDESnookerMove(gammas=1.7)
        q, factors = corrected.get_proposal(s, complement, FixedRandom())
        direction = np.zeros(18); direction[:2] = [0.6, 0.8]
        expected_q = s[0] + direction * 1.7 * np.dot(direction, z1-z2)
        expected_factor = 17.0 * math.log(np.linalg.norm(expected_q-z)/5.0)
        np.testing.assert_allclose(q[0], expected_q, rtol=0, atol=1e-14)
        self.assertAlmostEqual(float(factors[0]), expected_factor, places=13)
        old_q, old_factor = emcee.moves.DESnookerMove(gammas=1.7).get_proposal(
            s, complement, FixedRandom())
        self.assertFalse(np.allclose(old_q, expected_q, rtol=0, atol=1e-14))
        self.assertFalse(np.allclose(old_factor, expected_factor, rtol=0, atol=1e-14))
        with self.assertRaises(DegenerateSnookerProposal):
            corrected.get_proposal(np.zeros((1, 18)), complement, FixedRandom())


if __name__ == '__main__':
    unittest.main()
