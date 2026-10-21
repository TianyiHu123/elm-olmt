# ELM Three-Stage Surrogate MCMC Optimization Development Plan

**Repository:** [TianyiHu123/elm-olmt](https://github.com/TianyiHu123/elm-olmt)  
**Integration base:** `pmcpu`, after compatible three-stage surrogate artifacts/interfaces are available  
**Proposed development branch:** `feature/mcmc-optimization` (create when the integration base is agreed)  
**Development record:** `development/mcmc_optimization/`  
**Related plan:** [`development/three_stage_surrogate/PLAN.md`](https://github.com/TianyiHu123/elm-olmt/blob/feature/three-stage-surrogate/development/three_stage_surrogate/PLAN.md)  
**Computing:** UA Puma for surrogate-based initialization, MCMC, and diagnostics; NERSC Perlmutter for source ELM PPE and any later full-ELM verification  
**Status:** Draft campaign-level plan. **Spinup C/N observation-interface decision remains open.** Implementation details and iteration approvals are separate.

## Project context, goal, and scope

Develop a reproducible Bayesian calibration workflow using the **frozen, pooled, three-stage ELM surrogate** (spinup C/N → hourly GPP → hourly soil respiration, SR) and site-specific NEON observations. The nine target sites are **ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL**. **Initial optimization is independent for each site:** infer a distinct **18-dimensional** ELM parameter posterior per site, using that site's forcing and observations. The pooled surrogate is shared; parameter posteriors are not pooled. Begin with a small one-/two-site pilot, then run all eligible sites.

Reuse the current scrambled-Sobol candidate search, optional multistart local refinement, diverse candidate pool, `emcee` ensemble sampling, checkpointing, and diagnostic infrastructure wherever compatible. Implement reusable science and inference code under `model_ELM/` and appropriate repository-root entry points. Keep iteration records, HPC scripts, and development-specific tools under `development/mcmc_optimization/`; this directory is **not** a standalone Python package. Do not alter existing released workflows unintentionally.

**In scope:** observation/forcing alignment; explicit scientific priors; deterministic full-chain inference; resolution-specific likelihoods and fixed uncertainty inputs; site-specific initialization and MCMC; convergence, posterior, posterior-predictive, reproducibility, and verification diagnostics.  
**Out of scope for the first release:** retraining or redesigning the three-stage surrogate; fitted observation-error parameters; full temporal/cross-variable covariance estimation; simultaneous/hierarchical multisite calibration; full ELM simulations inside the MCMC likelihood. These are optional future extensions, not hidden dependencies.

**Key dependency:** MCMC requires versioned surrogate artifacts with trustworthy end-to-end inference and held-out uncertainty diagnostics. Do not silently substitute true ELM spinup C/N or GPP for predicted upstream inputs. The separate surrogate plan owns the training/validation process.

---

## 1. Inputs, scientific contract, and preflight

### 1.1 Authoritative inputs

- **Parameters:** the original 18-parameter `NEON_ppe_vertc_parmfile`, `generate_scramble_sobol.py`, and associated PPE sample/metadata files (parameter names, order, bounds, PFT indices, transforms, conditional C:N rule, seed, and software versions). The parm-list and recorded provenance are authoritative; do not infer bounds or reorder parameters from model weight shapes.
- **Surrogate:** frozen three-stage spinup/GPP/SR models, scalers, feature schemas, time/calendar and forcing-history requirements, training-member provenance, and artifact checksums. The full chain predicts all upstream quantities from a proposed parameter vector.
- **Uncertainty:** site-wise, held-out end-to-end validation errors from the surrogate campaign's **20 development-pool robustness repetitions**: GPP and SR at *hourly and daily* resolutions; spinup C/N in log space for the eventual observation-compatible targets. Record biases, error distributions, per-repetition RMSE/MAE, and derivation of the final error scales. No final-test-based retuning.
- **Flux observations:** user-preprocessed GPP and SR NetCDF observations with timestamps, units, quality masks, optional uncertainty variables, and provenance. GPP may provide `GPP_mean`, `GPP_halfdiff`, and/or a configured `GPP_err`; SR may provide `SR_err`. Validate actual variable names against each declared file rather than assuming they exist.
- **Soil observations:** user-provided `NEON_soilC_N_CN.csv` with one positive C stock and one positive N stock per site, units of gC/m² and gN/m², and `effectiveDepth_m`. Verify provenance/processing, effective depth, and anomalous site-level ratios (including TALL) before production use.

At preflight, enforce exact site identity, 18-parameter schema, configured surrogate input/output definitions, unit conversions, complete source identities, forcing/observation timestamp overlap, **ELM no-leap calendar** handling, valid masks, and positive finite uncertainty values. Reject mismatches rather than guessing a replacement dataset. Keep site-specific observational windows; do not truncate all sites to a common period.

### 1.2 Pending C/N interface — explicit release gate

The **spinup surrogate output structure is not finalized**. For likelihood design, assume that its predicted soil C/N stocks are comparable to the NEON stocks at the declared site-specific depth and pool definition. **This is an assumption for planning, not a statement that the present `TOTSOMC`/`TOTSOMN` outputs already satisfy it.** Before enabling C/N likelihood terms, confirm vertical integration depth, pools (soil organic matter versus litter/CWD), units, and consistency between training targets, inference outputs, and observations. If needed, add an observation operator or revise surrogate targets through the *separate* surrogate-development process, without forcing a four-output spinup design here.

The implementation must support a scientifically valid **GPP+SR-only mode** while this gate is unresolved. The final four-variable calibration is not approved until C/N comparability and uncertainty targets pass validation; never silently compare mismatched stocks or use placeholder C/N values.

---

## 2. Parameter prior and sampling domain

Use the PPE's probability model as the initial scientific prior, with exact parameter order and bounds loaded from its authoritative files. This **prior density** is evaluated at every MCMC proposal; the Sobol candidate pool only provides **initial walker positions**, not a discrete prior.

| PPE parameter family | Names / rule | Physical prior | MCMC coordinate |
| --- | --- | --- | --- |
| Decomposition rates (8) | `k_l1`, `k_l2`, `k_l3`, `k_s1`, `k_s2`, `k_s3`, `k_s4`, `k_frag` | Independent bounded **log-uniform** | Natural log |
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

Within the valid 18-dimensional domain \(\Omega\), the log-prior, up to parameter-independent constants, is

\[
\log p(\theta)=-\sum_{k\in K}\log k-\log\!\big[b(\mathrm{leafcn})-a(\mathrm{leafcn})\big]+\mathrm{const};
\quad\log p(\theta)=-\infty\;\text{outside }\Omega.
\]

Retain the physical-space prior as authoritative. When `emcee` works in log or logit coordinates, add the correct transformation Jacobian to the **sampling-coordinate posterior**; a transformation by itself is not a normal/lognormal prior. For deterministic local optimization of the *physical* posterior in transformed coordinates, do **not** add a sampling Jacobian to its objective. Numerical tests must confirm prior density, normalization/relative ratios, support, and physical/transformed posterior equivalence.

---

## 3. Site-specific likelihoods

For site \(s\), let \(\theta_s\) be its independent 18-parameter vector. The initial four-variable posterior is

\[
\log p(\theta_s\mid y_s)=\log p(\theta_s)+\ell_{s,\mathrm{GPP}}+\ell_{s,\mathrm{SR}}+\ell_{s,C}+\ell_{s,N}+\mathrm{const}.
\]

Each component and its number of valid observations must be reported separately. The initial covariance assumption is **diagonal**, conditional on \(\theta_s\): straightforward, efficient, and compatible with varying pointwise uncertainties, but potentially overconfident when errors are correlated. No arbitrary balancing weights are applied between GPP, SR, C, and N in a site's baseline posterior.

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

### 3.2 Soil C and N: lognormal likelihood

Once the C/N interface gate is passed, use one positive, depth-compatible C and one N stock per site. For \(v\in\{C,N\}\), write the log-space likelihood (omitting constants independent of \(\theta_s\)) as

\[
\ell_{s,v}(\theta_s)=-\frac12\left[\frac{\big(\log y^{obs}_{s,v}-\log\widehat y_{s,v}(\theta_s)\big)^2}{\tau_{s,v}^{2}}+\log(2\pi\tau^2_{s,v})\right],
\]
\[
\tau^2_{s,v}=\underbrace{\log(1+c_{\mathrm{obs},s,v}^2)}_{\text{log-space observation variance}}+\underbrace{\tau^2_{\mathrm{sur},s,v}}_{\text{held-out log-space surrogate error variance}}.
\]

Use a **fixed 30% observational coefficient of variation** (`c_obs=0.30`) as the initial assumption, with dedicated **20% and 50% sensitivity runs**. These are sensitivity assumptions, not known NEON measurement uncertainty. Estimate \(\tau_{\mathrm{sur}}\) using the held-out residuals of the *observation-compatible* spinup targets in log space. Check systematic surrogate bias and non-Gaussian residuals. If the surrogate predicts a nonpositive stock, reject the proposed parameter vector with `-inf` and diagnose the artifact/domain instead of silently clipping its prediction.

C and N are initially treated as conditionally independent; residual cross-correlation and potential double-counting of closely related stock constraints must be assessed as diagnostics. Do not replicate a stock observation across hours or days.

### 3.3 Surrogate error estimation and limitations

For each site and available likelihood resolution, use **out-of-sample full-chain errors** obtained from the surrogate development repetitions; preserve site-wise biases, RMSE, MAE, residual distributions, repetition-to-repetition variability, and the selected fixed uncertainty scale. Calculate daily errors by aggregating each held-out member's hourly ELM and surrogate predictions *before* taking daily residuals. For an initial constant Gaussian error scale, a root-mean-squared held-out residual is defensible if reported alongside bias and residual standard deviation; a systematic bias is **not** automatically solved by widening uncertainty. Avoid treating overlapping repeated validation splits as independent observations when quantifying precision of these estimates.

The quadrature combination assumes observation and surrogate errors are independent. The baseline does **not** represent all ELM structural discrepancy or serial and GPP/SR cross-error dependence. Document these limitations and inspect standardized residual autocorrelation and cross-variable dependence before interpreting narrow posterior intervals as well calibrated.

---

## 4. Candidate search and walker initialization

Retain the current **scrambled Sobol → evaluate log posterior → diversified promising anchors → optional local optimization → high-quality/diverse pool → initial walkers** workflow, but update it for the new 18-parameter posterior.

1. Draw a new 18-D Owen-scrambled Sobol sequence with an **initialization seed distinct from the PPE design seed**. Use power-of-two blocks and configurable staged evaluation budgets. Map each unit coordinate through the same physical marginal/conditional inverse transforms as `generate_scramble_sobol.py`: log-uniform for the eight rates, linear uniform for `rf_*`, `act25`, `leaf_long`, `leafcn`, and conditional-uniform for `frootcn`. Evaluate the **new** site-specific GPP/SR/(when enabled) C/N posterior, not the legacy SR-only score.
2. Select promising but diverse starting anchors. Retain the existing L-BFGS-B multistart concept only where the pilot confirms benefit; improve numerical conditioning by using normalized/log-scaled coordinates and a C:N-feasible parameterization or valid constraint enforcement. Optimization seeks the **physical posterior mode**, not the transformed-density mode.
3. Construct a documented pool balancing posterior score and parameter-space coverage, including separated modes when present. Use sensible **prior-unit / sampling-coordinate** distances rather than unscaled physical Euclidean distances, enforce the conditional support, and check numerical rank, nondegenerate span, uniqueness, and finiteness. The existing candidate counts, ~640 pool size, and 64 walkers are **configurable historical starting references**, not mandatory performance claims.
4. Choose independent, valid initial walker positions from that pool; re-evaluate their current posterior and save the original unit-space/physical states, selection rule, component scores, and provenance. Maintain per-site pools; do not transfer old 14-parameter/`fit_error=True` candidate scores or silently reuse pools evaluated under a different likelihood/prior.

The initialization design only helps **start** the ensemble. The prior still remains a continuous density evaluated for every proposed vector, and posterior convergence must be demonstrated independently of high initial scores.

---

## 5. MCMC inference and scientific diagnostics

Continue with `emcee` ensemble MCMC and the existing checkpoint/resume approach, using **exactly 18 inferred physical parameters** (no fitted error variances). Preserve the current log coordinates for rates, bounded-logit coordinates for `rf_*`, and physical coordinates for the other parameters as a baseline. Enforce C:N support for every proposal; retain the analytical Jacobian for transformed samplers. Consider constraint-aware C:N coordinates only if pilot mixing justifies them, and test any associated Jacobian carefully. `DEMove`/`DESnookerMove` mixture and `StretchMove` may remain selectable; choose production move settings and walker/chain lengths from the pilot, not from fixed assumptions.

Save complete raw chains, log-prior and component log-likelihoods (or reproducible evaluations thereof), log posterior, transformed/physical coordinate metadata, walker acceptance fractions, checkpoints, restart provenance, and non-overwriting per-site outputs. A failed numerical evaluation must return a well-documented `-inf` posterior or explicit error, never a finite fabricated likelihood. Distinct seeds/runs are needed to assess convergence, sensitivity to initial pools, and possible multimodality.

**Required reports:** trace plots and chain stationarity checks; per-parameter autocorrelation time and effective sample size when estimable; acceptance by walker; prior-bound occupancy; posterior marginal/joint summaries and cross-parameter correlations; comparison across independent initializations; site/variable log-likelihood breakdown; posterior-predictive GPP/SR time series and residual/QC diagnostics; C/N posterior predictions after its release gate; and interpretable convergence warnings when chain lengths are inadequate. Avoid declaring convergence solely from one high-likelihood point or one aggregate score. Retain raw draws even when summary/plot subsampling is used.

**Verification:** test selected posterior vectors against full ELM where computationally feasible, but do not turn such verification into an inner-loop MCMC dependency. Distinguish emulator agreement from full-model validation.

---

## 6. Development code responsibilities and tests

Prefer extending established modules over duplicating the MCMC machinery. Review these **responsibility boundaries**, not mandated new file/class names:

| Existing code | Expected adaptation |
| --- | --- |
| `model_ELM/coupling_pipeline.py`, `initialize_pipeline.py` | New 18-D science/prior contract; Sobol inverse maps; valid C:N candidates; prior-aware posterior scores; transformed diversity/local search; immutable pool provenance |
| `model_ELM/MCMC_forcing.py`, `model_ELM/MCMC.py` | Generalize current SR-only likelihood/sampler for full three-stage GPP/SR/C/N use and **remove `fit_error`** for the new path |
| `model_ELM/mcmc_geometry.py` | Verify log/logit transforms and Jacobians; enforce the authoritative 18-parameter schema and C:N support |
| `model_ELM/load_obs_nc.py`, `model_ELM/coupling_pipeline.py` | Reusable GPP/SR observation loading, calendar/time alignment, independent daily/hourly resolution, uncertainty precedence, masks, and daily variance handling |
| `model_ELM/mcmc_diagnostics.py`, `model_ELM/mcmc_artifacts.py` | Extend per-variable posterior/chain/residual diagnostics, reproducibility, and site-scoped output bundles |
| `model_ELM/optimization_config.py`, root campaign CLIs | Versioned configuration; no hardcoded 14-parameter count, SR-only target, or `fit_error=True` |
| `tests/` | Focused numerical/statistical/integration tests for the new posterior and pipeline |

Required tests should cover: inverse Sobol mapping versus PPE generation; parameter order/bounds; conditional C:N support **and density**; log-uniform prior ratios; coordinate Jacobian invariance; synthetic likelihood calculations; no fitted error dimension; all four component contributions; valid missing-data/zero-flux handling; daily aggregation and uncertainty at native scale; chronology and no-leap handling; invalid C/N stock behavior; deterministic replay of initialization and chain restart; preservation of legacy interfaces; and surrogate end-to-end inference without true upstream ELM target leakage.

A run must fail closed on incompatible artifact schema, trained-site identity, wrong parameter count/order, unsupported stock definition, missing uncertainty provenance, corrupted checkpoint/pool hashes, or absent required observation overlap.

---

## 7. Experiment progression, release gates, and extension points

### 7.1 Baseline configurations and comparisons

The **initial scientifically valid pilot** may run **GPP+SR only** while C/N interface work is pending. Its default is **daily GPP + daily SR**, with each resolution independently configurable (`hourly` or `daily`). Once the spinup C/N interface is approved, enable the full four-component model. Compare with GPP+SR-only to assess the incremental constraint from C/N; test C/N observational CV assumptions **20%, 30%, 50%** without tuning them opportunistically. Additional daily/hourly combinations are controlled experiments, not a requirement for the first production run.

### 7.2 Proposed development sequence

1. **Branch/project scaffold:** agree on the surrogate integration base, create the optimization branch, and initialize `development/mcmc_optimization/` as *pre-kickoff*. Examine reusable prior, pool, sampler, and artifact code; do not start production campaigns yet.
2. **Data and interface contract:** validate authoritative 18-parameter PPE metadata, frozen surrogate inference, observation files, error diagnostics, site forcing/timestamps, and provenance. Define reusable science/config validators; record the explicit pending C/N gate.
3. **Prior and initialization prototype:** implement/test physical prior with log-uniform rates and conditional C:N; 18-D scrambled Sobol inverse mapping; constraint-valid local search, candidate pools, and walker selection. Verify density transformations and source consistency.
4. **Flux-likelihood prototype:** implement the fixed-uncertainty Gaussian GPP/SR likelihood, independently selectable hourly/daily resolutions, and correct daily uncertainty/QC handling. Conduct synthetic and one-site deterministic posterior checks.
5. **MCMC pilot:** connect the frozen full three-stage surrogate to the new posterior, run GPP+SR-only site-specific chains, confirm checkpoint/restart and resource use on Puma, inspect chain health/multimodality and residual assumptions, and lock production settings after evidence-based review.
6. **C/N release gate and joint-likelihood pilot:** once observational and surrogate stock definitions match, validate site-level C/N observations and log-space surrogate uncertainty; enable C/N lognormal terms and compare the full and flux-only posterior.
7. **Nine-site production and sensitivity analysis:** run independent posteriors for eligible sites, including the fixed C/N CV sensitivity cases where enabled; produce per-site diagnostics, posterior-predictive checks, provenance, and summaries. Full ELM verification of representative posterior vectors may be a separately budgeted step.
8. **Review/integration:** test backward compatibility, scientific assumptions, reproducibility, and diagnostics; merge the approved implementation into the agreed integration branch.

These are **suggested phases**, not automatically approved numbered iterations. Detailed implementation tactics, Slurm configurations, resources, and gates are agreed at each kickoff. Do not create active iteration records before approval.

### 7.3 Development records

Mirror the existing surrogate development conventions: `README.md`, `PLAN.md`, `WORKFLOW.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, and folders for `iterations/`, `summaries/`, `slurm/`, `tools/`, and `templates/` as needed. Keep reusable optimization science code in `model_ELM/`, not inside this records folder. A small, reproducible **site campaign configuration** should record observation paths, variable/resolution choices, uncertainty assumptions, source hashes, prior metadata, seeds, pool settings, sampling settings, and output destinations.

### 7.4 Multisite future placeholder

Expose a per-site function returning **separate variable log-likelihood contributions** so a later multisite objective can combine them without rewriting inference. **Do not implement** shared-parameter, hierarchical, or site-balanced calibration in the first release. The user favors **equal site importance** if multisite calibration is added; this must become an **explicit, statistically justified combination policy** at that time, because averaging/normalizing site likelihoods changes the standard Bayesian posterior relative to summing independent observations.

---

## Expected outcome and remaining open dependency

A tested, provenance-complete, reproducible, **site-by-site 18-parameter Bayesian optimization system** that starts from a scientific-prior-aware scrambled Sobol search, runs transformed-coordinate `emcee` on the frozen three-stage ELM surrogate, uses fixed observation-plus-surrogate uncertainties, supports independently hourly/daily GPP/SR likelihoods and optional depth-compatible soil C/N lognormal likelihoods, and reports posterior quality, convergence limitations, and scientific fit.

**Only unresolved surrogate-science decision:** the final representation/observation operator for spinup soil C and N at NEON observation depths. The four-variable likelihood specification is settled *conditional on matching definitions*, and the GPP+SR-only implementation can proceed independently. Do not imply that the current spinup model already matches NEON depth-integrated stocks or force it to predict four outputs without a separate decision.
