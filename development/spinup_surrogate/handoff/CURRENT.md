# Spinup Surrogate - Current Handoff (iter010 closed)

## Live State

- Active iteration: none
- Status: `iter010 completed`
- Phase: `closed; new runtime contract required for any Iter011 work`
- Active job IDs: none. Corrected Iter010 production arrays completed 1,500/1,500 leaves `0:0`; aggregation `23399438` completed `0:0`.
- Site profile: `development/hpc/puma.md`
- Execution authority: on 2026-07-24 America/Phoenix the user replied `approved` to the complete
  Iter010 request: confirmed UA Puma login host `junonia.hpc.arizona.edu` with
  `development/hpc/puma.md`; one finite 15-variant / 1,500-leaf matrix; artifact preparation,
  static validation, independent read-only review, bounded no-training preflight, submission, and
  continuous monitoring through aggregation/selection/closeout. Resources are `standard` /
  `chopinsong`, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, and
  per-task cache isolation. One minimal validation-only correction/rerun is separate from one
  retry per leaf only for scheduler/resource interruption within the caps. Other
  application/code/configuration failures stop for fresh authorization. At most one closeout
  commit is authorized.

## Current Objective

Iter010 completed its 15-variant, 100-seed (1,500-leaf) alpha-40--50 and feature-policy matrix.
The exact aggregate validator accepted all 1,500 results and produced 15 summary, 15 stability,
and 15 importance artifacts. All variants are scientifically rejected by the locked zero-warning
gate (warnings `0.22-0.25` for both targets); no model is promoted. Retain the Iter009 baseline
`s32_tanh_lbfgs_a50_lr1e3_full45`. The detailed terminal accounting and failure-prevention rules
are in `iterations/iter010.md`.

The temporary Perlmutter-to-Puma migration is complete and validated. `iter006` remains closed
with `all_control` retained. Iter007 is now scaffolded as the first post-migration iteration: it
tests eight fixed MLP configurations with the iter006 45-feature set frozen. All eight original
arrays are terminal: 38 leaves completed, while two leaves failed before training due to a
concurrent ArviZ home-cache race. The two cache-isolated retry leaves completed, restoring all 40
stats files. Corrected aggregation produced all eight summary/stability pairs; only
`s08_tanh_adam_a10_lr1e3` passed the locked gates, exactly matching the iter006 all_control
baseline. Iter008 selected `s32_tanh_lbfgs_a50_lr1e3_full45`: median validation R2
`0.7935/0.7937`, absolute validation RMSE `4661.8/469.7`, median RMSE ratio `0.9499/0.9561`, and
zero warnings. Validation job `23362319` failed before checking invariants because
the absolute-path validator could not import `model_ELM`; this is an application/configuration
failure. On 2026-07-22 the user authorized adding the fixed repository root to `sys.path` and
rerunning the same one-CPU/5-GB/5-minute validation only. Corrected job `23362351` completed
successfully (`0:0`, `00:00:35`, MaxRSS `406084K`) and confirmed the global-filter invariants.
All 90 training leaves completed `0:0`; manifest aggregation job `23362489` completed `0:0`.
Iter009 completed all 75 leaves and aggregation job `23371111` without retry. Alpha 25/35 improved
R2 and absolute RMSE but warned on one of five seeds for both targets under every policy. Alpha 50
produced the only three passers; full45 ranked first (`0.7935/0.7937` median validation R2,
`4661.8/469.7` absolute validation RMSE, `0.9499/0.9561` median RMSE ratio, zero warnings) and is
retained. Corr080 retained 25 features and the direct ablation retained 32, but neither improved
the eligible full45 control. Any next iteration requires a new runtime contract.

## Durable Prevention Rule

For any Python utility launched by absolute path on Puma, prepend the fixed repository root
`/xdisk/chopinsong/tianyihu/elm-olmt` to `sys.path` before importing repository modules. Require a
bounded compute-node import/no-training preflight before a production matrix. Treat an import-path
failure as application/configuration: preserve diagnostics and apply only the validation-only
retry boundary defined below.

The canonical workflow now grants one separate validation-only retry when a bounded preflight
fails before training: the primary agent may apply one minimal import/launch/configuration fix and
rerun the same preflight once. It does not consume the matrix variant retry budget; a second
preflight failure, a changed failure class, or any scientific-control change stops for fresh
authorization.

## Historical Iter009 Plan

- Retained baseline: `s32_tanh_lbfgs_a50_lr1e3_full45` with full45.
- Hypothesis and matrix: refine the alpha-50 LBFGS result while testing whether either
  global 0.80 correlation pruning or direct removal of the longwave-radiation, wind, and pressure
  climatology inputs improves generalization. Cross alpha `25`, `35`, `50` control, `65`, and `75`
  with three feature-policy arms: `full45` with no correlation filter; `corr080_prioritydrop` with
  the full45 eligible pool and global pre-split correlation threshold `0.80`; and
  `drop_flds_wind_psrf` with no correlation filter and Slurm argument
  `--forcing-vars PRECTmms,FSDS,TBOT,RH`, yielding the strict 32-feature subset after directly
  excluding all 13 `FLDS_*`, `WIND_*`, and `PSRF_*` climatology features. Use `(32,), tanh, lbfgs`
  and five seeds per variant: 15 variants and 75 leaves. Keep the nine cases, `by_member`/`0.8`
  split, two targets, and disabled variance filtering; correlation filtering is enabled only for
  `corr080_prioritydrop`.
- Gates: apply the iter008 selected-baseline gates independently per target: median/min
  R2 within `0.01`/`0.02`, IQR within `0.02`, RMSE ratio within `0.02`, and zero warnings; rank
  passers by mean median R2, lower RMSE ratio, then lower alpha.
