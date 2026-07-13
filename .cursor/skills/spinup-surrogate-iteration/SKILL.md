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

## Commit Policy

- Do not commit every seed run or partial trial.
- Make one checkpoint commit per meaningful iteration milestone (after winner selection + tracking updates).
- Include the iteration ID in the commit message (for example `iter002`).
- Keep large raw outputs in `UQ_output` out of git unless explicitly requested.

## Iteration Checklist

Copy this checklist into `development/spinup_surrogate/iterations/iterXXX.md` and keep it updated.

- [ ] Define objective and hypothesis
- [ ] Define fixed controls (case, split mode, train fraction, seed range)
- [ ] Define variants to compare
- [ ] Prepare/update Slurm scripts in `development/spinup_surrogate/slurm/`
- [ ] Submit runs through Slurm
- [ ] Aggregate per-variant summary JSON
- [ ] Compare variants with consistent metrics
- [ ] Select winner and record decision
- [ ] Update `development/spinup_surrogate/registry.csv`
- [ ] Update `development/spinup_surrogate/handoff/CURRENT.md`
- [ ] Create one checkpoint commit with iteration ID in message

## Standard Comparison Metrics

For each target variable (`TOTSOMC`, `TOTSOMN`), report:

- median and IQR of `r2_val`
- median `r2_gap`
- median and IQR of `rmse_ratio`
- `overfit_warning_fraction`
- tails (`min r2_val`, `max rmse_ratio`)

## Required Outputs Per Iteration

- `development/spinup_surrogate/iterations/iterXXX.md`
- `development/spinup_surrogate/summaries/iterXXX/<variant>_summary.json`
- one new row in `development/spinup_surrogate/registry.csv`
- updated `development/spinup_surrogate/handoff/CURRENT.md`
- one checkpoint commit referencing `iterXXX`
