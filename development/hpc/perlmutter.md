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
