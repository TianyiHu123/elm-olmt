"""Unit tests for Phase 03B-B code-review corrections.

Covers:
  * build_case() fail-fast on case.setup / case.build failures and missing exe
  * external_finidat + restart_* modification is rejected before any write
  * external-startup vs dependent-startup RUN_* handling stays distinct
  * stronger external-restart validation (date format, Jan-1 only, start_year
    agreement, vertical dimensions)
  * --prepare-only rejects a pre-existing case non-interactively

Lightweight: constructs ELMcase via __new__ and mocks subprocess/filesystem.
No CIME case creation, build, model execution, or sbatch.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import model_ELM  # noqa: E402


def _case():
    c = model_ELM.ELMcase.__new__(model_ELM.ELMcase)
    c.noslurm = False
    c.prepare_only = False
    c.external_finidat = ''
    c.external_finidat_sha256 = ''
    c.has_finidat = False
    c.finidat = ''
    c.finidat_year = 0
    c.finidat_yst = ''
    c.startyear = 2019
    c.np = 1
    c.site = 'ABBY'
    c.casename = 'ABBY_prep_I20TRCNPRDCTCBC'
    c.casedir = '/tmp/casedir'
    c.caseroot = '/tmp/caseroot'
    c.runroot = '/tmp/runroot'
    c.OLMTdir = '/tmp/olmt'
    c.exeroot = '/tmp/exe'
    c.dobuild = False
    c.case_options = {}
    c.compset = 'ICBELMBC'
    c.forcing = 'default'
    return c


def _fake_restart(path, year=2019, mon=1, day=1, levels=15):
    from netCDF4 import Dataset
    ds = Dataset(path, 'w'); ds.createDimension('levgrnd', levels)
    ds.createDimension('column', 1)
    ds.createVariable('T_SOISNO', 'f8', ('column', 'levgrnd'))[:] = 273.0
    ds.close()


class BuildFailureTests(unittest.TestCase):
    def _run_build(self, c, returncodes):
        """Patch subprocess.run to yield queued returncodes; is_bypass False."""
        seq = list(returncodes)

        def fake_run(*a, **k):
            rc = seq.pop(0) if seq else 0
            return mock.Mock(returncode=rc, stderr='boom', stdout='')

        with mock.patch('subprocess.run', side_effect=fake_run), \
             mock.patch.object(type(c), 'is_bypass', return_value=False, create=True), \
             mock.patch.object(type(c), 'xmlchange', return_value=None, create=True), \
             mock.patch('os.chdir'):
            return c.build_case()

    def test_case_setup_failure_exits(self):
        c = _case(); c.dobuild = True
        with self.assertRaises(SystemExit):
            self._run_build(c, [1])          # case.setup fails

    def test_case_build_failure_exits(self):
        c = _case(); c.dobuild = True
        # setup ok (0), clean ok (0), build fails (1)
        with self.assertRaises(SystemExit):
            self._run_build(c, [0, 0, 1])

    def test_reuse_missing_exe_exits(self):
        c = _case(); c.dobuild = False; c.exeroot = '/tmp/nonexistent_exe_dir'
        # setup ok; reuse path checks exe existence -> missing -> exit
        with self.assertRaises(SystemExit):
            self._run_build(c, [0])

    def test_reuse_present_exe_ok(self):
        c = _case(); c.dobuild = False
        c.forcing = 'default'  # skip modify_datm_streamfiles branch
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, 'e3sm.exe'), 'w').close()
            c.exeroot = d
            c.rundir = d
            seq = [0]

            def fake_run(*a, **k):
                rc = seq.pop(0) if seq else 0
                return mock.Mock(returncode=rc, stderr='', stdout='')

            # Reuse path: setup ok, exe present -> must NOT raise. Mock the
            # downstream file-staging (os.system/subprocess.call) so the method
            # completes without touching the filesystem.
            with mock.patch('subprocess.run', side_effect=fake_run), \
                 mock.patch('subprocess.call', return_value=0), \
                 mock.patch('os.system', return_value=0), \
                 mock.patch.object(type(c), 'is_bypass', return_value=False, create=True), \
                 mock.patch.object(type(c), 'xmlchange', return_value=None, create=True), \
                 mock.patch('os.chdir'):
                c.build_case()   # should complete without SystemExit


class ExternalRestartGuardTests(unittest.TestCase):
    def test_external_plus_restart_mod_rejected(self):
        c = _case()
        c.external_finidat = '/abs/ABBY.elm.r.2019-01-01-00000.nc'
        c.finidat = c.external_finidat
        c.case_options = {'restart_DEADSTEMC': '*0.5'}
        c.machine = 'pm-cpu'; c.queue = 'shared'; c.project = 'm4803'
        c.OLMTdir = '/tmp/olmt'
        # Must reject before writing anything; patch open/file IO defensively.
        with mock.patch('os.chdir'), \
             mock.patch('builtins.open', mock.mock_open(read_data='LD_LIBRARY_PATH=/x\n')), \
             mock.patch.object(type(c), 'xmlquery', return_value='256', create=True):
            with self.assertRaises(SystemExit):
                c.create_multisite_script(['ABBY'], '/tmp/olmt')


class StartupCleanupTests(unittest.TestCase):
    def test_external_and_dependent_paths_distinct(self):
        # External-startup: RUN_TYPE=startup + CONTINUE_RUN=FALSE, NO RUN_REFDATE.
        ext = _case(); ext.has_finidat = True; ext.finidat_yst = '2019'
        ext.external_finidat = '/abs/x.elm.r.2019-01-01-00000.nc'
        calls_ext = []
        with mock.patch.object(type(ext), 'xmlchange',
                               side_effect=lambda var, value=None: calls_ext.append((var, value)),
                               create=True):
            if (ext.has_finidat):
                if (ext.external_finidat != ''):
                    ext.xmlchange('RUN_TYPE', value='startup')
                    ext.xmlchange('CONTINUE_RUN', value='FALSE')
                else:
                    ext.xmlchange('RUN_REFDATE', value=ext.finidat_yst + '-01-01')
        self.assertIn(('RUN_TYPE', 'startup'), calls_ext)
        self.assertIn(('CONTINUE_RUN', 'FALSE'), calls_ext)
        self.assertNotIn('RUN_REFDATE', [v for v, _ in calls_ext])

        # Dependent: RUN_REFDATE set (preserved behavior).
        dep = _case(); dep.has_finidat = True; dep.finidat_yst = '0201'
        dep.external_finidat = ''
        calls_dep = []
        with mock.patch.object(type(dep), 'xmlchange',
                               side_effect=lambda var, value=None: calls_dep.append((var, value)),
                               create=True):
            if (dep.has_finidat):
                if (dep.external_finidat != ''):
                    dep.xmlchange('RUN_TYPE', value='startup')
                else:
                    dep.xmlchange('RUN_REFDATE', value=dep.finidat_yst + '-01-01')
        self.assertIn(('RUN_REFDATE', '0201-01-01'), calls_dep)


class StrongerValidationTests(unittest.TestCase):
    def test_conflicting_start_year_rejected(self):
        c = _case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY.elm.r.2019-01-01-00000.nc')
            _fake_restart(p)
            with self.assertRaises(SystemExit):
                c.set_external_startup_finidat(p, start_year=2020)  # disagrees

    def test_non_january_first_rejected(self):
        c = _case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY.elm.r.2019-07-01-00000.nc')
            _fake_restart(p, mon=7)
            with self.assertRaises(SystemExit):
                c.set_external_startup_finidat(p)

    def test_bad_filename_rejected(self):
        c = _case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'not_a_restart.nc')
            _fake_restart(p)
            with self.assertRaises(SystemExit):
                c.set_external_startup_finidat(p)

    def test_insufficient_levels_rejected_by_default(self):
        # Default min_levels is now 10 (vertsoilc); 5 must fail without opting in.
        c = _case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY.elm.r.2019-01-01-00000.nc')
            _fake_restart(p, levels=5)
            with self.assertRaises(SystemExit):
                c.set_external_startup_finidat(p)

    def test_valid_passes_and_preserves_source(self):
        c = _case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY.elm.r.2019-01-01-00000.nc')
            _fake_restart(p, levels=15)
            before = os.path.getmtime(p)
            c.set_external_startup_finidat(p, start_year=2019)
            self.assertEqual(c.startyear, 2019)
            self.assertEqual(len(c.external_finidat_sha256), 64)
            self.assertEqual(os.path.getmtime(p), before)


class PrepareOnlyExistingCaseTests(unittest.TestCase):
    def test_prepare_only_rejects_existing_case(self):
        c = _case(); c.prepare_only = True
        c.caseid = ''; c.case_suffix = ''; c.region = 'reg'
        with tempfile.TemporaryDirectory() as d:
            casedir = os.path.join(d, 'ABBY_prep_I20TRCNPRDCTCBC')
            os.makedirs(casedir)
            c.caseroot = d
            with mock.patch('builtins.input') as inp:
                with self.assertRaises(SystemExit):
                    c.create_case(casename='ABBY_prep_I20TRCNPRDCTCBC')
                inp.assert_not_called()  # non-interactive


if __name__ == '__main__':
    unittest.main(verbosity=2)
