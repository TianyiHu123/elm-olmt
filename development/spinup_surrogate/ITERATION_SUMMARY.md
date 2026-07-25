# Spinup Surrogate Iteration Summary: iter001-iter010

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
- `iter008` implemented global pre-split correlation filtering, then tested the compact Adam
  control and five `(32,)`, tanh/LBFGS regularization levels under full45, 0.80, and 0.60 feature
  policies. LBFGS alpha 50/full45 was selected and materially improved both targets.
- `iter009` confirmed alpha-50/full45 as the strongest eligible candidate; lower alpha improved
  R2 but warned in one of five seeds.
- `iter010` used 100 seeds across 15 alpha/policy variants. Every variant warned in 22--25% of
  seeds, including alpha-50/full45, so no candidate was eligible and the Iter009 baseline remains
  retained.

Current preferred configuration: retain the full 45-feature schema and use iter008
`s32_tanh_lbfgs_a50_lr1e3_full45`. It is the highest full-gate passer so far.

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
| iter008 | Nine cases, `by_member` | Five per variant | Global feature pruning and LBFGS regularization | Completed: retain `(32,)` tanh/LBFGS alpha 50, full45 |
| iter009 | Nine cases, `by_member` | Five per variant | Alpha-50 refinement and forcing-group ablation | Completed: retain alpha-50 full45 |
| iter010 | Nine cases, `by_member` | 100 per variant | Warning-threshold bracket and importance stability | Completed: no gate passer; retain Iter009 baseline |

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

### iter008 — Global Correlation Pruning and LBFGS Regularization

Objective: test whether global, target-free correlation pruning improves the selected compact Adam
baseline and whether stronger LBFGS L2 regularization resolves iter007's RMSE-ratio/warning failure.

Locked setup:

- Nine cases; `by_member` split; train fraction `0.8`; targets `TOTSOMC,TOTSOMN`; five seeds.
- Exact iter006 45-feature pool; variance filtering disabled. Correlation filtering, when enabled,
  ran before split with priority drops for `WIND_*`, `PSRF_*`, and `FLDS_*`.
- Eighteen variants: the `(8,), tanh, adam, alpha=10` control plus `(32,), tanh, lbfgs` at alpha
  `50,100,250,500,1000`, each under `full45`, `corr080_prioritydrop`, and
  `corr060_prioritydrop`.
- Puma: `standard` / `chopinsong`, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, per-task
  cache isolation. All 90 leaves completed; aggregation job `23362489` completed.

Feature-schema evidence: full45, corr080, and corr060 retained 45, 25, and 21 features,
respectively, with identical selected schemas across all five seeds.

| Full-gate passer | TOTSOMC/TOTSOMN median R2 | Validation RMSE | RMSE ratio | Decision |
| --- | --- | --- | --- | --- |
| **LBFGS alpha 50, full45** | **0.7935 / 0.7937** | **4661.8 / 469.7** | **0.9499 / 0.9561** | **Selected** |
| LBFGS alpha 50, corr080 | 0.7896 / 0.7906 | 4719.5 / 472.6 | 0.9531 / 0.9539 | Pass; lower R2 than full45 |
| LBFGS alpha 50, corr060 | 0.7726 / 0.7724 | 4866.4 / 487.2 | 0.9542 / 0.9552 | Pass; lower R2 than full45 |
| LBFGS alpha 100, full45 | 0.6908 / 0.6905 | 5861.8 / 586.9 | 0.9727 / 0.9737 | Pass; lower R2 than alpha 50 |
| LBFGS alpha 100, corr080 | 0.6796 / 0.6798 | 5966.2 / 597.3 | 0.9817 / 0.9826 | Pass; lower R2 than alpha 50 |
| Adam control, full45 | 0.5892 / 0.5892 | 6758.3 / 676.4 | 1.0000 / 1.0008 | Pass; iter007 baseline |

