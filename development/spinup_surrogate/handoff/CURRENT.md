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
- Future spinup-surrogate output root:
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

The preferred nine-case baseline is the iter007-selected `s08_tanh_adam_a10_lr1e3` fixed MLP
with the iter006 `all_control` 45-feature schema (`TOTSOMC`/`TOTSOMN` median `r2_val=0.5892`).

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
- Correlation pruning will now be a global, feature-only preprocessing step before any
  train/test split; its priority and provenance must be tested before iter008 execution.
- Whether stronger LBFGS regularization can retain its high validation R2 without violating
  RMSE-ratio or overfit-warning gates remains untested.
- The Puma environment, nine pickles, and transferred data passed the dedicated compute-node
  migration preflight; iter007 training and training dry-run have not run.
- `OLMT_puma` currently uses the home-directory micromamba root; monitor the 50-GB home quota

## Next Iteration Plan (iter008, planning only)

No iter008 files, code changes, or Slurm jobs are authorized yet. This plan is the required
starting point for its scaffold and runtime-contract request.

### Durable correlation-filter ordering

For every current and future spinup-surrogate run that enables variance or correlation filtering:

1. Build the complete feature-only design matrix and apply filtering before any train/test split.
   Feature filtering must never inspect target values.
2. Freeze and record the retained schema before creating the seed-specific splits. The record must
   identify the scope as `global_pre_split`, so the same schema is used by every seed for that
   feature-policy arm.
3. For every high-correlation pair requiring a removal, preferentially drop a `WIND_*`, `PSRF_*`,
   or `FLDS_*` feature. If both or neither member has that drop priority, use canonical feature
   order as the deterministic tie-breaker. Record each dropped feature and its correlation pair.
4. Fit scalers and models only on the seed-specific training rows after the schema is frozen.

Historical iteration artifacts remain provenance and are not retroactively reinterpreted.

### Objective and locked design

Test whether stronger L2 regularization can make the high-validation-R2 LBFGS approach eligible
without the iter007 RMSE-ratio and overfit-warning failure, while measuring whether globally
pruned input schemas improve the selected compact Adam baseline.

- Fixed scientific controls: the same nine cases, `by_member` split, train fraction `0.8`, targets
  `TOTSOMC,TOTSOMN`, seeds `10001-10005`, stats-only outputs, and disabled variance filtering.
- Candidate feature pool: exactly the iter006 `all_control` 45 features. For filtered arms it is
  an eligible pool, not an all-must-survive explicit subset; correlation pruning may remove its
  members without causing explicit-subset validation failure.
- Model settings: `s08_tanh_adam_a10_lr1e3` plus `(32,)`, `tanh`, `lbfgs` candidates at alpha
  `50`, `100`, `250`, `500`, and `1000` (`learning_rate_init=1e-3` is provenance-only for
  LBFGS).
- Feature-policy arms for every model: `full45` (no correlation filter),
  `corr080_prioritydrop` (global absolute-correlation threshold `0.8`), and
  `corr060_prioritydrop` (global absolute-correlation threshold `0.6`).
- Matrix size: six models times three feature policies times five seeds: **18 variants and 90
  training leaves**. Derive each run slug as
  `spinup_surrogate_iter008_<model>_<feature-policy>`.

### Decision and execution requirements

- Retain the iter007 gates independently for both targets: required five readable stats files;
  median validation R2 no more than `0.01` below control; minimum R2 no more than `0.02` below;
  R2 IQR no more than `0.02` above; median per-seed RMSE ratio no more than `0.02` above; and zero
  overfit warnings. Report absolute validation RMSE alongside those gates.
- Rank full gate passers by mean cross-target median validation R2, then lower mean median RMSE
  ratio, then simpler architecture. If no new candidate passes, retain
  `s08_tanh_adam_a10_lr1e3` with `full45`.
- Before execution, implement and test global-pre-split filtering, the eligible-pool behavior,
  priority-aware pair pruning, and seed-invariant feature-schema evidence. Do not change closed
  iteration artifacts.
- The runtime-contract request must explicitly cover this 90-leaf matrix, Puma
  `development/hpc/puma.md`, the proposed 10-CPU/50-GB-implied/30-minute cap, one retry only for
  a scheduler/resource interruption, continuous monitoring through closeout, and closeout-commit
  authority. Application/code/configuration failures stop for fresh authorization.
- Each variant must use per-array-task `XDG_CACHE_HOME`, a variant-local self-describing submitted
  Slurm copy and `submission_config.env`, root-level stdout/stderr paths, and a manifest-derived
  aggregation input list validated against the 18 locked variant names.

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
3. Load the iter008 planning addendum in `iterations/iter007.md` and this plan section.
4. Review `development/spinup_surrogate/WORKFLOW.md` and
   `development/hpc/puma.md`.
5. Read `development/spinup_surrogate/iterations/iter007.md`; there is no live job set.
6. Do not scaffold, submit, or change code for iter008 until the new runtime contract explicitly
   authorizes the locked matrix and the required implementation work.

## Ready/Blocked Status for Next Iteration

Iter007 is complete. The training job set is terminal with all 40 stats files preserved,
including cache-isolated retry leaves `23346857_5` and `23346858_2`. Corrected aggregation job
`23346902` completed (`0:0`, `00:00:15`), producing all eight summary/stability pairs. Retain
`s08_tanh_adam_a10_lr1e3`; all other variants were rejected by the locked gates.

Iter008 has a defined, unexecuted 18-variant/90-leaf plan. It is blocked only on the required
implementation/test work and a new explicit runtime contract; it is not a retry or extension of
the iter007 authorization.

## Required User Decisions Before Execution (if any)

No active execution decision remains. Iter008 requires explicit authority for the documented
implementation/test work and the standard new runtime-contract authorization request under
`development/hpc/puma.md`; the request must name the 18 variants/90 leaves, proposed resource
cap, one scheduler/resource retry, continuous monitoring, and closeout-commit decision.

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
