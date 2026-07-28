# Spinup Surrogate - Current Handoff (iter010 closed; Iter011 proposal prepared)

## Live State

- Active iteration: none
- Status: `iter010 completed`
- Phase: `closed; Iter011 proposal prepared; new runtime contract required before initialization`
- Iter011 execution authority: none; do not create `iterations/iter011.md` until Iter011 is
  initialized under its fresh runtime contract.
- Active job IDs: none. Corrected Iter010 production arrays completed 1,500/1,500 leaves `0:0`; aggregation `23399438` completed `0:0`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-07-27 America/Phoenix`
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

The Iter011 proposal is ready for future initialization: rerun Iter010 alpha-40 drop32 as the
explicit control, then test whether a global pre-split, priority-aware `0.80` correlation filter
applied only after locking `DROP32` yields a stable smaller schema without unacceptable paired
performance or importance changes. No Iter011 iteration record or execution is authorized yet.

## Best Evidence So Far

- Historical retained baseline: `s32_tanh_lbfgs_a50_lr1e3_full45` from Iter009; it remains the
  completed Iter010 decision.
- Iter010 evidence: 15 variants, 100 seeds each, 1,500/1,500 corrected leaves `0:0`, aggregate
  `23399438` completed `0:0`, and 45 aggregate JSON artifacts passed exact validation.
- Iter011 control evidence: Iter010 alpha-40 drop32 had warning fractions `0.25 / 0.24` and will
  be rerun as `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf`. Its new role is prospective:
  control for Iter011 eligibility deltas and ranking, not retroactive promotion.

## Current Risks or Blockers

- No active runtime blocker or job set.
- Iter011 execution is blocked pending a fresh runtime contract. The plan now defines a
  prospective inclusive warning rule (`<= 0.25` per target), but this cannot alter Iter010's
  closed zero-warning decision.
- The sequential `DROP32` then correlation-filter implementation must be statically reviewed and
  validated to exclude all removed feature families before any compute-node preflight.

## Next Action

Request a fresh Iter011 runtime contract. Create `iterations/iter011.md` only during the
subsequent Iter011 initialization, then proceed with authorized scaffolding, preflight,
submission, monitoring, or scheduler operations as applicable.

## Next Iteration Plan (Planning Only)

- Sequential ID and control: `iter011` reruns alpha-40 drop32 as the explicit control for
  eligibility deltas and ranking.
- Matrix: 100 seeds (`10001-10100`) each for strict drop32 and `DROP32` followed by global
  pre-split, priority-aware correlation filtering at `0.80`; the candidate filter universe is
  only `DROP32` and cannot reintroduce `FLDS_*`, `WIND_*`, or `PSRF_*`.
- Acceptance gates: retain independent per-target R2, minimum-R2, IQR, and RMSE-ratio deltas
  against the Iter011 control; set the prospective warning gate to inclusive `<= 0.25` per
  target. Require exact result identity, per-seed selected schemas/counts, paired deltas, and
  8-repeat importance evidence.
- Expected artifacts: planning report, locked manifest, variant-local submitted scripts/configs,
  bounded preflight evidence, universal R2/RMSE and importance plots, paired analyses, summaries,
  stability/importance results, and closeout records.
- Required boundary: a new runtime contract must state Puma confirmation, finite scope/resources,
  retry/cancellation limits, monitoring authority, and closeout-commit authority.

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
6. Validate the Iter011 proposal in this handoff and `iterations/iter010.md` against the Iter010
   evidence.
7. Request and record a fresh Iter011 runtime contract before initializing Iter011 or doing any
   execution scaffolding.

## Ready/Blocked Status for Next Iteration

Iter010 is complete: corrected production arrays completed 1,500/1,500 leaves `0:0`, aggregate
`23399438` completed `0:0`, and all 15 variants passed exact result identity validation. Every
variant failed the locked zero-warning gate with warnings in the `0.22-0.25` range. Its Iter011
proposal reruns alpha-40 drop32 as control and compares one sequential drop32-then-correlation
candidate under a prospective inclusive `<= 0.25` warning rule. Iter011 itself is not initialized;
a fresh runtime contract remains required.

## Required User Decisions Before Execution (if any)

Before Iter011 execution, the user must approve Puma confirmation, the finite two-variant/
200-leaf scope, the proposed resources, preflight/submission/monitoring authority, retry and
emergency-cancellation boundary, and closeout-commit decision. The scientific plan already locks
the prospective inclusive warning rule, 100 seeds, control, and candidate semantics.

## Artifact Paths

- Current report: `development/spinup_surrogate/iterations/iter010.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter010 scripts and manifest: `development/spinup_surrogate/slurm/iter010/`
- Iter010 summaries, stability, and importance: `development/spinup_surrogate/summaries/iter010/`
- Iter011 proposal: `development/spinup_surrogate/iterations/iter010.md` section
  `Proposed Next-Iteration Plan (Planning Only)` and this handoff's `Next Iteration Plan`.
- Scratch output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/`
- Aggregate logs: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_aggregate_23399438.out/.err`
- Puma site profile: `development/hpc/puma.md`
- Historical handoff material: `development/spinup_surrogate/handoff/CURRENT_HISTORY.md`
## Files Modified in Repo

- `development/spinup_surrogate/slurm/iter010/`
- `development/spinup_surrogate/iterations/iter010.md`
- `development/spinup_surrogate/summaries/iter010/`
- `development/spinup_surrogate/ITERATION_SUMMARY.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

Current Iter011 proposal/tooling updates are:

- `development/spinup_surrogate/iterations/iter010.md`
- `development/spinup_surrogate/tools/plot_iter010_a40_distributions.py`
- `development/spinup_surrogate/tools/plot_iter010_a40_importance.py`

Previously identified post-closeout policy-document changes, if still present, are:

- `development/spinup_surrogate/WORKFLOW.md`
- `development/hpc/puma.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter010.md` for completed evidence, the incident
ledger, and the Iter011 planning-only controls, gates, matrix, and authorization boundary.
