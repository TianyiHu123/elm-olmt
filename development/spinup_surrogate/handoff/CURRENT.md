# Spinup Surrogate - Current Handoff (iter006 completed, all_control retained)

## Live State

- Active iteration: `iter007` (not yet scaffolded)
- Status: `planned`
- Phase: `planning`
- Active job IDs: none
- Site profile: `development/hpc/perlmutter.md`

## Current Objective

`iter006` completed feature-set settling under explicit subset validation. No reduced feature set passed the locked quality/tail gates, so `all_control` is retained. Iter007 should tune only MLP hyperparameters with the iter006 feature set frozen.

## Best Variant So Far

`all_control` remains the preferred nine-case baseline (`TOTSOMC`/`TOTSOMN` median `r2_val=0.5892`).

## Evidence (key metrics and failure signals)

`iter006` outcomes:

- Completed variants (5 seeds each): `all_control`, `all_params_all_surface_core_clim`, `core_tri_group`
- Rejected variant: `core_params_all_surface_all_clim` (2 failed tasks + 3 cancelled tasks) due to explicit subset validation
- `all_control`: median `r2_val=0.5892` (`TOTSOMC`, `TOTSOMN`), median `rmse_ratio=1.0000` (`TOTSOMC`) and `1.0008` (`TOTSOMN`)
- `all_params_all_surface_core_clim`: median `r2_val` dropped to approximately `0.551` for both targets
- `core_tri_group`: median `r2_val` dropped to approximately `0.519` for both targets
- Warning fraction remained `0` for successful variants, but reduced sets violated `r2_val` and/or tail/IQR gates

Explicit-rejection evidence (`core_params_all_surface_all_clim`):

- `ValueError: Explicit feature subset includes unavailable feature(s) after feature_set/clim/variance/correlation filtering`
- Missing requested features included `PRECTmms_clim_min`, `FSDS_clim_std`, `FSDS_clim_min`, `TBOT_clim_seasonal_amp`, `RH_clim_max`, `PSRF_clim_min`, `PSRF_clim_max`

Resource diagnostics (`iter006`):

- Completed-task elapsed approximately `108-153s`
- Completed-task MaxRSS approximately `37.18-47.97GB`
- `seff` CPU efficiency approximately `2.64-3.56%`
- `seff` memory efficiency approximately `76.25-99.94%`

## What Changed in Latest Iteration

- Added explicit feature-subset support in `train_surrogate_spinup.py` and `model_ELM/surrogate_NN_Spinup.py`
- Enforced hard rejection when requested explicit-subset features are unavailable after variance/correlation filtering
- Added full training-row Pearson-pair diagnostics before correlation pruning and persisted dropped-representative mapping
- Expanded `development/spinup_surrogate/analyze_feature_stability.py` with thresholded pair frequencies (`0.80`, `0.90`, `0.95`, `0.98`) and cross-target agreement summaries
- Ran iter006 four-variant matrix; completed three variants and rejected one invalid explicit subset
- Aggregated iter006 performance and stability summaries under `development/spinup_surrogate/summaries/iter006/`
- Kept `all_control` as baseline because no reduced candidate passed iter006 promotion gates

## Open Risks / Unknowns

- Memory headroom remains tight (completed tasks reached approximately `47.97GB` of `48GB`)
- CPU efficiency remains low despite short walltime, indicating resource under-utilization
- Correlated-feature attribution remains sensitive; explicit subset validity is now strict and may reject broad lists unless pre-screened
- Hyperparameter-space behavior with the frozen iter006 feature set is not yet characterized

## Next Iteration Plan (`iter007`, not started)

1. Freeze features to the exact 45-feature set actually used by iter006 `all_control` after filtering (explicit subset list from `iter006.md`).
2. For iter007 runs, enforce this explicit subset and disable variance/correlation filtering to keep inputs fixed.
3. Parameterize MLP hyperparameters via input arguments (instead of hardcoded values), while preserving backward compatibility when fixed args are not provided.
4. Evaluate an external fixed-hyperparameter matrix with 8 candidates (`4` single-layer + `4` two-layer), conservative widths (`8-32`), mostly `adam`, with one `lbfgs` stress-test.
5. Hyperparameter scope: vary `hidden_layer_sizes`, `alpha`, `learning_rate_init`; allow `activation` and `solver` changes for architecture-shift variants.
6. Use no anchor candidate inside the iter007 matrix; compare all candidates directly against iter006 `all_control` as the external baseline.
7. Keep scientific controls fixed: split mode `by_member`, train fraction `0.8`, targets `TOTSOMC,TOTSOMN`, seeds `10001-10005`.
8. Keep resource defaults unless changed by user: `--mem=48GB`, `--time=00:30:00`, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`.
9. Selection rule: apply standard iteration-loop gates first; among passers, rank by mean median `r2_val` across both targets, then lower `rmse_ratio`, then simpler architecture.
10. This handoff update is planning-only; no iter007 execution started.

## Plan Reference (optional)

- Primary execution summary: this file (`CURRENT.md`) under `Next Iteration Plan`.
- Iter007 full planning artifact (authoritative): `/global/homes/t/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`.
- Iter006 archival plan: `/global/homes/t/tianyihu/.cursor/plans/iter006-feature-settling-03e71a26.plan.md`.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter006.md`
   - `development/spinup_surrogate/iterations/iter005.md`
   - `development/spinup_surrogate/iterations/iter004.md`
3. Load iter007 full plan: `/global/homes/t/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`.
4. Review `development/spinup_surrogate/WORKFLOW.md` and
   `development/hpc/perlmutter.md`.
5. Treat iter006 as completed with `all_control` retained; execute iter007 only after runtime-contract confirmation (round budget, HPC/session confirmation, execution approval, resource policy).

## Ready/Blocked Status for Next Iteration

Ready for iter007 MLP-only tuning. No scientific decision gate is currently blocking start.

## Required User Decisions Before Execution (if any)

Standard runtime contract confirmations still apply before the next submission:

- round budget mode
- HPC/session confirmation
- execution approval
- resource policy mode

## Artifact Paths

- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter005 report: `development/spinup_surrogate/iterations/iter005.md`
- Iter005 summaries: `development/spinup_surrogate/summaries/iter005/`
- Iter006 report: `development/spinup_surrogate/iterations/iter006.md`
- Iter006 script root: `development/spinup_surrogate/slurm/iter006/`
- Iter006 summary root: `development/spinup_surrogate/summaries/iter006/`

## Files Modified in Repo (latest cycle)

- `train_surrogate_spinup.py`
- `model_ELM/surrogate_NN_Spinup.py`
- `development/spinup_surrogate/analyze_feature_stability.py`
- `development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm`
- `development/spinup_surrogate/iterations/iter006.md`
- `development/spinup_surrogate/summaries/iter006/`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter006.md` sections:

- `Execution Log`
- `Results`
- `Aggregation and Closeout`
