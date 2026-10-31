# Iterative Development Workflow

`WORKLOAD_ROOT` is `development/three_stage_surrogate`.

This is the context-independent lifecycle policy for bounded development iterations. It defines
procedure, authority, state transitions, evidence, continuity, and closeout. Campaign intent lives
in `PLAN.md`; iteration-specific objectives, inputs, tasks, resources, and acceptance gates live in
`iterations/iterXXX.md` and `handoff/CURRENT.md`.

`PLAN.md` defines the user-approved campaign direction but grants no iteration or runtime
authority. `WORKFLOW.md` defines procedure and authority. The approved iteration report defines
the exact bounded work and runtime contract. `handoff/CURRENT.md` records live state. An iteration
may specialize an open campaign detail, but any proposed change to campaign direction remains
advisory until the user authorizes a separate `PLAN.md` revision outside the iteration lifecycle.

## 1. Core Rules and Durable Records

- One primary agent is the sole writer, scheduler operator, decision maker, and closeout owner.
- A required reviewer must be a different agent and remain read-only. Primary-agent self-review
  does not satisfy the review gate.
- A planning-only proposal, campaign plan, or prior closeout grants no initialization, Python,
  compute, scheduler, retry, cancellation, directory-creation, or commit authority.
- Read-only inspection and shell/text validation may occur before runtime approval. Running
  repository Python or repository scripts requires confirmed HPC context and an approved runtime
  contract and must use a compute node unless the selected HPC profile explicitly permits another
  safe context.
- Every initialized iteration includes at least one bounded compute-node validation, integration
  test, data-preparation task, or experiment. Project scaffolding and documentation-only planning
  do not consume iteration IDs.
- Acceptance gates become immutable when the kickoff package is approved. Do not change or
  reinterpret them after preflight or results.

| Record | Purpose | Update rule |
| --- | --- | --- |
| `PLAN.md` | Campaign objective, architecture, invariants, scope, exclusions, and progression | User-authorized revisions occur outside the iteration lifecycle; never use a later revision to reinterpret completed work. |
| `handoff/CURRENT.md` | Live state, campaign-plan identity, authority, jobs, next action, and next proposal | Update at every state transition. |
| `iterations/iterXXX.md` | Exact approved plan, campaign alignment, chronological evidence, and decision | Create only after kickoff approval; finalize at closeout. |
| `registry.csv` | Fixed-schema index of closed iterations | Add one row at closeout; do not add iteration-specific columns. |
| `ITERATION_SUMMARY.md` | Cumulative closeout evidence and decisions | Append at every closeout; preserve prior entries. |
| `summaries/iterXXX/` | Compact decision evidence required by the iteration plan | Populate only when eligible evidence exists. |
| `slurm/iterXXX/` | Canonical iteration-specific scripts, manifests, and validators | Treat as execution source. |
| `tools/` | Reusable validation, analysis, and release utilities | Keep one-off utilities with their iteration. |

Use templates only to initialize or repair their corresponding records. Keep `CURRENT.md` concise;
detailed history belongs in iteration reports, summaries, and the registry.

### Concise record and log policy

Repository records preserve decision-relevant evidence, not full command or monitoring transcripts.
The iteration report records the approved contract, material lifecycle transitions, submitted job
scope, terminal accounting, classified failures and corrections, acceptance evidence, decision,
limitations, and exact paths or hashes needed to recover the detailed evidence. Keep raw scheduler
and application logs, repeated monitoring snapshots, verbose test output, per-work-unit payloads,
and other reproducible bulk evidence in the approved external run directory. Summarize their
outcome and location in Git rather than copying their contents into repository records.

Do not repeat the same narrative across records. `CURRENT.md` holds live state and the next action;
the iteration report holds authoritative lifecycle evidence; `summaries/iterXXX/` holds only the
compact evidence needed to reproduce the decision; `ITERATION_SUMMARY.md` holds one cumulative
closeout synopsis; and `registry.csv` remains a one-row index. Concision must not omit material
failures, retries, rejected work, authority changes, job IDs, terminal states, gate results, or
limitations. An iteration plan may require additional compact evidence but need not restate this
policy.

