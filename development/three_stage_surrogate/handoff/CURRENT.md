# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/active locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 5 GPP development; `aligned_with_scoped_deviation`
- Approved deviation: fixed published all-819 predicted-C/N inputs for both GPP fit and validation;
  validation is GPP-stage conditional, not end-to-end held-out evidence.

## Live State

- Latest iteration: `iter006`
- Active iteration: none
- Work type: `implementation`
- Status: `completed`
- Phase: `closed`
- Package state: `completed_failed_gate`
- Active job scope: none; all expected jobs and failures have authoritative terminal accounting
- Active monitoring: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-01T04:58:32-07:00`

## Closed Kickoff Package and Spent Runtime Authority

- Goal/stop: six normal submissions on the pass branch—combined preparation, smoke, unthrottled
  20-leaf robustness, combined aggregation/validation, conditional all-819 release, and conditional
  release validation—through terminal accounting, gate decision, correct publication branch,
  concise closeout records, validation, and one no-push commit.
- User approval: `Full revised package approved` at `2026-11-01T00:28:58-07:00`.
- System/profile: UA Puma `junonia.hpc.arizona.edu`; `development/hpc/puma.md`;
  `chopinsong/standard`; `OLMT_puma`; no GPU.
- Root/layout: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release`;
  `runs/{prepare,smoke,robustness,aggregate,release,release_validation}` plus staging; temporary
  unbacked `/xdisk`; no cleanup.
- Locked contract: exact snapshot/global/split/upstream identities; exact Iter004 20-split design;
  frozen Iter005 43-feature physical-GPP model; split-fit scalers; compact uncertainty and
  comprehensive tables; immutable numeric/technical gate; zero fixed-test and spinup execution.
- Spent authority: bounded implementation/tests/material, independent read-only review, six normal
  submissions, monitoring/accounting/evaluation, up to five additional contract-authorized
  submissions, bounded cancellation, conditional publication, concise records, and one no-push
  commit.
- Resources: preparation 25 GB/5 derived CPUs/4 h; smoke 4 CPUs/20 GB/2 h; unthrottled array
  `1-20`, 50 GB/10 derived CPUs/16 h per leaf; aggregate/validate 4 CPUs/20 GB/4 h; release
  50 GB/10 derived CPUs/16 h; release validation 8 CPUs/40 GB/4 h.
- Outside-sandbox: locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`,
  `job-limits`; bounded `scancel` for recorded Iter006 jobs only under approved conditions.

## Closeout Result and Best Evidence

Iter006 is closed with result `fail` and decision `optimization_required`. Prepare job `24489883`,
smoke `24489912`, all 20 leaves of robustness array `24489937`, and final aggregate/validation job
`24491301` completed `0:0`; no fixed-test or spinup execution occurred. All 20 split and reload
reports passed with complete coverage and zero convergence warnings.

The immutable gate failed R2 and RMSE for every site/resolution: ABBY hourly/daily R2 q10 is
`0.7084/0.1937` with RMSE q90 `7.0410/6.0718`; JERC is `0.7560/0.0288` with RMSE q90
`7.2607/5.9397`. All bias ceilings passed. Attempt 3 independently validated 240 metric rows, 84
uncertainty rows, the member-balanced moments, all four `gpp_uncertainty.nc` fields, provenance,
hashes, and the failed gate. Aggregate validator attempts `24491172` and `24491252` failed on
over-strict numerical-comparison implementation details; both bounded corrections received fresh
user approval and independent re-review. Two of five additional submissions were used.

The correct failed-gate branch was applied: diagnostic products remain under aggregate `attempt_3`
in the external Iter006 run root, but no all-819 artifact, predicted-GPP SR handoff, stable release,
or catalog was created. Compact evidence is in
`development/three_stage_surrogate/summaries/iter006/`.

## Current Risks or Blockers

- No active blocker or job. The frozen configuration is not robust under the approved gate and
  requires optimization before release can be reconsidered. Fixed upstream C/N limits claims to
  the GPP stage, and external `/xdisk` evidence remains temporary and unbacked.

## Next Action

Explicit terminal declaration. Discuss any future planning-only GPP configuration-optimization
iteration separately; no runtime authority carries forward.

## Artifact References

- Latest closed report: `development/three_stage_surrogate/iterations/iter006.md`
- Prior closed report: `development/three_stage_surrogate/iterations/iter005.md`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Summary destination: `development/three_stage_surrogate/summaries/iter006/`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter006/`
- Scratch output: approved Iter006 root above

