# iter011 - Sequential DROP32 correlation filtering

## Status

- Iteration ID: `iter011`
- Run slug: `spinup_surrogate_iter011_<variant>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-27 America/Phoenix`
- Closed: `2026-07-28 America/Phoenix`

## Runtime Contract

The user replied: `approved with one modification: use 15 min for run time`.

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One finite two-variant, 100-seed matrix (200 leaves), bounded no-training preflight, aggregation, gate evaluation, records, handoff validation, and closeout. Stop after validated closeout; stop for a second preflight failure, changed preflight failure class, scientific-control change, or application/code/configuration failure after training begins. |
| HPC confirmed | Yes: UA Puma login host `wentletrap.hpc.arizona.edu`, using `development/hpc/puma.md`. |
| Submission/monitoring authority | Authorized preparation, execution-affecting scaffolding, static validation, independent read-only review, bounded preflight, production submission, continuous monitoring, terminal accounting, failure classification, aggregation, gate evaluation, records, and closeout. |
| Resource policy and caps | `standard` / `chopinsong`; one node/task, 10 CPUs (about 50 GB implied), 15 minutes per production or aggregation job, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread BLAS/OpenMP, and per-task cache isolation. Preflight: 1 CPU / 5 minutes. |
| Retry and cancellation policy | One minimal pre-training validation-only import/launch/configuration correction and rerun; separately, one retry per failed leaf only for scheduler/resource interruption within the same resource caps. Emergency cancellation is authorized only for a proven universal pre-training defect. Application/code/configuration failures after training begins and scientific-control changes stop for fresh authorization. |
| Closeout commit authority | Authorized: at most one closeout commit after the handoff validator passes. |

## Context and Objective

- Historical retained baseline: Iter009 `s32_tanh_lbfgs_a50_lr1e3_full45`.
- Prospective Iter011 control: rerun Iter010 alpha-40 DROP32, whose Iter010 warning fractions were
  `0.25 / 0.24` for `TOTSOMC / TOTSOMN`.
- Hypothesis: after the domain-driven DROP32 restriction, global pre-split, priority-aware
  correlation filtering at `0.80` can produce a stable smaller schema without materially
  worsening paired validation performance or importance evidence.
- Objective: compare a strict DROP32 control with a candidate that first restricts the universe
  to DROP32 and then applies the global pre-split correlation filter.

## Fixed Controls and Variant Matrix

- Cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL; all
  `ppe6_I20TRCNPRDCTCBC`.
- Split / targets: `by_member`, fraction `0.8`, `TOTSOMC,TOTSOMN`.
- Seeds: `10001-10100` (exactly 100 per variant).
- Model: `(32,), tanh, lbfgs`, alpha `40`, learning rate `1e-3`
  (provenance-only for fixed-parameter LBFGS).
