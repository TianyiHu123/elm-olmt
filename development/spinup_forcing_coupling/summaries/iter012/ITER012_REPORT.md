# Iter012 — General-pipeline fixed production MCMC

Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`

## Outcome

Package v2 demonstrated the reusable `initialize_pipeline.py` → `optimize_surrogate_forcing.py`
workflow with transactional artifacts, locked provenance, local Slurm logs, and separate canonical
and legacy evidence. The implementation and integrity gates passed. The fixed-length scientific
decision is inconclusive at both sites, so no posterior is promoted and no chain is rerun.

## Comparison setup

Canonical Iter012 is compared with two controls that share the same observations, forcing/spinup
artifacts, physical bounds, and `de_mixture` scale `0.75`:

- **Iter011 baseline:** the matched site configuration from the likelihood-resolution / DE-scale
  pilot. ABBY control is `daily/0.75`; JERC control is `hourly/0.75`. Both used 64 walkers ×
  8,000 steps and seeds `9009/9010/9011`. Iter011 ABBY was
  `preferred_configuration_supported`; Iter011 JERC was `inconclusive_metric_tradeoff` with no
  unique selected configuration, but `hourly/0.75` was the user-selected Iter012 production
  setting.
- **ELM precal:** the ensemble-mean ELM prediction on the same NEON SR mask. This is a model
  baseline, not an MCMC baseline.

Iter012 used a new Sobol + L-BFGS-B frozen 640-member pool and 64 walkers × 32,000 steps. Skill
uses the same valid-observation counts (ABBY 26,264 daily points; JERC 51,882 hourly points).
Iter011 skill is the mean of the three per-seed `optimized_best` (MAP) tables. Iter012 skill is
the canonical pooled evaluation. Cross-seed Iter011 width fraction and Iter012 normalized
Wasserstein are related disagreement screens, not identical statistics.

## Evidence

- Preflight attempts `23574254` and `23574301` exhausted the approved 10 GB allocation and ended
  `OUT_OF_MEMORY 0:125`. The approved Revision1 preflight `23574395` used 4 CPUs/20 GB, completed
  `0:0`, and emitted `PREFLIGHT_PASS`.
- Generic initialization ABBY `23574453` and JERC `23574454`, pool validation `23574678`, all six
  production leaves `23574706`–`23574711`, all four evaluations `23575950`–`23575953`, and
  aggregate `23575960` completed `0:0`.
- Handoff validator `23575977` completed `0:0` with
  `ITER012_HANDOFF_VALIDATE_PASS abby=fixed_length_inconclusive jerc=fixed_length_inconclusive`.
- Package v1 is retained only as `legacy_misconfigured_sampler` comparison evidence.

## ABBY diagnostics versus Iter011 `daily/0.75`

| Metric | Iter011 baseline | Iter012 | Change |
| --- | ---: | ---: | --- |
| Walkers × steps | 64 × 8,000 | 64 × 32,000 | 4× longer |
| Mean acceptance (9009 / 9010 / 9011) | 0.236 / 0.238 / 0.237 | 0.239 / 0.232 / 0.238 | ~unchanged |
| Mean acceptance (all seeds) | 0.237 | 0.236 | −0.001 |
| Transformed saturation | 0.0134 | 0.0225 | worse (+0.009) |
| Min post-burn steps / τ | 33.1 | 28.7 | worse (−4.4) |
| τ stability (max across seeds) | 0.086 | 0.134 | worse (+0.048) |
| `sigma_SR` upper-edge occupancy | ~0 | 0.999 | worse (bound pile-up) |
| Cross-seed disagreement | width 0.0022 | Wasserstein 0.0044 | still small |
| Rank-normalized split R̂ max | not reported at site table | 1.018 | within common 1.01–1.05 band |
| Bulk ESS min | ~24 (approx, seed 9009) | 6,519 | more samples, different ESS |
| Label | preferred `daily/0.75` | `fixed_length_inconclusive` | not promoted |

### Metric-by-metric interpretation (ABBY)

- **Acceptance (~unchanged, still healthy).** Values remain in the 0.20–0.50 DE-mixture band.
  The 0.75 scale still matches local posterior curvature under the daily likelihood. The new
  pool and 4× length did not retune the proposal, so this metric was not expected to jump.
- **Saturation (worse).** More transformed samples sit at logit/probit walls. Hypothesis: the
  longer run and more diverse pool let walkers spend more time on the same prior-edge ridges
  already visible in Iter011 (`rf_*` and `sigma_SR`), rather than discovering a new interior
  mode.
- **Min steps / τ (worse despite a longer chain).** Maximum τ grew to ~893 versus ~234 in the
  Iter011 seed-9009 health file. Length increased 4×, but the slowest integrated timescale
  grew by more than 4×, so the steps/τ ratio fell. Hypothesis: 32,000 steps are long enough
  to resolve a slower edge-sticking or error-inflation mode that an 8,000-step window
  truncated.
- **τ stability (worse, still modest).** Seed-to-seed τ estimates drifted more. Hypothesis:
  different seeds occupy the `sigma_SR` ceiling and a few `rf_*` edges at slightly different
  rates; the extra length makes that disagreement visible without breaking seed overlap.
- **`sigma_SR` edge occupancy (much worse).** Iter011 MAP was already 3.674 against the 3.679
  bound, but few samples were counted at the edge. Iter012 occupancy is 0.999. Hypothesis:
  both campaigns found the same error-inflation ridge; the longer pooled-init run collapsed
  almost the entire posterior onto that ceiling instead of leaving a thin near-bound tail.
- **Cross-seed disagreement (still good).** Width/Wasserstein remain far below a 0.05 material
  split. Hypothesis: ABBY’s daily target has one dominant (poor) compromise. Seeds agree on
  that compromise even when they sit on bounds.
- **Split R̂ and ESS.** R̂ max 1.018 does not show the multi-basin split seen at JERC. Bulk
  ESS is larger than Iter011’s short-run approximation because there are 4× more draws, not
  because the target became easier.

**ABBY diagnostic hypothesis.** Iter012 did not repair ABBY mixing; it more fully occupied the
same daily-likelihood geometry Iter011 already preferred. The daily complete-day SR target
appears dominated by a large negative bias that `sigma_SR` absorbs. Extra steps and a fresh
pool therefore increase bound occupancy and estimated τ without moving the chain into a
better-mixed interior.

## ABBY skill versus Iter011 MAP and ELM precal

| Series | RMSE | Bias | R² | KGE |
| --- | ---: | ---: | ---: | ---: |
| ELM precal | 6.690 | −6.213 | −5.481 | −0.271 |
| Iter011 MAP (`optimized_best`, mean of 3 seeds) | 4.733 | −4.039 | −2.245 | −0.106 |
| Iter012 MAP (pooled evaluation) | 4.702 | −3.988 | −2.203 | −0.131 |
| Iter012 posterior median | 4.710 | −3.998 | −2.214 | −0.131 |
| Δ MAP (Iter012 − Iter011) | −0.031 | +0.051 | +0.042 | −0.025 |

Fitted `sigma_SR` is 3.67–3.68 in both MCMC campaigns, against the prior upper bound 3.679.

- **Versus ELM precal (better point skill, still unusable).** MCMC reduces RMSE from 6.69 to
  ~4.70 and lifts R² from −5.48 to about −2.20. The sign of the bias is unchanged (large
  negative). Hypothesis: shared parameters can reduce the magnitude of the daily underprediction
  but cannot remove a structural offset in the coupled daily SR mapping.
- **Versus Iter011 MAP (essentially unchanged).** RMSE and R² improve only slightly; KGE is
  slightly worse. Hypothesis: both campaigns sit on the same `sigma_SR` ceiling, so the
  likelihood is saturated. Longer sampling and a new initializer cannot improve a fit that is
  already using the maximum allowed observation-error inflation.
- **MAP versus posterior median (almost identical).** Seed agreement is high, so the pooled
  median and MAP describe the same poor compromise.

## JERC diagnostics versus Iter011 `hourly/0.75`

| Metric | Iter011 baseline | Iter012 | Change |
| --- | ---: | ---: | --- |
| Walkers × steps | 64 × 8,000 | 64 × 32,000 | 4× longer |
| Mean acceptance (9009 / 9010 / 9011) | 0.361 / 0.349 / 0.344 | 0.182 / 0.221 / 0.157 | worse |
| Mean acceptance (all seeds) | 0.349 | 0.187 | worse (−0.162) |
| Transformed saturation | 0.000 | 0.0415 | worse (+0.042) |
| Min post-burn steps / τ | 63.0 | 3.46 | much worse (−59.5) |
| τ stability (max across seeds) | 0.103 | 2.342 | much worse (unstable) |
| `sigma_SR` upper-edge occupancy | 0 | 0 | unchanged (interior) |
| Cross-seed disagreement | width 0.0041 | Wasserstein 0.548 | much worse |
| Rank-normalized split R̂ max | not reported at site table | 2.224 | not converged |
| Bulk ESS min | ~65 (approx, seed 9009) | 241 | still tiny vs 15-D |
| Label | eligible, not uniquely selected | `fixed_length_inconclusive` | worse mixing |

### Metric-by-metric interpretation (JERC)

- **Acceptance (worse, below the 0.20 healthy floor on two of three seeds).** Iter011 hourly/0.75
  accepted ~35% of proposals; Iter012 accepts ~19%. Hypothesis: the Sobol + L-BFGS-B pool
  starts walkers across a wider set of basins than the Iter011 TIM geometry, so a fixed 0.75
  DE scale is too large for at least some occupied regions. An alternative is that the 32,000-step
  run entered a tighter ridge where the same scale overshoots.
- **Saturation (worse, still under 0.05).** Iter011 had no transformed-wall occupancy; Iter012
  has 4.1%. Hypothesis: a subset of walkers from the diverse pool reached prior/transform
  edges (`k_l1` occupancy 0.971, `rf_l3s3` 0.940, `k_l3` 0.736) that the shorter TIM control
  did not occupy.
- **Min steps / τ (much worse).** τ max is ~3,784 versus ~130 in the Iter011 seed-9009 health
  file. After burn-in the chain is only a few autocorrelation times long. Hypothesis: walkers
  are switching slowly between, or stuck inside, distinct modes. A 4× longer budget is still
  short relative to that new timescale.
- **τ stability (much worse).** Seed 9011 stability 2.34 means the τ estimate is not internally
  consistent. Hypothesis: that seed has not settled on one mixing regime; apparent τ changes
  as more of a second basin is sampled.
- **`sigma_SR` edge (unchanged, good).** Both campaigns keep the error parameter interior
  (~0.67 versus bound 1.26). Hypothesis: hourly JERC mismatch is not being absorbed only by
  blowing up σ, unlike ABBY. The JERC failure is in parameter/multimodality space, not error
  saturation.
- **Cross-seed Wasserstein and split R̂ (much worse).** Wasserstein 0.548 and R̂ 2.22 mean the
  three seeds are not samples from one posterior. Hypothesis: the 640-member pool seeded
  different local modes, and 32,000 steps were not enough for DE-mixture to merge them. Iter011
  TIM starts were already closer together, so its 8,000-step seeds agreed even though that
  campaign also declined to select a unique JERC configuration.

**JERC diagnostic hypothesis.** The dominant change is initialization geometry, not likelihood
form. Iter011 `hourly/0.75` started from a locally consistent TIM neighborhood and looked
well-mixed on an 8,000-step window. Iter012 deliberately re-initialized from a space-filling
pool. That is the correct production-pipeline test, and it shows that JERC’s hourly posterior
is multi-modal or weakly identified: a good local MAP still exists, but independent seeds do
not converge to the same basin.

## JERC skill versus Iter011 MAP and ELM precal

| Series | RMSE | Bias | R² | KGE |
| --- | ---: | ---: | ---: | ---: |
| ELM precal | 1.575 | +1.427 | −2.423 | −0.156 |
| Iter011 MAP (`optimized_best`, mean of 3 seeds) | 0.668 | +0.002 | 0.384 | 0.455 |
| Iter012 MAP (pooled evaluation) | 0.665 | −0.002 | 0.390 | 0.456 |
| Iter012 posterior median | 0.679 | −0.113 | 0.364 | 0.480 |
| Δ MAP (Iter012 − Iter011) | −0.003 | −0.004 | +0.006 | +0.001 |

Fitted `sigma_SR` remains interior (~0.67) in both MCMC campaigns.

- **Versus ELM precal (much better point skill).** MAP RMSE falls from 1.575 to 0.665 and R²
  rises from −2.42 to +0.39. Hypothesis: hourly JERC SR is informative enough that a single
  best parameter vector can correct a large ELM-precal overprediction. This improvement is a
  point-estimate result, not evidence of a converged posterior.
- **Versus Iter011 MAP (unchanged).** The three Iter012 per-seed `optimized_best` RMSEs
  (0.667 / 0.667 / 0.665) match the Iter011 seed mean (0.668). Hypothesis: every seed can
  still find essentially the same local MAP. The new pool and extra length did not discover a
  better optimum; they failed to agree on the posterior around that optimum.
- **MAP versus posterior median (median worse).** Pooled median RMSE 0.679 and bias −0.113 are
  worse than MAP. Hypothesis: averaging disagreeing seeds mixes incompatible basins, so the
  median predictive series is not the series of any one good mode.

## Cross-site synthesis

ABBY and JERC fail for different reasons.

- ABBY is **stable but saturated**. Diagnostics stay close to the Iter011 daily/0.75 control,
  seeds agree, and skill barely moves. The daily target plus a bound-hitting `sigma_SR` look
  like a structural/error-model problem. More MCMC is unlikely to help until the daily
  likelihood or bias is changed.
- JERC is **locally skillful but not identified**. MAP skill matches the Iter011 hourly/0.75
  control and beats ELM precal, but the production-style pool init exposes multi-seed
  nonconvergence. More steps at the same DE scale are unlikely to merge basins; a topology,
  scale, or identifiability experiment is the relevant follow-up.

Neither site yields a promotable posterior. Package v1 stretch-move chains are not used in
these comparisons.

## Limitations and next state

Large empirical-range warning streams were localized correctly but should be deduplicated in a
future pipeline maintenance change. `/xdisk` remains temporary and unbacked. Iter011
cross-seed width fraction and Iter012 Wasserstein should not be subtracted as if they were
the same statistic. Iter011 approximate ESS and Iter012 rank-normalized ESS are also not
interchangeable.

No next iteration is proposed. This workflow is intentionally stopped because both canonical
fixed-length outcomes are inconclusive and JERC exhibits severe cross-seed nonconvergence. Any
ABBY continuation or JERC topology/likelihood investigation requires a fresh planning package and
explicit user approval.
