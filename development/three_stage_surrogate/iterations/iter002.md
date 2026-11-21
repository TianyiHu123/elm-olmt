# iter002 - ABBY/JERC spinup-surrogate baseline

## Status

- Iteration ID: `iter002`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter002_abby_jerc_spinup_baseline`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-29T01:33:27-07:00`
- Closed: `2026-10-29T05:40:50-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 3, two-site spinup baseline
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: implement and validate a deterministic pooled ABBY/JERC spinup C/N baseline with
  exact development-member control, flexible member prediction, physical/log evaluation,
  versioned development artifacts, and resource evidence.
- Inputs: immutable Iter001 snapshot `r0001`, its source/split manifests, named NetCDFs, and only
  the 819 development identities. Fixed-test parameter and target values are forbidden.
- Scope: four sequential jobs—preflight, 80/20 smoke, 655/164 operational baseline, and independent
  validation. No tuning, GPP/SR, all-819 fit or prediction, release, observations, MCMC, or push.
- Features: the 18 ordered parameters; `PCT_SAND`; `ORGANIC`; and five 2018--2022 no-leap
  climatology features (`PRECTmms` mean/std, `FSDS` mean, `TBOT` std, RH monthly-climatology
  amplitude). Site labels remain metadata, not model inputs.
- Estimator: independent C/N MLPs and scalers; `(32,)`, `tanh`, `lbfgs`, alpha `40`,
  `max_iter=800`, seed `42`.
- Decision: technical/package gates only. A technical pass may recommend either later release
  planning or a separate configuration-optimization iteration.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `agreed the complete package, now let's start the three-stage-surrogate iteration 002 by following development/three_stage_surrogate/WORKFLOW.md...`; recorded `2026-10-29T01:33:27-07:00`. This approval incorporates the revised root and concise-record request. |
| Kickoff goal, finite work-unit count, and stop conditions | Complete four sequential jobs and close out after terminal accounting, immutable-gate evaluation, concise records, one scoped no-push commit, and one planning-only Iter003 proposal. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`; progression item 3; aligned; deviation none. |
| Confirmed HPC system and site profile | UA Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter002_abby_jerc_spinup_baseline`; keep submitted material, attempts, logs, failures, artifacts, and validation evidence; never overwrite inputs or prior attempts. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Snapshot `r0001`; exact ranked development partitions; 25-feature schema; fixed MLP; physical/log train and validation evidence; strictly positive finite predictions; no scientific threshold; exclusions above. |
| Lifecycle authority | Authorizes Iter002 records, implementation/tests/scripts, approved directories, two read-only review gates, four jobs, bounded corrections/retries, monitoring/accounting, evaluation, concise closeout records, and one scoped commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preflight 2 CPUs/about 10 GB/30 min; smoke 4 CPUs/about 20 GB/1 h; operational 10 CPUs/about 50 GB/2 h; validation 4 CPUs/about 20 GB/1 h. Job-scoped supported monitoring through terminal `sacct`. Initial attempts plus three bounded preflight cycles and three shared operational cycles. |
| Cancellation scope | Recorded Iter002 jobs only, for scope/resource violation, runaway behavior, threatened inputs/outputs, or user request; reconcile terminal accounting afterward. |
| Outside-sandbox authority | Locked `sbatch` and contract-authorized resubmission; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the conditions above. |
| Closeout branch | One scoped no-push Iter002 closeout commit. |

Corrections may repair implementation, interfaces, paths, manifests, serialization, or numerical
handling within the locked scientific/configuration/resource contract. A fourth cycle, resource
increase, feature/model/member/gate change, or scope expansion requires fresh approval.

## Declared Inputs and Evidence

| Input or dependency | Role | Identity | Trust and compatibility evidence |
| --- | --- | --- | --- |
| Campaign plan | Direction and invariants | SHA-256 `9bbb6865...9128` | User-approved and committed at `66975fc`. |
| Iter001 catalog/snapshot | Prepared data commit marker | `r0001`; snapshot SHA-256 `39b05495...187a` | Revalidated during Section 4A recovery. |
| Parameter NetCDF | 18 ordered parameter values | `common/parameters_v1.nc` | Snapshot-owned immutable artifact. |
| ABBY/JERC site NetCDFs | Surface, forcing, and C/N targets | 1,024 members and 61,320 hours/site | Iter001 independent validation passed. |
| Member split | Development/fixed-test boundary | 819/205 ranked global split | Exact exhaustive disjoint Iter001 manifest. |
| Repository/environment | Implementation/runtime | base commit `66975fc`; `OLMT_puma` | Puma profile and compute-node preflight required. |

## Acceptance Gates and Decision Rule

