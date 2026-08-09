# Iter008 MCMC diagnostic report

## Reproducible setup
- Sites: JERC
- Variables: SR
- Walkers x steps: 64 x 4000
- Seed: 8008
- Discard/thin: 2414; 242
- Eligible draws: 448; predictive draws: 448

## Data and likelihood audit
See `collocation_audit.csv`, `skill_table.csv`, `delta_logL.csv`, and `residual_summary.csv`.
The fitted error parameter is site-specific under the locked `--fit-error` formulation.

## Chain health and stationarity
See `walker_acceptance.csv`, `parameter_chain_health.csv`, `chain_health.json`, and trace plots.
- Mean acceptance fraction: 0.10165625
- Mean/max autocorrelation time: 353.82287020534903 / 482.6513952341954
- Approximate ESS: 1.2661702725434145

## Posterior, identifiability, and prior edges
See `posterior_summary.csv`, `prior_edge_occupancy.csv`, and the parameter posterior plots.

## Predictive and residual diagnostics
See prediction plots, residual plots, `skill_table.csv`, and `residual_summary.csv`.

## Site conclusion
Scientific quality is characterization only. The paired validator must classify the next direction as sampler-limited, likelihood-limited, site-specific model/data limitation, joint-calibration candidate, or inconclusive.
