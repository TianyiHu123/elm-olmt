# Spinup Surrogate Iteration Summary: iter001-iter005

## Executive Summary

The workflow progressed from a single-case overfitting baseline to a successful nine-case feature-attribution study.

- `iter001` established the single-case NN baseline, but surface and climatology features had no usable variation and were removed by filtering.
- `iter002` moved to nine cases but failed because the five-minute walltime was inadequate; its retry pilot also timed out.
- `iter003` tested GridSearchCV parallelism and failed its runtime gate under both four- and eight-worker profiles.
- `iter004` instrumented source phases and showed that per-case forcing preparation, not model fitting, dominated runtime. A combined xarray-loading change did not improve runtime or memory.
- `iter005` successfully completed all 20 nine-case tasks using five seeds for each of four feature-set variants. `multi_all` was the preferred configuration, and stable surface/climatology features were identified.

Current preferred direction: use `multi_all` as the nine-case baseline and validate a reduced, interpretable feature set with targeted grouped ablations.

## Cross-Iteration Setup

| Iteration | Scientific setup | Seeds | Main purpose | Outcome |
|---|---|---:|---|---|
| iter001 | One case, `by_member` | 100 per variant | Overfitting-control baseline | Completed |
| iter002 | Nine cases, `by_member` | 30 per variant | Recover surface/climatology variation | Failed: walltime |
| iter003 | Nine cases, `by_member` | Five pilot seeds | Parallelism and timeout reduction | Failed: runtime |
| iter004 | Nine cases, `by_member` | One diagnostic seed plus retry | Source timing and memory diagnosis | Failed: memory headroom |
| iter005 | Nine cases, `by_member` | Five per variant | Feature attribution and model comparison | Completed |

All multicase iterations used train fraction `0.8`, targets `TOTSOMC,TOTSOMN`, compact climatology features, NN models, variance/correlation filtering, and permutation diagnostics unless noted otherwise.

## Iteration Details

### iter001 — Single-Case Variant Sweep

Setup:

- Case: `ABBY_ppe6_I20TRCNPRDCTCBC`
- Spinup case: `ABBY_ppe6_I1850CNPRDCTCBC`
- Five variants, 100 seeds each

Representative `TOTSOMC` medians:

| Variant | r2_val | r2_gap | rmse_ratio | Warning fraction |
|---|---:|---:|---:|---:|
| baseline | 0.6056 | 0.0207 | 0.9412 | 0.30 |
| tuned_nn | 0.6383 | 0.0541 | 0.9202 | 0.41 |
| no_clim | 0.6383 | 0.0541 | 0.9202 | 0.41 |
| reduced_clim | 0.6383 | 0.0541 | 0.9202 | 0.41 |
| rf_constrained | 0.5942 | 0.3174 | 1.2891 | 0.95 |

Finding: diagnostics retained only `parm_0` through `parm_13`. Surface and climatology features were removed by variance filtering in this single-case setup. NN variants were preferred over constrained RF.

Limitation: iter001 is not valid evidence about feature importance under case diversity because surface and climatology inputs had no usable variation.

### iter002 — Nine-Case Feature Attribution Attempt

Setup:

- Nine cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL
- Four NN feature-set variants
- 30 seeds per variant
- `--mem=42GB`, `--time=00:05:00`

Results:

- `multi_all`: 5 completed, 25 timeouts
- Each ablation variant: 4 completed, 26 timeouts
- Retry pilot at `00:15:00`: one completed, one timeout, remaining tasks cancelled

Decision: fail-fast closeout. No aggregation or winner selection was allowed.

### iter003 — Parallelism and Timeout Pilot

Objective: test whether GridSearchCV parallelism could improve CPU efficiency and runtime.

- Four-worker pilot: one seed completed at `00:18:13`; another timed out at `00:20:21`.
- Eight-worker retry: four of five seeds timed out between `00:20:09` and `00:20:22`.
- Memory reached approximately `41.97/42GB`.
- `seff` CPU efficiency remained approximately `0.26-0.42%`.

Resource interpretation lesson: under NERSC Shared QOS, the `42GB` memory request dominated CPU allocation, producing `AllocCPUS=24`; `cpus-per-task` was not a direct physical-core allocation proxy.

Decision: fail-fast closeout. The full matrix was not launched.

### iter004 — Source-Level Timing and Memory Diagnosis

Instrumentation added:

- Per-case preparation timing
- Design-matrix timing
- Feature-selection timing
- GridSearchCV timing
- Permutation-importance timing
- Configurable `GridSearchCV pre_dispatch`

Initial diagnostic:

