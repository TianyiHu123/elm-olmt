# Iter008 MCMC diagnostic report

## Reproducible setup
- Sites: ABBY
- Variables: SR
- Walkers x steps: 64 x 4000
- Seed: 8008
- Discard/thin: 2545; 255
- Eligible draws: 384; predictive draws: 384

## Data and likelihood audit
See `collocation_audit.csv`, `skill_table.csv`, `delta_logL.csv`, and `residual_summary.csv`.
The fitted error parameter is site-specific under the locked `--fit-error` formulation.

## Chain health and stationarity
See `walker_acceptance.csv`, `parameter_chain_health.csv`, `chain_health.json`, and trace plots.
- Mean acceptance fraction: 0.17846875
- Mean/max autocorrelation time: 356.7929209777713 / 508.82407114201413
- Approximate ESS: 1.0762545370790126

## Posterior, identifiability, and prior edges
See `posterior_summary.csv`, `prior_edge_occupancy.csv`, and the parameter posterior plots.

## Predictive and residual diagnostics
See prediction plots, residual plots, `skill_table.csv`, and `residual_summary.csv`.

## Site conclusion
Scientific quality is characterization only. The paired validator must classify the next direction as sampler-limited, likelihood-limited, site-specific model/data limitation, joint-calibration candidate, or inconclusive.
