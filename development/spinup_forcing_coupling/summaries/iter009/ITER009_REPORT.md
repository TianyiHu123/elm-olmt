# Iter009 comprehensive ABBY and JERC sampler-geometry report

## Executive conclusion

Iter009 is **integrity-valid but produces no geometry-qualified arm and no posterior that is
certified converged under the predeclared rule**.
All 30 chains completed with the locked physical posterior, three seeds per site-arm, 64 walkers,
8,000 steps, finite in-bounds physical states, dual-coordinate archives, HDF checkpoints, and
verified provenance. The scientific decision is nevertheless unambiguous: every arm fails at
least one immutable geometry criterion, so the selection rule permits no least-bad winner.

The five arms do not fail in the same way:

- **B (physical, uniform, StretchMove)** is poor at both sites: low acceptance, unstable and long
  tau, low steps-per-tau coverage, high split R-hat, terminal bands, and large cross-seed distance.
- **T (transformed, uniform, StretchMove)** does not repair B. It is worse on acceptance and
  R-hat, especially at JERC, and transformed-coordinate saturation shows that uniform physical
  initialization maps some walkers very near transformed boundaries.
- **I (physical, high-likelihood, StretchMove)** fixes acceptance and cross-seed marginal
  agreement at both sites. JERC approaches adequate tau coverage, but both sites retain split
  R-hat and terminal-band failures. Initialization is therefore important, but insufficient.
- **M (physical, uniform, DE mixture)** improves tau behavior relative to B, especially at ABBY,
  but retains acceptance heterogeneity, high R-hat, a positive terminal-screen result, and large
  seed disagreement. Proposal choice helps local movement without establishing global mixing.
- **TIM (transformed, high-likelihood, DE mixture)** is the only arm with stable tau, adequate
  steps per tau, split R-hat <=1.05, no low-acceptance walker subgroup, and small cross-seed
  Wasserstein distance at both sites. `TIM/JERC` also passes the mean-acceptance criterion.
  However, all six TIM chains trigger the deterministic terminal two-means screen. `TIM/ABBY`
  additionally has mean acceptance only about 0.147 and marked transformed-coordinate saturation.

The immutable route is therefore
`investigate_multimodality_nonidentifiability_likelihood_or_model_structure`. The result does
**not** say that TIM is a valid posterior sampler, but the screen also does **not** prove two
posterior modes. It always divides the 64 terminal walker medians into two groups and does not test
one cluster against two. The concentrated, mostly unimodal TIM corner plots are therefore relevant
counterevidence: a continuous ridge, a broad unimodal distribution, higher-dimensional weak
identifiability, or an over-sensitive screen remain plausible. The combined intervention removes
most other failures; the immediate task is to validate the terminal-screen interpretation using
the existing raw chains before extending the run or changing the likelihood.

## 1. Scope, arms, evidence, and status vocabulary

### 1.1 Locked experiment

| Item | Locked value |
| --- | --- |
| Sites | ABBY and JERC, evaluated separately |
| Physical posterior | Same coupled `drop21_corr080` SR posterior, observations, priors, bounds, and IID Gaussian likelihood as Iter008 |
| Matrix | B, T, I, M, TIM x ABBY/JERC x seeds 9009, 9010, 9011 |
| Per chain | 64 walkers x 8,000 steps x 15 dimensions; 16 workers |
| Checkpoints | 2,000, 4,000, 6,000, and 8,000 steps |
| B | physical coordinates; uniform initialization; `StretchMove(a=2)` |
| T | transformed coordinates; uniform initialization; `StretchMove(a=2)` |
| I | physical coordinates; high-likelihood initialization; `StretchMove(a=2)` |
| M | physical coordinates; uniform initialization; 80% `DEMove` + 20% `DESnookerMove` |
| TIM | transformed coordinates; high-likelihood initialization; 80% `DEMove` + 20% `DESnookerMove` |
| Selection exclusions | likelihood, MAP, RMSE, R2, KGE, and predictive skill cannot select an arm |

Every metric below is computed in physical posterior coordinates unless explicitly labeled as a
transformed-coordinate saturation diagnostic. The full machine-readable decision is in
[decision.json](decision.json); the compact matrices are in
[qualification_matrix.csv](qualification_matrix.csv) and
[worst_case_selection.csv](worst_case_selection.csv). Large per-arm traces, marginals, tau
trajectories, and decision packages remain under the external Iter009 validation directory.

### 1.2 How to read the classifications

- **Pass:** the metric meets the predeclared threshold for all required seeds/parameters.
- **Partial:** the intervention improves the metric materially but does not meet the full gate.
- **Fail:** the metric violates the immutable threshold.
- **Report-only:** useful evidence that was deliberately excluded from qualification.
- **Not established:** the metric cannot support convergence because another prerequisite fails.

Integrity acceptance and geometry qualification are separate. Iter009 passes technical integrity;
it does not pass scientific geometry qualification. A stable tau or a good marginal R-hat cannot
override a predeclared terminal-screen failure, and thinning cannot manufacture independent
information. Conversely, that screen alone cannot establish multimodality.

