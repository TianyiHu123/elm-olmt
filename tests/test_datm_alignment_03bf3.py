"""Regression tests for the Phase 03B-F3 DATM forcing-year alignment fix.

Verifies ELMcase.compute_met_alignyear() (the policy) and
validate_transient_forcing_alignment() (the guard), plus the rendered CLM1PT
stream entry the generator writes. Lightweight: constructs ELMcase via __new__,
no CIME case creation, no build, no model execution.

Required acceptance: the ABBY CLM1PT stream entry must be
  datm.streams.txt.CLM1PT.ELM_USRDAT 2018 2018 2024
and must NOT be 2019 2018 2024.
"""
from __future__ import annotations
import sys, unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import model_ELM  # noqa: E402


def _case(compset, casename, met_startyear, met_endyear, startyear, run_n):
    c = model_ELM.ELMcase.__new__(model_ELM.ELMcase)
    c.compset = compset
    c.casename = casename
    c.met_startyear = met_startyear
    c.met_endyear = met_endyear
    c.met_endyear_spinup = met_startyear + 20 - 1
    c.nyears_spinup = met_endyear - met_startyear + 1
    c.startyear = startyear
    c.run_n = run_n
    return c


def _clm1pt_stream_entry(c):
    """Mirror the production stream-line render for the site CLM1PT 20TR case:
    yearAlign=met_alignyear yearFirst=met_startyear yearLast=met_endyear."""
    return ('datm.streams.txt.CLM1PT.ELM_USRDAT %d %d %d'
            % (c.met_alignyear, c.met_startyear, c.met_endyear))


class AlignPolicyTests(unittest.TestCase):
    def test_abby_transient_start2018(self):
        c = _case('I20TRCNPRDCTCBC', 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC', 2018, 2024, 2018, 7)
        self.assertEqual(c.compute_met_alignyear(), 2018)

    def test_abby_external_finidat_start2019(self):
        # The bug case: external-finidat transient starting 2019, met 2018-2024.
        c = _case('I20TRCNPRDCTCBC', 'ABBY_ctrlvertsoc_prep_I20TRCNPRDCTCBC', 2018, 2024, 2019, 1)
        self.assertEqual(c.compute_met_alignyear(), 2018)   # NOT 2019

    def test_historical_2019_2024_calendar_matched(self):
        c = _case('I20TRCNPRDCTCBC', 'x_I20TRCNPRDCTCBC', 2018, 2024, 2019, 6)
        c.met_alignyear = c.compute_met_alignyear()
        self.assertEqual(c.met_alignyear, 2018)
        c.validate_transient_forcing_alignment()  # must not raise

    def test_ad_spinup_preserves_previous_behavior(self):
        # Spinup cycling start year 1: policy returns startyear (unchanged).
        c = _case('I1850CNRDCTCBC', 'ABBY_ctrlvertsoc_I1850CNRDCTCBC_ad_spinup', 2018, 2024, 1, 200)
        self.assertEqual(c.compute_met_alignyear(), 1)

    def test_final_spinup_preserves_previous_behavior(self):
        c = _case('I1850CNPRDCTCBC', 'ABBY_ctrlvertsoc_I1850CNPRDCTCBC', 2018, 2024, 1, 200)
        self.assertEqual(c.compute_met_alignyear(), 1)


class RenderedStreamTests(unittest.TestCase):
    def test_abby_external_finidat_stream_entry(self):
        c = _case('I20TRCNPRDCTCBC', 'ABBY_ctrlvertsoc_prep_I20TRCNPRDCTCBC', 2018, 2024, 2019, 1)
        c.met_alignyear = c.compute_met_alignyear()
        entry = _clm1pt_stream_entry(c)
        self.assertEqual(entry, 'datm.streams.txt.CLM1PT.ELM_USRDAT 2018 2018 2024')
        self.assertNotEqual(entry, 'datm.streams.txt.CLM1PT.ELM_USRDAT 2019 2018 2024')

    def test_abby_original_control_stream_entry(self):
        c = _case('I20TRCNPRDCTCBC', 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC', 2018, 2024, 2018, 7)
        c.met_alignyear = c.compute_met_alignyear()
        self.assertEqual(_clm1pt_stream_entry(c),
                         'datm.streams.txt.CLM1PT.ELM_USRDAT 2018 2018 2024')


class ValidationGuardTests(unittest.TestCase):
    def test_calendar_matched_passes(self):
        c = _case('I20TRCNPRDCTCBC', 'x_I20TRCNPRDCTCBC', 2018, 2024, 2019, 6)
        c.met_alignyear = c.compute_met_alignyear()
        c.validate_transient_forcing_alignment()  # no raise

    def test_requested_years_unavailable_fails(self):
        # Transient 2025, met only 2018-2024 -> model year 2025 cannot be matched.
        c = _case('I20TRCNPRDCTCBC', 'x_I20TRCNPRDCTCBC', 2018, 2024, 2025, 1)
        c.met_alignyear = c.compute_met_alignyear()
        with self.assertRaises(SystemExit):
            c.validate_transient_forcing_alignment()

    def test_no_silent_remap_shifted_alignment(self):
        # If something set a shifted (wrong) alignment, the guard must catch it,
        # not silently remap. Simulate yearAlign=2019 (the old bug value).
        c = _case('I20TRCNPRDCTCBC', 'x_I20TRCNPRDCTCBC', 2018, 2024, 2019, 6)
        c.met_alignyear = 2019
        with self.assertRaises(SystemExit):
            c.validate_transient_forcing_alignment()


if __name__ == '__main__':
    unittest.main(verbosity=2)
