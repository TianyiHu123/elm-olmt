# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter010`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-12T20:05:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved` (Iter010 initialized under the consolidated package).
- Kickoff goal and stop boundary: complete the six-chain TIM terminal-partition topology diagnosis,
  conditional prediction/skip, terminal accounting, durable records, validation, and one local
  closeout commit.
- User response and approval timestamp: `approved the full package`, `2026-08-12`.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`;
  creation limited to the four Iter010 run directories in the finalized plan.
- Locked dependencies/gates/decision: the exact complete plan below; Iter002 forcing and Iter012
  `drop21_corr080`, ABBY/JERC observations and Iter008 raw chains have the recorded hashes;
  five arms, three seeds, 30 leaves, 64x8000, physical posterior fixed, and immutable integrity
  and geometry-qualification rules.
- Outside-sandbox and closeout authorities: locked `sbatch`; job-scoped monitoring/accounting;
  bounded cancellation of recorded Iter010 jobs; one bounded local closeout commit after validation.
- Iter010 authority: approved full package. The primary agent may perform the locked preparation,
  independent read-only review, bounded Puma preflight/submission/monitoring/accounting,
  evaluation, durable records, and one local closeout commit within the plan below.

## Current Objective

TIM terminal-partition topology diagnosis

- Iteration ID: `iter010`
- Status: `completed`
- Phase: `closed`
- Objective: determine whether the six Iter009 TIM terminal partitions are reproducible basins,
  a connected ridge, a screen artifact, or inconclusive, separately for ABBY and JERC.
- Bounded scope: six immutable TIM chains; terminal windows 500/1000/2000/4000; rolling and
  late-half diagnostics; five figures per chain and three-seed site syntheses; prediction only
  for a site classified `two_basin_supported`.
- Kickoff approval: exact response `approved the full package`, received 2026-08-12.
- Active job IDs: none; preflight `23554607`, topology `23554935`, prediction `23555136`, and
  finalize `23555187` terminal `COMPLETED 0:0`.
- Overall acceptance result: `pass` for integrity/provenance/evidence completeness.
- Site results: ABBY `two_basin_declined`; JERC `two_basin_declined`; conditional prediction
  `skipped` with zero evaluations.
- Next route: replace the forced screen, reassess TIM/JERC, and propose Experiment 5 for ABBY
  acceptance/saturation.
- Stop reached: terminal accounting, integrity evaluation, topology/convergence decision,
  validated conditional skip, report/routing, durable-record validation, and closeout commit.

## Previous Iter009 Objective

ABBY and JERC sampler-geometry pilot

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Objective: `ABBY and JERC sampler-geometry pilot`
- Bounded scope: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Overall acceptance result: `pass`
- Decision: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
- Next state: `Planning-only Iter010 proposal recorded below; iter010 is not_initialized and requires a fresh consolidated kickoff package and explicit approval.`

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: five-arm sampler-geometry pilot; separate ABBY/JERC; 30 chains; 64x8000;
  three shared seeds; fixed physical posterior; integrity plus geometry routing
- Bounded scope label: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter010`
- Iter008 evidence: integrity-valid chains and paired route `sampler-limited`; all Iter009
  dependencies were re-hashed and match the finalized plan before approval
- Forcing identity: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Acceptance result: `pass` for integrity and provenance. All 30 final campaign leaves and the
  authoritative validation `23540912` completed `0:0`; 30 complete raw-chain/HDF/provenance
  bundles and ten site-arm packages were verified.
- Decision: no geometry-qualified arm. `TIM` is nearest to the overlap screens (ABBY/JERC
  maximum split R-hat 1.0317/1.02137 and cross-seed width fraction 0.000713/0.002603), but it
  still fails the immutable all-criteria rule; no least-bad winner is selected.

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Geometry qualification did not pass for any arm. This is a scientific routing result, not an
  integrity failure; follow-up requires fresh approval.
- The original 42-task cap is exceeded by user-approved exception attempts: two additional
  preflight attempts and two six-leaf B application recoveries make the pre-validation total 46.
  Final integrity accounting must state the exception and cannot represent the original cap as met.

## Next Action