## 2. Immutable diagnostic criteria and their meaning

| Diagnostic | Immutable criterion | What a pass supports | What a failure implies |
| --- | --- | --- | --- |
| Mean acceptance | 0.20-0.50 for every chain | Proposals move neither too rarely nor trivially | Poor proposal scale/geometry, boundary rejection, or mode trapping; it does not identify which cause alone |
| Low-acceptance walkers | At most 6/64 below 0.10 per chain | No substantial stuck-walker subgroup | Heterogeneous exploration; some walkers are effectively trapped even if the mean appears acceptable |
| Finite tau | All 15 physical parameters, all chains | Autocorrelation estimation returned a usable finite value | Run/mixing is too weak even for the declared tau screen |
| Tau stability | Relative change from 6,000 to 8,000 steps <=20% for every parameter/seed | The estimated correlation scale is no longer changing rapidly | Run length or stationarity is insufficient; an ESS derived from tau is not trustworthy |
| Steps per tau | `8000/tau >= 20` for every parameter/seed | At least minimal repeated traversal on the estimated correlation scale | Too few autocorrelation lengths; 20 is only a pilot threshold, not proof of convergence |
| Rank-normalized split R-hat | <=1.05 for every physical parameter and log probability | Split seed/trace distributions are broadly compatible | Drift, seed dependence, or multimodality remains; ensemble-walker interaction makes this a screening statistic |
| Terminal two-means screen | No forced partition with >=7 walkers in each group and silhouette >=0.5 | The predeclared one-dimensional terminal screen does not identify a large two-group partition | The deterministic screen is positive; this is a routing warning, not proof of bimodality or non-overlap |
| Cross-seed Wasserstein distance | <=5% of physical prior width for every parameter | Independent seeds have compatible one-dimensional marginals | Initialization/mode selection materially changes posterior location |
| Boundary/saturation | Report-only | Helps localize transformed-bound or prior-edge behavior | Cannot fail an arm by itself, but explains rejection or apparent mode structure |

Nominal unthinned ESS is algebraically tied to chain length and tau. Because emcee walkers interact,
and because unresolved terminal structure can invalidate a single-stationary-distribution
assumption, it is reported only as supporting scale evidence. It is not an independent
qualification gate.

### 2.1 Limitation of the terminal screen and existing plots

For each chain, the validator takes the median **physical** log posterior of every walker over the
last 1,000 steps, then runs deterministic one-dimensional two-means initialized at the minimum and
maximum. It records the smaller group size and a silhouette-like separation score. Because the
algorithm always asks for two groups, a broad unimodal sample can yield a balanced split and a
moderate score. It does not compute a density valley, compare one versus two clusters, quantify a
Bayes/information criterion, or test separation in physical parameter space.

The existing leaf `log_prob_trace.png` files are not direct visualizations of this gate: they show
only the first eight walkers and use the sampler-space log posterior. The existing corner plots use
postprocessed draws and generally show concentrated, unimodal one- and two-parameter projections
for TIM. A real mode split could still be hidden in a higher-dimensional combination, but the
corner plots mean that distinct parameter modes are **not established**. The complete
`raw_chain.npz` and HDF outputs contain all 64 physical trajectories and physical log posterior
values needed for a decisive group-colored reanalysis; no new MCMC run is needed.

## 3. Global qualification matrix

| Arm | Site | Mean acceptance by seed | Max low-accept walkers | Worst tau | Min steps/tau | Max split R-hat | Max seed distance / prior width | Qualified |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| B | ABBY | 0.144 / 0.142 / 0.196 | 14 | 1134.6 | 7.05 | 2.665 | 0.777 | No |
| B | JERC | 0.058 / 0.137 / 0.130 | 63 | 1086.1 | 7.37 | 4.585 | 0.422 | No |
| T | ABBY | 0.083 / 0.212 / 0.130 | 47 | 987.5 | 8.10 | 3.712 | 0.503 | No |
| T | JERC | 0.027 / 0.046 / 0.062 | 64 | 1012.3 | 7.90 | 5.453 | 0.379 | No |
| I | ABBY | 0.225 / 0.229 / 0.231 | 0 | 1112.9 | 7.19 | 1.743 | 0.0213 | No |
| I | JERC | 0.250 / 0.259 / 0.263 | 0 | 415.6 | 19.25 | 1.171 | 0.00841 | No |
| M | ABBY | 0.141 / 0.225 / 0.159 | 9 | 733.5 | 10.91 | 1.480 | 0.441 | No |
| M | JERC | 0.171 / 0.158 / 0.263 | 12 | 703.6 | 11.37 | 1.379 | 0.478 | No |
| TIM | ABBY | 0.148 / 0.146 / 0.147 | 0 | 386.3 | 20.71 | 1.032 | 0.000713 | No |
| TIM | JERC | 0.251 / 0.245 / 0.249 | 0 | 150.2 | 53.25 | 1.021 | 0.00260 | No |

All arms returned finite tau. The table uses the worst parameter/seed for tau, steps/tau, R-hat,
and seed distance because qualification required every parameter and seed to pass.

