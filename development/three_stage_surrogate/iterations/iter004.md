# iter004 - ABBY/JERC spinup robustness and release

## Status

- Iteration ID: `iter004`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter004_abby_jerc_spinup_release`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-31T01:41:02-07:00`
- Closed: `2026-10-31T04:59:22-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 4, frozen spinup configuration release
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Sequential ID and work type: `iter004` / `implementation`.
- Objective: characterize the frozen candidate-74 configuration with fresh development-only
  robustness evidence and a member-balanced empirical surrogate-error product, refit it on all 819
  development members, independently validate and publish a versioned ABBY/JERC inference artifact,
  and freeze the predicted-C/N handoff needed by the later GPP stage.
- Inputs and trust boundary: immutable input snapshot `r0001`; exact 819-development/205-fixed-test
  manifest; Iter003 winner `(64,32)`, `tanh`, alpha `10`, L-BFGS, `max_iter=800`, seed `42`; and the
  validated 25-feature, natural-log-target, separate fit-only scaler/model, positive exponentiated
  prediction, and no-clipping interface. Only recorded hashes are trusted and compatibility is
  revalidated before execution.
- Robustness design: an immutable seed-`20261031` manifest defines 20 deterministic balanced,
  ABBY/JERC-synchronized 655/164 splits from only the 819 development identities. It differs from
  Iter003 seed `20261030`; every member appears in validation four or five times. Only frozen
  candidate 74 is fit; no selection or retuning is permitted.
- Robustness evidence: paired held-out C/N truth and prediction by repetition, site, and member;
  physical and natural-log residuals using `prediction minus ELM`; per-repetition and cross-
  repetition R2, RMSE, MAE, signed bias, residual standard deviation, and quantiles
  `0.01,0.025,0.05,0.25,0.50,0.75,0.95,0.975,0.99`; per-repetition site log-error bias and 2x2 C/N
  covariance/correlation; and same-member surrogate/depth-error dependence where supported by the
  validated preprocessing.
- Uncertainty rule: retain raw and per-repetition evidence and calculate one site-specific
  surrogate log-error bias vector and 2x2 covariance by member-balanced pooling. A member with `k`
  validation appearances gives weight `1/k` to each occurrence; normalize over members and use
  population (`ddof=0`) weighted covariance. This is only the surrogate component for later MCMC
  selection, not observational, depth, or total likelihood covariance.
- Release scope: after eligible robustness evidence, fit the frozen model once on all 819
  development members; create a new artifact schema for models and fit-only scalers; generate an
  in-sample ABBY/JERC predicted-C/N handoff for all 819 members; and validate flexible-size
  inference, serialization, fresh-process reload, identities, and package hashes before publication.
- File contracts: hash-verified pickle plus JSON manifest for the sklearn artifact; NetCDF4 plus
  JSON manifest for the 819-member handoff; NetCDF4 for paired robustness evidence and uncertainty
  summaries; CSV for human-readable metric distributions; JSON for split, schema, provenance, and
  package manifests. The handoff contains predicted C/N and exact `(site, member_id)` coordinates,
  but no ELM C/N truth or duplicated parameter/features.
- NetCDF naming: explicit `TOTSOMC_*` and `TOTSOMN_*` variables, including `*_elm`, `*_predicted`,
  `*_residual`, `*_log_elm`, `*_log_predicted`, and `*_log_residual`; summaries use explicit
  per-target bias/variance and `TOTSOMC_TOTSOMN_log_error_covariance` names. Products record units,
  dimensions, identities, definitions, hashes, and residual convention.
- Bounded work: locked preparation and two read-only review gates; one no-training preflight; one
  20-split robustness run; one uncertainty aggregation; one all-819 release fit/staging run; one
  independent release-validation run; catalog-last publication; concise records; and one no-push
  closeout commit. Preflight uses lightweight fixtures and performs no model training.
- Exclusions: no fixed-test parameter or target access; no configuration, feature, solver, target,
  or split selection; no held-out performance claim from the all-development fit; no GPP/SR fit;
  no observations, fitted uncertainty, total MCMC covariance, posterior work, campaign-plan edit,
  full-chain robustness claim, or push.
- Storage: run root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter004_abby_jerc_spinup_release`;
  stable root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc`;
  immutable `release_0001` with artifact, handoff, uncertainty, validation, and top-level manifest.
  Validated staged files are copied, hashes reverified, and the product catalog updated last. No
  hardlink or symlink joins published and run trees. The immutable input snapshot is unchanged.
- Retention: `/xdisk` is accepted as temporary unbacked operational publication. Independent run
  and release copies on the same filesystem are not backups; neither is deleted during Iter004.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `Yes, full package approved.` Recorded `2026-10-31T01:41:02-07:00`. This clean approval applies to the entire revised package after removal of the smoke test and increase to three retry opportunities. |
| Kickoff goal, finite work-unit count, and stop conditions | Five sequential Slurm submissions: no-training preflight, robustness, uncertainty aggregation, all-819 release fit/staging, and independent release validation. Continue through publication, terminal accounting, concise records, validation, and one no-push commit if every gate passes. Stop before GPP/SR training, fixed-test evaluation, full-chain robustness, MCMC, or unapproved changes. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb6865...9128`; progression item 4; aligned; deviation none. |
| Confirmed HPC system and site profile | UA Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; account/partition `chopinsong/standard`; interpreter `/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python`. |
| Approved output and storage policy | Create the exact run root and its five run directories plus staging. Keep raw outputs external. After all gates pass, copy to stable `release_0001`, reverify, and update the catalog last. `/xdisk` is temporary and unbacked; preserve both copies. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Snapshot/member/configuration/feature/target/split identities; seed-20261031 20-split design; member-balanced uncertainty rule; release schemas; fixed-test and retuning prohibitions; gates and all-or-nothing publication rule in this report. |
| Lifecycle authority | Authorizes Iter004 records; bounded implementation, tests, CLIs, scripts, configurations, manifests, validators; exact directories; two read-only reviews; five submissions; publication after validation; monitoring/accounting; bounded retries/cancellation; concise closeout records; and one scoped no-push commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | All five jobs use Puma `chopinsong/standard`, one node/task/CPU, Puma-derived 5 GB, no GPU, single-thread BLAS/OpenMP, and `OLMT_puma`. Preflight, aggregation, and validation: 30 minutes each; robustness and all-819 fit: two hours each. Each work unit has its initial attempt plus at most three unchanged resubmissions only after proven scheduler, transport, node, or preemption failure. OOM/timeout grants neither resource change nor unchanged retry. No application/code/schema/data/numerical/interface/scientific retry after submission without fresh approval. Use job-scoped scheduler monitoring and a supported wait mechanism through authoritative terminal `sacct`. |
| Cancellation scope | Only recorded Iter004 jobs, and only for identity mismatch, duplicate submission, unsafe behavior, or explicit user direction; terminal accounting remains required. |
| Outside-sandbox authority | Locked `sbatch` submissions and authorized unchanged retries; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` only for the conditions above. |
| Closeout branch | One scoped Iter004 no-push closeout commit authorized. |

### Runtime debugging amendment

After robustness attempt 1 failed before fitting, the user responded `Approved. And no need to ask
me again for this kind of debugging unless it might change our scientific purpose.` This authorizes
the exact development-position correction and future bounded implementation/interface debugging,
manifest/submitted-copy refreshes, re-reviews, and retries within the remaining approved attempt
budget when the locked scientific purpose, data boundary, estimator, split design, formulas,
schemas, resources, gates, and interpretation remain unchanged. Any change that might alter
scientific purpose or interpretation still requires fresh user approval.

The approved goal was established in the active session. Base commit is
`11900419f8b1ea22002bb7a789574d2f6f500416`; the pre-initialization `CURRENT.md` planning diff had
SHA-256 `d66a55cccdbe5e6250db088150b68218bd6876dfacacaea6bd923cc57d75c67a`.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction and invariants | `development/three_stage_surrogate/PLAN.md` | approved plan | `9bbb6865...9128` | Iter003 aligned; no deviation. |
| Workflow | Lifecycle authority | `development/three_stage_surrogate/WORKFLOW.md` | base commit `1190041` | `f23f040e...dc4` | Current canonical workflow. |
| Puma profile | Site/runtime contract | `development/hpc/puma.md` | base commit `1190041` | `12d05836...2851` | Confirms scheduler and derived memory rule. |
| Snapshot catalog | Published input selector | `<snapshot>/catalog.json` | catalog v1 / `r0001` | `24b5bbdd...a8a4` | Selects the locked snapshot. |
| Snapshot manifest | Immutable ABBY/JERC package | `<snapshot>/manifests/dataset_snapshot_r0001.json` | snapshot v1 | `39b05495...187a` | Iter001 validation passed. |
| Global member split | Development/fixed-test boundary | `<snapshot>/splits/member_split_1024_v1.json` | 819/205 | `99467dea...0fce` | Shared identities; fixed-test access forbidden. |
| Parameter design | 18 ordered PPE inputs | `<snapshot>/common/parameters_v1.nc` | snapshot component | 276751 bytes | Manifest-owned immutable component. |
| ABBY site input | Features and C/N targets | `<snapshot>/sites/ABBY/input_data_v1.nc` | snapshot component | 438515369 bytes | Iter001 validation passed. |
| JERC site input | Features and C/N targets | `<snapshot>/sites/JERC/input_data_v1.nc` | snapshot component | 427530711 bytes | Iter001 validation passed. |
| Iter003 selection | Frozen estimator and evidence | `development/three_stage_surrogate/summaries/iter003/` | candidate 74 | aggregate `eae3...4ab7`; ranking `63c864...05ae`; validation `27f6...9d38` | Independent selection validation passed; 27/40 warnings retained. |

`<snapshot>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`.

## Acceptance Gates and Decision Rule

- Exact snapshot, 819/205 member boundary, candidate-74 estimator, 25-feature order, natural-log
  target transform, seed-20261031 split identity, and explicit file-schema identities.
- Exactly 20 by 164 held-out rows per site, four-or-five validation appearances per development
  member, no fixed-test identity or data access, and complete paired C/N evidence.
- Finite metrics, quantiles, bias vectors, and covariance; covariance symmetry tolerance `1e-12`
  and minimum eigenvalue at least `-1e-12`.
- Finite strictly positive predictions without clipping; exact all-and-only 819 development-member
  fit scope; deterministic flexible-size inference; serialization and fresh-process reload
  equivalence with `rtol=1e-12`, `atol=1e-10`.
- Complete self-describing component and package hashes, independent validation, and no active or
  unaccounted jobs. Convergence warnings are diagnostic and do not alone fail a gate.
- Publish and authorize the artifact, handoff, and uncertainty product only if every gate passes.
  Otherwise publish nothing and retain candidate 74 as frozen but unreleased. There is no
  performance threshold and robustness evidence cannot authorize retuning.
- Any feature, site-input, estimator, target transform, split/scientific rule, schema, fixed-test,
  GPP/SR, MCMC, resource, or post-submission application correction requires fresh authorization.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter004.slurm` / `dff7c648...86b0` | submitted `dff7c648...86b0`; config `3de0ed3f...9fd1`; manifest `74b1b8ce...aa81` | `<root>/runs/preflight`; `preflight_%j.out/.err` | locked snapshot/global split | base `1190041`; execution manifest `74b1b8ce...aa81` | job `24479223` | `COMPLETED 0:0` | Attempt 1; 25 s; MaxRSS 1,307,180 KiB; no retry. `ITER004_PREFLIGHT_OK`; split file `7644ed38...ace0`, design `0b343378...6ecb`; no training. |