1. Submit and monitor the reviewed Iter010 preflight, then submit topology only after a passing
   terminal preflight and immediate identity check.

## Planning-Only Proposed Iter010 Plan

This proposal records the agreed next experiment. It does not initialize `iter010` and grants no
Python, implementation, directory-creation, compute, scheduler, retry, cancellation, closeout, or
commit authority. A fresh consolidated kickoff package must resolve the closeout commit/no-commit
branch and receive explicit approval before any Iter010 action beyond read-only inspection.

### 1. Sequential ID and work type

- Sequential ID: `iter010`
- Status: `not_initialized`
- Work type: `implementation`
- Objective label: `TIM terminal-partition topology diagnosis`
- Proposed run slugs: `spinup_forcing_coupling_iter010_preflight`,
  `spinup_forcing_coupling_iter010_topology`,
  `spinup_forcing_coupling_iter010_predict`, and
  `spinup_forcing_coupling_iter010_finalize`.

### 2. Evidence-derived objective and hypothesis

Objective: determine whether the deterministic terminal two-means partitions reported for the
six Iter009 `TIM` chains are reproducible separated basins in the physical posterior, a connected
ridge, a broad/unimodal diagnostic artifact, or inconclusive. Evaluate ABBY and JERC separately,
then state the cross-site implication without pooling the two sites.

Evidence basis: `TIM` is the only Iter009 arm with stable tau, adequate steps per tau, split
R-hat at most 1.05, no low-acceptance walker subgroup, and small cross-seed Wasserstein distance
at both sites. `TIM/JERC` also passes mean acceptance. All six chains nevertheless fail the
terminal screen, which always forces two groups from walker median physical log posterior and
does not compare one group against two or establish separation in 15-dimensional physical space.
Existing uncolored physical corner plots appear mostly concentrated and unimodal.

Hypothesis: if the screen found genuine basins, its scalar separation, physical multivariate
separation, temporal persistence, and corresponding group locations will reproduce in all three
seeds for a site. Continuous occupied paths support a ridge; physical overlap or unstable labels
support a screen artifact. The topology conclusion is primary. Existing convergence evidence is
reassessed only after the terminal screen is interpreted.

### 3. Proposed dependencies and trust assumptions

| Dependency | Role | Proposed lock / trust |
| --- | --- | --- |
| Iter009 TIM raw archives | Authoritative topology inputs | Six immutable `raw_chain.npz` files: ABBY/JERC x seeds 9009/9010/9011; preparation must lock paths, SHA-256, schema, shapes, parameter order, bounds, and physical-log-posterior convention |
| Iter009 TIM HDF and metadata | Provenance cross-check | Immutable backend, metadata, hashes, checkpoint manifest, and selection ledger for each chain |
| Iter002 forcing surrogate | Conditional SR prediction | Same released forcing surrogate and identity as Iter009 |
| Iter012 `drop21_corr080` | Conditional coupled spinup | Same released spinup surrogate and identity as Iter009 |
| ABBY/JERC observations and cases | Conditional likelihood/skill interpretation | Same observations, validity masks, cases, site windows, and `SR:SR_err` mapping as Iter009 |
| Physical posterior | Fixed target | Same 14 process parameters, site-specific fitted `sigma_SR`, physical bounds/prior, IID Gaussian likelihood, and transformation/Jacobian convention as Iter009 |
| Puma environment | Runtime | `development/hpc/puma.md`; `chopinsong` / `standard` / `OLMT_puma`; exact environment identity recorded by preflight |

The existing archives already contain the physical posterior. Inside the locked uniform physical
bounds, the physical prior is constant, so groupwise physical likelihood comparisons can be
derived from the archived physical log posterior. New surrogate evaluations are permitted only
for the conditional prediction branch defined below and do not create posterior samples.

### 4. Bounded scope and diagnostic design

#### 4.1 Six-chain matrix and reference assignment

Analyze all six existing `TIM` chains separately:

- ABBY seeds 9009, 9010, and 9011; and
- JERC seeds 9009, 9010, and 9011.

Each chain is 64 walkers x 8,000 steps x 15 physical parameters. The reference assignment remains
the exact Iter009 deterministic two-means screen over each walker's median physical log posterior
during steps 7001--8000. Labels are aligned as lower versus higher median physical log posterior;
arbitrary label swapping is not allowed.