### 3.1 Exact criterion failures by site-arm

Counts are out of 15 physical parameters except acceptance and terminal-band counts, which are out
of three seeds. `Tau delta` counts parameters whose worst 6k-to-8k relative change exceeds 20%;
`coverage` counts parameters whose worst `8000/tau` is below 20.

| Arm/site | Acceptance seeds failing | Max low walkers | Tau delta failures | Coverage failures | R-hat failures | Wasserstein failures | Terminal-band seed failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B/ABBY | 3 | 14 | 14 | 15 | 15 | 14 | 2 |
| B/JERC | 3 | 63 | 15 | 14 | 15 | 14 | 1 |
| T/ABBY | 2 | 47 | 13 | 11 | 15 | 14 | 2 |
| T/JERC | 3 | 64 | 15 | 15 | 15 | 14 | 0 |
| I/ABBY | 0 | 0 | 15 | 15 | 14 | 0 | 3 |
| I/JERC | 0 | 0 | 2 | 2 | 15 | 0 | 2 |
| M/ABBY | 2 | 9 | 0 | 11 | 15 | 12 | 1 |
| M/JERC | 2 | 12 | 6 | 12 | 15 | 13 | 1 |
| TIM/ABBY | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| TIM/JERC | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

This failure topology is central to the conclusion. B and T fail nearly everywhere. I and M each
repair a different subset. TIM repairs every numerical marginal/serial screen at JERC and all but
mean acceptance at ABBY, yet the terminal two-means screen is positive at both sites. This is the
formal reason TIM does not qualify, not by itself evidence of two physical posterior modes.

## 4. Arm-by-arm diagnostic interpretation

### 4.1 B — physical coordinates, uniform initialization, StretchMove

**ABBY.** No seed reaches mean acceptance 0.20; up to 14 walkers fall below 0.10. Worst tau is
1134.6, so the worst parameter spans only 7.05 tau. Fourteen parameters fail tau stability, all 15
fail coverage and R-hat, and 14 fail cross-seed distance. Two seeds finish in qualifying terminal
bands, including partitions as large as 30 walkers with silhouette near 1.0.

**JERC.** The result is worse: mean acceptance is 0.058-0.137, as many as 63 walkers are below
0.10, worst tau is 1086.1, all 15 parameters fail tau stability and R-hat, and 14 fail seed
distance. One seed has a qualifying 8-walker terminal subgroup; the other two have only one walker
in the smaller band and therefore miss the hard band-size threshold, but this does not repair the
other failures.

**Implication.** B reproduces and strengthens the Iter008 sampler-limited diagnosis. Uniform
physical initialization plus the default stretch proposal does not reliably enter a common
stationary region by 8,000 steps. B provides the baseline against which the other interventions
must be interpreted; it is not a viable candidate for simple run-length extension.

### 4.2 T — transformed coordinates, uniform initialization, StretchMove

**ABBY.** Only one seed reaches target mean acceptance; up to 47 walkers are below 0.10. Thirteen
parameters fail tau stability, 11 fail coverage, all 15 fail R-hat, and 14 fail seed distance.
Two seeds have qualifying terminal bands. Eight transformed parameters spend nonzero mass at
absolute sampler coordinate >=10; the worst fraction is 0.817 and the maximum magnitude is 39.3.

**JERC.** All seed means are extremely low (0.027-0.062), with 51-64 low-acceptance walkers.
Every parameter fails tau stability, coverage, and R-hat; 14 fail seed distance. The terminal-band
gate happens to pass because the smaller groups contain fewer than seven walkers, not because the
ensemble otherwise mixes. Two transformed parameters show saturation, with a worst fraction 0.140.

**Implication.** Coordinate transformation alone is declined. It does not make uniform physical
initialization benign; it maps near-bound states to extreme sampler coordinates and leaves the
StretchMove operating across highly separated scales. The result does not show that transformation
is intrinsically harmful, because TIM demonstrates that it works much better when paired with
high-likelihood initialization and DE moves. It shows a strong interaction among transformation,
initialization, and proposal.

### 4.3 I — physical coordinates, high-likelihood initialization, StretchMove

**ABBY.** All three seeds have target acceptance around 0.225-0.231 and no low-acceptance walkers.
Cross-seed distance passes for all parameters (worst 0.0213). Nevertheless, all 15 parameters fail
tau stability and coverage, 14 fail R-hat, and all three seeds retain large terminal partitions of
20-30 walkers. Worst tau remains 1112.9.

**JERC.** Acceptance is good (0.250-0.263), no walkers are below 0.10, and all Wasserstein screens
pass (worst 0.00841). This is much better than B/JERC. Only two parameters fail tau stability and
coverage, but all 15 fail R-hat, and two seeds have large terminal bands. Worst coverage is 19.25,
just below the threshold.

**Implication.** High-likelihood initialization is strongly supported as a necessary intervention:
it fixes proposal acceptance and one-dimensional seed agreement at both sites. It does not prove
convergence. Compatible marginals combined with high R-hat and a positive terminal screen can arise
from drift, a continuous ridge, higher-dimensional weak identifiability, or distinct modes; these
possibilities are not resolved here. At ABBY, long and unstable tau remains a first-order
limitation regardless of the terminal-screen interpretation.

