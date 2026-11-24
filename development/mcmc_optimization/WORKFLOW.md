# MCMC Optimization Iterative Development Workflow

`WORKLOAD_ROOT` is `development/mcmc_optimization`.

This policy governs bounded MCMC optimization development iterations. Scientific intent and
invariants live only in `MCMC_OPTIMIZATION_PLAN.md`; implementation choices, experimental settings,
resources, and acceptance gates live in approved `iterations/iterXXX.md` records. The campaign
plan grants no iteration or runtime authority.

## 1. Core rules and durable records

- One primary agent is the sole writer, scheduler operator, decision maker, and closeout owner.
- Required independent review is performed by a different, read-only reviewer. Primary self-review
  does not satisfy that gate.
- Planning, the campaign plan, and a prior closeout grant no initialization, repository Python,
  compute, scheduler, retry, cancellation, directory-creation, or commit authority.
- Read-only inspection and shell/text validation are allowed before runtime approval. Repository
  Python and scripts require confirmed HPC context and an approved runtime contract and must run
  on a compute node unless the selected profile explicitly permits another safe context.
- Documentation-only scaffolding does not consume an iteration ID. Every initialized iteration
  includes approved bounded implementation validation, data preparation, integration, benchmark,
  or scientific work.
- Acceptance gates and the decision rule become immutable at kickoff approval. Results cannot be
  used to revise or reinterpret them.
- Published surrogate artifacts and historical MCMC records are immutable provenance.

| Record | Purpose | Update rule |
| --- | --- | --- |
| `MCMC_OPTIMIZATION_PLAN.md` | Scientific objective, priors, likelihood, architecture, invariants, exclusions, and progression | Amend only with separate user authorization outside an iteration; never reinterpret completed work with a later plan. |
| `handoff/CURRENT.md` | Live plan identity, authority, dependencies, jobs, blockers, and next action | Update at every state transition. |
| `iterations/iterXXX.md` | Exact approved plan, runtime contract, chronological evidence, and decision | Create only after kickoff approval; finalize at closeout. |
| `registry.csv` | Fixed-schema index of closed iterations | Add one row at closeout; do not add iteration-specific columns. |
| `ITERATION_SUMMARY.md` | Cumulative immutable closeout evidence and decisions | Append one section at closeout. |
| `summaries/iterXXX/` | Compact evidence required to reproduce the decision | Populate only when eligible evidence exists. |
| `slurm/iterXXX/` | Canonical iteration-specific execution material | Treat as execution source; preserve submitted copies externally. |
| `tools/` | Reusable campaign validation and analysis utilities | Keep one-off utilities with their iteration. |

Repository records retain decision-relevant evidence, not complete transcripts. Preserve material
failures, rejected work, retries, job IDs and scopes, hashes, gates, decisions, limitations, and
exact external evidence paths. Keep raw logs, checkpoints, chains, per-candidate outputs, repeated
monitoring snapshots, and other bulk evidence in the approved external run directory.

## 2. State and status model

| Phase | Required action | Allowed change |
| --- | --- | --- |
| `pre_kickoff` | Recover state and resolve the planning-only proposal | Read-only; no iteration scaffold. |
| `ready_for_kickoff_approval` | Present one consolidated package | No iteration-specific changes. |
| `initializing` | Create the approved report and update the handoff | Approved record changes only. |
| `preparing` | Lock dependencies and prepare approved execution material | Contract-controlled paths only. |
| `review` | Obtain independent read-only review | Reviewer makes no changes. |
| `preflight` | Run and account for bounded compute-node preflight | Authorized scheduler actions only. |
| `execution` | Run and monitor locked work units | Authorized scheduler actions only. |
| `evaluation` | Validate evidence and apply immutable gates | Approved analysis and records only. |
| `closeout` | Cross-validate records and follow the approved commit branch | Authorized closeout changes only. |
| `closed` | Publish a reconciled handoff | No active or unaccounted work. |

Iteration statuses are `planned`, `in_progress`, `completed`, `failed`, and `blocked`.
`not_initialized` is a handoff-only sentinel; `rejected` is a work-unit gate result. IDs are
independent, zero-padded, and begin at `iter001`. Each initialized iteration records a unique run
slug and exact work-unit-to-output mapping.

## 3. MCMC scientific and technical invariants

