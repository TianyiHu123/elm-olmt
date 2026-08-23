# iter009 - ABBY and JERC sampler-geometry pilot

## Status

- Iteration ID: `iter009`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter009_preflight`,
  `spinup_forcing_coupling_iter009_initialize`,
  `spinup_forcing_coupling_iter009_{b,t,i,m,tim}_campaign`, and
  `spinup_forcing_coupling_iter009_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Summary path: `development/spinup_forcing_coupling/summaries/iter009`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Started: `2026-08-10T20:29:27-07:00`
- Closed: `2026-08-11T14:20:00-07:00`

## Finalized Plan

The finalized plan is the complete Iter009 proposal copied unchanged from the closed Iter008
report into `handoff/CURRENT.md` under **Finalized Iter009 Plan**. That body, including the
five-arm matrix, transformation contract, initialization preprocessing, integrity and geometry
gates, resources, retries, exclusions, evidence, and closeout branch, is immutable for this
iteration.

- Objective: determine whether Iter008 poor mixing primarily arises from parameter scaling and
  bounds, initial walker placement, or the default stretch proposal, without changing the
  physical posterior.
- Hypothesis: bounded geometry interventions can improve acceptance, terminal overlap, stable
  autocorrelation estimates, and cross-seed agreement at both ABBY and JERC.
- Scope: five arms (`B`, `T`, `I`, `M`, `TIM`), separate ABBY/JERC chains, three seeds per
  site-arm, 64 walkers x 8,000 steps, 15 dimensions, 16 workers, checkpoints and immutable
  dual-coordinate chains. This is exactly 30 campaign leaves.
- Exclusions: no change to likelihood, prior, physical bound, surrogate, observation, case,
  site window, coupled schema, feature, or scientific model; no joint MCMC, predictive campaign,
  automatic proposal tuning, or scientific-quality/convergence claim from this pilot.
- Decision: all integrity gates must pass. Geometry qualification and selection use only the
  immutable rules in the finalized plan; no least-bad arm is selected if none qualifies.
- Stop: terminal accounting, immutable integrity evaluation, geometry qualification and route,
  durable records, cross-record validation, and the authorized closeout branch.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approve for the complete iter009 package`; `2026-08-10T20:29:27-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Iter009 sampler-geometry pilot; 33 nominal scheduler tasks across eight submissions and 42-task hard cap; stop as finalized above |
| Confirmed HPC system and site profile | University of Arizona Puma, `development/hpc/puma.md` |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to the eight finalized Iter009 run directories; `/xdisk` is temporary and unbacked; raw/large outputs remain outside Git |
| Locked dependencies, scope, exclusions, gates, and decision rule | Complete finalized plan in `handoff/CURRENT.md`; forcing, spinup, observations, Iter008 chains, cases, likelihood, priors, bounds, matrix, seeds, and gates are immutable |
| Lifecycle authority | Initialization, preparation, scoped source/config changes, run-directory creation, independent read-only review, compute-node preflight/initialization, submission, continuous monitoring/accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs/10 GB/30 min; initialize 4 CPUs/20 GB/1 h; campaign leaves 16 CPUs/80 GB/4 h/16 workers; validate 4 CPUs/20 GB/2 h; exact retry limits as finalized |
| Cancellation scope | Recorded Iter009 jobs only; only the finalized proven universal or arm-specific pre-execution defect conditions |
| Outside-sandbox authority | Locked `sbatch` and contract-allowed resubmissions; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, job-history, and job-limits; bounded `scancel` under the stated rule |
| Closeout branch | One bounded local closeout commit after final validation; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | SHA-256 |
| --- | --- | --- | --- | --- |
| Iter002 forcing surrogate | Coupled `SR` | external Iter002 release | `forcing-surrogate-v1` | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup | Coupled state | external Iter012 `drop21_corr080` release | `spinup-surrogate-v1` | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY / JERC observations | Likelihood targets | NEON v4 evaluation files | `SR:SR_err` | `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` / `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` |
| Iter008 raw chains | Initialization source | external Iter008 ABBY / JERC campaigns | unthinned physical chains | `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87` / `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080` |

- Preparation base: clean `b086a212390af5f198a27799b92d8bc5ce09a321`; planning commit
  `dff5da3373e9e61800e9a65fdd28fa0344066d5b` is the clean initialization HEAD.
- Execution source is locked only by the reviewed Iter009 source manifest after authorized
  preparation; it must contain only contract-controlled paths.
