# ELM Diagnostic Iteration Summary

## Iter001 — failed input-interface preflight

- Objective: nine-site seed-resolved optimized `SR` diagnostic against `ppe6` control ensembles and coupling observations.
- Evidence: Puma preflight `23718019` failed `1:0` after 28 seconds; its receipt found `ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl` missing `case.output['SR']`.
- Resources: 2.41 GB/20 GB and 7.925 CPU seconds; this was not a resource failure.
- Gate result: `fail`; no substantive diagnostic, figures, metrics, or scientific conclusion.
- Decision: close failed; require a fresh package with compatible optimized historical outputs or authorized output generation.

## Iter002 — completed nine-site SR diagnostic

- Objective: the recovered nine-site, seed-resolved optimized `SR` diagnostic against the same `ppe6` control ensembles and coupling observations.
- Input gate: preflight `23723017` passed for all 60 updated `ctrlopt` pickles, nine controls, and nine SR observations using the locked receipt.
- Execution: first substantive attempt `23723072` failed only at the ABBY boxplot due to a Matplotlib `labels` API incompatibility. After user-directed minimal revision and independent re-review, retry `23723308` completed `0:0` in 2:51 (22.94/30 GB).
- Outputs: 45 PNGs (hourly, complete-day daily, monthly, UTC diurnal, and hourly distribution for every site), plus 69 hourly descriptive metric rows (60 seed-level optimized and nine control means) in the external results directory.
- Decision: accepted as a descriptive diagnostic package; no cross-site ranking, score threshold, or scientific selection conclusion was made.

## Iter003 — completed generalized SR diagnostic

- Objective: direct-YAML generalized carbon-flux diagnostics for nine-site SR.
- Recovery: first job timed out; retry one was user-cancelled for efficiency revision; vectorized retry two `23729042` completed `0:0` in 02:29 using 21.6 GB/30 GB.
- Outputs: 45 variable-named figures, 69 series metrics, 960 member metrics, receipt, and manifest at `.../elm_diagnose_iter003/results_retry2`.
- Decision: accepted descriptive package only; no ranking or scientific conclusion. Monitoring-wrapper and agent-continuity limitations are retained in the Iter003 report for separate workflow improvement.

## Iter004 — completed ABBY OAT response diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Rank ABBY range-wide OAT responses for 13 carbon targets across 14 separately perturbed parameters.
- Bounded scope: 14 exact historical pickles; 1,400 members; 2018-2024 hourly means and population standard deviations; descriptive OAT only.
- Locked method: baseline-conditioned one-at-a-time response spread, `100 * (P95 - P05) / abs(median)`, ranked separately for member means and population temporal standard deviations; no PAWN, Sobol, joint/global sensitivity, interaction, causal, tuning, or parameter-value claim.
- Execution: preflight `23830156` and diagnostic `23830259` both completed `0:0` on attempt one; no retry was consumed. Preflight validated all 14 cases, 1,400 members, exact common 61,320-hour axes, variables, metadata, and calculation fixture.
- Outputs: 14 parameter rows, 1,400 member rows, 364 finite score rows, 40,040 curve rows, and 35 PNGs in `.../elm_diagnose_iter004_abby_oat/results`; output manifest SHA-256 `9d4308d04b68e49a816ebb23e6162703165a3dca9d810e4cc958f714ea86eca2`.
- Quantitative result: `leaf_long` leads GPP and ER for both statistics and mean SR/HR_TOTAL/LITFALL; `act25` leads temporal variability for SR/HR_TOTAL/LITFALL. Matched decomposition rates lead corresponding litter/soil mean-pool responses, except total litter-plus-soil C is led by `k_s4`. Full 26-group leaders and all 364 ranks are recorded in `summaries/iter004/` and the external score table.
- Overall acceptance result: `pass`.
- Decision: Accepted range-conditional descriptive OAT package; no global sensitivity, interaction, causal, tuning, or parameter-value claim.