- Operational shape: Puma `standard` / `chopinsong`, 10 CPUs (50 GB implied), 30 minutes,
  `N_JOBS=4`, per-task cache isolation, iteration-local Slurm manifest, independent read-only
  reviewer subagent, and no-training compute preflight. The validation-only retry is separate from
  the one scheduler/resource retry per leaf.
- Authorization: the finite iter009 lifecycle completed under the runtime contract recorded in
  Live State and `iterations/iter009.md`; this historical plan is not future authority.

## Proposed Iter010 Plan (Planning Only; Revised)

- Retained baseline: `s32_tanh_lbfgs_a50_lr1e3_full45`.
- Hypothesis and tentative matrix: bracket the alpha-35/50 warning transition across all three
  iter009 full-gate passers: `full45`, `corr080_prioritydrop`, and
  `drop_flds_wind_psrf`. Cross each policy with alpha `40`, `42.5`, `45`, `47.5`, and `50`
  control, using seeds `10001-10100`: 15 variants and 1,500 leaves. Keep the nine cases,
  `(32,), tanh, lbfgs`, `by_member`/`0.8`, two targets, stats-only output, and disabled variance
  filtering. Correlation filtering remains enabled only for `corr080_prioritydrop`; direct feature
  removal remains locked for `drop_flds_wind_psrf`. Record the warning seed and reason.
- Proposed gates: apply the iter009 selected-baseline gates independently per target: median/min
  R2 within `0.01/0.02`, IQR within `0.02`, median per-seed RMSE ratio within `0.02`, and zero
  warnings. Report absolute validation RMSE and rank passers by mean median R2, lower mean median
  RMSE ratio, then lower alpha.
- Feature-importance analysis: retain the existing validation permutation-importance method with
  `8` repeats. For every variant, target, and retained feature, aggregate the 100 seed results and
  report the feature's median rank across seeds, rank spread, median RMSE increase, and R2-drop
  diagnostics. Provide separate `TOTSOMC` and `TOTSOMN` rankings plus a combined cross-target
  view. Order each aggregate ranking by median rank, then median RMSE increase.
- Proposed operations: Puma `standard` / `chopinsong`, 10 CPUs (50 GB implied), 30 minutes,
  `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread BLAS/OpenMP, task-local cache, immutable
  variant artifacts, read-only reviewer, and bounded no-training preflight. `N_JOBS=4` is retained
  for the legacy GridSearchCV compatibility path; the fixed-parameter LBFGS path and current
  permutation-importance loop are sequential. The validation-only retry remains separate from one
  scheduler/resource retry per leaf; other application/code/configuration failures stop.
- Authorization boundary: evidence-derived planning only. A new iter010 runtime contract is
  required before scaffolding, code/configuration changes, submission, or execution.

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
- Iter009 MaxRSS reached `52427868K` against the 50-GB implied allocation, so headroom remains
  tight even though all 75 leaves completed.
- The zero-warning transition for full45 LBFGS lies somewhere between alpha 35 and 50; intermediate
  alphas remain untested.
- `OLMT_puma` currently uses the home-directory micromamba root; monitor the 50-GB home quota

## Historical Iter008 Plan

This is the pre-execution plan retained as provenance. Iter008 is closed; do not treat this
historical text as an execution authorization.

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
   - `development/spinup_surrogate/iterations/iter009.md`
   - `development/spinup_surrogate/iterations/iter008.md`
   - `development/spinup_surrogate/iterations/iter007.md`
3. Treat historical iter008/iter009 plan sections as provenance only.
4. Review `development/spinup_surrogate/WORKFLOW.md` and
   `development/hpc/puma.md`.
5. Confirm there is no live job set.
6. Validate the proposed iter010 plan and request its fresh runtime contract before scaffolding.

## Ready/Blocked Status for Next Iteration

Iter009 is complete: preflight `23370951`, all 75 training leaves, and aggregation `23371111`
completed successfully without retry. All 15 summary/stability pairs are preserved. Retain the
alpha-50 full45 LBFGS model; alpha 25/35 failed the warning gate and the two alternative feature
policies did not improve the eligible control. Iter010 is planning-only and requires a fresh
runtime contract.

## Required User Decisions Before Execution (if any)

No active execution decision remains. A future iteration must name its own locked matrix,
Puma resource cap, retry boundary, monitoring authority, and closeout-commit decision.

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
- Iter008 report: `development/spinup_surrogate/iterations/iter008.md`
- Iter008 summary root: `development/spinup_surrogate/summaries/iter008/`
- Iter009 report: `development/spinup_surrogate/iterations/iter009.md`
- Iter009 script root: `development/spinup_surrogate/slurm/iter009/`
- Iter009 summary root: `development/spinup_surrogate/summaries/iter009/`

## Files Modified in Repo (migration cycle)

- `development/spinup_surrogate/migrate_case_pickles.py`
- `development/hpc/puma.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `development/spinup_surrogate/iterations/iter006.md` (provenance restoration only)

The authoritative external plan was updated in place at
`/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`; it has no tracked mirror or
recorded hash.

## Files Modified in Repo (latest completed iteration)

- `development/spinup_surrogate/slurm/iter009/`
- `development/spinup_surrogate/iterations/iter009.md`
- `development/spinup_surrogate/iterations/iter009_source_manifest.txt`
- `development/spinup_surrogate/summaries/iter009/`
- `development/spinup_surrogate/ITERATION_SUMMARY.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter009.md` sections:

- `Execution and Diagnostics`
- `Results and Decision`
- `Proposed Iter010 Plan (Planning Only)`
