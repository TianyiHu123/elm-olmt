# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `none`
- Most recent iteration: `iter002`
- Status: `completed`
- Phase: `closed`
- Active job IDs: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-29T17:27:04-07:00`

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

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, and `iterations/iter002.md`.
2. Treat Iter002 artifacts as retained provenance; do not overwrite them without new scope and runtime authority.
3. Obtain a new approved package before any additional diagnostic, rerun, interpretation, or model execution.
