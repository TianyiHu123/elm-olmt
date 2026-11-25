# ELM Three-Stage Surrogate MCMC Optimization Development Plan

**Repository:** [TianyiHu123/elm-olmt](https://github.com/TianyiHu123/elm-olmt)  
**Future integration target:** `pmcpu`, subject to a separate review after development  
**Development branch:** `feature/mcmc-optimization` (created; plan changes are committed independently of implementation iterations)  
**Development record:** `development/mcmc_optimization/`  
**Related plan:** [`development/three_stage_surrogate/PLAN.md`](https://github.com/TianyiHu123/elm-olmt/blob/feature/three-stage-surrogate/development/three_stage_surrogate/PLAN.md)  
**Computing:** UA Puma for surrogate-based initialization, MCMC, and diagnostics; NERSC Perlmutter for source ELM PPE and any later full-ELM verification  
**Status:** Campaign-level scientific and engineering contract; PPE1 is the active baseline, and PPE2 is a prepared but inactive prior option. Implementation details and iteration approvals are separate.

## Project context, goal, and scope

Develop a reproducible Bayesian calibration workflow using the **frozen, pooled, three-stage ELM surrogate** (spinup C/N → hourly GPP → hourly soil respiration, SR) and site-specific NEON observations. The nine target sites are **ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL**. **Initial optimization is independent for each site:** infer a distinct **18-dimensional** ELM parameter posterior per site, using that site's forcing and observations. The pooled surrogate is shared; parameter posteriors are not pooled. **The initial executable baseline uses the original PPE1 (`NEON_ppe_vertc`) prior and its coupled surrogate `release_0001`.** Prepare optional PPE2-prior support now, but do not activate PPE2 scientific calibration until a compatible PPE2-trained/validated release and uncertainty handoff exist. Begin with a small one-/two-site pilot, then run all eligible sites.

Reuse the current scrambled-Sobol candidate search, optional multistart local refinement, diverse candidate pool, `emcee` ensemble sampling, checkpointing, and diagnostic infrastructure wherever compatible. Implement reusable science and inference code under `model_ELM/` and appropriate repository-root entry points. Keep iteration records, HPC scripts, and development-specific tools under `development/mcmc_optimization/`; this directory is **not** a standalone Python package. Do not alter existing released workflows unintentionally.

**In scope:** observation/forcing alignment; explicit scientific priors; deterministic full-chain inference; resolution-specific likelihoods and fixed uncertainty inputs; site-specific initialization and MCMC; convergence, posterior, posterior-predictive, reproducibility, and verification diagnostics.  
**Out of scope for the first release:** retraining or redesigning the three-stage surrogate; fitted observation-error, covariance, bias, or depth-fraction parameters; full temporal covariance and cross-variable covariance beyond the fixed joint C/N formulation below; simultaneous/hierarchical multisite calibration; full ELM simulations inside the MCMC likelihood. These are optional future extensions, not hidden dependencies.

**Key dependency:** MCMC requires versioned surrogate artifacts with trustworthy end-to-end inference and held-out uncertainty diagnostics. Do not silently substitute true ELM spinup C/N or GPP for predicted upstream inputs. The separate surrogate plan owns the training/validation process. **Prior identity, sampling domain, trained parameter support, surrogate release, and uncertainty provenance must be compatible.** Changing only the prior switch cannot turn a PPE1 surrogate into a PPE2 surrogate.

---

## 1. Inputs, scientific contract, and preflight

### 1.1 Authoritative inputs

- **Parameters:** use the original 18-parameter PPE1 `NEON_ppe_vertc_parmfile`, `generate_scramble_sobol.py`, and associated metadata as the **active default**. Preserve the separately supplied PPE2 `generate_scramble_sobol.py`, `SAMPLING_ppe2.md`, and `sobol18_1024.txt` identities for a **selectable but initially inactive** `ppe2` prior. Record each design's parameter names/order, bounds, PFT indices, transforms and conditional rules, seed, and software versions. The selected design's authoritative files define its support; do not infer bounds from model weights.
- **Surrogate:** initially the published **PPE1 coupled** spinup/GPP/SR `release_0001` via `model_ELM.three_stage_coupled_release.CoupledThreeStageInference`, with its scalers, feature schemas, time/calendar and forcing-history requirements, training-member provenance, and checksums. The full chain predicts all upstream quantities from a proposed parameter vector. A future PPE2-trained release must have an independently validated artifact identity.
- **Uncertainty:** for PPE1, reuse and validate the **Iter015 development-only 20-repetition handoff**: GPP/SR errors at *hourly and daily* resolutions and paired full-profile spinup C/N errors. Record biases, error distributions, per-repetition RMSE/MAE, site-specific C–N covariance, and derivation of fixed error inputs. **Do not rerun the PPE1 robustness study merely to start MCMC.** A future PPE2-trained surrogate requires its **own** held-out uncertainty estimates and depth coefficients; PPE1 values cannot be silently transferred. The protected fixed-test members must not enter surrogate training, surrogate uncertainty estimation, or surrogate retuning. The separately defined full-ensemble depth observation operator in Section 1.2 is an explicit exception for depth-operator estimation only.
- **Flux observations:** user-preprocessed GPP and SR NetCDF observations with timestamps, units, quality masks, optional uncertainty variables, and provenance. GPP may provide `GPP_mean`, `GPP_halfdiff`, and/or a configured `GPP_err`; SR may provide `SR_err`. Validate actual variable names against each declared file rather than assuming they exist.
- **Soil observations:** user-provided `NEON_soilC_N_CN.csv` with one positive C stock and one positive N stock per site, units of gC/m² and gN/m², and `effectiveDepth_m`. Verify provenance/processing, effective depth, and anomalous site-level ratios (including TALL) before production use.

At preflight, enforce exact site identity, 18-parameter schema, configured surrogate input/output definitions, unit conversions, complete source identities, forcing/observation timestamp overlap, **ELM no-leap calendar** handling, valid masks, and positive finite uncertainty values. Reject mismatches rather than guessing a replacement dataset. Keep site-specific observational windows; do not truncate all sites to a common period.

### 1.2 Settled spinup interface and fixed observation-depth operator

The frozen spinup surrogate supplies exactly two soil-only, full-profile stocks:

\[
(\widehat C_{s,\mathrm{full}},\widehat N_{s,\mathrm{full}})
=f_{\mathrm{spinup}}(\theta,z_s),
\]

with units gC/m² and gN/m². It does not perform NEON depth correction. The MCMC project exclusively owns the site-specific observation operator

\[
\widehat C_{s,D}(\theta)=\bar f_{C,s}\widehat C_{s,\mathrm{full}}(\theta),
\qquad
\widehat N_{s,D}(\theta)=\bar f_{N,s}\widehat N_{s,\mathrm{full}}(\theta),
\]

where \(D\) is the site's validated NEON effective observation depth. The fractions are fixed site/element inputs, not inferred parameters. Initial **PPE1** preprocessing gives the following descriptive estimates from all 1,024 PPE1 members at each site:

| Site | NEON effective depth | Mean C fraction | Mean N fraction |
| --- | ---: | ---: | ---: |
| ABBY | 2.0 m | 0.709296 | 0.707732 |
| JERC | 2.0 m | 0.757688 | 0.756602 |

For the fixed **PPE1 MCMC observation-depth operator**, adopt the already characterized site-specific means of member-level C and N depth fractions from **all 1,024 PPE1 members** in the previously validated ABBY/JERC spinup-preprocessing NetCDFs. The depth operator is a fixed empirical transformation of full-profile ELM soil stocks, not a refit of the frozen surrogate. Reuse the existing PPE1 preprocessing reports, source hashes, and diagnostic results; read the member-level files only as needed to obtain full-precision operator and paired depth-error covariance values and to verify consistency with the published summaries. Do not rerun ELM restart integration or generate redundant depth-preprocessing figures. Record source identities, the 1,024-member population, estimator, effective observation depth, stock definitions, units, and adopted numerical coefficients. Because the 205 historically protected fixed-test members contribute to this final depth operator, those members are **not independent tests of the combined surrogate-plus-depth operator**; this does not retroactively change the completed independent evaluation of the frozen full-profile surrogate. For additional sites, require an equally documented eligible full PPE-specific depth-preprocessing ensemble. **PPE2 depth fractions/covariance must come from its own PPE2 preprocessing and compatible surrogate/uncertainty release before PPE2 scientific inference is activated; never transfer PPE1 values.** The two-output surrogate architecture and MCMC ownership of depth correction remain unchanged.

### 1.3 Inference execution and performance contract

The published `CoupledThreeStageInference` delegates to `FoldThreeStageInference.predict_to_arrays`, which **batches hourly GPP and SR feature rows** (bounded by `member_chunk`); it is not inherently an hour-by-hour model invocation. The older `FrozenThreeStageInference` uses a deterministic one-row prediction kernel, so the MCMC adapter must select and record the **coupled release path** rather than accidentally reverting to the older path. Batching does **not** guarantee affordable posterior evaluation, especially for long windows and many MCMC proposals. Forcing-window feature generation, site-context loading, scaler work, stage predictions, and memory allocation may still dominate.

**Early engineering gate:** before setting large candidate budgets or production chain lengths, measure reproducible cold/warm **coupled-surrogate evaluation** time and peak memory, then measure full posterior-call time once the likelihood adapter is available on the target Puma environment for representative ABBY/JERC forcing windows, both single-proposal and plausible batch sizes. Separate artifact loading/preprocessing from per-proposal cost; record thread settings, hardware, exact release, window length, output resolution, and projected Sobol and MCMC walltime from measured throughput. Check deterministic replay and scientifically equivalent stage/likelihood outputs under any batching or caching proposal. Define acceptable resource budgets from evidence at the iteration kickoff, not from an unmeasured claim of speed.

If measured throughput is inadequate, propose a **separately reviewed infrastructure optimization** (for example, safe caching of site-static/forcing features, bounded batching, or avoiding repeated loading); require numerical equivalence and provenance checks before adopting it. This gate belongs to the campaign plan because it affects feasibility, but the optimization design, code changes, and benchmarks belong to approved iteration records. **No inference-engine rewrite or performance experiment is authorized by the plan revision itself.**

---

## 2. Parameter prior and sampling domain

Require a versioned `prior_id` with two variants: **`ppe1` (default; active scientific baseline)** and **`ppe2` (optional implementation, inactive for science until its compatible surrogate is released)**. Load the selected design's exact order, bounds, conditional draws, and provenance. This **prior density** is evaluated at every MCMC proposal; the Sobol candidate pool only provides **initial walker positions**, not a discrete prior. Switching priors changes the target posterior and the identity of all candidate pools and checkpoints: never reinterpret or resume an old run under the other prior.

| PPE parameter family | Names / rule | Physical prior | MCMC coordinate |
| --- | --- | --- | --- |
| Other decomposition rates (7) | `k_l1`, `k_l2`, `k_l3`, `k_s1`, `k_s2`, `k_s3`, `k_frag` | Independent bounded **log-uniform** in both designs | Natural log |
| `k_s4` (1) | `k_s4` | **PPE1:** independent log-uniform on `[2e-5, 2e-4]`. **PPE2:** conditional log-uniform on `[8e-5, min(1e-3, k_s3)]`, with normalized conditional density | Natural log; conditional support |
| Respiration fractions (6) | `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, `rf_s3s4` | Independent bounded **uniform** | Bounded logit |
| Other scalar traits (2) | `act25`, `leaf_long` | Independent bounded **uniform** | Physical/linear initially |
| Leaf and root C:N (2) | `leafcn`, `frootcn` | **Uniform leafcn**, **conditional-uniform frootcn** | Physical/linear initially, with joint support check |

The generator's default C:N construction (subject to exact persisted PPE metadata) is

\[
L=\mathrm{leafcn}\sim U(L_{\min},L_{\max}),\quad a(L)=\max(R_{\min},L+g),\quad b=\min(R_{\max},W-g),
\]
\[
R=\mathrm{frootcn}\mid L\sim U(a(L),b),\qquad g=0.5,\;W=\mathrm{livewoodcn}=50.
\]

For the documented PPE list, `leafcn` is bounded 15–40, `frootcn` is listed as 40–60, and the effective upper bound is 49.5. `livewoodcn` is **fixed**, not an additional inferred parameter. Preserve the **sequential conditional distribution**, not merely the inequalities or a joint-uniform density over the feasible polygon. Require \(a(L)<b\).

Let \(K\) be all eight decomposition rates, with the same conditional C:N limits \(a(L), b\) in both variants. **PPE1** draws `k_s4` independently. **PPE2** draws \(k_{s4}\mid k_{s3}\sim\mathrm{LogUniform}(\ell_4,u_4(k_{s3}))\), where \(\ell_4=8\times10^{-5}\), \(u_4(k_{s3})=\min(10^{-3},k_{s3})\), and the upper limit must exceed the lower limit. Within each design's complete support, the physical-space log densities, up to parameter-independent constants, are

\[
\log p_{\mathrm{PPE1}}(\theta)=-\sum_{k\in K}\log k-\log[b(L)-a(L)]+\mathrm{const},
\]
\[
\log p_{\mathrm{PPE2}}(\theta)=-\sum_{k\in K}\log k-\log\!\left[\log\!\left(\frac{u_4(k_{s3})}{\ell_4}\right)\right]-\log[b(L)-a(L)]+\mathrm{const}.
\]

Each density is \(-\infty\) outside **its own** support. The extra PPE2 log-width factor is a **conditional-prior normalization**, not an added uncertainty term in the likelihood. Implement the PPE2 conditional inverse Sobol map and density together: a simple `k_s4 <= k_s3` inequality with the independent PPE1 prior density is wrong.

Retain the physical-space prior as authoritative. When `emcee` works in log or logit coordinates, add the correct transformation Jacobian to the **sampling-coordinate posterior**; a transformation by itself is not a normal/lognormal prior. For deterministic local optimization of the *physical* posterior in transformed coordinates, do **not** add a sampling Jacobian to its objective. Numerical tests must confirm **both variants'** density, conditional normalization and relative ratios, support, inverse Sobol maps, and physical/transformed posterior equivalence. Validate selected-prior/support versus selected-release compatibility before inference; never clip, extrapolate, or silently truncate an incompatible prior to the released surrogate's support.

---

## 3. Site-specific likelihoods

For site \(s\), let \(\theta_s\) be its independent 18-parameter vector. The initial four-variable posterior is

\[
\log p(\theta_s\mid y_s)=\log p(\theta_s)+\ell_{s,\mathrm{GPP}}+\ell_{s,\mathrm{SR}}+\ell_{s,CN}+\mathrm{const}.
\]

Report the GPP, SR, and joint C/N likelihood contributions and their valid-observation counts separately. GPP and SR retain their initial conditionally independent pointwise Gaussian formulation. C and N use the fixed joint covariance below rather than independent likelihood terms. No arbitrary balancing weights are applied between fluxes and stocks in a site's baseline posterior.

### 3.1 GPP and SR: independent Gaussian residuals

For \(v\in\{\mathrm{GPP},\mathrm{SR}\}\) at a chosen hourly or daily resolution, use

\[
\ell_{s,v}(\theta_s)=-\frac12\sum_{i\in\mathcal V_{s,v}}\left[\frac{(y^{obs}_{s,v,i}-\widehat y_{s,v,i}(\theta_s))^2}{\sigma^2_{s,v,i}}+\log(2\pi\sigma^2_{s,v,i})\right],
\]
\[
\sigma^2_{s,v,i}=\sigma^2_{\mathrm{obs},s,v,i}+\sigma^2_{\mathrm{sur},s,v,\mathrm{resolution}}.
\]

Use independently configurable `GPP.resolution` and `SR.resolution`; **daily/daily is the first baseline**. Hourly surrogate inference remains intact even when a flux's likelihood is daily: always aggregate predictions and observations to identical validated day groups and consistent flux units. Daily rates are daily means; a daily-integrated quantity must be handled consistently on both sides. Define a minimum daily-coverage rule explicitly and record excluded days; full valid 24-hour days are the conservative initial default.

**Observation uncertainties:**

- **GPP:** the user supplies `GPP_mean=(GPP_DT+GPP_NT)/2` and signed `GPP_halfdiff=(GPP_DT-GPP_NT)/2`. The initial heuristic observational standard deviation is `max(abs(GPP_halfdiff), 0.10*abs(GPP_mean), positive_absolute_floor)` in the **same resolution and units as the likelihood**, unless a validated configured `GPP_err` provides the authoritative uncertainty. Partitioning-method disagreement is a **proxy**, not a calibrated full measurement error; never double count it if `GPP_err` already incorporates it. Preserve the signed half-difference for diagnostics.
- **SR:** use valid provided `SR_err`; otherwise `max(0.10*abs(SR_obs), positive_absolute_floor)` at the likelihood resolution. Apply a fixed, documented fallback; do not estimate `sigma_SR` in MCMC.
- **Daily observations:** estimate/derive observation uncertainty at the *daily* scale from source data and their dependence assumptions; **do not automatically divide hourly errors or hourly surrogate RMSE by \(\sqrt{24}\)**. Derive daily surrogate errors from actual daily-aggregated held-out predictions versus targets.

The absolute floors, error-source precedence, coverage rules, and observation preprocessing versions must be configured and frozen per run, not selected after seeing posterior results. Treat physically valid zero/nighttime fluxes and occasional negative GPP measurements according to explicit QC rules, rather than removing all nonpositive fluxes by default.

### 3.2 Soil C and N: joint bivariate lognormal likelihood

Apply the fixed depth operator in Section 1.2 to obtain positive depth-compatible predictions. Define

\[
\mathbf d_s(\theta)=
\begin{bmatrix}
\log C_s^{obs}-\log\widehat C_{s,D}(\theta)\\
\log N_s^{obs}-\log\widehat N_{s,D}(\theta)
\end{bmatrix}.
\]

With an optional fixed, independently estimated prediction-bias correction \(\boldsymbol{\mu}_{s,\mathrm{pred}}\), define \(\mathbf e_s(\theta)=\mathbf d_s(\theta)+\boldsymbol{\mu}_{s,\mathrm{pred}}\) and

\[
\ell_{s,CN}(\theta)=-\frac12\left[
\mathbf e_s^T\boldsymbol{\Sigma}_{s,\mathrm{total}}^{-1}\mathbf e_s
+\log|\boldsymbol{\Sigma}_{s,\mathrm{total}}|
\right]+\mathrm{const}.
\]

Freeze the 2×2 covariance for each site and observational-CV configuration before MCMC. Do not add uncertainty, covariance, depth-fraction, or bias parameters to the 18-dimensional parameter vector. Under the initial assumption that observation, surrogate, and depth-correction errors are mutually uncorrelated,

\[
\boxed{
\boldsymbol{\Sigma}_{s,\mathrm{total}}=
\boldsymbol{\Sigma}_{s,\mathrm{obs}}+
\boldsymbol{\Sigma}_{s,\mathrm{sur}}+
\boldsymbol{\Sigma}_{s,\mathrm{depth}}
}.
\]

#### Observation covariance

Use a **30% observational coefficient of variation** as the baseline and fixed **20%** and **50%** sensitivity cases. Convert each assumed CV to log-space variance with

\[
\tau_{\mathrm{obs}}^2=\log(1+CV^2),
\qquad
\boldsymbol{\Sigma}_{s,\mathrm{obs}}=
\begin{bmatrix}
\tau_{\mathrm{obs},C,s}^2&0\\
0&\tau_{\mathrm{obs},N,s}^2
\end{bmatrix}.
\]

For the 30% baseline, each diagonal entry is approximately 0.08618. Initial C and N observation errors are independent. The CV values are sensitivity assumptions, not empirically established NEON measurement-error estimates.

#### Surrogate covariance

For PPE1 held-out development member \(m\) in robustness repetition \(r\), retain the paired full-profile log errors

\[
\boldsymbol{\delta}_{s,m,r}^{sur}=
\begin{bmatrix}
\log\widehat C^{full}_{s,m,r}-\log C^{full}_{s,m}\\
\log\widehat N^{full}_{s,m,r}-\log N^{full}_{s,m}
\end{bmatrix},
\qquad
\boldsymbol{\Sigma}_{s,\mathrm{sur}}=
\operatorname{Cov}(\boldsymbol{\delta}^{sur}_s).
\]

For the **PPE1 baseline**, estimate a site-specific 2×2 covariance, including the C–N term, using development-only held-out predictions from the existing 20 repetitions. When a PPE2 surrogate is trained, repeat the **uncertainty estimation** on its own development held-out predictions instead of transferring the PPE1 covariance. Preserve paired values and per-repetition estimates, summarize variation among repetitions, and document the estimator used to produce the one fixed covariance selected for MCMC. Because validation members overlap among repetitions, do not treat repeated occurrences as independent replicates when quantifying estimator precision. The protected fixed-test members must not select or estimate this covariance.

#### Depth-correction covariance

For element \(v\in\{C,N\}\) and eligible member \(m\) of the full PPE-specific depth-preprocessing ensemble, define

\[
\varepsilon_{v,s,m}^{depth}=\log\left(
\frac{\bar f_{v,s}S^{full}_{v,s,m}}{S^{NEONdepth}_{v,s,m}}
\right),
\qquad
\boldsymbol{\Sigma}_{s,\mathrm{depth}}=
\operatorname{Cov}
\begin{pmatrix}
\varepsilon^{depth}_{C,s}\\
\varepsilon^{depth}_{N,s}
\end{pmatrix}.
\]

Completed **PPE1** ABBY/JERC preprocessing gives these 1,024-member full-ensemble summaries (rounded here; do not use report-rounding as numerical likelihood inputs):

| Statistic | ABBY | JERC |
| --- | ---: | ---: |
| C log-error SD | 0.152458 | 0.139499 |
| N log-error SD | 0.155987 | 0.141593 |
| C–N log-error correlation | 0.998835 | 0.999092 |
| C log-error mean | 0.011174 | 0.009329 |
| N log-error mean | 0.011633 | 0.009577 |

The corresponding full-ensemble covariance matrices, rounded for presentation, are approximately

\[
\boldsymbol{\Sigma}_{ABBY,\mathrm{depth}}=
\begin{bmatrix}
0.02324&0.02375\\
0.02375&0.02433
\end{bmatrix},
\qquad
\boldsymbol{\Sigma}_{JERC,\mathrm{depth}}=
\begin{bmatrix}
0.01946&0.01973\\
0.01973&0.02005
\end{bmatrix}.
\]

For the PPE1 production depth operator, use the existing 1,024-member fraction and depth log-residual estimates; verify or recover the **full-precision paired 2×2 covariance** from the existing member-level ABBY/JERC preprocessing NetCDFs if it was not already stored at full precision. Record the covariance estimator and require agreement with the earlier reports within their printed precision. This is a bounded numerical extraction/verification, **not** new ELM spinup preprocessing, restart processing, surrogate fitting, or a mandatory 819/205 rerun. Keep the 819/205 split strictly for the frozen surrogate training and held-out uncertainty provenance. The near-one C–N depth-error correlations are not the total likelihood-error correlations; the total correlation follows from the sum of all three covariance components.

#### Cross-source independence diagnostic, bias, and numerical handling

Retain zero cross-source covariance in the initial total-covariance formula. During normal surrogate robustness evaluation, calculate the empirical within-element and available cross-element correlation or covariance between \(\boldsymbol{\delta}^{sur}_{s,m,r}\) and \(\boldsymbol{\varepsilon}^{depth}_{s,m}\) on the same held-out members. Report whether these omitted terms are small relative to the retained surrogate and depth components. This is a diagnostic only—not a new experiment, additional training campaign, or release gate. If dependence is substantial, document its potential effect and consider a directly estimated combined surrogate-plus-depth covariance only as a later refinement; do not automatically alter the baseline likelihood.

Record surrogate and depth prediction biases separately. Under the initial additive-error approximation, the optional fixed correction may combine the **Iter015 development-only surrogate-error mean** with the separately characterized **full-ensemble PPE1 depth-error mean**, \(\boldsymbol{\mu}_{s,\mathrm{pred}}=\boldsymbol{\mu}_{s,\mathrm{sur}}+\boldsymbol{\mu}_{s,\mathrm{depth}}\), with the sign convention in \(\mathbf e_s\) above. Do not conflate bias with variance, inflate covariance to hide systematic error, or fit a bias in MCMC.

Require positive finite observed, full-profile, and depth-adjusted stocks. A nonpositive surrogate stock returns `-inf` and triggers artifact/domain diagnostics rather than clipping. Require every total covariance to be finite, symmetric, and positive definite; use stable covariance estimation and Cholesky/linear-solve and log-determinant calculations rather than an explicit matrix inverse in implementation. Do not replicate either stock observation across hours or days.

The preprocessing provides additional scientific context: modeled NEON-depth log C/N stock correlation is near 0.9998 at ABBY and JERC; member-level modeled C:N ratios are approximately 10.10 ± 0.25; and observed NEON C:N ratios are approximately 13.94 at ABBY and 12.19 at JERC. Treat these as possible structural stoichiometric limitations. Distinguish correlation of modeled stocks from surrogate prediction-error covariance, depth-error covariance, and observational-error covariance. No additional identifiability study is a prerequisite for the initial likelihood.

### 3.3 Error estimation and limitations

For each site and available flux-likelihood resolution, use **out-of-sample full-chain errors** from the **selected surrogate's own** development validation (the existing Iter015 handoff for PPE1; a separately validated handoff for any future PPE2 release); preserve site-wise biases, RMSE, MAE, residual distributions, repetition-to-repetition variability, and the selected fixed uncertainty scale. Calculate daily errors by aggregating each held-out member's hourly ELM and surrogate predictions *before* taking daily residuals. For an initial constant Gaussian flux-error scale, a root-mean-squared held-out residual is defensible if reported alongside bias and residual standard deviation; a systematic bias is **not** automatically solved by widening uncertainty.

The flux quadrature formula assumes observation and surrogate errors are independent, while the initial C/N covariance formula assumes mutual independence among observation, surrogate, and depth errors subject to the diagnostic above. Neither formulation represents all ELM structural discrepancy. Hourly errors may be serially correlated, GPP/SR errors may be cross-correlated, and robustness validation sets overlap. Document these limitations and inspect the existing standardized-residual diagnostics before interpreting narrow posterior intervals as well calibrated.

---

## 4. Candidate search and walker initialization

Retain the current **scrambled Sobol → evaluate log posterior → diversified promising anchors → optional local optimization → high-quality/diverse pool → initial walkers** workflow, but update it for the new 18-parameter posterior.

1. Draw a new 18-D Owen-scrambled Sobol sequence with an **initialization seed distinct from the PPE design seed**. Use power-of-two blocks and configurable staged evaluation budgets. Map each unit coordinate through the selected, provenance-checked generator: log-uniform for the seven shared independent rates, **independent PPE1 or conditional PPE2 `k_s4` log-uniform**, linear uniform for `rf_*`, `act25`, `leaf_long`, and `leafcn`, and conditional-uniform for `frootcn`. Evaluate the **new** site-specific GPP/SR/(when enabled) C/N posterior, not the legacy SR-only score.
2. Select promising but diverse starting anchors. Retain the existing L-BFGS-B multistart concept only where the pilot confirms benefit; improve numerical conditioning by using normalized/log-scaled coordinates and a C:N-feasible parameterization or valid constraint enforcement. Optimization seeks the **physical posterior mode**, not the transformed-density mode.
3. Construct a documented pool balancing posterior score and parameter-space coverage, including separated modes when present. Use sensible **prior-unit / sampling-coordinate** distances rather than unscaled physical Euclidean distances, enforce the conditional support, and check numerical rank, nondegenerate span, uniqueness, and finiteness. The existing candidate counts, ~640 pool size, and 64 walkers are **configurable historical starting references**, not mandatory performance claims.
4. Choose independent, valid initial walker positions from that pool; re-evaluate their current posterior and save the original unit-space/physical states, selection rule, component scores, and provenance. Maintain per-site pools; do not transfer old 14-parameter/`fit_error=True` candidate scores or silently reuse pools evaluated under a different likelihood/prior.

The initialization design only helps **start** the ensemble. The prior still remains a continuous density evaluated for every proposed vector, and posterior convergence must be demonstrated independently of high initial scores.

---

## 5. MCMC inference and scientific diagnostics

Continue with `emcee` ensemble MCMC and the existing checkpoint/resume approach, using **exactly 18 inferred physical parameters** (no fitted error variances). Preserve the current log coordinates for rates, bounded-logit coordinates for `rf_*`, and physical coordinates for the other parameters as a baseline. Enforce C:N support for every proposal; retain the analytical Jacobian for transformed samplers. Consider constraint-aware C:N coordinates only if pilot mixing justifies them, and test any associated Jacobian carefully. `DEMove`/`DESnookerMove` mixture and `StretchMove` may remain selectable; choose production move settings and walker/chain lengths from the pilot, not from fixed assumptions.

Save complete raw chains, log-prior and component log-likelihoods (or reproducible evaluations thereof), log posterior, transformed/physical coordinate metadata, walker acceptance fractions, checkpoints, restart provenance, and non-overwriting per-site outputs. A failed numerical evaluation must return a well-documented `-inf` posterior or explicit error, never a finite fabricated likelihood. Distinct seeds/runs are needed to assess convergence, sensitivity to initial pools, and possible multimodality.

**Required reports:** trace plots and chain stationarity checks; per-parameter autocorrelation time and effective sample size when estimable; acceptance by walker; prior-bound occupancy; posterior marginal/joint summaries and cross-parameter correlations; comparison across independent initializations; GPP, SR, and joint C/N log-likelihood breakdown; posterior-predictive GPP/SR time series and residual/QC diagnostics; depth-adjusted C/N posterior predictions for four-component runs; fixed covariance components and bias handling; and interpretable convergence warnings when chain lengths are inadequate. Avoid declaring convergence solely from one high-likelihood point or one aggregate score. Retain raw draws even when summary/plot subsampling is used.

**Verification:** test selected posterior vectors against full ELM where computationally feasible, but do not turn such verification into an inner-loop MCMC dependency. Distinguish emulator agreement from full-model validation.

---

## 6. Development code responsibilities and tests

Prefer extending established modules over duplicating the MCMC machinery. Review these **responsibility boundaries**, not mandated new file/class names:

| Existing code | Expected adaptation |
| --- | --- |
| `model_ELM/coupling_pipeline.py`, `initialize_pipeline.py` | New 18-D science/prior contract; Sobol inverse maps; valid C:N candidates; prior-aware posterior scores; transformed diversity/local search; immutable pool provenance |
| `model_ELM/MCMC_forcing.py`, `model_ELM/MCMC.py` | Generalize current SR-only likelihood/sampler for GPP, SR, and joint bivariate-lognormal C/N use; keep all uncertainty inputs fixed and **remove `fit_error`** for the new path |
| `model_ELM/mcmc_geometry.py` | Verify log/logit transforms, Jacobians, and exact support for both `prior_id` variants; reject incompatible prior/release combinations |
| `model_ELM/three_stage_coupled_release.py`, `model_ELM/three_stage_inference.py` | Adapt the published PPE1 coupled inference interface with minimal changes; benchmark full-chain throughput before considering separately approved caching/batching changes; preserve existing release behavior |
| `model_ELM/load_obs_nc.py`, `model_ELM/coupling_pipeline.py` | Reusable GPP/SR observation loading and time alignment; fixed site-specific C/N depth operator; validated observation, surrogate, and depth covariance inputs; uncertainty precedence and masks |
| `model_ELM/mcmc_diagnostics.py`, `model_ELM/mcmc_artifacts.py` | Extend per-variable posterior/chain/residual diagnostics, reproducibility, and site-scoped output bundles |
| `model_ELM/optimization_config.py`, root campaign CLIs | Versioned configuration; no hardcoded 14-parameter count, SR-only target, or `fit_error=True` |
| `tests/` | Focused numerical/statistical/integration tests for the new posterior and pipeline |

Required tests should cover: inverse Sobol mapping versus **each PPE generator**; parameter order/bounds; PPE1 independent and PPE2 normalized conditional `k_s4` support **and density**; conditional C:N support **and density**; log-uniform prior ratios; coordinate Jacobian invariance; synthetic GPP, SR, and bivariate C/N likelihood calculations; exact depth-fraction application; covariance assembly and C–N off-diagonal retention; no fitted error/covariance/bias/depth-fraction dimensions; all four observed-variable contributions; valid missing-data/zero-flux handling; daily aggregation and uncertainty at native scale; chronology and no-leap handling; invalid C/N stocks and non-positive-definite covariance; deterministic replay of initialization and chain restart; preservation of legacy interfaces; surrogate end-to-end inference without true upstream ELM target leakage; rejection of PPE2/release support mismatch; and reproducible measured throughput plus numerical-equivalence checks for any future inference optimization.

A run must fail closed on **mismatched `prior_id`, PPE design metadata, surrogate training support/release, or uncertainty/depth provenance**; incompatible artifact schema, trained-site identity, wrong parameter count/order, unsupported stock definition, missing or inconsistent full-ensemble PPE-specific depth-operator inputs, fixed-test-contaminated **surrogate uncertainty** estimates, missing uncertainty provenance, non-finite/non-positive-definite covariance, corrupted checkpoint/pool hashes, or absent required observation overlap.

---

## 7. Experiment progression, validation, and extension points

### 7.1 Baseline configurations and comparisons

The initial scientific baseline uses **`prior_id=ppe1` and the published, frozen PPE1 coupled `release_0001`**. The first MCMC pilot targets independent ABBY and JERC site posteriors using the complete **GPP+SR+joint-C/N four-observable posterior**, with **daily GPP + daily SR** likelihoods and **C/N observational CV 0.30** by default. Iter002--003 already implemented and validated the full four-observable likelihood, its fixed uncertainties, and the associated immutable observation and full-ensemble PPE1 depth products. Retain GPP+SR-only as a controlled comparison, not a prerequisite for joint C/N sampling. Test C/N observational CV assumptions **20%, 30%, 50%** without tuning them opportunistically, and treat alternative independently configurable (`hourly` or `daily`) GPP/SR resolution combinations as separately controlled sensitivity configurations. The short initial pilot validates sampler behavior and operational feasibility; it does not establish scientific convergence.

### 7.2 Proposed development sequence

1. **Campaign-plan lock (outside iterations):** finish this campaign-level revision and commit it on the existing `feature/mcmc-optimization` branch. Keep the plan change distinct from iteration kickoff, code implementation, HPC execution, and later scientific-plan amendments.
2. **Release and prior contracts:** validate PPE1 `release_0001`, the existing PPE1 uncertainty handoff, exact `ppe1` default prior, and optional `ppe2` conditional-`k_s4` inverse map/log-density with independent numerical tests. Bind all run/configuration artifacts to the selected prior and release; **do not execute PPE2 scientific likelihoods against PPE1 artifacts**.
3. **Interface and performance preflight:** build the minimum coupled adapter, check site/forcing/time/stock interfaces and reproducible end-to-end inference, and benchmark coupled-surrogate throughput and memory under representative workloads. Recheck complete posterior-call throughput once the likelihood is implemented. Decide from measured budgets whether a separate infrastructure optimization is needed before large candidate searches or chains.
4. **Observation and flux-likelihood prototype:** validate GPP/SR files, masks, timestamps and daily uncertainties; implement independently selectable hourly/daily Gaussian likelihood terms and deterministic one-site checks.
5. **Candidate search and MCMC pilot:** use prior-aware 18-D scrambled-Sobol initialization, valid diversified pools and walkers, optional local refinement, and independent ABBY and JERC site-specific `emcee` pilots with the complete four-observable posterior by default. Verify checkpoint/restart, sampler behavior, performance, mixing, residual diagnostics, and pilot limitations before locking production settings.
6. **Joint C/N comparisons and sensitivity:** subsequently compare GPP+SR-only and four-observable posteriors and evaluate C/N observation-CV sensitivity while retaining the frozen full-ensemble **1,024-member PPE1 depth coefficients**, observation, surrogate, and depth covariance, and fixed C/N bias correction. Reuse the already validated PPE1 observation, preprocessing, and depth-diagnostic products without repeating soil preprocessing; this step evaluates controlled comparisons and sensitivities rather than implementing the C/N likelihood for the first time.
7. **Site expansion and sensitivity:** run independent eligible-site posteriors, including C/N CV scenarios where enabled; produce posterior-predictive and provenance reports. A future switch to PPE2 is a **separate scientific release gate** after PPE2 surrogate and uncertainty validation; it reuses the implemented prior option but requires fresh prior/release compatibility and model checks.
8. **Review and integration:** evaluate backward compatibility, scientific limitations, reproducibility and diagnostics; merge only approved changes into the agreed integration target.

These are **campaign progression phases**, not approved numbered implementation iterations. Agree each iteration's implementation scope, resource contract, and specific gates separately. Completing or committing this plan does **not** authorize an Iter001 code change, benchmark job, or sampler run.

### 7.3 Development records

Mirror the existing surrogate development conventions: `README.md`, `PLAN.md`, `WORKFLOW.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, and folders for `iterations/`, `summaries/`, `slurm/`, `tools/`, and `templates/` as needed. Keep reusable optimization science code in `model_ELM/`, not inside this records folder. A small, reproducible **site campaign configuration** should record observation paths, variable/resolution choices, uncertainty assumptions, source hashes, **`prior_id`, PPE design and coupled surrogate release identifiers, PPE-specific depth/uncertainty handoff IDs**, seeds, pool settings, sampling settings, measured performance settings, and output destinations.

### 7.4 Multisite future placeholder

Expose a per-site function returning separate **GPP, SR, and joint C/N log-likelihood contributions** so a later multisite objective can combine them without rewriting inference. **Do not implement** shared-parameter, hierarchical, or site-balanced calibration in the first release. The user favors **equal site importance** if multisite calibration is added; this must become an **explicit, statistically justified combination policy** at that time, because averaging/normalizing site likelihoods changes the standard Bayesian posterior relative to summing independent observations.

---

## Expected outcome

A tested, provenance-complete, reproducible, **site-by-site 18-parameter Bayesian optimization system** that starts from a scientific-prior-aware scrambled Sobol search, runs transformed-coordinate `emcee` on the **validated PPE1 coupled three-stage ELM surrogate by default**, uses fixed observation-plus-surrogate uncertainty for GPP/SR, and applies a fixed site-specific depth operator plus observation, surrogate, and depth covariance for a joint bivariate-lognormal C/N likelihood. It preserves the GPP+SR-only comparison, reports posterior quality, convergence limitations, covariance assumptions, and scientific fit, and never expands the MCMC parameter vector beyond the original 18 physical parameters. The optional PPE2 conditional-`k_s4` prior is implemented and tested without scientifically activating it until a compatible PPE2-trained release and PPE2-specific uncertainty/depth inputs exist. Surrogate throughput is benchmarked before production budgets are approved; any performance rewrite remains an independently reviewed iteration decision.