- Importance: 8 validation permutation repeats per seed and target.
- Worker controls: `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread numerical libraries,
  task-local `XDG_CACHE_HOME`.
- DROP32: all 14 parameters, three surface fields, and compact climatology features from
  `PRECTmms,FSDS,TBOT,RH`; no `FLDS_*`, `WIND_*`, or `PSRF_*`.
- Locked manifest:
  `development/spinup_surrogate/slurm/iter011/iter011_variants.tsv`.

| Variant | Change from control | Expected output path |
| --- | --- | --- |
| `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf` | Strict 32-feature control; no correlation pruning | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf/` |
| `s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop` | Restrict to DROP32, then apply global pre-split priority-aware correlation filtering at `0.80` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop/` |

## Decision and Retry Rules

- Required eligibility: both variants must have exactly 100 validated seed results. Do not
  aggregate or select from an incomplete matrix.
- Gates are applied independently to `TOTSOMC` and `TOTSOMN`, candidate against the Iter011
  control:
  - candidate median validation R2 delta must be `>= -0.01`;
  - candidate minimum validation R2 delta must be `>= -0.02`;
  - candidate validation R2 IQR delta must be `<= +0.02`;
  - candidate median per-seed RMSE-ratio delta must be `<= +0.02`;
  - candidate warning fraction must be `<= 0.25`;
  - exact identity, model, seed, input-universe, selected-schema, and finite 8-repeat importance
    validation must pass.
- Candidate schema gate: every selected feature must be in DROP32; all 100 schemas must be
  identical; the selected count must be less than 32; no `FLDS_*`, `WIND_*`, or `PSRF_*` may
  appear.
- Importance evidence gate: report per-target and combined rankings and paired control/candidate
  importance changes. This is an evidence requirement, not an automatic numeric rejection unless
  an exactness or finiteness invariant fails.
- Target combination: the candidate passes only if every gate passes for both targets.
- Ranking and tie-breaker: a full-gate-passing candidate is preferred because it has the smaller
  locked schema. Otherwise retain the Iter011 DROP32 control for the prospective comparison.
  Neither outcome retroactively changes the historical Iter009 retained baseline.
- Scientific rejection: a completed candidate failing any gate is rejected; preserve both arms'
  evidence and continue to closeout.
- Retry boundary: one retry per failed leaf only for scheduler/resource interruption within the
  approved caps. Do not invent retry groups. Wait for all terminal states and diagnose every
  failure before deciding whether failed-only retry is safe.
- One separate validation-only correction/rerun is allowed before training. A second preflight
  failure, changed failure class, application/code/configuration failure after training begins,
  or scientific-control change stops for fresh authorization.

## Expected Artifacts

- Canonical and variant-local submission scripts/configurations with hashes.
- Bounded preflight logs and reviewer evidence.
- Exactly 200 seed stats JSON files with exact result identity.
- Two summary JSON, two feature-stability JSON, two 100-seed importance JSON, one combined
  paired-analysis/gate-decision JSON, and universal R2/RMSE and importance plots.
- Terminal accounting and resource evidence for every submitted job.
- Updated `ITERATION_SUMMARY.md`, `registry.csv`, and `handoff/CURRENT.md`, followed by the
  four-record handoff validator.

## Provenance and Job Ledger

| Variant | Canonical script and SHA-256 | Variant-local submitted copy/config and SHA-256 | Variant-local log paths | Commit | Dirty diff/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf` | `slurm/iter011/case.train_surrogate_spinup_iter011.slurm`; `10ad8017f8987ecd9fb233a19d69aa1f76c186197825bb432a2057556b0bd0c4` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf/submit_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf.slurm`; same script hash; `submission_config.env`; `6ef15d6648f4024f8268ba6282e50c6c3d28e17e79c58a639fe417f29647730a` | same run directory: `spinup_iter011_%A_%a.out/.err` | `2346b46f8987ce9e30df50372655deaba1b5ba33` | `slurm/iter011/iter011_source_manifest.sha256`; manifest hash `43a5c616b6a99967260dc866c826384e591a9c22f375a43599202f01e997af17` | `23432904_1` (seed gate); `23432937_[2-100]` | 100/100 `COMPLETED 0:0` | no retry used |
| `s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop` | `slurm/iter011/case.train_surrogate_spinup_iter011.slurm`; `10ad8017f8987ecd9fb233a19d69aa1f76c186197825bb432a2057556b0bd0c4` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop/submit_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop.slurm`; same script hash; `submission_config.env`; `82bdab9059f3d196efe127f89d6371eee4b838f31f3a1928c6a355a9d6e50490` | same run directory: `spinup_iter011_%A_%a.out/.err` | `2346b46f8987ce9e30df50372655deaba1b5ba33` | `slurm/iter011/iter011_source_manifest.sha256`; manifest hash `43a5c616b6a99967260dc866c826384e591a9c22f375a43599202f01e997af17` | `23432938_[1-100]` | 100/100 `COMPLETED 0:0` | no retry used |

## Independent Read-Only Review

