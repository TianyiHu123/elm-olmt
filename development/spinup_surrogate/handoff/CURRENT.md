# Spinup Surrogate - Current Handoff (iter005 completed, multi_all preferred)

## Current Objective

`iter005` completed the nine-case feature-attribution study. Iter006 will settle the feature set before any MLP hyperparameter tuning, using targeted reductions, training-row Pearson correlation analysis, and five-seed validation.

## Best Variant So Far

From the last successful iteration (`iter001` single-case), `tuned_nn` (tied with `no_clim` and `reduced_clim`) remains the best available baseline.

No winner was selected in `iter002`, `iter003`, or `iter004`; iter005 successfully selected `multi_all` under the within-round comparison.

## Evidence (key metrics and failure signals)

`iter002` initial matrix outcomes (30 seeds planned per variant):

- `multi_all` (`55918399`): `5 COMPLETED`, `25 TIMEOUT`
- `multi_params_surface` (`55919047`): `4 COMPLETED`, `26 TIMEOUT`
- `multi_params_clim` (`55919049`): `4 COMPLETED`, `26 TIMEOUT`
- `multi_params_only` (`55919050`): `4 COMPLETED`, `26 TIMEOUT`

One approved retry pilot at `--time=00:15:00`:

- job `55950336` (`multi_all`, `--array=1-5`)
- result: `1 COMPLETED`, `1 TIMEOUT`, remaining pending retry tasks cancelled by fail-fast
- representative rows:
  - `55950336_2|TIMEOUT|0:0|00:15:15`
  - `55950336_2.batch|CANCELLED|0:15|00:15:20`

`iter003` pilot outcomes at `--time=00:20:00`:

- Initial `n_jobs=4` pilot (`55952433`): seed 10001 completed at `00:18:13`, seed 10002 timed out at `00:20:21`; remaining tasks were fail-fast cancelled.
- Retry `n_jobs=8` pilot (`55954503`): 4/5 tasks timed out (`00:20:09-00:20:22`); only seed 10004 completed at `00:18:19`.
- `seff`: memory reached `41.97/42.00 GB` on the largest tasks; CPU efficiency was only `0.26-0.42%`.

`iter004` source-debug outcomes:

- Initial diagnostic (`55957524`) completed in `00:19:19`, but reached `41.97/42.00 GB`.
- Phase timing showed per-case preparation dominated (`53-186s` per case); design matrix, GridSearchCV, and permutation phases were negligible.
- Combined xarray forcing-load retry (`55958511`) completed in `00:26:18`, still reached `41.97/42.00 GB`, and did not improve preparation time.

`iter005` feature-attribution outcomes:

- All 20 tasks completed: five seeds for each of `multi_all`, `multi_params_surface`, `multi_params_clim`, and `multi_params_only`.
- `multi_all` ranked first for both targets: median `r2_val=0.5892` for `TOTSOMC` and `TOTSOMN`, median `rmse_ratio` approximately `1.000`.
- `multi_params_clim` ranked second with median `r2_val` approximately `0.561`; surface-only and parameter-only variants were lower.
- Median `r2_gap` was near zero or negative and warning fraction was `0` for all variants.
- Stable `multi_all` candidates across both targets included `parm_6`, `parm_13`, `parm_9`, `parm_12`, `parm_10`, `PCT_SAND`, `FSDS_clim_mean`, `PRECTmms_clim_mean`, and `RH_clim_seasonal_amp`.

## What Changed in Latest Iteration

- Closed `iter002` as `failed` with full debug bundle and provenance.
- Recorded failed status in `development/spinup_surrogate/registry.csv`.
- Completed a grilling session and locked `iter003` planning direction:
  - success gate: runtime + quality
  - optimization priority: parallelism tuning first
  - quality tolerance: tight (`r2_val` drop `<=0.01`, `rmse_ratio` increase `<=0.02`)
  - runtime target: no timeout with walltime target `<=00:20:00` in pilot
- Closed `iter003` as failed after both the initial pilot and one retry failed the runtime gate.
- Corrected the NERSC Shared-QOS resource interpretation: `42GB` memory forces approximately `23` hyperthread CPUs, rounded to `AllocCPUS=24` / `12` physical cores, regardless of `cpus-per-task=4` versus `8`.
- Preserved partial retry stats for seeds 10003 and 10004 in scratch; skipped aggregation and winner selection.
- Closed `iter004` as failed after the diagnostic memory-headroom gate and one source-fix retry failed.
- Added source timing and `pre_dispatch` instrumentation; the combined xarray forcing-load optimization was tested but not promoted.
- Locked iter005 objective to nine-case model-performance and feature attribution using four variants and five seeds per variant.
- Explicitly deferred cache work; iter001 remains historical metric context, not valid nine-case feature-variation evidence.
- Completed iter005 with no timeout or blocked variant and aggregated standard metrics plus feature-stability summaries.
- Promoted `multi_all` as the within-round preferred configuration; iter001 remains historical context only.

## Open Risks / Unknowns

- Iter005 completed under `48GB/30min`, but memory remained high: up to approximately `47.97GB`.
- Reported `seff` CPU efficiency remained low (`0.26-0.65%`); runtime is acceptable operationally but resource efficiency remains poor.
- Feature importance under correlated inputs remains attribution-sensitive; stable candidates should be validated with targeted follow-up ablations or grouped features.
- Iter001 performance values are not a valid nine-case feature-variation gate, though they remain useful historical context.
- Correlation analysis will begin at `|r|=0.80`; these are diagnostic pair thresholds, while the operational filter remains `0.98`.

