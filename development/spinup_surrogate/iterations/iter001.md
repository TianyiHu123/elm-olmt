# iter001 - Variant Sweep Baseline

## Objective

Evaluate overfitting mitigation strategies for the spinup surrogate with seed-robust comparison across five variants.

## Fixed Setup

- Case: `ABBY_ppe6_I20TRCNPRDCTCBC`
- Spinup case: `ABBY_ppe6_I1850CNPRDCTCBC`
- Split mode: `by_member`
- Train fraction: `0.8`
- Seeds: `10001-10100` (100 runs per variant)
- Targets: `TOTSOMC`, `TOTSOMN`

## Variants

- `baseline`
- `tuned_nn`
- `no_clim`
- `reduced_clim`
- `rf_constrained`

## Key Results (medians)

Using `TOTSOMC` as representative (same ranking for `TOTSOMN`):

- `baseline`: `r2_val=0.6056`, `r2_gap=0.0207`, `rmse_ratio=0.9412`, warning fraction `0.30`
- `tuned_nn`: `r2_val=0.6383`, `r2_gap=0.0541`, `rmse_ratio=0.9202`, warning fraction `0.41`
- `no_clim`: identical to `tuned_nn`
- `reduced_clim`: identical to `tuned_nn`
- `rf_constrained`: `r2_val=0.5942`, `r2_gap=0.3174`, `rmse_ratio=1.2891`, warning fraction `0.95`

## Diagnostic Finding

For `tuned_nn`, `no_clim`, and `reduced_clim`, `feature_diagnostics` consistently selected only:

- `parm_0 ... parm_13` (14 parameter features)

Surface and climatology features were dropped by variance filtering in this single-case setup.

## Decision

Use parameter-only NN as the main direction for next iteration. Keep RF out of primary path for now.

## Next Iteration Plan (iter002)

1. Parameter-only NN regularization sweep (small targeted grid).
2. Optional baseline control run for drift check.
3. Keep same seed range for direct comparability.
4. Re-check warning fraction and validation tails.

## Artifacts

- Scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter1_*`
- Aggregated summaries copied to: `development/spinup_surrogate/summaries/iter001/`
