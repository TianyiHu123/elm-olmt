# Spinup Surrogate - Current Handoff (Iter011 closed)

## Live State

- Active/latest iteration: `iter011`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none. Preflight `23432877`, control seed gate `23432904_1`, control
  remainder `23432937_[2-100]`, candidate `23432938_[1-100]`, and aggregation `23436731`
  are terminal `COMPLETED 0:0`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-07-28 America/Phoenix`
- The approved Iter011 finite run mode is exhausted. Its submission, retry, and closeout
  authorities do not authorize Iter012 execution.

## Current Objective

Iter011 tested whether global pre-split, priority-aware correlation filtering at `0.80`, applied
only after locking the strict DROP32 universe, could produce a stable smaller schema without
unacceptable paired validation-performance or importance changes.

## Best Evidence So Far

- Execution: the bounded preflight, all 200 unique production leaves, and aggregation completed
  `0:0`; no retry was used. Exact seed, metadata, input-universe, schema, metric, and finite
  8-repeat importance validation passed.
- Control: alpha-40 DROP32 retained a stable 32-feature schema. TOTSOMC/TOTSOMN median validation
  R2 was `0.827271 / 0.827497`, minimum R2 `0.699599 / 0.699270`, R2 IQR
  `0.090059 / 0.090807`, median validation RMSE `4150.32 / 415.26`, median RMSE ratio
  `0.893196 / 0.893928`, and warning fraction `0.25 / 0.24`.
- Candidate: DROP32 then corr080 retained one stable 21-feature schema with no `FLDS_*`,
  `WIND_*`, or `PSRF_*`. Its TOTSOMC/TOTSOMN median validation R2 was
  `0.801217 / 0.801178` and warning fraction was `0.22 / 0.23`. It passed IQR, warning, schema,
  exactness, and importance gates, but failed both targets' median-R2
  (`-0.026054 / -0.026319`), minimum-R2
  (`-0.028238 / -0.027061`), and median-RMSE-ratio (`+0.028101 / +0.028060`) gates.
- Decision: reject the 21-feature candidate and retain alpha-40 DROP32 only as the prospective
  Iter011 feature-reduction control. No Iter011 candidate is promoted.
- Historical retained baseline: Iter009
  `s32_tanh_lbfgs_a50_lr1e3_full45`; it remains unchanged.

## Current Risks or Blockers

- No active runtime blocker and no unaccounted Iter011 job.
- Production memory sometimes approached the 50-GiB allocation; the observed maximum was
  `52427916K`, but every leaf completed. Keep the same cap unless a fresh contract authorizes a
  resource change.
- Codex filesystem-sandbox Slurm connection errors are not Puma controller evidence. Per
  `development/hpc/puma.md`, scheduler submission and authoritative monitoring must use the
  approved elevated HPC context when the user namespace drops connectivity or project groups.
- The planning-only Iter012 proposal below is not execution authority.

## Next Action

Review or modify the planning-only Iter012 proposal. Before any Iter012 scaffolding, preflight, or
scheduler action, approve a fresh runtime contract covering Puma, the finite 300-leaf scope,
resources, submission/monitoring authority, retry/cancellation bounds, and closeout-commit
authority.

## Next Iteration Plan (Planning Only)

- Sequential ID and retained baselines: propose `iter012`. Keep Iter009
  `s32_tanh_lbfgs_a50_lr1e3_full45` as the historical retained baseline and use the completed
  Iter011 alpha-40 DROP32 arm as the prospective paired control; do not retroactively promote it.
- Focused hypothesis: the 0.80 correlation threshold reduced DROP32 from 32 to 21 stable features
  but failed both R2 and median-RMSE-ratio gates. Milder global pre-split priority-aware
  thresholds of `0.90` and `0.95`, applied only after locking DROP32, may retain enough information
  to pass while still producing a stable schema smaller than 32.
- Tentative locked matrix: 100 paired seeds (`10001-10100`) for three arms:
  (1) strict alpha-40 DROP32 control,
  (2) `DROP32` then `corr090_prioritydrop`, and
  (3) `DROP32` then `corr095_prioritydrop`. Preserve the nine cases, `by_member` split, train
  fraction `0.8`, targets `TOTSOMC,TOTSOMN`, `(32,), tanh, lbfgs`, alpha `40`, provenance-only
  learning rate `1e-3`, 8 permutation repeats, and the exact DROP32 input universe.
- Acceptance gates: require exactly 100 validated seeds per arm; stable per-candidate schemas that
  are strict DROP32 subsets with fewer than 32 features and no `FLDS_*`, `WIND_*`, or `PSRF_*`;
  apply independently to both targets the Iter011 limits of median validation-R2 delta
  `>= -0.01`, minimum validation-R2 delta `>= -0.02`, R2-IQR delta `<= +0.02`, median
  RMSE-ratio delta `<= +0.02`, and warning fraction `<= 0.25`. Require finite 8-repeat importance
  and exact identity/schema validation. Among full-gate passers, prefer the smaller stable schema;
  otherwise retain the prospective DROP32 control. The historical Iter009 baseline remains
  unchanged without a separately defined direct-promotion comparison.
- Proposed Puma resources and retry boundary: `development/hpc/puma.md`,
  `standard/chopinsong`, one task, 10 CPUs (about 50 GB), 15 minutes per production or aggregation
  job, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread numerical libraries, and task-local cache;
  1 CPU/5 minutes for the no-training preflight. Propose one validation-only preflight correction
  and separately one failed-leaf retry only for scheduler/resource interruption within the same
  caps. Application/code/configuration failures after training begins or scientific-control
  changes must stop for fresh authorization.
- Expected artifacts: Iter012 report and locked manifest; canonical and variant-local submitted
  scripts/configurations and hashes; reviewer and preflight evidence; exactly 300 seed JSONs;
  three summary, three feature-stability, and three 100-seed importance JSONs; paired gate/decision
  JSON comparing both candidates to control; universal R2/RMSE and importance plots; terminal
  accounting; updated four durable records; handoff-validator evidence; and, only if authorized,
  one closeout commit.
- Required user decision and boundary: this is planning-only. Before any Iter012 scaffolding or
  scheduler action, obtain one fresh runtime contract confirming Puma, the finite 300-leaf scope,
  exact resources, submission/monitoring authority, retry/cancellation bounds, and whether one
  closeout commit is authorized.

## Durable Prevention Rules

- Launch Python utilities only in a compute allocation or Slurm job, with the fixed repository
  root explicitly on `sys.path` before repository imports. Use the bounded no-training preflight.
- Materialize each submitted Slurm copy in its specified run directory, submit from inside that
  directory, record `sbatch --parsable` mappings, and verify identity with job-scoped
  `squeue`/`scontrol`.
- Treat scheduler-query failure as unknown. Retry boundedly in the approved elevated HPC context,
  then reconcile with logs, exact artifacts, and terminal accounting.
- Do not interpret an in-sandbox `scontrol ping`, `sbatch`, `squeue`, or `sacct` connection error
  as authoritative Puma state when the Codex namespace lacks project groups or scheduler
  connectivity.
- Wait for every terminal state before retry classification; retry only failed leaves whose
  scheduler/resource class is permitted by the active contract.

## Next Session Start Protocol

1. Read `development/spinup_surrogate/handoff/CURRENT.md`.
2. Read `development/spinup_surrogate/iterations/iter011.md`,
   `development/spinup_surrogate/iterations/iter010.md`, and
   `development/spinup_surrogate/iterations/iter009.md`.
3. Read `development/spinup_surrogate/WORKFLOW.md` and `development/hpc/puma.md`.
4. Verify the Iter011 report, cumulative summary, registry row, and current handoff agree that
   Iter011 is completed, the corr080 candidate is rejected, and Iter009 alpha-50/full45 remains
   the historical retained baseline.
5. Treat the Iter012 section as planning-only. Assess or revise it before any scaffold.
6. Obtain and record a fresh complete Iter012 runtime contract before changing execution-affecting
   files or scheduler state.

## Required User Decisions Before Execution

- Confirm or modify the Iter012 hypothesis, three-arm matrix, and gates.
- If execution is desired, approve one fresh runtime contract with Puma confirmation, finite
  scope, resources, submission/monitoring authority, retry/cancellation boundaries, and
  closeout-commit authority.

## Artifact Paths

- Current report: `development/spinup_surrogate/iterations/iter011.md`
- Cumulative summary: `development/spinup_surrogate/ITERATION_SUMMARY.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter011 canonical scripts and manifest: `development/spinup_surrogate/slurm/iter011/`
- Iter011 summaries, decision JSON, and plots:
  `development/spinup_surrogate/summaries/iter011/`
- Control scratch root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf/`
- Candidate scratch root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop/`
- Aggregation submitted copy:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_aggregate/aggregate_iter011.slurm`
- Aggregation logs:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter011_aggregate_23436731.out/.err`
- Puma site profile: `development/hpc/puma.md`
- Historical handoff material: `development/spinup_surrogate/handoff/CURRENT_HISTORY.md`

## Files Modified in Repo (latest completed iteration)

- `development/spinup_surrogate/iterations/iter011.md`
- `development/spinup_surrogate/slurm/iter011/`
- `development/spinup_surrogate/summaries/iter011/`
- `development/spinup_surrogate/tools/aggregate_permutation_importance.py`
- `development/spinup_surrogate/tools/plot_spinup_distributions.py`
- `development/spinup_surrogate/tools/plot_spinup_importance.py`
- `development/spinup_surrogate/ITERATION_SUMMARY.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter011.md` for the completed runtime contract,
provenance, terminal accounting, exact validation, gate decision, and planning-only Iter012
proposal.
