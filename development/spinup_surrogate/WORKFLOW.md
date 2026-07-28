# Spinup Surrogate Workflow

Use this repository-tracked playbook for spinup-surrogate experiment iterations. It is the
canonical instruction source; do not require project-specific Cursor skills.

## Durable Records and Ownership

One primary agent owns all state changes, Slurm submission/cancellation, and closeout.
Read-only reviewers may independently check a metric comparison or failure diagnosis, but
must not edit records or operate jobs.

| Record | Role | Update rule |
| --- | --- | --- |
| `handoff/CURRENT.md` | Live control record: current iteration, phase, active job IDs, next action | Update at scaffold, submission, terminal-state, and closeout transitions. |
| `iterations/iterXXX.md` | Detailed, append-only evidence for one iteration | Create at planning; update the ledger as work occurs; finalize at closeout. |
| `registry.csv` | One-row index of completed/failed iterations | Update only at closeout. |
| `ITERATION_SUMMARY.md` | Cumulative cross-iteration scientific and operational summary | Update at every iteration closeout with objective, locked settings, quantitative evidence, and conclusion. |
| `summaries/iterXXX/` | Compact metrics and stability evidence | Populate after successful aggregation. |
| `slurm/iterXXX/` | Canonical submission scripts for an iteration | Treat as the source of truth; materialize a variant-local, self-describing submission copy before each `sbatch`. |
| `tools/` | Reusable, no-training validation utilities | Keep only iteration-independent utilities here; promote or remove one-off validation code at closeout. |

Use `templates/iteration.md` to create an iteration record and
`templates/current-handoff.md` only to initialize or repair the handoff format. Do not
overwrite historical records with a template.

## Status and Naming

Use these iteration statuses consistently: `planned`, `in_progress`, `completed`,
`failed`, and `blocked`. Variant-level results may additionally be `rejected` when a
predeclared scientific validity rule excludes that variant without blocking the iteration.

- Assign zero-padded sequential IDs: `iter001`, `iter002`, and so on.
- Record a `run_slug` in every iteration report and derive all output directories from it.
- Default new run slug: `spinup_surrogate_iterXXX_<variant>`, where `XXX` is the iteration
  ID's numeric suffix. If a legacy or site-specific path differs, record the exact mapping
  in the iteration report before submission.

## Runtime Contract

Before any execution, record the following in the active iteration report and
`CURRENT.md`:

1. **Run mode:** a finite number of rounds or `run-until-stopped`, plus stop conditions.
2. **HPC and site profile:** user confirms the active session is on HPC and selects a profile
   under `development/hpc/` (for example `perlmutter.md`).
3. **Submission authority:** explicit authorization for Slurm preparation, submission,
   monitoring, a one-time preflight-validation retry, and a single matrix retry within the
   stated scope.
4. **Resource policy:** explicit resources, or calibrated mode with memory and walltime caps.
5. **Commit authority:** whether one closeout commit per completed iteration is authorized.

The contract is scoped to the declared run. A new iteration outside that scope, a resource
increase beyond the cap, or a code/configuration change needed to retry requires fresh user
authorization, except for the validation-only retry defined below. Do not create a commit unless
closeout-commit authority was explicitly given.

### Kickoff Goal Contract

Start each execution session with an explicit session goal for the finite iteration. The goal must
name the iteration and its complete stop boundary; writing a `/goal` example in this file does not
create the session goal by itself. The user or primary agent must establish the goal through the
session's goal mechanism, then record the goal text or an unambiguous summary in the iteration
report and `CURRENT.md`.

Use a full-execution goal when the user authorizes the complete lifecycle:

```text
/goal Execute iterXXX according to development/spinup_surrogate/WORKFLOW.md:
complete planning and authorized scaffolding, independent review, bounded preflight,
submission, continuous monitoring, terminal accounting, failure classification,
aggregation, gate evaluation, record updates, handoff validation, and authorized closeout.
Do not stop before a recorded workflow stop condition.
```

Use a planning-only goal when execution authority has not been granted:

```text
/goal Prepare the planning-only iterXXX proposal according to
development/spinup_surrogate/WORKFLOW.md; do not scaffold, submit, or run jobs.
```

A goal defines the completion objective; it does not grant HPC execution, retry, cancellation,
or commit authority. Those authorities must still be stated in the runtime contract and approved
by the user. A goal also does not replace `CURRENT.md` checkpoints, Slurm reconciliation, the
pre-return gate, or final handoff cross-validation.

### Required authorization request

At the start of every new iteration, after planning has identified the matrix and before any
execution or scheduler action, the primary agent must explicitly request and record a single
runtime-contract response covering all of the following:

1. confirmation that the active session is on the selected HPC system;
2. the finite run mode and its task/round count;
3. authorization to prepare, submit, and monitor the locked matrix, including a bounded
   no-training preflight;
4. the exact resource profile, one automatic validation-only retry, and the separate one-retry
   boundary for scheduler/resource matrix failures;
5. whether one closeout commit is authorized.

The request must name the selected `development/hpc/` profile and state that application or
code/configuration failures stop for fresh authorization. A plain approval is sufficient only
when the request states all five items. Record the response verbatim or as an unambiguous
summary in both the active iteration report and `handoff/CURRENT.md` before submission.

## Bootstrap

Before planning a new round:

1. Read `handoff/CURRENT.md`.
2. Read the latest iteration report in full and the two preceding reports, when available.
3. Read the relevant `registry.csv` rows and summary JSON files.
4. Read the selected site profile in `development/hpc/`.
5. Find the preceding iteration's proposed next-iteration plan in both its `iterXXX.md` record
   and `handoff/CURRENT.md`. Verify that the two records agree on the retained baseline and
   proposed sequential ID.
6. Assess plan quality before scaffolding. A plan is actionable only when it states an
   evidence-derived objective/hypothesis, tentative candidate matrix and seed count, comparison
   baseline and acceptance gates, proposed site/resources and retry boundaries, expected artifacts,
   and the new-runtime-contract boundary. If the plan is absent, contradictory, or materially
   obscure on any of those points, stop and ask the user to propose or clarify the next plan; do
   not infer a scientific matrix, create iteration artifacts, or request execution authority.
7. Determine the next iteration ID and run slug from the validated proposal.
8. Record a focused objective, fixed controls, candidate matrix, acceptance gates, retry
   policy, and expected artifacts in the new iteration report.

The report's decision rules are authoritative for that iteration. They must state how
multiple targets are combined, the required seed count, metric/tail/IQR/stability gates, and
the tie-breaker. Do not infer an automatic promotion rule when a report does not define one.

## Iteration Lifecycle

### 1. Plan and prepare

1. Create `iterations/iterXXX.md` from the template; set the status to `planned`.
2. Create canonical scripts under `slurm/iterXXX/` and expected summary paths.
3. Update `CURRENT.md` to show the active iteration and `planning` phase.
4. Before submit, record:
   - canonical and submitted script paths and SHA-256 hashes;
   - the variant-local configuration manifest or rendered configuration block and its SHA-256 hash;
   - the variant-local standard-output and standard-error paths;
   - commit hash;
   - a hash and path for the relevant uncommitted diff or source manifest when the tree is
     dirty;
   - selected site profile, resource request, exports, and exact submission command.
5. Confirm the selected site's pre-submit requirements in its profile. Keep raw outputs in
   the configured scratch root, not Git.
6. For every submitted variant, create `<scratch-output-root>/<run_slug>/` before submission.
   Put the exact submission copy, immutable configuration manifest, and Slurm standard/error logs
   directly at that variant root; do not add `slurm/` or `logs/` subdirectories. The submission
   copy must be self-describing for that variant: it must either render the locked variant
   configuration into the script or source the configuration manifest beside it. Submit that
   variant-local copy, not the repository canonical script. The primary submission procedure is to
   `cd` into that run directory and invoke `sbatch ./submit_<variant>.slurm`; do not submit from a
   different caller directory with an absolute script path. Use the Puma profile's explicit
   `</dev/null>` safeguard when submission occurs inside a manifest-reading loop. Record the
   canonical source, submitted copy, configuration, run directory, and log paths in the iteration
   ledger.
