import configparser
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import OLMTmachine as om  # noqa: E402


CFG_CIME = ROOT / 'examples' / 'ua_puma' / 'ABBY_ctrlvertsoc_cime_exec.cfg'
CFG_NATIVE = ROOT / 'examples' / 'ua_puma' / 'ABBY_ctrlvertsoc_olmt_native.cfg'

FORBIDDEN_PATH_SNIPPETS = (
    '/global/homes',
    '/pscratch/',
    '/global/cfs/',
    '/E3SM_out/SOIL_project',
    'elm_puma_abby_',
    'NEON_ppe',
    '/xdisk/chopinsong/tianyihu/elm-olmt/',
)


def _load_cfg(path):
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.optionxform = str
    parser.read(path)
    cfg = {}
    for section in parser.sections():
        cfg[section] = {}
        for key, value in parser.items(section, raw=False):
            cfg[section][key] = value.strip().strip("'\"")
    return cfg


class MachineDetectionTests(unittest.TestCase):
    def test_puma_default_paths(self):
        defaults = om.puma_machine_defaults()
        self.assertEqual(defaults['machine'], 'ua-puma9')
        self.assertEqual(defaults['queue'], 'standard')
        self.assertEqual(defaults['project'], 'chopinsong')
        self.assertEqual(
            defaults['inputdata'],
            '/xdisk/chopinsong/tianyihu/e3sm_inputdata')
        self.assertEqual(
            defaults['rootdir'],
            '/xdisk/chopinsong/tianyihu/E3SM_out/port_uapuma')

    def test_explicit_ua_puma9_and_puma_alias(self):
        self.assertTrue(om.machine_name_selects_ua_puma9('ua-puma9'))
        self.assertTrue(om.machine_name_selects_ua_puma9('puma'))
        self.assertTrue(om.is_ua_puma9('ua-puma9'))

    def test_puma_compute_and_login_hostnames(self):
        self.assertTrue(om.machine_name_selects_ua_puma9(
            'r7u17n2.puma.hpc.arizona.edu'))
        self.assertTrue(om.machine_name_selects_ua_puma9(
            'wentletrap.puma.hpc.arizona.edu'))
        self.assertTrue(om.machine_name_selects_ua_puma9('junonia'))

    def test_perlmutter_names_are_not_puma(self):
        self.assertFalse(om.machine_name_selects_ua_puma9('pm-cpu'))
        self.assertFalse(om.machine_name_selects_ua_puma9('login01.nersc.gov'))
        self.assertFalse(om.machine_name_selects_ua_puma9('login'))
        self.assertFalse(om.is_ua_puma9('pm-cpu'))

    def test_puma_login_hostname_containing_login_selects_puma(self):
        self.assertTrue(om.machine_name_selects_ua_puma9(
            'login01.puma.hpc.arizona.edu'))
        self.assertIn('login', 'login01.puma.hpc.arizona.edu')

    def test_get_machine_info_puma_and_perlmutter(self):
        try:
            from OLMTutils import get_machine_info
        except Exception as exc:
            self.skipTest('OLMTutils import unavailable: '+str(exc))
        machine, rootdir, inputdata, queue, project, hostname = get_machine_info(
            machine_name='ua-puma9')
        self.assertEqual(machine, 'ua-puma9')
        self.assertEqual(queue, 'standard')
        self.assertEqual(project, 'chopinsong')
        self.assertEqual(inputdata, '/xdisk/chopinsong/tianyihu/e3sm_inputdata')
        self.assertIn('port_uapuma', rootdir)
        self.assertEqual(hostname, 'puma.hpc.arizona.edu')
        self.assertEqual(om.puma_machine_defaults()['machine'], 'ua-puma9')

        env = os.environ.copy()
        os.environ['SCRATCH'] = '/tmp/pm_scratch'
        try:
            machine, rootdir, inputdata, queue, project, hostname = get_machine_info(
                machine_name='pm-cpu')
        finally:
            if 'SCRATCH' in env:
                os.environ['SCRATCH'] = env['SCRATCH']
            else:
                os.environ.pop('SCRATCH', None)
        self.assertEqual(machine, 'pm-cpu')
        self.assertEqual(rootdir, '/tmp/pm_scratch')
        self.assertEqual(inputdata, '/global/cfs/cdirs/e3sm/inputdata')

        os.environ['SCRATCH'] = '/tmp/pm_scratch'
        try:
            machine, _, inputdata, queue, project, _ = get_machine_info(
                machine_name='login01.puma.hpc.arizona.edu')
            self.assertEqual(machine, 'ua-puma9')
            self.assertEqual(queue, 'standard')
            self.assertEqual(project, 'chopinsong')
            self.assertEqual(
                inputdata, '/xdisk/chopinsong/tianyihu/e3sm_inputdata')

            machine, rootdir, inputdata, queue, project, _ = get_machine_info(
                machine_name='login01.nersc.gov')
            self.assertEqual(machine, 'pm-cpu')
            self.assertEqual(rootdir, '/tmp/pm_scratch')
            self.assertEqual(inputdata, '/global/cfs/cdirs/e3sm/inputdata')
        finally:
            if 'SCRATCH' in env:
                os.environ['SCRATCH'] = env['SCRATCH']
            else:
                os.environ.pop('SCRATCH', None)

    def test_hostname_autodetect_puma(self):
        try:
            from OLMTutils import get_machine_info
        except Exception as exc:
            self.skipTest('OLMTutils import unavailable: '+str(exc))
        old = os.environ.get('HOSTNAME')
        os.environ['HOSTNAME'] = 'r4u07n2.puma.hpc.arizona.edu'
        try:
            machine, _, _, queue, project, _ = get_machine_info(machine_name='')
        finally:
            if old is None:
                os.environ.pop('HOSTNAME', None)
            else:
                os.environ['HOSTNAME'] = old
        self.assertEqual(machine, 'ua-puma9')
        self.assertEqual(queue, 'standard')
        self.assertEqual(project, 'chopinsong')

    def test_hostname_autodetect_puma_login_containing_login(self):
        try:
            from OLMTutils import get_machine_info
        except Exception as exc:
            self.skipTest('OLMTutils import unavailable: '+str(exc))
        old_host = os.environ.get('HOSTNAME')
        old_scratch = os.environ.get('SCRATCH')
        os.environ['HOSTNAME'] = 'login01.puma.hpc.arizona.edu'
        os.environ['SCRATCH'] = '/tmp/pm_scratch'
        try:
            machine, _, inputdata, queue, project, _ = get_machine_info(
                machine_name='')
        finally:
            if old_host is None:
                os.environ.pop('HOSTNAME', None)
            else:
                os.environ['HOSTNAME'] = old_host
            if old_scratch is None:
                os.environ.pop('SCRATCH', None)
            else:
                os.environ['SCRATCH'] = old_scratch
        self.assertEqual(machine, 'ua-puma9')
        self.assertEqual(queue, 'standard')
        self.assertEqual(project, 'chopinsong')
        self.assertEqual(
            inputdata, '/xdisk/chopinsong/tianyihu/e3sm_inputdata')


