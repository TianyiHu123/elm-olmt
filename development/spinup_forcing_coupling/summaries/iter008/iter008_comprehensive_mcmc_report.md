# Iter008 comprehensive ABBY and JERC MCMC report

## Executive conclusion

Iter008 is **integrity-valid but not a converged or scientifically valid calibration**.
Both 64-walker, 4,000-step single-site runs are reproducible, complete, finite, in bounds,
and supported by raw-chain checksums. However, neither posterior can be treated as
converged: acceptance is low, the runs contain only about 8–31 estimated autocorrelation
times, the archived post-selection ESS proxy is only about 1–3 per parameter, and the raw
log-probability traces finish in separated walker bands. A conventional raw-chain ESS cannot
be certified because tau is not stable and the walkers are not sampling one stationary
ensemble.

The best-fit behavior differs sharply by site:

- **ABBY:** optimization improves substantially over the ELM-precal baseline, but absolute
  skill remains poor (RMSE 4.84, bias -4.16, R2 -2.39, KGE -0.13). The fitted error scale
  is at its prior ceiling and residual lag-1 correlation is 0.999. This is not an adequate
  SR calibration.
- **JERC:** optimization produces a materially better point fit (RMSE 0.668, bias 0.002,
  R2 0.384, KGE 0.450) than ELM-precal. Nevertheless, lag-1 residual correlation is 0.994
  and the posterior chain is not mixed, so the point fit does not validate the posterior.

The selected diagnostic route remains **sampler-limited**. This does not mean the
likelihood or model is adequate. It means sampler failure is the common, first-order
bottleneck at both sites and must be resolved before posterior comparisons can reliably
separate likelihood limitation from ABBY-specific model/data limitation. Likelihood
misspecification is already strongly indicated and should be the next scientific test once
sampler geometry is improved.

## 1. Scope, evidence, and interpretation

### 1.1 Locked experiment

| Item | ABBY | JERC |
| --- | --- | --- |
| Coupled path | `drop21_corr080`, SR, `--fit-error` | same |
| Sampler | 64 walkers x 4,000 steps | same |
| Seed | 8008 | 8008 |
| Free dimensions | 14 model parameters + `sigma_SR` | same |
| Collocated period | 2019-01-01 to 2021-12-31 | 2018-01-01 to 2023-12-31 |
| Collocated / valid skill rows | 26,280 / 26,264 | 52,560 / 51,882 |
| Raw chain shape | `(4000, 64, 15)` | `(4000, 64, 15)` |
| Raw-chain SHA-256 | `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87` | `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080` |

The chain shape, seed, source/artifact provenance, checksums, finite values, parameter
schema, and prior bounds passed the Iter008 integrity validator. Those are hard technical
gates. Skill, convergence, posterior shape, residual behavior, and fitted error behavior are
scientific diagnostic evidence, not Iter008 hard gates.

### 1.2 Status vocabulary

- **Good:** the metric supports the intended interpretation.
- **Bad:** the metric directly contradicts a usable calibration or converged posterior.
- **Mixed:** relative improvement exists, but the absolute result remains inadequate.
- **Not established:** the available chain is too weak to support the claimed inference.

The practical reference values are inherited from the Iter007 diagnostic framework:
acceptance commonly around 0.2–0.5; stable autocorrelation estimates with at least 50
autocorrelation times, preferably 100; effective sample size of at least a few hundred per
parameter, with `10 x n_dim = 150` only a minimal floor; overlapping walker traces; an
interior fitted error scale; and approximately uncorrelated standardized residuals.

## 2. Best-fit SR skill

The `optimized_best` row is a best available chain point, not a stable posterior estimate.
Because neither chain converged, it is useful for testing whether a high-likelihood point can
improve predictions, but it must not be interpreted as a robust parameter estimate.

### 2.1 ABBY

