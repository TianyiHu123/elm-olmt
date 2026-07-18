# Spinup Surrogate - Current Handoff (Puma migration validated; iter007 ready to scaffold)

## Live State

- Active iteration: `iter007` (not yet scaffolded)
- Status: `planned`
- Phase: `ready for scaffolding`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Execution authority: not granted; confirm a new runtime contract before any iter007 execution

## Current Objective

The temporary Perlmutter-to-Puma migration is complete and validated without scaffolding iter007.
`iter006` remains closed with `all_control` retained. Iter007 is ready for scaffolding as the first
post-migration iteration and should tune only MLP hyperparameters with the iter006 feature set
frozen. Execution authority for iter007 remains not granted.

## Puma Migration State

- Authoritative iter007 plan (by path only):
  `/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`.
- Fixed repository root: `/xdisk/chopinsong/tianyihu/elm-olmt`. Future Slurm scripts must use this
  literal root and fail early if `train_surrogate_spinup.py`, `WORKFLOW.md`, the Puma profile, the
  Puma environment YAML, or iteration-specific tracked artifacts are absent. `$0`, copied-script
  locations, `SLURM_SUBMIT_DIR`, current-directory discovery, and environment overrides are
  prohibited for repository-root selection.
- Pickle utility: `development/spinup_surrogate/migrate_case_pickles.py`, with mutually exclusive
  inspect, apply, and recovery modes. All nine pickles form one transaction and originals are
  retained as `<case>.pkl.perlmutter.bak` until the user manages them.
- Puma run mapping:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe`.
- Puma meteorology mapping:
  `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/<SITE>/1x1pt_<SITE>/CLM1PT_data`.
- Future iter007 output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output`.
- Puma runtime and lifecycle: use `micromamba run -n OLMT_puma` and treat
  `development/spinup_surrogate/WORKFLOW.md` as canonical.
- Only `case.runroot` and `case.metdir` are rewritten. `finidat`, `dependcase`, and unrelated
  historical path metadata are unchanged; restart lookup continues through `dependcase` and the
  `finidat` basename.
- Login-node read-only inventory observed the nine meteorology directories and complete filename
  sequences: 84 monthly files (2018-01 through 2024-12) for ABBY/JERC/OSBS/SOAP/RMNP/TALL and 72
  (2019-01 through 2024-12) for TEAK/WREF/YELL. This is not compute-node validation.
- Compute-node validation and activation passed under the bounded Puma contract. Inspection job
  `23333089` completed successfully; apply job `23333093` completed successfully; final live-set
  verification job `23333117` completed successfully. All nine original pickles are now Puma
  mapped, and all nine `.perlmutter.bak` files remain preserved. No staged or temporary files
  remain.

Migration runtime contract completed:

1. The intended interactive allocation path was unavailable because the Puma interactive and
   `salloc` wrappers terminated before allocation. Under subsequent explicit user authority, the
   bounded migration work ran as 1-CPU standard-partition batch jobs under account `chopinsong`,
   where Puma derives the 5-GB allocation from the requested CPU.
2. Load micromamba and run the utility through `micromamba run -n OLMT_puma`.
3. Permit one retry at 2 CPUs and 10 GB only after confirmed OOM.
4. Stop and request fresh authority for serialization, application, data, or validation failures.
5. No training, training dry-run, iter007 artifacts, or unrelated jobs were run or created.

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
- The Puma environment, nine pickles, and transferred data passed the dedicated compute-node
  migration preflight; iter007 training and training dry-run have not run.
- `OLMT_puma` currently uses the home-directory micromamba root; monitor the 50-GB home quota

## Next Iteration Plan (`iter007`, not started)

1. Freeze features to the exact 45-feature set actually used by iter006 `all_control` after filtering (explicit subset list from `iter006.md`).
2. For iter007 runs, enforce this explicit subset and disable variance/correlation filtering to keep inputs fixed.
3. Parameterize MLP hyperparameters via input arguments (instead of hardcoded values), while preserving backward compatibility when fixed args are not provided.
4. Evaluate an external fixed-hyperparameter matrix with 8 candidates (`4` single-layer + `4` two-layer), conservative widths (`8-32`), mostly `adam`, with one `lbfgs` stress-test.
5. Hyperparameter scope: vary `hidden_layer_sizes`, `alpha`, `learning_rate_init`; allow `activation` and `solver` changes for architecture-shift variants.
6. Use no anchor candidate inside the iter007 matrix; compare all candidates directly against iter006 `all_control` as the external baseline.
7. Keep scientific controls fixed: split mode `by_member`, train fraction `0.8`, targets `TOTSOMC,TOTSOMN`, seeds `10001-10005`.
8. Start from the Puma standard-node baseline unless changed by user: account `chopinsong`,
   partition `standard`, `--cpus-per-task=10` (which implies 50 GB total memory at Puma's 5 GB/CPU
   ratio), omit `--mem` and `--mem-per-cpu`, use `--time=00:30:00`, `N_JOBS=4`,
   `PRE_DISPATCH=n_jobs`, and single-threaded BLAS/OpenMP settings.
9. Selection rule: apply the standard `WORKFLOW.md` gates first; among passers, rank by mean median `r2_val` across both targets, then lower `rmse_ratio`, then simpler architecture.
10. Iter007 is the first iteration after the temporary Perlmutter-to-Puma migration. Migration
    checks passed; iter007 is ready for scaffolding, but no iter007 execution has started.

## Plan Reference

- Iter007 full planning artifact (authoritative by path only): `/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`.
- Live migration and execution state: this file (`CURRENT.md`).
- Iter006 archival plan: `/home/u32/tianyihu/.cursor/plans/iter006-feature-settling-03e71a26.plan.md`.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter006.md`
   - `development/spinup_surrogate/iterations/iter005.md`
   - `development/spinup_surrogate/iterations/iter004.md`
3. Load iter007 full plan: `/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`.
4. Review `development/spinup_surrogate/WORKFLOW.md` and
   `development/hpc/puma.md`.
5. Keep iter007 unscaffolded until the user requests the planned scaffolding step. Do not use
   training or training dry-run as migration preflight.
6. Confirm a separate iter007 runtime contract before any training execution; execution authority
   remains not granted.

## Ready/Blocked Status for Next Iteration

Ready for iter007 scaffolding. The nine-case Puma compute-node preflight, transactional rewrite,
and post-activation verification passed. Retain `Execution authority: not granted` until the
separate iter007 runtime contract is confirmed.

## Required User Decisions Before Execution (if any)

The remaining authority is the standard iter007 runtime contract: round budget mode, HPC/session
confirmation, execution approval, and resource policy mode.

## Artifact Paths

- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Pickle migration utility: `development/spinup_surrogate/migrate_case_pickles.py`
- Puma site profile: `development/hpc/puma.md`
- Iter005 report: `development/spinup_surrogate/iterations/iter005.md`
- Iter005 summaries: `development/spinup_surrogate/summaries/iter005/`
- Iter006 report: `development/spinup_surrogate/iterations/iter006.md`
- Iter006 script root: `development/spinup_surrogate/slurm/iter006/`
- Iter006 summary root: `development/spinup_surrogate/summaries/iter006/`

## Files Modified in Repo (migration cycle)

- `development/spinup_surrogate/migrate_case_pickles.py`
- `development/hpc/puma.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `development/spinup_surrogate/iterations/iter006.md` (provenance restoration only)

The authoritative external plan was updated in place at
`/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`; it has no tracked mirror or
recorded hash.

## Files Modified in Repo (latest completed iteration)

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
