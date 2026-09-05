# ELM Diagnostic Development Workflow

`WORKLOAD_ROOT` is `development/ELM_diagnose`.

This is the canonical lifecycle policy for bounded ELM diagnostic development. It defines authority, state transitions, evidence, and closeout. Iteration-specific objectives, diagnostic inputs, tasks, dependencies, and acceptance gates belong in `iterations/iterXXX.md` and `handoff/CURRENT.md`.

This workflow establishes correct, validated diagnostic interfaces, provenance, and evidence. A correctness change may only restore a predeclared interface, schema, unit, provenance, or execution contract. Changes to diagnostic questions, input selection, comparison design, statistical interpretation, or performance expectations require a separately approved iteration plan.

## 1. Core Rules and Durable Records

- One primary agent is the sole writer, scheduler operator, decision maker, and closeout owner.
- A required reviewer must be a different agent and remain read-only. Primary-agent self-review does not satisfy the review gate.
- A planning-only proposal or prior closeout grants no initialization, Python, compute, scheduler, retry, cancellation, or commit authority. Only the user's approved consolidated kickoff package grants the authorities stated in that package.
- Read-only inspection and shell/text validation may occur before runtime approval. Running repository Python or repository scripts requires confirmed HPC context and an approved runtime contract and must use a compute node unless the selected profile explicitly permits another safe context.
- Every initialized iteration must include at least one bounded compute-node validation, integration test, or experiment. Planning and records maintenance alone are not iterations.
- Acceptance gates become immutable when the runtime contract is approved. Do not change or reinterpret them after preflight or results.

| Record | Purpose | Update rule |
| --- | --- | --- |
| `handoff/CURRENT.md` | Authoritative live state, authority, active jobs, next action, and next plan | Update at every state transition. |
| `iterations/iterXXX.md` | Detailed chronological evidence for one initialized iteration | Create only after consolidated kickoff approval; finalize at closeout. |
| `registry.csv` | Fixed-schema index of closed iterations | Add one row at closeout; do not add iteration-specific columns. |
| `ITERATION_SUMMARY.md` | Cumulative closeout evidence and decisions | Append at every closeout with objective, locked settings, quantitative evidence, and conclusion; preserve prior entries. |
| `summaries/iterXXX/` | Compact decision evidence required by the plan | Populate after eligible results exist. |
| `slurm/iterXXX/` | Canonical iteration-specific scripts, manifests, and validators | Treat as execution source. |
| `tools/` | Reusable validation, analysis, and release utilities | Keep one-off utilities with their iteration. |

Use templates only to initialize or repair their corresponding records. Keep `CURRENT.md` concise; detailed history belongs in iteration reports, summaries, and the registry.

## 2. State and Status Model

| Phase | Required action | Allowed change |
| --- | --- | --- |
| `pre_kickoff` | Recover state, assess the plan, and resolve missing kickoff decisions | Read-only; no new iteration report. |
| `ready_for_kickoff_approval` | Present one consolidated plan, runtime contract, goal, and authority package | No iteration-specific changes. |
| `initializing` | After approval, create `iterXXX.md` and update `CURRENT.md` with the approved package | Approved durable-record changes. |
| `preparing` | Lock inputs and create authorized scripts, configurations, and submitted copies | Contract-controlled paths only. |
| `review` | Obtain independent read-only review | Reviewer makes no changes. |
| `preflight` | Submit, monitor, and account for bounded preflight | Authorized scheduler actions. |
| `execution` | Submit and monitor locked work units | Authorized scheduler actions. |
| `evaluation` | Validate evidence and apply immutable gates | Analysis and durable records. |
| `closeout` | Cross-validate records and follow the commit or no-commit branch | Authorized closeout changes. |
| `closed` | Publish the validated handoff | No active or unaccounted jobs. |

Iteration statuses are `planned`, `in_progress`, `completed`, `failed`, and `blocked`. `rejected` is a work-unit gate result, not an iteration status. `not_initialized` is a handoff-only sentinel. Assign independent zero-padded IDs beginning with `iter001`. Default run slugs are `elm_diagnose_iterXXX_<work_unit>`; use a slug only within the exact user-approved output root and mapping.

## 3. Required Schemas

### Planning-only proposal

A complete proposal states:

1. sequential ID and work type;
2. evidence-derived objective and optional hypothesis;
3. proposed diagnostic inputs, upstream dependencies, and trust assumptions;
4. bounded scope, work units, and exclusions;
5. tentative acceptance gates and decision rule;
6. proposed site and resource envelope, preflight, review, retry, cancellation, and stop boundaries;
7. expected evidence, artifacts, and record updates; and
8. the fresh consolidated kickoff-approval boundary.