## 2. State and Status Model

| Phase | Required action | Allowed change |
| --- | --- | --- |
| `pre_kickoff` | Recover state, assess the proposal, and resolve missing decisions | Read-only; no iteration-specific scaffold. |
| `ready_for_kickoff_approval` | Present one consolidated plan, runtime contract, goal, and authority package | No iteration-specific changes. |
| `initializing` | Create the approved report and update the handoff | Approved durable-record changes. |
| `preparing` | Lock inputs and prepare approved execution material | Contract-controlled paths only. |
| `review` | Obtain independent read-only review | Reviewer makes no changes. |
| `preflight` | Submit, monitor, and account for bounded preflight | Authorized scheduler actions. |
| `execution` | Submit and monitor locked work units | Authorized scheduler actions. |
| `evaluation` | Validate evidence and apply immutable gates | Approved analysis and records. |
| `closeout` | Cross-validate records and follow the commit or no-commit branch | Authorized closeout changes. |
| `closed` | Publish the validated handoff | No active or unaccounted jobs. |

Iteration statuses are `planned`, `in_progress`, `completed`, `failed`, and `blocked`. `rejected`
is a work-unit gate result, not an iteration status. `not_initialized` is a handoff-only sentinel.
Assign independent zero-padded IDs beginning with `iter001`. Every iteration records a unique run
slug and an exact mapping from work units to external output directories.

## 3. Required Schemas

### Planning-only proposal

A complete proposal states:

1. sequential ID and work type;
2. campaign-plan path, SHA-256 identity, applicable phase, alignment, and proposed deviation or `none`;
3. evidence-derived objective and optional hypothesis;
4. proposed inputs, upstream dependencies, identities, and trust assumptions;
5. bounded scope, work units, and exclusions;
6. tentative acceptance gates and decision rule;
7. proposed HPC profile, output root, resources, preflight, review, monitoring, retry,
   cancellation, and stop boundaries;
8. expected evidence, artifacts, and record updates; and
9. the fresh consolidated kickoff-approval boundary.

For `iter001`, the user supplies or approves the proposal at kickoff. For later iterations, copy
the complete proposal unchanged from the preceding closed report into `CURRENT.md`. A proposal is
not initialized work and grants no authority. If the user later revises that planning-only
proposal, preserve the closed report as historical evidence and record the superseding proposal,
revision provenance, and unresolved approval boundary in `CURRENT.md`. If a proposal conflicts
materially with the campaign plan, stop and ask the user whether to revise the proposal or
separately revise `PLAN.md` before kickoff.

### Consolidated kickoff package and runtime contract

After read-only bootstrap and clarification, present one package containing the finalized proposal
and stating:

1. kickoff goal, finite work-unit count, and stop conditions;
2. locked campaign-plan identity, applicable phase, alignment, and approved deviation or `none`;
3. confirmed HPC system and selected `development/hpc/` profile;
4. exact user-approved output root, layout, directory-creation authority, and retention assumptions;
5. locked dependencies, scope, exclusions, acceptance gates, and decision rule;
6. preparation, review, preflight, submission, monitoring, accounting, evaluation, records, and
   closeout authority;
7. exact resources and separate preflight and scheduler/resource retry boundaries;
8. bounded cancellation conditions and exact current-iteration job scope;
9. outside-sandbox authority for locked submission, job-scoped monitoring/accounting, and bounded
   cancellation; and
10. whether one closeout commit is authorized.

Ask once for approval of the complete package. Do not initialize an iteration, create its scaffold,
or perform runtime action before approval. Record the approved package, response, and timestamp in
both the iteration report and `CURRENT.md`.

A goal names the lifecycle stop boundary but grants no authority by itself. Remembered command
approval does not broaden the package. Treat omitted authority as declined. Application, code,
interface, schema, data, dependency, numerical, gate, resource-cap, or scope changes outside the
contract require a revised package and fresh approval.

