---
name: perlmutter-slurm-jobops
description: Submit, monitor, and triage Slurm jobs on NERSC Perlmutter. Use when preparing sbatch submissions, checking squeue/sacct status, or diagnosing failed jobs.
disable-model-invocation: true
---

# Perlmutter Slurm JobOps

## Use When

- Submitting Perlmutter batch jobs with `sbatch`
- Monitoring pending/running jobs with `squeue`
- Getting terminal outcome with `sacct`
- Diagnosing failed/time-out/cancelled/OOM jobs

## Safety and Control

- User remains responsible for commands, resources, and scientific correctness.
- Confirm HPC context and ask user permission before execution actions.
- Use login nodes for edit/prepare/submit/monitor only; do not run heavy workloads directly on login nodes.
- Prefer smallest concrete step, then verify using command output evidence.

## Required Submission Inputs

Collect or confirm:

- script path
- canonical script path (if submit script is a copied version)
- `--account`
- `--qos`
- `--constraint` (required at NERSC)
- `--nodes`
- `--time`
- GPU request (`--gpus` or `--gpus-per-node`) for GPU jobs
- any job-specific export vars

## Pre-Submit Checks

Before `sbatch`:

1. Verify script exists and is readable.
2. Verify required Slurm options are set explicitly (do not rely on defaults).
3. Verify workload launch uses `srun` inside the script.
4. If using a copied submit script, compare canonical and submit script checksums and confirm they match.
5. Show the exact `sbatch` command before running it.
6. Warn that quota/account issues can reject submission (or fail later at `srun` time).

## Submission Pattern

Use:

`sbatch --export=ALL,<KEY=VALUE,...> <script_path>`

After submit:

- capture `job_id`
- record submit timestamp, script path, exports, and command used
- record script checksum(s) and source commit hash when available

## Monitoring Pattern

Use these commands:

- Start estimate / pending reason:
  `squeue --start -j <job_id>`
- Current queue state:
  `squeue -j <job_id>`
- Final state and exit code:
  `sacct -j <job_id> --format=JobID,JobName,Partition,Account,AllocTRES,State,ExitCode,Elapsed`

## Failure Triage

If final state is not `COMPLETED`:

1. Capture `State` and `ExitCode` from `sacct`.
2. Capture pending/failure reason from `squeue`/`sacct`.
3. Categorize likely cause:
   - invalid/missing Slurm option (account/qos/constraint/time/resources)
   - quota/account/policy limit
   - resource mismatch (CPU/GPU/task layout)
   - application/runtime error
4. Propose the smallest next fix and one verification step.

Retry policy:

- Retry once after a minimal fix.
- If second run fails, mark the job `blocked` and escalate to user with evidence and options.
- Do not make higher-level experiment decisions; caller workflow must request user decision when blocked jobs exist.
- On blocked jobs, return a debug bundle suitable for next-session troubleshooting.

## Return Format

Always report:

- `job_id`
- submit command used
- `state`
- `exit_code` (if available)
- pending/failure reason (if available)
- canonical/submitted script checksum status (when applicable)
- source commit hash (when available)
- `blocked` (true/false)
- recommended next step
- debug bundle fields (when blocked): `job_id`, `state`, `exit_code`, reason, script paths, checksums, key `squeue`/`sacct` output snippets
