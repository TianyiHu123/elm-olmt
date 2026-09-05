# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `none`
- Most recent iteration: `iter003`
- Status: `completed`
- Phase: `closed`
- Active job scope: `none`
- Active monitoring: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-31T19:03:50-07:00`

## Completed Iter003

- Retry two `23729042` completed `0:0` in 02:29 after vectorizing complete-day aggregation; 21.6 GB/30 GB peak memory.
- Accepted package: 45 figures, 69 series rows, 960 member rows, passing receipt, and nine-site manifest at `.../elm_diagnose_iter003/results_retry2/`.
- The package is descriptive only. Monitoring-wrapper and agent-continuity evidence remains recorded for a separate workflow-improvement scope.

## Completed Iter002

- Goal: generate the recovered, integrated nine-site seed-resolved `SR` diagnostic package.
- Inputs: nine `ppe6` controls, all 60 updated `ctrlopt` pickles, and nine standard coupling SR NetCDF observations, locked by the passing preflight receipt.
- Execution: preflight `23723017` completed. Initial diagnostic `23723072` failed only because the installed Matplotlib rejects `Axes.boxplot(labels=...)`. The user authorized a minimal revision; focused independent review passed the `labels=` to `tick_labels=` correction. Retry `23723308` completed `0:0` in 2:51 using 22.94/30 GB.
- Deliverables: every site has raw-hourly, complete-day daily, monthly climatology, UTC diurnal, and hourly-distribution plots (45 PNGs total). `metrics.csv` has 69 descriptive hourly rows: 60 optimized seeds and nine control means.
- Scope result: accepted for descriptive diagnostics only. No cross-site ranking, score threshold, parameter selection, or scientific conclusion was made.

## Artifact References

- Iteration record: `development/ELM_diagnose/iterations/iter002.md`
- Registry: `development/ELM_diagnose/registry.csv`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Immutable input receipt: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/preflight/preflight_result.json`
- Figures/metrics/manifest: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/results/`
- Canonical retry material: `development/ELM_diagnose/tools/iter002_sr_diagnostics.py` and `development/ELM_diagnose/slurm/iter002/`

## Current Objective

Iter003 is closed by user authorization; await a separately approved next scope.

## Current Risks or Blockers

- Historical monitoring-context limitations are recorded in `iterations/iter003.md`. Future
  monitoring strategy selection and behavior are governed by `WORKFLOW.md` Section D and the active
  runtime contract.

## Agent-Continuity Failure to Carry Forward

- The agent repeatedly ended turns while Iter003 still had an approved next action (review retrieval, materialization, submission, or cadence observation), requiring the user to issue `continue`. Record this as a control-flow failure to diagnose in a future workflow-improvement scope; it is not an HPC failure and does not change current runtime authority.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, and `iterations/iter003.md`.
2. Treat Iter003 outputs and failed/cancelled attempts as retained provenance.
3. Obtain fresh approval before a new iteration or workflow-improvement work.