| Metric | Optimized best | ELM-precal | Status | Evidence and reason |
| --- | ---: | ---: | --- | --- |
| RMSE | 4.839 | 6.690 | **Mixed** | Error falls 27.7%, so optimization helps relative to baseline; 4.84 remains large and is paired with poor R2/KGE. |
| Bias | -4.161 | -6.213 | **Bad** | Bias magnitude falls 33.0%, but the optimized series still systematically underpredicts SR by 4.16. |
| R2 | -2.392 | -5.481 | **Bad** | Improvement is real, but negative R2 means the fit is worse than predicting the observed mean. |
| KGE | -0.125 | -0.271 | **Bad** | Improvement is real, but negative KGE indicates poor combined correlation, variability, and bias behavior. |
| Delta log likelihood | +182,462.9 | reference | **Good relative / insufficient absolute** | The optimized point is strongly preferred to ELM-precal under the current likelihood, but that likelihood is contradicted by residual autocorrelation and saturated `sigma_SR`. |

ABBY therefore supports only the narrow claim that parameter optimization can improve the
locked baseline. It does **not** support the hypothesis that the current coupled model and
IID-error likelihood can reproduce observed ABBY SR adequately.

### 2.2 JERC

| Metric | Optimized best | ELM-precal | Status | Evidence and reason |
| --- | ---: | ---: | --- | --- |
| RMSE | 0.668 | 1.575 | **Good** | Error falls 57.6%; the optimized RMSE is also consistent with the fitted error scale near 0.67. |
| Bias | +0.0019 | +1.427 | **Good** | Mean bias is effectively removed. |
| R2 | +0.384 | -2.423 | **Good but moderate** | Optimization changes an unusable baseline into positive explanatory skill, although substantial variance remains unexplained. |
| KGE | +0.450 | -0.156 | **Good but moderate** | The optimized series has useful combined skill but is not close to a high-skill value of 1. |
| Delta log likelihood | +28,644,482.8 | reference | **Good relative / insufficient posterior evidence** | The optimized point is overwhelmingly preferred under the current likelihood, but the chain producing it is not converged and the residuals are highly autocorrelated. |

JERC supports the hypothesis that the locked coupled surrogate contains a useful
site-specific SR solution. It does **not** establish uncertainty, parameter identifiability,
or posterior validity.

### 2.3 Cross-site skill interpretation

The two sites are not consistent in absolute skill: JERC reaches useful positive R2/KGE and
near-zero bias, while ABBY remains negatively biased with negative R2/KGE. They are
consistent in showing a large improvement over ELM-precal under separate calibration. This
contrasts with Iter007's shared-parameter result, where JERC was sacrificed. Separate-site
optimization therefore removes the immediate joint compromise, but it exposes an ABBY-
specific limitation and does not solve chain mixing.

Primary evidence: [ABBY skill](iter008_abby_skill_table.csv),
[JERC skill](iter008_jerc_skill_table.csv), [ABBY likelihood change](iter008_abby_delta_logL.csv),
[JERC likelihood change](iter008_jerc_delta_logL.csv), and
[ABBY](iter008_abby_collocation_audit.csv) and
[JERC](iter008_jerc_collocation_audit.csv) collocation audits.

## 3. MCMC optimization diagnostics

### 3.1 Summary against the Iter007 criteria

| Diagnostic | ABBY | Status | JERC | Status |
| --- | ---: | --- | ---: | --- |
| Mean acceptance | 0.178 | **Bad** | 0.102 | **Bad** |
| Walker acceptance range | 0.025–0.252 | **Bad** | 0.0068–0.180 | **Bad** |
| Walkers below 0.10 | 20/64 | **Bad** | 31/64 | **Bad** |
| Walkers in 0.20–0.50 target | 44/64 | **Mixed** | 0/64 | **Bad** |
| Mean / max tau | 356.8 / 508.8 | **Bad** | 353.8 / 482.7 | **Bad** |
| Parameter steps per tau | 7.86–30.66 | **Bad** | 8.29–20.65 | **Bad** |
| Archived post-selection ESS proxy | 0.75–2.94 | **Bad / conservative proxy** | 0.93–2.31 | **Bad / conservative proxy** |
| Raw post-burn nominal ESS | 183–714 | **Not established** | 210–524 | **Not established** |
| Adaptive discard / thin | 2545 / 255 | **Mechanically valid** | 2414 / 242 | **Mechanically valid** |
| Retained draws | 384 (6/walker) | **Bad** | 448 (7/walker) | **Bad** |
| In-bounds and finite | all selected draws | **Good** | all selected draws | **Good** |
| First-half vs second-half means | generally small deltas | **Not established** | generally small deltas | **Not established** |
| Terminal log-probability overlap | separated bands | **Bad** | separated bands | **Bad** |
| Fitted `sigma_SR` | 3.673 MAP / 3.679 upper bound | **Bad** | 0.668 MAP / 1.259 upper bound | **Good** |
| Residual lag-1 correlation | 0.99899 | **Bad** | 0.99395 | **Bad** |

