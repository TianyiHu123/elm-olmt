# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter009`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-11T14:20:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved` (Iter009 initialized under the consolidated package).
- Kickoff goal and stop boundary: complete the immutable 30-chain ABBY/JERC sampler-geometry
  pilot; stop after terminal accounting, integrity and geometry evaluation, durable records,
  handoff validation, and one local closeout commit.
- User response and approval timestamp: `approve for the complete iter009 package`,
  `2026-08-10T20:29:27-07:00`.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`;
  creation limited to the eight Iter009 run directories in the finalized plan.
- Locked dependencies/gates/decision: the exact complete plan below; Iter002 forcing and Iter012
  `drop21_corr080`, ABBY/JERC observations and Iter008 raw chains have the recorded hashes;
  five arms, three seeds, 30 leaves, 64x8000, physical posterior fixed, and immutable integrity
  and geometry-qualification rules.
- Outside-sandbox and closeout authorities: locked `sbatch` and contract-authorized retries;
  job-scoped monitoring/accounting; bounded cancellation of recorded Iter009 jobs; one bounded
  local closeout commit after validation.

## Current Objective

ABBY and JERC sampler-geometry pilot

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Objective: `ABBY and JERC sampler-geometry pilot`
- Bounded scope: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Overall acceptance result: `pass`
- Decision: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
- Next state: `No next iteration is proposed; any follow-up requires a new approved package to investigate multimodality, non-identifiability, likelihood discontinuity, or model structure.`

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: five-arm sampler-geometry pilot; separate ABBY/JERC; 30 chains; 64x8000;
  three shared seeds; fixed physical posterior; integrity plus geometry routing
- Bounded scope label: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter009`
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

1. Iter009 is closed after cross-record validation and the bounded local closeout commit.

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

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter008.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter008`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter008/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter008_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
