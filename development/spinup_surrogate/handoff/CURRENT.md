# Spinup Surrogate - Current Handoff (iter010 closed)

## Live State

- Active iteration: none
- Status: `iter010 completed`
- Phase: `closed; new runtime contract required for any Iter011 work`
- Active job IDs: none. Corrected Iter010 production arrays completed 1,500/1,500 leaves `0:0`; aggregation `23399438` completed `0:0`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-07-25 America/Phoenix`
- Execution authority: on 2026-07-24 America/Phoenix the user replied `approved` to the complete
  Iter010 request: confirmed UA Puma login host `junonia.hpc.arizona.edu` with
  `development/hpc/puma.md`; one finite 15-variant / 1,500-leaf matrix; artifact preparation,
  static validation, independent read-only review, bounded no-training preflight, submission, and
  continuous monitoring through aggregation/selection/closeout. Resources are `standard` /
  `chopinsong`, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, and
  per-task cache isolation. One minimal validation-only correction/rerun is separate from one
  retry per leaf only for scheduler/resource interruption within the caps. Other
  application/code/configuration failures stop for fresh authorization. At most one closeout
  commit is authorized.

## Current Objective

Iter010 completed its 15-variant, 100-seed (1,500-leaf) alpha-40--50 and feature-policy matrix.
The exact aggregate validator accepted all 1,500 results and produced 15 summary, 15 stability,
and 15 importance artifacts. All variants are scientifically rejected by the locked zero-warning
gate (warnings `0.22-0.25` for both targets); no model is promoted. Retain the Iter009 baseline
`s32_tanh_lbfgs_a50_lr1e3_full45`. The detailed terminal accounting and failure-prevention rules
are in `iterations/iter010.md`.

## Best Evidence So Far

- Baseline retained: `s32_tanh_lbfgs_a50_lr1e3_full45` from Iter009.
- Iter010 evidence: 15 variants, 100 seeds each, 1,500/1,500 corrected leaves `0:0`, aggregate
  `23399438` completed `0:0`, and 45 aggregate JSON artifacts passed exact validation.
- Decision: all variants failed the locked zero-warning gate with warning fractions `0.22-0.25`;
  no Iter010 candidate is promoted.

## Current Risks or Blockers

- No active runtime blocker or job set.
- Iter011 is blocked from execution pending a new runtime contract and a decision on whether the
  zero-warning definition remains scientifically appropriate after the 100-seed evidence.
- Do not relax the Iter010 gate retroactively or infer an Iter011 matrix automatically.

## Next Action

Prepare and review a planning-only Iter011 proposal; request fresh runtime authority before any
scaffolding, code/configuration change, preflight, submission, or scheduler operation.

## Next Iteration Plan (Planning Only)

- Sequential ID and baseline: `iter011`; retain `s32_tanh_lbfgs_a50_lr1e3_full45` unless a new
  contract explicitly changes the decision rule.
- Hypothesis: determine whether the warning metric/threshold is scientifically appropriate at
  100-seed scale before proposing another alpha or feature-policy sweep.
- Tentative controls/matrix: no execution matrix is locked yet; any candidate matrix must be
  evidence-derived and explicitly authorized after the warning-definition decision.
- Acceptance/retry gates: retain the current independent R2, minimum-R2, IQR, RMSE-ratio, and
  zero-warning gates unless the user explicitly approves a revised scientific rule; retain one
  validation-only retry and one scheduler/resource retry within the new contract.
- Expected artifacts: planning report, locked manifest, variant-local submitted scripts/configs,
  bounded preflight evidence, summaries, stability/importance results, and closeout records.
- Required boundary: planning only. A new runtime contract must state Puma, finite scope,
  resources, retry/cancellation authority, monitoring authority, and closeout-commit authority.

## Durable Prevention Rule

For any Python utility launched by absolute path on Puma, prepend the fixed repository root
`/xdisk/chopinsong/tianyihu/elm-olmt` to `sys.path` before importing repository modules. Require a
bounded compute-node import/no-training preflight before a production matrix. Treat an import-path
failure as application/configuration: preserve diagnostics and apply only the validation-only
retry boundary defined below.

The canonical workflow now grants one separate validation-only retry when a bounded preflight
fails before training: the primary agent may apply one minimal import/launch/configuration fix and
rerun the same preflight once. It does not consume the matrix variant retry budget; a second
preflight failure, a changed failure class, or any scientific-control change stops for fresh
authorization.

Iter010 also established these active prevention rules: materialize each submitted Slurm copy in
the specified run directory and submit from inside it; use the supported Puma Slurm command
interface first; capture and verify each returned job ID against its variant, script, run
directory, array range, and configuration; isolate manifest-loop stdin with `</dev/null`; use
emergency cancellation only for a proven universal pre-training failure; and remain active
through terminal accounting, aggregation, decision, handoff validation, and closeout.

## Historical Handoff Records

Detailed historical plans, migration notes, Iter006 evidence, Iter007 scaffold notes, and closed
resource observations were moved to `development/spinup_surrogate/handoff/CURRENT_HISTORY.md`.
Authoritative scientific evidence remains in the iteration reports and
`development/spinup_surrogate/ITERATION_SUMMARY.md`.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter010.md`
   - `development/spinup_surrogate/iterations/iter009.md`
   - `development/spinup_surrogate/iterations/iter008.md`
3. Treat historical Iter008, Iter009, and completed Iter010 plan sections as provenance only.
4. Review `development/spinup_surrogate/WORKFLOW.md` and
   `development/hpc/puma.md`.
5. Confirm there is no live job set.
6. Validate the planning-only Iter011 proposal against current evidence.
7. Request and record a fresh Iter011 runtime contract before scaffolding or execution.

## Ready/Blocked Status for Next Iteration

Iter010 is complete: corrected production arrays completed 1,500/1,500 leaves `0:0`, aggregate
`23399438` completed `0:0`, and all 15 variants passed exact result identity validation. Every
variant failed the locked zero-warning gate with warnings in the `0.22-0.25` range. No candidate
was promoted; retain the Iter009 alpha-50 full45 baseline. Iter011 is planning-only and requires a
fresh runtime contract.

## Required User Decisions Before Execution (if any)

No active execution decision remains. Before Iter011 execution, the user must approve its warning
definition/gates, locked matrix and seed count, Puma resource cap, retry and emergency-cancellation
boundary, monitoring authority, and closeout-commit decision.

## Artifact Paths

- Current report: `development/spinup_surrogate/iterations/iter010.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter010 scripts and manifest: `development/spinup_surrogate/slurm/iter010/`
- Iter010 summaries, stability, and importance: `development/spinup_surrogate/summaries/iter010/`
- Scratch output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/`
- Aggregate logs: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_aggregate_23399438.out/.err`
- Puma site profile: `development/hpc/puma.md`
- Historical handoff material: `development/spinup_surrogate/handoff/CURRENT_HISTORY.md`
## Files Modified in Repo (latest completed iteration)

- `development/spinup_surrogate/slurm/iter010/`
- `development/spinup_surrogate/iterations/iter010.md`
- `development/spinup_surrogate/summaries/iter010/`
- `development/spinup_surrogate/ITERATION_SUMMARY.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

Post-closeout policy-document changes are currently uncommitted in:

- `development/spinup_surrogate/WORKFLOW.md`
- `development/hpc/puma.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter010.md` sections:

- `Execution and Diagnostics`
- `Complete Incident Ledger`
- `Results and Decision`
- `Proposed Next-Iteration Plan (Planning Only)`