The adaptive discard/thin calculation behaves as implemented, but it cannot manufacture
independent information. It leaves only six or seven draws per walker because the estimated
tau is so large. The archived `ess_approx` applies the unthinned tau to this already thinned
flat sample count, so its 1–3 values are a conservative post-selection proxy, not a
conventional MCMC ESS. Using `nwalkers x post-burn unthinned steps / tau` gives nominal raw
ESS ranges of 183–714 for ABBY and 210–524 for JERC. Those values must also be labeled
**not established**, rather than good: each chain is shorter than 50 tau, tau has not been
shown stable, and terminal walkers occupy separated log-probability bands. No defensible ESS
claim can be made until those prerequisites pass.

Several standard raw-chain diagnostics are unavailable and therefore cannot support
convergence. Iter008 has one ensemble run per site with one seed, so rank-normalized split
R-hat across independent runs was not computed. Bulk ESS, tail ESS, and Monte Carlo standard
error were not reported. The first-half/second-half statistic pools walkers after adaptive
thinning and is not a substitute for split-chain rank diagnostics. These omissions are not
integrity failures under the approved contract, but they are scientific limitations that the
next experiment should correct.

### 3.2 ABBY raw-chain evidence

1. **Acceptance — bad.** Mean acceptance is 0.178. Five walkers are below 0.05 and 20 are
   below 0.10. Although 44 walkers reach 0.20–0.50, the low-acceptance subgroup indicates
   heterogeneous and partly stuck walkers.
2. **Autocorrelation and run length — bad.** Parameter tau ranges from 130.4 for
   `sigma_SR` to 508.8 for `k_l3`. The 4,000-step run therefore spans only 7.86 tau for
   `k_l3`, 8.23 for `k_l2`, and 8.70 for `k_l1`; even the best case spans only 30.66 tau.
   This is well below the 50-tau minimum used to trust a tau estimate.
3. **Effective sample size — not established.** Adaptive selection leaves 384 draws and the
   archived post-selection proxy ranges from 0.75 (`k_l3`) to 2.94 (`sigma_SR`). The
   conventional raw post-burn formula gives a nominal 183–714, but neither quantity is a
   valid convergence claim because tau is unstable and walkers remain separated.
4. **Raw log-probability trace — bad.** The first 100 steps have mean log probability
   -130,355 with an extreme minimum of -48.9 million; the final 100 improve to -83,515.
   Improvement is expected during burn-in, but terminal walkers remain split: 44 finish
   above -83,000, 15 between -90,000 and -83,000, and 5 at or below -90,000. This is direct
   raw-chain evidence that walkers have not reached one overlapping stationary ensemble.
5. **Stationarity check — not established.** Selected first-half/second-half mean deltas are
   numerically small for many parameters. With only six retained points per walker and
   separated log-probability bands, that agreement is not independent evidence of
   convergence.
6. **Posterior geometry — bad / weakly identified.** `k_l1` has MAP 0.201 near its 0.2
   lower bound but mean 0.781; `rf_l2s2` spans approximately 0.100–0.900; `rf_s2s3` has
   median 0.890 near its 0.9 upper bound; and `rf_s3s4` has median 0.102 near its 0.1 lower
   bound. These MAP/mean and percentile patterns indicate ridges, modes, or prior-edge
   concentration. The recorded zero edge-occupancy values do not overturn this conclusion:
   the thresholded metric misses near-edge and multimodal mass in the small selected sample.
