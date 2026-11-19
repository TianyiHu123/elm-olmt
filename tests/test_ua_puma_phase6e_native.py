import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import OLMTmachine as om  # noqa: E402


class NativeSbatchTests(unittest.TestCase):
    def test_puma_sbatch_adds_parsable_export_and_afterok(self):
        ad = om.native_sbatch_argv('ua-puma9', './ad.sh')
        self.assertEqual(
            ad, ['sbatch', '--parsable', '--export=ALL', './ad.sh'])
        fn = om.native_sbatch_argv('ua-puma9', './fn.sh', depend=24714900)
        self.assertEqual(
            fn,
            ['sbatch', '--parsable', '--export=ALL',
             '--dependency=afterok:24714900', './fn.sh'])
        hi = om.native_sbatch_argv('ua-puma9', './hi.sh', depend=24714901)
        self.assertIn('--dependency=afterok:24714901', hi)
        self.assertNotIn('--prereq', ' '.join(hi))

    def test_perlmutter_sbatch_keeps_plain_afterok(self):
        cmd = om.native_sbatch_argv(
            'pm-cpu', './case.submit_ensemble', depend=111)
        self.assertEqual(
            cmd, ['sbatch', '--dependency=afterok:111', './case.submit_ensemble'])
        self.assertNotIn('--parsable', cmd)
        self.assertNotIn('--export=ALL', cmd)

    def test_parse_sbatch_jobid_parsable_and_legacy(self):
        self.assertEqual(om.parse_sbatch_jobid('24715001\n'), 24715001)
        self.assertEqual(om.parse_sbatch_jobid('24715001;puma\n'), 24715001)
        self.assertEqual(
            om.parse_sbatch_jobid('Submitted batch job 24678909\n'), 24678909)
        with self.assertRaises(ValueError):
            om.parse_sbatch_jobid('')
        with self.assertRaises(ValueError):
            om.parse_sbatch_jobid('sbatch: error: failed')

    def test_dynamic_job_ids_are_not_hardcoded_in_argv_builder(self):
        first = 111
        second = om.native_sbatch_argv('ua-puma9', 'fn.sh', depend=first)
        self.assertEqual(second[-2], '--dependency=afterok:111')
        other = om.native_sbatch_argv('ua-puma9', 'fn.sh', depend=222)
        self.assertEqual(other[-2], '--dependency=afterok:222')
        self.assertNotEqual(second, other)


