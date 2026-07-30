# iter006 - Feature-Set Settling with Explicit Subset Validation

## Status

- Iteration ID: `iter006`
- Iteration status: `completed`
- Round budget mode: `1 round` (iter006 only)
- Phase: `Round G closeout complete`
- HPC confirmed: yes
- Execution approval: approved for Slurm submission and monitoring within this round
- Resource policy mode: explicit
  - `#SBATCH --mem=48GB`
  - `#SBATCH --time=00:30:00`
  - `N_JOBS=4`
  - `PRE_DISPATCH=n_jobs`

## Bootstrap and Decision Context

Loaded:

- `development/spinup_surrogate/iteration_loop.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `/global/homes/t/tianyihu/.cursor/plans/iter006-feature-settling-03e71a26.plan.md`
- `development/spinup_surrogate/iterations/iter005.md`
- `development/spinup_surrogate/iterations/iter004.md`
- `development/spinup_surrogate/iterations/iter003.md`

`iter005` is treated as completed. `multi_all` is the baseline control for the iter006 feature-settling round.

## Objective

Settle a reduced, interpretable nine-case feature set before any MLP hyperparameter tuning by comparing targeted reductions against an all-feature control, while preserving strict subset validation and training-row Pearson diagnostics.

## Fixed Scientific Controls

- Cases and spinup cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL, all `ppe6_I20TRCNPRDCTCBC`
- Split mode: `by_member`
- Train fraction: `0.8`
- Targets: `TOTSOMC,TOTSOMN`
- Model class: NN
- Seeds per variant: `10001-10005` via Slurm array `1-5`
- Variance filter: enabled, threshold `1.0e-12`
- Correlation filter: enabled, threshold `0.98`
- Permutation repeats: `8`
- Quick grid: enabled
- Stats-only output: enabled
- Explicit subset rule: reject configuration if any requested feature is unavailable after filtering

## Variant Matrix

- `all_control`: all 14 parameters, all surface features, all compact climatology features
- `core_params_all_surface_all_clim`: `parm_6,parm_9,parm_10,parm_12,parm_13` plus all surface and all compact climatology features
- `all_params_all_surface_core_clim`: all 14 parameters and all surface features plus `FSDS_clim_mean,PRECTmms_clim_mean,RH_clim_seasonal_amp`
- `core_tri_group`: `parm_6,parm_9,parm_10,parm_12,parm_13` plus `PCT_SAND,PCT_CLAY,ORGANIC` and `FSDS_clim_mean,PRECTmms_clim_mean,RH_clim_seasonal_amp`

This is 20 Slurm array tasks total.

## Artifact Paths

- Canonical Slurm script: `development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm`
- Scratch roots:
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_all_control`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_core_params_all_surface_all_clim`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_all_params_all_surface_core_clim`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_core_tri_group`
- Summary root: `development/spinup_surrogate/summaries/iter006/`
- Feature-stability analyzer: `development/spinup_surrogate/tools/analyze_feature_stability.py`

## Provenance and Submission Log

Source baseline commit: `e694a00`. Working tree state at submission: `dirty` (iter006 artifacts and untracked `plot_surrogate.py`).

| variant | canonical_script | canonical_sha256 | submitted_script | submitted_sha256 | source_head | tree_state | job_id | state | notes |
|---|---|---|---|---|---|---|---|---|---|
| all_control | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_all_control/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `e694a00` | dirty | `56002979` | COMPLETED (5/5) | five seeds |
| core_params_all_surface_all_clim | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_core_params_all_surface_all_clim/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `e694a00` | dirty | `56002981` | REJECTED (2 FAILED, 3 CANCELLED) | explicit subset invalid after filtering |
| all_params_all_surface_core_clim | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_all_params_all_surface_core_clim/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `e694a00` | dirty | `56002984` | COMPLETED (5/5) | five seeds |
| core_tri_group | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter006/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter6_core_tri_group/case.train_surrogate_spinup_iter6_feature_settle.slurm` | `2bfe0210869613a4ed8754159b1cdb5db53e096bb7ac99aa9a4a59bc2c166178` | `e694a00` | dirty | `56002986` | COMPLETED (5/5) | five seeds |

## Execution Log

Submitted in parallel:

- `all_control`: `56002979`
- `core_params_all_surface_all_clim`: `56002981`
- `all_params_all_surface_core_clim`: `56002984`
- `core_tri_group`: `56002986`

Terminal accounting and diagnostics:

- `all_control`: 5 completed, elapsed approximately `112-132s`, MaxRSS approximately `40.02-44.79GB`
- `core_params_all_surface_all_clim`: 2 failed (`56004670`, `56004671`) and 3 cancelled after rejection
- `all_params_all_surface_core_clim`: 5 completed, elapsed approximately `108-146s`, MaxRSS approximately `37.18-47.97GB`
- `core_tri_group`: 5 completed, elapsed approximately `112-153s`, MaxRSS approximately `40.57-47.97GB`
- `seff` across iter006 leaf jobs: CPU efficiency approximately `2.64-3.56%`, memory efficiency approximately `76.25-99.94%`

Explicit rejection evidence (`core_params_all_surface_all_clim`):

- `ValueError: Explicit feature subset includes unavailable feature(s) after feature_set/clim/variance/correlation filtering`
- Missing requested features included: `PRECTmms_clim_min`, `FSDS_clim_std`, `FSDS_clim_min`, `TBOT_clim_seasonal_amp`, `RH_clim_max`, `PSRF_clim_min`, `PSRF_clim_max`

This matches iter006 rule: reject the invalid configuration only and continue evaluating other configurations.

## Results

Aggregated model metrics (`median`):