| robustness | `robustness_iter004.slurm` / `72cd39b8...3d9d` | submitted script unchanged; attempt 1 manifest `74b1b8ce...aa81`; attempt 2 manifest `4798b2b6...7d87` | `<root>/runs/robustness`; `robustness_%j.out/.err` | preflight pass/generated split; second review; correction re-review pass | base `1190041`; attempt-specific manifests preserved | jobs `24479279`, `24480121` | attempt 1 `FAILED 1:0`; attempt 2 `COMPLETED 0:0` | Attempt 1 failed before fitting; exact provenance preserved. Attempt 2 passed in 2m58s, MaxRSS 1,307,596 KiB; 6,560 paired observations, 168 metric rows, 80 depth rows, 22 warnings. |
| uncertainty | `uncertainty_iter004.slurm` / `0f2f89c3...6976` | submitted `0f2f89c3...6976`; config `3de0ed3f...9fd1`; manifest `4798b2b6...7d87` | `<root>/runs/uncertainty`; `uncertainty_%j.out/.err` | robustness attempt 2 terminal pass | base `1190041`; execution manifest `4798b2b6...7d87` | job `24480153` | `COMPLETED 0:0` | Attempt 1; 13 s; MaxRSS 204,776 KiB; member-balanced `ddof=0` aggregation passed. ABBY/JERC minimum covariance eigenvalues 0.00298/0.00287. |
| release fit/staging | `release_fit_iter004.slurm` / `08053637...3901` | submitted `08053637...3901`; config `3de0ed3f...9fd1`; manifest `4798b2b6...7d87` | `<root>/runs/release_fit`; `release_fit_%j.out/.err` | uncertainty terminal pass | base `1190041`; execution manifest `4798b2b6...7d87` | job `24480174` | `COMPLETED 0:0` | Attempt 1; 25 s; MaxRSS 1,053,812 KiB; exact 819/1,638 scope; artifact `9abb342d...a809`; handoff `9e2d5be4...fdb5`; both convergence warnings retained. |
| validation | `validation_iter004.slurm` / `23dfdaf0...57d2` | submitted `23dfdaf0...57d2`; config `3de0ed3f...9fd1`; manifest `4798b2b6...7d87` | `<root>/runs/validation`; `validation_%j.out/.err` | release-fit attempt 1 complete | base `1190041`; execution manifest `4798b2b6...7d87` | job `24480199` | `COMPLETED 0:0` | Attempt 1; 16 s; MaxRSS 1,061,016 KiB; `ITER004_VALIDATE_OK`; 14-file package manifest `69f840f7...f2dc`; all gates passed. |

