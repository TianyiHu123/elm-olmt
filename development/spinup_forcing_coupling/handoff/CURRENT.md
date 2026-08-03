# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter001`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-03T14:52:55-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved` and exhausted at closeout
- Kickoff goal and stop boundary: establish the nine-site historical forcing-surrogate offline
  baseline for `SR`; continue through terminal accounting, aggregation, immutable gate evaluation,
  durable records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response `Approve the package as written`; accepted
  `2026-07-31T20:15:05-07:00`.
- Confirmed HPC system and profile: Puma on `junonia.hpc.arizona.edu`;
  `development/hpc/puma.md`.
- Approved output root, layout, creation authority, and retention policy: exact root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to
  `spinup_forcing_coupling_iter001_pilot/`, `spinup_forcing_coupling_iter001_baseline/`, and
  `spinup_forcing_coupling_iter001_aggregate/`; retain the validated memmap/layout, pilot
  artifact/scalers, 100 production records, aggregates/plots, submitted material, logs, and
  accounting; no production models; temporary unbacked `/xdisk` storage.
- Locked dependencies, scope, exclusions, gates, and decision rule: exact approved plan
  `iterations/iter001_plan.md` SHA-256
  `74ee92bddb286d194a899785ac82de0647f74a058a74888b32f4890d88ac3433`; nine local case pickles,
  `SR`, `random_time_window`, train fraction 0.8, pilot seed 10001, production seeds 10001-10100,
  historical quick grid/three-fold CV/12 workers, complete declared input schema, direct output
  layout, complete metrics/diagnostics and eight-repeat pooled importance; no coupling, saved-model
  inference validation, feature selection, extra tuning, accuracy retraining, or gate changes;
  functional/data-integrity gates only and no numerical accuracy threshold.
- Recorded later amendments remain historical authority evidence: pilot OOM rerun at 150 GB /
  `N_JOBS=4` / four hours with memmap reuse; conditional 12-hour timeout retry unused; validator
  repair and validation-only job; replacement production array at 150 GB / `N_JOBS=4` / six hours /
  `1-100%10` with amended 206-task cap and no second OOM/application retry.
- Closeout branch: at most one bounded local closeout commit; no push; exclude raw outputs,
  memmap, models, logs, and unrelated `.README.md.swp`.

## Current Objective

Historical nine-site SR forcing-surrogate offline baseline

Nine sites; SR; random_time_window; seeds 10001-10100; pooled/per-site metrics; eight-repeat pooled permutation importance; no coupling or saved-artifact inference

## Best Evidence So Far

- Work type: `implementation`.
- Upstream dependency identities: source manifest SHA-256
  `1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6`; dependency manifest SHA-256
  `e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9`; production config SHA-256
  `ef9b837bcdeb85ea96438ac6e9321a37623aa13ac9156d9ed96d5c942c104246`; repository commit
  `2648998d4ceb08ecf72859a7d5200c0e3a5eb41d`.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter001`
- Preflight job `23467631` and composite pilot (`23473876` training + `23475958` validation) passed.
- Failed first production array `23476014` remains classified: leaves 1-15 `OUT_OF_MEMORY 0:125`,
  leaves 16-100 cancelled before execution under universal-defect authority.
- Replacement production array `23476164`: all 100 leaves `COMPLETED 0:0`; exact-100 eligibility
  passed at `2026-08-03T14:49:08-07:00`.
- Aggregation job `23489654`: `COMPLETED 0:0` in 23 seconds; `AGGREGATION_PASS` with
  `warning_fraction=0.000000`; aggregate SHA-256
  `b75510b4f1fc64109d5be942e93d4af1662bd1c7a2a07c565f065245ce69f0a3`; aggregate-validation SHA-256
  `63a0b23bf9337c762e4d6583eac4ce4ac67efc01ba904847a71666c6b6fc9611`.
- Pooled test R2 mean/median `0.945275` / `0.945557`; pooled test RMSE mean/median `0.210745` /
  `0.209810`; pooled R2 gap mean/median `0.012502` / `0.012155`; pooled RMSE ratio mean/median
  `1.254273` / `1.244005`; pooled overfitting warning fraction `0.0`.
- Acceptance result: `pass`
- Decision: Technical offline baseline validated; predictive quality characterized; coupling readiness not established

## Current Risks or Blockers

- No active Iter001 jobs remain.
- `/xdisk` retention is temporary and unbacked; raw outputs stay outside Git.
- Iter001 does not establish coupling readiness or saved-artifact inference validation.

## Next Action

1. Iter001 closeout and post-commit verification are complete.
2. Treat the workflow as idle until a new consolidated kickoff package is approved.

## Next Iteration Plan (Planning Only)

No next iteration is proposed before Iter001 evidence is evaluated.
No next iteration is proposed.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Read `iterations/iter001.md` and `summaries/iter001/` if resuming from this closed baseline.
3. Do not initialize a new iteration until a fresh consolidated kickoff package is approved.
4. Inspect Git state and external artifact retention before any new work.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter001.md`
- Approved plan: `development/spinup_forcing_coupling/iterations/iter001_plan.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter001/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter001/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
