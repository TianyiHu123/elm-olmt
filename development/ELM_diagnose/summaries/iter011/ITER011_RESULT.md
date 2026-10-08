# Iter011 ABBY OAT Transient and Spinup Result

- Status: `completed`; overall acceptance: `pass`.
- Scope: 21 separate ABBY vertical-soil-carbon OAT ensembles, 100 members each. Results are baseline-conditioned and range-dependent; they are not global sensitivity, interaction, causal, tuning, or parameter-recommendation evidence.
- Inputs: exactly 21 transient pickles, 21 configs, 21 parameter files, and 21 restart cases with 2,100 final restart files. Transient coverage is 61,320 hourly samples/member for 2018--2024 noleap; spinup states are the final `0201-01-01` restarts.
- Outputs: exactly 80,200 primary CSV data rows and 11 PNGs. Input manifest `7f528763...`; output manifest `0e13dfa6168c0df852f0f19aa5a2c7db8549e43e17345a579014ffb5224e577a`.
- Execution: initial preflight `24101686` failed only because the fixture lacked the repository-root import bootstrap; the authorized correction passed as preflight `24102996`. Generation completed in diagnostic job `24103048`, whose first artifact-validation pass failed only because of an overbroad blank-field assertion. With fresh user authority, validator-only job `24103109` corrected that assertion, passed `COMPLETED 0:0`, and atomically published the unchanged staging package. All four jobs are terminally accounted.

## Methods and support

- Transient endpoints are arithmetic temporal means of direct model `SR`, direct model `HR`, direct model `GPP`, direct model `LITFALL`, and the sum of `CWDC`, `LITR1C`--`LITR3C`, and `SOIL1C`--`SOIL4C`. Flux units are `gC m-2 day-1`; the transient decomposer stock is `gC m-2`.
- Final spinup C/N/P states sum every stored vertical element of the exact eight lowercase `_vr` decomposer pools. Units are `gC m-2`, `gN m-2`, and `gP m-2`.
- The descriptive screening score is `100 * (P95 - P05) / abs(ensemble median)`, ranked separately within each endpoint across the 21 declared parameter ranges. All 105 transient and 63 spinup scores are supported.
- Observed SR is contextual only: mean `7.501337 gC m-2 day-1` over 26,264 valid hours (`42.83%` of the model window). It is shown as a reference line and never enters scores or ranks.

## Range-conditional results

Transient leaders by response-spread score are:

| Endpoint | First | Second | Third |
| --- | --- | --- | --- |
| SR mean | `act25` 65.3% | `leaf_long` 56.5% | `leafcn` 22.2% |
| HR mean | `act25` 74.5% | `leaf_long` 66.6% | `frootcn` 38.5% |
| GPP mean | `leaf_long` 68.4% | `act25` 65.1% | `leafcn` 32.9% |
| LITFALL mean | `act25` 74.5% | `leaf_long` 63.4% | `frootcn` 38.9% |
| transient decomposer C | `k_s4` 3359.5% | `k_s3` 600.4% | `k_s2` 142.0% |

Final-spinup C, N, and P share the same three leading parameters: `k_s4` (`1778.9%`, `2010.6%`, `1944.6%`), `k_s3` (`360.8%`, `389.3%`, `382.2%`), and `k_s2` (`132.9%`, `105.7%`, `175.9%`). `act25` ranks fourth for all three and `leaf_long` fifth.

Lowest-to-highest parameter-bin contrasts show direction and nonlinearity, not derivatives. Higher `k_s4` corresponds to approximately `-99.7%` transient decomposer C and `-98.8%` to `-99.3%` final spinup C/N/P; `k_s3` and `k_s2` show the same declining-stock direction with smaller spreads. Higher `act25` and `leaf_long` correspond to higher flux means and decomposer stocks, whereas higher `leafcn` corresponds to lower SR, HR, GPP, LITFALL, and transient decomposer C over its sampled range. Several rate and allocation responses are strongly curved, so their heatmap scores should not be read as constant slopes.

## Idealized decomposition pathways

The accumulated pathways are constructed diagnostics and are distinct from direct model `HR`. Across all 2,100 parameter-member combinations, neither limited total exceeds potential, and P-limited totals exceed N-limited totals. Mean member-level limited/potential ratios are `0.293590` for N and `0.388401` for P, with sampled ranges `0.014214`--`0.680442` and `0.019006`--`0.755961`, respectively. These comparisons describe the declared idealized pathway formulas and do not establish whole-ecosystem nutrient limitation.

## Validation and limitations

- Independent reviewer `/root/iter011_review` reproduced representative transient and spinup scores, ten-bin summaries, pathway component-to-total sums, limiter ordering, exact row/figure counts, and support/rank coverage. Visual review passed all 11 figures, including the 21-panel layouts, native markers, observed SR reference, heatmap annotations, and pathway legend.
- Heatmap colors are dominated by the very large `k_s4` stock scores, but numeric score/rank annotations remain legible.
- `/xdisk` is temporary and unbacked. Observation support is partial and contextual. Separate OAT ranges are not directly comparable as probability distributions and do not measure interactions or global variance contributions.