#### 4.2 Time windows and deterministic plotting draws

- Test terminal windows of 500, 1,000, 2,000, and 4,000 steps.
- Use 1,000-step rolling windows with a 250-step stride over steps 4001--8000.
- Compare late-chain halves 4001--6000 and 6001--8000.
- For colored corner and PCA plots, select 32 equally spaced draws per walker from steps
  4001--8000: exactly 2,048 draws per chain, with identical indices for both colors.
- Temporal stability requires at least 90% walker-assignment agreement between the 2,000- and
  4,000-step terminal windows and no more than a 10-percentage-point group-occupancy change
  between the two late-chain halves.

#### 4.3 Required figure package

Produce the following five figures for every chain:

1. all 64 physical-log-posterior traces colored by reference terminal assignment;
2. sorted terminal walker medians with forced threshold, group sizes, rug plot, and density;
3. physical-parameter corner plot colored by terminal assignment;
4. prior-width-normalized PCA projection colored by group and showing intermediate trajectories;
5. rolling assignments, transitions, residence times, and group occupancy through time.

Also produce one three-seed comparison figure for ABBY and one for JERC. Report GMM one-versus-two
BIC, KDE bandwidth sensitivity, multivariate classifier accuracy, standardized parameter-group
differences, assignment agreement, and transition counts as supporting measurements. These are
not independent hard vetoes.

Every new figure's caption and corresponding report text must state: the question answered; exact
construction and source data; coordinates, windows, draw selection, normalization, colors, and
smoothing; how to read the figure; the observed seed/site result; its topology implication; and
what the figure cannot establish alone.

#### 4.4 Simplified topology synthesis rule

For each site, classify evidence for four requirements as `support`, `oppose`, or `ambiguous`:

1. robust scalar physical-log-posterior separation;
2. physical multivariate separation;
3. temporal persistence or discrete transitions; and
4. reproducible corresponding group locations across all three seeds.

Assign exactly one site-level topology result:

- `two_basin_supported`: all four requirements support separated basins in every seed;
- `connected_ridge_supported`: occupied intermediate states and gradual trajectories form a
  reproducible connected manifold without a robust intervening gap;
- `two_basin_declined`: physical groups overlap or terminal assignments are unstable in all
  three seeds; or
- `inconclusive`: diagnostics conflict or any seed materially disagrees.

A general TIM two-basin claim is supported only if both sites are `two_basin_supported`. Otherwise
preserve the separate site findings. Two scalar log-posterior bands alone cannot establish two
physical basins.

#### 4.5 Secondary convergence implication

Topology is the primary Iter010 result. Apply only these downstream labels from existing evidence:

- If the JERC partition is an artifact and all remaining Iter009 criteria still pass, report
  `convergence_supported_under_revised_iter009_diagnostics`.
- If the ABBY partition is an artifact, convergence remains unsupported because its mean
  acceptance still fails the Iter009 criterion; transformed saturation is additional adverse,
  report-only evidence.
- Genuine basins without repeated exchange and stable occupancy imply
  `convergence_not_established_unmixed_basins`.
- A connected ridge supports convergence only if all three seeds consistently explore its full
  occupied extent through time; otherwise state the missing coverage evidence.
- Inconclusive topology implies `convergence_not_established_inconclusive_topology`.

Do not claim mathematical proof of convergence or let this secondary interpretation expand the
experiment into a new convergence-length study.

#### 4.6 Conditional prediction and equifinality branch

Run this branch only for a site classified `two_basin_supported`. For every walker, compute its
median physical parameter vector over steps 4001--8000, normalize distances by physical prior
width, and select the actual observed state in that interval nearest the median vector. Never
evaluate a constructed median state. Preserve site, seed, walker, raw step, group, parameters,
selection distance, and input/output checksums in a ledger.

This yields 192 new coupled-surrogate evaluations when one site supports two basins, 384 when both
do, and a validated `skipped` record when neither does. Compare group distributions of physical
log likelihood per valid observation, RMSE, bias, R2, KGE, group-median predicted SR time series,
and fitted `sigma_SR`.

