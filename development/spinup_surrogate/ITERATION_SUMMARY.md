# Spinup Surrogate Iteration Summary: iter001-iter007

## Executive Summary

The workflow progressed from a single-case overfitting baseline to a validated nine-case feature
set and fixed-MLP selection.

- `iter001` established the single-case NN baseline, but surface and climatology features had no usable variation and were removed by filtering.
- `iter002` moved to nine cases but failed because the five-minute walltime was inadequate; its retry pilot also timed out.
- `iter003` tested GridSearchCV parallelism and failed its runtime gate under both four- and eight-worker profiles.
- `iter004` instrumented source phases and showed that per-case forcing preparation, not model fitting, dominated runtime. A combined xarray-loading change did not improve runtime or memory.
- `iter005` successfully completed all 20 nine-case tasks using five seeds for each of four feature-set variants. `multi_all` was the preferred configuration, and stable surface/climatology features were identified.
- `iter006` tested whether a smaller interpretable feature set could retain the all-feature result.
  No reduction passed the locked validation/tail/stability gates, so the exact 45-feature
  `all_control` set was retained.
- `iter007` held those 45 features fixed and evaluated eight MLP configurations. The compact
  `(8,)`, `tanh`, `adam`, alpha `10`, learning rate `1e-3` model was the sole gate passer and
  exactly reproduced the iter006 baseline.

Current preferred configuration: retain the iter006 45-feature `all_control` input set and use
the iter007 `s08_tanh_adam_a10_lr1e3` fixed MLP. No tested feature reduction or MLP alternative
improved it under the declared gates.

## Cross-Iteration Setup

| Iteration | Scientific setup | Seeds | Main purpose | Outcome |
|---|---|---:|---|---|
| iter001 | One case, `by_member` | 100 per variant | Overfitting-control baseline | Completed |
| iter002 | Nine cases, `by_member` | 30 per variant | Recover surface/climatology variation | Failed: walltime |
| iter003 | Nine cases, `by_member` | Five pilot seeds | Parallelism and timeout reduction | Failed: runtime |
| iter004 | Nine cases, `by_member` | One diagnostic seed plus retry | Source timing and memory diagnosis | Failed: memory headroom |
| iter005 | Nine cases, `by_member` | Five per variant | Feature attribution and model comparison | Completed |
| iter006 | Nine cases, `by_member` | Five per variant | Feature-set settlement | Completed: retain 45 features |
| iter007 | Nine cases, `by_member` | Five per variant | Fixed MLP hyperparameter tuning | Completed: retain `(8,)` tanh/adam MLP |

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

### iter006 — Feature-Set Settlement and the 45-Feature Decision

Setup:

- Five seeds per variant (`10001-10005`), the same nine cases, `by_member` split, and both
  spinup targets.
- `all_control` retained all 14 parameters, all three surface variables, and 28 compact
  climatology features: 45 features total.
- Reduced candidates used 20 features (`all_params_all_surface_core_clim`) or 11 features
  (`core_tri_group`). `core_params_all_surface_all_clim` was rejected before fitting because
  seven requested features were unavailable after the locked variance/correlation filtering.

The table reports five-seed medians. `r2_val` is shown as `median / minimum / IQR` for each
target; absolute validation RMSE and RMSE ratio are shown as `TOTSOMC / TOTSOMN`. RMSE ratio is
the median of per-seed `validation RMSE / training RMSE` values. Warning fraction is the fraction
of seeds with an overfit warning.

| Feature variant | Features | TOTSOMC r2_val | TOTSOMN r2_val | Validation RMSE | RMSE ratio | Warning fraction | Decision |
| --- | ---: | --- | --- | ---: | --- | --- | --- |
| **all_control** | **45** | **0.5892 / 0.4922 / 0.0745** | **0.5892 / 0.4930 / 0.0746** | **6758.3 / 676.4** | **1.0000 / 1.0008** | **0.00 / 0.00** | **Retained** |
| all_params_all_surface_core_clim | 20 | 0.5513 / 0.4413 / 0.0521 | 0.5515 / 0.4417 / 0.0517 | 7590.5 / 760.2 | 1.0132 / 1.0142 | 0.00 / 0.00 | Rejected: median and tail R2 gates fail |
| core_tri_group | 11 | 0.5189 / 0.3958 / 0.1122 | 0.5188 / 0.3965 / 0.1124 | 7368.2 / 737.8 | 1.0048 / 1.0059 | 0.00 / 0.00 | Rejected: median, tail, and IQR R2 gates fail |
| core_params_all_surface_all_clim | — | — | — | — | — | — | Rejected before fitting: explicit subset invalid after filtering |

