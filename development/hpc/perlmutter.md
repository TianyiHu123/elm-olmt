# Perlmutter Site Profile

Use this profile for NERSC Perlmutter Slurm operations. Record this path in the iteration
runtime contract before submission.

## Scheduler Operations

| Purpose | Command |
| --- | --- |
| Submit | `sbatch --export=ALL,<KEY=VALUE,...> <script>` |
| Queue state and pending reason | `squeue -j <job_ids>` |
| Start estimate | `squeue --start -j <job_id>` |
| Terminal accounting | `sacct -j <job_ids> --format=JobID,JobName,Partition,Account,AllocTRES,State,ExitCode,Elapsed` |
| Cancel | `scancel <job_ids>` |
| Efficiency report | `seff <job_id>` |

For a variant matrix, submit one job or array per variant and monitor the full comma-separated
job set concurrently.

## Required Submission Inputs

Set these explicitly in the canonical script or documented submit command:

- account;
- QOS;
- constraint;
- nodes, tasks, CPUs per task, memory, and walltime;
- GPU allocation when applicable;
- job-array range and output/error paths when applicable;
- exported variant and runtime variables.

The current spinup-surrogate CPU scripts use `#SBATCH --account=m4803`,
`--constraint=cpu`, `--qos=shared`, one node, one task, four CPUs per task, `48GB`, and
`00:30:00`. These are iteration-specific defaults, not portable constants; validate account
and QOS availability before use.

## Environment and Storage

- Capture the repository root, activated environment name, and scratch output root in the
  iteration's provenance ledger.
- Use the site's configured scratch root for heavy raw outputs. Keep compact summaries and
  canonical scripts in the repository.
- Check available capacity and account policy before requesting resource increases.

### Repository Python environment (Python 3.11)

For new Perlmutter Python workloads, use `OLMT_pm_TianyiPY311` (not the legacy py39
`OLMT_pm_Tianyi` env). Spec file: `conda_envs/OLMT_pm_py311.yml`.

Install prefix (primary provenance path):

```text
/global/common/software/m4803/conda/envs/OLMT_pm_TianyiPY311
```

Create the environment with NERSC conda after loading the module. Prefer `mamba` when it
is on `PATH` after `module load conda`. Creating this environment on a login node is
acceptable; use a compute-node session only if the solver is unusually long. Do not treat
env creation as part of a science workload without separate execution authority.

```bash
module load conda
# Prefer mamba when available:
mamba env create -f conda_envs/OLMT_pm_py311.yml \
  --prefix /global/common/software/m4803/conda/envs/OLMT_pm_TianyiPY311
# Fallback:
# conda env create -f conda_envs/OLMT_pm_py311.yml \
#   --prefix /global/common/software/m4803/conda/envs/OLMT_pm_TianyiPY311
```

Activate and verify:

```bash
module load conda
conda activate /global/common/software/m4803/conda/envs/OLMT_pm_TianyiPY311
python --version   # expect 3.11.x
```

Optional: keep `/global/common/software/m4803/conda/envs` in conda `envs_dirs` (see
`~/.condarc`) so short-name activation works:

```bash
module load conda
conda activate OLMT_pm_TianyiPY311
```

Job scripts may still record the full `--prefix` path for provenance.

Smoke check after create or repair:

```bash
python -c "import numpy, scipy, pandas, netCDF4, xarray, sklearn, SALib, emcee, pathos, matplotlib, cartopy, geopy; print('ok')"
ncks --version
```

Historical scripts that activate `OLMT_pm_Tianyi` (Python 3.9) remain provenance; do not
rewrite them solely to adopt this environment. Do not use Puma micromamba conventions on
Perlmutter.

## Launch Convention

The existing single-task canonical spinup scripts launch Python directly inside the Slurm
allocation. That is the supported convention for their `--ntasks=1` workload; do not require
`srun` solely because the job is submitted through Slurm.

Use `srun` when the script launches multiple Slurm tasks, MPI ranks, or a site requirement
specifically calls for it. Every new canonical script must state its chosen launch convention
and request resources consistent with it.

## Pre-submit and Monitoring Checklist

1. Verify the script exists and its resource directives are explicit.
2. Verify canonical and submitted copies have identical SHA-256 hashes.
3. Record commit plus dirty-diff/source-manifest provenance.
4. Show the exact `sbatch` command and obtain runtime-contract authority.
5. Record job IDs immediately after submission.
6. Use `squeue` while jobs are active and `sacct` after terminal state; record state, exit
   code, elapsed time, and resource diagnostics.
7. Use `seff` when diagnosing memory headroom or CPU efficiency.

## Failure Diagnostics

Capture accounting evidence and distinguish scheduler/account policy errors, resource
exhaustion, launch-layout mismatch, and application failures. Only retry resource/scheduler
failures once within the iteration's declared caps. Code or configuration changes require fresh
user authorization before retry.