Classify `equifinal_comparable` only when central 90% intervals overlap for physical log likelihood
per observation and RMSE, neither group consistently dominates both measures in all three seeds,
and qualitative SR time-series behavior is comparable. Otherwise report
`distinct_solutions_unequal_support`. These labels interpret supported basins; they cannot detect
topology, establish posterior basin weights, or certify convergence.

#### 4.7 Exclusions

No new MCMC sampling, continuation, altered burn-in, or resampling; no change to prior, bound,
likelihood, transform/Jacobian, surrogate, observation, fitted-error definition, or site window;
no analysis of B/T/I/M beyond contextual Iter009 summaries; no pooled ABBY/JERC clustering; no
interpolated posterior paths; no tempering, proposal tuning, parameter reduction, or temporal-
likelihood test; no use of skill or best likelihood to determine topology; no interpretation of
terminal occupancy as posterior basin weights without demonstrated exchange; no claim that
thinning establishes independence; and no production-sampler selection from Iter010 alone.

### 5. Tentative hard integrity gates and decision rule

Scientific topology, prediction quality, likelihood, and convergence implications are routing
results, not technical acceptance gates. An integrity pass requires:

- authoritative terminal accounting and classified outcomes for all submitted tasks;
- exact identity, schema, shape `(8000, 64, 15)`, finiteness, parameter order, bounds, site, seed,
  and physical-log-posterior convention for all six source archives;
- deterministic regeneration metadata for every selection, figure, table, and supporting metric;
- complete five-figure packages for all six chains and complete three-seed syntheses for both
  sites;
- application of the immutable simplified topology rule without post-result threshold changes;
- exactly 192 conditional evaluations per supported site, up to 384 total, with a complete ledger
  and finite predictions, or a validated conditional skip record;
- the comprehensive report's required figure descriptions, separate ABBY/JERC conclusions,
  cross-site synthesis, secondary convergence implication, conditional equifinality interpretation,
  limitations, and exactly one routed next experiment; and
- agreement among the iteration report, cumulative summary, registry, handoff, accounting, and
  compact machine-readable decision evidence at closeout.

Missing, mismatched, non-finite, non-reproducible, or incomplete evidence fails closed. No topology
category is intrinsically a failed result.

### 6. Proposed site, resources, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / environment | `chopinsong` / `standard` / `OLMT_puma` |
| Preflight | 2 CPUs / Puma-derived 10 GB / 30 minutes |
| Topology analysis | 4 CPUs / Puma-derived 20 GB / 2 hours |
| Conditional prediction | 4 CPUs / Puma-derived 20 GB / 1 hour; submitted only when at least one site is `two_basin_supported` |
| Finalize/report | 2 CPUs / Puma-derived 10 GB / 1 hour |
| Nominal scheduler count | Three tasks if prediction is skipped; four if triggered |
| Review | Independent read-only agent after preparation and before preflight; primary agent remains sole writer and scheduler operator; re-review after any authorized source correction |
| Retry | One minimal preflight-only correction/rerun; one unchanged scheduler/resource retry for each substantive work unit |
| Hard cap | Eight scheduler tasks including every permitted retry |
| Cancellation | Recorded Iter010 IDs only, and only for a proven universal pre-execution defect affecting the recorded work |
| Stop | After terminal accounting, integrity evaluation, topology decision, secondary convergence interpretation, conditional equifinality branch, comprehensive report, next-experiment routing, durable-record validation, and the kickoff-selected closeout branch |

Application, analysis-code, schema, dependency, numerical, plotting-content, topology-rule, or
conditional-routing failures require fresh approval before correction or rerun. Cancellation does
not authorize a correction or resubmission.

### 7. Proposed output layout, evidence, and next-experiment routing

