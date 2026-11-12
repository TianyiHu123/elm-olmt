# Iter008 Closeout Summary

- Iteration/work type: `iter008` / `implementation`.
- Objective/result: characterize Iter007 candidate 21 on 20 fresh development-only splits,
  publish descriptive GPP uncertainty, fit all 819 development members, and release the artifact
  plus downstream predicted-GPP handoff; `pass`.
- Decision: `gpp_release_published`. Stable catalog-last release `gpp_abby_jerc/release_0001`
  contains artifact `67214897...8ec9`, handoff `c905fc60...98bb`, and validated release manifest
  `57cc18b0...70d1`.
- Scope: 20 synchronized seed-20261102 balanced 655/164 splits; 815 members appear four times and
  four appear five times; exact candidate-21 `(64,32)` tanh model; 819-member release fit; zero
  fixed-test access and zero convergence warnings.
- Interpretation: evidence is `fixed_upstream_gpp_stage`; published predicted C/N is fixed
  in-sample upstream input. Robustness metrics are sampled-split descriptive evidence and no
  performance gate was applied.

## Descriptive robustness evidence

Quantiles use NumPy's linear method across 20 validation repetitions. Bias is prediction minus ELM
in `gC/m^2/day`.

| Site / resolution | R2 q10 | RMSE q90 | Median absolute bias |
| --- | ---: | ---: | ---: |
| ABBY hourly | 0.908730 | 3.813338 | 0.141745 |
| ABBY daily | 0.873134 | 2.372245 | 0.141745 |
| JERC hourly | 0.909111 | 4.437556 | 0.132374 |
| JERC daily | 0.811444 | 2.582691 | 0.132374 |

- Products: 240-row `metric_distribution.csv`, 84-row `uncertainty_estimates.csv`, compact
  `gpp_uncertainty.nc`, all-819 `gpp_surrogate_artifact.pkl`, and 100,442,160-value
  `gpp_predicted_for_sr.nc` passed independent technical validation.
- Publication validation: all 13 release-manifest files match their size and SHA-256; validated,
  staging, and stable trees are identical; catalog `ad488095...2665` points to release manifest
  `57cc18b0...70d1`; `performance_gate_applied=false`; fixed-test access is false.
- Correction evidence: initial final job `24523438` exposed a raw-interface replay mismatch.
  Diagnostic attempt `24523514` proved handoff versus stored predictions exact and localized the
  defect to scaler-stat dtype order. The reviewed correction reproduces scikit-learn's float32
  cast-before-arithmetic path; corrected final job `24523529` passed without changing the model,
  artifact, handoff, science, or gate.
- Accounting: preflight `24512852`, all 20 robustness leaves under `24513943`, release fit
  `24520151`, diagnostic retry `24523514`, and corrected final `24523529` completed `0:0`.
  Failed final `24523438` and failed diagnostic `24523491` are preserved and classified. Two of
  three additionally approved retry units were consumed; one remained unused.
- Limitations: two sites; fixed in-sample upstream C/N; all-819 release predictions are in-sample;
  robustness distributions describe the approved repeated splits rather than global or causal
  sensitivity; `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; SR fitting,
  full-chain uncertainty, likelihood/MCMC, or later release requires separate planning and kickoff
  approval.
