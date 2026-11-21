# Iter006 Closeout Summary

- Iteration/work type: `iter006` / `implementation`.
- Objective/result: test the frozen fixed-upstream ABBY/JERC GPP configuration on 20 balanced
  655/164 development-member splits and conditionally release only on gate pass; technical
  validation passed, but the immutable robustness gate failed.
- Decision: `optimization_required`. Preserve the comprehensive metrics and compact uncertainty
  products as diagnostic evidence. Do not fit or publish an all-819 GPP artifact, predicted-GPP SR
  handoff, stable release, or catalog entry.
- Scope: 20 newly fitted repetitions, exact Iter004 split design, 240 comprehensive metric rows,
  84 uncertainty-estimate rows, 4/5 held-out appearances per development member, zero fixed-test
  access, zero spinup execution, and zero convergence warnings.
- Interpretation: evidence is `fixed_upstream_gpp_stage`; published predicted C/N is an in-sample
  fixed upstream input, so this is not end-to-end held-out evidence.

## Immutable publication gate

All quantiles use NumPy's linear method across the 20 validation repetitions. Bias is prediction
minus ELM in `gC/m^2/day`.

| Site | Resolution | R2 q10 / floor | RMSE q90 / ceiling | Median abs bias / ceiling | Result |
| --- | --- | ---: | ---: | ---: | --- |
| ABBY | hourly | 0.708444 / 0.85 | 7.041041 / 5.0 | 0.170771 / 0.35 | fail |
| ABBY | daily | 0.193684 / 0.75 | 6.071767 / 3.0 | 0.170771 / 0.35 | fail |
| JERC | hourly | 0.755954 / 0.85 | 7.260702 / 5.0 | 0.284831 / 0.35 | fail |
| JERC | daily | 0.028777 / 0.75 | 5.939709 / 3.0 | 0.284831 / 0.35 | fail |

Bias passed all four ceilings, but R2 and RMSE failed every site/resolution gate. Coverage is 1.0
throughout. The all-or-nothing decision is therefore `optimization_required`.

## Member-balanced uncertainty estimates

Each member contributes equally after its repeated held-out occurrences are averaged. RMSE is the
candidate downstream surrogate-error standard deviation; bias remains separate.

| Site | Resolution | Bias | RMSE | Centered residual SD | Coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| ABBY | hourly | -0.335024 | 5.318698 | 5.308136 | 1.0 |
| ABBY | daily | -0.335024 | 4.191663 | 4.178253 | 1.0 |
| JERC | hourly | -0.111644 | 5.821192 | 5.820122 | 1.0 |
| JERC | daily | -0.111644 | 4.133033 | 4.131525 | 1.0 |

- Products: `metric_distribution.csv` (`0c5f13f2...a366`),
  `uncertainty_estimates.csv` (`2dcb974e...e790`), `gpp_uncertainty.nc`
  (`cd0fc5a7...92d4`), and independent `aggregate_validation.json`
  (`f95fccbf...5d07`) remain under aggregate `attempt_3` in the external run root.
- Validation: attempt 3 independently recalculated all 12 metrics for each leaf from stored truth
  and predictions, the 240-row comprehensive table, member-balanced moments, all four NetCDF
  fields, coordinates, units, definitions, provenance, hashes, and the failed gate.
- Accounting: prepare `24489883`, smoke `24489912`, all 20 leaves of array `24489937`, and final
  aggregation/validation `24491301` completed `0:0`. Aggregate attempts `24491172` and `24491252`
  failed only in progressively stricter independent numerical comparisons; their evidence and the
  user-approved bounded corrections are preserved. Two of five additional submissions were used.
- Publication boundary: no release fit, artifact, predicted-GPP handoff, stable package, catalog,
  or push occurred. Diagnostic products are not an authorized downstream SR input.
- Limitations: two sites; fixed in-sample upstream C/N; overlapping 4/5-appearance validation
  sets; temporary unbacked storage; no fixed test, all-819 GPP fit, SR, full-chain, observation,
  likelihood, or posterior evidence.
- Campaign-plan amendment recommendation: `none`; the failed frozen configuration calls for a
  separately approved optimization-planning iteration, not a campaign-goal change.
- Next state: explicit terminal declaration for Iter006. Any GPP optimization iteration requires a
  new planning discussion and consolidated kickoff approval.