When outside-sandbox Slurm access is needed, the package must explicitly ask whether it authorizes:

```text
1. sbatch for the locked submission and contract-authorized resubmission;
2. job-scoped squeue, scontrol show job, sacct, seff, job-history, and job-limits throughout
   monitoring and terminal accounting; and
3. scancel only for recorded current-iteration job IDs and only under the stated conditions.
```

## 4. Lifecycle Procedures

### A. Bootstrap, clarify, and recover

1. Read `PLAN.md`; record its path and SHA-256.
2. Read `handoff/CURRENT.md` and compare its current and active-iteration plan identities.
3. If an iteration is active or closed, read its report in full and up to two preceding reports.
4. Read relevant registry rows and summaries.
5. Read the proposed or approved HPC profile. If none is selected, leave site-dependent planning
   and scheduler actions unresolved.
6. Inspect Git state and reconcile recorded scheduler, dependency, and artifact state.
7. Verify that the proposal identifies its campaign phase and is aligned, or records an explicit
   deviation for user consideration in the kickoff package.
8. If an iteration is already initialized, verify its recorded package is complete, unexhausted,
   and unchanged, then resume from the recorded phase without asking again.

For `iter002` and later, first compare the preceding closed report and `CURRENT.md`. They must
contain the same complete next proposal unless `CURRENT.md` explicitly records a later user-directed
planning revision that supersedes the historical proposal. If they differ without that provenance,
or a material term is unclear, stop and ask the user. Clarification or proposal revision does not
grant initialization or runtime authority.

### B. Approve and initialize

1. Assess the proposal against Section 3 and build the complete kickoff package.
2. Present the entire package and ask once for approval before editing iteration-specific files.
3. If the response changes or omits a material term, revise and seek approval of the complete new
   package; do not combine partial responses into inferred authority.
4. After approval, create `iterations/iterXXX.md` from the template, set status `planned` and phase
   `initializing`, record the package and campaign alignment, and update `CURRENT.md`.
5. Create only the scaffold and external directories authorized by the package, then advance to
   `preparing`.

### C. Prepare and review

1. Lock declared inputs and dependencies, including the identities, schemas, provenance, and
   compatibility evidence required by the plan. Do not silently substitute inputs.
2. Create canonical scripts, configurations, manifests, and validators under `slurm/iterXXX/` when
   execution is required.
3. Create each approved run directory and materialize its self-describing submitted script and
   immutable configuration before submission.
4. Record canonical/submitted hashes, configuration equality, logs, dependencies, resources,
   repository/source identity, and exact submission command.
5. Obtain review by a different read-only agent. The reviewer checks the locked proposal and
   contract, dependencies, interfaces, paths, static validation, submitted-copy equality, and
   configuration/manifest equality. The primary agent must wait for that review result.
6. Record the reviewed source hash, findings, and `pass`, `pass_with_concerns`, or `block`. A
   `block` requires correction and passing re-review. Proceed past concerns only with recorded
   rationale.

Keep raw and large outputs outside Git. Follow the selected HPC profile for script format,
environment, storage, submission copies, and execution context. Keep one-off utilities with their
iteration; promote only reusable utilities.

### D. Preflight, execute, monitor, and account

1. Run the approved bounded compute-node preflight before substantive execution. It may validate
   imports, environment, paths, manifests, schemas, dependencies, launch behavior, and lightweight
   fixtures; it must not perform substantive work. A contract-authorized minimal preflight-only
   correction is separate from scheduler/resource retry authority.
2. For every submission, submit only the locked local copy from its approved run directory,
   capture the ID directly from `sbatch --parsable`, atomically record the mapping, update
   `CURRENT.md`, and perform an immediate scheduler-identity check.
3. Monitor the full recorded job or array scope using the selected profile's authoritative,
   job-scoped commands and a supported wait mechanism.
4. Continue until every expected job or array element has an authoritative terminal state in
   `sacct`. Record state, exit code, elapsed time, resources, and failure reason; record unavailable
   fields explicitly. Queue departure, an empty `squeue`, partial accounting, or unchanged state is
   not completion.
