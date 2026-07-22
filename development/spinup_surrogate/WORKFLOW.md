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
| `summaries/iterXXX/` | Compact metrics and stability evidence | Populate after successful aggregation. |
| `slurm/iterXXX/` | Canonical submission scripts for an iteration | Treat as the source of truth; materialize a variant-local, self-describing submission copy before each `sbatch`. |

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
   monitoring, and a single retry within the stated scope.
4. **Resource policy:** explicit resources, or calibrated mode with memory and walltime caps.
5. **Commit authority:** whether one closeout commit per completed iteration is authorized.

The contract is scoped to the declared run. A new iteration outside that scope, a resource
increase beyond the cap, or a code/configuration change needed to retry requires fresh user
authorization. Do not create a commit unless closeout-commit authority was explicitly given.

### Required authorization request

At the start of every new iteration, after planning has identified the matrix and before any
execution or scheduler action, the primary agent must explicitly request and record a single
runtime-contract response covering all of the following:

1. confirmation that the active session is on the selected HPC system;
2. the finite run mode and its task/round count;
3. authorization to prepare, submit, and monitor the locked matrix;
4. the exact resource profile and the one-retry boundary for scheduler/resource failures;
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
5. Determine the next iteration ID and run slug.
6. Record a focused objective, fixed controls, candidate matrix, acceptance gates, retry
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
   variant-local copy, not the repository canonical script. Record the canonical source,
   submitted copy, configuration, and log paths in the iteration ledger.

### 2. Submit and monitor

1. Submit only the locked matrix, normally one job or array per variant.
2. Record each job ID immediately in the iteration ledger and update `CURRENT.md` to
   `in_progress` with the active job set.
3. Monitor the complete job set concurrently using the selected site's documented queue and
   accounting commands.
4. Record terminal state, exit code, elapsed time, resource diagnostics, and failure reason
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
- **Application or code failure:** preserve the diagnostic bundle and obtain fresh
  authorization before changing code/configuration or retrying.

If a variant is blocked after its allowed retry, mark the iteration `blocked` or `failed` as
defined by its decision rules; cancel remaining active jobs when the report's fail-fast policy
requires it. Do not aggregate incomplete variants or select a winner. Record a debug bundle
with job IDs, states, exit codes, reasons, provenance, accounting evidence, and the next
hypothesis; then update `CURRENT.md`.

### 4. Aggregate and decide

For every eligible completed variant:

1. Aggregate `surrogate_spinup_stats_seed*.json` with `summarize_spinup_stats.py`.
2. Copy compact summaries to `summaries/iterXXX/`.
3. Run any iteration-specific analysis, such as feature-stability diagnostics.
4. Evaluate the report's explicit gates and record the comparison table and rationale.

An optional read-only reviewer may validate summaries against those gates before the primary
agent records the final decision.

### 5. Close out

1. Finalize the iteration report, including outcome, evidence, decision, next action, and
   status.
2. Add or update the corresponding `registry.csv` row.
3. Update `CURRENT.md` with the completed/blocked state, key evidence, and next-session
   protocol.
4. If the runtime contract allows it, create at most one checkpoint commit after all closeout
   artifacts are updated.
5. Stop when the run mode is exhausted, a report-defined convergence condition is met, a
   blocked failure ends the run, or the user stops it.

## Portability

Keep experiment intent in this playbook and the iteration records. Keep scheduler commands,
accounts, environment setup, storage roots, and launch conventions in the selected shared
profile under `development/hpc/`. Add a profile for each HPC system rather than copying this
workflow or creating a site-specific skill.