### 4.4 M — physical coordinates, uniform initialization, DE mixture

**ABBY.** The maximum 6k-to-8k tau change is 0.193, so tau stability passes all parameters, and
worst tau falls to 733.5. Yet two seed means miss acceptance, up to nine walkers are below 0.10,
11 parameters fail coverage, all 15 fail R-hat, 12 fail seed distance, and one seed retains a
qualifying terminal band.

**JERC.** Only one seed reaches target mean acceptance; up to 12 walkers are below 0.10. Six
parameters fail tau stability, 12 fail coverage, all 15 fail R-hat, 13 fail seed distance, and one
seed has a qualifying terminal band. Worst tau is 703.6.

**Implication.** The DE mixture improves local autocorrelation behavior relative to B, most clearly
at ABBY, but uniform initialization still directs seeds into materially different regions. A lower
or more stable tau within each region does not imply global mixing. Proposal limitation is part of
the Iter008 failure, but proposal replacement alone is declined as a complete explanation.

### 4.5 TIM — transformed coordinates, high-likelihood initialization, DE mixture

**ABBY.** Tau is stable for every parameter; worst tau falls to 386.3 and minimum coverage rises to
20.71. Every physical parameter passes R-hat and cross-seed distance, and no walker is below 0.10.
However, all seed means are only 0.146-0.148, below the acceptance gate, and all three chains end
with 27-31 walkers in the smaller terminal band at silhouette 0.698-0.719. Five transformed
parameters have nonzero saturation; the worst fraction is 0.553 and coordinates reach magnitude
39.3. This is a coherent ensemble that still fails the declared acceptance and terminal-screen
criteria; distinct physical parameter modes are not established by those failures.

**JERC.** Mean acceptance is 0.245-0.251, there are no low-acceptance walkers, all tau changes are
<=0.111, worst tau is 150.2, minimum coverage is 53.25, maximum R-hat is 1.021, and maximum seed
distance is 0.00260. No transformed coordinate reaches the saturation threshold. Despite those
strong metrics, forced two-means produces a nearly balanced terminal partition in every seed:
28-30 walkers in the smaller group with silhouette 0.637-0.668.

**Implication.** TIM is diagnostically the strongest arm. At JERC, all marginal, acceptance,
autocorrelation, run-length, and cross-seed screens pass, while only the forced terminal two-means
screen blocks qualification. The mostly concentrated, unimodal corner plot does not display two
obvious parameter modes. Thus the safe conclusion is narrower: convergence is not certified under
the declared rule, and the terminal partition must be validated in physical joint space before it
is interpreted as non-overlap or multimodality. At ABBY, low acceptance and transformed saturation
remain independent failures even if the terminal partition proves artificial. TIM therefore
supports an interaction among scaling, initialization, and proposal, but does not yet establish
either complete repair or genuine multimodality.

## 5. Cross-arm causal interpretation

| Hypothesis tested by the arm matrix | Evidence | Assessment |
| --- | --- | --- |
| The default physical/uniform/stretch geometry only needs more steps | B remains poor after 8,000 steps with 7-12 worst-case tau and severe seed disagreement | **Declined as the immediate remedy** |
| Scaling/bounds are the primary cause | T fails broadly and shows transformed saturation; TIM improves only with initialization and proposal changes | **Transformation alone declined; interaction supported** |
| Initial placement is the primary cause | I fixes acceptance and seed-distance screens, especially at JERC, but R-hat and terminal bands remain | **Important contributor, not sufficient** |
| StretchMove is the primary cause | M improves tau but not seed agreement or R-hat; TIM improves much further | **Proposal limitation contributes, but is not sufficient alone** |
| Scaling + initialization + proposal jointly repair sampling | TIM passes nearly every criterion, especially at JERC | **Strongly supported as partial repair** |
| A single stationary posterior is sampled | All TIM seeds trigger the terminal screen, but the corner plots are concentrated and the forced split has not been validated | **Not established, not declined** |
| Remaining failure is simple burn-in | TIM/JERC has >53 tau coverage and good marginal diagnostics, but terminal-screen meaning is unresolved | **Long burn-in is not the leading explanation; topology versus screen artifact remains open** |

The conclusion follows the immutable logic rather than a subjective ranking. First, no arm passes
all criteria. Second, the single-factor arms I and M repair different failures, establishing that
both initialization and proposal matter. Third, TIM combines those repairs and yields highly
consistent seed marginals, stable tau, and low R-hat. Fourth, the terminal two-means screen still
fails in every TIM chain. Under the immutable decision rule, that is sufficient to withhold
selection and route toward posterior topology, identifiability, likelihood continuity, or model
structure. Scientifically, however, forced two-means is not direct evidence of non-overlap. The
corner plots motivate first testing whether the partition is real. Selecting TIM as a production
sampler now would violate the declared no-least-bad rule; diagnosing TIM as definitively multimodal
would overstate the evidence in the opposite direction.