## Next Iteration Plan (`iter006`, not started)

1. Freeze the current MLP quick-grid; defer MLP hyperparameter tuning to iter007.
2. Run four five-seed configurations, with every candidate retaining parameter, surface, and climatology groups:
   - `all_control`: all 14 parameters, all three surface features, and all eligible climatology features.
   - `core_params_all_surface_all_clim`: stable parameter core (`parm_6`, `parm_9`, `parm_10`, `parm_12`, `parm_13`) plus all surface/climatology features.
   - `all_params_all_surface_core_clim`: all parameters and surface features plus `FSDS_clim_mean`, `PRECTmms_clim_mean`, and `RH_clim_seasonal_amp`.
   - `core_tri_group`: stable parameter core plus all three surface features and the core climatology set.
3. Do not run a parameter-only configuration; iter005 already showed it was inferior to `multi_all`.
4. Add explicit feature-subset validation. If a requested feature is removed by variance/correlation filtering, reject that configuration rather than silently changing it.
5. Persist complete upper-triangle training-row Pearson pair lists and report pair frequencies at `|r| >= 0.80`, `0.90`, `0.95`, and `0.98`; do not form automatic transitive clusters.
6. Accept a reduced set only if median `r2_val` loss is `<=0.01`, median `rmse_ratio` increase is `<=0.02`, warning fraction does not increase, tail bounds pass, IQR expands by no more than 25% when gated, and feature stability meets the `4/5` retention and `3/5` top-10 rules.
7. Keep `--mem=48GB`, `--time=00:30:00`, `N_JOBS=4`, and `PRE_DISPATCH=n_jobs` as proposed resources.

## Plan Reference (optional)

- Primary execution plan: this file (`CURRENT.md`) under `Next Iteration Plan`.
- Optional long-form plan file: `/global/homes/t/tianyihu/.cursor/plans/iter006-feature-settling-03e71a26.plan.md`.
- Autonomy fallback: if no optional plan file is present, continue the loop by drafting the next-round plan directly in `CURRENT.md` and in `development/spinup_surrogate/iterations/iterXXX.md`.
- Sync rule: when an optional plan file exists, treat `CURRENT.md` as the authoritative run summary and keep only critical deltas there.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. If `Plan Reference` provides an optional long-form plan path, load it; if not, proceed using `CURRENT.md` only.
3. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter005.md`
   - `development/spinup_surrogate/iterations/iter004.md`
   - `development/spinup_surrogate/iterations/iter003.md`
4. Review `development/spinup_surrogate/iteration_loop.md`.
5. Treat `iter005` as completed and use its `multi_all` evidence as the next baseline.
6. Scaffold the iter006 explicit-subset and correlation-analysis plan only after the standard runtime contract confirmation.

## Ready/Blocked Status for Next Iteration

`iter005` completed successfully for its five-seed attribution objective. `multi_all` is the preferred baseline; iter006 feature-set validation is ready, but no execution is authorized until the new round contract is confirmed.

## Required User Decisions Before Execution (if any)

The iter006 scientific strategy is locked. Round budget, HPC confirmation, execution approval, and resource policy confirmations still apply before submission.

Standard session run-contract confirmations still apply before any new submissions.

## Artifact Paths

- Prior failed iteration report: `development/spinup_surrogate/iterations/iter002.md`
- Latest failed iteration report: `development/spinup_surrogate/iterations/iter003.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter002 script root: `development/spinup_surrogate/slurm/iter002/`
- Iter002 scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`
- Iter003 report path: `development/spinup_surrogate/iterations/iter003.md`
- Iter003 script root: `development/spinup_surrogate/slurm/iter003/`
- Iter003 retry scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_retry_multi_all`
- Iter004 report: `development/spinup_surrogate/iterations/iter004.md`
- Iter004 script root: `development/spinup_surrogate/slurm/iter004/`
- Iter004 diagnostic scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_diag_multi_all`
- Iter004 source-fix scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_sourcefix_multi_all`
- Iter005 report target: `development/spinup_surrogate/iterations/iter005.md`
- Iter005 script root: `development/spinup_surrogate/slurm/iter005/`
- Iter005 summary root: `development/spinup_surrogate/summaries/iter005/`
- Iter006 report target: `development/spinup_surrogate/iterations/iter006.md`
- Iter006 script root: `development/spinup_surrogate/slurm/iter006/`
- Iter006 summary root: `development/spinup_surrogate/summaries/iter006/`

## Files Modified in Repo (latest cycle)

- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter003.md`
- `development/spinup_surrogate/iterations/iter004.md`
- `development/spinup_surrogate/iterations/iter005.md`
- `development/spinup_surrogate/ITERATION_SUMMARY.md`
- `development/spinup_surrogate/analyze_feature_stability.py`
- `development/spinup_surrogate/summaries/iter005/`
- `model_ELM/surrogate_NN_Spinup.py`
- `train_surrogate_spinup.py`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter005.md` sections:

- `Results`
- `Feature-Importance Evidence`
- `Model-Performance Interpretation`