- Exact catalog, snapshot, component, and member identities; no fixed-test parameter/target reads.
- Operational split: first 655 ranked development members fit, remaining 164 validate. Smoke uses
  the first 80 operational-fit and first 20 operational-validation identities.
- Exact 2018--2022 no-leap climatology (43,800 hours/site) and ordered 25-feature schema.
- Training and validation metrics per site and pooled in physical/log space: predictive R2, RMSE,
  MAE, signed `prediction - ELM` bias, residual SD, counts, gaps, and eight-repeat validation
  permutation importance.
- Physical/log C/N scatter plots show training and validation; prediction CLIs support exact
  single/subset/20/164-member requests.
- All predictions finite and strictly positive; no clipping or dropped rows.
- Fresh-process artifact reload reproduces recorded predictions within the locked tolerance;
  package/manifests/tests/independent validation pass.
- Convergence warnings are recorded but nonfatal. Exceptions, missing artifacts, nonfinite or
  nonpositive predictions, identity leakage, or reload/package disagreement fail.
- No performance threshold. Technical pass plus `release_planning` or `optimization_recommended`
  completes Iter002; neither authorizes an all-819 fit or release.

## Provenance and Job Ledger

| Work unit | Run directory | Resources | State | Evidence |
| --- | --- | --- | --- | --- |
| preflight | `<root>/runs/preflight` | 2 CPUs / ~10 GB / 30 min | `COMPLETED` `0:0` | job `24450843`; 43 s; MaxRSS 1,319,044 KiB; `ITER002_PREFLIGHT_OK` |
| corrected preflight cycle 2 | `<root>/runs/preflight` | 2 CPUs / ~10 GB / 30 min | `COMPLETED` `0:0` | job `24453852`; 26 s; MaxRSS 1,317,716 KiB; updated tests passed |
| smoke cycle 1 | `<root>/runs/smoke_80_20` | 4 CPUs / ~20 GB / 1 h | `FAILED` `1:0` | job `24450877`; 23 s; MaxRSS 1,310,240 KiB; nonpositive C prediction |
| smoke cycle 2 | `<root>/runs/smoke_80_20` | 4 CPUs / ~20 GB / 1 h | `COMPLETED` `0:0` | job `24450974`; 29 s; MaxRSS 1,311,456 KiB; artifact `95df80b1...a7fe` |
| operational cycle 2 | `<root>/runs/operational_655_164` | 10 CPUs / ~50 GB / 2 h | `COMPLETED` `0:0` | job `24451007`; 18 s; MaxRSS 1,053,000 KiB; artifact `4c42e818...47064` |
| validation cycle 2 | `<root>/runs/validation` | 4 CPUs / ~20 GB / 1 h | `COMPLETED` `0:0` | job `24453838`; 44 s; MaxRSS 1,320,268 KiB; `ITER002_VALIDATE_OK` |

## Independent Read-Only Review

- Preflight review 1: `block`; explicit metric-gap outputs and complete submitted-command provenance
  were missing. Corrected before runtime; re-review requested against source manifest SHA-256
  `17098b2d3dce43d3824f1512c4ece7744c0f25ffe73566d2d7ffdde89a6cf4f0`.
- Preflight re-review: `pass_with_concerns`. All locked identities/equality/static/interface checks
  passed. The validator checks gap schema, coverage, and finiteness but does not independently
  recompute every subtraction; accepted because gaps are produced directly from paired metric rows
  and focused unit coverage checks validation-minus-training arithmetic.
- Operational review: `pass`; preflight terminal evidence and locked smoke/operational/validation
  identity, linkage, paths, commands, and resources passed with no new concern.
- Cycle-2 correction review: requested against execution-manifest SHA-256
  `0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756`.
- Cycle-2 correction re-review: `pass`; identities, preserved cycle-1 evidence, bounded transform,
  no-clipping behavior, unchanged scientific/runtime scope, and downstream linkage all passed.

## Execution and Diagnostics

- Section 4A recovery: clean Git state; plan identity matched; snapshot `r0001` hash matched;
  Puma/account limits adequate; no active user jobs returned; storage usage 7.6/19.5 TB.
- Preparing: shell syntax, JSON, diff, and source-manifest checks passed. Canonical and submitted
  copies agree; config SHA-256 `10cff87f0df0080131a7208aed07cbf51cbebe0fc3fa86574ced44fd5ed01f4e`.
  Review correction added 12 explicit validation-minus-training gap records and CSV coverage.
- Submissions, accounting, resources, failure classification, and the authorized cycle-2 retry are
  finalized in the ledger below.
- Preflight attempt 1 submitted as job `24450843` at `2026-10-29T01:49:34-07:00` using the locked
  command above; monitor scope `24450843`.
