# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/latest locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 3 baseline closed; item 4 configuration experiment proposed;
  `aligned`; deviation `none`

## Live State

- Latest iteration: `iter002`
- Active iteration: none
- Work type: `implementation`
- Status: `completed`
- Phase: `closed`
- Package state: `closed`
- Active job scope: none
- Active monitoring: none; every recorded job has authoritative terminal accounting
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-29T05:40:50-07:00`

## Closed Runtime Contract

- Goal satisfied: pooled ABBY/JERC spinup baseline implemented, corrected, trained, independently
  validated, evaluated, and closed with concise records and one no-push commit branch.
- Input/scope: snapshot `r0001`; 819 development/205 fixed-test boundary; smoke 80/20 and
  operational 655/164; fixed-test access remained false.
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter002_abby_jerc_spinup_baseline`.
- Final interface: fixed 25 features, natural-log C/N target fitting, positive exponentiated
  predictions, separate `(32,)` MLPs/scalers, and no clipping.
- Authority exhausted: no active scheduler, retry, directory, correction, or commit authority
  remains after the closeout commit; no push was authorized.

## Best Evidence and Decision

- Result/decision: `pass` / `optimization_recommended`.
- Operational artifact SHA-256:
  `4c42e818e124a2f72ed54635ae02979afeb7ec10518c15be187b8775e6947064`.
- Pooled validation R2 C/N: physical `0.6704/0.6696`; log `0.6880/0.6857`. JERC validation log R2:
  `0.5914/0.5901`; pooled physical bias is negative for both targets.
- Validation: `ITER002_VALIDATE_OK`; flexible 1/7/20/164 prediction, package hashes, positive
  outputs, exact identities, fresh reload, and fixed-test exclusion passed; no 819 prediction exists.
- Accounting: jobs `24450843`, `24450974`, `24451007`, `24453838`, and corrected preflight
  `24453852` completed `0:0`; failed initial smoke `24450877` is preserved and accounted.
- Summary: `development/three_stage_surrogate/summaries/iter002/`.
- Limitations: two sites, one development split, non-release artifact, temporary unbacked `/xdisk`.
- Campaign-plan amendment recommendation: `none`.

## Next Action

Review the planning-only Iter003 proposal below. Fresh consolidated kickoff approval is required;
do not initialize, create directories, edit Iter003 scaffold, or submit work from this handoff.

## Next Iteration Plan (Planning Only)

### Iter003 - ABBY/JERC spinup configuration experiment

- Sequential ID/work type: `iter003` / `experiment`.
- Campaign alignment: `development/three_stage_surrogate/PLAN.md`, SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`; progression item 4;
  `aligned`; proposed deviation `none`.
- Objective/hypothesis: use held-out development evidence to select and freeze a better spinup MLP
  configuration. Modest capacity/regularization changes may improve the Iter002 pooled/JERC log
  validation performance without an unacceptable per-site regression.
- Inputs/dependencies: immutable snapshot `r0001`; exact 819/205 split; validated Iter002 loader,
  25-feature schema, natural-log target interface, metrics, predictor, and package contracts. Trust
  only the recorded hashes and revalidate compatibility before execution.
- Bounded scope: preflight; nested small smoke; one matched 655-train/164-validation screen of six
  deterministic candidates: baseline `(32,), alpha=40`; `(64,), 40`; `(32,16), 40`; `(64,32), 40`;
  `(32,), 10`; and `(32,), 100`. Retain `tanh`, L-BFGS, `max_iter=800`, seed 42, separate C/N
  models/scalers, log-target fitting, the fixed features, and the exact member split. Finish with
  independent package/selection validation and a frozen configuration recommendation.
- Exclusions: no fixed-test reads; no all-819 fit/prediction or release artifact; no feature/site-ID
  changes; no GPP/SR, observations, robustness repetitions, MCMC, campaign-plan edit, or push.
- Tentative gates/decision: all Iter002 identity, positivity, no-clipping, artifact, reload, physical/
  log train-validation, per-site/pooled, gap, plot, and provenance gates remain. Rank eligible
  candidates by mean pooled validation log R2 across C/N; within 0.005 use lower mean pooled log
  RMSE. A candidate is ineligible if either site's C or N validation log R2 is more than 0.02 below
  the Iter002 baseline. Freeze the winner only after independent validation; otherwise retain the
  Iter002 baseline. This is development selection, not release evidence.
- Proposed runtime contract: Puma `chopinsong/standard`; output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter003_abby_jerc_spinup_config`;
  preflight 2 CPUs/about 10 GB/30 min, smoke 4 CPUs/about 20 GB/1 h, candidate screen 10 CPUs/about
  50 GB/2 h, validation 4 CPUs/about 20 GB/1 h. Require read-only reviews before preflight and
  candidate execution, job-scoped monitoring through terminal accounting, initial plus three
  bounded correction/retry cycles, and cancellation only for recorded Iter003 jobs under the
  workflow conditions.
- Expected evidence/stop: locked candidate manifest and member identities; candidate artifacts;
  complete physical/log training/validation metrics and plots; ranking/eligibility table; resource
  accounting; independent validation; concise records; one authorized closeout branch; and one
  planning-only follow-up for all-819 release/handoff if a configuration is frozen. Stop before
  any full-development refit. Fresh consolidated kickoff approval is required for all authority.