Diagnostic-input selection, including whether site-to-site comparison is in scope, belongs in the proposal. Do not infer a missing material plan field; ask the user before advancing.

For `iter001`, the user supplies the plan at kickoff. For `iter002` and later, the plan must be copied unchanged from the preceding closed report into `CURRENT.md`. A planning-only proposal does not authorize initialization or execution; it becomes the finalized plan only when included in the approved kickoff package.

### Consolidated kickoff package and runtime contract

After read-only bootstrap and clarification, present one package that contains the finalized plan
unchanged and adds:

1. kickoff goal, finite work-unit count, and stop conditions;
2. confirmed HPC system and selected `development/hpc/` profile;
3. exact user-approved output root, work-unit layout, directory-creation authority, and retention or backup assumptions;
4. preparation, review, preflight, submission, agent-owned monitoring, terminal accounting,
   evaluation, records, and closeout authority;
5. exact resources, supported monitoring and wait mechanism, and separate preflight and
   scheduler/resource retry boundaries;
6. bounded cancellation conditions and exact current-iteration job scope;
7. outside-sandbox authority for locked submission, job-scoped read-only monitoring and
   accounting, and bounded cancellation; and
8. whether one closeout commit is authorized.

Ask once for approval of the complete package. Do not initialize an iteration, create its scaffold, or perform authorized action until the package is approved. After approval, record the exact plan, contract, goal, response, and timestamp in both the iteration report and `CURRENT.md`.

A goal names the lifecycle stop boundary but grants no authority by itself. A remembered command approval does not broaden the approved package.

The request must explicitly ask:

```text
For this iteration, do you authorize the primary agent to execute outside the Codex sandbox:
1. sbatch for the locked submission and any resubmission already allowed by this contract;
2. job-scoped squeue, scontrol show job, sacct, seff, job-history, and job-limits commands throughout monitoring and terminal accounting, without another workflow-authority question;
3. scancel only for the current iteration's recorded job IDs and only under the cancellation conditions stated in this contract?
```

Treat omitted authority as declined. Application, code, interface, schema, data, dependency, numerical, gate, resource-cap, or scope changes outside the contract require a revised consolidated package and fresh approval.

## 4. Lifecycle Actions

### A. Bootstrap, clarify, and recover

1. Read `handoff/CURRENT.md`. If an active or closed iteration exists, read its `iterations/iterXXX.md` report in full and up to two preceding iteration reports. For pre-kickoff `iter001`, no iteration report is expected.
2. Read relevant `registry.csv` rows and summary files.
3. Read the selected site profile under `development/hpc/` when `CURRENT.md` or the active package names one. If no profile is selected, treat site selection and scheduler commands as unresolved.
4. Inspect Git state and reconcile recorded scheduler and artifact state before diagnosing drift.
5. Verify declared diagnostic-input and dependency identity and availability when they have been proposed or locked.
6. If an iteration is already initialized, verify its recorded kickoff package is complete, unexhausted, and unchanged, then route work from the recorded phase without asking again.

For `iter002` and later, confirm that the closed report and `CURRENT.md` contain the same complete next plan. If they differ or a material field is unclear, stop and ask the user. For a new iteration, resolve every missing decision before seeking approval. Clarification questions do not grant authority.

### B. Approve and initialize an iteration

1. Assess the plan against the planning schema and build the complete consolidated kickoff package.
2. Present the entire package and ask once for approval before editing iteration-specific files.
3. If the response modifies or omits a material term, revise the package and seek one approval of the new complete package; do not treat partial answers as cumulative execution authority.
4. After approval, create `iterations/iterXXX.md` from the template, set status `planned` and phase `initializing`, record the package, and update `CURRENT.md`.
5. Create only scaffolding and external directories authorized by the package, then advance to `preparing`.

### C. Prepare and review

After kickoff-package approval:

1. Lock declared diagnostic inputs and dependencies, including only the schemas, identities, provenance, and compatibility evidence required by the approved iteration plan. Do not silently substitute inputs.
2. Create canonical scripts, configurations, manifests, and validators under `slurm/iterXXX/` when execution is required.
3. Create each approved run directory. Materialize its self-describing submitted script and immutable configuration there before submission.
4. Verify and record canonical/submitted byte identity, configuration/manifest equality, hashes, logs, dependencies, resources, repository/source identity, and exact submission command.
5. Obtain review by a different read-only agent and record its reviewer identity or handle. After
   starting the review, the primary agent must wait on that existing handle and retrieve its result
   rather than ending the turn while review remains pending. Use the runtime's supported blocking
   wait operation; do not repeatedly issue reviewer-list or review-status operations, start a
   duplicate review, or replace a reviewer merely because its result is not yet available. If a
   blocking wait returns without a result, resume waiting on the same handle unless the wait
   operation explicitly reports that the reviewer or handle failed or became unavailable; only
   after recording that outcome may the primary agent start a replacement.
   The reviewer checks the locked plan and contract, diagnostic inputs, interfaces, paths, static
   validation, submitted-copy equality, and configuration/manifest equality.
