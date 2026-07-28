# iter010 - LBFGS warning-threshold bracket and 100-seed importance stability

## Status

- Iteration ID: `iter010`
- Run slug: `spinup_surrogate_iter010_<variant>`
- Status: `completed`
- Phase: `closed after complete matrix accounting, aggregation, and selection`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-24 America/Phoenix`
- Closed: `2026-07-24 America/Phoenix`

## Runtime Contract

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One finite 15-variant, 100-seed matrix (1,500 leaves), bounded no-training preflight, and aggregation. Stop after terminal accounting and closeout; stop for an application, code, or configuration failure. |
| HPC confirmed | Yes: UA Puma login host `junonia.hpc.arizona.edu`, using `development/hpc/puma.md`. |
| Submission/monitoring authority | User replied `approved` on 2026-07-24 after the request explicitly named artifact preparation, static validation, independent read-only review, preflight, submission, continuous monitoring through selection and closeout. |
| Resource policy and caps | `standard` / `chopinsong`; one node/task, 10 CPUs (about 50 GB implied), 30 minutes per production or aggregation job, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread BLAS/OpenMP, task-local cache. The preflight is 1 CPU / 5 minutes. |
| Retry policy | One minimal validation-only correction/rerun before training; one retry per leaf only for scheduler/resource interruption within the cap. Application/code/configuration failures stop for fresh authorization. |
| Closeout commit authority | Authorized: at most one closeout commit after complete records. |

## Context and Objective

- Retained baseline: iter009 selected `s32_tanh_lbfgs_a50_lr1e3_full45`, validation R2 `0.7935/0.7937`, absolute validation RMSE `4661.8/469.7`, RMSE ratio `0.9499/0.9561`, zero warnings.
- Hypothesis: the warning transition lies between alpha 35 (one warning seed per target under all policies) and alpha 50 (zero warnings). A 100-seed bracket determines whether lower regularization remains eligible and characterizes importance stability.
- Objective: compare the three iter009 full-gate passers across alpha `40`, `42.5`, `45`, `47.5`, and `50` control, while retaining 8-repeat validation permutation importance for every seed.

## Fixed Controls and Variant Matrix

- Cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL; all `ppe6_I20TRCNPRDCTCBC`.
- Split / targets: `by_member`, fraction `0.8`, `TOTSOMC,TOTSOMN`; seeds `10001-10100`.
- Model: `(32,), tanh, lbfgs`, learning rate `1e-3` (provenance-only in fixed-parameter LBFGS), `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, 8 permutation repeats, stats-only.
- Feature policies: strict full45; global pre-split 0.80 correlation priority-drop over full45; strict drop32 excluding all `FLDS_*`, `WIND_*`, and `PSRF_*`. Variance filtering remains disabled.
- Locked manifest: `development/spinup_surrogate/slurm/iter010/iter010_variants.tsv` (15 variants, 1,500 leaves).

| Variants | Expected output path |
| --- | --- |
| alpha 40, 42.5, 45, 47.5, 50 × `full45`, `corr080_prioritydrop`, `drop_flds_wind_psrf` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter010_<variant>/` |

## Decision and Retry Rules

- Eligibility: exactly 100 readable stats files for every variant, complete metadata validation, seed-invariant feature schema within each variant, and complete importance payloads for both targets.
- Gates independently per target against iter009 selected full45 alpha-50: median R2 no more than `0.01` below; minimum R2 no more than `0.02` below; R2 IQR no more than `0.02` above; median per-seed RMSE ratio no more than `0.02` above; zero warnings. Report absolute validation RMSE and every warning seed/reason.
- Rank full-gate passers by mean cross-target median validation R2, lower mean median RMSE ratio, then lower alpha. In ties, prefer full45 and then the simpler locked feature policy only when all preceding metrics tie.
- Importance records: for each variant and target, sort features by median seed-rank ascending and median RMSE increase descending; report rank spread and R2-drop diagnostics. A combined cross-target view follows the same ordering using the cross-target medians.
- Scientific rejection: complete variants that fail gates are rejected; independent variants continue. Do not aggregate or select from an incomplete matrix.

## Provenance and Job Ledger

| Item | Evidence |
| --- | --- |
| Canonical training script | `slurm/iter010/case.train_surrogate_spinup_iter010.slurm`; initial SHA-256 `86f72e33faa6efa3f2adb7c139a9946a521753593a4fc0cc8a68f47ead1a971f`; corrected SHA-256 `bbe48e2e7e5812284573f9670235bbff81ec2de7290de38ca3e062419e122189` |
| Locked manifest | `slurm/iter010/iter010_variants.tsv`; 15 locked variants; SHA-256 `18fec9c72d0b0446d81c73fcc792f29398c5cbf6b37a7277a3947f541cdf52bb` |
| Preflight | `slurm/iter010/validate_iter010.slurm` SHA-256 `118bf510743abf3b39afd1a4c6573fcf813f64061a4a5c63bd86d5db58213d9a`; validator `validate_iter010.py` SHA-256 `9a395478280e7f7edb2ea8dce7346f589c7d24f3fb270bf36a2a29bec068ebb7`; no training or case loading |
| Aggregation | `slurm/iter010/aggregate_iter010.slurm` SHA-256 `fe187990d2f2abe5f8bed5caf4cbc260b308013a48be8b0db5bc580ce3e39856`; result validator SHA-256 `63a4689ef9d43c7258777feaeaa67218c301f947e1bf7035ccb792edbe963ceb`; importance aggregator SHA-256 `9b3d69c835d5424b09941d9dfb94ea102d7328624a71a9a7e021d814a4627354` |
| Variant-local artifacts | Required per variant: `submit_<variant>.slurm`, `submission_config.env`, `slurm_%A_%a.out`, `slurm_%A_%a.err` directly at the variant root |
| Source state | `f1a8226` at kickoff; current dirty source manifest and exact hashes to be recorded before preflight/submission |

## Execution and Diagnostics

- Materialization created 15 variant-local roots, submitted-script copies, and seven-field configurations. Every submitted script has SHA-256 `86f72e33faa6efa3f2adb7c139a9946a521753593a4fc0cc8a68f47ead1a971f`; all configuration hashes were emitted by `materialize_iter010_variants.sh` and are retained beside their scripts.
- Independent reviewer: initial review **block** found incomplete importance-payload validation. Primary-agent correction added required 8 repeats, exact unique feature identity, input/selected schema equality, and finite importance metrics. Re-review **pass** (read-only) accepted result-validator SHA-256 `63a4689ef9d43c7258777feaeaa67218c301f947e1bf7035ccb792edbe963ceb`; no remaining static blocker.
- Preflight submission command: `/usr/bin/sbatch --parsable --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_validate_%j.out --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_validate_%j.err development/spinup_surrogate/slurm/iter010/validate_iter010.slurm`.
- Initial preflight job `23384231`: `FAILED`, exit `1:0`, elapsed `00:00:54`, MaxRSS `438688K`. The reusable global feature-filter invariant passed. Before any case loading or training, Iter010's synthetic validator raised `TypeError` because `_select_feature_columns` has keyword-only `n_params`, `n_surface`, `n_climatology`, and `feature_set` arguments.
- Classification: preflight validation failure, not scheduler/resource or scientific failure. Under the single authorized validation-only retry, change only `validate_iter010.py` to pass those four unchanged values by keyword. Corrected validator SHA-256 `026b71624b20f12a1dcaa3cfa92a5bddf0ea9ee494ffe247bfed7163f4d352e0`; independent read-only re-review **pass** confirmed the minimal correction and no other static block. This consumes the validation-only retry; any second validation failure stops for fresh authorization.
- Rerun submission command: `/usr/bin/sbatch --parsable --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_validate_rerun_%j.out --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter010_validate_rerun_%j.err development/spinup_surrogate/slurm/iter010/validate_iter010.slurm`.
- Corrected preflight rerun job `23384263` completed `0:0` in `00:00:39` (MaxRSS `266384K`) and confirmed both global invariants and the Iter010 manifest artifacts.
- Initial production array `23384275` (full45, alpha 40) failed before training for elements 1--50; elements 51--100 were cancelled under the user's explicit cancellation authorization. The defect was a Bash dependent-assignment error: `RUN_DIR` and `SUBMITTED_SCRIPT` were expanded before the same command assigned `RUN_NAME`, leaving an empty run-directory suffix and causing the early `pwd` guard to exit under `bash -e`. The canonical script now uses three sequential `readonly` assignments. Preserve this as a launch/configuration incident, not a scientific result.
- Diagnostic seed probe `23384385` confirmed the failure mechanism. After rematerializing submitted copies while preserving the failed `23384275` copies with a `.failed23384275` suffix, normal `bash -e` seed check `23384428_1` completed `0:0` in `00:02:09` (MaxRSS `49386472K`). This is the user-authorized success gate for the corrected matrix.
- Corrected production arrays accepted so far: `23384458` (alpha 40/full45), `23384459` (alpha 40/corr080), `23384461` (alpha 40/drop32), `23384503`--`23384507` (alpha 42.5 and alpha 45, except the corrected alpha-45/drop32 ID below), `23384510` (alpha 45/drop32; replacement for pending typo job `23384509`, cancelled before execution), `23384512` (alpha 47.5/full45), and `23384712` (alpha 47.5/corr080). The initial direct manifest-loop submission also failed to return accepted arrays because `sbatch` inherited the loop's manifest stdin; subsequent arrays use explicit submissions with returned job-ID and queue verification. Four variants remain deferred only by the user 1,000 submitted-task cap: alpha 47.5/drop32 and all alpha-50 policies.
- Corrected production terminal accounting: all 15 corrected arrays completed 100/100 leaves with exit `0:0` (1,500 valid leaves): `23384458`, `23384459`, `23384461`, `23384503`--`23384507`, `23384510`, `23384512`, `23384712`, `23385025`, `23385396`, `23385858`, and `23399185`. The original `23384275` is excluded as a launcher/configuration failure; `23387290` is excluded as a bad `SUBMISSION_CONFIG` path submission. No scheduler/resource retry was used.
- The final replacement `23399185` completed all 100 alpha-50/drop32 leaves `0:0`. A transient Slurm accounting-database connection error occurred after it cleared `squeue`; it was an external query-service failure, not a leaf failure. The aggregate validator subsequently proved the exact 1,500-file result set.
- Aggregate job `23399438` completed `0:0` in `00:00:43`. Its exact validator passed seed/run/model/schema/importance identity for all 1,500 files and wrote 45 artifacts (15 summary, 15 feature-stability, 15 100-seed importance JSON files) under `summaries/iter010/`.
- Submission incidents and durable prevention: (1) `23384275` used dependent Bash assignments in one command, expanding `RUN_DIR`/`SUBMITTED_SCRIPT` before `RUN_NAME` existed; use sequential assignments and a normal one-seed `bash -e` gate before a matrix. (2) the first manifest-loop submission let `sbatch` inherit the loop's manifest stdin, so accepted array IDs were not reliably captured; never submit from a manifest-fed loop unless `sbatch` receives an explicit independent stdin, and require a returned job ID plus `squeue` verification before recording a submission. (3) `23387290` had a hand-typed `SUBMISSION_CONFIG` path typo and all leaves failed before useful work; derive `--chdir`, logs, and `SUBMISSION_CONFIG` from one validated `run_dir`, test the config path immediately before submission, and verify the exported path for a representative accepted task. (4) premature agent handoffs occurred during live queue/array stages; the workflow completion condition is terminal accounting of the full corrected matrix, aggregation, gate decision, records, and closeout--never submission, a pending queue, or a partial completion.

### Complete Incident Ledger

This ledger records every error or operational anomaly encountered by the primary agent in this
round, including static-review, scheduler, submission, query, and documentation mistakes. None of
the excluded failed submissions contributes data to the scientific result.

| # | Incident | Impact and classification | Corrective/prevention rule |
| --- | --- | --- | --- |
| 1 | Independent reviewer initially blocked the result validator because it did not fully validate the importance payload. | Static execution-material defect; no compute submitted under the blocked artifact. | Add exact repeat count, feature identity/schema equality, and finite-metric checks; obtain a passing read-only re-review before preflight. |
| 2 | Preflight `23384231` raised `TypeError` by calling keyword-only `_select_feature_columns` arguments positionally. | Validation-only application/configuration failure before case loading or training. | Pass the unchanged arguments by keyword; use the one authorized validation-only rerun and stop on a second preflight failure. |
| 3 | Initial array `23384275` expanded dependent Bash assignments before `RUN_NAME` was set. | Launch/configuration failure before training for leaves 1--50; 51--100 were user-authorized cancellations. | Sequentialize dependent `readonly` assignments and require a normal `bash -e` one-seed gate after rematerialization. |
| 4 | The cancellation request waited for interactive approval for several hours; during that wait the targeted jobs continued running and had already completed. After approval, the local `scancel` wrapper also segfaulted/delayed. | Time-sensitive control-plane failure: approval latency made cancellation ineffective, and the wrapper behavior added a second control-plane anomaly. The jobs were not stopped by cancellation because they were already terminal. | The runtime contract must explicitly authorize in-scope cancellation of known launcher/configuration failures before submission, without a second per-command approval. Issue cancellation immediately, then reconcile `squeue` and `sacct`; if approval is pending, mark cancellation as ineffective-risk rather than assuming it will stop work. Prefer `/usr/bin/scancel` and record request/approval/execution timestamps. |
| 5 | The first manifest-fed submission loop let `sbatch` inherit its stdin, so accepted array IDs were not reliably captured. | Submission control-flow failure; no accepted matrix entry was inferred from the loop. | Give `sbatch` independent stdin or submit explicitly; require parsable returned ID and queue verification before ledger entry. |
| 6 | Deferred job `23384509` had an ID/variant submission typo and was cancelled before execution; `23384510` replaced it. | Pre-execution submission mistake; no scientific data lost. | Record exact variant-to-job mapping immediately and verify the rendered variant/config before dispatch. |
| 7 | Submission `23387290` used a hand-typed, nonexistent `SUBMISSION_CONFIG` path. | All leaves failed before useful work; excluded as configuration failure and replaced by `23399185`. | Derive `--chdir`, logs, and exported config path from one validated `run_dir`; test it before submission and inspect a representative accepted task environment. |
| 8 | Slurm accounting briefly returned persistent-connection/resource errors after `23399185`; one queue query also returned an empty transient response. | External scheduler-query anomaly only; no job failure. | Treat query transport failure as unknown state, retry read-only `squeue`/`sacct`, inspect logs, and rely on the aggregate exact validator before final accounting. |
| 9 | A compact `jq` metrics query accidentally changed context to the input filename and failed. | Read-only reporting-query error; no results or files changed. | Bind the filename separately and preserve the JSON object as query context; rerun before using extracted metrics. |
| 10 | Two broad documentation patches initially failed to apply because their expected context/patch syntax was stale or malformed. | Local documentation-edit error; no partial patch was applied. | Re-read the exact target context and apply smaller, verified patches. |
| 11 | The primary agent stopped/handoff occurred prematurely during live monitoring on multiple occasions. | Workflow-continuity failure that required user intervention; it did not change completed outputs. | Never terminate after submission, partial completion, or a pending queue. Remain active through full terminal accounting, aggregation, selection, records, and closeout; record platform-forced interruption state in `CURRENT.md` before any unavoidable suspension. |

## Results and Decision

All 15 variants have exactly 100 valid stats files and seed-invariant schemas: full45 has 45
features, corr080 has 25, and drop32 has 32. Values are `TOTSOMC / TOTSOMN` 100-seed medians.

| Alpha/policy | Validation R2 | Validation RMSE | RMSE ratio | Warnings | Decision |
| --- | --- | --- | --- | --- | --- |
| 40 full45 | 0.8310 / 0.8301 | 4090.9 / 410.8 | 0.9024 / 0.9078 | 0.24 / 0.24 | Reject: warning gate |
| 40 corr080 | 0.8297 / 0.8275 | 4123.9 / 414.8 | 0.8983 / 0.9002 | 0.24 / 0.24 | Reject: warning gate |
| 40 drop32 | 0.8273 / 0.8275 | 4150.3 / 415.3 | 0.8932 / 0.8939 | 0.25 / 0.24 | Reject: warning gate |
| 42.5 full45 | 0.8232 / 0.8233 | 4167.8 / 417.1 | 0.8993 / 0.9006 | 0.24 / 0.23 | Reject: warning gate |
| 42.5 corr080 | 0.8214 / 0.8218 | 4182.9 / 418.8 | 0.8917 / 0.8937 | 0.24 / 0.24 | Reject: warning gate |
| 42.5 drop32 | 0.8210 / 0.8214 | 4221.7 / 422.8 | 0.8922 / 0.8931 | 0.23 / 0.24 | Reject: warning gate |
| 45 full45 | 0.8162 / 0.8174 | 4258.0 / 426.4 | 0.8958 / 0.8966 | 0.23 / 0.23 | Reject: warning gate |
| 45 corr080 | 0.8146 / 0.8146 | 4268.1 / 429.9 | 0.8931 / 0.8975 | 0.23 / 0.23 | Reject: warning gate |
| 45 drop32 | 0.8146 / 0.8144 | 4282.6 / 428.8 | 0.8885 / 0.8895 | 0.22 / 0.22 | Reject: warning gate |
| 47.5 full45 | 0.8116 / 0.8109 | 4324.6 / 431.3 | 0.8949 / 0.8930 | 0.22 / 0.22 | Reject: warning gate |
| 47.5 corr080 | 0.8090 / 0.8093 | 4352.6 / 435.7 | 0.8940 / 0.8949 | 0.23 / 0.23 | Reject: warning gate |
| 47.5 drop32 | 0.8089 / 0.8090 | 4363.6 / 437.2 | 0.8910 / 0.8921 | 0.22 / 0.22 | Reject: warning gate |
| 50 full45 | 0.8060 / 0.8069 | 4387.3 / 439.3 | 0.8939 / 0.8947 | 0.22 / 0.22 | Reject: warning gate |
| 50 corr080 | 0.8062 / 0.8062 | 4383.1 / 439.2 | 0.8861 / 0.8870 | 0.22 / 0.22 | Reject: warning gate |
| 50 drop32 | 0.8040 / 0.8042 | 4430.5 / 443.6 | 0.8908 / 0.8918 | 0.22 / 0.22 | Reject: warning gate |

No candidate passes the locked zero-warning requirement, so no Iter010 model is promoted. Retain
the Iter009 selected `s32_tanh_lbfgs_a50_lr1e3_full45` as the current baseline. For alpha-40/full45
importance, both targets have the same stable top five: `parm_6`, `parm_13`, `parm_12`, `parm_9`,
and `parm_10`; the per-variant 100-seed importance JSON files retain ranks, spread, RMSE-increase,
and R2-drop diagnostics.

## Proposed Next-Iteration Plan (Planning Only)

A new runtime contract will be required before any Iter011 execution. Iter010 shows the apparent
alpha-35/50 transition from five seeds is not stable at 100 seeds: alpha 50 itself warned on 22%
of seeds. The Iter011 planning decision is prospective only: it changes neither the Iter010
result nor its zero-warning rejection.

- Sequential ID and control: `iter011` reruns
  `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf` as its 100-seed control. It becomes the
  reference for candidate eligibility deltas and ranking; it does not revise the historical
  Iter009 retained baseline or retroactively promote an Iter010 result.
- Hypothesis: after the domain-driven `DROP32` restriction, global pre-split, priority-aware
  correlation filtering at `0.80` can produce a stable smaller schema without materially
  worsening paired validation performance or importance evidence.
- Tentative matrix: the rerun control and one alpha-40 candidate that first locks `DROP32`, then
  applies the `0.80` correlation filter only within that 32-feature universe. The candidate must
  never reintroduce `FLDS_*`, `WIND_*`, or `PSRF_*`. Both variants use seeds `10001-10100`.
- Tentative prospective warning rule: require `overfit_warning_fraction <= 0.25` independently
  for `TOTSOMC` and `TOTSOMN`. Retain the existing per-target median-R2, minimum-R2, R2-IQR, and
  median-RMSE-ratio deltas against the Iter011 control unless the Iter011 report explicitly
  changes a value.
- Required evidence: exact 100-file identity/metadata validation; selected feature names and
  count for every seed; seed-paired validation R2/RMSE/RMSE-ratio deltas; train/test R2 and RMSE
  distributions; and 8-repeat permutation-importance rankings for both targets plus combined
  views. Generic plotting tools, rather than Iter010-hard-coded scripts, will produce the visual
  comparisons.
- Authorization boundary: planning artifacts may be prepared, but a fresh Iter011 runtime
  contract must authorize the Puma resources, no-training preflight, submission, monitoring,
  retry/cancellation limits, and any closeout commit.

## Closeout Checklist

- [x] Locked artifacts and independent read-only review recorded
- [x] Compute-node preflight completed
- [x] Matrix terminal accounting recorded
- [x] Summary, stability, and 100-seed importance artifacts copied to `summaries/iter010/`
- [x] `ITERATION_SUMMARY.md`, `registry.csv`, and `CURRENT.md` finalized
- [x] One authorized closeout commit created
