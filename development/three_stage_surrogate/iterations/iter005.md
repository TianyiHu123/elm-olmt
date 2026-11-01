# iter005 - ABBY/JERC GPP initialization and baseline

## Status

- Iteration ID: `iter005`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter005_abby_jerc_gpp_baseline`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-31T16:37:48-07:00`
- Closed: `2026-10-31T22:17:39-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 5, two-site GPP development
- Alignment: `aligned_with_scoped_deviation`
- Approved deviation: use the published all-819 predicted-C/N handoff for both the 655 GPP-training
  and 164 GPP-validation members. The validation evidence is GPP-stage conditional on the fixed
  upstream product, not end-to-end spinup -> GPP held-out evidence. Later full-chain robustness
  remains required; no `PLAN.md` amendment is authorized.

## Finalized Plan

- Sequential ID and work type: `iter005` / `implementation`.
- Objective: implement and independently validate memory-aware ABBY/JERC GPP data, feature,
  artifact, and deterministic inference interfaces, then characterize one fixed-configuration
  655-training/164-validation GPP baseline using every valid hourly row.
- Inputs and trust boundary: immutable snapshot `r0001`; exact 819-development/205-fixed-test
  boundary; stable spinup `release_0001`, artifact, and predicted-C/N handoff; prepared ABBY/JERC
  forcing and GPP; canonical 18-parameter order; and site-specific no-leap timestamps. Trust only
  the recorded hashes and fail on identity, schema, unit, time, or coverage mismatch.
- Split: first 655 ranked development members fit and remaining 164 validate, matching Iter002.
  Smoke uses the first 80/20 members and first 1,440 hours. Fixed-test data are forbidden.
- Upstream policy: directly join the published all-819 predicted-C/N handoff to both sides of the
  GPP split. Do not fit, tune, or execute the spinup surrogate. Label validation
  `fixed_upstream_gpp_stage` and disclose that the 164 GPP-validation members were included in the
  upstream spinup fit.
- Features: 43 ordered inputs: seven raw forcing variables; timestamp-derived hour and day-of-year
  sine/cosine terms; 24/168/720-hour TBOT means and PRECTmms sums; 30-day PRECTmms, FSDS, and TBOT
  anomalies; 18 ordered parameters; `PCT_SAND`, `PCT_CLAY`, `ORGANIC`; and predicted
  `TOTSOMC`/`TOTSOMN`. Site identity is metadata only. Full-window starts use explicit partial-history
  semantics; arbitrary inference windows require sufficient ordered history.
- Target/model: physical-unit GPP (`gC/m^2/day`), fit-only standardization, no log transform and no
  clipping. One configuration-driven sklearn MLP: `(128,)`, ReLU, Adam, alpha `1e-4`, adaptive
  learning rate with initial `0.001`, `max_iter=500`, early stopping, internal validation fraction
  `0.1`, `n_iter_no_change=10`, tolerance `1e-4`, batch size `auto`, shuffle, seed `42`. The internal
  row-random subset uses only 655 GPP-training members and is optimizer control, not scientific
  validation.
- Bounded work: independent read-only review; four sequential Slurm submissions—combined
  preparation, smoke, baseline, and final validation; concise records; and one no-push closeout
  commit. The combined preparation job runs lightweight no-training preflight, conditionally
  materializes attempt-local inputs, and invokes an independent fresh-process validator before
  marking the cache eligible.
- Exclusions: no grid/configuration search, feature selection, temporal subsampling, spinup
  execution, 20-repetition robustness, all-819 GPP fit, GPP release/uncertainty/SR handoff, fixed-test
  access, true ELM C/N feature, site-category feature, SR, observations, MCMC, campaign-plan edit,
  or push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `Full package approved`; recorded `2026-10-31T16:37:48-07:00`, after directing combination of preflight/materialization/materialization-validation and receiving the complete revised package. |
| Kickoff goal, finite work-unit count, and stop conditions | Four sequential submissions: combined preparation, smoke, 655/164 baseline, final validation. Continue through terminal accounting, immutable-gate evaluation, concise records, one no-push commit, and a user decision of `freeze_baseline` or `optimization_required`. Stop for exhausted retries or unapproved change. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb6865...9128`; progression item 5; `aligned_with_scoped_deviation`; fixed all-819 upstream handoff on both sides of the GPP split. |
| Confirmed HPC system and site profile | UA Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter005_abby_jerc_gpp_baseline` with `runs/{prepare,smoke,baseline,validation}`. Keep caches, models, predictions, logs, and detailed evidence external; compact evidence in Git. `/xdisk` is temporary and unbacked; expiration was unavailable to a non-PI query. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities, split, 43-feature order, physical target, fixed MLP, fixed-upstream limitation, all-valid-hour scope, fixed-test prohibition, technical gates, metrics, and decision rule in this report. |
| Lifecycle authority | Iter005 report/scaffold; bounded implementation/tests/configurations/manifests/validators; exact directories; independent read-only reviews; four submissions; monitoring/accounting; evaluation; bounded corrections/retries/cancellation; concise records; one commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Prepare 4 CPUs/derived 20 GB/4 h; smoke 4 CPUs/derived 20 GB/2 h; baseline total 200 GB/Puma-derived 40 CPUs/16 h; validation 8 CPUs/derived 40 GB/4 h. Job-scoped monitoring and supported waiting through terminal `sacct`. At most three additional submissions total for unchanged scheduler/node/transport failures or bounded non-scientific implementation/interface corrections preserving every locked scientific/data/model/resource/gate/interpretation term; changed material requires preserved evidence and re-review. OOM, timeout, data/schema, numerical-policy, feature/model/split, or resource change requires fresh approval. |
| Cancellation scope | Recorded Iter005 jobs only, for identity mismatch, duplicate submission, unsafe/runaway behavior, proven universal defect, or explicit user direction; terminal accounting remains required. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` only under the conditions above. |
| Closeout branch | One scoped no-push Iter005 closeout commit. |

