"""Unit tests for Phase 03B-B OLMT features:
  * prepare-only finalization (no scheduler submission)
  * external startup-finidat initialization (independent of spinup dependency)
  * explicit-finidat handling in set_finidat_file()
  * file/date validation and source protection
  * unsupported external-initialization ensemble requests (driver-level)

Lightweight: constructs ELMcase via __new__ and mocks filesystem/scheduler
interactions. No CIME case creation, no build, no model execution, no sbatch.
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


def _bare_case():
    """An ELMcase instance without running __init__ (avoids machine setup)."""
    c = model_ELM.ELMcase.__new__(model_ELM.ELMcase)
    c.noslurm = False
    c.prepare_only = False
    c.external_finidat = ''
    c.external_finidat_sha256 = ''
    c.has_finidat = False
    c.finidat = ''
    c.finidat_year = 0
    c.finidat_yst = ''
    c.startyear = 2018
    c.casename = 'ABBY_test_I20TRCNPRDCTCBC'
    c.casedir = '/tmp/casedir'
    c.OLMTdir = '/tmp/olmt'
    return c


def _make_fake_restart(path, year=2019, levels=15):
    """Write a minimal NetCDF ELM-restart-like file with a levgrnd dim."""
    from netCDF4 import Dataset
    ds = Dataset(path, 'w')
    ds.createDimension('levgrnd', levels)
    ds.createDimension('column', 1)
    v = ds.createVariable('T_SOISNO', 'f8', ('column', 'levgrnd'))
    v[:] = 273.0
    ds.close()


class SetFinidatFileTests(unittest.TestCase):
    def test_explicit_finidat_parses_year_and_yst(self):
        c = _bare_case()
        p = '/run/ABBY_ctrlvertsoc_annual_I20TRCNPRDCTCBC.elm.r.2019-01-01-00000.nc'
        c.set_finidat_file(finidat=p)
        self.assertEqual(c.finidat, p)
        self.assertTrue(c.has_finidat)
        self.assertEqual(c.finidat_year, 2019)
        # yst must be derived from the PARSED year, not the default 0
        self.assertEqual(c.finidat_yst, '2019')

    def test_dependent_finidat_case_branch_unchanged(self):
        c = _bare_case()
        c.runroot = '/run'
        c.set_finidat_file(finidat_case='PREVCASE', finidat_year=201)
        self.assertEqual(c.finidat_yst, '0201')
        self.assertTrue(c.finidat.endswith('PREVCASE.elm.r.0201-01-01-00000.nc'))


class ExternalStartupFinidatTests(unittest.TestCase):
    def test_sets_startup_finidat_and_checksum(self):
        c = _bare_case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY_x.elm.r.2019-01-01-00000.nc')
            _make_fake_restart(p, year=2019, levels=15)
            before = os.path.getmtime(p)
            c.set_external_startup_finidat(p, min_levels=10)
            self.assertTrue(c.has_finidat)
            self.assertEqual(c.finidat, os.path.abspath(p))
            self.assertEqual(c.startyear, 2019)   # RUN_STARTDATE year
            self.assertEqual(len(c.external_finidat_sha256), 64)
            # source file is never modified
            self.assertEqual(os.path.getmtime(p), before)

    def test_missing_file_exits(self):
        c = _bare_case()
        with self.assertRaises(SystemExit):
            c.set_external_startup_finidat('/does/not/exist.elm.r.2019-01-01-00000.nc')

    def test_insufficient_levels_exits(self):
        c = _bare_case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY_x.elm.r.2019-01-01-00000.nc')
            _make_fake_restart(p, year=2019, levels=5)
            with self.assertRaises(SystemExit):
                c.set_external_startup_finidat(p, min_levels=10)

    def test_no_branch_refcase_attrs_set(self):
        # The feature must not introduce RUN_REFCASE/REFTOD semantics.
        c = _bare_case()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'ABBY_x.elm.r.2019-01-01-00000.nc')
            _make_fake_restart(p)
            c.set_external_startup_finidat(p, min_levels=10)
            self.assertFalse(hasattr(c, 'run_refcase'))
            self.assertFalse(hasattr(c, 'run_reftod'))


class PrepareCaseTests(unittest.TestCase):
    def test_prepare_case_writes_pickle_no_submit(self):
        c = _bare_case()
        created = {'pkl': 0}

        def fake_pkl(outdir='./pklfiles'):
            created['pkl'] += 1

        c.create_pkl = fake_pkl  # type: ignore
        with mock.patch('os.chdir'):
            rc = c.prepare_case(multisite_script='/tmp/olmt/ABBY_test.sh')
        self.assertEqual(rc, 0)
        # pickle written to both casedir and pklfiles
        self.assertEqual(created['pkl'], 2)

    def test_prepare_case_does_not_call_subprocess(self):
        c = _bare_case()
        c.create_pkl = lambda outdir='./pklfiles': None  # type: ignore
        with mock.patch('subprocess.run') as sp, mock.patch('os.chdir'):
            c.prepare_case()
        sp.assert_not_called()


class DriverConfigTests(unittest.TestCase):
    """Driver-level checks via load_config on tiny temp configs."""

    def _write_cfg(self, text):
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'cfg.cfg')
        with open(p, 'w') as f:
            f.write(text)
        return p

    def test_external_init_section_parsed(self):
        import elm_olmt_Tianyi as drv
        p = self._write_cfg(
            "[external_initialization]\n"
            "target_stage = transient\n"
            "mode = startup_finidat\n"
            "finidat = /abs/ABBY.elm.r.2019-01-01-00000.nc\n"
        )
        cfg = drv.load_config(p)
        self.assertIn('external_initialization', cfg)
        self.assertEqual(cfg['external_initialization']['mode'], 'startup_finidat')
        self.assertEqual(cfg['external_initialization']['target_stage'], 'transient')


if __name__ == '__main__':
    unittest.main(verbosity=2)