6. Record reviewed source hash, findings, and `pass`, `pass_with_concerns`, or `block`. A `block` requires correction, repeated static checks, and passing re-review. Proceed past concerns only with recorded rationale.

Keep raw and large outputs outside Git. Write human-readable Slurm scripts following the selected site profile. Keep one-off validators under the iteration; promote only reusable utilities.

### D. Submit, monitor, and account for preflight and execution work

1. Before substantive execution, run the approved bounded compute-node preflight. It may validate
   imports, environment, paths, manifests, schemas, dependency identity, launch behavior, and
   lightweight fixtures; it must not perform substantive model execution, data generation,
   optimization, or iteration evaluation. One contract-authorized minimal preflight-only
   correction and rerun is separate from scheduler/resource retry authority.

2. For every scheduler submission, including preflight and validators submitted through Slurm:

   a. submit only the locked local copy from its approved run directory;

   b. capture the job ID directly from `sbatch --parsable`;

   c. atomically record the work unit, parent job ID and approved job or array scope, submitted
      script, run directory, configuration hash, dependencies, resources, and submission time;

   d. set status `in_progress`, record the active phase and job in `CURRENT.md`, and perform an
      immediate `squeue` or `scontrol` identity check; and

   e. begin agent-owned monitoring using the selected site profile's command shapes, supported
      wait mechanism, output-suppression rules, and bounded-backoff behavior.

3. After monitoring begins, continue it until every expected job or array element has an
   authoritative terminal state in `sacct` and its state, exit code, elapsed time, available
   resources, and failure reason have been recorded. Terminal states include `COMPLETED`, `FAILED`,
   `TIMEOUT`, `CANCELLED`, `OUT_OF_MEMORY`, and other Slurm terminal states. A job remaining
   `PENDING` or `RUNNING`, an unchanged scheduler snapshot, a completed subset, an empty `squeue`
   response, or partial accounting does not satisfy this criterion.

4. Before starting or restarting a wait or monitoring operation, apply the monitor-strategy retry
   gate:

   a. Check `CURRENT.md` and the current iteration's `Provenance and Job Ledger` monitoring/retry
      notes for prior attempts using the same mechanism or command shape and job scope.

   b. In that ledger, record the mechanism or command shape, process or session handle when active,
      outcome (`active`, `handoff`, `failed`, `unsupported`, or `finished`), and a brief reason.
      While a monitor is active, mirror its job scope, mechanism or command shape, handle, and
      outcome in `CURRENT.md`.

   c. If a foreground monitor was terminated because the agent runtime or terminal wrapper did not
      preserve its process handle, mark that mechanism `unsupported` in the ledger and clear the
      active-monitor entry in `CURRENT.md`. Do not relaunch the same or materially equivalent
      foreground command.

   d. Internal bounded retries for a transient `squeue` or `sacct` query failure are not strategy
      restarts. After those retries are exhausted, classify the strategy outcome before taking
      another action.

   e. Retry a failed strategy only when recorded evidence shows that the failure condition changed,
      such as a corrected command defect or a materially different runtime capability. Record the
      revised mechanism or command shape separately and permit only one new capability attempt.

   Do not run a separate capability-verification operation. For this section, an available strategy
   is one exposed by the active agent runtime and not already retired by recorded evidence. Treat
   its first actual monitoring invocation as the bounded capability attempt.

   While work remains active, start the selected non-retired operation once and observe its outcome.
   If it yields an ongoing process or session handle, continue waiting on that same handle. Do not
   use goal continuation as a polling timer, issue back-to-back scheduler queries, or generate
   user-facing updates solely to report unchanged state. Report only material state transitions,
   query failures, terminal accounting, or a user-requested snapshot.

5. When observation hands off or a job leaves `squeue`, reconcile the recorded job scope through
   job-scoped `sacct`. If accounting is absent or incomplete, preserve state as pending or unknown
   and recheck with bounded backoff using supported wait and accounting operations. Transitioning
   between operations does not complete monitoring; step 3 remains the completion criterion.

