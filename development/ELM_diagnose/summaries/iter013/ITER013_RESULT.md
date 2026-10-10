# Iter013 ABBY Observation and Spinup-Ratio OAT Result

- Status: `completed`; overall acceptance: `pass`.
- Scope: 27 separate ABBY vertical-soil-carbon OAT ensembles, 100 members each, preserving the Iter012 transient/pathway design while adding contextual `GPP_DT` and `GPP_NT`, final-spinup eight-pool C:N and C:P ratios, and contextual observed soil C, N, and C:N.
- Interpretation: baseline-conditioned and sampled-range descriptive OAT only. Observations are independent contextual references and never enter scores, ranks, acceptance, calibration, or tuning. The observed 0--2 m soil profile and model all-stored-element CWD+litter+soil totals have an accepted boundary mismatch.
- Inputs: exactly 27 transient pickles, configs, parameter files, and restart cases with 2,700 final restart files. Model coverage is the full 61,320-hour 2018--2024 no-leap window; final spinup states are `0201-01-01` restarts.
- Outputs: exactly 109,113 primary CSV data rows and 13 PNGs. Passing input manifest `808ec4f0870f13f6c947a65e9d466c3bb80cd036708bbb32648075bbd3863225`; output manifest `99d84254e00f8bb0f49312ff99413a4b87b4249d0eadedb3b3dad53a7878539d`.
- Execution: preflight jobs `24192660` and `24204148` and diagnostic job `24204180` completed `0:0`; preparations 1 and 3 were deliberately unsubmitted. Passing diagnostic generation, artifact validation, and atomic publication completed with a `6413020K` process peak and no swaps.

## Observation context

- Observed SR mean is `7.501337 gC m-2 day-1` over 26,264 valid hours (`42.83%` of the model-window denominator).
- Daytime-partitioning GPP mean is `4.338426 gC m-2 day-1` over 15,771 valid hours (`25.72%`); finite zero values are retained.
- Nighttime-partitioning GPP mean is `6.809636 gC m-2 day-1` over 11,404 valid hours (`18.60%`); 4,367 post-calendar negative values are rejected.
- Every observation mean uses its own valid support after calendar/unit conversion. Model means remain full-window rather than collocated. The two GPP products are plotted in distinct colors with one figure-level legend.
- ABBY soil references are C `32303.953054 gC m-2`, N `2317.321905 gN m-2`, and C:N `13.940210 gC gN-1`. They appear only on the matching spinup response atlases, with the boundary warning. There is no P or C:P observation.

## Range-conditional response results

Transient leaders are unchanged from Iter012: `rf_s2s3` leads SR (73.4%), HR (77.4%), and LITFALL (77.3%); `leaf_long` leads GPP (68.4%); and `k_s4` leads transient decomposer C (3359.5%).

Final-spinup leaders by response-spread score are:

| Endpoint | First | Second | Third |
| --- | --- | --- | --- |
| decomposer C | `k_s4` 1778.9% | `k_s3` 360.8% | `rf_s2s3` 156.9% |
| decomposer N | `k_s4` 2010.6% | `k_s3` 389.3% | `k_s2` 105.7% |
| decomposer P | `k_s4` 1944.6% | `k_s3` 382.2% | `k_s2` 175.9% |
| C:N ratio | `rf_s2s3` 166.2% | `k_s4` 76.8% | `cn_s4` 50.9% |
| C:P ratio | `k_s4` 51.7% | `cn_s4` 48.7% | `rf_s2s3` 39.7% |

All 2,700 memberwise C:N and C:P ratios have finite positive denominators, and all 135 final-spinup endpoint scores are supported. The score remains `100 * (P95-P05) / abs(ensemble median)` and compares response spreads across different declared ranges; it is neither a derivative nor probability-weighted importance.

## Pathways, validation, and limitations

- The constructed pathways remain distinct from direct model `HR`. Across 2,700 cases, mean N-limited/potential and P-limited/potential ratios are `0.305316` and `0.401703`; P exceeds N in 2,693 cases, preserving the seven low-range `rf_s2s3` exceptions.
- The compute-node validator passed exact identities, formulas, restart samples, support, tables, row counts, figures, and atomic publication. Independent final review reproduced the numerical/artifact gates and inspected all 13 figures.
- Primary visual review found all 13 figures populated, legible, and unclipped. The transient heatmap contains five endpoints; the spinup heatmap contains C, N, P, C:N, and C:P and no observation values. Context lines, legends, units, native markers, ranks, and boundary warnings are visible where required.
- `/xdisk` is temporary and unbacked. Observation support is partial and independent, and the soil reference is not boundary matched. These results support no PAWN/Sobol/global-sensitivity, interaction, causal nutrient-limitation, threshold, optimization, tuning, parameter recommendation, or cross-site/configuration claim.