## 6. What Iter009 establishes—and what it does not

### Established

- The full 30-chain campaign is technically complete and provenance-valid.
- Iter008's default geometry is not repaired by doubling run length from 4,000 to 8,000 alone.
- High-likelihood initialization materially improves acceptance and seed agreement.
- DE moves materially improve tau behavior; their benefit is strongest when paired with the
  transformed coordinates and high-likelihood initialization.
- TIM/JERC reaches strong conventional marginal diagnostics but triggers the replicated terminal
  two-means screen. Whether this represents topology, a ridge, or a forced-partition artifact is
  now the next limiting question.
- ABBY remains harder: even TIM has low mean acceptance and transformed-bound saturation.

### Not established

- No arm is geometry-qualified; convergence is not certified under the declared rule.
- TIM is not selected for production inference.
- The forced terminal groups are not proven to be scientifically distinct posterior modes. They
  could reflect a broad unimodal distribution, non-identifiable ridge, higher-dimensional
  structure, likelihood discontinuity, persistent walker families, or screen artifact.
- Parameter means, intervals, ESS, or posterior predictive uncertainty are not validated.
- Iter009 does not test likelihood adequacy, residual autocorrelation, predictive skill, or joint
  ABBY/JERC calibration.
- Better likelihood values or skill from any arm cannot override the geometry decision.

## 7. Recommended next experiments

These are proposals, not execution authorization. Each experiment should retain multiple seeds,
unthinned chains, physical-coordinate diagnostics, and exact provenance. Posterior-defining inputs
must stay fixed unless changing one is the explicit experimental variable.

### Implementation specification — reproducible new-site high-posterior initialization

#### Why a replacement is required

Iter009 could construct its high-likelihood pools because ABBY and JERC already had checksum-locked
Iter008 raw chains. The initializer read each chain's final half, retained finite strictly in-bound
unique states, selected the top physical-posterior decile, required at least 640 candidates, and
used seeded maximin selection to produce each 64-walker ensemble. A genuinely new site has no such
source chain. Requiring a prior iteration would make TIM non-repeatable as a first-site workflow
and would encourage an arbitrary preliminary MCMC run to become an undeclared dependency.

The replacement should be called an **initialization-search pilot**, not preflight. Preflight must
remain a cheap technical check of data, target equivalence, transformations, dependencies, and
short sampler execution. The search pilot is a separate non-inferential work unit whose sole
product is a diverse, site-specific high-physical-posterior pool. Production TIM still needs its
own burn-in after starting from that pool.

#### Required three-stage lifecycle

| Stage | Purpose | Allowed methods | May contribute posterior draws? |
| --- | --- | --- | --- |
| Technical preflight | Verify new-site data/collocation, likelihood, bounds, transform/Jacobian, surrogate calls, and short HDF continuation | Tiny deterministic evaluations and a few sampler steps | No |
| Initialization-search pilot | Locate and represent diverse high-physical-posterior regions for this site | Space-filling search, multi-start optimization, annealed/tempered exploration, short scouting chains | No |
| Production TIM | Sample with transformed coordinates, high-posterior initialization, and the locked DE mixture | Final declared sampler and target only | Yes, but only after separately diagnosed burn-in and convergence |

The search pilot and production burn-in solve different problems. The pilot asks where plausible
regions are and ensures that the initial ensemble covers them. Burn-in asks whether the final
production kernel forgets those selected starting states. A longer burn-in cannot reliably find a
narrow region that no walker reaches, rescue walkers rejected near transformed boundaries, or
guarantee traversal among disconnected regions. Conversely, starting in a high-posterior pool
does not make those states posterior samples and cannot eliminate the need for burn-in.

#### Candidate-generation algorithm

Implement a deterministic new-site pool builder with the following default sequence:

1. **Lock the target.** Hash the forcing and spinup surrogates, new-site observations and case
   inputs, valid-time mask/window, parameter names/order, physical bounds and priors, likelihood
   definition, fitted-error configuration, and transformation implementation. Any change to these
   items invalidates the pool.
2. **Generate broad site-independent starts.** By default, draw 8,192 scrambled Sobol states in
   normalized physical-prior coordinates with a recorded scramble seed and map them strictly inside
   the physical bounds. If the later high-posterior filter yields fewer than 640 unique states,
   extend the same Sobol sequence deterministically to 16,384, 32,768, and at most 65,536 states.
   Reaching that cap without a valid pool is a failed initialization search, not permission to
   change the target or threshold.
3. **Evaluate the new-site physical posterior.** Store physical log likelihood, log prior, and
   physical log posterior separately. Never rank candidates by the transformed sampler target,
   because that includes the coordinate Jacobian and can change the initialization ranking.
4. **Refine multiple regions.** Select a predeclared number of dispersed high-ranking anchors in
   normalized physical space, not simply the top adjacent rows. From every anchor, run the same
   locked local optimizer or short annealed/tempered scouting kernel with a common evaluation
   budget. Retain complete trajectories or particles, not only optimizer endpoints, so the pool
   contains local spread. The anchor count, evaluation budget, seeds, and stopping rules belong in
   the search contract and cannot be chosen after seeing the candidate topology.