`<root>` is the approved Iter004 run root above.

## Independent Read-Only Review

- Reviewer: independent agent `/root/iter004_preflight_review`.
- Reviewed source hash: initial execution manifest `cb172e07...bfdb`; corrected manifest
  `74b1b8ce6b6ecf9cb190605665cbe462ca46b63e3695a73a416e4042b541aa81`.
- Outcome: initial `block`; corrected-package re-review `pass_with_concerns`.
- Findings and primary-agent response: initial review found fixed-test preprocessing reads and
  unproved source-member alignment, non-retryable shared staging writes, a self-inconsistent split
  identity, incomplete robustness metadata, and trusted rather than recomputed appearance counts.
  Before submission, the primary agent changed depth access to the exact 819 development indices
  with coordinate and immutable-target equality checks; made release-fit and validation packages
  attempt-local with a separate post-validation promotion; defined one split-payload hash; added
  target/source metadata; and independently recomputed counts in validation. Submitted copies and
  manifest were refreshed and reverified. Re-review passed at `2026-10-31T01:49:49-07:00` with one
  concern: the no-training preflight does not exercise the preprocessing-depth schema. The primary
  accepted this because both source files are hash-locked and robustness validates dimensions,
  coordinates, exact development-only values, and snapshot equality before fitting the first
  split. Any incompatibility is an application/interface failure and stops without retry.