Proposed external root:
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`.
Use the four proposed run slugs as self-describing run directories. The prediction directory must
contain either complete conditional evidence or an explicit validated `skipped` decision. The six
Iter009 archives and HDF files remain immutable in place and must never be copied over, modified,
or overwritten.

Large figures, intermediate arrays, ledgers, and predictions remain outside Git. Compact evidence
under `summaries/iter010/` must include `ITER010_REPORT.md`, selected conclusion-supporting figures,
the topology/convergence decision JSON, per-chain and per-site topology tables, assignment and
transition summaries, parameter group differences, conditional prediction/equifinality evidence
or skip record, and accounting.

The report selects exactly one planning-only next route:

| Iter010 result | Next proposed experiment |
| --- | --- |
| Reproducible basins | Iter009 Experiment 3 likelihood-continuity/boundary-path audit; tempered bridging follows only if paths are scientifically smooth |
| Connected ridge | Experiment 3 first; then Experiment 4 parameter reduction if numerical discontinuity is declined |
| Artifact at both sites | Replace the forced screen, reassess TIM/JERC, and propose Experiment 5 for ABBY acceptance/saturation |
| Different site outcomes | Follow the unresolved site-specific route without pooling conclusions |
| Inconclusive | Narrow Experiment 3 path/connectivity audit targeting the conflicting directions |

The closeout commit/no-commit branch is intentionally unresolved in this planning record. It must
be selected and explicitly authorized in the complete consolidated kickoff package. No push is
proposed.

### 8. Fresh consolidated kickoff boundary

`iter010` remains `not_initialized`. Before initialization, present one complete consolidated
kickoff package containing this finalized plan, exact locked dependency identities, goal and stop
boundary, output/directory authority, lifecycle and scheduler authorities, resources, retry and
cancellation limits, outside-sandbox submission/monitoring/accounting/cancellation authority, and
an explicit commit or validated-uncommitted closeout branch. Only the user's approval of that
complete package may authorize Iter010 work.

## Finalized Iter009 Plan

- Iteration: `iter009`; plan finalized and approved.
- The complete plan remains identical to the planning-only proposal in `iterations/iter008.md`.
- Authority is exactly the approved consolidated package above; no change to an immutable term is
  authorized.

### 1. Sequential ID and work type

- Sequential ID: `iter009`
- Work type: `implementation`
- Objective label: `ABBY and JERC sampler-geometry pilot`
- Proposed run slugs: `spinup_forcing_coupling_iter009_preflight`,
  `spinup_forcing_coupling_iter009_initialize`,
  `spinup_forcing_coupling_iter009_b_campaign`,
  `spinup_forcing_coupling_iter009_t_campaign`,
  `spinup_forcing_coupling_iter009_i_campaign`,
  `spinup_forcing_coupling_iter009_m_campaign`,
  `spinup_forcing_coupling_iter009_tim_campaign`, and
  `spinup_forcing_coupling_iter009_validate`.

### 2. Evidence-derived objective and hypothesis

Objective: determine whether Iter008's poor mixing is primarily caused by parameter scaling
and bounds, initial walker placement, or the default stretch proposal, while holding the
physical posterior fixed.

Evidence basis: Iter008 completed integrity-valid separate ABBY and JERC chains, but mean
acceptance was 0.178/0.102, maximum autocorrelation time was 508.8/482.7, only about 8--31
autocorrelation times were covered, and terminal walkers remained in separated log-probability
bands. The paired decision was `sampler-limited`; blindly extending the current geometry is not
the first action.

Hypothesis: one or more bounded geometry interventions will consistently improve acceptance,
terminal walker overlap, autocorrelation stability, and cross-seed agreement at both ABBY and
JERC without changing the likelihood, prior, scientific inputs, or physical posterior.

### 3. Proposed dependencies and trust assumptions

| Dependency | Role | Proposed lock / trust |
| --- | --- | --- |
| Preparation base | Repository parent | Clean HEAD `b086a212390af5f198a27799b92d8bc5ce09a321`; execution source will be locked by a reviewed manifest after authorized implementation |
| Iter002 forcing surrogate | Coupled `SR` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 `drop21_corr080` | Coupled spinup state | SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY observations | Likelihood target | NEON v4; SHA-256 `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` |
| JERC observations | Likelihood target | NEON v4; SHA-256 `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` |
| Iter008 ABBY raw chain | High-likelihood initialization source | SHA-256 `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87` |
| Iter008 JERC raw chain | High-likelihood initialization source | SHA-256 `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080` |
| ABBY/JERC cases and physical posterior | Fixed scientific contract | Same cases, site windows, `SR:SR_err` validity mapping, 14 physical parameters and bounds, IID Gaussian likelihood, and fitted site-specific `sigma_SR` as Iter008 |
| Puma environment | Runtime | `development/hpc/puma.md`; `chopinsong` / `standard` / `OLMT_puma`; exact package versions recorded by preflight |

The Iter009 initialization pools and bundles may be reused by a later convergence-length
experiment only while every posterior-defining input remains identical. A likelihood, prior,
bound, observation window, case, site input, or surrogate change invalidates the
`high-likelihood` designation and requires regeneration.

### 4. Bounded scope, work units, and exclusions

#### 4.1 Locked five-arm matrix

Each arm runs separate ABBY and JERC chains with 64 walkers, 8,000 steps, 15 free dimensions,
16 worker processes, unthinned retention, checkpoints at 2,000/4,000/6,000/8,000 steps, and
MCMC seeds 9009, 9010, and 9011. The matrix contains exactly 30 chains.

| Arm | Coordinates | Initialization | Proposal |
| --- | --- | --- | --- |
| `B` | physical | uniform-prior | explicit `StretchMove(a=2.0)` |
| `T` | transformed | same physical initial ensemble as `B` | explicit `StretchMove(a=2.0)` |
| `I` | physical | dispersed high-likelihood | explicit `StretchMove(a=2.0)` |
| `M` | physical | same physical initial ensemble as `B` | 80% `DEMove()` + 20% `DESnookerMove()` |
| `TIM` | transformed | same physical initial ensemble as `I` | 80% `DEMove()` + 20% `DESnookerMove()` |

The same three replicate seeds are used across sites and arms. Initialization and sampler RNG
streams are separated explicitly:

| Replicate | MCMC seed | Uniform-init seed | Maximin-selection seed |
| --- | ---: | ---: | ---: |
| 1 | 9009 | 19009 | 29009 |
| 2 | 9010 | 19010 | 29010 |
| 3 | 9011 | 19011 | 29011 |

#### 4.2 Transformation contract

- Apply the natural logarithm to the eight positive rate parameters: `k_l1`--`k_l3`,
  `k_s1`--`k_s4`, and `k_frag`.
- Apply a scaled logit to the six bounded `rf_*` fractions.
- Apply a scaled logit over the site-specific `[0, U]` interval to `sigma_SR`.
- Include the analytic Jacobian so the existing uniform physical-space prior is unchanged.
- Require physical-to-sampler-to-physical round-trip tests, analytic-versus-finite-difference
  Jacobian tests, and physical/transformed target equivalence. Do not clip or silently coerce
  invalid sampler coordinates.
- Retain both native sampler-space and physical-space chains. Physical coordinates are
  authoritative for cross-arm scientific comparison.

#### 4.3 Initialization preprocessing

The distinct post-preflight `initialize` work unit will, separately for ABBY and JERC:

1. Read the final half of the checksum-locked Iter008 unthinned raw chain.
2. Require finite log probability and in-bounds physical coordinates.
3. Remove exact repeated physical states before applying the likelihood percentile.
4. Retain the top 10% of unique states by log posterior.
5. Require at least 640 unique pool members and nonzero spread in every dimension.
6. Select 64 distinct positions per maximin seed in normalized physical-prior coordinates.
7. Require finite log posterior, strict bounds, uniqueness, full 15-dimensional rank, and a
   passing numerical condition check for every selected ensemble.
8. Write immutable per-site pool artifacts and per-site/per-seed initialization bundles with
   source step/walker indices, log probabilities, distances, ranks, metadata, and SHA-256.

The physical initialization bundle is authoritative. `B`/`T`/`M` share the corresponding
uniform bundle, and `I`/`TIM` share the corresponding high-likelihood bundle.

#### 4.4 Preflight and persistence

The bounded compute-node preflight verifies Puma/environment identity, all manifests and input
hashes, the exact 30-row matrix, transformation and Jacobian tests, target equivalence, and HDF
creation/reopen/continuation/finalization. It exercises the four unique execution mechanisms
(physical/stretch, transformed/stretch, physical/DE mixture, transformed/DE mixture) for both
sites with 32 walkers x 2 steps: 512 smoke proposals total. It makes no acceptance, tau, ESS,
skill, or convergence inference.

Every production leaf writes incrementally to an emcee HDF backend. Successful finalization
writes an immutable dual-coordinate `raw_chain.npz` containing both chains, raw log
probabilities, both initial states, parameter schema, transforms, bounds, Jacobian convention,
site, arm, seeds, move configuration, provenance, and hashes. A verified continuation finishes
at exactly 8,000 total steps; it never adds a second 8,000-step budget. A backend that already
contains 8,000 valid steps may undergo finalization-only recovery without resampling.

#### 4.5 Scheduler work units and layout

Use eight run directories under
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`, one for each proposed
slug. Each of the five arm-specific campaign parents is an unthrottled `--array=1-6` with an
explicit locked manifest:

```text
leaf_01_abby_seed9009
leaf_02_abby_seed9010
leaf_03_abby_seed9011
leaf_04_jerc_seed9009
leaf_05_jerc_seed9010
leaf_06_jerc_seed9011
```

The five parent arrays are submitted sequentially for identity verification and may overlap
after every parent passes its immediate check. There is no agent-imposed concurrency cap; Puma
schedules the approved maximum envelope.

#### 4.6 Exclusions

No likelihood, prior, physical bound, surrogate, observation, case, site window, coupled schema,
feature, or scientific-model change; no joint MCMC; no posterior-predictive campaign; no
Experiment 2 convergence-length confirmation; no Experiment 3 temporal-likelihood comparison;
no automatic proposal tuning; no arm selection by best log probability or predictive skill; and
no scientific adequacy or convergence claim from this pilot alone. Raw chains, HDF, logs,
NetCDF, full plots, and other large products remain outside Git.

### 5. Tentative integrity gates, geometry qualification, and decision rule

#### 5.1 Hard integrity gates

An integrity pass requires all submitted tasks to have authoritative terminal accounting and a
classified outcome; preflight and initialization to pass; every dependency, source, submitted
copy, configuration, matrix, and initialization identity to match; all 30 eligible chains to
contain exactly `(8000, 64, 15)` physical and sampler-space states with matching log
probabilities; transformation, provenance, finiteness, bounds, schema, and checksum validators
to pass; required diagnostic/report artifacts to exist; and the iteration report, cumulative
summary, registry, and handoff to agree after final validation. Missing or mismatched evidence
fails closed.