5. **Treat prior-site states only as optional proposals.** ABBY/JERC states may be added as extra
   anchors, but they must be reevaluated under the new site's physical posterior and cannot be
   required for success. The manifest must distinguish broad new-site starts from transferred
   proposals and report whether transferred states survive selection.
6. **Filter reproducibly.** Require finite, strictly in-bound, exact-unique physical states. Apply a
   predeclared high-posterior rule, such as the upper decile used in Iter009, with a predeclared
   expansion rule if fewer than 640 states remain. Do not tighten the cutoff to favor a visually
   attractive basin. Record every rejected row and reason.
7. **Test topology before bundling.** Normalize by physical prior width and assess whether the pool
   contains multiple clusters, connected ridges, or one region. Use clustering only to preserve
   diversity, not to declare posterior modes. Report cluster sensitivity, occupancy, pairwise
   distances, physical-space rank, condition number, and per-parameter spread.
8. **Construct independent production ensembles.** Allocate each 64-walker bundle across every
   supported pool stratum, then use a distinct recorded maximin seed within strata. Each bundle
   must contain 64 unique, strictly in-bound rows, full 15-dimensional rank, acceptable condition
   number, and nonzero spread in every parameter. Bundles for different production seeds must not
   be identical.
9. **Freeze before production.** Hash the pool, candidate ledger, diagnostics, and every initial
   bundle. Production launchers must verify those hashes and must never regenerate or overwrite a
   pool implicitly.

An annealed sequential Monte Carlo search is the preferred future implementation when feasible,
because it starts from the prior, adapts through intermediate temperatures, and can preserve
several regions more naturally than one short MCMC chain. A simpler multi-start space-filling plus
local-refinement builder is an acceptable first implementation if it preserves the same provenance,
diversity, and target-lock requirements. A single short ordinary ensemble chain is not sufficient
as the sole pool generator unless independent evidence shows it traversed all relevant regions.

#### Required artifacts and schemas

The initialization-search work unit should produce at least:

- `search_contract.json`: target hashes, site/window, schema/order, bounds/priors, transformation,
  candidate generator, algorithms, all seeds, thresholds, expansion rules, and stopping rules;
- `candidate_ledger.npz` plus metadata: every physical candidate, normalized coordinate, source
  method/index, log likelihood, log prior, physical log posterior, and rejection status/reason;
- `high_posterior_pool.npz`: selected physical states, physical-posterior components, source rows,
  diversity/stratum labels, and parameter metadata;
- `high_posterior_pool.json`: checksums, counts through every filter, cutoff, rank, condition number,
  per-parameter spread, topology-sensitivity results, and transferred-anchor accounting;
- `initial_state_seedNNNN.npz/json`: the exact 64 physical states, source pool indices/strata,
  maximin seed/distances, validation results, and bundle checksum; and
- `initialization_search_report.md`: human-readable coverage plots, physical-posterior distribution,
  cluster/ridge sensitivity, prior-edge occupancy, and explicit limitations.

The existing `--initial-state` interface already accepts a physical `(64, 15)` NPZ bundle, so the
new implementation should change pool construction rather than the production TIM target. The
production transform must continue to convert those physical states internally and include the
Jacobian only in sampler-space evaluation.

#### Hard initialization gates

Before any production TIM submission, require:

- exact target/dependency identity and physical-versus-transformed target-equivalence tests;
- a complete candidate ledger with deterministic regeneration metadata;
- at least 640 unique finite strictly in-bound selected pool states;
- nonzero spread in all 15 physical dimensions;
- full-rank pool and every 64-walker bundle, with the declared condition-number ceiling;
- demonstrated representation of every robust pool stratum, or an explicit finding that only one
  connected region is supported;
- three nonidentical seed-specific bundles with exact source indices and hashes; and
- independent review that the pilot output is initialization evidence only, not posterior or
  convergence evidence.

Fail closed if broad search and refinement cannot produce a sufficiently diverse pool. Do not
silently compensate by lowering a threshold, copying a previous site's bundle, duplicating/jittering
one optimum, or labeling optimization trajectories as posterior samples.

#### Production burn-in and validation after pool generation

Production TIM must still retain its full unthinned trajectory and diagnose sensitivity to the
pool. Burn-in should be determined from trace/region stability rather than set equal to the search
pilot length. Compare the three seed-specific ensembles for acceptance, low-acceptance walkers,
tau stability, rank-normalized split R-hat, physical-space overlap, and any robust region weights.
If all seeds agree only because every bundle came from one narrow pool stratum, that is not
successful convergence. If distinct initial strata converge to compatible distributions and, when
applicable, compatible region weights, the high-posterior initialization has served its purpose
without dictating the result.

### Experiment 1 — validate the terminal-screen partition using existing outputs

**Purpose:** determine whether forced two-means found genuine posterior modes, a persistent ridge,
walker-family structure, a broad unimodal distribution, or a diagnostic artifact.