- Preflight terminal evidence: `COMPLETED` `0:0`; 43 s; 2 CPUs/10 GB; MaxRSS 1,319,044 KiB;
  four tests passed; exact environment, snapshot, feature schema, splits, and fixed-test rejection
  passed. Low CPU/memory efficiency is acceptable for this bounded integrity check.
- Smoke cycle 1 submitted as job `24450877` at `2026-10-29T01:56:27-07:00`; monitor scope
  `24450877`.
- Smoke cycle 1 terminal evidence: `FAILED` `1:0`; 23 s; 4 CPUs/20 GB; MaxRSS 1,310,240 KiB.
  Training completed, but strict prediction validation rejected at least one nonpositive TOTSOMC
  value before package creation. Classified as numerical/interface gate failure, not resource or
  scheduler failure; attempt evidence preserved and no downstream job submitted.
- User approved the bounded correction and cycle-2 retry at `2026-10-29T02:08:11-07:00`: fit
  standardized natural-log C/N targets and exponentiate predictions; retain the approved features,
  MLP, splits, metrics, resources, and no-clipping rule.
- Smoke cycle 2 submitted as job `24450974` at `2026-10-29T02:11:12-07:00`; monitor scope
  `24450974`.
- Smoke cycle 2 completed `0:0` in 29 s with MaxRSS 1,311,456 KiB. Both log-target MLPs converged
  without warnings; the 80/20 package has 24 metric rows, 12 gap rows, four plots, positive outputs,
  and matching file hashes. Artifact SHA-256 `95df80b18b08a62b5a290a85cdfc34863927c5cfab0e8c425d2ba4517904a7fe`.
- Operational cycle 2 submitted as job `24451007` at `2026-10-29T02:15:18-07:00`; monitor scope
  `24451007`.
- After interruption, operational job `24451007` was reconciled as `COMPLETED` `0:0`: 18 s,
  MaxRSS 1,053,000 KiB, no convergence warnings, complete 655/164 metric/gap/plot package, and
  matching hashes. Artifact SHA-256 `4c42e818e124a2f72ed54635ae02979afeb7ec10518c15be187b8775e6947064`.
- Validation cycle 2 submitted as job `24453838` at `2026-10-29T05:34:21-07:00`; monitor scope
  `24453838`.
- Validation job `24453838` completed `0:0` in 44 s with MaxRSS 1,320,268 KiB. Package/identity,
  fresh-process reload, positive-output, fixed-test exclusion, and flexible 1/7/20/164-member
  prediction gates passed; no 819-member prediction was created.
- Closeout cross-record/static package validation: `ITER002_FOUR_RECORD_VALIDATE_PASS`; active
  jobs `0`; report, summary, registry, handoff, and external attempt-2 evidence agree.
- Corrected preflight cycle 2 submitted as job `24453852` at `2026-10-29T05:39:21-07:00` to close
  the updated-test evidence gap; monitor scope `24453852`.
- Corrected preflight job `24453852` completed `0:0` in 26 s with MaxRSS 1,317,716 KiB; all four
  updated tests and `target_transform=natural_log` contract checks passed.

### Locked submitted material and commands

| Unit | Canonical/submitted script SHA-256 | Logs in run directory |
| --- | --- | --- |
| preflight | `74197c3a8257b7d80cb6e579abd7741df5bec8b86d8ae7e4fc81304dad82e647` | `preflight_%j.out`, `preflight_%j.err` |
| smoke | `8fe1c0f4ee16163e4799afccf15e0bd597c27040852222a7a16558d959c476bf` | `smoke_%j.out`, `smoke_%j.err` |
| operational | `1eccb547559678d610e39ca1b15402d2d8dbaea02d6af148614ade78a36a836e` | `operational_%j.out`, `operational_%j.err` |
| validation | `bd79ed40c919b66da8e240e39b0ac422008df80ba7150bfb7d4b7e8cc0989405` | `validation_%j.out`, `validation_%j.err` |

Submit from each exact run directory with `sbatch --parsable` and these locked exports (attempt or
cycle `1`; later authorized retries change only that integer):