Iteration records specialize these contracts but cannot weaken them without a separately approved
campaign-plan amendment.

### 3.1 Prior and parameter contract

- Infer exactly 18 physical ELM parameters. Do not add fitted observation-error, covariance,
  bias, depth-fraction, or other nuisance dimensions.
- `prior_id=ppe1` is the active baseline. `prior_id=ppe2` is optional implementation support and
  scientifically inactive until compatible PPE2 surrogate and uncertainty products exist.
- Every candidate pool, posterior evaluation, chain, checkpoint, diagnostic, and result records
  `prior_id`, exact parameter order/schema, source identities, support, transforms, and seed.
- Preserve conditional `k_s4` support and normalization for the selected prior and conditional
  leaf/root C:N support and normalization. Validate physical-space prior ratios, inverse maps,
  support boundaries, coordinate Jacobians, and physical-versus-transformed density equivalence.
- Never reinterpret a candidate pool or checkpoint under a different prior or schema, clip an
  incompatible prior to surrogate support, or treat a Sobol candidate distribution as the prior.

### 3.2 Surrogate dependency contract

- The initial dependency is the frozen PPE1 ABBY/JERC coupled `release_0001`, with its model,
  feature, forcing-history, time/calendar, site, parameter, and output schemas and checksums.
- Record repository source, release artifact, catalog/manifest, uncertainty handoff, and input
  provenance. Verify selected prior, trained support, release, site, and uncertainty compatibility.
- Inference is target-free and sequential: predicted spinup C/N feeds GPP and predicted C/N plus
  same-hour predicted GPP feeds SR. True upstream ELM targets are prohibited in normal inference.
- Do not modify published artifacts or silently substitute an older inference path. Treat
  observations and ELM targets as evaluation inputs only where the approved task requires them.
- PPE2 scientific inference is prohibited until a PPE2-trained and independently validated
  release, PPE2-specific uncertainty, and PPE2-specific depth products exist.

### 3.3 Likelihood and observation contract

- The scientific variables are GPP, SR, TOTSOMC, and TOTSOMN. GPP and SR likelihood resolutions
  are independently configured as hourly or daily; predictions and observations must use aligned
  timestamps, calendar, masks, units, aggregation, and coverage rules.
- Observation, forcing, QC, uncertainty, and preprocessing identities are locked per experiment.
  Observation uncertainty is fixed, positive, finite, and defined at the likelihood resolution.
- C/N uses the established joint bivariate-lognormal formulation and fixed observation,
  surrogate, and depth covariance components, including the C-N covariance term. Covariance and
  any fixed development-only bias correction are not inferred.
- Surrogate training, tuning, selection, robustness, uncertainty estimation, and validation use
  only the allowed development population. Protected fixed-test members remain excluded from
  those uses and from estimating surrogate likelihood uncertainty.
- For the fixed PPE1 depth observation operator only, Section 1.2 of the current campaign plan
  explicitly requires the complete 1,024-member PPE1 preprocessing ensemble for the C/N depth
  fractions, depth-residual means, and paired depth covariance. This exception does not make the
  205 protected members independent evaluation data for the combined surrogate-plus-depth
  operator and grants no other fixed-test use.
- Likelihood construction may consume that frozen full-ensemble depth operator together with the
  separately frozen development-only surrogate uncertainty; it must preserve both provenance
  populations and the resulting statistical-independence caveat.
- Each site has a distinct inference configuration, observation window, and 18-parameter
  posterior. Site identity and site-specific provenance must not be pooled away.

### 3.4 Performance and infrastructure contract

- Characterize cold/warm coupled-surrogate throughput and peak memory early on representative
  approved ABBY/JERC windows and proposal batch sizes. Separate loading/preprocessing from
  per-proposal cost and project candidate-search and MCMC resources from measured evidence.
- Record hardware, environment, threads, release, window, resolution, batching, walltime, memory,
  and deterministic replay. Unmeasured resource or throughput claims cannot define production
  budgets.
- Performance optimization is a separately proposed and authorized iteration decision. Any
  caching, batching, or infrastructure change must preserve numerical equivalence, deterministic
  behavior where required, scientific schemas, and complete provenance.

### 3.5 MCMC validation contract

Approved gates must cover the relevant subset of:

- prior, conditional normalization, transformed-density, support, and likelihood numerical
  correctness, including component-wise synthetic or independently computed expectations;
- candidate, local-refinement, diversified-pool, and walker validity, uniqueness, rank/span,
  finiteness, support, and current posterior re-evaluation;
- deterministic candidate generation, non-overwriting checkpoints, exact restart provenance, and
  reproducible chain continuation under locked software and configuration;
- chain diagnostics including acceptance by walker, traces/stationarity, autocorrelation time and
  effective sample size where estimable, prior-bound occupancy, independent initializations, and
  explicit convergence limitations;
- component likelihood accounting, posterior summaries, posterior predictive GPP/SR and
  depth-adjusted C/N evidence where applicable, residual/QC diagnostics, and fixed covariance
  provenance; and
- separation of scientific gate rejection from numerical, interface, dependency, scheduler,
  resource, observation-context, and infrastructure failures.

No workflow rule fixes provisional candidate counts, walker counts, chain lengths, move mixtures,
resource sizes, or performance thresholds. Lock them in an approved iteration record.

## 4. Required schemas and lifecycle

### A. Bootstrap, clarify, and recover

1. Read `MCMC_OPTIMIZATION_PLAN.md`, calculate its SHA-256, and compare it with the handoff and any
   active iteration identity.
2. Read `handoff/CURRENT.md`; if an iteration exists, read its full report and up to two preceding
   reports, relevant registry rows, summaries, and compact evidence.
3. Read the proposed or approved `development/hpc/` profile. A proposed profile does not confirm
   the current host or grant runtime authority.
4. Inspect Git state and reconcile recorded dependency, artifact, checkpoint, and scheduler state.
5. Verify the planning proposal's campaign phase, alignment, dependencies, and any proposed
   deviation. A material conflict requires user resolution or a separately authorized plan change.
6. If work is initialized, verify its package is complete, unexhausted, and unchanged, then resume
   from the recorded phase without requesting duplicate authority.

A complete planning-only proposal states: sequential ID/work type; campaign-plan identity and
alignment; evidence-derived objective/hypothesis; exact prior, parameter, surrogate, observation,
uncertainty, site/time, and source dependencies; finite scope and exclusions; tentative gates and
decision rule; proposed HPC profile, output root, resources, preflight, review, monitoring,
retries, cancellation, and stop boundaries; expected evidence and record updates; and the fresh
approval boundary. It grants no authority.

For Iter001, finalize the user-supplied planning direction. For later work, copy the preceding
closed report's complete next proposal unchanged into the handoff unless a later user-directed
planning revision is recorded with provenance.

### B. Consolidated kickoff approval and initialization

Present one package containing:

1. kickoff goal, finite work units, and stop conditions;
2. locked campaign-plan identity, phase, alignment, and approved deviation or `none`;
3. confirmed HPC system and selected profile;
4. exact output root/layout, creation authority, retention limits, and storage risks;
5. locked prior/schema, surrogate/release, observations, uncertainty, site/time scope, exclusions,
   acceptance gates, and decision rule;
6. preparation, independent review, preflight, submission, monitoring, terminal accounting,
   evaluation, record, and closeout authority;
7. exact resources and separate preflight-correction and scheduler/resource retry limits;
8. bounded cancellation conditions and exact current-iteration job scope;
9. outside-sandbox authority for locked `sbatch`, job-scoped monitoring/accounting, and bounded
   `scancel`; and
10. either one closeout commit or `validated_uncommitted`.

Ask once for approval of the complete package. Treat omissions as declined. A goal or remembered
command approval does not broaden authority. After approval only, create the report from the
template, record the response and timestamp, update the handoff, create approved paths, and move
from `initializing` to `preparing`.

### C. Controlled preparation and independent review

1. Lock every declared dependency and compatibility check. Do not silently replace data,
   artifacts, uncertainty, sites, priors, schemas, or configurations.
2. Create canonical scripts, configurations, manifests, and validators under `slurm/iterXXX/`
   where execution is required. Materialize a self-describing submitted copy and immutable config
   in each approved run directory before submission.
3. Record canonical/submitted hashes, repository/diff identity, dependencies, environment,
   resources, exact command, logs, checkpoints, and output mapping.
