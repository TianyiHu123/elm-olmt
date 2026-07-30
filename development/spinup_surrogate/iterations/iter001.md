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

1. Move to multi-case setup (9 cases) with `by_member` split to recover variance in surface and forcing-derived climatology features.
2. Run seeds `10001-10030` for iter002 (30 seeds).
3. Use NN-only attribution matrix:
   - `multi_all` (`feature_set=all`)
   - `multi_params_surface` (`feature_set=params_surface`)
   - `multi_params_clim` (`feature_set=params_clim`)
   - `multi_params_only` (`feature_set=params_only`)
4. Keep `train_fraction=0.8`, targets `TOTSOMC,TOTSOMN`, and permutation diagnostics enabled.
5. Compare feature retention + permutation importance and validation metrics (`r2_val`, `r2_gap`, `rmse_ratio`, warning fraction, tails, `IQR=p75-p25`).
6. Apply fail-fast rule: if any variant blocks after one retry, terminate iter002 as `failed` and hand off as debug session.

## Artifacts

- Scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter1_*`
- Aggregated summaries copied to: `development/spinup_surrogate/summaries/iter001/`
- Iter002 canonical script location: `development/spinup_surrogate/slurm/iter002/`
- Iter002 planned scratch root: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`