**Design:** use the existing TIM `raw_chain.npz` and HDF outputs without new sampling. Produce:

1. all-64-walker **physical** log-posterior traces colored by terminal assignment;
2. sorted terminal medians, rug/density plots, the forced threshold, and the observed density gap;
3. corner plots colored by terminal assignment using identical raw post-burn draws;
4. per-parameter standardized group differences and multivariate classifiers;
5. PCA or another declared physical-space projection colored by group;
6. rolling-window assignments, transition counts, and residence times; and
7. one-cluster-versus-two-cluster comparisons and sensitivity to terminal window length.

Then compare physical parameters, log prior, log likelihood, `sigma_SR`, boundary occupancy, and
predicted SR between groups and across seeds. Do not call the group weights posterior mode weights
unless independent evidence supports genuine modes.

**Expected result:** true modes show a density valley, stable multivariate parameter/prediction
differences, long residence times, few transitions, and reproducible locations across seeds. A
ridge shows continuous physical paths and similar likelihood across a correlated manifold. A broad
unimodal distribution shows overlapping colored corners/PCA and no stable density gap. A diagnostic
artifact changes or disappears under one-versus-two-cluster tests or alternative terminal windows.

**Proves/declines:** reproducible separated physical basins support multimodality. Continuous
connectivity supports non-identifiability/ridges. Overlapping joint structure and no robust gap
decline the modal interpretation and justify revising the screen before any new sampler experiment.

### Experiment 2 — tempered mode-bridging pilot

**Purpose:** only if Experiment 1 validates distinct basins, test whether energy barriers rather
than local proposal efficiency prevent TIM from moving between them.

**Design:** condition this experiment on robust mode evidence. Keep the exact physical posterior
and transformed parameterization, but compare TIM against a small parallel-tempering/
replica-exchange or sequential-tempering pilot. Use multiple
temperatures selected from measured log-probability separation, record swap acceptance and
round-trip counts, and retain three seeds per site. Compare cold-chain band transitions, mode
weights, R-hat, tau stability, and cross-seed distances. Do not select by best likelihood.

**Expected result:** if barriers are responsible, tempered chains make repeated cold-chain mode
transitions, reproduce mode weights across seeds, and eliminate terminal band separation without
damaging other TIM metrics.

**Proves/declines:** successful round trips and stable cold-chain weights support multimodality with
an addressable barrier. Persisting separation despite adequate temperature exchange shifts weight
toward disconnected support, numerical discontinuity, or structural non-identifiability.

### Experiment 3 — likelihood continuity and boundary-path audit

**Purpose:** if robust physical groups or ridges are found, identify discontinuities or narrow
invalid regions that create artificial barriers, especially at ABBY.

**Design:** interpolate and adaptively refine paths between representative terminal-band states in
both physical and transformed coordinates. Decompose total log posterior into prior, likelihood,
and numerical-validity components. Record surrogate inputs/outputs, bound distances, invalid
predictions, clipping, missing-data masks, and finite-to-`-inf` transitions. Repeat with paths along
dominant covariance/ridge directions.

**Expected result:** a smooth scientific barrier produces continuous likelihood valleys. Abrupt
jumps tied to clipping, validity masks, bounds, or surrogate behavior identify an implementation or
model-interface discontinuity.

**Proves/declines:** reproducible numerical jumps support a likelihood/interface defect and should
be corrected before further MCMC. Smooth paths with persistent barriers decline that explanation
and support genuine posterior topology.

### Experiment 4 — identifiability and parameter-reduction experiment

**Purpose:** test whether SR alone can identify 14 process parameters plus `sigma_SR`.

**Design:** if Experiment 1 validates physical groups, use group-specific TIM draws; otherwise use
the complete TIM posterior geometry. Compute correlation structure, local rank, profile
likelihoods, and weakly constrained parameter combinations. Compare the full model with one
scientifically justified reduced model that fixes or groups weakly identified `rf_*` directions.
Keep data, likelihood, and sampler otherwise fixed. Evaluate mode count, band transitions, seed
agreement, held-out prediction, and whether reduced-model posteriors become unimodal.

**Expected result:** if over-parameterization drives the split, a reduced model preserves predictive
behavior while improving rank, mode overlap, R-hat, tau, and seed stability.

**Proves/declines:** improved topology with equivalent prediction supports non-identifiability in
the full parameterization. Persistent modes in both models decline parameter count as the primary
cause.

### Experiment 5 — ABBY transformed-bound and proposal-scale pilot

**Purpose:** isolate why TIM/ABBY has stable tau and seed agreement but sub-target acceptance and
strong transformed-coordinate saturation.

**Design:** after the topology audit, compare the current transform with scientifically equivalent
softened numerical transforms or boundary-aware proposals; alternatively tune the DE scale using a
predeclared small grid. Preserve the exact physical prior and include the correct Jacobian. Use
three seeds, record per-parameter rejection/boundary causes, and require target equivalence tests.

**Expected result:** if extreme transformed coordinates cause ABBY's rejection, saturation and
boundary-linked rejection fall, mean acceptance enters 0.20-0.50, and physical posterior summaries
remain invariant.