8. Write canonical and submitted Slurm scripts in the human-readable format required by the
   selected site profile: one variable assignment per line, no combined dependent assignments,
   multiline long commands, and explicit `#SBATCH --output`/`#SBATCH --error` directives (`%A_%a`
   for arrays, `%j` otherwise).
9. Keep iteration-specific Slurm manifests, variant matrices, and preflight scripts under
   `slurm/iterXXX/`. A validation utility must be promoted to `tools/` only when it is reusable
   across iterations; otherwise remove it at closeout after its evidence is recorded.
10. When the iteration introduces or changes execution-affecting code, Slurm scripts, manifests,
   variant-local configuration rendering, or preflight utilities, obtain one independent,
   separately scoped **read-only reviewer subagent** check before the compute-node preflight.
   This review must be performed by a different agent from the primary agent; it is not a
   primary-agent self-review. The reviewer subagent verifies the locked matrix and runtime
   contract, fixed-root/import behavior, artifact paths, and static checks; it must not edit
   files, submit/cancel jobs, update records, or make the final decision. Record its concise
   findings, outcome (`pass`, `pass_with_concerns`, or `block`), and the reviewed source hash in
   the iteration ledger. On `block`, the primary agent must revise the identified
   execution-affecting material, rerun static checks, and obtain a passing re-review before
   preflight or submission. The primary agent may proceed past `pass_with_concerns` only after
   recording a concrete rationale; it may not override `block`. A records-only iteration does not
   require this check.
11. Before a production matrix, run the contract-authorized bounded compute-node preflight. It
   must verify absolute-path repository imports, locked manifests/configuration, and its declared
   no-training invariants.

### 2. Submit and monitor

1. Submit only the locked matrix, normally one job or array per variant.
2. Capture each returned job ID directly from `sbatch --parsable`; never transcribe or infer a
   job ID manually. Immediately record an atomic mapping of variant, job ID, submitted script,
   run directory, configuration hash, and submission timestamp in the iteration ledger, then
   update `CURRENT.md` to `in_progress` with the active job set.
3. Before submitting the next variant, perform an independent post-submission identity check with
   the site's supported `squeue` or `scontrol` interface. Confirm the job ID, variant/job name,
   working directory, submitted script, array range, and exported configuration path match the
   locked manifest and recorded mapping. Preserve the command/output as submission evidence. If
   any identity check mismatches, stop further submissions and classify the submission; do not
   assume the job is safe to run.
4. Monitor the complete job set concurrently using the selected site's documented queue and
   accounting commands.
5. Record terminal state, exit code, elapsed time, resource diagnostics, and failure reason
   for every job.

After an approved submission, the primary agent must remain in the active iteration lifecycle
until terminal accounting is recorded for the complete job set and every non-completion is
classified. Poll at a bounded cadence and autonomously perform only the subsequent actions already
authorized by the runtime contract. Do not issue a terminal handoff while jobs are active; a
user-facing message during execution is a status update only. On a platform-forced interruption,
record the time and active job set in `CURRENT.md`; the next active agent must resume with
`squeue`/`sacct` before any other iteration action.

### Primary-Agent Continuity Rule

Once an iteration is `in_progress`, the primary agent must not autonomously interrupt, end, or
hand off its own lifecycle before the workflow reaches a recorded stop condition. In particular,
it must not treat submission, a status response, a pending queue, an optional monitoring helper,
or a completed subset of jobs as permission to return control and leave the iteration unfinished.
Remain active through monitoring, failure classification, every runtime-contract-authorized next
step, aggregation/decision when eligible, and closeout. Only an explicit user stop/replacement
request, a contract-defined stop condition, or a platform-forced interruption may suspend this
continuity. A platform-forced interruption must be logged in `CURRENT.md` and resumed from Slurm
state before any other action.

#### Pre-return gate