- Substantive review: `pass_with_concerns` at `2026-10-31T02:01:52-07:00`. The reviewer
  independently reproduced the file hash `7644ed38...ace0`, canonical design `0b343378...6ecb`, 20
  split IDs, exact 655/164 development partitions, zero fixed-test hits, and the 815/4 plus 4/5
  appearance balance; verified all downstream submitted copies and attempt-local interfaces; and
  retained only the already accepted preprocessing-depth pre-fit validation concern.

## Execution and Diagnostics

- Static validation: shell syntax, JSON syntax, execution-manifest verification, submitted-copy
  equality, `git diff --check`, and exact external file hashes passed at
  `2026-10-31T01:46:14-07:00`. Repository Python was not run on the login node.
- Preflight: job `24479223` passed at `2026-10-31T01:55:36-07:00`; snapshot and global split
  identities, 20 fresh balanced splits, release serialization, and NetCDF fixtures passed with
  `no_training=true`.
- Exact proposed preflight submission command: from `<root>/runs/preflight`,
  `sbatch --parsable --export=ALL,ITER004_ATTEMPT=1,ITER004_CONFIG_SHA256=3de0ed3fbfdab0900b1d0ffd67c174805ad3144128771bce4bc08f88f9139fd1,ITER004_EXECUTION_MANIFEST_SHA256=74b1b8ce6b6ecf9cb190605665cbe462ca46b63e3695a73a416e4042b541aa81 ./submit_preflight_iter004.slurm`.