7. **Error scale and residuals — bad.** `sigma_SR` MAP is 3.6728 against an upper bound of
   3.6786; its 97.5th percentile is 3.6784. Residual mean is -4.1609, standard deviation
   2.4709, and lag-1 correlation 0.99899. The error model is saturating while leaving strong
   bias and temporal structure.

**ABBY convergence verdict:** not converged. **ABBY validity verdict:** technically
integrity-valid, but not statistically or scientifically valid as a posterior calibration.

### 3.3 JERC raw-chain evidence

1. **Acceptance — bad.** Mean acceptance is 0.102. Twenty-five walkers are below 0.05,
   31 are below 0.10, and no walker reaches 0.20. This is a stronger stuck-walker signal
   than ABBY despite JERC's better point skill.
2. **Autocorrelation and run length — bad.** Parameter tau ranges from 193.7 for
   `sigma_SR` to 482.7 for `rf_s1s2`. The chain spans only 8.29 tau for `rf_s1s2`, 8.58
   for `k_l3`, and at most 20.65 tau for `sigma_SR`.
3. **Effective sample size — not established.** Adaptive selection leaves 448 draws and the
   archived post-selection proxy ranges from 0.93 (`rf_s1s2`) to 2.31 (`sigma_SR`). The
   conventional raw post-burn formula gives a nominal 210–524, but tau instability and
   non-overlapping walkers prevent treating that as valid effective information.
4. **Raw log-probability trace — bad.** The first 100 steps have mean log probability
   -81,516 with a minimum of -43.6 million; the final 100 improve to -52,966. At the final
   step, 33 walkers are above -52,800, 30 lie between -54,000 and -52,800, and one is below
   -54,000. The persistent two-band split is incompatible with a well-mixed ensemble.
5. **Stationarity check — not established.** Small selected-half mean differences cannot
   establish stationarity when only seven points per walker remain and terminal walkers
   occupy separate log-probability bands.
6. **Posterior geometry — bad / weakly identified.** `k_l2` MAP 0.01003 is at its 0.01
   lower bound; `k_s4` MAP 0.0001997 is at its 0.0002 upper bound; `k_s3` 97.5th percentile
   is 0.002998 against a 0.003 upper bound; and `rf_s1s2` extends to 0.8978 against a 0.9
   upper bound. As at ABBY, the zero thresholded edge-occupancy count is not sufficient to
   establish an interior, unimodal posterior.
7. **Error scale — good; residual independence — bad.** `sigma_SR` MAP is 0.6678 against
   an upper bound of 1.2586, so it is comfortably interior. Residual mean is only 0.0019 and
   standard deviation is 0.6684, but lag-1 correlation is 0.99395. The mean/scale fit is good
   while the IID temporal-error assumption is not.

**JERC convergence verdict:** not converged. **JERC validity verdict:** technically
integrity-valid, with a useful best-fit prediction, but not statistically valid as a posterior
calibration.

