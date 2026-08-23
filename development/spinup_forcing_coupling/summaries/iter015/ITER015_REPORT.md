# Iter015 aggregate and decision report

## Closeout identity

- Iteration ID: `iter015`
- Status: `completed`
- Work type: `implementation`
- Objective: `hybrid-init Iter011 configuration matrix at ABBY and JERC`
- Bounded scope: `1 preflight; 2 hybrid rebuilds; 36 64x8000 leaves; 1 analysis; 1 handoff validation; user-directed ELM-precal plot makeup`
- Overall acceptance result: `pass`
- Decision: `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`

## Integrity and provenance

All 36 immutable packages passed selection-ledger, chain, Jacobian, and plot gates after the ELM-precal makeup. Hybrid pools were rebuilt from frozen Iter012 Revision1 site ledgers under `hybrid_high_l_maximin` (q=0.90) and reused with `site_hybrid_pool_reuse_v1`. ABBY pool SHA-256 `3627bb1d…`; JERC pool SHA-256 `40ac807e…` matched Iter014. Production `23589325` analysis failed because coupled plots skipped ELM precal; makeup `23589330` restored overlap-aligned overlays and `elm_precal` skill rows before analysis `23589339`.

Sampler metrics are interpretability evidence, not integrity gates. W/R̂/ESS are reported, not a veto. Skill cannot override the Iter011 decision rule. No posterior is promoted.

The healthy/material thresholds are fixed in the approved plan: acceptance 0.20–0.50 (0.03 material), saturation ≤0.05 (0.10), steps/tau tier crossing or 20%, lag-24 0.05, sigma edge 0.20, and Wasserstein threshold crossing at 0.05. A configuration is tau-eligible only when every seed has `max_tau_change ≤ 0.20`. Seed-level signs, medians, and material directions are preserved in the paired audit CSVs.

## MCMC diagnostics

Medians across seeds `9009/9010/9011`. Width is the max cross-seed normalized Wasserstein. Tau-change is the median of per-seed `max_tau_change`; eligibility requires all three seeds ≤ 0.20.

| Site | Configuration | Acceptance | Saturation | Min steps/tau | Abs lag-24 | Sigma edge | Width | Tau-change | Tau-eligible |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ABBY | hourly/0.50 | 0.32781 | 0.43770 | 10.299 | 0.97265 | 0.0072115 | 0.34436 | 0.17540 | no (9011=0.280) |
| ABBY | hourly/0.75 | 0.22542 | 0.47953 | 9.0653 | 0.97267 | 0.0066964 | 0.00050014 | 0.25230 | no |
| ABBY | hourly/1.00 | 0.13538 | 0.52609 | 18.731 | 0.97265 | 0.0066964 | 0.46115 | 0.058635 | yes |
| ABBY | daily/0.50 | 0.26943 | 0.011975 | 10.361 | 0.97220 | 0 | 0.023529 | 0.30631 | no |
| ABBY | daily/0.75 | 0.15761 | 0.017051 | 10.853 | 0.97256 | 0 | 0.052184 | 0.27949 | no |
| ABBY | daily/1.00 | 0.059295 | 0.045998 | 10.984 | 0.97269 | 0 | 0.19631 | 0.24480 | no |
| JERC | hourly/0.50 | 0.10292 | 0 | 8.7889 | 0.91641 | 0 | 0.34522 | 0.44654 | no |
| JERC | hourly/0.75 | 0.22109 | 0 | 8.7041 | 0.91617 | 0 | 0.48541 | 0.25456 | no (9009=0.548) |
| JERC | hourly/1.00 | 0.15427 | 0 | 8.6296 | 0.91760 | 0 | 0.89615 | 0.27640 | no |
| JERC | daily/0.50 | 0.025031 | 0 | 8.9434 | 0.91868 | 0 | 0.10789 | 0.42947 | no |
| JERC | daily/0.75 | 0.014557 | 0 | 8.9698 | 0.92022 | 0 | 0.081714 | 0.44152 | no |
| JERC | daily/1.00 | 0.012262 | 0 | 8.9151 | 0.92071 | 0 | 0.11225 | 0.41238 | no |

Residual lag-24 is evaluated on hourly MAP residuals for both likelihood resolutions; it does not turn a daily target into an hourly target. Across this matrix it is essentially constant within each site (~0.973 at ABBY, ~0.917–0.921 at JERC) and does not distinguish configurations.

Saturation splits ABBY by resolution: every hourly configuration saturates (~0.44–0.53), while every daily configuration stays at or below the 0.05 healthy band. JERC saturation is ~0 for all six configurations. Acceptance at JERC daily collapses to 0.012–0.025, well below the 0.20 floor.

## Model skill

MAP skill is the selected-walker best fit against overlap-aligned SR observations. ELM skill is the overlap-aligned ensemble-mean pre-calibration curve restored by makeup; it is independent of MCMC configuration.