class ELMcaseCompilerMpilibTests(unittest.TestCase):
    def test_constructor_keeps_cfg_compiler_and_mpilib(self):
        try:
            from model_ELM.main import ELMcase
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        case = ELMcase(
            machine='ua-puma9', queue='standard', project='chopinsong',
            caseroot='/tmp/cases', runroot='/tmp/run', inputdata='/tmp/in',
            modelroot='/tmp/e3sm', compiler='gnu', mpilib='openmpi',
            olmtdir=str(ROOT))
        self.assertEqual(case.compiler, 'gnu')
        self.assertEqual(case.mpilib, 'openmpi')
        case.assign_casename(casename='ABBY_ctrlvertsoc_I1850CNRDCTCBC_ad_spinup',
                             walltime='03:00:00')
        cmd = case.create_newcase_command()
        self.assertIn('--compiler gnu', cmd)
        self.assertIn('--mpilib openmpi', cmd)
        self.assertIn('--mach ua-puma9', cmd)

    def test_constructor_empty_defaults_omit_flags(self):
        try:
            from model_ELM.main import ELMcase
        except Exception as exc:
            self.skipTest('model_ELM import unavailable: '+str(exc))
        case = ELMcase(
            machine='pm-cpu', queue='shared', project='m4803',
            caseroot='/tmp/cases', runroot='/tmp/run',
            olmtdir=str(ROOT))
        self.assertEqual(case.compiler, '')
        self.assertEqual(case.mpilib, '')
        case.assign_casename(casename='perlmutter_case', walltime='02:00:00')
        cmd = case.create_newcase_command()
        self.assertNotIn('--compiler', cmd)
        self.assertNotIn('--mpilib', cmd)


