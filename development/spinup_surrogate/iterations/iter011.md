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