All other candidates were rejected: the pruned Adam arms missed R2 gates; LBFGS alpha 100/corr060
warned on 2/5 seeds; alpha 250 and above missed R2 gates, with alpha 500/1000 also exceeding RMSE
ratio limits in some policies. The selected alpha-50/full45 model had zero overfit warnings and
the highest mean cross-target median R2 (`0.7936`).

Conclusion: retain full45 rather than promote correlation pruning. The iter007 LBFGS signal was
real but required stronger regularization; alpha 50 converted it into the best eligible model.
The next proposed round narrows full45 LBFGS alpha around 50 (`25,35,50,65,75`) under a fresh
runtime contract.

### iter009 — Alpha-50 LBFGS Refinement and Forcing-Group Ablation

Objective: refine the iter008 alpha-50 LBFGS selection and test whether global correlation-0.80
pruning or direct exclusion of FLDS/WIND/PSRF climatology inputs improves generalization.

Locked setup:

- Nine cases; `by_member` split; train fraction `0.8`; `TOTSOMC,TOTSOMN`; seeds `10001-10005`.
- `(32,), tanh, lbfgs` at alpha `25,35,50,65,75`; learning rate `1e-3` recorded as provenance.
- Three policies per alpha: strict full45; global pre-split `corr080_prioritydrop`; and strict
  32-feature `drop_flds_wind_psrf` using forcing variables `PRECTmms,FSDS,TBOT,RH`.
- Puma `standard` / `chopinsong`, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, task-local
  cache. Preflight `23370951`, all 75 leaves, and aggregation `23371111` completed without retry.
- Leaf elapsed range was `00:01:17-00:02:09`; MaxRSS was `37314780K-52427868K`. Full45,
  corr080, and drop32 schemas were seed-invariant at 45, 25, and 32 features.

The table reports `TOTSOMC / TOTSOMN` five-seed medians. Absolute RMSE is validation RMSE;
RMSE ratio is the median of per-seed validation/training RMSE ratios.

| Alpha and policy | Median validation R2 | Validation RMSE | RMSE ratio | Warning fraction | Decision |
| --- | --- | --- | --- | --- | --- |
| 25 full45 | 0.8538 / 0.8542 | 3668.8 / 367.5 | 0.9652 / 0.9661 | 0.2 / 0.2 | Reject: warning gate |
| 25 corr080 | 0.8547 / 0.8540 | 3708.9 / 370.6 | 0.9588 / 0.9578 | 0.2 / 0.2 | Reject: warning gate |
| 25 drop32 | 0.8506 / 0.8519 | 3696.1 / 370.4 | 0.9551 / 0.9565 | 0.2 / 0.2 | Reject: warning gate |
| 35 full45 | 0.8291 / 0.8286 | 4137.7 / 413.9 | 0.9518 / 0.9518 | 0.2 / 0.2 | Reject: warning gate |
| 35 corr080 | 0.8276 / 0.8270 | 4165.2 / 417.0 | 0.9425 / 0.9440 | 0.2 / 0.2 | Reject: warning gate |
| 35 drop32 | 0.8259 / 0.8258 | 4204.0 / 420.5 | 0.9509 / 0.9519 | 0.2 / 0.2 | Reject: warning gate |
| **50 full45** | **0.7935 / 0.7937** | **4661.8 / 469.7** | **0.9499 / 0.9561** | **0 / 0** | **Pass; selected** |
| 50 corr080 | 0.7896 / 0.7906 | 4719.5 / 472.6 | 0.9531 / 0.9539 | 0 / 0 | Pass; lower R2 |
| 50 drop32 | 0.7906 / 0.7904 | 4746.2 / 474.8 | 0.9533 / 0.9541 | 0 / 0 | Pass; lower R2 |
| 65 full45 / corr080 / drop32 | 0.7496-0.7605 / 0.7539-0.7571 | 5106.3-5183.6 / 510.9-518.9 | 0.9605-0.9653 / 0.9614-0.9661 | 0 / 0 | Reject: median and minimum R2 |
| 75 full45 / corr080 / drop32 | 0.7343-0.7393 / 0.7342-0.7391 | 5336.9-5450.7 / 534.0-545.8 | 0.9637-0.9723 / 0.9645-0.9732 | 0 / 0 | Reject: R2; some RMSE ratio |

