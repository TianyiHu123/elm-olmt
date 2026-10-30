# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/latest locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 4 spinup configuration frozen; `aligned`; deviation `none`

## Live State

- Latest iteration: `iter003`
- Active iteration: none
- Work type: `experiment`
- Status: `completed`
- Phase: `closed`
- Package state: `closed`
- Next proposal state: `planning_only`
- Active job scope: none
- Active monitoring: none; all Iter003 jobs terminally accounted
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-30T15:15:56-07:00`

## Best Evidence and Decision

- Result/decision: `pass` / freeze candidate 74 for an all-819 development refit and artifact
  handoff.
- Frozen configuration: `(64,32)`, `tanh`, alpha `10`, L-BFGS, `max_iter=800`, seed `42`.
- Winner median mean pooled validation log R2: `0.8910`; Iter002 baseline: `0.8015`; paired mean
  delta: `+0.07655`; every ABBY/JERC C/N site-median delta is positive.
- Stability: 27/40 winner fits emitted nonfatal convergence warnings; preserve this as release
  validation evidence.
- Independent validation: `ITER003_VALIDATE_OK selected=74`; 96 candidates; fixed-test access
  false; model artifacts created false.
- Accounting: preflight `24472427`, smoke `24472428`, all 96 leaves of `24472431_[0-95]`,
  aggregation `24475235`, and validation `24475275` completed `0:0`; no retry.
- Summary: `development/three_stage_surrogate/summaries/iter003/`.
- External root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter003_abby_jerc_spinup_config`.
- Limitations: two sites; overlapping development splits; finite MLP grid; convergence warnings;
  temporary unbacked `/xdisk`; no release or fixed-test evidence.
- Campaign-plan amendment recommendation: `none`.

## Current Objective and Next Action

Iter003 is closed. Review and, if acceptable, grant fresh consolidated kickoff authority for the
planning-only Iter004 proposal below. No initialization, runtime, scheduler, directory, retry,
record, or commit authority is currently active.

## Next Iteration Plan (Planning Only)

### Iter004 - ABBY/JERC frozen spinup artifact and GPP handoff

- Sequential ID/work type: `iter004` / `implementation`.
- Campaign alignment: `development/three_stage_surrogate/PLAN.md`, SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`; progression item 4;
  `aligned`; proposed deviation `none`.
- Objective: refit the frozen candidate-74 spinup configuration on all 819 development members,
  publish and independently validate its versioned ABBY/JERC inference artifact, and freeze the
  predicted-C/N handoff contract needed by the later GPP stage.
- Inputs/dependencies: immutable snapshot `r0001`; exact global 819-development/205-fixed-test
  manifest; Iter003 winner `(64,32)`, `tanh`, alpha `10`, L-BFGS, `max_iter=800`, seed `42`;
  validated 25-feature order, natural-log C/N targets, separate fit-only scalers/models, positive
  exponentiated predictions, and no-clipping interface. Trust only recorded hashes and revalidate
  compatibility before execution.
- Bounded scope: locked preparation and read-only review; no-training preflight; bounded smoke of
  artifact serialization/reload; one all-819 development fit; flexible-size inference validation;
  exact feature/target/member provenance; artifact/package manifests and hashes; concise records;
  and one user-selected closeout branch. Record convergence behavior but do not alter the frozen
  configuration from runtime evidence.
- Exclusions: no fixed-test parameter or target access; no configuration, feature, solver, target,
  or split selection; no held-out performance claim from the all-development fit; no GPP/SR model
  fitting, observations, MCMC, campaign-plan edit, or push.
- Tentative gates/decision: exact snapshot/member/config/feature/target identities; all and only 819
  development members in fit scope; zero fixed-test access; finite positive outputs without
  clipping; deterministic flexible-size inference; serialization and fresh-process reload
  equivalence; complete self-describing package and hashes; no unaccounted jobs; and independent
  validation. Publish the artifact and authorize it as the GPP-stage upstream dependency only if
  every gate passes; otherwise publish nothing and retain candidate 74 as frozen but unreleased.
- Proposed runtime contract: Puma `chopinsong/standard`; proposed output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter004_abby_jerc_spinup_release`;
  initial one CPU/Puma-derived 5 GB with single-thread BLAS/OpenMP, 30 minutes for preflight/smoke/
  validation and two hours for the all-819 fit, subject to bounded smoke evidence before the fit.
  Require independent read-only reviews before preflight and fit, job-scoped monitoring through
  terminal accounting, explicit retry/cancellation bounds, and separate authority for one no-push
  closeout commit.
- Expected evidence/stop: versioned all-development artifact and manifest; exact 819-member fit
  provenance; flexible prediction/reload validation; resource and terminal accounting; frozen C/N
  handoff schema for a planning-only GPP iteration; concise records; and no fixed-test access.
  Stop before any GPP training or fixed-test evaluation. Fresh consolidated kickoff approval is
  required for every initialization, directory, execution, scheduler, retry, cancellation, record,
  and closeout authority.