4. Obtain review by a different read-only agent. The reviewer checks the contract, scientific
   compatibility, leakage boundary, paths, static validation, numerical-test design, submitted-copy
   equality, and config/manifest equality. Record `pass`, `pass_with_concerns`, or `block` and the
   reviewed source identity. A block requires correction and passing re-review.

Keep large outputs outside Git and follow the selected profile. Promote only reusable utilities;
preserve iteration-specific material with its iteration.

### D. Preflight, execute, monitor, and account

1. Run the approved bounded compute-node preflight before substantive work. It may check imports,
   paths, identities, schemas, small fixtures, launch behavior, and numerical contracts but must
   not consume the production workload.
2. Submit only locked local copies from approved run directories. Capture `sbatch --parsable`,
   atomically record the work-unit mapping, update the handoff, and immediately verify identity.
3. Submit substantive work only after preflight passes. Verify each independent work unit before
   launching a dependent one; stop further submissions on identity mismatch.
4. Monitor the entire recorded job/array scope with the profile's authoritative commands and a
   supported wait mechanism. Continue until every expected task has terminal `sacct` accounting.
   Empty `squeue`, queue departure, or aggregate success is not terminal evidence.
5. Record state, exit code, elapsed time, allocation, memory, failure reason, and unavailable
   fields. Query failure means workload state is unknown and grants no retry or cancellation.

### E. Continuity, failures, retries, and cancellation

Once status is `in_progress`, the primary remains responsible through terminal accounting,
evaluation, record validation, and closeout. Before ending a turn, re-read the handoff and job
ledger. If either shows active work or any expected task without terminal accounting, remain in
the supported wait/monitoring operation. A voluntary checkpoint is allowed only for a material
user decision or an external wait without a supported wake mechanism; first record exact scope,
last evidence, reason, and resume action.

Classify before acting:

- **Scientific gate rejection:** eligible completed evidence fails an immutable scientific gate.
- **Infrastructure performance rejection:** eligible benchmark evidence fails a declared resource
  or throughput gate without implying scientific invalidity.
- **Scheduler/resource failure:** retry only inside the approved same-scope boundary.
- **Preflight failure:** use only an approved minimal preflight correction and rerun boundary.
- **Application/code/interface/schema/data/dependency/numerical failure:** preserve evidence and
  obtain fresh approval before changing execution material or retrying.
- **Observation-context failure:** state remains unknown until authoritative reconciliation.

Cancel only an exact recorded current-iteration scope when its approved condition is met. Record
authority and evidence, cancel, and then obtain terminal accounting. Cancellation does not grant
fix or retry authority.

### F. Evidence-based evaluation and decision

Verify work-unit completeness, identity, provenance, leakage exclusions, and artifact integrity.
Run only approved validation and analysis, apply every immutable gate and tie-break/decision rule,
and report component and overall results. Preserve convergence limitations and distinguish
scientific conclusions from infrastructure feasibility and failure classification.

### G. Controlled closeout

1. Finalize the report with exactly one complete next planning-only proposal or a terminal
   declaration. Record any plan-amendment recommendation as advisory only.
2. Add one fixed-schema registry row, append one cumulative summary section, and rebuild the
   handoff with plan identity, authority, dependencies, evidence, decision, risks, next action,
   and the unchanged next proposal.
3. Validate agreement across report, summary, registry, and handoff on iteration identity, status,
   work type, objective, scope, gate result, decision, dependencies, outputs, active-job state,
   campaign-plan identity/alignment where represented, and next direction.
4. Preserve validator identity, command, output, and result. A validation failure blocks closeout.
5. Follow the approved branch: create at most one closeout commit, or record a bounded source/diff
   identity as `validated_uncommitted`. Never push without separate authorization.
6. Mark `closed` only when no job is active or unaccounted, failures are classified, evaluation and
   records are complete, validation passes, and the selected closeout branch is satisfied.

## 5. Portability and plan amendments

Keep scientific direction in `MCMC_OPTIMIZATION_PLAN.md`, lifecycle policy here, and bounded
decisions in iteration records. Keep Puma mechanics, account, environment, storage, and resource
rules in `development/hpc/puma.md`; that profile constrains operations but does not choose scope or
grant authority.

An iteration may recommend a campaign-plan amendment but cannot edit the plan under iteration
authority. The user must separately authorize the exact amendment and resulting handoff identity.
Never use a new plan version to reinterpret completed evidence.