Conclusion: retain alpha-50/full45. Lower alpha values produced much better R2 and absolute RMSE,
but one of five seeds warned for both targets under every policy, so they failed the locked gate.
Neither correlation pruning nor removal of all 13 FLDS/WIND/PSRF features improved the eligible
control. The evidence brackets the warning transition between alpha 35 and 50 and supports a
future full45-only intermediate-alpha study.

### iter010 — 100-Seed Warning-Threshold Test and Importance Stability

Iter010 tested alpha `40,42.5,45,47.5,50` under full45, corr080, and drop32 with 100 seeds per
variant (1,500 leaves). The corrected production matrix completed 1,500/1,500 leaves `0:0`; the
exact validator and aggregation job `23399438` completed successfully. Full45, corr080, and
drop32 remained seed-invariant at 45, 25, and 32 features respectively.

Every candidate failed the zero-warning gate: TOTSOMC/TOTSOMN warning fractions ranged from
`0.22/0.22` to `0.25/0.24`. Alpha-40/full45 had the best median R2 (`0.8310/0.8301`) and absolute
validation RMSE (`4090.9/410.8`), but warned on 24% of seeds for both targets. The alpha-50/full45
control also warned on 22% of seeds, overturning the five-seed zero-warning result. Consequently,
no Iter010 candidate is promoted and Iter009 alpha-50/full45 remains the baseline. The 100-seed
importance records consistently rank `parm_6`, `parm_13`, `parm_12`, `parm_9`, and `parm_10` at
the top for alpha-40/full45 across both targets.

Operational lessons recorded in `iterations/iter010.md`: sequentialize dependent Bash assignments;
do not let `sbatch` inherit a manifest loop's stdin; construct `--chdir`, logs, and exported config
paths from one validated run root; and keep the primary agent active through terminal accounting,
aggregation, decision, records, and closeout.

## Main Conclusions Through iter010

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
7. Iter008 established that global correlation pruning is seed-invariant but does not improve the
   selected full45 policy. LBFGS alpha 50/full45 is the current best eligible model.
8. Runtime is operationally manageable at 30 minutes, but memory remains near the request ceiling
   and CPU efficiency remains low.
9. Iter009 retained alpha-50/full45: alpha 25/35 improved R2 and absolute RMSE but warned on one
   seed for both targets, while corr080 and the strict 32-feature forcing-group ablation did not
   improve the eligible alpha-50 control.
10. Iter010's 100-seed matrix found 22--25% warnings for every alpha/policy arm, including
    alpha-50/full45; the five-seed zero-warning observation did not generalize. No threshold
    candidate may be promoted without changing the gate under a future, explicit contract.

## Next Iteration Guidance

Retain full45 and `(32,), tanh, lbfgs, alpha=50` as the current baseline. Before any Iter011
proposal, decide whether the warning definition is scientifically appropriate in light of the
100-seed evidence; do not relax the Iter010 zero-warning gate retroactively. Any new work requires
a new runtime contract, reviewer, and no-training preflight.

## Source Artifacts

- Canonical workflow: `development/spinup_surrogate/WORKFLOW.md`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Detailed reports: `development/spinup_surrogate/iterations/iter001.md` through `iter010.md`
- Iter005 summaries: `development/spinup_surrogate/summaries/iter005/`
- Iter006 summaries: `development/spinup_surrogate/summaries/iter006/`
- Iter007 summaries: `development/spinup_surrogate/summaries/iter007/`
- Iter008 summaries: `development/spinup_surrogate/summaries/iter008/`
- Iter009 summaries: `development/spinup_surrogate/summaries/iter009/`
- Iter010 summaries: `development/spinup_surrogate/summaries/iter010/`
- Feature analyzer: `development/spinup_surrogate/analyze_feature_stability.py`