Sampler quality remains scientific routing evidence, not an execution-integrity gate.

#### 5.2 Geometry qualification

An arm is `geometry-qualified` only when every condition holds for all six site-seed chains:

- mean acceptance is 0.20--0.50;
- at most 6 of 64 walkers have acceptance below 0.10;
- tau is finite for all 15 physical parameters;
- every parameter's 6,000-to-8,000-step relative tau change is at most 20%;
- `8000 / tau >= 20` for every parameter;
- rank-normalized split screening R-hat is at most 1.05 for every physical parameter and log
  probability;
- no deterministic terminal two-band partition has at least seven walkers per band and
  silhouette at least 0.5; and
- every pairwise cross-seed Wasserstein distance is at most 5% of the physical prior width for
  every parameter.

Split R-hat is a screening statistic because walkers within an emcee ensemble interact. Nominal
unthinned ESS is reported with its formula and units but is not a separate gate because it is
algebraically tied to length and tau. Physical boundary occupancy and transformed-coordinate
saturation are reported but do not fail geometry qualification by themselves.

#### 5.3 Selection and attribution

Among geometry-qualified arms, select lexicographically by: (1) lowest worst-case physical-space
tau over every parameter/site/seed; (2) if worst-case tau differs by less than 10%, lowest worst
split R-hat; (3) lowest worst cross-seed Wasserstein distance; and (4) fixed simplicity order
`B -> M -> T -> I -> TIM`. Best likelihood, MAP skill, RMSE, R2, KGE, and predictive scores cannot
select an arm.

The report separately attributes evidence: `B` qualification supports a default-geometry/run-
length explanation; `T` supports scaling/bound geometry; early-only `I` improvement supports
initialization/burn-in; `M` supports proposal limitation; `TIM` alone supports an interaction.
If no arm qualifies, select no least-bad winner and route toward multimodality,
non-identifiability, likelihood discontinuity, or model-structure investigation.