## Iter005 — completed ABBY extended OAT pathway and stoichiometry diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Extend the reusable ABBY OAT diagnostic with explicit targets, SR observation context, decomposition pathways, and litter-flux stoichiometry.
- Bounded scope: 14 exact historical pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Execution: preflight `23834413` passed on authorized attempt three after two classified fixture-expectation corrections; diagnostic `23834468` passed on attempt one. All four jobs are terminally accounted, and passing peak memory was 31.90/40 GB and 32.85/40 GB.
- Outputs: 3,520,119 data rows and 44 PNGs in `.../elm_diagnose_iter005_abby_oat_extended/results`; input manifest `7581cafa`; output manifest `99d3f377`; Iter004 core table hashes reproduce exactly.
- Quantitative result: observed SR mean/std are `7.501337`/`2.627639` versus model-member ranges `0.622847`--`3.076300`/`0.134623`--`0.586511` gC m-2 day-1. Potential and P-limited accumulated total HR are identical across all 1,400 pairs and span `1,912.427`--`13,685.020` gC m-2; N-limited totals span `1,710.962`--`11,512.151`. All litter-ratio hours have 100-member support, with fixed flux-weighted leaf C:N/C:P `70`/`1050` and fine-root C:N/C:P `42`/`1000`.
- Overall acceptance result: `pass`.
- Decision: Accepted validated range-conditional descriptive OAT and pathway/stoichiometry package; no global sensitivity, interaction, causal, optimization, tuning, or parameter-value claim.

## Iter006 — completed JERC extended OAT pathway and stoichiometry diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Apply the complete Iter005 extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles with explicit site-generalized tooling.
- Bounded scope: 14 exact JERC pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Execution: after two classified preflight failures and an approved explicit-gap revision, preflight `23856771` and diagnostic `23861155` completed `0:0`. All four jobs are terminally accounted; passing peak memory was 5.85/40 GB and 32.87/40 GB.
- Outputs: 3,520,119 data rows and 44 PNGs in `.../elm_diagnose_iter006_jerc_oat_extended/results`; input manifest `b10901c1`; output manifest `256cc1e1`; all artifact and support-reconciliation gates pass.
- Quantitative result: potential/P-limited, N-limited, model SR, and observed SR means are `3.961651`, `3.560783`, `2.930035`, and `1.326166` gC m-2 day-1. Relative to model SR, these differ by `+35.21%`, `+21.53%`, and `-54.74%`; N limitation reduces potential HR by `10.12%`. Observations cover 51,882 hours (`84.61%`). Each litter ratio retains 1,363 supported and 37 explicitly rejected members.
- Overall acceptance result: `pass`.
- Decision: Accepted validated JERC range-conditional descriptive OAT and pathway/stoichiometry package under the explicit-gap support contract; no global sensitivity, interaction, causal, optimization, tuning, parameter-value, or cross-site claim.

## Iter007 — completed ABBY vertical-soil-carbon extended OAT diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Apply the complete Iter005/Iter006 extended OAT diagnostic to 13 ABBY vertical-soil-carbon one-parameter ensembles with explicit dynamic parameter mapping.
- Bounded scope: 13 exact ABBY vertical-soil-carbon pickles; 1,300 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Execution: preflight `23882524` completed `0:0` after two classified pre-Python failures and explicitly authorized corrections; diagnostic `23882574` completed `0:0` on attempt one. All jobs are terminally accounted; passing peak memory was 40.00/40 GB and 42.99/60 GB.
- Outputs: 3,268,682 data rows and 44 PNGs in `.../elm_diagnose_iter007_abby_ctrlvertc_oat_extended/results`; input manifest `bf459ada`; output manifest `61a85ab5`; all artifact, publication, and review gates pass.
- Quantitative result: potential, P-limited, N-limited, model SR, and observed SR means are `11.782900`, `3.834530`, `2.865373`, `1.342808`, and `7.501337` gC m-2 day-1. Relative to model SR, the first three and observed SR differ by `+777.48%`, `+185.56%`, `+113.39%`, and `+458.63%`; N limitation reduces potential HR by `75.68%`. Observations cover 26,264 hours (`42.83%`). All four litter ratios retain 1,300 supported members and no rejected members.
- Range-conditional result: `leaf_long` leads mean GPP/ER; `act25` leads mean SR/HR_TOTAL/LITFALL; `k_s4` leads mean total litter-plus-soil C and SOIL4C. `decomp_depth_efolding` has small flux-summary spreads and ranks 8th--11th for aggregated soil-C summaries over its sampled range.
- Overall acceptance result: `pass`.
- Decision: Accepted validated standalone ABBY vertical-soil-carbon range-conditional descriptive OAT and pathway/stoichiometry package; no PAWN/Sobol/global sensitivity, interaction, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site claim.

