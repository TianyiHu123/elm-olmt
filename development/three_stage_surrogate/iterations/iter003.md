# iter003 - ABBY/JERC spinup MLP configuration experiment

## Status

- Iteration ID: `iter003`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter003_abby_jerc_spinup_config`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-30T03:20:20-07:00`
- Closed: `2026-10-30T15:15:56-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 4, spinup configuration selection
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: select and freeze a better ABBY/JERC spinup MLP configuration using repeated
  development-only held-out evidence while preserving the validated Iter002 data, feature, target,
  inference, and fixed-test boundaries.
- Inputs: immutable snapshot `r0001`; exact 819-development/205-fixed-test split; Iter002 25-feature
  schema, natural-log C/N targets, separate models/scalers, positive exponentiated prediction, and
  no-clipping contract.
- Implementation: remove hardcoded estimator settings from the fitting path. The driver accepts,
  validates, normalizes, and records explicit MLP CLI arguments.
- Matrix: 96 unique candidates from eight layer shapes—`(16,)`, `(32,)`, `(64,)`, `(128,)`,
  `(16,8)`, `(32,16)`, `(64,32)`, `(128,64)`—two activations (`tanh`, `relu`), and six alpha
  values (`0`, `1`, `10`, `40`, `100`, `300`). Retain `lbfgs`, `max_iter=800`, model seed `42`,
  fixed features, log targets, separate C/N models, and fit-only scalers.
- Repeated splits: one immutable manifest generated with seed `20261030`; 20 deterministic balanced
  655-training/164-validation development-only splits shared by all candidates and both sites. The
  3,280 validation slots assign 815 members four times and four members five times.
- Work units: no-training preflight; one-split baseline/largest-candidate smoke; production array
  `0-95` without a concurrency cap; aggregation; independent selection validation; concise records;
  and one no-push closeout commit.
- Exclusions: fixed-test reads; all-819 fit/prediction or release artifact; feature/site-ID changes;
  alternative solver or target transform; retransformation calibration; GPP/SR; observations;
  MCMC; campaign-plan edit; push; per-candidate pickles, prediction NetCDFs, plots, permutation
  importance, or full packages.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `Approved the complete package with 2 more extra retry budget for smoke test and operational run. If the smoke test find we need larger production shape for operational run, adjust it with your judgement.` Recorded `2026-10-30T03:20:20-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Five Slurm submissions: preflight, smoke, production array, aggregation, and validation. Continue through terminal accounting, selection, concise records, and one no-push commit. Stop before fixed-test access, all-819 release fit, publication, GPP/SR, or unapproved scope change. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb6865...9128`; progression item 4; aligned; deviation none. |
| Confirmed HPC system and site profile | UA Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; account/partition `chopinsong/standard`; interpreter `/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python`. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter003_abby_jerc_spinup_config` with `runs/preflight`, `runs/smoke`, `runs/screen`, `runs/aggregate`, and `runs/validation`. Keep raw logs and detailed work-unit outputs external; keep only compact decision evidence in Git. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Snapshot/split identities, 96-candidate matrix, seed-20261030 balanced split contract, fixed estimator controls, fixed-test exclusion, compact output contract, eligibility gates, and ranking rule in this report. |
| Lifecycle authority | Authorizes Iter003 records, implementation/tests/scripts/manifests, approved directories, two read-only review gates, five submissions, monitoring/accounting, bounded retries and cancellation, evaluation, concise closeout records, and one scoped commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Initial shape: one CPU with Puma-derived 5 GB, single-thread BLAS/OpenMP; 30 minutes for preflight/smoke/aggregation/validation and two hours per production leaf. Smoke evidence authorizes the primary agent to increase the production CPU/memory/walltime shape using recorded judgment before submission. Smoke and production each have the initial attempt plus three retry opportunities; unchanged scheduler/node retries may target only recorded failed work. Application/code/interface/schema/data/numerical failures outside the smoke-authorized production resource calibration stop for fresh approval. |
| Cancellation scope | Recorded Iter003 jobs only, for scope/resource mismatch, runaway behavior, threatened inputs/outputs, or user request; reconcile terminal accounting afterward. |
| Outside-sandbox authority | Authorized locked `sbatch` submissions and contract-authorized retries; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` only for recorded Iter003 jobs under the stated conditions. |
| Closeout branch | One scoped Iter003 no-push closeout commit authorized. |

The approved goal was established in the active session at kickoff. Base commit is
`a8810d8378d17b3b3ca02904703661fdf0d5b9db`; the pre-initialization `CURRENT.md` planning diff had
SHA-256 `8658d185fa38ab592f345ee32b2411fad7903177f4200d603d809253d0450b3c`.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction and invariants | `development/three_stage_surrogate/PLAN.md` | current approved plan | `9bbb6865...9128` | Iter002 aligned; no proposed deviation. |
| Workflow | Lifecycle authority | `development/three_stage_surrogate/WORKFLOW.md` | commit `a8810d8` | `f23f040e...dc4` | Concise-record policy committed before kickoff. |
| Snapshot catalog | Published input selector | `<snapshot>/catalog.json` | catalog v1 / `r0001` | `24b5bbdd...a8a4` | Points to locked snapshot `39b05495...187a`. |
| Snapshot manifest | Immutable ABBY/JERC package | `<snapshot>/manifests/dataset_snapshot_r0001.json` | snapshot v1 | `39b05495...187a` | 1,024 members/site; 61,320 hours/site; validated in Iter001. |
| Global member split | Development/fixed-test boundary | `<snapshot>/splits/member_split_1024_v1.json` | 819/205 | `99467dea...fce` | Shared member identities; fixed-test reads forbidden. |
| Parameter design | 18 ordered PPE inputs | `<snapshot>/common/parameters_v1.nc` | snapshot component | `6af11a7f...39fb` | Manifest-owned immutable artifact. |
| ABBY/JERC site data | Features and C/N targets | `<snapshot>/sites/<SITE>/input_data_v1.nc` | snapshot components | ABBY `85f52690...c9c1`; JERC `a846c731...c0cb6` | Iter001 validation passed. |
| Iter002 baseline | Comparison configuration and interface | repository code plus Iter002 summary/artifact evidence | `(32,), tanh, alpha=40` | artifact `4c42e818...47064` | Technical/package pass; optimization recommended. |

`<snapshot>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`.

## Acceptance Gates and Decision Rule

- Exact 96-candidate uniqueness and array-index mapping; candidate 15/recorded baseline identity is
  explicitly validated.
- Exact shared split identities: 20 splits, 655/164 counts, development-only membership, no
  within-split overlap, identical cross-site use, and 4-or-5 validation appearances per member.
- Every eligible candidate produces all 20 repetitions, both targets, pooled/ABBY/JERC coverage,
  training/validation partitions, physical/log scales, finite metrics, convergence/timing evidence,
  and finite strictly positive predictions without clipping.
- Exceptions, nonfinite/numerically invalid outputs, identity drift, fixed-test access, or missing
  repetitions make a candidate ineligible. Convergence warnings are nonfatal but retained as
  ranking/stability evidence.
- Rank eligible candidates by the median across splits of the mean pooled validation log R2 across
  C/N. Within `0.005`, prefer lower median pooled log RMSE, then lower cross-split R2 standard
  deviation.
- A candidate is ineligible if any site's C or N median validation log R2 is more than `0.02` below
  the paired repeated-split Iter002-baseline configuration.
- Freeze the winner only after independent aggregation/selection validation; otherwise retain the
  Iter002 baseline. This is development selection, not release or fixed-test evidence.
- Any feature, site-input, solver, target-transform, fixed-test, all-development-release, or
  scientific decision-rule change requires fresh authorization.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | canonical `preflight_iter003.slurm` / `eded8dd5...3f75` | submitted/config/manifest hashes locked above | `<root>/runs/preflight`; `preflight_%j.out/.err` | snapshot/global split | execution manifest `0eb6c6a3...579a` | job `24472427` | `COMPLETED 0:0` | 45 s; MaxRSS 1,318,368 KiB; seven tests and `ITER003_PREFLIGHT_OK` passed. |
| smoke | canonical/submitted `cee67e77...8218` | locked config/manifests | `<root>/runs/smoke`; logs | preflight pass | manifest `0eb6c6a3...579a` | job `24472428` | `COMPLETED 0:0` | 30 s; MaxRSS 218,152 KiB; all three one-split candidates passed. |
| screen | canonical/submitted `b1597143...d3e1` | locked config/manifests | `<root>/runs/screen`; `screen_%A_%a.out/.err` | smoke/review pass | manifest `0eb6c6a3...579a` | array `24472431_[0-95]` | `COMPLETED 0:0` for all 96 leaves | 25 s to 5 min 24 s; peak batch MaxRSS 214,600 KiB; 96 result and 96 metrics files; no retry. |
| aggregate | canonical/submitted `1106557d...89a3` | locked config/manifest | `<root>/runs/aggregate`; `aggregate_%j.out/.err` | complete terminal screen | manifest `0eb6c6a3...579a` | job `24475235` | `COMPLETED 0:0` | 14 s; MaxRSS 95,252 KiB; selected candidate 74 from 42 eligible candidates. |
| validation | canonical/submitted `d55e2d43...4ace` | locked config/manifest and candidate/split hashes | `<root>/runs/validation`; `validation_%j.out/.err` | aggregate complete | manifest `0eb6c6a3...579a` | job `24475275` | `COMPLETED 0:0` | 11 s; MaxRSS 43,196 KiB; `ITER003_VALIDATE_OK selected=74`. |

## Independent Read-Only Review

- Preflight review 1: `block` against execution manifest `76d2b076...9067`; findings were legacy
  artifact-driver/config mismatch, missing IQR/worst summaries, insufficiently independent
  validation, omitted candidate/split provenance, incomplete aggregate/validation hash checks, and
  an incorrect baseline candidate label. All were corrected without scheduler action.
- Preflight re-review 2: `block` against corrected execution manifest `9701ce7c...2d6a`; independent
  selection recomputation was still incomplete. The validator was replaced with raw-metric
  recomputation and direct fixed-test/prohibited-output checks.
- Preflight re-review 3: `pass` with no findings against execution manifest `0eb6c6a3...579a`.
- Production review: `pass` with no findings; exact submitted copies and all hashes, unthrottled
  array shape, CLI/index mapping, baseline ID 15, attempt isolation, and fixed-test exclusion passed.

## Execution and Diagnostics

- Static validation: shell syntax, JSON syntax, execution-manifest verification, submitted-copy
  equality, and `git diff --check` passed before execution.
- Initialization: approved report and five external run directories created; advanced to
  `preparing`.
- Preparation: shell syntax, JSON syntax, `git diff --check`, execution-manifest verification, and
  submitted-copy equality passed. Proposed preflight command from the exact run directory:
  `sbatch --parsable --export=ALL,ITER003_PREFLIGHT_ATTEMPT=1,ITER003_CONFIG_SHA256=faa46ac9d4dd588491056960ebfd0cb427fe4ac1199529e031edeab44141ff9f,ITER003_EXECUTION_MANIFEST_SHA256=0eb6c6a38c30557c29df6ec2a502b80c2c49b73118b2e3414f442b14613e579a ./submit_preflight_iter003.slurm </dev/null`.
- Preflight: job `24472427` passed seven tests and emitted `ITER003_PREFLIGHT_OK candidates=96
  splits=20 no_training=true`; immutable candidate and split manifests were generated with hashes
  `30d45b26...a95d` and `8795d2b4...9307`.
- Exact submission commands and exports are preserved in the Slurm `SubmitLine` accounting and raw
  logs under the five external run directories.
- Job identity checks: all five submissions matched their locked script, work directory, account,
  partition, resources, time limit, and required exports. Production was the exact unthrottled
  `0-95` array.
- Queue and terminal accounting: preflight job `24472427` completed `0:0` in 45 seconds on
  `r7u01n2`; MaxRSS 1,318,368 KiB.
- Resource diagnostics: production leaves used 25 s to 5 min 24 s and at most 214,600 KiB batch
  RSS; aggregation used 14 s/95,252 KiB and validation 11 s/43,196 KiB. The retained production
  shape was conservative and no resource adjustment or retry was needed.
- Smoke resource evidence: candidate 15 took 7.13 s/307,808 KB; candidate 84 took 10.49 s/
  309,544 KB; candidate 90 took 5.94 s/310,036 KB. Retain one CPU/5 GB/two hours per array leaf.
- Failure, rejection, retry, or cancellation evidence: none.
- Closeout cross-record/static evidence: `ITER003_FOUR_RECORD_VALIDATE_PASS`; command
  `bash development/three_stage_surrogate/slurm/iter003/validate_closeout_iter003.sh
  --active-job-count 0`; all 100 top-level work units were terminal `COMPLETED`, and external
  aggregate/ranking/validation hashes matched the compact records.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| Iter003 configuration experiment | yes | 96 candidates x 20 shared splits; aggregate `eae3ef79...4ab7`; ranking `63c864b4...5ae`; independent validation `27f6a543...d38` | `pass` | Candidate 74 was independently reproduced as the winner; 42 candidates were eligible and every scheduled work unit completed without retry. |

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: freeze candidate 74—hidden layers `(64,32)`, `tanh`,
  alpha `10`, L-BFGS, `max_iter=800`, seed `42`—for the ABBY/JERC spinup stage. Its median across
  splits of mean pooled validation log R2 is `0.8910`, versus `0.8015` for baseline candidate 15;
  its paired primary mean delta is `+0.07655`. Site/target median log-R2 deltas range from
  `+0.07224` to `+0.09391`, so it clears the no-regression gate. Its 27 convergence warnings are
  nonfatal under the locked rule and remain a deployment limitation to record and validate.
- Limitations: two sites; development-only repeated splits; finite predefined MLP grid; `/xdisk`
  is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`; the campaign already requires freezing spinup
  configuration before an all-819 development refit and GPP handoff.
- Next action: seek fresh consolidated approval for the planning-only Iter004 proposal below.

## Proposed Next-Iteration Plan (Planning Only)

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

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required compact evidence copied to `summaries/iter003/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] One verified no-push closeout commit created