- Exact proposed robustness command: from `<root>/runs/robustness`,
  `sbatch --parsable --export=ALL,ITER004_ATTEMPT=1,ITER004_PREFLIGHT_ATTEMPT=1,ITER004_CONFIG_SHA256=3de0ed3fbfdab0900b1d0ffd67c174805ad3144128771bce4bc08f88f9139fd1,ITER004_EXECUTION_MANIFEST_SHA256=74b1b8ce6b6ecf9cb190605665cbe462ca46b63e3695a73a416e4042b541aa81,ITER004_SPLIT_SHA256=7644ed38ffa33536e6b6cfcdbc6d80181f31282a84b8e81218ab3e2abfb4ace0 ./submit_robustness_iter004.slurm`.
- Job identity checks: preflight `24479223` and robustness `24479279` each matched approved
  account, partition, script, workdir, resources, time limit, and exact exports immediately after
  submission. Robustness attempt 2 `24480121`, uncertainty `24480153`, release fit `24480174`, and
  validation `24480199` likewise matched their approved identities and resources.
- Queue and terminal accounting: preflight `24479223` terminal `COMPLETED 0:0`, elapsed 25 s,
  TotalCPU 4.522 s, one CPU, MaxRSS 1,307,180 KiB, requested 5 GB, node `r7u01n1`.
  Robustness attempt 1 `24479279` is terminal `FAILED 1:0`, elapsed 24 s, TotalCPU 11.218 s,
  MaxRSS 214,888 KiB, node `r7u01n1`. Attempt 2 `24480121` is terminal `COMPLETED 0:0`, elapsed
  2m58s, TotalCPU 2m22.584s, MaxRSS 1,307,596 KiB, requested 5 GB, node `r7u04n1`.
- Resource diagnostics: Iter003 candidate-74 repetitions took approximately 4.5--7.5 seconds and
  prior peak RSS was approximately 215 MB. Successful robustness/uncertainty/release-fit/validation
  jobs used 2m58s/13s/25s/16s and batch MaxRSS 1,307,596/204,776/1,053,812/1,061,016 KiB.