```text
preflight: --export=ALL,ITER002_PREFLIGHT_ATTEMPT=1,ITER002_CONFIG_SHA256=10cff87f0df0080131a7208aed07cbf51cbebe0fc3fa86574ced44fd5ed01f4e,ITER002_EXECUTION_MANIFEST_SHA256=17098b2d3dce43d3824f1512c4ece7744c0f25ffe73566d2d7ffdde89a6cf4f0 ./submit_preflight_iter002.slurm </dev/null
smoke: --export=ALL,ITER002_OPERATIONAL_CYCLE=1,ITER002_CONFIG_SHA256=10cff87f0df0080131a7208aed07cbf51cbebe0fc3fa86574ced44fd5ed01f4e,ITER002_EXECUTION_MANIFEST_SHA256=17098b2d3dce43d3824f1512c4ece7744c0f25ffe73566d2d7ffdde89a6cf4f0 ./submit_smoke_iter002.slurm </dev/null
operational: --export=ALL,ITER002_OPERATIONAL_CYCLE=1,ITER002_CONFIG_SHA256=10cff87f0df0080131a7208aed07cbf51cbebe0fc3fa86574ced44fd5ed01f4e,ITER002_EXECUTION_MANIFEST_SHA256=17098b2d3dce43d3824f1512c4ece7744c0f25ffe73566d2d7ffdde89a6cf4f0 ./submit_operational_iter002.slurm </dev/null
validation: --export=ALL,ITER002_OPERATIONAL_CYCLE=1,ITER002_SMOKE_ATTEMPT=1,ITER002_OPERATIONAL_ATTEMPT=1,ITER002_CONFIG_SHA256=10cff87f0df0080131a7208aed07cbf51cbebe0fc3fa86574ced44fd5ed01f4e,ITER002_EXECUTION_MANIFEST_SHA256=17098b2d3dce43d3824f1512c4ece7744c0f25ffe73566d2d7ffdde89a6cf4f0 ./submit_validate_iter002.slurm </dev/null
```

Cycle-1 config/manifest copies were preserved with `_cycle_1` names. The approved correction locks
config SHA-256 `0fc9a200be8117cbaf956e6c6af6f75503e3a6f869d795f2012fc38d7391f15f`
and manifest SHA-256 `0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756`.
Cycle 2 uses the same script hashes and exact run directories with these exports:

```text
smoke: --export=ALL,ITER002_OPERATIONAL_CYCLE=2,ITER002_CONFIG_SHA256=0fc9a200be8117cbaf956e6c6af6f75503e3a6f869d795f2012fc38d7391f15f,ITER002_EXECUTION_MANIFEST_SHA256=0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756 ./submit_smoke_iter002.slurm </dev/null
operational: --export=ALL,ITER002_OPERATIONAL_CYCLE=2,ITER002_CONFIG_SHA256=0fc9a200be8117cbaf956e6c6af6f75503e3a6f869d795f2012fc38d7391f15f,ITER002_EXECUTION_MANIFEST_SHA256=0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756 ./submit_operational_iter002.slurm </dev/null
validation: --export=ALL,ITER002_OPERATIONAL_CYCLE=2,ITER002_SMOKE_ATTEMPT=2,ITER002_OPERATIONAL_ATTEMPT=2,ITER002_CONFIG_SHA256=0fc9a200be8117cbaf956e6c6af6f75503e3a6f869d795f2012fc38d7391f15f,ITER002_EXECUTION_MANIFEST_SHA256=0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756 ./submit_validate_iter002.slurm </dev/null
corrected preflight: --export=ALL,ITER002_PREFLIGHT_ATTEMPT=2,ITER002_CONFIG_SHA256=0fc9a200be8117cbaf956e6c6af6f75503e3a6f869d795f2012fc38d7391f15f,ITER002_EXECUTION_MANIFEST_SHA256=0ca11f53345ecdd22c253c438abbbf0eae4571168e70ee832b25814a5ef35756 ./submit_preflight_iter002.slurm </dev/null
```

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass` for technical/package success after the approved cycle-2
  correction. Cycle 1 remains a preserved failed attempt.
- Operational performance: pooled validation R2 is 0.6704 C and 0.6696 N in physical space and
  0.6880 C and 0.6857 N in log space. Pooled log R2 drops about 0.138/0.136 from training;
  JERC validation log R2 is 0.5914/0.5901 versus ABBY 0.8199/0.8157. Physical biases are
  -23,778 gC/m2 and -2,398 gN/m2 (prediction minus ELM).
- Decision: `optimization_recommended`. The package is technically sound, but the validation gap,
  JERC log performance, and negative physical bias justify a bounded development-only configuration
  experiment before any 819-member refit or release.
- Limitations: two sites; one baseline split; development artifacts only; no all-819 fit/release.
- Campaign-plan amendment recommendation: `none`; the existing plan already provides a separate
  configuration experiment before full-development refit when baseline evidence motivates it.
- Next action: complete concise records, validate four-record agreement, and create the authorized
  no-push closeout commit.

## Proposed Next-Iteration Plan (Planning Only)

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

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter002/`
- [x] `ITERATION_SUMMARY.md` updated concisely
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator passes
- [x] No job active or unaccounted
- [x] One scoped no-push closeout commit verified
