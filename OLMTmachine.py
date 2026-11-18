"""Machine-portable helpers for OLMT.

Puma-specific behavior lives here so Perlmutter paths in the drivers stay
unchanged unless an explicit ua-puma9 machine is selected. This module is
stdlib-only so unit tests can run without the OLMT conda stack.
"""
import glob
import os

PUMA_MACHINE_ID = 'ua-puma9'
PUMA_MICROMAMBA_MODULE = 'micromamba/2.0.2-2'
PUMA_DEFAULT_CONDAENV = 'OLMT_puma'
PUMA_LOGIN_SHORT_NAMES = ('wentletrap', 'junonia')

PUMA_DEFAULTS = {
    'machine': PUMA_MACHINE_ID,
    'rootdir': '/xdisk/chopinsong/tianyihu/E3SM_out/port_uapuma',
    'inputdata': '/xdisk/chopinsong/tianyihu/e3sm_inputdata',
    'queue': 'standard',
    'project': 'chopinsong',
    'hostname': 'puma.hpc.arizona.edu',
}


def is_ua_puma9(machine):
    return PUMA_MACHINE_ID in str(machine or '')


def machine_name_selects_ua_puma9(machine_name):
    """Return True when a cfg name or hostname should map to ua-puma9.

    Intentionally does not treat a bare 'puma' substring as a match, and does
    not overlap Perlmutter's 'login' heuristic.
    """
    name = str(machine_name or '').strip()
    if not name:
        return False
    lowered = name.lower()
    if lowered in ('ua-puma9', 'puma'):
        return True
    if 'ua-puma9' in lowered:
        return True
    if 'puma.hpc.arizona.edu' in lowered:
        return True
    short = lowered.split('.')[0]
    if short in PUMA_LOGIN_SHORT_NAMES:
        return True
    return False


def puma_machine_defaults():
    return dict(PUMA_DEFAULTS)


def create_newcase_command(casedir, machine, compset, res, walltime,
                           project='', compiler='', mpilib='', queue='',
                           log_path=''):
    """Build the create_newcase command string used by ELMcase.create_case.

    Empty compiler/mpilib/project/queue omit those flags, preserving the
    Perlmutter behavior of taking CIME machine defaults.
    """
    cmd = ('./create_newcase --case ' + casedir + ' --mach ' + machine
           + ' --compset ' + compset + ' --res ' + res
           + ' --walltime ' + walltime + ' --handle-preexisting-dirs u')
    if project != '':
        cmd = cmd + ' --project ' + project
    if compiler != '':
        cmd = cmd + ' --compiler ' + compiler
    if mpilib != '':
        cmd = cmd + ' --mpilib ' + mpilib
    if queue != '':
        cmd = cmd + ' --queue ' + queue
    if log_path != '':
        cmd = cmd + ' > ' + log_path
    return cmd


def puma_blocks_existing_casedir(machine, casedir_exists):
    """Puma never removes or interactively reuses an existing CIME case."""
    return is_ua_puma9(machine) and bool(casedir_exists)


def slurm_batch_directives(machine, walltime, queue, project, jobname, nnodes,
                           ntasks=None, output=None, error=None,
                           flavor='ensemble'):
    """Return #SBATCH lines (no shebang).

    flavor='ensemble' matches case.submit_ensemble.
    flavor='multisite' matches the one-site/multi-site wrapper, including the
    historical non-pm-cpu duplicate --time lines.
    """
    lines = []
    if 'pm-cpu' in str(machine):
        lines.append('#SBATCH --time=' + walltime)
        lines.append('#SBATCH --constraint=cpu')
        lines.append('#SBATCH --qos=' + queue)
        lines.append('#SBATCH --account=' + project)
    elif is_ua_puma9(machine):
        lines.append('#SBATCH --time=' + walltime)
        lines.append('#SBATCH --partition=' + queue)
        lines.append('#SBATCH --account=' + project)
    else:
        if flavor == 'multisite':
            lines.append('#SBATCH -t ' + str(walltime) + ':00:00')
            lines.append('#SBATCH -t ' + walltime)
        else:
            lines.append('#SBATCH -t ' + walltime)
        lines.append('#SBATCH -p ' + queue)
        if project != '':
            lines.append('#SBATCH -A ' + project)
    lines.append('#SBATCH -J ' + jobname)
    lines.append('#SBATCH --nodes=' + str(nnodes))
    if ntasks is not None:
        lines.append('#SBATCH --ntasks=' + str(ntasks))
    if is_ua_puma9(machine):
        lines.append('#SBATCH --cpus-per-task=1')
    if output:
        lines.append('#SBATCH --output=' + output)
    if error:
        lines.append('#SBATCH --error=' + error)
    return lines


def e3sm_launch_command(machine, np, exeroot, log_path, noslurm=False):
    """Background launch line written into the OLMT wrapper script."""
    exe = exeroot + '/e3sm.exe'
    if noslurm:
        return 'mpiexec -n ' + str(np) + ' ' + exe + ' > ' + log_path + ' &'
    if is_ua_puma9(machine):
        return 'mpirun -np ' + str(np) + ' ' + exe + ' > ' + log_path + ' &'
    return 'srun -n ' + str(np) + ' -c 1 ' + exe + ' > ' + log_path + ' &'


def olmt_python_preamble_lines(machine, env_name):
    if is_ua_puma9(machine):
        return ['module load ' + PUMA_MICROMAMBA_MODULE]
    return ['conda activate ' + env_name]


def olmt_python_command(machine, env_name, invocation):
    """Return the shell command that runs an OLMT Python entry point.

    Perlmutter keeps `conda activate` plus the original invocation. Puma uses
    `micromamba run -n <env> python ...` after the preamble module load.
    """
    if not is_ua_puma9(machine):
        return invocation
    env = env_name or PUMA_DEFAULT_CONDAENV
    text = invocation.strip()
    if text.startswith('python '):
        text = text[len('python '):]
    elif text.startswith('./'):
        text = text[2:]
    return 'micromamba run -n ' + env + ' python ' + text


def _is_inside(parent, path):
    try:
        return os.path.commonpath([parent, path]) == parent
    except ValueError:
        return False


def cleanup_olmt_temp(workspace_root, patterns=('*.nc', '*.tmp')):
    """Remove matching files only in <workspace_root>/temp.

    Refuses to follow symlinks or to touch anything whose real path is not
    inside that temp directory. Returns the list of removed paths.
    """
    root = os.path.realpath(os.path.abspath(workspace_root))
    temp_dir = os.path.realpath(os.path.join(root, 'temp'))
    if not _is_inside(root, temp_dir):
        return []
    if not os.path.isdir(temp_dir):
        return []
    removed = []
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(temp_dir, pattern)):
            if os.path.islink(file_path):
                continue
            real = os.path.realpath(file_path)
            if not _is_inside(temp_dir, real):
                continue
            if os.path.isfile(real):
                os.remove(real)
                removed.append(real)
    return removed