- Failure, rejection, retry, or cancellation evidence: robustness attempt 1 job `24479279` failed
  before the first fit. The validated preprocessing reader returned an 819-element array ordered by
  `snapshot.development_ranked`, but the diagnostic indexed it with global zero-based member
  numbers; member `g01020` produced index 1019 and `IndexError`. This was an application-code
  failure, not an authorized scheduler retry under the original contract. The user approved the
  bounded repair and non-scientific debugging authority: map each development member ID to its
  exact position in the 819-element development order, use that map for diagnostic selection, add
  explicit coverage/order assertions, refresh source and submitted manifests, obtain re-review,
  and retry robustness as attempt 2. The corrected code and execution manifest
  `4798b2b6...7d87` passed re-review; attempt 2 completed successfully.
  The first correction re-review blocked only because the active manifest refresh had overwritten
  the submitted attempt-1 manifest. The exact historical contents are now preserved in Git as
  `iter004_execution_manifest_attempt1.sha256` and externally in the robustness run directory as
  `iter004_execution_manifest_attempt_1.sha256`; both hash to the actual submitted identity
  `74b1b8ce...aa81`. Active attempt-2 material remains `4798b2b6...7d87`; provenance re-review
  returned `pass` at `2026-10-31T04:37:29-07:00`, confirming exact attempt-1 provenance,
  active-copy equality, attempt-2 isolation, and no scientific or resource change.
- Publication: the validated attempt-local package was promoted into shared staging with every
  manifest-owned hash verified. Stable `release_0001` was then copied, reverified, and cataloged
  last. Run, staging, validation, and stable manifests all hash to `69f840f7...f2dc`; stable and
  staging artifact files are different single-link inodes. Catalog hash is `93f080de...10be`.
- Closeout validation: `ITER004_FOUR_RECORD_VALIDATE_PASS`; command
  `bash development/three_stage_surrogate/slurm/iter004/validate_closeout_iter004.sh
  --active-job-count 0`; report, cumulative summary, registry, handoff, proposal equality, external
  identities, stable catalog, and zero-active-job record agree.
- Final source hygiene removed one trailing blank line from the release module after runtime. Exact
  runtime attempt-2 source remains reproducible under archived manifest `4798b2b6...7d87`; the
  behavior-identical closeout source verifies under canonical manifest `ed9a1f14...811a`. No
  executable statement, interface, schema, output, or scientific behavior changed.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| Preflight | yes | `ITER004_PREFLIGHT_OK`; job `24479223`; split `7644ed38...ace0` | `pass` | No training; exact dependencies, balanced splits, serialization, and NetCDF fixtures passed. |
| Robustness | yes | job `24480121`; evidence `702a336b...024a`; metrics `ef8319de...ea8` | `pass` | Complete 20 x 164 x 2 coverage, finite positive predictions, zero fixed-test access, and declared diagnostics. |
| Uncertainty | yes | job `24480153`; NetCDF `f15a25b1...411c` | `pass` | Member-balanced `ddof=0` bias/covariance is finite, symmetric, and PSD for both sites. |
| Release fit | yes | job `24480174`; artifact `9abb342d...a809`; handoff `9e2d5be4...fdb5` | `pass` | Exact all-and-only 819-development/1,638-row fit; in-sample handoff is positive and self-describing. |
| Validation/publication | yes | job `24480199`; `ITER004_VALIDATE_OK`; manifest `69f840f7...f2dc` | `pass` | Independent reload, flexible prediction, hashes, covariance, identities, catalog-last copy, and fixed-test exclusion passed. |

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: publish and authorize spinup `release_0001`, its
  predicted-C/N development handoff, and its explicitly surrogate-only uncertainty package for
  downstream GPP and later MCMC development. Candidate 74 remains frozen. The failed attempt-1
  diagnostic-indexing bug was non-scientific, corrected under explicit user authority, and fully
  preserved; all subsequent gates passed.
- Limitations: two sites; development-only robustness; all-819 release predictions are in-sample;
  surrogate-only error component; temporary unbacked `/xdisk`; no fixed-test or full-chain evidence.
- Campaign-plan amendment recommendation: `none`.
- Next action: close records and commit; seek fresh consolidated approval for planning-only Iter005.

## Proposed Next-Iteration Plan (Planning Only)

### Iter005 - ABBY/JERC GPP input and inference-interface materialization

