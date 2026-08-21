# Iter017 Coupled Optimization-Pipeline Regression

Closeout identity: Iteration ID `iter017`; Status `completed`; Work type `implementation`; Objective `consolidate and end-to-end regress the coupled optimization pipeline before the separate nine-site operational campaign`; Bounded scope `1 preflight; 4 initialization/rebuild jobs; 12 optimization leaves; 4 reporting jobs; 1 handoff validation`; Overall acceptance result `pass`; Decision `technical_pipeline_regression_passed; all four reports insufficient_retained; no posterior promotion; Iter018 planning deferred`.

## Result

The complete three-stage pipeline passed its integrity regression. The tested paths were ABBY daily/0.50, JERC hourly/0.75, and joint ABBY+JERC daily/0.50 and hourly/0.75, each with seeds 9009--9011 and `64x2000` MCMC leaves. Final handoff validator job `23610344` completed `0:0` and emitted `ITER017_HANDOFF_PASS paths=4`.

Every report wrote its standard outputs at the submitted output root: a physical corner plot, per-seed diagnostic/corner/posterior-time-series products, combined CSV and text MAP parameter sets, and one exact `clm_params_seed_<seed>.nc` per seed. NetCDF parameter products remain separate because the ELM input contract requires one value per parameter.

## Retention outcome

All four reports are `insufficient_retained` with zero Tier-A seeds. The short regression leaves had acceptance fractions outside the configured descriptive range, so the pipeline correctly prevented posterior promotion while still producing reviewable standard diagnostics. This is a pipeline behavior result, not a claim of MCMC convergence or a scientific calibration result.

## Provenance and next state

- Production source: `70506cc0221a147b945fa5fc3a03ed767d69d6dd`
- Source manifest: `f2d9ea2d51cdc9180e357172e4bdfcf5cacb9fc3cc695d0f113528a02a490756`
- Dependency manifest: `a636037c452618d4588e3de3a758ef922c6ce4dd43e950ad5d51ef441f7ecefe`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression`

No Iter018 plan is authorized. The next action is a separate discussion and approval of the operational nine-site campaign.