Why the 45 features were retained:

- The 20-feature reduction lost `0.0379 / 0.0377` median validation R2 and `0.0509 / 0.0513`
  minimum validation R2 versus control (`TOTSOMC / TOTSOMN`), exceeding the allowed drops of
  `0.01` and `0.02` respectively.
- The 11-feature reduction lost `0.0703 / 0.0704` median validation R2, lost
  `0.0964 / 0.0965` at the validation tail, and expanded R2 IQR to approximately `0.112`, beyond
  the control-IQR allowance.
- All completed variants had zero warnings, so the decision is driven by validated performance
  and stability rather than a warning tradeoff.
- Strong cross-target feature evidence in the selected 45-feature set included `parm_6`,
  `parm_9`, `parm_10`, `parm_12`, `parm_13`, `PCT_SAND`, `FSDS_clim_mean`,
  `PRECTmms_clim_mean`, `RH_clim_mean`, and `RH_clim_seasonal_amp`.

### iter007 — Fixed-Feature MLP Hyperparameter Selection

Setup:

- The exact 45 iter006 `all_control` features were frozen. Variance and correlation filtering
  were disabled so every MLP saw identical inputs.
- Five seeds per candidate, eight fixed MLP configurations, `by_member` split, and the same nine
  cases/targets were used.
- Gates were applied independently to both targets: median validation R2 no more than `0.01`
  below control, minimum R2 no more than `0.02` below, R2 IQR within `0.02`, median RMSE ratio
  within `0.02`, and no overfit warnings.

The table reports five-seed medians. `R2 gap` is median `train R2 - validation R2`; absolute
validation RMSE, RMSE ratio, R2 gap, and warning fraction are all shown as `TOTSOMC / TOTSOMN`.

| MLP variant | Hidden layers; activation; solver | Alpha; learning rate | TOTSOMC/TOTSOMN r2_val (median / min / IQR) | Validation RMSE | RMSE ratio | R2 gap | Warning fraction | Decision |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| **s08_tanh_adam_a10_lr1e3** | **(8,); tanh; adam** | **10; 1e-3** | **0.5892 / 0.4922 / 0.0745; 0.5892 / 0.4930 / 0.0746** | **6758.3 / 676.4** | **1.0000 / 1.0008** | **0.0017 / 0.0024** | **0.00 / 0.00** | **Selected: only full gate passer; reproduces iter006 control** |
| s16_tanh_adam_a50_lr1e3 | (16,); tanh; adam | 50; 1e-3 | 0.4082 / 0.3109 / 0.0503; 0.4080 / 0.3116 / 0.0503 | 8650.9 / 866.1 | 1.0037 / 1.0046 | 0.0111 / 0.0116 | 0.00 / 0.00 | Reject: median and tail R2 |
| s24_relu_adam_a50_lr5e4 | (24,); relu; adam | 50; 5e-4 | 0.3326 / 0.2660 / 0.0598; 0.3341 / 0.2673 / 0.0593 | 8989.5 / 899.7 | 1.0092 / 1.0100 | 0.0280 / 0.0275 | 0.00 / 0.00 | Reject: median and tail R2 |
| s32_tanh_lbfgs_a10_lr1e3 | (32,); tanh; lbfgs | 10; 1e-3* | 0.9043 / 0.8884 / 0.0339; 0.9045 / 0.8883 / 0.0327 | 3096.6 / 308.3 | 1.2244 / 1.2176 | 0.0324 / 0.0322 | 0.40 / 0.40 | Reject: RMSE-ratio caps and warning gate |
| d08_08_tanh_adam_a10_lr1e3 | (8, 8); tanh; adam | 10; 1e-3 | 0.5588 / 0.4051 / 0.0871; 0.5586 / 0.4057 / 0.0874 | 7511.7 / 752.1 | 0.9966 / 0.9976 | -0.0134 / -0.0127 | 0.00 / 0.00 | Reject: median and tail R2 |
| d16_08_tanh_adam_a50_lr1e3 | (16, 8); tanh; adam | 50; 1e-3 | 0.2666 / 0.2201 / 0.0309; 0.2652 / 0.2210 / 0.0506 | 9351.8 / 936.1 | 1.0251 / 1.0260 | 0.0265 / 0.0269 | 0.00 / 0.00 | Reject: median and tail R2 |
| d16_16_relu_adam_a50_lr5e4 | (16, 16); relu; adam | 50; 5e-4 | 0.2016 / 0.1108 / 0.0971; 0.2030 / 0.1121 / 0.0976 | 10061.0 / 1007.4 | 1.0173 / 1.0182 | 0.0191 / 0.0191 | 0.00 / 0.00 | Reject: median and tail R2 |
| d32_16_tanh_adam_a100_lr1e3 | (32, 16); tanh; adam | 100; 1e-3 | 0.1785 / 0.1080 / 0.0148; 0.1795 / 0.1084 / 0.0151 | 9526.0 / 953.7 | 1.0390 / 1.0399 | 0.0333 / 0.0336 | 0.00 / 0.00 | Reject: median and tail R2 |