- Reviewer: independent read-only subagent `/root/iter011_readonly_review`.
- Reviewed source hash:
  `43a5c616b6a99967260dc866c826384e591a9c22f375a43599202f01e997af17`.
- Outcome: `pass_with_concerns`.
- Findings: every source-manifest entry matched; the contract, 15/15/5-minute limits,
  two variants/200 leaves, DROP32-first global-pre-split filter ordering, seeds/repeats/resources,
  exact validation, paired gates, paths, lifecycle boundaries, Slurm formatting, materialized
  byte equality, config hashes, and forbidden-feature exclusion passed. No blocking defect was
  found.
- Concern and primary-agent response: the report originally described paired-analysis and
  gate-decision JSONs separately, while the implementation intentionally writes one
  `iter011_paired_gate_analysis.json`. The report now explicitly treats that combined file as
  both artifacts. This is a records-only clarification and does not change reviewed execution
  source. Proceeding is justified because computation and gate enforcement were already aligned.

## Execution and Diagnostics

- Static validation: `bash -n` passed all Iter011 shell/Slurm scripts; Python compilation passed
  for all Iter011 Python and generic plotting/importance tools using a temporary bytecode root;
  the TSV shape check found exactly two seven-field rows; `git diff --check` passed; all source
  manifest entries passed `sha256sum -c`; both submitted copies matched the canonical script.
- Preflight submission: `sbatch --parsable
  development/spinup_surrogate/slurm/iter011/validate_iter011.slurm` returned job `23432877`;
  submitted from repository root on `2026-07-27 America/Phoenix`. Identity check confirmed
  `spinup_iter011_validate`, `standard/chopinsong`, 1 CPU, 5-minute limit, repository work
  directory, exact validator script, and expected stdout/stderr paths.
- Preflight terminal accounting: `23432877` completed `0:0` in `00:00:35`, `TotalCPU
  00:05.749`, `MaxRSS 258416K`, allocation `cpu=1,mem=5G,node=1`. It cleared `squeue`.
  Stdout reported `global feature-filter invariants passed` and `Iter011 manifest, submitted
  artifacts, and sequential DROP32-filter invariants passed`. Stderr contained only a
  non-fatal upstream ArviZ future warning. No validation-only retry was used.
- One-seed production gate submission: from the control run directory,
  `sbatch --parsable --array=1 --export=ALL,SUBMISSION_CONFIG=<control
  run_dir>/submission_config.env ./submit_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf.slurm
  </dev/null` returned `23432904`. This is control seed `10001` and counts as one of the 200
  locked leaves. Immediate `squeue`/`scontrol` identity checks confirmed task `1`, job name,
  `standard/chopinsong`, 10 CPUs/50 GB, 15-minute limit, exact control run directory,
  relative submitted script, `/dev/null` stdin, and variant-local stdout/stderr. The configured
  script fails closed unless the exported config is the exact colocated path.
- One-seed production gate terminal evidence: `23432904_1` completed `0:0` in `00:01:35`,
  `TotalCPU 01:05.660`, `MaxRSS 37681356K`, allocation `cpu=10,mem=50G,node=1`, and cleared
  `squeue`. Provenance printed the exact variant, seed `10001`, config hash `6ef15d66...`,
  canonical hash `10ad8017...`, and commit `2346b46...`. The exact stats file was written with
  32 selected control features, both targets, and 8-repeat importance. One expected scientific
  overfit warning occurred for `TOTSOMC`; no application/configuration failure occurred.
- Control remainder submission: from the control run directory, the same exact submission shape
  with `--array=2-100` returned parent job `23432937` for seeds `10002-10100`.
  Expanded `squeue` showed exactly tasks `2-100`; representative `scontrol 23432937_2`
  confirmed `standard/chopinsong`, 10 CPUs/50 GB, 15 minutes, exact control run directory,
  submitted relative script, `/dev/null` stdin, and variant-local logs.