Primary chain evidence: [ABBY chain health](iter008_abby_chain_health.json),
[JERC chain health](iter008_jerc_chain_health.json),
[ABBY parameter diagnostics](iter008_abby_parameter_chain_health.csv),
[JERC parameter diagnostics](iter008_jerc_parameter_chain_health.csv),
[ABBY posterior](iter008_abby_posterior_summary.csv),
[JERC posterior](iter008_jerc_posterior_summary.csv),
[ABBY walker acceptance](iter008_abby_walker_acceptance.csv), and
[JERC walker acceptance](iter008_jerc_walker_acceptance.csv).
The all-walker raw log-probability counts were derived directly from
`diagnostics/log_prob_trace.txt` in the external ABBY and JERC campaign directories under
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/`.

## 4. Diagnostic-route evaluation

Iter008 required exactly one primary route. The route is interpreted as the next limiting
bottleneck, not as a claim that every other failure mode is absent.

| Route | Evidence supporting it | Evidence against it or reason not selected | Evaluation |
| --- | --- | --- | --- |
| **Sampler-limited** | Both independent site chains have low acceptance, tau about 130–509, fewer than 31 tau, archived ESS proxies around 1–3, unvalidated raw nominal ESS, stuck walkers, and separated terminal log-probability bands. JERC has good point skill and interior sigma but still has poor mixing, showing sampler failure is not merely a symptom of ABBY fit failure. | None of the posterior summaries can be stabilized without improving sampling. | **Selected primary route.** It is common to both sites, directly observed at raw-chain level, and logically precedes posterior scientific interpretation. |
| Likelihood-limited | Residual lag-1 correlations are 0.999 and 0.994; ABBY `sigma_SR` saturates its prior; hourly residuals are not IID Gaussian. | JERC's sigma is interior and its point skill is useful, while both sites share sampler failure. Changing the likelihood before establishing basic sampler mixing would confound whether posterior changes reflect better statistics or merely different geometry. | **Strong secondary hypothesis, not the primary route.** Test immediately after or jointly with a controlled sampler-geometry experiment. |
| Site-specific model/data limitation | ABBY remains strongly biased with negative R2/KGE while JERC fits well, indicating an ABBY-specific structural, observation, collocation, or surrogate limitation. | The ABBY posterior is not converged and its likelihood is saturated, so structural inadequacy cannot yet be separated from optimization and error-model failure. This route does not explain JERC's poor chain health. | **Plausible for ABBY, not yet proven.** Requires targeted ABBY residual and structural tests. |
| Joint-calibration candidate | Separate calibration improves both sites relative to ELM-precal, so a staged joint model may eventually be useful. | The site posteriors are not converged, parameter summaries differ, and Iter007 showed a shared fit could improve ABBY while degrading JERC. There is no reliable posterior-overlap evidence yet. | **Declined for now.** Do not resume a shared-parameter joint chain until single-site convergence and compatibility are demonstrated. |
| Inconclusive | Multiple limitations coexist and the current posterior is weak. | Raw-chain evidence consistently identifies sampler behavior as an immediate common failure. The remaining uncertainty concerns the secondary scientific cause, not whether sampling is adequate. | **Not selected.** The exact ultimate model remedy is unresolved, but the first bottleneck is not. |

### Why sampler-limited is the correct primary choice

The route follows three observations. First, sampler failure appears at both sites even though
their best-fit scientific outcomes differ sharply. Second, isolated runs removed the Iter007
shared-site compromise but did not remove low acceptance, high tau, low ESS, or separated
walker bands. Third, all claims about posterior boundaries, site compatibility, and uncertainty
depend on representative posterior draws; the current runs do not provide them. Therefore,
sampler improvement is the necessary first diagnostic intervention. The residual and ABBY
skill evidence simultaneously requires that likelihood and site-specific tests remain in the
next experiment sequence.

## 5. Hypothesis assessment

Iter008 hypothesized that isolated, longer, same-seed raw-chain runs would distinguish
sampler, likelihood, and site-specific limitations before another joint calibration.

| Hypothesis component | Result | Reason |
| --- | --- | --- |
| Isolation will expose whether Iter007's joint compromise caused poor fit | **Supported** | JERC changes from severe degradation in the joint run to useful positive skill in its single-site run; ABBY also improves over baseline. |
| A longer chain will produce a usable posterior | **Declined at 4,000 steps** | The longer trace reveals tau of roughly 130–509 and only 8–31 tau of run length; it does not converge. |
| Raw-chain diagnostics can identify the immediate bottleneck | **Supported** | Acceptance, per-parameter tau/ESS, walker-level acceptance, and separated terminal log-probability bands consistently identify sampler limitation. |
| Likelihood behavior is adequate once sites are separated | **Declined** | Residual lag-1 correlation remains above 0.99 at both sites; ABBY sigma saturates its prior. |
| Both sites support the same scientific model-quality conclusion | **Declined** | JERC has useful best-fit skill; ABBY remains scientifically poor. |
| The two sites are ready for another shared-parameter joint calibration | **Declined for now** | Single-site posteriors are not converged, and reliable posterior-overlap evidence is absent. |

## 6. Recommended next experiments

These are recommended tests, not execution authorization. Each experiment should preserve
the locked data, surrogate artifacts, parameter bounds, and site windows unless that item is
the explicit variable under test. Use multiple seeds for every inferential comparison; the
single shared seed in Iter008 proves reproducibility of setup, not robustness across initial
ensembles.

### Experiment 1 — sampler-geometry pilot at each site

**Purpose:** determine whether poor mixing is caused by parameter scaling, bounded geometry,
initial walker placement, or the default stretch proposal rather than simply insufficient
steps.

**Design:** keep the current IID likelihood and scientific inputs fixed. Compare the Iter008
sampler against a transformed parameterization (log for positive rate parameters and logit
for bounded fractions), dispersed high-likelihood initialization, and a documented move
mixture or tuned stretch scale. Run at least three independent seeds per site with enough
steps to estimate tau; retain unthinned raw chains. Evaluate walker-level acceptance,
rank/split trace overlap, tau stability, ESS, terminal log-probability bands, and boundary
occupancy. Do not select a configuration by best log likelihood alone.

**Expected result if the sampler-limited hypothesis is correct:** acceptance moves toward
0.2–0.5, no substantial walker group remains below 0.10, terminal log-probability bands
merge, tau falls or stabilizes, and independent seeds give overlapping marginals.

**Proves / declines:** consistent improvement at both sites with unchanged likelihood
supports sampler geometry as the primary cause. If all reasonable parameterizations and
proposals retain low acceptance and separated bands, the narrow geometry hypothesis is
declined and likelihood discontinuity, multimodality, or model non-identifiability becomes
the stronger explanation.

### Experiment 2 — convergence-length confirmation

**Purpose:** test whether a geometry-improved chain becomes converged when its length is set
from measured tau rather than a fixed step budget.

**Design:** continue only the best geometry from Experiment 1. Require a stable pilot tau,
then run at least 50 tau per walker after burn-in and preferably 100 tau. Under the current
observed maximum tau, 50 tau would require roughly 24,000–25,500 total steps, so blindly
extending the present sampler is not the first action. Use at least three seeds, adaptive
burn-in based on trace stability, and report both unthinned ESS and any thinned product ESS.

**Expected result:** stable repeated tau estimates; at least the 150 ESS dimensional floor
for every parameter and preferably hundreds to 1,000+; overlapping split-chain and
seed-specific summaries; stable MAP, means, intervals, and posterior predictive bands.

**Proves / declines:** success proves that the posterior can be sampled with the selected
geometry and sufficient length. Continued drift, seed disagreement, or ESS failure after
50–100 stable tau declines a simple run-length explanation and points to multimodality or
non-identifiability.

### Experiment 3 — temporal likelihood comparison

**Purpose:** test the clear likelihood-limitation signal from lag-1 residual correlations
above 0.99 and ABBY error-scale saturation.

**Design:** after establishing a workable sampler, compare the current IID Gaussian
likelihood with at least one temporally aware alternative, such as an AR(1) residual model,
and one information-reduction alternative, such as daily aggregation or block weighting.
Optionally test a robust Student-t innovation model. Keep parameters, priors, data period,
and sampler geometry fixed. Evaluate multi-lag residual ACF, standardized residuals,
site-held-out predictive log score, skill, sigma location, tau, and ESS.

**Expected result if likelihood misspecification is important:** residual ACF drops
substantially across multiple lags, effective information is no longer inflated by hourly
replication, ABBY sigma moves away from its upper bound, and parameter/posterior summaries
become more stable across seeds without degrading held-out skill.

**Proves / declines:** those changes support the likelihood-limited hypothesis. If residual
dependence and ABBY bias remain while sampling is healthy, changing the error model alone is
declined and site-specific structural/model investigation becomes primary.

### Experiment 4 — ABBY model/data and residual audit

**Purpose:** identify why ABBY remains poor while JERC reaches useful skill.

**Design:** with no MCMC change, audit ABBY units, sign convention, observation QC/missingness,
timestamp/time-zone alignment, forcing/collocation, and surrogate-domain coverage. Stratify
best-fit residuals by season, hour, temperature/moisture regime, and observed SR magnitude.
Compare the coupled surrogate response with available ELM/PPE behavior at matched parameters
and identify whether the negative bias already exists before MCMC.

**Expected result:** either a specific data/interface mismatch or a stable regime-dependent
bias appears, or all audit checks pass and the coupled model itself is unable to span the
observed ABBY response.

**Proves / declines:** a reproducible mismatch or out-of-domain regime supports a site-specific
data/surrogate explanation. Clean alignment and surrogate fidelity, combined with persistent
ABBY bias under a converged temporal likelihood, support structural model limitation. If
ABBY skill becomes adequate after sampler/likelihood repair, the site-specific hypothesis is
declined.

### Experiment 5 — identifiability and parameter-reduction test

**Purpose:** determine whether SR alone can identify all 14 model parameters plus error scale.

**Design:** use converged single-site runs to measure cross-parameter dependence and
seed-to-seed stability. Compare the full parameter set against a scientifically justified
reduced set that fixes or groups weakly constrained `rf_*` parameters. If available and
scientifically appropriate, separately test an additional constraining observable rather
than tightening priors only to improve numerics.

**Expected result if over-parameterization is limiting:** the reduced model has narrower,
unimodal, seed-stable posteriors, higher ESS, and equivalent held-out SR skill without
boundary concentration.

**Proves / declines:** improved stability with preserved predictive skill supports weak
identifiability in the full model. If the full and reduced models are equally stable after
sampler repair, parameter count is not the dominant limitation.

### Experiment 6 — replicated compatibility test before joint calibration

**Purpose:** decide whether ABBY and JERC can share parameters, require hierarchical
site effects, or should remain separately calibrated.

**Design:** only after Experiments 1–3 yield converged site-local chains, compare posterior
overlap parameter by parameter across multiple seeds. Then perform posterior transfer tests:
predict ABBY with JERC draws and JERC with ABBY draws. If overlap and transfer are adequate,
test a shared model; otherwise test hierarchical/site-offset structure with explicit
site-balanced likelihood contributions.

**Expected result for a joint-calibration candidate:** substantial site-posterior overlap,
stable transfer skill, and a joint fit that does not degrade either site's held-out prediction
relative to its converged single-site baseline.

**Proves / declines:** those outcomes support shared calibration. Disjoint posteriors,
poor transfer, or renewed JERC degradation decline a shared-parameter model and support
hierarchical or site-specific calibration.

## 7. Recommended sequence and decision gates

1. Run the bounded sampler-geometry pilots (Experiment 1).
2. Extend only a geometry that removes stuck walkers and terminal bands (Experiment 2).
3. With sampling controlled, test temporal likelihoods (Experiment 3).
4. Run the ABBY audit in parallel as a read-only/model-evaluation stream (Experiment 4).
5. Test parameter reduction only after reliable posterior draws exist (Experiment 5).
6. Reconsider joint calibration only after both sites pass convergence and likelihood checks
   (Experiment 6).

The immediate go/no-go gate is not a better best-fit score. It is reproducible mixing across
seeds: acceptance broadly in the target range, no stuck walker subgroup, merged terminal
log-probability traces, stable tau with at least 50 tau of sampling, and adequate per-parameter
ESS. Scientific progression additionally requires residual dependence to be addressed and
ABBY's persistent bias to be explained.

## 8. Final answer to the Iter008 questions

- **Did each run complete correctly?** Yes. Both runs pass integrity, provenance, checksum,
  shape, bounds, and completeness checks.
- **Did either MCMC converge?** No. Both fail acceptance, run-length/tau, ESS, and raw-walker
  overlap criteria.
- **Is either posterior scientifically valid?** No. JERC has a useful point fit, but its
  uncertainty and parameter posterior are not validated. ABBY fails both convergence and
  absolute predictive adequacy.
- **Are the two sites consistent with the Iter008 hypothesis?** Yes for identifying the
  immediate sampler bottleneck and exposing site-specific behavior; no for the expectation
  that 4,000 steps would be sufficient or that site separation alone would make the
  likelihood adequate.
- **What should be tested next?** Sampler geometry first, convergence length second, temporal
  likelihood third, ABBY-specific model/data causes in parallel, and only then parameter
  reduction and staged joint compatibility.