Base commit is `0b50975ca7c66e9ab6b9ad0d5bfb8580bd4aeec4`; the approved pre-initialization
`CURRENT.md` planning diff had SHA-256
`8e37a2d63cc885a22aa14451ed3556bf986ab5bb8b883312433416e3553c259e`.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction/invariants | `development/three_stage_surrogate/PLAN.md` | approved plan | `9bbb6865...9128` | Iter004 aligned; scoped Iter005 deviation approved. |
| Workflow | Lifecycle authority | `development/three_stage_surrogate/WORKFLOW.md` | base `0b50975` | `f23f040e...dc4` | Canonical workflow. |
| Puma profile | Site mechanics | `development/hpc/puma.md` | base `0b50975` | `12d05836...2851` | Account/resource semantics checked. |
| Snapshot catalog | Input selector | `<snapshot>/catalog.json` | catalog v1 / `r0001` | `24b5bbdd...a8a4` | Live hash matched. |
| Snapshot manifest | Immutable inputs | `<snapshot>/manifests/dataset_snapshot_r0001.json` | snapshot v1 | `39b05495...187a` | Live hash matched; 1,024 members and 61,320 hours/site. |
| Global split | Development/fixed-test boundary | `<snapshot>/splits/member_split_1024_v1.json` | 819/205 | `99467dea...4fce` | Live hash matched. |
| ABBY/JERC inputs | Forcing, GPP, surface | `<snapshot>/sites/<SITE>/input_data_v1.nc` | prepared NetCDF | ABBY 438515369 B; JERC 427530711 B | Iter001 independently validated. |
| Spinup catalog | Stable product selector | `<spinup>/catalog.json` | release catalog v1 | `93f080de...10be` | Live hash selects `release_0001`. |
| Spinup release | Artifact and handoff package | `<spinup>/release_0001/release_manifest.json` | release package v1 | `69f840f7...f2dc` | Live hash matched. |
| Spinup artifact | Frozen upstream model | `<spinup>/release_0001/artifact/spinup_release_artifact.pkl` | Iter004 release | `9abb342d...a809` | Validated release; not executed in Iter005. |
| Predicted-C/N handoff | Fixed upstream inputs | `<spinup>/release_0001/handoff/spinup_predicted_cn.nc` | 819 development members | `9e2d5be4...fdb5` | Live hash matched; all rows in-sample to spinup fit. |

`<snapshot>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`.
`<spinup>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc`.

## Acceptance Gates and Decision Rule

- Exact input/release/member/parameter/site/time/unit/schema identities and exact first-655/last-164
  development split; zero fixed-test access and zero spinup execution.
- Exactly 100,442,160 site/member/hour rows and ordered 43-feature contract. A deterministic float32
  design memmap may occupy 17,276,051,520 bytes, with hash-verified layout and row indexes.
