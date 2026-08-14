# Iter011 aggregate and decision report

## Closeout identity

- Iteration ID: `iter011`
- Status: `completed`
- Work type: `implementation`
- Objective: `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`
- Bounded scope: `ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains`
- Overall acceptance result: `pass`
- Decision: `ABBY preferred_configuration_supported daily_0.75; JERC inconclusive_metric_tradeoff with no selected configuration`

## Integrity and provenance

All 36 immutable raw/HDF packages, checkpoint contracts, bundle identities, parameter/transform contracts, daily maps, MAP target re-evaluations, and required leaf diagnostics passed.

## Six-configuration quantitative evidence

| Site | Configuration | Acceptance | Saturation | Min steps/tau | Abs lag-24 | Sigma edge | Max Wasserstein |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ABBY | hourly/0.50 | 0.37132 | 0.53854 | 17.137 | 0.97219 | 0.004375 | 0.00060915 |
| ABBY | hourly/0.75 | 0.23258 | 0.54788 | 21.056 | 0.97219 | 0.0082721 | 0.00042785 |
| ABBY | hourly/1.00 | 0.14707 | 0.5505 | 21.086 | 0.97219 | 0.0050781 | 0.00071333 |
| ABBY | daily/0.50 | 0.37531 | 0.014338 | 24.806 | 0.97221 | 0 | 0.0056516 |
| ABBY | daily/0.75 | 0.23671 | 0.013359 | 33.095 | 0.97219 | 0 | 0.0022312 |
| ABBY | daily/1.00 | 0.14837 | 0.017184 | 39.87 | 0.97219 | 0 | 0.0021688 |
| JERC | hourly/0.50 | 0.50219 | 0 | 49.798 | 0.91806 | 0 | 0.0027055 |
| JERC | hourly/0.75 | 0.34897 | 0 | 63.01 | 0.9181 | 0 | 0.0041012 |
| JERC | hourly/1.00 | 0.24942 | 0 | 58.127 | 0.91823 | 0 | 0.0026027 |
| JERC | daily/0.50 | 0.083754 | 0 | 8.3675 | 0.91958 | 0 | 0.039003 |
| JERC | daily/0.75 | 0.041654 | 0 | 7.9278 | 0.91864 | 0 | 0.065198 |
| JERC | daily/1.00 | 0.027184 | 0 | 8.3216 | 0.91815 | 0 | 0.056201 |

The healthy/material thresholds are fixed in the approved plan: acceptance 0.20–0.50 (0.03 material), saturation ≤0.05 (0.10), steps/tau tier crossing or 20%, lag-24 0.05, sigma edge 0.20, and Wasserstein threshold crossing at 0.05. Seed-level signs, medians, and material directions are preserved in the paired audit CSVs.

## Decisions and route

- ABBY: `preferred_configuration_supported`; eligible configurations: daily_0.50, daily_0.75, daily_1.00, hourly_0.50, hourly_0.75, hourly_1.00; non-dominated: daily_0.75; selected: daily_0.75.
- JERC: `inconclusive_metric_tradeoff`; eligible configurations: hourly_0.50, hourly_0.75, hourly_1.00; non-dominated: hourly_0.75, hourly_1.00; selected: none.

## Site-specific rationale

### ABBY

Tau-stable configurations: daily_0.50, daily_0.75, daily_1.00, hourly_0.50, hourly_0.75, hourly_1.00.
Tau-unstable configurations: none.
Outcome: `preferred_configuration_supported`. A supported configuration is evidence for a future site-specific production proposal only; no production run is authorized.

Favorable evidence:
- hourly_0.75 dominates hourly_0.50 by min_steps_per_tau.
- hourly_0.75 dominates hourly_1.00 by mean_acceptance.
- daily_0.50 dominates hourly_0.50 by saturation;min_steps_per_tau.
- daily_0.50 dominates hourly_0.75 by saturation;min_steps_per_tau.
- daily_0.50 dominates hourly_1.00 by mean_acceptance;saturation.
- daily_0.75 dominates hourly_0.50 by saturation;min_steps_per_tau.

Adverse or limiting evidence:
- hourly_0.50 vs hourly_0.75 worsens min_steps_per_tau.
- hourly_0.50 vs hourly_1.00 worsens min_steps_per_tau.
- hourly_0.50 vs daily_0.50 worsens saturation;min_steps_per_tau.
- hourly_0.50 vs daily_0.75 worsens saturation;min_steps_per_tau.
- hourly_0.50 vs daily_1.00 worsens saturation;min_steps_per_tau.
- hourly_0.75 vs daily_0.50 worsens saturation;min_steps_per_tau.

The paired metric audit records every seed-level signed difference and median used for the all-three-seed/no-material-opposite rule.

### JERC

Tau-stable configurations: hourly_0.50, hourly_0.75, hourly_1.00.
Tau-unstable configurations: daily_0.50, daily_0.75, daily_1.00.
Outcome: `inconclusive_metric_tradeoff`. Retain the default only as the current bounded-pilot conclusion; any next diagnostic or production proposal requires fresh approval.

Favorable evidence:
- hourly_0.50 dominates daily_0.50 by mean_acceptance;min_steps_per_tau.
- hourly_0.50 dominates daily_0.75 by mean_acceptance;min_steps_per_tau;max_cross_seed_width_fraction.
- hourly_0.50 dominates daily_1.00 by mean_acceptance;min_steps_per_tau;max_cross_seed_width_fraction.
- hourly_0.75 dominates hourly_0.50 by min_steps_per_tau.
- hourly_0.75 dominates daily_0.50 by mean_acceptance;min_steps_per_tau.
- hourly_0.75 dominates daily_0.75 by mean_acceptance;min_steps_per_tau;max_cross_seed_width_fraction.

Adverse or limiting evidence:
- hourly_0.50 vs hourly_0.75 worsens min_steps_per_tau.
- hourly_0.50 vs hourly_1.00 worsens min_steps_per_tau.
- daily_0.50 vs hourly_0.50 worsens mean_acceptance;min_steps_per_tau.
- daily_0.50 vs hourly_0.75 worsens mean_acceptance;min_steps_per_tau.
- daily_0.50 vs hourly_1.00 worsens mean_acceptance;min_steps_per_tau.
- daily_0.75 vs hourly_0.50 worsens mean_acceptance;min_steps_per_tau;max_cross_seed_width_fraction.

The paired metric audit records every seed-level signed difference and median used for the all-three-seed/no-material-opposite rule.


## Interpretation, limitations, and route

Sampler metrics are interpretability evidence, not iteration-integrity gates. A lack of a supported unique non-dominated configuration is an inconclusive result rather than evidence of scientific equivalence. Residual lag-24 is evaluated on hourly predictions for both likelihood resolutions; it does not turn the daily target into an hourly target.

## Next experiment

No follow-up execution is authorized here. Any production or narrower diagnostic proposal requires a new consolidated kickoff approval.