## Approved Iter006 Plan

### Iter006 - ABBY/JERC fixed-upstream GPP robustness and conditional release

- Revision provenance: this user-finalized proposal supersedes the narrower planning-only Iter006
  proposal copied from the Iter005 closeout. The user approved the combined robustness,
  uncertainty, conditional all-development fit, SR handoff, and publication scope on
  `2026-11-01`; the closed Iter005 report remains unchanged as historical evidence.
- Proposed sequential ID and work type: `iter006` / `implementation`.
- Campaign alignment: progression item 5 under locked `PLAN.md` SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`, with the same scoped
  deviation: use the published all-819 predicted-C/N handoff on both sides and label evidence
  `fixed_upstream_gpp_stage`, not end-to-end held out. No campaign-plan amendment is proposed.
- Objective: characterize the frozen Iter005 43-feature, hourly-trained `(128,)` ReLU/Adam GPP
  configuration on 20 balanced 655/164 development-member splits, produce a compact GPP
  surrogate-uncertainty product, and, only if the immutable robustness gate passes, refit on all
  819 development members, publish the GPP artifact, and publish its predicted-GPP SR handoff.
- Inputs and split design: immutable snapshot `r0001`; exact 819-development/205-fixed-test
  boundary; Iter004 spinup `release_0001` artifact and predicted-C/N handoff; validated Iter005
  feature/inference interfaces and eligible cache; and the exact Iter004 seed-`20261031` balanced
  20-split manifest. Reusing its split identities aligns stage-level comparisons but does not reuse
  fitted models or create end-to-end held-out evidence. Every GPP repetition is newly fit; each
  development member appears in validation four or five times.
- Repetition contract: each split fits feature/target scalers and optimizer stopping state using
  only its 655 training members; the synchronized 164 members are inference-only at ABBY and JERC.
  All 205 fixed-test members remain forbidden from fitting, evaluation, uncertainty estimation,
  gate selection, and publication decisions.
- Proposed work units: bounded no-training preflight plus split/cache validation; separate smoke;
  unthrottled 20-repetition robustness array; deterministic uncertainty aggregation and independent
  gate validation; conditional all-819 release fit/staging plus predicted-GPP handoff; independent
  release validation and catalog-last publication; concise closeout records. The kickoff package
  must lock the finite submission/dependency shape rather than infer authority from this proposal.
- Frozen scientific terms: exact 43-feature order and history semantics; physical GPP in
  `gC/m^2/day`; fit-only standardization; no clipping or target transform; Iter005 MLP configuration
  and seed policy; published fixed-upstream C/N interpretation; batch-aware inference contract;
  and hourly/daily evaluation definitions. Daily values are complete-day means derived from the
  same hourly predictions; no daily model is trained.
- Robustness evidence: `metric_distribution.csv` retains every repetition's train/validation,
  ABBY/JERC/pooled, hourly/daily R2, RMSE, MAE, signed bias, residual standard deviation, declared
  residual quantiles, expected/valid counts, gaps, coverage, train-validation R2 gap, and
  validation/train RMSE ratio. `convergence.json` retains split, iteration, warning, finite-output,
  and batch-aware reload diagnostics. No temporal-profile, autocorrelation, target-bin,
  heteroscedasticity, skewness, kurtosis, or outlier-rate analysis is in Iter006; that work is
  reserved for a later independent analysis iteration.
- Compact uncertainty product: `gpp_uncertainty.nc` has dimensions `site`, `resolution`, and
  `repetition`; coordinates ABBY/JERC, hourly/daily, and the 20 split IDs; and only
  `GPP_error_bias`, `GPP_error_rmse`, `GPP_per_repetition_error_bias`, and
  `GPP_per_repetition_error_rmse`. Aggregate values use member-balanced occurrence weight `1/k`,
  normalized across development members. RMSE is the candidate downstream surrogate-error
  standard deviation; bias remains separate. Global attributes record schema, snapshot/split/GPP
  configuration/upstream identities, units, residual convention, pooling, daily aggregation,
  validation label, and surrogate-only scope. `repeated_split_manifest.json` and
  `uncertainty_report.json` preserve exact membership, definitions, gate results, provenance, and
  hashes. No member dimension, MAE, quantiles, residual standard deviation, coverage, R2, or fit
  diagnostics are duplicated in this NetCDF.
- Immutable publication gate: all 20 repetitions and independent aggregation validation must pass;
  no fixed-test access, leakage, nonfinite prediction, unexplained gap, identity drift, or missing
  member is allowed; per-site validation-R2 10th percentile must be at least `0.85` hourly and
  `0.75` daily; per-site validation-RMSE 90th percentile must be at most `5.0` hourly and `3.0`
  daily in `gC/m^2/day`; per-site median absolute signed bias must be at most `0.35 gC/m^2/day`;
  coverage must equal `1.0`; convergence warnings must be nonfatal, fully recorded, and not linked
  to failed performance or unstable tails; and fresh-process artifact, schema, membership,
  handoff, batch-aware inference, and hash checks must pass before publication.
- Gate branches: always create the robustness and compact uncertainty evidence in the Iter006 run
  root. If the gate fails, preserve it as diagnostic evidence, decide `optimization_required`, and
  do not fit/publish an all-819 artifact or create/authorize an SR handoff. If the gate passes, fit
  the frozen configuration once on all 819 development members; the all-development fit supports
  release inference but no held-out-performance claim.
- Conditional release contract: publish a hash-verified sklearn artifact plus manifest and a
  NetCDF4 `gpp_predicted_for_sr.nc` containing only site, exact development-member identity,
  validated site-specific no-leap time, and physical predicted GPP. The handoff contains no ELM
  GPP truth, fixed-test members, parameters, forcing, or duplicated C/N features. Validate
  serialization, flexible batch inference, identities, schemas, units, coverage, and hashes in a
  fresh process.
- Run and stable layout: proposed run root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release`.
  On the pass branch only, stage and promote the immutable package to
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/release_0001`
  with `artifact/`, `uncertainty/`, `handoff/`, and `validation/`; write
  `gpp_abby_jerc/catalog.json` last. `surrogate_input_data/r0001` remains immutable. `/xdisk` is
  temporary and unbacked, so publication provides stable identity but not archival backup.
- Publication claim: at most, the frozen artifact is robust across 20 development-member splits
  for the two-site fixed-upstream GPP stage. Do not claim general proof, end-to-end robustness,
  fixed-test performance, observational validation, or transfer to the final 819-member fit's
  exact error distribution.
- Exclusions: no spinup refit/execution; fixed-test access; feature selection; GPP configuration
  search; SR fitting; full-chain robustness; temporal or target-conditioned residual analysis;
  observations; likelihood construction; MCMC; campaign-plan edit; durable backup; or push.
- Approval boundary: the complete revised runtime package is recorded in the closed Iter006 report
  and was approved at `2026-11-01T00:28:58-07:00`. Its exact resources, unthrottled array, five
  additional-submission budget, monitoring/cancellation rules, conditional publication, and
  no-push closeout commit authority governed execution.
- Stop condition: continue through authoritative accounting, immutable gate application, correct
  publication or non-publication, four-record validation, and the verified no-push closeout commit.