- Full declared valid coverage, timestamp-derived cyclic features, rolling/history boundary behavior,
  and exact predicted-C/N join independently reproduced.
- GPP fit scalers and stopping state see only 655 training members. Training and fresh-process
  inference agree on sampled/interior/history-boundary rows; flexible batch sizes and reload
  equivalence pass; predictions are finite and unclipped.
- Hourly and complete-day (`24/24`, `sum(hourly)/24`) train/validation R2, RMSE, MAE, signed
  `prediction - ELM` bias, residual SD, gaps, coverage, and quantiles
  `0.01,0.025,0.05,0.25,0.50,0.75,0.95,0.975,0.99` are reported per site and pooled.
- Scores are characterization, not technical thresholds. Technical pass requires independent
  validation and terminal accounting, then pauses for the user's `freeze_baseline` or
  `optimization_required` decision. A failure publishes no baseline artifact.
- Any scientific interpretation, feature, target, split, model, fixed-test, upstream mode, output,
  gate, or resource-cap change requires fresh approval.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prepare | `c917e5c2...8242` | equal canonical; config `185dbc6a...21a`; manifest `62de2e48...216e` | `<root>/runs/prepare`; `prepare_%j.out/.err` | locked inputs | base `0b50975`; manifest `62de2e48...216e` | `24485863` | `COMPLETED 0:0` | 3:55; 4 CPUs/20 GB; peak 17.76 GB; preflight, materialization, full hashes, exact layout and 20-row source reconstruction passed; eligible. |
| smoke | `341ab5d5...2b7` | equal canonical; same config/manifest | `<root>/runs/smoke`; `smoke_%j.out/.err` | eligible preparation attempt 1 | base `0b50975`; manifest `62de2e48...216e` | `24485909` | `COMPLETED 0:0` | 28 s; 4 CPUs/20 GB; MaxRSS 619,556 KiB; separate 230,400 fit and 57,600 validation-inference rows; passed. |
| baseline | `9cb180c1...662` | equal canonical; same config/manifest | `<root>/runs/baseline`; `baseline_%j.out/.err` | preparation/smoke attempt 1 pass | base `0b50975`; manifest `62de2e48...216e` | `24485952` | `COMPLETED 0:0` | 1:34:30; 40 CPUs/200 GB; batch MaxRSS 32,771,276 KiB; 29 iterations, 0 convergence warnings; output hashes matched report. |
| validation | `f42b04d6...9e2` | equal canonical; revised config `516c3cbd...5edb`; current manifest `72f7e19d...13cc`; attempts 1-4 archived | `<root>/runs/validation`; `validation_%j.out/.err` | preparation/baseline attempt 1 complete | base `0b50975`; revised manifest `72f7e19d...13cc` | prior attempts `24488350`/`24488401`/`24488434`/`24488468`; revised `24488737` | prior attempts `FAILED 1:0`; revised `COMPLETED 0:0` | 38 s; batch MaxRSS 5,844,724 KiB; chunk replay/flexible batches/12 metric rows passed; no active job. |

`<root>` is the approved Iter005 output root.

## Independent Read-Only Review

- Reviewer: `/root/iter005_review` (different read-only agent)
- First reviewed source hash: `9d37e18d433c25db34b67f96956ea6580b407bb500da9116dd81ca0a00ab583a`
- First outcome: `block`
- Findings: smoke fitting mixed the 20 validation members into training; preparation validation did
  not independently enforce exact split/layout/schema/handoff provenance; final validation bypassed
  the public artifact inference interface and did not compare artifact preprocessing metadata.
- Primary-agent response: separated 80-member fit from 20-member inference; independently enforced
  exact member/offset/feature/manifest/handoff contracts and reconstructed source rows; exercised
  public flexible-batch/reload inference and exact artifact/prepared scaler/schema equality; added
  a history-aware forcing-window interface and synthetic check. Regenerated source manifest
  `62de2e48...216e` and submitted copies.
- Re-review outcome: `pass` with no concerns at `2026-10-31T16:45:32-07:00`; complete manifest,
  shell/resource, prior-finding resolution, and canonical/submitted equality checks passed.

## Execution and Diagnostics

- Initialization: approved report, repository scaffold, and exact external run directories created;
  phase advanced to `preparing`.
- Static validation: `bash -n` for all four Slurm scripts, locked JSON assertions, complete
  `sha256sum -c` source manifest, canonical/submitted equality and `git diff --check` passed.
