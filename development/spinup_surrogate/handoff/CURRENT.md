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

- Sequential ID and terminal-development objective: propose `iter012` as the final
  spinup-surrogate development iteration. Package two user-accepted versions from Iter011:
  `drop32`, the recommended accuracy-oriented 32-feature model, and `drop21_corr080`, the compact
  21-feature alternative. Preserve the Iter011 comparative-gate result as provenance, including
  that the compact version missed the locked median-R2, minimum-R2, and median-RMSE-ratio gates;
  the user nevertheless accepts both final versions for different tradeoffs. No new comparative
  promotion decision is in scope.
- Locked data and model: use the same ordered nine cases and matching `--spinup-case` list as
  Iter011, 100 members per case (900 rows), targets `TOTSOMC,TOTSOMN`, compact climatology,
  forcing variables `PRECTmms,FSDS,TBOT,RH`, and ABBY
  `ABBY_ppe6_I20TRCNPRDCTCBC` as the parameter-metadata and example reference case. Train one
  independent `MLPRegressor` per target with `(32,)`, `tanh`, `lbfgs`, alpha `40`,
  `max_iter=800`, estimator seed `42`, and provenance-only learning rate `1e-3`; retain separate
  X and Y `StandardScaler` objects per target.
- Freeze schemas by exact names and disable variance and correlation filtering. The actual
  canonical fitted order for `drop32` is:
  `parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp`.
  The actual canonical fitted order for `drop21_corr080` is:
  `parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,FSDS_clim_mean,TBOT_clim_std,RH_clim_seasonal_amp`.
- Two-stage fitting: first reproduce each Iter011 seed-`10001` `by_member` 80/20 validation run
  with exact cases, split membership, feature order, architecture, and configuration. Require
  the recorded metrics to agree with the Iter011 reference using `rtol=1e-10` and `atol=1e-8`;
  separately require pre-save and post-load predictions to agree with each other at that
  tolerance. Only after the reproduction gate passes, refit the same frozen model on all 900
  rows with estimator seed `42`. Use Iter011's 100-seed summaries as the scientific performance
  and importance evidence; do not mislabel full-data training diagnostics or training-set
  permutation importance as validation evidence.
- Version and enrich the existing dictionary artifact while keeping older unversioned artifacts
  loadable. Each final artifact must include release/schema versions, ordered physical parameter
  names read from ABBY `ensemble_parms`, `parm_N` aliases and mapping, `ensemble_pmin/pmax`,
  complete and selected feature orders, empirical feature ranges, ordered targets, output
  definitions and audited units, models/scalers, architecture, cases, fit scope, validation
  evidence, package versions, source/configuration hashes, and creation time. Pickles are
  trusted-source-only and environment-version-sensitive.
- Keep pickle binaries outside Git. Write:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl`
  and
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl`.
  Put `artifact_manifest.json` and `validation_report.json` beside each pickle and keep
  byte-identical tracked evidence copies. Record paths, sizes, and SHA-256 hashes. Backup
  confirmation is not a closeout gate; record that `/xdisk` is temporary and unbacked and that
  the user owns backup.
- Inference contract: the user supplies a case name, optional distinct spinup-case name, artifact
  path or directory, exact ordered feature subset, and either case-member parameters or new
  parameters. Reuse the training code for case pickle loading and construction of parameters,
  member or explicit mean surface data, the spinup-cycle forcing subset, and compact climatology;
  do not load restart-derived `TOTSOMC/TOTSOMN` for inference. Support (1) one or more existing
  case members and (2) new parameters supplied either positionally in physical `ensemble_parms`
  order or as an exact physical-name mapping, matching the convention needed by
  `optimize_surrogate_forcing.py`.
- Enforce input contracts before prediction. Reject missing, duplicate, extra, or misordered
  parameters/features and values outside `ensemble_pmin/pmax`; warn without blocking for values
  within declared bounds but outside empirical training ranges. Do not silently reorder a
  supplied feature subset. A feature-order error must show the supplied and required orders,
  first mismatch, missing/unexpected names, and the complete correct `--feature-subset` value.
- Operational release gates for both artifacts: fresh-process load; supported schema; exact
  target/model/scaler keys; exact feature and physical-parameter order; correct single-row and
  batch shapes; finite predictions; identical named and positional new-parameter results;
  manifest size/hash equality; and strict pre-save/post-load agreement. Test one real member from
  every training case, several ABBY members as a batch, the ABBY parameter-bounds midpoint in
  positional and named forms, an empirical-range warning when possible, and negative cases for
  ordering, missing/extra inputs, bounds, and schema. Audit authoritative restart-variable
  definitions and NetCDF metadata for the exact scalar aggregation and units of `TOTSOMC` and
  `TOTSOMN`; ambiguity stops release.
- Forcing-surrogate bridge: document and validate
  `parameters + surface + compact spinup-cycle climatology -> spinup surrogate -> ordered
  [TOTSOMC,TOTSOMN] -> existing [engineered forcing | parameters | spinup] forcing-surrogate
  interface`. Verify order, shape, dtype, and design-matrix compatibility. No forcing artifact
  currently exists in the inspected output tree, so Iter012 must not train one or claim a real
  SR/flux prediction; provide a complete future example for use with a real forcing artifact.
  The deprecated `model_ELM/surrogate_NN.py` interface is out of scope, as is actual integration
  into the forcing surrogate.
- Documentation: fully populate `iterations/iter012.md`; add a separate detailed "Final Spinup
  Surrogate Models" section to `ITERATION_SUMMARY.md`; and audit/update the root `README.md` for
  stale spinup-surrogate material. Document both versions, physical and engineered inputs,
  ordered outputs and units, architecture, Iter011 100-seed evidence, full-data-fit distinction,
  validated nine-site domain, new-site and out-of-range limitations, artifact trust/version
  requirements, both inference modes, failure messages, copyable examples, and the future
  spinup-to-forcing bridge.
- Proposed finite Puma topology after independent read-only review: one 1-CPU/5-minute
  no-training preflight; one `drop32` release job and one `drop21_corr080` release job, each
  10 CPUs (about 50 GB)/15 minutes; then one cross-artifact validation job at the same
  10-CPU/15-minute cap. Use `development/hpc/puma.md`, `standard/chopinsong`, `N_JOBS=4`,
  `PRE_DISPATCH=n_jobs`, single-thread numerical libraries, task-local cache, elevated
  authoritative Slurm access, and roughly 5-10 minute monitoring intervals.
- Proposed retry/stop boundaries: allow one no-training validation correction and one retry per
  failed job only for scheduler/resource interruption within the same caps. Do not automatically
  retry application/code/schema/numerical/artifact/scientific failures. Emergency cancellation is
  limited to a proven universal pretraining defect. Architecture, schema, data-scope, resource,
  or scientific changes require fresh authorization.
- Closeout expectations: tracked code, tests, Slurm material, manifests/evidence, detailed
  records, four-record handoff validation, no active jobs, and one separately authorized Iter012
  closeout commit; never track the pickle binaries. Record PR readiness but do not fetch, rebase,
  merge, or operate the `pmcpu` branch or GitHub PR.
- Required new-session boundary: this plan does not authorize Iter012 scaffolding or execution.
  The new session must create the exact native Iter012 lifecycle goal and obtain one fresh
  consolidated runtime contract confirming Puma, the four-job finite scope, preparation,
  submission and monitoring authority, the stated resources and retry/cancellation boundaries,
  and one closeout commit before changing execution-affecting files or scheduler state.

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