Before yielding control or sending a completion-style response, the primary agent must perform this
gate and record the result in the iteration ledger or durable state checkpoint:

1. Confirm that no submitted job is still `PENDING`, `RUNNING`, or otherwise unaccounted for;
   if jobs remain active or accounting is incomplete, continue monitoring.
2. Confirm that every non-completion has been classified and that all runtime-contract-authorized
   retries, cancellations, and reconciliation steps are finished.
3. Confirm that aggregation, gate evaluation, selection/no-promotion, and required artifact
   validation are complete when the iteration is eligible for them.
4. Confirm that `iterXXX.md`, `ITERATION_SUMMARY.md`, `registry.csv`, and `CURRENT.md` have been
   updated and cross-validated when closeout is required.
5. Confirm a recorded workflow stop condition: exhausted run mode, report-defined convergence,
   blocked failure, explicit user stop/replacement, or completed closeout.

Until all applicable checks pass, the agent may send only a status update that explicitly states
the iteration remains `in_progress` and identifies the next monitoring or workflow action. It must
never issue a completion-style response, final handoff, or claim that the work is done while jobs,
terminal accounting, aggregation, decision, records, handoff validation, or closeout remain
unfinished.

Direct `squeue`/`sacct` checks are the default. `/loop` is optional only when the user
requests unattended status checks; it must not submit work or advance a round. Its optional status
does not remove the primary agent's continuity, monitoring, or terminal-accounting obligation.

### 3. Handle failures and rejections

Classify each non-completion before acting:

- **Scientific rejection:** a predeclared validity rule rejects the variant. Record evidence
  and continue only if the iteration report explicitly permits other independent variants to
  continue.
- **Resource or scheduler failure:** make one minimal resource/configuration adjustment within
  the runtime contract and retry once.
- **Preflight validation failure:** if the failure occurs before training/model execution, the
  primary agent may make one minimal validation-only import, launch, or configuration correction
  and rerun that same bounded preflight once. Record the diagnostic, correction, source/config
  hashes, and rerun job ID. This retry does not consume a matrix variant's retry budget. A second
  validation failure, a changed failure class, any change to scientific controls, or a failure
  after training begins stops for fresh user authorization.
- **Application or code failure:** preserve the diagnostic bundle and obtain fresh
  authorization before changing code/configuration or retrying.

If a variant is blocked after its allowed retry, mark the iteration `blocked` or `failed` as
defined by its decision rules; cancel remaining active jobs when the report's fail-fast policy
requires it. Do not aggregate incomplete variants or select a winner. Record a debug bundle
with job IDs, states, exit codes, reasons, provenance, accounting evidence, and the next
hypothesis; then update `CURRENT.md`.

### Emergency cancellation authority

The runtime contract may grant the primary agent bounded authority to cancel active jobs from
the current iteration without requesting a second interactive approval, but only for a proven
universal pre-training launcher, configuration, or application defect that will cause all
remaining jobs in the same locked round to fail. This authority does not cover scientific
disagreement, isolated leaf failures, resource tuning, code changes, or retry submission.

Before cancelling, record the failing evidence, affected iteration/job set, and reason in the
iteration ledger. Issue the site-supported `scancel` command immediately, then verify both queue
state and terminal accounting. Record cancellation-request, approval, and execution timestamps;
if command approval is pending, mark cancellation as potentially ineffective and continue
reconciling state rather than assuming the jobs will stop. Any fix or retry beyond the declared
boundary still requires fresh authorization.

### 4. Aggregate and decide

For every eligible completed variant:

1. Aggregate `surrogate_spinup_stats_seed*.json` with `summarize_spinup_stats.py`.
2. Copy compact summaries to `summaries/iterXXX/`.
3. Run any iteration-specific analysis, such as feature-stability diagnostics.
4. Evaluate the report's explicit gates and record the comparison table and rationale.

An optional read-only reviewer may validate summaries against those gates before the primary
agent records the final decision.

### 5. Close out