| variant | TOTSOMC r2_val | TOTSOMN r2_val | TOTSOMC rmse_ratio | TOTSOMN rmse_ratio | warning fraction |
|---|---:|---:|---:|---:|---:|
| all_control | 0.5892 | 0.5892 | 1.0000 | 1.0008 | 0.00 |
| all_params_all_surface_core_clim | 0.5513 | 0.5515 | 1.0132 | 1.0142 | 0.00 |
| core_tri_group | 0.5189 | 0.5188 | 1.0048 | 1.0059 | 0.00 |
| core_params_all_surface_all_clim | rejected | rejected | rejected | rejected | rejected |

Exact features used by each variant:

- Feature sets were stable across all five seeds for each successful variant (`unique_feature_sets=1`).
- Shared filter removals under iter006 controls:
  - dropped by variance: `PRECTmms_clim_min`, `FSDS_clim_min`, `RH_clim_max`
  - dropped by correlation: `FSDS_clim_std`, `TBOT_clim_seasonal_amp`, `PSRF_clim_min`, `PSRF_clim_max`

- `all_control` (`45` features used):
  - `parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp`

- `all_params_all_surface_core_clim` (`20` features used):
  - `parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,FSDS_clim_mean,PRECTmms_clim_mean,RH_clim_seasonal_amp`

- `core_tri_group` (`11` features used):
  - `parm_6,parm_9,parm_10,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,FSDS_clim_mean,PRECTmms_clim_mean,RH_clim_seasonal_amp`

- `core_params_all_surface_all_clim` (rejected; no trained feature set):
  - requested explicit subset:
    - `parm_6,parm_9,parm_10,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_min,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_std,FSDS_clim_min,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,TBOT_clim_seasonal_amp,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_max,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_min,PSRF_clim_max,PSRF_clim_seasonal_amp`
  - unavailable after filtering:
    - `PRECTmms_clim_min`, `FSDS_clim_std`, `FSDS_clim_min`, `TBOT_clim_seasonal_amp`, `RH_clim_max`, `PSRF_clim_min`, `PSRF_clim_max`

Gate comparison versus `all_control`:

- `all_params_all_surface_core_clim` failed the median `r2_val` tolerance on both targets (`-0.0379`, `-0.0377`; limit `-0.01`) and the min-`r2_val` tail bound (`-0.0509`, `-0.0513`; limit `-0.02`)
- `core_tri_group` failed median `r2_val` tolerance on both targets (`-0.0703`, `-0.0704`), min-`r2_val` tail bound (`-0.0964`, `-0.0965`), and `r2_val` IQR expansion gate
- `core_params_all_surface_all_clim` was rejected earlier by explicit subset validation and excluded from promotion

Feature-stability highlights (strong in both targets, selected >=4/5 and top-10 >=3/5):

- `all_control`: `parm_6`, `parm_9`, `parm_10`, `parm_12`, `parm_13`, `PCT_SAND`, `FSDS_clim_mean`, `PRECTmms_clim_mean`, `RH_clim_mean`, `RH_clim_seasonal_amp`
- `all_params_all_surface_core_clim`: retained a similar core but did not meet performance gates
- `core_tri_group`: retained core param/surface/climatology signatures but did not meet performance gates

Promotion decision: no reduced set passed iter006 gates. Keep `all_control` as the baseline for iter007.

## Post-closeout iter007 Planning Update (No Execution Yet)

Planning decisions finalized after iter006 closeout:

- Freeze iter007 inputs to the exact 45 features used by iter006 `all_control` (listed above).
- Run iter007 with explicit subset enforcement and with variance/correlation filters disabled to keep fixed inputs.
- Expose MLP tuning controls through input arguments (replace hardcoded-only workflow; retain backward-compatible defaults).
- Use an external fixed-hyperparameter matrix with 8 candidates total:
  - 4 single-layer candidates
  - 4 two-layer candidates
  - conservative width range (`8-32`)
  - mostly `adam`, with one `lbfgs` stress candidate
- Hyperparameter scope includes `hidden_layer_sizes`, `alpha`, `learning_rate_init`; allow `activation`/`solver` changes for architecture-shift variants.
- No anchor candidate in iter007 matrix; iter006 `all_control` remains the external baseline for comparisons.
- Keep fixed controls for comparability: nine cases, split mode `by_member`, train fraction `0.8`, targets `TOTSOMC,TOTSOMN`, seeds `10001-10005`, resource defaults `--mem=48GB`, `--time=00:30:00`.
- Selection rule for iter007: keep standard iteration-loop gates; among passers, rank by mean median `r2_val` across both targets, then lower `rmse_ratio`, then simpler architecture.

Plan reference for next agent:

- `/global/homes/t/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`

Status note:

- This update records planning only. No iter007 code edits, Slurm submission, or execution were performed.

## Aggregation and Closeout

On success path:

1. Aggregate each variant with `summarize_spinup_stats.py`.
2. Run `development/spinup_surrogate/tools/analyze_feature_stability.py` for each variant.
3. Compare control vs reduced variants using median/tail/IQR/warning/stability gates.
4. Select the simplest passing configuration or retain `all_control` if no reduced configuration passes.
5. Update `registry.csv` and `handoff/CURRENT.md`.

## Closeout Checklist

- [x] Runtime contract recorded
- [x] Iter006 canonical script created
- [x] Iter006 summary root created
- [x] Canonical/submitted checksums recorded
- [x] Arrays submitted and monitored
- [x] `sacct`/`seff` diagnostics recorded
- [x] Variant summaries aggregated
- [x] Feature stability analyzed
- [x] Winner selected under iter006 gates
- [x] `registry.csv` updated
- [x] `CURRENT.md` updated