- Completed in `00:19:19`
- Memory reached `41.97/42GB`
- Per-case preparation took approximately `53-186s` per case
- Design matrix and model fitting were negligible by comparison

Source-fix retry:

- Combined forcing-variable xarray load
- Completed in `00:26:18`
- Memory remained `41.97/42GB`
- No runtime improvement; the attempted forcing-load optimization was not promoted

Decision: fail-fast closeout. The workflow accepted the approximately 30-minute task runtime operationally and returned focus to scientific feature attribution.

### iter005 — Successful Nine-Case Feature Attribution

Setup:

- Four variants: `multi_all`, `multi_params_surface`, `multi_params_clim`, `multi_params_only`
- Five seeds per variant: `10001-10005`
- `--mem=48GB`, `--time=00:30:00`, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`
- 20 tasks total; all completed

Resource results:

- Task elapsed range: approximately `00:09:16-00:23:57`
- Memory range: approximately `36.18-47.97GB`
- Allocated CPUs: `26`, determined largely by the `48GB` memory request
- `seff` CPU efficiency: approximately `0.26-0.65%`

Standard metric medians:

| Variant | TOTSOMC r2_val | TOTSOMN r2_val | TOTSOMC rmse_ratio | TOTSOMN rmse_ratio | TOTSOMC r2_gap | Warning fraction |
|---|---:|---:|---:|---:|---:|---:|
| multi_all | 0.5892 | 0.5892 | 1.0000 | 1.0008 | 0.0017 | 0 |
| multi_params_clim | 0.5609 | 0.5608 | 1.0016 | 1.0025 | -0.0169 | 0 |
| multi_params_surface | 0.4285 | 0.4276 | 1.0317 | 1.0329 | 0.0373 | 0 |
| multi_params_only | 0.4135 | 0.4124 | 1.0542 | 1.0554 | 0.0291 | 0 |

Interpretation:

- `multi_all` is the preferred nine-case configuration.
- Climatology features provide a substantial contribution: `multi_params_clim` clearly outperforms `multi_params_only`.
- Surface features provide a smaller contribution: `multi_params_surface` is slightly better than `multi_params_only`, but substantially below the climatology-inclusive variants.
- All variants had zero overfit warnings and near-zero or negative median `r2_gap`, indicating improved internal overfitting behavior relative to the single-case warning pattern.
- Iter001 values are historical context only; direct performance comparison is confounded by the change from one case to nine cases.

Stable `multi_all` feature candidates across both targets:

- Parameters: `parm_6`, `parm_13`, `parm_9`, `parm_12`, `parm_10`
- Surface: `PCT_SAND`
- Climatology: `FSDS_clim_mean`, `PRECTmms_clim_mean`, `RH_clim_seasonal_amp`

These candidates were retained across all five seeds and generally appeared in the top-10 permutation rankings for both targets. Full retention, rank, magnitude, sign, IQR, and overlap data are in:

- `development/spinup_surrogate/summaries/iter005/*_summary.json`
- `development/spinup_surrogate/summaries/iter005/*_feature_stability.json`

## Main Conclusions

1. The single-case feature conclusion from iter001 was limited by absent surface/climatology variation.
2. Nine-case diversity made surface and climatology features informative.
3. The all-feature NN performed best among the iter005 variants.
4. Climatology features contributed more strongly than surface features in the tested ablation comparison.
5. Overfitting diagnostics improved substantially in the nine-case study, with zero warning fractions across all iter005 variants.
6. Runtime is operationally manageable at 30 minutes, but memory remains near the request ceiling and CPU efficiency remains low.

## Next Recommended Iteration: iter006

Use `multi_all` as the control and freeze the current MLP quick-grid while settling the feature set. Do not rerun a parameter-only configuration.

- Test four five-seed configurations, each retaining parameter, surface, and climatology groups: all eligible features; core parameters plus all surface/climatology; all parameters/surface plus core climatology; and core parameters plus all surface plus core climatology.
- Add training-row Pearson pair analysis at `|r| >= 0.80`, `0.90`, `0.95`, and `0.98`.
- Reject a requested subset if filtering removes one of its required features.
- Choose the simplest reduced set that remains within the performance, tail, IQR, and cross-seed feature-stability gates.
- Defer MLP hyperparameter tuning to iter007.

## Source Artifacts

- Canonical workflow: `development/spinup_surrogate/WORKFLOW.md`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Detailed reports: `development/spinup_surrogate/iterations/iter001.md` through `iter005.md`
- Iter005 summaries: `development/spinup_surrogate/summaries/iter005/`
- Feature analyzer: `development/spinup_surrogate/analyze_feature_stability.py`