1. Finalize `iterations/iterXXX.md`, including outcome, evidence, decision, next action, and
   status. It must contain a **planning-only proposed next-iteration plan** derived from the
   completed result: sequential ID, retained baseline, focused hypothesis, tentative locked
   matrix, fixed controls, acceptance gates, resource/retry proposal, expected artifacts, and an
   explicit new-runtime-contract requirement. Do not leave the next scientific direction
   unspecified when the completed evidence supports a bounded proposal.
2. Update `ITERATION_SUMMARY.md` with the completed iteration's detailed objective, fixed controls
   and variant settings, seed/resource context, quantitative evidence (including absolute RMSE and
   normalized metrics when available), gate outcome, and conclusion/retained baseline. Preserve
   prior entries as historical evidence; do not replace them with a high-level recap.
3. Add or update the corresponding `registry.csv` row. Its status, objective, seed range, variant
   set, retained baseline or explicit no-promotion result, summary path, and closeout conclusion
   must agree with the iteration report.
4. Rebuild `handoff/CURRENT.md` as the live handoff for the newly completed iteration. At
   closeout, update these sections (or clearly equivalent headings) and no longer leave their
   values copied from an older iteration:
   - `Live State`: active iteration, status, phase, active job IDs, site profile, and a
     last-updated timestamp;
   - `Current Objective` and `Best Evidence So Far`: the concise objective, quantitative headline
     evidence, gate outcome, and retained-baseline/no-promotion decision;
   - `Current Risks or Blockers` and `Next Action`;
   - `Next Iteration Plan (Planning Only)`: **copy (`cp`) the plan that exists in
     `iterations/iterXXX.md`**; copy it from the completed iteration report without re-authoring
     or silently changing it,
     and preserve its ID, hypothesis, controls, matrix, gates, resources/retry boundary, expected
     artifacts, required user decisions, and new runtime-contract boundary;
   - `Next Session Start Protocol`, including the current report/profile paths and the fresh
     runtime-contract gate;
   - `Artifact Paths`, with current report, registry, summary, canonical scripts, and
     scratch-output references;
   - `Files Modified in Repo (latest completed iteration)` and `Latest Iteration Reference`.
5. Mark older plans and older iteration narratives explicitly as historical. `CURRENT.md` must not
   call a completed iteration planning-only, point `Latest Iteration Reference` at an older
   iteration, retain an obsolete `Ready/Blocked` statement, or instruct the next session to
   validate an already completed iteration.
6. Run the **handoff validator** as the final closeout gate. Its primary job is cross-validation,
   not scientific re-analysis, across exactly these four records:
   `iterations/iterXXX.md`, `ITERATION_SUMMARY.md`, `registry.csv`, and `handoff/CURRENT.md`.
   It must verify at minimum:
   - the same latest iteration ID, status, retained baseline/no-promotion decision, and conclusion;
   - matching objective, variant count/policies, seed range, and summary/artifact paths;
   - matching quantitative headline metrics and gate outcome where each record claims them;
   - a current `CURRENT.md` next-iteration plan that matches the report's plan and is marked
     planning-only with a fresh runtime-contract requirement;
   - no active jobs for a completed/closed iteration and no stale latest-iteration references;
   - every referenced report, summary, script, and required artifact exists;
   - no contradictory status, phase, baseline, or next-action statements.
   Preserve the validator command, version/hash, output, and pass/fail result in the iteration
   ledger. A failed cross-validation blocks closeout, the closeout commit, and the final handoff
   until corrected and rerun.
7. If the runtime contract allows it, create at most one checkpoint commit only after the handoff
   validator passes. If the commit changes the recorded commit hash, update the handoff evidence
   in the same authorized closeout operation and rerun the validator as needed; do not claim a
   finalized handoff from a dirty or unvalidated state.
8. Stop when the run mode is exhausted, a report-defined convergence condition is met, a blocked
   failure ends the run, or the user stops it.

## Portability

Keep experiment intent in this playbook and the iteration records. Keep scheduler commands,
accounts, environment setup, storage roots, and launch conventions in the selected shared
profile under `development/hpc/`. Add a profile for each HPC system rather than copying this
workflow or creating a site-specific skill.