- Preflight: completed inside preparation job `24485863`; input, split, schema, resource, and
  no-training checks passed before materialization.
- Exact submission material and commands were preserved under each external run attempt; canonical
  and submitted scripts/configurations matched their recorded source manifests.
- Submission: `/usr/bin/sbatch --parsable --export=ALL,ITER005_ATTEMPT=1,ITER005_CONFIG_SHA256=185dbc6a...,ITER005_EXECUTION_MANIFEST_SHA256=62de2e48... ./submit_prepare_iter005.slurm` from the approved prepare run directory returned `24485863`.
- Job identity checks: `squeue` and `scontrol show job 24485863` matched job name, account,
  partition, script, working directory, 4 CPUs, derived 20 GB memory, and 4-hour limit.
- Queue and terminal accounting: preparation `24485863` terminal `COMPLETED 0:0`, elapsed 3:55,
  TotalCPU 2:05.263, 4 CPUs, batch MaxRSS 18,622,640 KiB, ReqMem 20 GB, node `r4u03n2`.
- Smoke `24485909` terminal `COMPLETED 0:0`, elapsed 28 s, TotalCPU 5.712 s, 4 CPUs,
  batch MaxRSS 619,556 KiB, ReqMem 20 GB, node `r3u03n2`.
- Baseline `24485952` terminal `COMPLETED 0:0`, elapsed 1:34:30, TotalCPU 1:32:40,
  40 derived CPUs, batch MaxRSS 32,771,276 KiB, ReqMem 200 GB, node `r3u09n2`.
- Validation attempt 1 `24488350` terminal `FAILED 1:0`, elapsed 23 s, TotalCPU 4.197 s,
  8 CPUs, batch MaxRSS 857,752 KiB, ReqMem 40 GB, node `r7u11n2`. Classified as a bounded
  non-scientific inference-interface correction: public scaling retained float64 while the frozen
  estimator fit/prediction path used float32. No baseline artifact changed.
- Correction material: `predict_artifact` now restores the trained float32 design at the estimator
  boundary without changing raw scaling, tolerance, artifact, model, features, split, resources,
  gates, or metrics; regenerated source manifest is
  `d8e887f96b213dae33bc591dba22f7560d515ccebbd51c628439c6b0746887d8`.
- Correction re-review: `/root/iter005_review` returned `pass` with no concerns; full manifest,
  submitted-copy equality, unchanged frozen artifact/scalers/model/config/split/gates/resources, and
  exact attempt-1 failure classification were verified. Attempt 2 is contract-authorized.
- Validation attempt 2 `24488401` terminal `FAILED 1:0`, elapsed 14 s, TotalCPU 3.994 s,
  8 CPUs, batch MaxRSS 212,900 KiB, ReqMem 40 GB, node `r7u11n2`; it reached the same unchanged
  reload-equivalence gate. Classification: the first correction still differed from sklearn's
  in-place float32 subtraction/division sequence, while the validator supplied a lossy inverse of
  rounded standardized values rather than immutable source rows. The second bounded correction
  reproduces the exact scaler operation sequence and independently rebuilds sampled raw forcing,
  parameters, surface properties, and predicted-C/N from locked sources; tolerance remains `1e-6`.
- Second-correction source manifest:
  `be1820b978bc698ab8b82d1000766639be2cc03ed275ab9bf4470f5f00e02bcb`; complete hash check and
  submitted-manifest refresh passed. `/root/iter005_review` returned `pass` with no concerns after
  checking exact scaler semantics, independent source-row reconstruction, unchanged gate/contract,
  and canonical/submitted equality. Attempt 3 is contract-authorized.
- Validation attempt 3 `24488434` terminal `FAILED 1:0`, elapsed 15 s, TotalCPU 5.342 s,
  8 CPUs, batch MaxRSS 1,060,788 KiB, ReqMem 40 GB, node `r7u11n2`; it reached the same unchanged
  reload gate. Classification: independently summed rolling features are semantically valid but not
  bit-identical to the production cumulative-sum engine, which is material at a `1e-6` prediction
  gate. The final bounded validator correction uses the production `engineer_forcing` interface for
  reload equivalence, retains the separate preparation-stage independent semantic reconstruction,
  requires exact equality to sampled stored scaled rows, separately checks direct artifact reload,
  and writes reload diagnostics before assertions. No tolerance or scientific term changes.