- Environment: `OLMT_puma`; exact micromamba module/version is a preflight requirement.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| preflight | `23538732`, `23538737`, `23538751` | terminal `COMPLETED 0:0` | User approved one additional launcher-only correction/review/rerun after the original retry boundary: `23538732` lacked `pytest`; `23538737` lacked repository `PYTHONPATH`; reviewed retry-2 copy `23538751` passed in 28 s using 2 CPUs / 10 GB, with eight all-pass smoke cases and 512 total proposals. |
| initialize | `23538764` | terminal `COMPLETED 0:0` | completed in 15 s using 4 CPUs / 20 GB; both pools pass the ≥640 requirement and all 12 immutable initialization bundles exist |
| B array | `23538767_[1-6]`, recovery 1 `23538796_[1-6]`, recovery 2 `23538844_[1-6]` | recovery 2 terminal `COMPLETED 0:0` | original all-six failure occurred before model work from uppercase `${INITIALIZATION}`. Recovery 1 reached coupled-site preparation then failed before sampling on non-existent HDF backend access. The reviewed HDF-creation recovery completed all six leaves. |
| T array | `23538909_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| I array | `23538920_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| M array | `23538931_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| TIM array | `23538937_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| validate | `23540890`, retry `23540912` | retry terminal `COMPLETED 0:0` | first attempt failed pre-evaluation from missing repository import context; reviewed v5 launcher corrected `cd`/`PYTHONPATH`; final validator passed 30 leaves and ten packages |

## Independent Read-Only Review

- Reviewer: independent read-only agent `iter009_review`.
- Reviewed source manifest and outcome: `pass` on `2026-08-11`; the reviewer confirmed all six
  original findings were corrected. A subsequent delta review caught a Bash `readonly` loop
  reassignment before submission; it was corrected and the final delta outcome was `pass`.
- Reviewed source lock: `development/spinup_forcing_coupling/slurm/iter009/iter009_source_manifest.sha256`
  (15 execution-source entries; mutable ledgers excluded). Static evidence: `git diff --check`,
  `bash -n` for all five submission/materializer scripts, and `sha256sum -c` all passed.
- A subsequent review of the validation-evaluator correction initially blocked two immutable
  decision-rule defects: transformed-arm log-probability screens used sampler rather than
  physical posterior values, and the selection comparator did not implement the less-than-10%
  tau tie-break. Both were corrected; re-review passed. The validator now emits the ten required
  site-arm packages, common-target R-hat/terminal-band evidence, the conditional selection rule,
  and report-only transformed-coordinate saturation tables. The unused original validation copy
  is preserved; reviewed `submit_validate_iter009_v2.slurm` is byte-identical to canonical source.
- The new closeout validator initially blocked because it searched broad strings rather than
  proving exact four-record field agreement and controlled-path ownership. It was strengthened
  to compare standardized identity, acceptance, decision, dependencies, and next state across
  the report, cumulative summary, registry, and handoff, and to require exact observed changed
  paths before and after the closeout commit. Re-review passed.

## Execution and Diagnostics

- Static validation: source-manifest, shell syntax, and diff checks passed before materialization.
- Preflight `23538732`: terminal `FAILED 1:0`, 11 s, 2 CPUs/10 GB; environment-only missing
  `pytest` before scientific/model execution. The one authorized minimal rerun `23538737` is
  terminal `FAILED 1:0`, 13 s, 2 CPUs/10 GB, before smoke execution with
  `ModuleNotFoundError: No module named 'model_ELM'`. User then explicitly approved one additional
  launcher-only correction, re-review, and third preflight submission. `23538751` is terminal
  `COMPLETED 0:0`; `smoke/preflight_result.json` records 8 pass results across ABBY/JERC and all
  four mechanisms, 32 walkers x 2 steps = 512 proposals.
- Campaign accounting is currently 46 submitted tasks before final validation: the nominal 33
  plus two explicitly approved extra preflight attempts and two explicitly approved six-leaf B
  application recoveries. This exceeds the original 42-task cap; the closeout integrity decision
  must therefore classify the user-approved exception explicitly rather than silently treating
  the cap as satisfied.
- The complete campaign source is already running; the evaluator-only source correction is
  independently reviewed and staged solely for the pending validation work unit.

## Validation, Evaluation, and Decision

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Objective: `ABBY and JERC sampler-geometry pilot`
- Bounded scope: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Overall acceptance result: `pass`
- Decision: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
- Next state: `Planning-only Iter010 proposal recorded below; iter010 is not_initialized and requires a fresh consolidated kickoff package and explicit approval.`

All 30 final leaves are terminal `COMPLETED 0:0`, with required HDF, final raw chains, metadata,
hashes, diagnostics, and checkpoints. Validation `23540912` is terminal `COMPLETED 0:0` and
emitted all ten site-arm packages. Integrity and provenance passed, but no arm met every immutable
geometry qualification criterion: the best overlap screens occur in TIM, while its other required
screens still fail. The original 42-task cap was exceeded only through user-approved exception
attempts: final submitted count is 48, including the failed first validation attempt; this is
recorded as an exception rather than treated as cap satisfaction.

The complete arm-by-arm diagnostic interpretation, causal assessment, and proposed follow-up
experiments are in
[`summaries/iter009/ITER009_REPORT.md`](../summaries/iter009/ITER009_REPORT.md).

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