class CreateNewcaseArgumentTests(unittest.TestCase):
    def test_empty_compiler_mpilib_omitted_for_perlmutter(self):
        cmd = om.create_newcase_command(
            casedir='/tmp/case', machine='pm-cpu', compset='I1850CNRDCTCBC',
            res='hcru_hcru', walltime='02:00:00', project='m4803',
            compiler='', mpilib='', queue='shared')
        self.assertIn('--mach pm-cpu', cmd)
        self.assertIn('--project m4803', cmd)
        self.assertIn('--queue shared', cmd)
        self.assertNotIn('--compiler', cmd)
        self.assertNotIn('--mpilib', cmd)

    def test_puma_cfg_values_propagate(self):
        cmd = om.create_newcase_command(
            casedir='/xdisk/chopinsong/tianyihu/E3SM_port/cases/olmt_abby/cime_exec/ABBY',
            machine='ua-puma9', compset='I1850CNRDCTCBC', res='hcru_hcru',
            walltime='03:00:00', project='chopinsong', compiler='gnu',
            mpilib='openmpi', queue='standard',
            log_path='/tmp/create_newcase.log')
        self.assertIn('--mach ua-puma9', cmd)
        self.assertIn('--compiler gnu', cmd)
        self.assertIn('--mpilib openmpi', cmd)
        self.assertIn('--project chopinsong', cmd)
        self.assertIn('--queue standard', cmd)
        self.assertIn('> /tmp/create_newcase.log', cmd)

    def test_puma_refuses_existing_casedir(self):
        self.assertTrue(om.puma_blocks_existing_casedir('ua-puma9', True))
        self.assertFalse(om.puma_blocks_existing_casedir('ua-puma9', False))
        self.assertFalse(om.puma_blocks_existing_casedir('pm-cpu', True))


class SlurmGenerationTests(unittest.TestCase):
    def test_perlmutter_ensemble_keeps_constraint_and_qos(self):
        lines = om.slurm_batch_directives(
            'pm-cpu', '06:00:00', 'regular', 'm4803', 'job', 2,
            ntasks=512, flavor='ensemble')
        text = '\n'.join(lines)
        self.assertIn('#SBATCH --constraint=cpu', text)
        self.assertIn('#SBATCH --qos=regular', text)
        self.assertIn('#SBATCH --account=m4803', text)
        self.assertNotIn('--partition', text)
        self.assertNotIn('mpirun', text)

    def test_puma_multisite_uses_partition_ntasks_and_mpirun(self):
        lines = om.slurm_batch_directives(
            'ua-puma9', '03:00:00', 'standard', 'chopinsong', 'ABBY_ctrlvertsoc',
            1, ntasks=1, flavor='multisite')
        text = '\n'.join(lines)
        self.assertIn('#SBATCH --partition=standard', text)
        self.assertIn('#SBATCH --account=chopinsong', text)
        self.assertIn('#SBATCH --ntasks=1', text)
        self.assertIn('#SBATCH --cpus-per-task=1', text)
        self.assertNotIn('--constraint', text)
        self.assertNotIn('--qos=', text)
        launch = om.e3sm_launch_command(
            'ua-puma9', 1, '/tmp/bld', '/tmp/run/e3sm_log.txt')
        self.assertTrue(launch.startswith('mpirun -np 1 '))
        self.assertIn('2>&1', launch)
        self.assertNotIn('srun', launch)

    def test_perlmutter_launch_remains_srun(self):
        launch = om.e3sm_launch_command(
            'pm-cpu', 1, '/tmp/bld', '/tmp/run/e3sm_log.txt')
        self.assertTrue(launch.startswith('srun -n 1 -c 1 '))
        self.assertIn('2>&1', launch)

    def test_puma_python_uses_micromamba(self):
        preamble = om.olmt_python_preamble_lines('ua-puma9', 'OLMT_puma')
        self.assertEqual(preamble, ['module load micromamba/2.0.2-2'])
        cmd = om.olmt_python_command(
            'ua-puma9', 'OLMT_puma', './manage_ensemble.py --case X')
        self.assertEqual(
            cmd, 'micromamba run -n OLMT_puma python manage_ensemble.py --case X')
        pm = om.olmt_python_command(
            'pm-cpu', 'OLMT_pm_TianyiPY311', './manage_ensemble.py --case X')
        self.assertEqual(pm, './manage_ensemble.py --case X')


