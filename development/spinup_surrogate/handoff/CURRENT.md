# Spinup Surrogate - Current Handoff

## Current Objective

Improve spinup surrogate generalization under small-sample conditions while keeping seed-to-seed behavior stable.

## Best Variant So Far

`tuned_nn` (tied with `no_clim` and `reduced_clim`).

## Evidence (iter001, 100 seeds)

For `TOTSOMC` medians:

- `baseline`: `r2_val=0.6056`, `rmse_ratio=0.9412`, warning frac `0.30`
- `tuned_nn`: `r2_val=0.6383`, `rmse_ratio=0.9202`, warning frac `0.41`
- `rf_constrained`: `r2_val=0.5942`, `rmse_ratio=1.2891`, warning frac `0.95`

`TOTSOMN` shows the same ranking pattern.

## What Changed in Latest Iteration

- Added feature filtering + diagnostics in spinup training.
- Ran five variants across 100 seeds each.
- Generated and copied summary JSON files into `development/spinup_surrogate/summaries/iter001/`.

## Open Risks / Unknowns

- Baseline has lower warning fraction but weaker median `r2_val`.
- Current setup is single-case; non-parameter features are mostly constant and removed by variance filter.
- Need confirmation that improvements hold under broader case/site diversity.

## Next Iteration Plan (iter002)

1. Keep parameter-only NN path.
2. Run a small NN regularization sweep (focused alpha/hidden-size choices).
3. Keep fixed seed range and split settings for fair comparison.
4. Re-evaluate median metrics plus tails and warning fractions.

## Exact Commands to Run Next

Example submission pattern:

```bash
VARIANT=tuned_nn sbatch examples/slurm/case.train_surrogate_spinup_iter1.slurm
```

(Create iter002 Slurm scripts under `development/spinup_surrogate/slurm/iter002/` before running.)

## Artifact Paths

- Scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter1_*`
- Repo summaries: `development/spinup_surrogate/summaries/iter001/`

## Files Modified in Repo (latest cycle)

- `model_ELM/surrogate_NN_Spinup.py`
- `train_surrogate_spinup.py`
- `examples/slurm/case.train_surrogate_spinup_iter1.slurm`
- `summarize_spinup_stats.py`