### 6. Proposed site, resources, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / environment | `chopinsong` / `standard` / `OLMT_puma` |
| Preflight | 2 CPUs / Puma-derived 10 GB / 30 minutes |
| Initialize | 4 CPUs / Puma-derived 20 GB / 1 hour |
| Each of 30 campaign leaves | 16 CPUs / Puma-derived 80 GB / 4 hours / 16 workers |
| Validate/report | 4 CPUs / Puma-derived 20 GB / 2 hours |
| Maximum simultaneous campaign envelope | 480 CPUs / Puma-derived 2,400 GB; five unthrottled six-leaf arrays, subject to Puma scheduling |
| Nominal scheduler count | 33 tasks across eight submissions: preflight, initialize, 30 leaves, validate |
| Review | Independent read-only agent after preparation and before substantive submission; primary agent remains sole writer and scheduler operator |
| Retry | One minimal preflight-only correction/rerun; one unchanged initialize scheduler/resource retry; at most six campaign-leaf recoveries total and at most one per leaf; one unchanged validation scheduler/resource retry |
| Hard cap | 42 scheduler tasks including every permitted retry/recovery |
| Cancellation | Recorded Iter009 IDs only; a proven universal pre-execution defect may cancel all affected pending work, and a proven arm-specific defect may cancel only that arm's recorded array |
| Stop | After terminal accounting, immutable integrity evaluation, geometry qualification and selection/route, durable records, handoff validation, and the authorized closeout branch |

A campaign continuation requires a checksum- and metadata-verified HDF state and preserves every
locked scientific and sampler term. More than six affected leaves, or any application, numerical,
schema, dependency, scientific-input, provenance, or scope failure, stops for fresh approval.
Live `uquota`/capacity and `job-limits` evidence must be checked before submission; normal
scheduler throttling or pending state does not change the approved matrix.

### 7. Expected evidence, artifacts, records, and closeout

Each leaf must retain submitted material and manifests, HDF identity, final dual-coordinate raw
archive, initialization identity, checkpoint acceptance and tau tables, correct unthinned nominal
ESS, trace and terminal-log-probability evidence, boundary/saturation evidence, target-equivalence
audit, metadata/checksums, and a human-readable leaf report.

Validation creates ten site-arm three-seed packages with rank/split screening, pairwise
Wasserstein distances, tau trajectories, acceptance/stuck-walker tables, terminal-band results,
and overlaid seed marginals/traces. The global package contains a 5-arm x 2-site qualification
matrix, worst-case selection table, attribution/route, accounting table, machine-readable
decision, and comprehensive Iter009 report. Compact tables and selected plots go under
`summaries/iter009`; large artifacts remain in the external run directories.

Closeout finalizes `iterations/iter009.md`, appends `ITERATION_SUMMARY.md` and `registry.csv`,
rebuilds `handoff/CURRENT.md`, and runs a cross-record validator. After all gates pass, the
proposed closeout branch permits exactly one bounded local commit with expected subject
`Close Iter009 sampler geometry pilot`; raw/large outputs are excluded and no push is proposed.

### 8. Consolidated kickoff approval

The user approved this unchanged plan as the complete Iter009 package on
`2026-08-10T20:29:27-07:00`. The active contract is recorded above and in
`iterations/iter009.md`; it authorizes only the stated preparation, review, runtime, recovery,
record, and closeout actions. Any material change still requires a revised package and fresh
approval.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. If an active or closed iteration exists, read its `iterations/iterXXX.md` report in full and up
   to two preceding reports. No report is expected for pre-kickoff `iter001`.
3. Read relevant registry rows and summaries.
4. Read the proposed or approved HPC profile when one exists; otherwise leave site selection
   unresolved.
5. Inspect Git state and reconcile scheduler and artifact state relevant to any recorded
   iteration.
6. For a new iteration, resolve missing decisions and seek one approval of the complete
   consolidated kickoff package. For an initialized iteration, verify and reuse its recorded,
   unexhausted package without asking again.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter010.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter010`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter010/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter010_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
