# Iter006 JERC Extended OAT Result

- Iteration ID: `iter006`
- Status: `completed`
- Work type: `implementation`
- Objective: Apply the complete Iter005 extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles with explicit site-generalized tooling.
- Bounded scope: 14 exact JERC pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated JERC range-conditional descriptive OAT and pathway/stoichiometry package under the approved explicit-gap support contract; no global sensitivity, interaction, causal, optimization, tuning, parameter-value, or cross-site claim.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter006_jerc_oat_extended/results`

## Quantitative evidence

- Preflight attempts `23856493` and `23856561` failed on a commit-SHA preamble mismatch and the original all-members litter denominator gate, respectively. After the approved material revision, preflight `23856771` completed `0:0`; diagnostic `23861155` completed `0:0`. Passing peak memory was 5.85/40 GB and 32.87/40 GB, respectively.
- Input manifest SHA-256: `b10901c14c8d5689f1a704038860f51d79d9fa3ca663bfdef510555c9f5941f0`. Output manifest SHA-256: `256cc1e1318aaa3e2a2ceaa123fdb06f2fd9e7ff224f4950caea659e4571ec31`.
- The package contains 14 parameter rows, 1,400 member rows, 364 score rows, 40,040 standard response rows, one observation row, 37,800 HR-pathway rows, 420 HR-curve rows, 5,600 litter member-ratio rows, 3,433,920 litter time-series rows, 560 litter-curve rows, and exactly 44 PNGs: 3,520,119 data rows total.
- The explicit SR observation has 51,882 valid hours, mean `1.326166`, and population temporal SD `0.851455` gC m-2 day-1. Model-member SR means span `0.000000`--`5.624627` and temporal SDs span `0.000000`--`1.540170`; both observed summaries are bracketed by the ensemble-wide ranges. Observation context does not enter any OAT score.
- Accumulated total potential HR and P-limited HR are identical across all 1,400 pairs and span `0.000`--`21,824.860` gC m-2. N-limited totals span `0.000`--`19,559.953` gC m-2.
- Each litter ratio retains 1,363 supported and 37 explicitly rejected member rows. The 148 rejected ratio rows all record `nonpositive_nutrient_total`: five members per ratio in `leaf_long` and 32 per ratio in `q10_mr`. Supported values remain effectively constant at leaf C:N `70`, leaf C:P `1050`, fine-root C:N `42`, and fine-root C:P `1000`; machine-scale numerical scatter is not sensitivity.
- `q10_mr` ranks first for mean and temporal-standard-deviation responses of GPP, ER, and SR, and for most aggregate flux targets. The matched decomposition rate leads each corresponding mean litter/soil pool; `k_s4` leads mean total litter-plus-soil C, while a few temporal-variability pool leaders differ. These rankings are conditional on the declared one-parameter ranges.

### Mean HR and SR flux comparison

The model values are pooled ensemble means across 1,400 members, with equal representation from the 14 separate 100-member OAT ensembles. Potential and limited HR means divide each member's 2018--2024 accumulation by the full 2,555-day model window. Model SR is the arithmetic mean of daily-equivalent hourly rates over the same 61,320 model timesteps. Observed SR is the arithmetic mean over its 51,882 finite, unique hourly timesteps after unit conversion; missing observation hours are not filled or extrapolated.

The percentage column uses model SR as the reference: `100 * (mean flux / model SR mean - 1)`.

| Flux | Timesteps used | Mean flux (gC m⁻² day⁻¹) | Difference from model SR |
| --- | ---: | ---: | ---: |
| Potential HR | 61,320 model hours per member | 3.961651 | +35.21% |
| P-limited HR | 61,320 model hours per member | 3.961651 | +35.21% |
| N-limited HR | 61,320 model hours per member | 3.560783 | +21.53% |
| Model SR | 61,320 model hours per member | 2.930035 | 0.00% (reference) |
| Observed SR | 51,882 valid observation hours | 1.326166 | -54.74% |

N limitation reduces the ensemble-mean potential HR by `10.12%` when potential HR is the denominator. The observation comparison is not exactly time-support matched because valid observations cover `84.61%` of the model hours and may be seasonally or diurnally nonrepresentative.

## Descriptive interpretation

Within the declared JERC ranges, `q10_mr` produces the broadest responses for most ecosystem flux summaries, including zero-response members at part of its range; `act25` and `leaf_long` also produce substantial target-dependent responses. Matched decomposition parameters dominate their corresponding mean pool responses. Potential and P-limited HR coincide, while N limitation lowers the pooled potential-HR mean by 10.12%. Observed SR is lower than the pooled model SR mean, although both its mean and temporal variability lie within the full member ranges.

The revised support contract makes low-litter-flux members visible rather than dropping them or interpreting undefined ratios as zero. Supported ratios remain effectively fixed. Visual review found complete JERC-labelled panels and coherent gap behavior. Two non-blocking presentation limitations remain: heatmap annotations have weak contrast in some cells, and Matplotlib offset notation magnifies machine-scale noise in nearly constant litter-ratio panels.

These are baseline-conditioned, range-dependent responses from separately perturbed ensembles. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal, optimization, tuning, parameter-value, or cross-site results.