class TempCleanupTests(unittest.TestCase):
    def test_cleanup_only_workspace_temp_and_skips_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / 'olmt'
            temp_dir = workspace / 'temp'
            outside = Path(tmp) / 'outside'
            temp_dir.mkdir(parents=True)
            outside.mkdir()
            inside = temp_dir / 'clm_params.nc'
            inside.write_text('ok')
            stray = outside / 'secret.nc'
            stray.write_text('no')
            link = temp_dir / 'escape.nc'
            link.symlink_to(stray)
            removed = om.cleanup_olmt_temp(str(workspace))
            self.assertEqual(removed, [str(inside.resolve())])
            self.assertFalse(inside.exists())
            self.assertTrue(stray.exists())
            self.assertTrue(link.exists())

    def test_cleanup_refuses_workspace_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            removed = om.cleanup_olmt_temp(tmp)
            self.assertEqual(removed, [])


class AbbyCfgTests(unittest.TestCase):
    def _assert_isolated_puma_cfg(self, path, caseroot_tail, runroot_tail):
        cfg = _load_cfg(path)
        machine = cfg['machine']
        self.assertEqual(machine.get('machine_name'), 'ua-puma9')
        self.assertEqual(machine.get('compiler'), 'gnu')
        self.assertEqual(machine.get('mpilib'), 'openmpi')
        self.assertEqual(machine.get('queue'), 'standard')
        self.assertEqual(machine.get('project'), 'chopinsong')
        self.assertEqual(machine.get('olmt_condaenv'), 'OLMT_puma')
        self.assertIn('simulation', cfg)
        self.assertNotIn('ensemble', cfg)
        self.assertEqual(cfg['simulation'].get('sites'), 'ABBY')
        self.assertTrue(machine.get('caseroot').endswith(caseroot_tail))
        self.assertTrue(machine.get('runroot').endswith(runroot_tail))
        self.assertEqual(
            cfg['simulation'].get('metdir'),
            '/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/ABBY')
        self.assertNotIn('CLM1PT_data', cfg['simulation'].get('metdir'))
        self.assertNotIn('1x1pt_ABBY', cfg['simulation'].get('metdir'))
        for section in cfg.values():
            for value in section.values():
                for snippet in FORBIDDEN_PATH_SNIPPETS:
                    self.assertNotIn(
                        snippet, value, msg=snippet+' in '+path.name+' value '+value)
        self.assertNotEqual(machine.get('caseroot'), machine.get('runroot'))

    def test_cime_exec_cfg(self):
        self._assert_isolated_puma_cfg(
            CFG_CIME,
            'E3SM_port/cases/olmt_abby/cime_exec',
            'port_uapuma/olmt_abby/cime_exec')

    def test_olmt_native_cfg_is_isolated_from_cime_exec(self):
        self._assert_isolated_puma_cfg(
            CFG_NATIVE,
            'E3SM_port/cases/olmt_abby/olmt_native',
            'port_uapuma/olmt_abby/olmt_native')
        cime = _load_cfg(CFG_CIME)
        native = _load_cfg(CFG_NATIVE)
        self.assertNotEqual(
            cime['machine'].get('caseroot'), native['machine'].get('caseroot'))
        self.assertNotEqual(
            cime['machine'].get('runroot'), native['machine'].get('runroot'))


if __name__ == '__main__':
    unittest.main()