## Iter008 — completed ABBY vertical-soil-carbon C:N nutrient-stress OAT diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Characterize how separate perturbations of `cn_s1`--`cn_s4` affect realized decomposition, microbial N/P demand satisfaction, plant N/P demand satisfaction, ecosystem carbon fluxes, and mineral nutrient cycling in the ABBY vertical-soil-carbon configuration.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 27 direct raw metrics; four accumulated satisfaction ratios; 58 response endpoints; 27,555 CSV rows; 11 figures; descriptive OAT only.
- Execution: preflight `24015245` and diagnostic `24015300` completed `0:0` on attempt one; no scheduler/resource retry was consumed. The published package contains exactly 27,555 CSV data rows, 11 PNGs, and 1,600/1,600 supported ratios.
- Quantitative result: low-to-high sampled C:N changes microbial N satisfaction by `+2.3%`, `+25.4%`, `+108.4%`, and `+118.6%` and microbial P satisfaction by `+22.2%`, `+33.7%`, `+96.1%`, and `+95.7%` for `cn_s1`--`cn_s4`. Plant satisfaction changes only about `+0.6%`, `-3.6%`, `+1.4%`, and `+4.3%`; direct HR changes `+1.0%`, `-5.4%`, `-0.7%`, and `+4.6%`.
- Overall acceptance result: `pass`.
- Decision: Accepted the validated baseline-conditioned ABBY C:N OAT package. Higher pool C:N primarily reduces microbial nutrient demand and improves microbial satisfaction, strongest for pools 3/4, but does not broadly relieve plant demand or guarantee higher realized decomposition.

## Iter009 — completed ABBY vertical-soil-carbon C:N pool-context diagnostic

- Work type: `implementation`; status: `completed`.
- Objective: Amend the Iter008 N/P-stress diagnostic by separating mean and temporal-variability figures, restoring observed SR context, and adding pool-C and realized pool-HR-per-C responses.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 47 metrics; 74 response endpoints per parameter; 37,812 CSV rows; 17 figures; baseline-conditioned descriptive OAT only.
- Execution: preflight `24019322` and diagnostic `24019366` completed `0:0` on attempt one in `00:01:12` and `00:01:17`; each used about 19.72/60 GB peak memory. No retry or cancellation was used.
- Outputs: exactly 4 parameter rows, 47 metric definitions, 400 member rows, 32,560 response rows, 4,800 supported-ratio rows, one observation row, 37,812 CSV data rows, and 17 PNGs in `.../elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context/results`; output manifest `afa885d5`.
- Quantitative result: lowest-to-highest sampled-parameter-bin SOIL pool C, matched HR, and realized HR/C change by `+53.01%`/`-0.53%`/`-34.99%` for `cn_s1`, `-3.90%`/`-4.76%`/`-0.89%` for `cn_s2`, `-0.47%`/`-0.66%`/`-0.18%` for `cn_s3`, and `+3.56%`/`+4.64%`/`+1.04%` for `cn_s4`. ABBY observed SR coverage is 26,264/61,320 hours (`42.83%`), with mean/std `7.501337`/`2.627639` gC m-2 day-1.
- Overall acceptance result: `pass`.
- Decision: Accepted the validated amendment. Pool stocks and realized respiration per pool C can respond differently to the separate C:N perturbations; the evidence remains conditional on the declared baseline-conditioned OAT ranges and supports no causal, global-sensitivity, prescribed-rate, threshold, or cross-site claim.