- Proposed sequential ID/work type: `iter005` / `data_initialization`.
- Campaign alignment: `development/three_stage_surrogate/PLAN.md`, SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`; progression item 5;
  `aligned`; proposed deviation `none`.
- Evidence-derived objective: before any hourly GPP fit, implement and independently validate the
  memory-aware ABBY/JERC GPP loader, timestamp-aware feature builder, and deterministic inference
  interface using the published spinup `release_0001` and its 819-member predicted-C/N handoff.
  Freeze a reusable prepared-data contract that a later GPP baseline can consume without ELM C/N.
- Inputs/dependencies: immutable snapshot `r0001` and its exact 819-development/205-fixed-test
  boundary; stable spinup catalog `93f080de...10be`, release manifest `69f840f7...f2dc`, artifact
  `9abb342d...a809`, and handoff `9e2d5be4...fdb5`; ABBY/JERC forcing and ELM GPP targets in the
  snapshot; canonical 18-parameter order; and site-specific no-leap timestamp axes. Trust only
  recorded hashes and reject any identity, time, unit, or coverage mismatch.
- Bounded scope/work units: locked implementation and read-only review; one no-training preflight;
  one compute-node streaming/sharded development-only materialization; one independent contract
  validation; concise records; and one user-selected closeout branch. Implement one shared
  training/inference feature path with explicit `upstream_mode=in_sample`; predicted C/N only;
  exact site/member/time coordinates; actual-timestamp `sin_hour`, `cos_hour`, `sin_doy`, and
  `cos_doy`; declared forcing/history features and masks; per-site coverage; and deterministic
  shard/manifests. Unsupported upstream modes fail explicitly.
- Exclusions: no GPP model fit, tuning, artifact, or performance claim; no fixed-test parameter,
  C/N, GPP, or forcing access; no true ELM C/N as an upstream feature; no SR, full-chain robustness,
  observations, MCMC, campaign-plan edit, or push. Do not silently force a common site window or
  materialize duplicated parameter/CN columns when indexed references suffice.
- Tentative gates/decision: exact snapshot/release/member/parameter/site/time identities; all and
  only 819 development members; zero fixed-test access; GPP units/valid masks and each site's full
  declared window preserved; no-leap calendar and timestamp-derived cyclic features independently
  reproduced; predicted-C/N values exactly match the release handoff; training and inference
  feature order/values agree on sampled rows; deterministic shard hashes and row accounting;
  bounded memory behavior; no active/unaccounted jobs; independent validation. Publish the prepared
  GPP-input contract only if all gates pass; otherwise publish nothing and retain spinup release as
  valid but GPP-uninitialized.
- Proposed site/output/resources: Puma `chopinsong/standard`; run root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter005_abby_jerc_gpp_input`;
  temporary unbacked `/xdisk`, with raw/sharded data external and compact schemas/evidence in Git.
  Propose one CPU/derived 5 GB/30 minutes for preflight and validation, and four CPUs/derived 20 GB/
  four hours for streaming materialization, single-threaded per worker and no GPU. Confirm capacity
  and input sizes at kickoff; any different shape requires explicit package approval.
- Proposed review/monitoring/retry/cancellation: independent read-only review before preflight and
  substantive materialization; exact submitted copies and configurations; job-scoped monitoring
  through terminal `sacct`; initial attempt plus up to three same-scope retries or bounded
  non-scientific debugging corrections that preserve the approved contract; any scientific,
  feature, target, coverage, upstream-mode, fixed-test, or resource change requires fresh approval.
  Cancel only recorded Iter005 jobs for identity mismatch, duplicate submission, unsafe behavior,
  or explicit user direction.
- Expected evidence/stop: validated GPP target/forcing/time inventory; frozen feature schema and
  units; predicted-C/N join proof; development-only shard/index manifests and hashes; sampled
  training/inference equivalence; coverage/mask/resource evidence; concise records. Stop before any
  GPP fitting. Fresh consolidated approval is required before initialization, directory creation,
  implementation, execution, scheduler mutation, publication, records, or closeout.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter004/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit
