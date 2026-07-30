# iter005 - Nine-Case Feature Attribution

## Status

- Iteration ID: `iter005`
- Iteration status: `completed`
- Round budget mode: `1 round` (iter005 only)
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
- `development/spinup_surrogate/iterations/iter004.md`
- `development/spinup_surrogate/iterations/iter003.md`
- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter001.md`

`iter004` is closed as failed. Iter001 remains a historical single-case metric reference; its feature-variation finding is not valid evidence for the nine-case study. Cache work is explicitly deferred for this round.

## Objective

Identify important input features under the nine-case setup and determine whether adding surface and climatology features improves model behavior and reduces overfitting relative to parameter-only alternatives.

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
- Source instrumentation retained; `pre_dispatch=n_jobs` used consistently

## Variant Matrix

- `multi_all` -> `feature_set=all`
- `multi_params_surface` -> `feature_set=params_surface`
- `multi_params_clim` -> `feature_set=params_clim`
- `multi_params_only` -> `feature_set=params_only`

This is 20 Slurm array tasks total. All four arrays use identical seeds and scientific controls.

## Feature-Importance Evidence

For both targets, preserve and aggregate:

- Feature retention frequency after variance/correlation filtering
- Permutation-importance magnitude, sign, rank, IQR, and top-10 overlap
- Cross-seed and cross-target stability
- Features removed by filtering, separately from features with weak importance

Provisional strong-feature rule:

- Retained in at least `4/5` seeds
- Top-10 permutation rank in at least `3/5` seeds
- Consistent support across both `TOTSOMC` and `TOTSOMN`
- Supported by feature-set ablation behavior

Correlated features must be interpreted as groups where appropriate; permutation rank alone is not sufficient for promotion.

## Model-Performance Interpretation

Aggregate per variant and target:

- Median `r2_val`
- Median `r2_gap`
- Median `rmse_ratio`
- `overfit_warning_fraction`
- Tails: minimum `r2_val`, maximum `rmse_ratio`
- IQR for each metric

Iter001 medians are historical context only, not a pass/fail gate for this nine-case feature study. Prefer configurations with stable validation performance, lower internal overfitting signals, and feature evidence that agrees with ablations.

## Resource and Provenance Rules

- Use `--mem=48GB`, `--time=00:30:00`, `N_JOBS=4`, and `PRE_DISPATCH=n_jobs`.
- Record `ReqTRES`, `MinCPUsNode`, `AllocCPUS`, and `SLURM_CPUS_PER_TASK`; memory controls Shared-QOS allocation.
- For every variant, record canonical/submitted paths and checksums, source HEAD commit, tree state, job ID, state transitions, `sacct`, `seff`, and timing logs.
- Submit arrays in parallel by default.
- If any variant is blocked after one retry, cancel remaining active/pending jobs, mark iter005 failed, skip aggregation, and update `CURRENT.md`.

## Artifact Paths

- Canonical Slurm script: `development/spinup_surrogate/slurm/iter005/case.train_surrogate_spinup_iter5_feature_attribution.slurm`
- Scratch roots:
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_all`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_surface`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_clim`
  - `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_only`
- Summary root: `development/spinup_surrogate/summaries/iter005/`
- Feature-stability analyzer: `development/spinup_surrogate/tools/analyze_feature_stability.py`

## Provenance and Submission Log

Source baseline commit: `3101069` (`docs(iter004): close source diagnostic round`). The working tree is dirty because iter005 artifacts and the feature-stability analyzer are being created; unrelated `plot_surrogate.py` remains excluded.

| variant | canonical_script | canonical_sha256 | submitted_script | submitted_sha256 | source_head | tree_state | job_id | state | notes |
|---|---|---|---|---|---|---|---|---|---|
| multi_all | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter005/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_all/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `3101069` | dirty; iter005 artifacts plus `plot_surrogate.py` | `55960276` | COMPLETED (5/5) | five seeds |
| multi_params_surface | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter005/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_surface/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `3101069` | dirty; iter005 artifacts plus `plot_surrogate.py` | `55960277` | COMPLETED (5/5) | five seeds |
| multi_params_clim | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter005/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_clim/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `3101069` | dirty; iter005 artifacts plus `plot_surrogate.py` | `55960279` | COMPLETED (5/5) | five seeds |
| multi_params_only | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter005/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter5_multi_params_only/case.train_surrogate_spinup_iter5_feature_attribution.slurm` | `cb85bc045944ca6f50e41e4b1c19a92b97a19e5b29a6caabf48af6e6919116a9` | `3101069` | dirty; iter005 artifacts plus `plot_surrogate.py` | `55960280` | COMPLETED (5/5) | five seeds |

## Execution Log

Submitted all four arrays in parallel after canonical/scratch checksum verification:

- `multi_all`: job `55960276`
- `multi_params_surface`: job `55960277`
- `multi_params_clim`: job `55960279`
- `multi_params_only`: job `55960280`

All four arrays reached terminal state with all 20 tasks completed. No retry or cancellation was required.

Terminal resource range across tasks:

- Elapsed: approximately `00:09:16-00:23:57`
- Allocated CPUs: `26` (memory-determined by the `48GB` request)
- Maximum memory: approximately `36.18-47.97GB`
- `seff` CPU efficiency: approximately `0.26-0.65%`

## Results

Standard summaries:

- `multi_all`: `TOTSOMC` median `r2_val=0.5892`, `rmse_ratio=1.0000`; `TOTSOMN` median `r2_val=0.5892`, `rmse_ratio=1.0008`; median `r2_gap` about `0.002`, warning fraction `0`.
- `multi_params_clim`: `TOTSOMC` median `r2_val=0.5609`, `rmse_ratio=1.0016`; `TOTSOMN` median `r2_val=0.5608`, `rmse_ratio=1.0025`; median `r2_gap` about `-0.017`, warning fraction `0`.
- `multi_params_surface`: `TOTSOMC` median `r2_val=0.4285`, `rmse_ratio=1.0317`; `TOTSOMN` median `r2_val=0.4276`, `rmse_ratio=1.0329`; median `r2_gap` about `0.037`, warning fraction `0`.
- `multi_params_only`: `TOTSOMC` median `r2_val=0.4135`, `rmse_ratio=1.0542`; `TOTSOMN` median `r2_val=0.4124`, `rmse_ratio=1.0554`; median `r2_gap` about `0.029`, warning fraction `0`.

Preferred configuration: `multi_all`. It has the best validation fit and lowest RMSE ratio across both targets. The ablations support a meaningful contribution from climatology features, with a smaller surface-feature contribution.

Stable feature evidence in `multi_all` across both targets:

- Parameter features: `parm_6`, `parm_13`, `parm_9`, `parm_12`, and `parm_10`.
- Surface feature: `PCT_SAND`.
- Climatology features: `FSDS_clim_mean`, `PRECTmms_clim_mean`, and `RH_clim_seasonal_amp`.

These candidates were retained in all five seeds and generally appeared in the top-10 permutation rankings across both targets. Exact stability data is in the per-variant feature-stability JSON files.

Iter001 remains contextual only: iter005 shows lower internal overfitting signals and zero warning fractions, but its nine-case validation medians are not directly comparable to the single-case iter001 values.

## Aggregation and Closeout

On the success path only:

1. Aggregate each variant with `summarize_spinup_stats.py`.
2. Copy summaries to `development/spinup_surrogate/summaries/iter005/`.
3. Aggregate feature diagnostics and permutation stability across seeds and targets.
4. Select the preferred feature configuration only when performance and feature evidence agree.
5. Update `registry.csv` and `CURRENT.md`.
6. Create the iter005 checkpoint commit at closeout.

## Closeout Checklist

- [x] Runtime contract recorded
- [x] Four-variant/five-seed matrix locked
- [x] Canonical script created
- [x] Summary root created
- [x] Canonical/submitted checksums recorded
- [x] Arrays submitted and monitored
- [x] `sacct`/`seff` diagnostics recorded
- [x] Variant summaries aggregated
- [x] Feature stability analyzed
- [x] `registry.csv` updated
- [x] `CURRENT.md` updated
