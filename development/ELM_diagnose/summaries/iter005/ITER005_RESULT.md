# Iter005 ABBY Extended OAT Result

- Iteration ID: `iter005`
- Status: `completed`
- Work type: `implementation`
- Objective: Extend the reusable ABBY OAT diagnostic with explicit targets, SR observation context, decomposition pathways, and litter-flux stoichiometry.
- Bounded scope: 14 exact historical pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated range-conditional descriptive OAT and pathway/stoichiometry package; no global sensitivity, interaction, causal, optimization, tuning, or parameter-value claim.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter005_abby_oat_extended/results`

## Quantitative evidence

- Preflight attempt three `23834413` completed `0:0` after two authorized, classified fixture-expectation corrections; diagnostic attempt one `23834468` completed `0:0`. Passing peak memory was 31.90/40 GB and 32.85/40 GB, respectively.
- Input manifest SHA-256: `7581cafa262c112e3881ecf30ef4c0f0425058e195b02de8b37002832a5592cc`. Output manifest SHA-256: `99d3f377f9242d85eac3c29d94ec88fc66a8b415a07d31cf6a8491306267e339`.
- The package contains 14 parameter rows, 1,400 member rows, 364 score rows, 40,040 standard response rows, one observation row, 37,800 HR-pathway rows, 420 HR-curve rows, 5,600 litter member-ratio rows, 3,433,920 litter time-series rows, 560 litter-curve rows, and exactly 44 PNGs. The four core standard tables reproduce Iter004 byte-for-byte.
- The explicit SR observation has 26,264 valid hours, mean `7.501337`, and population temporal SD `2.627639` gC m-2 day-1. Model-member SR means span `0.622847`--`3.076300` and temporal SDs span `0.134623`--`0.586511`; the observations are not bracketed by these OAT ensembles.
- Accumulated total potential HR spans `1,912.427`--`13,685.020` gC m-2; N-limited totals span `1,710.962`--`11,512.151` gC m-2. P-limited and potential totals are exactly equal for every parameter/member pair.
- Hourly litter-ratio support is 100 members everywhere. Flux-weighted values are constant across the declared cases: leaf C:N `70`, leaf C:P `1050`, fine-root C:N `42`, and fine-root C:P `1000`.

### Mean HR and SR flux comparison

The model values are pooled ensemble means across 1,400 members, with equal representation from the 14 separate 100-member OAT ensembles. Potential and limited HR means divide each member's 2018--2024 accumulation by the full 2,555-day model window. Model SR is the arithmetic mean of the daily-equivalent hourly rates over the same 61,320 model timesteps. Observed SR is the arithmetic mean over its 26,264 valid, unique hourly timesteps after unit conversion; missing observation hours are not filled or extrapolated.

The percentage column uses model SR as the reference: `100 * (mean flux / model SR mean - 1)`.

| Flux | Timesteps used | Mean flux (gC m⁻² day⁻¹) | Difference from model SR |
| --- | ---: | ---: | ---: |
| Potential HR | 61,320 model hours per member | 2.130507 | +48.70% |
| P-limited HR | 61,320 model hours per member | 2.130507 | +48.70% |
| N-limited HR | 61,320 model hours per member | 1.827990 | +27.58% |
| Model SR | 61,320 model hours per member | 1.432799 | 0.00% (reference) |
| Observed SR | 26,264 valid observation hours | 7.501337 | +423.54% |

N limitation reduces the ensemble-mean potential HR by `14.20%` when potential HR is the denominator. The observation comparison is not exactly time-support matched because its valid hours cover only `42.83%` of the model window and may be seasonally or diurnally nonrepresentative.

## Descriptive interpretation

The observation comparison exposes a large ABBY SR level and variability mismatch without changing any OAT score. The accumulated-pathway atlas shows strong range-conditional responses for `act25` and `leaf_long`, lower N-limited totals, and coincident potential/P-limited totals. The litter-ratio outputs verify complete support but show fixed stoichiometry rather than a response across these parameter sweeps. Standard target rankings are unchanged from Iter004 by the byte-identical regression gate.

These are baseline-conditioned, range-dependent responses from separately perturbed ensembles. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal, optimization, tuning, or parameter-value results.
