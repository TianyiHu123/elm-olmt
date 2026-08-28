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

After read-only bootstrap and clarification, present one package that contains the finalized plan and states:

1. kickoff goal, finite work-unit count, and stop conditions;
2. confirmed HPC system and selected `development/hpc/` profile;
3. exact user-approved output root, work-unit layout, directory-creation authority, and retention or backup assumptions;
4. locked diagnostic inputs, dependencies, scope, exclusions, acceptance gates, and decision rule;
5. preparation, review, preflight, submission, continuous monitoring, terminal accounting, evaluation, records, and closeout authority;
6. exact resources, monitoring cadence and permitted exceptions, and separate preflight and scheduler/resource retry boundaries;
7. bounded cancellation conditions and exact current-iteration job scope;
8. outside-sandbox authority for locked submission, job-scoped read-only monitoring and accounting, and bounded cancellation; and
9. whether one closeout commit is authorized.

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
5. Obtain review by a different read-only agent. The reviewer checks the locked plan and contract, diagnostic inputs, interfaces, paths, static validation, submitted-copy equality, and configuration/manifest equality.
6. Record reviewed source hash, findings, and `pass`, `pass_with_concerns`, or `block`. A `block` requires correction, repeated static checks, and passing re-review. Proceed past concerns only with recorded rationale.

Keep raw and large outputs outside Git. Write human-readable Slurm scripts following the selected site profile. Keep one-off validators under the iteration; promote only reusable utilities.

### D. Submit preflight and execution work

Every scheduler submission, including preflight and any validator submitted through Slurm, follows the same ledger:

1. submit only the locked local copy from its approved run directory;
2. capture the job ID directly from `sbatch --parsable`;
3. atomically record work unit, job ID, submitted script, run directory, configuration hash, dependencies, resources, and submission time;
4. set status `in_progress`, record the active phase and job in `CURRENT.md`, and perform an immediate `squeue` or `scontrol` identity check; and
5. monitor with authoritative job-scoped commands and record terminal state, exit code, elapsed time, resources, and failure reason.

The contract must record a monitoring cadence. Do not query an active job more frequently than that cadence except for the immediate post-submission identity check, a user request, terminal accounting, or reconciliation of a recorded unknown state or observed failure. Follow the selected profile for its default cadence, command shapes, and bounded-backoff behavior.

Run a bounded compute-node preflight before substantive work. It may validate imports, environment, paths, manifests, schemas, dependency identity, launch behavior, and lightweight fixtures; it must not perform substantive model execution, data generation, optimization, or iteration evaluation. One contract-authorized minimal preflight-only correction and rerun is separate from scheduler/resource retry authority.

After preflight passes, submit only locked substantive work. Verify one job before submitting the next independent work unit. An identity mismatch stops further submissions. Apply the selected profile's execution-context gate to all scheduler evidence. Query, transport, sandbox, authentication, controller, or connection failure leaves state unknown; it is not a workload failure and authorizes no retry, resubmission, cancellation, or completion claim.

### E. Maintain continuity and handle failures

Once `in_progress`, remain active through terminal accounting, classification, authorized next steps, evaluation, records, validation, and closeout. Submission, pending state, a status message, or partial completion is not a stop condition. A platform-forced interruption must be recorded in `CURRENT.md` and resumed from authoritative scheduler state.

Classify before acting:

- **Gate rejection:** completed work fails a predeclared gate; record it separately from status.
- **Scheduler/resource failure:** retry only within the approved same-scope boundary.
- **Preflight failure:** use only the approved minimal preflight correction/rerun.
- **Application/code/interface/schema/data/dependency/numerical failure:** preserve diagnostics and obtain fresh approval before changing execution material or retrying.
- **Observation-context failure:** preserve unknown state and reconcile it authoritatively.

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

Before any completion-style response, confirm all conditions in step 6. Until then, report only that the iteration remains active and identify the next workflow action.

## 5. Portability

Keep lifecycle policy here and iteration intent in iteration records. Keep scheduler commands, accounts, environments, storage rules, resources, and launch conventions in the selected shared profile under `development/hpc/`. A site profile constrains valid output locations but never selects one for the user.