**Proves/declines:** improvement without physical-posterior change supports a numerical geometry
cause. Persistent low acceptance after boundary-aware movement shifts focus to ABBY likelihood or
model structure. This experiment cannot by itself resolve the terminal-screen ambiguity.

### Experiment 6 — convergence-length confirmation after terminal-screen resolution

**Purpose:** establish convergence only after the terminal screen is either validated and repaired,
or shown to be a false/over-sensitive partition and replaced with a justified diagnostic.

**Design:** continue only a method that passes the revised topology/overlap assessment. Set length
from stable pilot tau, require at least 50 tau after burn-in and preferably 100, retain at least
three independent seeds, and report bulk/tail ESS, Monte Carlo standard error, rank-normalized
split R-hat, transition/region-weight metrics when genuine regions exist, and posterior predictive
stability.

**Expected result:** stable tau and, where applicable, region weights and repeated transitions;
R-hat <=1.01-1.05; adequate bulk/tail ESS; and seed-invariant intervals/predictions.

**Proves/declines:** success establishes a usable sampler for the locked posterior. Continued band
separation or seed-dependent weights after 50-100 tau declines a simple run-length remedy.

### Experiment 7 — temporal likelihood comparison, then ABBY model/data audit

**Purpose:** revisit Iter008's strong scientific warning—residual lag-1 correlations above 0.99 and
ABBY error-scale saturation—only after posterior topology is controlled.

**Design:** compare the IID Gaussian likelihood with a predeclared temporally aware alternative
(for example AR(1)), block/daily information reduction, and optionally robust innovations. Keep the
sampler that passes the revised overlap assessment fixed. In parallel, audit ABBY observation timing/QC, units, forcing
collocation, surrogate-domain coverage, and regime-specific residuals.

**Expected result:** a better likelihood reduces multi-lag residual dependence and stabilizes
posterior/mode behavior without sacrificing held-out prediction. A clean audit with persistent ABBY
bias instead supports a site-specific structural limitation.

**Proves/declines:** likelihood improvement supports misspecification as a scientific cause.
Persistent residual structure and ABBY bias under healthy sampling support model/data limitation.

## 8. Recommended sequence and decision gates

1. Validate or decline the forced terminal partition using existing outputs (Experiment 1); no new
   MCMC is needed.
2. If distinct groups or a ridge are supported, run the likelihood-continuity/boundary-path audit
   (Experiment 3).
3. Only if reproducible modes are established, test tempered bridging (Experiment 2).
4. If a ridge/non-identifiability dominates, test justified parameter reduction (Experiment 4).
5. Address ABBY transformed saturation with target-equivalent proposal/transform tests
   (Experiment 5).
6. Run convergence-length confirmation only after the terminal screen is resolved and, if genuine
   modes exist, repeated movement among them is demonstrated (Experiment 6).
7. Then test temporal likelihoods and ABBY-specific model/data causes (Experiment 7).

For any genuinely new site, the new-site initialization-search specification above is a required
pre-production branch: technical preflight -> initialization-search pilot -> frozen bundles ->
production TIM and independent burn-in. It does not require or assume a previous-site posterior.

The immediate go/no-go question is whether the terminal partition is a reproducible feature of the
physical posterior at all. If it is, require movement among all supported regions and stable mode
weights across seeds. If it is not, revise the terminal criterion and reassess TIM/JERC against the
remaining diagnostics. In either case, preserve the physical posterior and do not use a better
point fit as a substitute for validation.

## 9. Final answers

- **Did Iter009 execute correctly?** Yes. Thirty final chains and ten validation packages pass
  integrity, completeness, provenance, shape, finiteness, and bounds checks.
- **Did any arm qualify?** No. Every arm fails at least one immutable geometry criterion.
- **Which intervention helped most?** The combined TIM intervention. It passes all numerical
  marginal/serial criteria at JERC and all except mean acceptance at ABBY, but it is not selected.
- **Why is TIM not selected?** All six TIM chains trigger the immutable terminal two-means gate;
  TIM/ABBY also fails mean acceptance. The gate outcome is binding, although its scientific
  interpretation as distinct modes is not validated.
- **What do the single-factor arms show?** High-likelihood initialization fixes acceptance and seed
  agreement; DE moves improve tau; transformation helps only in interaction with both.
- **What conclusion is justified?** The default sampler limitation is partly repaired. The only
  remaining TIM/JERC gate failure is an unvalidated forced-partition diagnostic. Multimodality,
  non-identifiability, a broad unimodal posterior, likelihood discontinuity, model structure, and
  screen artifact remain competing explanations.
- **What should happen next?** Replot and test the terminal partition from existing raw outputs.
  Use tempered bridging only if distinct modes are established; otherwise revise the screen and
  reassess TIM/JERC. Do not use TIM for inference until that ambiguity is resolved.
- **How should TIM initialize at a new site?** Build a site-specific high-physical-posterior pool
  with the reproducible initialization-search pilot specified above. Do not treat preflight as pool
  generation, require a former iteration, or replace production burn-in with optimization output.