`*` Scikit-learn's `lbfgs` solver does not use `learning_rate_init`; it is recorded only for
matrix provenance. Although the lbfgs candidate attained the highest R2 and lowest absolute RMSE,
its validation-to-training RMSE ratio exceeded the overfit threshold and 2/5 seeds warned for
overfitting. It was therefore ineligible under the predeclared gate.

The selected `(8,)` tanh/adam model retained the same strong cross-target top-10 stability signals
as iter006 (`FSDS_clim_mean`, `PCT_SAND`, `PRECTmms_clim_mean`, `RH_clim_seasonal_amp`, `parm_6`,
`parm_9`, `parm_10`, `parm_12`, and `parm_13`). This confirms that the parameter selection did
not obtain its result by changing the frozen feature evidence.

## Main Conclusions Through iter007

1. The single-case feature conclusion from iter001 was limited by absent surface/climatology variation.
2. Nine-case diversity made surface and climatology features informative.
3. The 45-feature iter006 `all_control` set was the only feature configuration to meet all
   performance, tail, IQR, and validity requirements; no reduced set is justified by the data.
4. With those inputs frozen, the compact `(8,)` tanh/adam MLP was the only iter007 parameter
   configuration to satisfy all gates. It matches, rather than improves upon, the feature-control
   baseline.
5. The high-R2 lbfgs candidate illustrates why absolute RMSE/R2 alone is insufficient: its RMSE
   ratio and warning fraction showed unacceptable generalization behavior.
6. Overfitting diagnostics remain clean for the selected configuration (zero warnings), and the
   same cross-target feature-stability signals remain present.
7. Runtime is operationally manageable at 30 minutes, but memory remains near the request ceiling
   and CPU efficiency remains low.

## Next Iteration Guidance

Retain the exact 45-feature input set and the selected fixed MLP `(8,)`, `tanh`, `adam`, alpha
`10`, learning rate `1e-3` as the current baseline. A future iteration should start from a new
runtime contract and state a distinct hypothesis; it should not repeat these failed reductions or
hyperparameter variants without a new scientific reason.

## Source Artifacts

- Canonical workflow: `development/spinup_surrogate/WORKFLOW.md`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Detailed reports: `development/spinup_surrogate/iterations/iter001.md` through `iter007.md`
- Iter005 summaries: `development/spinup_surrogate/summaries/iter005/`
- Iter006 summaries: `development/spinup_surrogate/summaries/iter006/`
- Iter007 summaries: `development/spinup_surrogate/summaries/iter007/`
- Feature analyzer: `development/spinup_surrogate/analyze_feature_stability.py`