- Candidate submission: from the candidate run directory, the same exact submission shape with
  `--array=1-100` returned parent job `23432938` for seeds `10001-10100`.
  The first expanded `squeue` identity query stalled and a bounded same-scope retry timed out
  after 15 seconds, so full queue state was held unknown rather than classified. Read-only
  `scontrol 23432938_1` then succeeded and confirmed `standard/chopinsong`, task 1, 10 CPUs/
  50 GB, 15 minutes, exact candidate run directory, submitted relative script, `/dev/null`
  stdin, and variant-local logs.
- Scheduler-query reconciliation: the next expanded parent-scoped queries succeeded. Control
  `23432937` showed exactly tasks `2-100`, with tasks `2-11` running and `12-100` pending;
  candidate `23432938` showed exactly tasks `1-100`, all pending for priority. This resolves the
  earlier unknown interval without evidence of a workload failure.
- Exact production submission commands were run from each validated variant directory:
  `sbatch --parsable --array=2-100 --export=ALL,SUBMISSION_CONFIG=<control
  run_dir>/submission_config.env ./submit_s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf.slurm
  </dev/null` and `sbatch --parsable --array=1-100
  --export=ALL,SUBMISSION_CONFIG=<candidate run_dir>/submission_config.env
  ./submit_s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop.slurm </dev/null`.
- Production terminal accounting: direct parent and leaf `sacct` checks accounted for all
  `23432904_1`, `23432937_[2-100]`, and `23432938_[1-100]` leaves. Every one of the 200 unique
  leaves completed `0:0`; both parent-scoped queues cleared; exact filesystem validation found
  one JSON for every seed `10001-10100` in each arm. No retry was used. Temporary read-only Slurm
  connection failures were kept unknown and boundedly retried; later direct elevated-context
  queries reconciled the complete arrays.
- Production resources: elapsed time ranged from about `00:01:05` to `00:01:54`, with 10 CPUs
  and 50 GB requested per leaf. MaxRSS was usually about `3731xxxxK`; the observed maximum was
  `52427916K`, immediately below the 50-GiB allocation. Every near-ceiling leaf completed, so no
  resource retry was indicated.
- Aggregation materialization: canonical
  `development/spinup_surrogate/slurm/iter011/aggregate_iter011.slurm` and submitted
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter011_aggregate/aggregate_iter011.slurm`
  were byte-identical at SHA-256
  `fec9764703d5b5f40fae1f12f6b822675314be3ef3eb0fd56595bb345ab71ad6`.
- Aggregation submission incident and correction: two calls made from the Codex filesystem
  sandbox did not create a job; queue and recent accounting queries proved that no duplicate
  `spinup_iter011_aggregate` existed. An in-sandbox `scontrol ping` also falsely reported the
  controller down. Per `development/hpc/puma.md`, the primary agent discarded that sandboxed
  diagnosis and resubmitted the immutable copy through the approved elevated Slurm context.
  `/usr/bin/sbatch --parsable ./aggregate_iter011.slurm` returned `23436731`.
- Aggregation identity and terminal evidence: `squeue`/`scontrol` confirmed job
  `23436731`, `standard/chopinsong`, 10 CPUs/50 GB, 15 minutes, exact aggregate run directory,
  relative submitted script, `/dev/null` stdin, and expected shared-output logs. It completed
  `0:0` in `00:00:23`, `TotalCPU 00:08.189`, `MaxRSS 2246988K`. Stdout reported exact seed,
  metadata, input-universe, schema, metric, and finite 8-repeat importance validation passed,
  then wrote all 15 expected summary/decision/plot artifacts. Stderr was empty.
- Failure classification: no production or aggregation workload failed. The correlation-0.80
  candidate is a completed scientific rejection under the predeclared gates, not an execution
  failure.

## Results and Decision

| Variant | Eligible | Key metrics | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf` | yes; 100 exact seeds, stable 32-feature schema | TOTSOMC/TOTSOMN median R2 `0.827271 / 0.827497`; minimum R2 `0.699599 / 0.699270`; R2 IQR `0.090059 / 0.090807`; median validation RMSE `4150.32 / 415.26`; median RMSE ratio `0.893196 / 0.893928`; warning fraction `0.25 / 0.24` | control/reference; warning fractions satisfy inclusive `<=0.25` rule | Retain as the prospective Iter011 control because the smaller candidate fails performance gates. |
| `s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop` | yes; 100 exact seeds, stable 21-feature schema, DROP32 subset, forbidden families absent | TOTSOMC/TOTSOMN median R2 `0.801217 / 0.801178`; minimum R2 `0.671361 / 0.672209`; R2 IQR `0.102057 / 0.102155`; median validation RMSE `4478.95 / 448.79`; median RMSE ratio `0.921297 / 0.921987`; warning fraction `0.22 / 0.23` | reject: median-R2 deltas `-0.026054 / -0.026319`, minimum-R2 deltas `-0.028238 / -0.027061`, and median-RMSE-ratio deltas `+0.028101 / +0.028060` fail both targets; IQR deltas `+0.011998 / +0.011348`, warning, schema, exactness, and importance gates pass | The stable 21-feature reduction is too aggressive: it loses materially more R2 and worsens median RMSE ratio beyond the locked allowances. |

