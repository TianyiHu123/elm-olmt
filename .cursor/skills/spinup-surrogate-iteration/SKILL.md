---
name: spinup-surrogate-iteration
description: Run and document one full spinup surrogate development iteration including variants, Slurm execution, result aggregation, and decision logging.
disable-model-invocation: true
---

# Spinup Surrogate Iteration

## Use When

- Starting a new spinup surrogate iteration (for example `iter002`)
- Defining a variant matrix and Slurm runs
- Summarizing completed variant runs and selecting the next candidate

## Required Project Paths

- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/iterations/`
- `development/spinup_surrogate/summaries/`
- `development/spinup_surrogate/slurm/`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Execution Guardrails

- Confirm whether the current workspace/session is on HPC before execution.
- Ask user permission before execution, even when on HPC.
- For large tasks (multi-CPU, high-memory, long runs, seed arrays), use Slurm (`sbatch`).

## Iteration ID and Naming

- Iteration IDs must be zero-padded and sequential: `iter001`, `iter002`, ..., `iterXXX`.
- Use the current `iterXXX` consistently across iteration notes, Slurm paths, run naming, and summaries.

## Iteration Report Policy

- Every iteration must have a report at `development/spinup_surrogate/iterations/iterXXX.md`.
- Create/update that report from iteration start through closeout (not only at the end).
- At minimum, record: objective, controls/variants, submitted job IDs + states, summary metrics, decision, blockers, and next action.
- Include iteration status: `success` or `failed`.
- An iteration is not considered complete until `iterXXX.md` is updated and finalized.

## Variant Provenance Log (Required)

Inside `iterations/iterXXX.md`, keep a per-variant run ledger with:

- variant name
- canonical script path
- submitted script path
- canonical script checksum
- submitted script checksum
- source commit hash (`git rev-parse HEAD`)
- job ID(s) and final state
- retry notes (if any)

## Canonical Slurm Script Location

- For each new iteration, create/update scripts under `development/spinup_surrogate/slurm/iterXXX/`.
- Treat `development/spinup_surrogate/slurm/iterXXX/` as the source of truth for that iteration.
- If a script is copied elsewhere for execution convenience, keep the canonical copy in sync.

## Default Scratch Output Location

- Unless the user specifies otherwise, use:
  `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>`
- Replace `iterXXX` with the active iteration and `<VARIANT>` with variant name.

## Required Submission Procedure (Parallel Default)

Phase A - Prepare each variant in the matrix:

1. Ensure the canonical script exists in
   `development/spinup_surrogate/slurm/iterXXX/`.
2. If the user does not specify another submit location, copy the script to
   `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/`.
3. Verify canonical and submitted scripts are in sync via checksum compare.
4. Record checksums and source commit hash in `iterations/iterXXX.md` before submit.

Phase B - Submit all variants:

5. Submit exactly one job per variant with `VARIANT=<name>`, in parallel by default.
6. Record submitted script path and job ID per variant in `iterations/iterXXX.md` immediately after submit.

Phase C - Monitor all variants concurrently:

7. Monitor all submitted job IDs as one active set until every job reaches terminal state.
8. Record terminal `state`/`exit_code` and diagnostics per variant in `iterations/iterXXX.md`.

If the user explicitly asks for sequential execution, sequential submission/monitoring is allowed as an override.

Command pattern (example):

`sbatch --export=ALL,VARIANT=<VARIANT> /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/case.train_surrogate_spinup_iterXXX.slurm`

Sync-check example:

`sha256sum development/spinup_surrogate/slurm/iterXXX/case.train_surrogate_spinup_iterXXX.slurm /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/case.train_surrogate_spinup_iterXXX.slurm`

Use `.cursor/skills/perlmutter-slurm-jobops/SKILL.md` for batched submission and concurrent monitoring operations.

## Failed Job Handling

If `perlmutter-slurm-jobops` reports a variant job failure:

1. Record `job_id`, `state`, `exit_code`, and reason in `iterations/iterXXX.md`.
2. Do not aggregate that variant yet.
3. Apply one minimal fix (resources/script option/runtime command) and resubmit once.
4. If the retry still fails, mark that variant `blocked`.
5. Mark iteration status as `failed` in `iterations/iterXXX.md` and `registry.csv`.
6. Cancel all remaining active/pending variant jobs for the same iteration and log cancellation evidence.
7. Do not continue remaining variants, do not aggregate/compare, and do not select a winner.
8. Write a failure debug bundle in `iterations/iterXXX.md` containing:
   - blocked variant name
   - canonical/submitted script paths + checksums
   - source commit hash
   - job ID(s), `state`, `exit_code`, pending/failure reason
   - last `squeue`/`sacct` diagnostic snippets and next debug hypothesis
9. Update `handoff/CURRENT.md` with the failed status and debug entry point for next session.

## Required Aggregation Procedure (Per Variant)

For each variant:

1. Run `summarize_spinup_stats.py` using the variant's `surrogate_spinup` stats directory.
2. Use `--glob "surrogate_spinup_stats_seed*.json"`.
3. Write aggregate output to the variant run directory as `summary.json`.
4. Copy that `summary.json` to
   `development/spinup_surrogate/summaries/iterXXX/<variant>_summary.json`.

Command pattern:

`python summarize_spinup_stats.py --stats-dir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/surrogate_spinup --glob "surrogate_spinup_stats_seed*.json" --output-json /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/surrogate_spinup/summary.json`

## Commit Policy

- Do not commit every seed run or partial trial.
- Default: make one checkpoint commit per finished iteration milestone after iteration artifacts are updated.
- Optional: split into two commits only when it improves review clarity (for example code changes vs tracking/docs updates).
- If an iteration is aborted without meaningful tracked updates, skip creating a checkpoint commit.
- Include the iteration ID in the commit message (for example `iter002`).
- Keep large raw outputs in `UQ_output` out of git unless explicitly requested.

## Iteration Checklist

Copy this checklist into `development/spinup_surrogate/iterations/iterXXX.md` and keep it updated.

- [ ] Define objective and hypothesis
- [ ] Define fixed controls (case, split mode, train fraction, seed range)
- [ ] Define variants to compare
- [ ] Prepare/update Slurm scripts in `development/spinup_surrogate/slurm/iterXXX/`
- [ ] Copy script to default scratch variant directory unless user overrides path
- [ ] Verify canonical/submitted script sync with checksum compare
- [ ] Record per-variant provenance (`commit hash`, checksums, job IDs/states) in `iterations/iterXXX.md`
- [ ] Invoke `perlmutter-slurm-jobops` to submit one job per variant (`VARIANT=<name>`) with parallel default
- [ ] Monitor all variant job IDs concurrently until terminal states are known
- [ ] Log submitted script path, job ID, and final state in `development/spinup_surrogate/iterations/iterXXX.md`
- [ ] For failed variants, follow Failed Job Handling section before aggregation
- [ ] If any variant is blocked after retry, terminate iteration as `failed` and write failure debug bundle
- [ ] If no blocked variants, aggregate each variant with `summarize_spinup_stats.py` and copy summary JSON to `development/spinup_surrogate/summaries/iterXXX/`
- [ ] If no blocked variants, compare variants with consistent metrics
- [ ] If no blocked variants, select winner and record decision
- [ ] Finalize `development/spinup_surrogate/iterations/iterXXX.md` with outcomes and rationale
- [ ] Update `development/spinup_surrogate/registry.csv`
- [ ] Update `development/spinup_surrogate/handoff/CURRENT.md`
- [ ] Create checkpoint commit(s) per Commit Policy with iteration ID in message

## Standard Comparison Metrics

For each target variable (`TOTSOMC`, `TOTSOMN`), report:

- median and IQR of `r2_val`
- median `r2_gap`
- median and IQR of `rmse_ratio`
- `overfit_warning_fraction`
- tails (`min r2_val`, `max rmse_ratio`)

IQR definition:

- `IQR = p75 - p25` using the `p25` and `p75` fields from each variant summary JSON.

## Required Outputs Per Iteration

- finalized `development/spinup_surrogate/iterations/iterXXX.md`
- `development/spinup_surrogate/summaries/iterXXX/<variant>_summary.json`
- one new row in `development/spinup_surrogate/registry.csv`
- updated `development/spinup_surrogate/handoff/CURRENT.md`
- checkpoint commit(s) per Commit Policy referencing `iterXXX`

On failed iterations, summary outputs may be incomplete; failure debug bundle is required.
