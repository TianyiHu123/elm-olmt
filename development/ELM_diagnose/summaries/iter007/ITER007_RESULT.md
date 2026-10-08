# Iter007 ABBY Vertical-Soil-Carbon Extended OAT Result

- Iteration ID: `iter007`
- Status: `completed`
- Work type: `implementation`
- Objective: Apply the complete Iter005/Iter006 extended OAT diagnostic to 13 ABBY vertical-soil-carbon one-parameter ensembles with explicit dynamic parameter mapping.
- Bounded scope: 13 exact ABBY vertical-soil-carbon pickles; 1,300 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated standalone ABBY vertical-soil-carbon range-conditional descriptive OAT and pathway/stoichiometry package; no PAWN/Sobol/global sensitivity, interaction, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site claim.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/results`

## Quantitative evidence

- Preflight jobs `23882414` and `23882462` failed before Python on a mistyped pinned postprocessing digest; attempt two also corrected a latent newline-sensitive parameter-file reader. After the exact final retry was explicitly authorized, preflight `23882524` completed `0:0`. Diagnostic `23882574` completed `0:0` on attempt one. Passing peak memory was 40.00/40 GB and 42.99/60 GB.
- Input manifest SHA-256: `bf459adab7ce1ed4400ba14a4b217381ecad812510c94164992d54bfe887fd49`. Output manifest SHA-256: `61a85ab5395a10865996faea1ad425229a594439e53d210941798b45688935ce`.
- The package contains 13 parameter rows, 1,300 member rows, 338 score rows, 37,180 standard response rows, one observation row, 35,100 HR-pathway rows, 390 HR-curve rows, 5,200 litter member-ratio rows, 3,188,640 litter time-series rows, 520 litter-curve rows, and exactly 44 PNGs: 3,268,682 data rows total.
- Observed SR has 26,264 valid hours (`42.83%` coverage), mean `7.501337`, and population temporal SD `2.627639` gC m-2 day-1. Model-member SR means span `0.830247`--`2.665878` with pooled mean `1.342808`; temporal SDs span `0.169364`--`0.549677` gC m-2 day-1. Observation summaries exceed the full member ranges, but observation support is not exactly time-matched and does not enter OAT scores.
- Mean potential, P-limited, and N-limited HR from the 1,300 `TOTAL` rows are `11.782900`, `3.834530`, and `2.865373` gC m-2 day-1 after dividing seven-year accumulation by 2,555 days. Relative to pooled model SR as denominator, they are `+777.48%`, `+185.56%`, and `+113.39%`; observed SR is `+458.63%`. N limitation reduces potential HR by `75.68%`. These constructed pathways are distinct from actual model `HR_TOTAL`, whose pooled mean is `0.785350` gC m-2 day-1.
- All four litter ratios retain 1,300/1,300 supported members. Flux-weighted medians remain effectively fixed at leaf C:N/C:P `70`/`1050` and fine-root C:N/C:P `42`/`1000`; machine-scale scatter is not sensitivity.
- `leaf_long` leads mean GPP and ER spread; `act25` leads mean SR, HR_TOTAL, and LITFALL. `k_s4` leads mean total litter-plus-soil C and SOIL4C. `decomp_depth_efolding` ranks 13th for the five standard flux means (`0.30%`--`0.57%`), 11th for total litter-plus-soil C (`11.74%`), and 8th--10th for the four soil pools (`8.66%`--`12.59%`) over its sampled `0.1`--`15.0` range.

### Mean HR and SR flux comparison

The model values are pooled ensemble means across 1,300 members, with equal representation from the 13 separate 100-member OAT ensembles. Potential and limited HR means divide each member's 2018--2024 accumulation by the full 2,555-day model window. Model SR is the arithmetic mean of the daily-equivalent hourly rates over the same 61,320 model timesteps. Observed SR is the arithmetic mean over its 26,264 valid, unique hourly timesteps after unit conversion; missing observation hours are not filled or extrapolated.

The percentage column uses model SR as the reference: `100 * (mean flux / model SR mean - 1)`.

| Flux | Timesteps used | Mean flux (gC m⁻² day⁻¹) | Difference from model SR |
| --- | ---: | ---: | ---: |
| Potential HR | 61,320 model hours per member | 11.782900 | +777.48% |
| P-limited HR | 61,320 model hours per member | 3.834530 | +185.56% |
| N-limited HR | 61,320 model hours per member | 2.865373 | +113.39% |
| Model SR | 61,320 model hours per member | 1.342808 | 0.00% (reference) |
| Observed SR | 26,264 valid observation hours | 7.501337 | +458.63% |

N limitation reduces the ensemble-mean potential HR by `75.68%` when potential HR is the denominator. The observation comparison is not exactly time-support matched because its valid hours cover only `42.83%` of the model window and may be seasonally or diurnally nonrepresentative.

## Descriptive interpretation

Within the declared ABBY vertical-soil-carbon OAT ranges, vegetation parameters dominate most ecosystem-flux response spreads, while decomposition rates dominate total and matched soil-pool responses. The new `decomp_depth_efolding` ensemble has comparatively small response spreads for flux summaries and modest soil-pool spreads over its sampled range. Constructed potential HR is strongly reduced by both nutrient limiters, and the model's actual HR remains a separate diagnostic.

The observed SR mean and temporal variability exceed every modeled member summary, but only 42.83% of model hours have valid observations and the supports are not time matched. This is descriptive context, not a calibrated goodness-of-fit score. All litter-ratio members are supported and retain nominal stoichiometry.

Visual review found complete ABBY-labelled panels and coherent responses. Low-valued heatmap annotations have weak contrast, and axis-offset notation magnifies machine-scale scatter around fixed litter ratios; the numerical tables remain authoritative.

These results are baseline-conditioned and range-dependent responses from separately perturbed ensembles. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site results.