- Paired validation R2 medians were lower for the candidate by `-0.021609 / -0.021161`;
  median absolute validation RMSE increased by about `239.70 / 23.16`.
- Importance evidence remained finite and complete. Both arms ranked `parm_6` and `parm_13`
  first and second across targets. The candidate elevated `RH_clim_seasonal_amp` and
  `FSDS_clim_mean` after pruning, but importance redistribution did not offset the locked
  performance failures.
- Selected prospective Iter011 result:
  `s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf`.
- Historical retained baseline: Iter009 `s32_tanh_lbfgs_a50_lr1e3_full45`.
- Promotion decision: no Iter011 candidate promotion; the historical retained baseline is
  unchanged.
- Next action: use the planning-only Iter012 proposal below only after a fresh runtime contract.

## Proposed Next-Iteration Plan (Planning Only)

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

## Handoff Validation

- Validator:
  `development/spinup_surrogate/slurm/iter011/validate_iter011_handoff.py`;
  SHA-256 `703b76c546b3d509f04f3245efcbcdce98c5964a8d83a5d461e0deaa2aeb74a7`.
- External precondition: elevated `/usr/bin/squeue --me` showed only unrelated job `23436635`
  (`vscode`) and no Iter011 job, so the validator received
  `--active-iteration-job-count 0`.
- Command:
  `python development/spinup_surrogate/slurm/iter011/validate_iter011_handoff.py
  --active-iteration-job-count 0`.
- Records-only corrections from blocked validation attempts: the cumulative summary was given
  both exact variant slugs, `CURRENT.md` was given candidate absolute median R2 and warning
  headlines, and validator assertions were completed with explicit diagnostics. No scientific,
  result, execution, or decision value changed.
- Final output: `Iter011 four-record handoff validation passed: report, cumulative summary,
  registry, and CURRENT agree; 200 exact leaves, 15 summary artifacts, no active jobs, candidate
  rejected, historical Iter009 baseline retained, and the planning-only Iter012 plan matches
  verbatim.`

## Closeout Checklist

- [x] Locked artifacts and independent read-only review recorded
- [x] Compute-node preflight completed
- [x] Matrix terminal accounting and failure classification recorded
- [x] Exact validation, aggregation, paired analysis, plots, and gate decision completed
- [x] Summary/stability/importance artifacts populated under `summaries/iter011/`
- [x] `ITERATION_SUMMARY.md`, `registry.csv`, and `CURRENT.md` finalized
- [x] Four-record handoff validator passed
- [x] One authorized closeout commit contains this finalized state