class NativeRestartAndLogTests(unittest.TestCase):
    def test_restart_guard_requires_existing_file(self):
        lines = om.native_restart_guard_lines(
            '/tmp/olmt_native/ad/run/ad.elm.r.0201-01-01-00000.nc')
        text = '\n'.join(lines)
        self.assertIn('EXPECTED_FINIDAT=', text)
        self.assertIn('0201-01-01-00000.nc', text)
        self.assertIn('required restart missing', text)
        self.assertEqual(om.native_restart_guard_lines(''), [])
        self.assertEqual(om.native_restart_guard_lines(None), [])

    def test_restart_guard_fails_closed_in_bash(self):
        missing = '/no/such/phase6e/restart.nc'
        script = '#!/bin/bash\nset -euo pipefail\n' + '\n'.join(
            om.native_restart_guard_lines(missing)) + '\necho reached\n'
        result = subprocess.run(
            ['bash', '-s'], input=script, text=True,
            capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('required restart missing', result.stderr)
        self.assertNotIn('reached', result.stdout)

    def test_restart_guard_passes_when_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            restart = Path(tmp) / 'ad.elm.r.0201-01-01-00000.nc'
            restart.write_text('ok')
            script = '#!/bin/bash\nset -euo pipefail\n' + '\n'.join(
                om.native_restart_guard_lines(str(restart))) + '\necho reached\n'
            result = subprocess.run(
                ['bash', '-s'], input=script, text=True,
                capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('reached', result.stdout)

    def test_successful_wrappers_delete_slurm_logs_on_puma_and_perlmutter(self):
        self.assertTrue(om.native_wrapper_deletes_slurm_logs('ua-puma9'))
        self.assertTrue(om.native_wrapper_deletes_slurm_logs('pm-cpu'))


class NativeExitStatusTests(unittest.TestCase):
    def test_background_model_failure_is_nonzero(self):
        script = r'''#!/bin/bash -e
e3sm_pids=()
false > /dev/null &
e3sm_pids+=($!)
e3sm_status=0
for pid in "${e3sm_pids[@]}"; do
  wait $pid || e3sm_status=1
done
if [ $e3sm_status -ne 0 ]; then
    echo "Error: e3sm.exe failed. Aborting post-processing."
    exit 1
fi
echo should_not_postprocess
'''
        result = subprocess.run(
            ['bash', '-s'], input=script, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('e3sm.exe failed', result.stdout)
        self.assertNotIn('should_not_postprocess', result.stdout)

    def test_postproc_failure_is_nonzero_and_keeps_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'slurm_error_123.out'
            log.write_text('keep me')
            script = r'''#!/bin/bash -e
postproc_status=0
set +e
false
if [ $? -ne 0 ]; then postproc_status=1; fi
set -e
if [ $postproc_status -ne 0 ]; then
    echo "Error: postprocessing failed." >&2
    exit 1
fi
rm -v ''' + str(log) + r'''
'''
            result = subprocess.run(
                ['bash', '-s'], input=script, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(log.exists())


class NativeWrapperGenerationTests(unittest.TestCase):
    def _write_wrapper(self, tmp, machine, has_finidat=True, postproc=True):
        try:
            from model_ELM.ensemble import create_multisite_script
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        casedir = Path(tmp) / 'case'
        casedir.mkdir()
        (casedir / 'software_environment.txt').write_text(
            'LD_LIBRARY_PATH = /tmp/lib\n')
        finidat = str(Path(tmp) / 'ad' / 'run' /
                      'AD.elm.r.0201-01-01-00000.nc')
        fake = SimpleNamespace(
            casedir=str(casedir),
            caseroot=str(Path(tmp) / 'cases'),
            runroot=str(Path(tmp) / 'run'),
            casename='ABBY_ctrlvertsoc_I1850CNPRDCTCBC',
            site='ABBY',
            machine=machine,
            queue='standard' if machine == 'ua-puma9' else 'regular',
            project='chopinsong' if machine == 'ua-puma9' else 'm4803',
            np=1,
            exeroot=str(Path(tmp) / 'bld'),
            noslurm=False,
            OLMTdir=str(ROOT),
            OLMT_condaenv='OLMT_puma',
            case_options={},
            has_finidat=has_finidat,
            finidat=finidat if has_finidat else '',
            postproc_vars=['GPP', 'NEE'] if postproc else [],
            postproc_freq='hourly',
            compset='I1850CNPRDCTCBC',
            xmlquery=lambda key: '94',
        )
        old = os.getcwd()
        try:
            os.chdir(casedir)
            return Path(create_multisite_script(
                fake, ['ABBY'], str(casedir), walltime='03:00:00'))
        finally:
            os.chdir(old)

    def test_puma_wrapper_has_restart_guard_mpirun_and_deletes_logs_on_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_wrapper(tmp, 'ua-puma9')
            text = path.read_text()
            self.assertIn('#SBATCH --partition=standard', text)
            self.assertIn('#SBATCH --account=chopinsong', text)
            self.assertIn('#SBATCH --ntasks=1', text)
            self.assertIn('#SBATCH --cpus-per-task=1', text)
            self.assertIn('mpirun -np 1', text)
            self.assertIn('2>&1', text)
            self.assertNotIn('srun -n', text)
            self.assertIn('EXPECTED_FINIDAT=', text)
            self.assertIn('0201-01-01-00000.nc', text)
            self.assertIn('wait $pid || e3sm_status=1', text)
            self.assertIn('Error: e3sm.exe failed', text)
            self.assertIn('Error: postprocessing failed', text)
            self.assertIn('rm -v', text)
            self.assertIn('slurm_error_${SLURM_JOB_ID}', text)
            self.assertGreater(text.rfind('rm -v'), text.rfind('postprocessing failed'))
            self.assertIn('micromamba run -n OLMT_puma python manage_postproc.py', text)

    def test_ad_wrapper_omits_restart_guard_but_deletes_logs_after_model_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_wrapper(
                tmp, 'ua-puma9', has_finidat=False, postproc=False)
            text = path.read_text()
            self.assertNotIn('EXPECTED_FINIDAT=', text)
            self.assertIn('mpirun -np 1', text)
            self.assertIn('2>&1', text)
            self.assertIn('rm -v', text)
            self.assertIn('slurm_error_${SLURM_JOB_ID}', text)
            self.assertGreater(text.rfind('rm -v'), text.rfind('e3sm.exe failed'))

    def test_perlmutter_wrapper_still_deletes_logs_and_uses_srun(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_wrapper(tmp, 'pm-cpu')
            text = path.read_text()
            self.assertIn('srun -n 1 -c 1', text)
            self.assertIn('2>&1', text)
            self.assertNotIn('mpirun -np', text)
            self.assertIn('EXPECTED_FINIDAT=', text)
            self.assertIn('rm -v', text)
            self.assertIn('slurm_error_${SLURM_JOB_ID}', text)


class NativeSubmitCaseTests(unittest.TestCase):
    def test_submit_case_uses_native_sbatch_afterok_not_cime_prereq(self):
        try:
            from model_ELM.main import ELMcase
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        case = ELMcase(
            machine='ua-puma9', queue='standard', project='chopinsong',
            caseroot='/tmp/cases', runroot='/tmp/run', inputdata='/tmp/in',
            modelroot='/tmp/e3sm', compiler='gnu', mpilib='openmpi',
            olmtdir=str(ROOT))
        case.casedir = str(ROOT)
        case.casename = 'ABBY_ctrlvertsoc_I1850CNPRDCTCBC'
        case.noslurm = False
        captured = {}

        def fake_run(cmd, **kwargs):
            captured['cmd'] = list(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout='24716000\n')

        with mock.patch.object(case, 'create_pkl'), \
                mock.patch('model_ELM.main.subprocess.run', side_effect=fake_run):
            job = case.submit_case(
                depend=24715999, ensemble=False,
                multisite_script='/tmp/fn.sh')
        self.assertEqual(job, 24716000)
        self.assertEqual(
            captured['cmd'],
            ['sbatch', '--parsable', '--export=ALL',
             '--dependency=afterok:24715999', '/tmp/fn.sh'])
        self.assertNotIn('--prereq', captured['cmd'])
        self.assertNotIn('./case.submit', captured['cmd'])

    def test_cime_case_submit_prereq_path_unchanged_without_native_script(self):
        try:
            from model_ELM.main import ELMcase
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        case = ELMcase(
            machine='pm-cpu', queue='regular', project='m4803',
            caseroot='/tmp/cases', runroot='/tmp/run',
            olmtdir=str(ROOT))
        case.casedir = str(ROOT)
        case.casename = 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC'
        case.noslurm = False
        captured = {}

        def fake_run(cmd, **kwargs):
            captured['cmd'] = list(cmd)
            return subprocess.CompletedProcess(
                cmd, 0, stdout='Submitted batch job 99\n')

        with mock.patch.object(case, 'create_pkl'), \
                mock.patch('model_ELM.main.subprocess.run', side_effect=fake_run):
            job = case.submit_case(depend=88, ensemble=False, multisite_script='')
        self.assertEqual(job, 99)
        self.assertEqual(captured['cmd'], ['./case.submit', '--prereq', '88'])

    def test_dump_pickles_writes_casename_files(self):
        try:
            from model_ELM.main import ELMcase
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        with tempfile.TemporaryDirectory() as tmp:
            olmtdir = Path(tmp) / 'olmt'
            casedir = Path(tmp) / 'case'
            olmtdir.mkdir()
            casedir.mkdir()
            case = ELMcase(
                machine='ua-puma9', queue='standard', project='chopinsong',
                caseroot=str(Path(tmp) / 'cases'), runroot=str(Path(tmp) / 'run'),
                olmtdir=str(olmtdir))
            case.casename = 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC'
            case.casedir = str(casedir)
            case.dump_pickles()
            self.assertTrue(
                (casedir / 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC.pkl').is_file())
            self.assertTrue(
                (olmtdir / 'pklfiles' / 'ABBY_ctrlvertsoc_I20TRCNPRDCTCBC.pkl'
                 ).is_file())


if __name__ == '__main__':
    unittest.main()