- Final-retry source manifest:
  `34a38d27d03f9b1e39ded8e6cd2600858cefa3ae5975496c3e2628bc833e644a`; complete hash check and
  submitted-manifest refresh passed. `/root/iter005_review` returned `pass` with no concerns after
  verifying failure classification, production-vs-independent feature-check separation, diagnostic
  preservation, unchanged contract, and submitted equality. Attempt 4 is the final authorized
  additional submission.
- Validation attempt 4 `24488468` terminal `FAILED 1:0`, elapsed 26 s, TotalCPU 5.221 s,
  8 CPUs, batch MaxRSS 1,706,156 KiB, ReqMem 40 GB, node `r7u14n1`. Preserved diagnostic at
  `<root>/runs/validation/attempt_4/reload_diagnostics.json`: direct frozen-model prediction on the
  eight identical stored scaled rows differed from stored 250,000-row-chunk predictions by max
  `4.00543212890625e-05`; public source-row inference differed by max `2.6702880859375e-05`; scaled
  source rows differed by max `1.7881393432617188e-06`. This demonstrates float32 batch-shape/GEMM
  roundoff against the locked `1e-6` equivalence gate. The gate failed before metric recomputation,
  no baseline artifact was accepted, and all three additional submissions are consumed.
- Revised validation `24488737` terminal `COMPLETED 0:0`, elapsed 38 s, TotalCPU 15.485 s,
  8 CPUs, batch MaxRSS 5,844,724 KiB, ReqMem 40 GB, node `r4u11n1`. Original-chunk replay covered
  692,160 rows across three chunks and passed unchanged `1e-6` tolerance with max absolute
  difference `3.812002717040741e-06`; public batches 1/7/1,000 were finite and exactly repeatable
  within batch; cross-batch max difference `3.337860107421875e-06` was characterization only; all
  12 metric rows were independently recomputed and matched. Validation report SHA-256
  `a8c6ad33...4d8a`, reload diagnostics `a7c06f84...ea7d`, recomputed metrics `26787443...0189`.
- Resource diagnostics: current Puma capacity adequate; approximately 12 TB free on `/xdisk`.
- Failure, rejection, retry, or cancellation evidence: initial sandboxed external-directory creation
  was denied before any directory was created there; the exact approved mkdir was rerun outside the
  sandbox successfully. This is an agent filesystem-control event, not a workload attempt.

## Validation, Evaluation, and Decision

### User-approved batch-aware validation revision

- Approval: user response `Ok, revised contract and additional submission permitted.`
- Preserve `rtol=atol=1e-6` for fresh-process replay of the original 250,000-row prediction chunk
  boundaries; replayed chunk predictions must pass the unchanged tolerance against stored output.
- For public inference batches 1, 7, and 1,000, require finite predictions and exact repeatability
  for repeated calls with the same batch. Cross-batch float32 differences are characterized and
  reported, not treated as reload failures.
- Preserve independent preparation-stage feature semantics and source reconstruction; final reload
  uses the production feature interface and reports source-to-prepared and cross-batch differences.
- No change to model/artifact, data, upstream mode, feature schema, split, target, clipping policy,
  scientific metrics, resources, or interpretation.
- Authority: revise validator/configuration, preserve attempts 1-4 submitted material, obtain
  independent read-only review, and make one additional validation submission at 8 CPUs, 40 GB,
  and 4 hours with job-scoped monitoring/accounting. No further retry is authorized.
- Revised config SHA-256: `516c3cbd...5edb`; corrected source manifest SHA-256:
  `72f7e19df389396a08062f5bc3eb2cf884a9103dd634c8d1e13c2a625baa13cc`.
- First revision review outcome: `block`; required writing flexible-batch/per-chunk diagnostics
  before assertions, exact float64 target inverse scaling during replay, and explicit preservation
  of attempts 1-3 submitted manifests. All three findings were corrected; exact reconstructed
  attempts 1/2/3 manifest hashes are `62de2e48...216e`, `d8e887f9...87d8`, and
  `be1820b9...2bcb`; attempt-4 config/manifest were already archived.