6. Apply the monitoring continuity gate before voluntarily ending a turn or sending a final
   response. Re-read `CURRENT.md` and the current iteration's `Provenance and Job Ledger`. The
   monitoring stage remains active while `CURRENT.md` records `in_progress` preflight or execution,
   an active job scope, or an unsatisfied step 3 criterion. The primary agent must remain in the
   supported wait or monitoring operation rather than voluntarily end the turn or send a
   completion-style response. Once step 3 is satisfied, record the transition and proceed to
   classification or evaluation. Any earlier yield must follow Section E's checkpoint rule or be a
   platform-forced interruption.

7. If the selected monitoring strategy is unavailable, is lost, or fails the monitor-strategy
   retry gate, record its outcome in the current iteration's `Provenance and Job Ledger`, clear the
   active-monitor entry in `CURRENT.md`, and select the next materially different approach allowed
   by the site profile and runtime contract. If none exists, use Section E's checkpoint rule. Handle
   monitoring-context and query failures under Section E.

8. Submit substantive work only after preflight passes. Submit only locked material, and verify
   each independent work unit's scheduler identity before submitting the next one. An identity
   mismatch stops further submissions.

### E. Maintain continuity and handle failures

Once `in_progress`, the primary agent remains responsible through monitoring, classification,
authorized next steps, evaluation, records, validation, and closeout.

The workflow goal owns lifecycle continuity but is not a clock. When progress depends on elapsed
time, the primary agent must enter the applicable agent wait or ongoing terminal-monitoring
operation. It must not repeatedly start new goal turns merely to discover that no scheduler state
has changed.

When the next authorized action is immediately available, the primary agent must perform it instead
of yielding control.

A voluntary checkpoint is permitted only when a fresh material user decision is required or an
active external wait has no supported wait or wake mechanism. First record the current phase,
active job or reviewer scope, last authoritative evidence, reason for yielding, and exact resume
action in `CURRENT.md`; then ask the narrow required question when applicable. A checkpoint is not
a completion claim and does not exhaust the approved package.

Record a platform-forced interruption when control resumes and recover from authoritative state.
Emit an intermediate status only for a material transition, failure, or user-requested snapshot;
do not repeat unchanged-state messages.

Classify before acting:

- **Gate rejection:** completed work fails a predeclared gate; record it separately from status.
- **Scheduler/resource failure:** retry only within the approved same-scope boundary.
- **Preflight failure:** use only the approved minimal preflight correction/rerun.
- **Application/code/interface/schema/data/dependency/numerical failure:** preserve diagnostics and obtain fresh approval before changing execution material or retrying.
- **Observation-context failure:** preserve unknown state and reconcile it authoritatively; loss of
  a monitoring session grants no retry, cancellation, or resubmission authority.

Emergency cancellation is allowed only when the contract covers recorded job IDs and a proven universal pre-execution defect will make all affected work fail. Record evidence and authority, issue `scancel`, then verify queue state and terminal accounting. Cancellation does not authorize a fix or retry.

### F. Evaluate and decide

1. Verify result completeness, identity, provenance, and existence of current required artifacts.
2. Run validation and analysis declared by the plan; aggregate or compare only when required.
3. Apply every immutable gate and the decision rule.
4. Record the overall acceptance result, work-unit results, limitations, and rationale without post-result reinterpretation.

### G. Close out

1. Finalize the iteration report and record exactly one next state: a complete planning-only proposal following Section 3, or an explicit terminal declaration that the workflow is complete, blocked, or intentionally stopped. Do not leave the next direction unspecified when evidence supports a bounded proposal.
2. Append one immutable `ITERATION_SUMMARY.md` section with objective, locked settings, quantitative evidence, gate outcome, and conclusion. Add one fixed-schema registry row and rebuild `CURRENT.md` with live state, runtime authority, evidence, gate result, decision, risks, next action, and artifact references. Copy any next plan unchanged.
3. Run the final validator across the iteration report, summary, registry, and handoff. Require iteration ID, status, work type, objective, bounded scope, overall gate result, and decision to agree across all four. Cross-check dependency identity, output root, summary path, detailed evidence, current artifacts, next action, and next-plan state among records that contain those fields.
4. Preserve validator identity, command, output, and result. A failed validator blocks closeout and commit.
5. Follow the approved branch: with commit authority, create at most one closeout commit and verify its controlled changes; without it, preserve a validated bounded diff/source manifest and label the handoff `validated_uncommitted`.
6. Mark phase `closed` only when no job is active or unaccounted, every failure is classified, evaluation and records are complete, the validator passes, and the selected commit branch is satisfied.

Until step 6 is satisfied, follow Section E's continuity and checkpoint rules and do not send a
completion-style response.

## 5. Portability

Keep lifecycle policy here and iteration intent in iteration records. Keep scheduler commands, accounts, environments, storage rules, resources, and launch conventions in the selected shared profile under `development/hpc/`. A site profile constrains valid output locations but never selects one for the user.