| Site | Configuration | MAP RMSE | MAP bias | MAP R2 | ELM RMSE | ELM bias | ELM R2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ABBY | hourly/0.50 | 4.7212 | −4.0146 | −2.2283 | 6.6896 | −6.2132 | −5.4813 |
| ABBY | hourly/0.75 | 4.6986 | −3.9839 | −2.1974 | 6.6896 | −6.2132 | −5.4813 |
| ABBY | hourly/1.00 | 4.7213 | −4.0143 | −2.2284 | 6.6896 | −6.2132 | −5.4813 |
| ABBY | daily/0.50 | 4.7319 | −4.0376 | −2.2430 | 6.6896 | −6.2132 | −5.4813 |
| ABBY | daily/0.75 | 4.7294 | −4.0350 | −2.2396 | 6.6896 | −6.2132 | −5.4813 |
| ABBY | daily/1.00 | 4.7108 | −3.9976 | −2.2141 | 6.6896 | −6.2132 | −5.4813 |
| JERC | hourly/0.50 | 0.66744 | +0.00066 | 0.38554 | 1.5752 | +1.4271 | −2.4226 |
| JERC | hourly/0.75 | 0.66658 | −0.00002 | 0.38712 | 1.5752 | +1.4271 | −2.4226 |
| JERC | hourly/1.00 | 0.66771 | −0.00015 | 0.38504 | 1.5752 | +1.4271 | −2.4226 |
| JERC | daily/0.50 | 0.67285 | −0.00965 | 0.37554 | 1.5752 | +1.4271 | −2.4226 |
| JERC | daily/0.75 | 0.67358 | −0.00859 | 0.37418 | 1.5752 | +1.4271 | −2.4226 |
| JERC | daily/1.00 | 0.67331 | −0.01786 | 0.37467 | 1.5752 | +1.4271 | −2.4226 |

Skill interpretation:

- At both sites the calibrated MAP series beats ELM precal (ABBY RMSE 4.70–4.73 vs 6.69; JERC RMSE 0.667–0.674 vs 1.575). JERC MAP R2 is positive (~0.385 hourly, ~0.375 daily) against ELM R2 −2.42.
- Within each site, MAP RMSE/R2 are nearly identical across the six configurations. Skill therefore does not rank resolution or DE-scale and cannot select a configuration.
- ABBY MAP R2 remains strongly negative (~−2.2). Calibration improves ELM but does not produce an adequate ABBY fit at `64×8000`.
- JERC hourly MAP skill is slightly better than daily, in the same direction as the sampler-acceptance contrast, but the gap is far too small to override the Iter011 rule.

## Decisions and route

- ABBY: `inconclusive_seed_instability`; eligible: `hourly_1.00`; unique non-dominated: `daily_0.50`; selected: none.
- JERC: `inconclusive_seed_instability`; eligible: none; unique non-dominated: `hourly_0.50`, `hourly_0.75`, `hourly_1.00`; selected: none.

No configuration is preferred or default-retained. No posterior promotion.

## Site-specific rationale

### ABBY

Tau-stable configurations: hourly_1.00.
Tau-unstable configurations: hourly_0.50, hourly_0.75, daily_0.50, daily_0.75, daily_1.00.
Outcome: `inconclusive_seed_instability`. The unique non-dominated configuration is not in the interpretable set.

Favorable evidence:

- daily_0.50 dominates hourly_0.50 by saturation;max_cross_seed_width_fraction.
- daily_0.50 dominates hourly_0.75 by saturation;min_steps_per_tau.
- daily_0.50 dominates hourly_1.00 by mean_acceptance;saturation;max_cross_seed_width_fraction.
- daily_0.50 dominates daily_0.75 by mean_acceptance;max_cross_seed_width_fraction.
- daily_0.50 dominates daily_1.00 by mean_acceptance;max_cross_seed_width_fraction.
- hourly_0.50 dominates hourly_1.00 by mean_acceptance.
- hourly_0.75 dominates hourly_0.50 by max_cross_seed_width_fraction.
- daily_0.75 dominates hourly_1.00 by saturation and daily_1.00 by mean_acceptance.

Adverse or limiting evidence:

- hourly_1.00, the only tau-eligible configuration, is dominated by daily_0.50 and has the worst ABBY saturation (0.526) and a below-floor acceptance (0.135).
- All three daily configurations have healthy saturation, but all three fail `max_tau_change ≤ 0.20` on every seed.
- hourly_0.75 has near-zero cross-seed width (0.00050), which is seed agreement, not mixing length: saturation remains ~0.48 and tau-change remains >0.20 on every seed.
- hourly_0.50 vs daily_0.50 worsens saturation;max_cross_seed_width_fraction.

The paired metric audit records every seed-level signed difference and median used for the all-three-seed/no-material-opposite rule.

### JERC

Tau-stable configurations: none.
Tau-unstable configurations: hourly_0.50, hourly_0.75, hourly_1.00, daily_0.50, daily_0.75, daily_1.00.
Outcome: `inconclusive_seed_instability`. Interpretability fails because no configuration is tau-eligible, so the hourly non-dominated set cannot be selected.

Favorable evidence:

- hourly_0.50 dominates daily_0.50, daily_0.75, and daily_1.00 by mean_acceptance.
- hourly_0.75 dominates daily_0.50, daily_0.75, and daily_1.00 by mean_acceptance.
- hourly_1.00 dominates daily_0.50, daily_0.75, and daily_1.00 by mean_acceptance.
- Among hourly configurations, hourly_0.75 is the only one whose median acceptance sits in the 0.20–0.50 band (0.221).

Adverse or limiting evidence:

- No hourly configuration dominates another hourly configuration. The three hourly leaves are a non-dominated set.
- Daily acceptance (0.012–0.025) is an order of magnitude below the 0.20 floor.
- Cross-seed width remains large on hourly configurations (0.345 / 0.485 / 0.896), comparable to Iter014 hybrid `hourly/0.75` (W ≈ 0.437) rather than Iter011 TIM hourly (W ≈ 0.003).
- Seed 9009 remains the weak hybrid seed on hourly/0.75 (acceptance 0.089, tau-change 0.548), repeating the Iter014 seed split (0.089 / 0.221 / 0.259).

The paired metric audit records every seed-level signed difference and median used for the all-three-seed/no-material-opposite rule.

## Equifinality evidence from Iter015 (not selected configurations)

These are scientific inputs to the planning-only Iter016 ensemble proposal. They do not authorize execution or posterior promotion.

**JERC hourly hybrid configs.** Physical-corner plots and cross-seed width (0.345 / 0.485 / 0.896) show seed-separated parameter clusters while MAP SR RMSE stays ~0.667 across seeds and configurations. That pattern is consistent with **parameter equifinality for soil decomposition**: different `(k, rf)` vectors can yield nearly identical SR because SR alone under-constrains the cascade. However, chains are not fully mixed (R-hat ~2, bulk ESS ~250, no tau-eligible configuration), so seed clusters are **candidate modes under incomplete mixing**, not a validated posterior mixture. Seed 9009 on `hourly/0.75` is unhealthy (acceptance 0.089, tau-change 0.548) and should not enter an operational ensemble without explicit exclusion rationale.

**ABBY `daily/0.50`.** Unique non-dominated under Iter011 core metrics with healthy saturation (0.012) and low width (0.024), suggesting seeds agree on one region rather than JERC-style separation. Still tau-ineligible at 8k (`max_tau_change` ≈ 0.30–0.35 on every seed). Useful as a contrast case: not every site shows multi-mode seed separation at this chain length.

**Flat MAP skill across the matrix.** At both sites, MAP RMSE/R² vary little across resolution and DE-scale. Skill therefore supports treating **SR as the operational target** and parameters as a set, not picking one configuration by predictive score alone.

## Integrated conclusion and decision

Integrity passed. The hybrid-init Iter011 matrix at `64×8000` does not yield a preferred or default-retained configuration at either site.

Decision: `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`. Selected configuration: none. No posterior promotion.

The two evidence classes do not conflict, and they also do not substitute for each other:

1. MCMC diagnostics decide the Iter011 rule. ABBY has a unique non-dominated configuration (`daily/0.50`) that is not tau-eligible, while the only tau-eligible configuration (`hourly/1.00`) is dominated. JERC has a non-dominated hourly set and no tau-eligible configuration. Both outcomes are `inconclusive_seed_instability` by the locked rule, not a metric tradeoff and not a skill ranking.
2. Model skill shows that calibrated MAP beats ELM precal at both sites, more clearly at JERC than at ABBY, but MAP scores are effectively flat across the six configurations. Skill therefore confirms that the coupled hybrid chains are doing something better than uncalibrated ELM; it does not identify a resolution or DE-scale.

Iter015 therefore answers the hybrid-init matrix question in the negative at 8k length: hybrid `hybrid_high_l_maximin` starts do not recover the Iter011 TIM ABBY `daily/0.75` preference, and they do not repair JERC seed agreement under the configuration-selection rule. The scientifically interesting remainder is not “rerun the 36-leaf matrix” or “pick one calibrated vector.” It is whether **multi-seed equifinal parameter ensembles** — one representative mode per healthy seed, SR as the operational target, explicit seed-health and equifinality gates — are the right operational product for soil-decomposition parameters under SR-only constraints. That is the planning-only Iter016 direction.

## Interpretation, limitations, and route

- Hybrid 8k chains remain seed-unstable on tau-change at both sites except ABBY hourly/1.00.
- R̂/ESS fields in the aggregate are null; W is reported and is not a veto.
- Coupled `case.output['SR']` is full-forcing length; ELM precal overlays must use overlap indices. The Iter015 makeup repaired products, not the engine. The later `baseline_output` attachment on `build_coupling_target()` is the durable contract for future campaigns.
- `/xdisk` products are temporary and unbacked.
- A lack of a supported unique non-dominated configuration is an inconclusive result rather than evidence of scientific equivalence.

## Next experiment

No follow-up execution is authorized here. The planning-only Iter016 proposal is a **multi-seed equifinal parameter ensemble** for operational SR use: retain one representative parameter set per healthy seed/mode from Iter015 discovery evidence, document SR predictive envelopes, apply seed-health and equifinality gates, and treat within-seed clustering as diagnostic only. Any such work requires a new consolidated kickoff approval.