- Corrected revision re-review: `/root/iter005_review` returned `pass` with no concerns; diagnostic
  ordering, exact replay arithmetic, unchanged tolerance, complete prior-submission preservation,
  12-row metric path, and current canonical/submitted equality all passed.

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| prepare | yes | prepared manifest `acd9a7bb...416b`; validation `fbb6f181...b9e4` | pass | Exact cache identity/layout/hash/source-row gates passed. |
| smoke | yes | report `58799d42...836f`; job `24485909` | pass | Separate 80-member fit/20-member inference passed. |
| baseline | yes | artifact `09820737...c31b`; predictions `74b2b133...4024`; metrics `5b7a40bf...172d` | pass | Complete outputs passed revised independent validation; user froze this baseline for robustness. |
| validation | yes | revised job `24488737`; report `a8c6ad33...4d8a`; diagnostics `a7c06f84...ea7d` | pass | Original-chunk reload, flexible batches, and all 12 metric rows passed revised immutable gates. |

- Overall acceptance result: `pass` under the user-approved batch-aware validation contract.
- Overall decision and closeout conclusion: `freeze_baseline`. Carry the fixed configuration into
  Iter006 robustness; reconsider configuration optimization only if robustness evidence is poor.
- Limitations: fixed upstream C/N is in-sample for all 819 development members; two sites; one GPP
  split; temporary unbacked storage; no fixed-test, robustness, release, SR, or full-chain evidence.
- Campaign-plan amendment recommendation: `none`.
- Next action: close the records and make the authorized one no-push closeout commit.

## Proposed Next-Iteration Plan (Planning Only)

### Iter006 - ABBY/JERC fixed-upstream GPP robustness

- Proposed sequential ID and work type: `iter006` / `experiment`.
- Campaign alignment: progression item 5 under locked `PLAN.md` SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`, with the same scoped
  deviation: use the published all-819 predicted-C/N handoff on both sides and label evidence
  `fixed_upstream_gpp_stage`, not end-to-end held out. No campaign-plan amendment is proposed.
- Objective: characterize the frozen Iter005 43-feature, hourly-trained `(128,)` ReLU/Adam GPP
  configuration on 20 fresh synchronized 655/164 development-member splits before deciding whether
  configuration optimization is needed.
- Inputs: immutable snapshot `r0001`, exact 819-development/205-fixed-test split, Iter004
  `release_0001` predicted-C/N handoff, and validated Iter005 interfaces/cache. Each repetition must
  fit feature/target scalers and optimizer stopping state from its 655 training members only; the
  remaining 164 members are inference-only. Fixed-test members remain forbidden.
- Proposed work units: bounded preflight and split/cache validation; separate smoke; throttled
  20-repetition robustness array; deterministic aggregation; independent validation; concise
  closeout records. Preserve full repetition metrics, convergence warnings, coverage/gaps, and
  declared quantiles for hourly and same-artifact complete-day metrics by site and pooled.
- Frozen terms: feature order and history semantics, physical GPP target and units, no clipping,
  model configuration and seed policy, fixed-upstream interpretation, batch-aware inference
  contract, and evaluation definitions. Daily metrics remain derived from hourly predictions; no
  daily model is trained.
- Decision rule: retain the frozen configuration if repeated-split performance and stability are
  acceptable; otherwise conclude `optimization_required` and plan a later configuration screen.
  Iter006 itself performs no configuration search and creates no all-819 GPP release.
- Exclusions: no spinup refit/execution, fixed-test access, feature selection, GPP configuration
  optimization, all-819 GPP fit/release, SR surrogate, full-chain robustness, observations,
  likelihood, MCMC, campaign-plan edit, or push.
- Kickoff requirements: recover current records; lock exact split seeds, output root, array
  throttle, resources and time limits using Iter005's observed memory/runtime as evidence; declare
  retry/cancellation bounds and monitoring; obtain independent read-only review and fresh
  consolidated user approval before initialization, repository Python, directory creation, or
  scheduler action.
- Stop condition: planning only. This proposal grants no runtime, scheduler, retry, directory,
  commit, or execution authority.

## Four-Record Closeout Validation

- Validator: `development/three_stage_surrogate/slurm/iter005/validate_closeout_iter005.sh`.
- Command: `bash development/three_stage_surrogate/slurm/iter005/validate_closeout_iter005.sh
  --active-job-count 0`.
- Result: `pass`.
- Output: `ITER005_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass
  decision=freeze_baseline active_jobs=0`.
- Staged closeout checks passed for all records and scripts. `model_ELM/three_stage_gpp.py`
  intentionally retains its runtime terminal blank line so its byte hash remains
  `e5ae810c...6ba3` and the execution manifest continues to validate; that exact-provenance byte is
  the sole `git diff --cached --check` whitespace diagnostic.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter005/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified no-push commit
