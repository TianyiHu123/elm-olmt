# Spinup Surrogate - Current Handoff (iter007 completed)

## Live State

- Active iteration: `iter007`
- Status: `completed`
- Phase: `selection and closeout complete`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Execution authority: on 2026-07-20, the user approved a fresh finite retry contract for only
  `s24_relu_adam_a50_lr5e4` seed `10005` and `d16_16_relu_adam_a50_lr5e4` seed `10002`, using the
  per-array-task `XDG_CACHE_HOME` isolation in the canonical script. The user also authorized
  continuous monitoring, successful-path aggregation/selection/closeout, one further retry per
  leaf only for scheduler/resource interruption, and amendment of the existing iter007 closeout
  commit. Both leaf retries completed. The user subsequently authorized correction of aggregation
  job `23346866`'s one `d16_08` path suffix and a same-resource aggregation rerun. Corrected job
  `23346902` completed; selection and closeout authority are now exhausted.

## Current Objective

The temporary Perlmutter-to-Puma migration is complete and validated. `iter006` remains closed
with `all_control` retained. Iter007 is now scaffolded as the first post-migration iteration: it
tests eight fixed MLP configurations with the iter006 45-feature set frozen. All eight original
arrays are terminal: 38 leaves completed, while two leaves failed before training due to a
concurrent ArviZ home-cache race. The two cache-isolated retry leaves completed, restoring all 40
stats files. Corrected aggregation produced all eight summary/stability pairs; only
`s08_tanh_adam_a10_lr1e3` passed the locked gates, exactly matching the iter006 all_control
baseline. Do not broaden the matrix or alter the selected result.

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

## What Changed in Iter007 Scaffold

- Added fixed MLP CLI controls and a direct fixed-parameter fitting path while retaining legacy
  GridSearchCV behavior when the controls are absent.
- Created the iter007 report, canonical Puma script, and expected summary path.
- Added the required five-part runtime-contract authorization request to `WORKFLOW.md` for every
  future iteration start.
- Recorded the user's iter007 approval, the confirmed Puma login host, resource cap, retry limit,
  and closeout-commit authority in `iterations/iter007.md`.

## Open Risks / Unknowns

- Memory headroom remains tight (completed tasks reached approximately `47.97GB` of `48GB`)
- CPU efficiency remains low despite short walltime, indicating resource under-utilization
- Correlated-feature attribution remains sensitive; explicit subset validity is now strict and may reject broad lists unless pre-screened
- Hyperparameter-space behavior with the frozen iter006 feature set is not yet characterized
- The Puma environment, nine pickles, and transferred data passed the dedicated compute-node
  migration preflight; iter007 training and training dry-run have not run.
- `OLMT_puma` currently uses the home-directory micromamba root; monitor the 50-GB home quota

## Iter007 Plan (scaffolded, not submitted)

1. Freeze the exact iter006 `all_control` 45-feature subset and disable variance/correlation
   filtering, so all candidates see identical inputs.
2. Evaluate four single-layer and four two-layer fixed MLPs with widths 8-32, mostly `adam`, and
   one `lbfgs` stress candidate.
3. Keep `by_member`, train fraction 0.8, targets `TOTSOMC,TOTSOMN`, and seeds 10001-10005 fixed.
4. Use Puma `standard`, account `chopinsong`, 10 CPUs/50 GB implied memory, 30 minutes,
   `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, and single-threaded BLAS/OpenMP settings.
5. Gate each target against iter006 `all_control`; rank passers by mean median `r2_val`, then
   lower mean median `rmse_ratio`, then simpler architecture. Full parameters and gates are in
   `iterations/iter007.md`.

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
5. Read `development/spinup_surrogate/iterations/iter007.md` and inspect the live job set.
6. Follow the iter007 runtime contract; do not submit an additional matrix or change code without
   fresh user authority.

## Ready/Blocked Status for Next Iteration

Iter007 is complete. The training job set is terminal with all 40 stats files preserved,
including cache-isolated retry leaves `23346857_5` and `23346858_2`. Corrected aggregation job
`23346902` completed (`0:0`, `00:00:15`), producing all eight summary/stability pairs. Retain
`s08_tanh_adam_a10_lr1e3`; all other variants were rejected by the locked gates.

## Required User Decisions Before Execution (if any)

No active execution decision remains. A subsequent iteration requires the standard new
runtime-contract authorization request under `development/hpc/puma.md`.

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
- Iter007 report: `development/spinup_surrogate/iterations/iter007.md`
- Iter007 script: `development/spinup_surrogate/slurm/iter007/case.train_surrogate_spinup_iter007_mlp_tuning.slurm`
- Iter007 summary root: `development/spinup_surrogate/summaries/iter007/`

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