5. Submit substantive work only after preflight passes. Verify each independent work unit before
   submitting the next one. An identity mismatch stops further submissions.

Record each monitoring mechanism or command shape, job scope, active handle when applicable,
outcome, and reason in the ledger and handoff. Reuse an active handle instead of launching duplicate
monitors. If a mechanism fails or is unsupported, record that evidence before selecting a materially
different permitted strategy. Query or observation failure leaves workload state unknown and grants
no retry, cancellation, or resubmission authority.

### E. Maintain continuity and classify failures

Once status becomes `in_progress`, the primary agent remains responsible through terminal
accounting, classification, evaluation, records, validation, and closeout. Use the runtime's wait or
ongoing monitoring operation while work remains active; do not use repeated goal turns or user
updates as a polling timer.

Before voluntarily ending a turn or sending a final response, apply the **monitoring-continuity
gate**: re-read `CURRENT.md` and the active iteration's job ledger. If either records an
`in_progress` preflight or execution phase, an active job scope, or any expected job without
authoritative terminal accounting, remain in the supported wait or monitoring operation. Yield
only through the checkpoint rule below or when the platform forces an interruption.

A voluntary checkpoint is allowed only when a material user decision is required or an active
external wait has no supported wake mechanism. First record the phase, active scope, last evidence,
reason, and exact resume action in `CURRENT.md`.

Classify before acting:

- **Gate rejection:** completed eligible work fails a predeclared gate.
- **Scheduler/resource failure:** retry only within the approved same-scope boundary.
- **Preflight failure:** use only the approved minimal preflight correction and rerun.
- **Application/code/interface/schema/data/dependency/numerical failure:** preserve evidence and
  obtain fresh approval before changing execution material or retrying.
- **Observation-context failure:** preserve unknown state and reconcile it authoritatively.

Cancellation is permitted only when the contract covers the exact recorded job scope and its stated
condition is met. Record evidence and authority, cancel, then verify queue state and terminal
accounting. Cancellation does not authorize a fix or retry.

### F. Evaluate and decide

1. Verify completeness, identity, provenance, and current required artifacts.
2. Run only the validation and analysis declared by the approved plan.
3. Apply every immutable gate and the decision rule.
4. Record overall and work-unit results, limitations, and rationale without post-result
   reinterpretation.

### G. Close out

1. Finalize the report and record exactly one next state: a complete planning-only proposal or an
   explicit terminal declaration.
2. Record whether evidence suggests a `PLAN.md` amendment. Any recommendation is advisory only;
   closing the iteration does not authorize editing `PLAN.md`, and the user owns that separate
   decision outside this lifecycle.
3. Append one immutable summary section, add one fixed-schema registry row, and rebuild `CURRENT.md`
   with live state, plan identity, authority, evidence, decision, risks, next action, and any next
   proposal copied unchanged.
4. Run a final validator across the report, summary, registry, and handoff. Require agreement on
   iteration identity, status, work type, objective, scope, gate result, decision, dependencies,
   outputs, active-job state, and next direction among records that contain those fields. Require
   the iteration report and handoff to agree on campaign-plan identity and alignment; check other
   records only when their fixed schemas contain those fields.
5. Preserve validator identity, command, output, and result. A failure blocks closeout and commit.
6. Follow the approved branch: with commit authority, create at most one closeout commit and verify
   its controlled changes; otherwise preserve a validated bounded diff/source manifest labeled
   `validated_uncommitted`.
7. Mark phase `closed` only when no job is active or unaccounted, every failure is classified,
   evaluation and records are complete, validation passes, and the selected commit branch is
   satisfied.

Until step 7 is satisfied, follow Section E and do not issue a completion-style handoff.

## 5. Portability

Keep campaign intent in `PLAN.md`, lifecycle procedure here, and iteration intent in iteration
records. Keep scheduler commands, accounts, environments, storage rules, resources, and launch
conventions in the selected shared profile under `development/hpc/`. A profile constrains valid
operations and locations but never selects workload scope or grants authority.
