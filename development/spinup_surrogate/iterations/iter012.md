# iter012 - Final spinup-surrogate release

## Status

- Iteration ID: `iter012`
- Run slug: `spinup_surrogate_iter012_<variant>`
- Status: `completed`
- Phase: `records and closeout validation`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-28 America/Phoenix`
- Closed: pending

## Runtime Contract

The user replied `approved` to the primary agent's consolidated Iter012 contract request.

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One finite four-job release: one bounded no-training preflight, one `drop32` release job, one `drop21_corr080` release job, then one cross-artifact validation job. Continue through terminal accounting, release-gate evaluation, records, handoff validation, and closeout. Stop for a second preflight failure, changed preflight failure class, any application/code/schema/numerical/artifact/scientific failure, a resource change beyond the caps, or completed closeout. |
| HPC confirmed | Yes: UA Puma login host `wentletrap.hpc.arizona.edu`, using `development/hpc/puma.md`. |
| Preparation/submission/monitoring authority | Authorized execution-affecting scaffolding, static validation, independent read-only review, bounded preflight, the locked release/validation submissions, continuous monitoring, terminal accounting, failure classification, release-gate evaluation, record updates, handoff validation, and closeout. |
| Outside-sandbox authority | Authorized bounded `sbatch` for the locked jobs and allowed resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits` throughout monitoring/accounting; and `scancel` only for recorded Iter012 job IDs under the cancellation rule below. |
| Resource policy and caps | Puma `standard` / `chopinsong`. Preflight: one task, 1 CPU (about 5 GB implied), 5 minutes. Each release and cross-artifact validation job: one task, 10 CPUs (about 50 GB implied), 15 minutes. `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread numerical libraries, and task-local cache. |
| Retry and cancellation policy | One minimal pre-training validation-only import/launch/configuration correction and rerun. Separately, one retry per failed job only for scheduler/resource interruption within the same caps. Do not retry application/code/schema/numerical/artifact/scientific failures. Emergency cancellation is limited to recorded Iter012 job IDs affected by a proven universal pre-training defect. |
| Closeout commit authority | Authorized: at most one Iter012 closeout commit after all release gates and four-record handoff validation pass. |

The native session goal is: execute Iter012 according to `development/spinup_surrogate/WORKFLOW.md`
through authorized scaffolding, independent review, bounded preflight, submission, continuous
monitoring, terminal accounting, failure classification, aggregation/release-gate evaluation,
record updates, handoff validation, and authorized closeout; do not stop before a recorded
workflow stop condition. The goal does not expand the runtime contract above.

### Fresh Recovery Authorization

After job `23445100` stopped at the application/schema target-metadata gate, the user replied
`approved` to this bounded recovery contract:

1. Run one no-fitting metadata diagnostic on Puma at 1 CPU, about 5 GB, and 5 minutes.
2. Inspect authoritative ELM definitions and the raw attributes, dimensions, and values for
   every `TOTSOMC`/`TOTSOMN` restart component across the nine reference restarts.
3. Make only an evidence-supported target-metadata audit correction. If the scalar definition or
   units remain ambiguous, stop without weakening the release gate.
4. Rerun static checks, independent read-only review, and the no-training preflight.
5. Retry `drop32` once at the unchanged 10-CPU/about-50-GB/15-minute cap.
6. Only if that retry passes, continue autonomously with `drop21_corr080`, cross-artifact
   validation, records, handoff validation, and the already authorized closeout commit.

This fresh authorization permits the diagnostic submission, a justified execution-material
correction, and one application/schema recovery retry of `drop32`; it does not authorize a
scientific-definition guess, relaxed unit gate, resource increase, or any other scope change.

### Standing OOM Recovery Authorization

While `drop21_corr080` job `23445296` was active, the user authorized the primary agent to
increase memory and rerun without further permission if another OOM occurs. This is interpreted
narrowly: a remaining Iter012 job must be terminally classified `OUT_OF_MEMORY`; the replacement
memory request must be evidence-based; only that failed job may be retried; and its CPU count,
walltime, code, data, scientific contract, and all non-OOM stop rules remain unchanged. Jobs that
do not OOM retain their locked 50-GB request.

### Standing Slurm Submission Authorization

While cross-artifact validation job `23445328` was active, the user approved the primary agent
to submit any jobs using `sbatch` without asking again and then left the session. This removes
per-command approval prompts for the remainder of the active Iter012 lifecycle; it does not
expand the scientific objective, allowed job purposes, retry/stop rules, resource controls
except the standing OOM exception above, cancellation scope, or closeout boundary. Every job
must still be materialized, mapped, identity-checked, monitored, accounted, and recorded.

## Context and Objective

- Historical retained scientific baseline: Iter009
  `s32_tanh_lbfgs_a50_lr1e3_full45`.
- Final release provenance: Iter011 compared alpha-40 DROP32 with DROP32 then correlation-0.80.
  The 32-feature arm is the recommended accuracy-oriented release. The stable 21-feature arm
  failed the locked median-R2, minimum-R2, and median-RMSE-ratio gates, but the user accepts it as
  a compact tradeoff release. Iter012 does not rerank or promote either arm scientifically.
- Objective: reproduce each Iter011 seed-`10001` validation fit exactly, then train the same
  frozen estimator on all 900 rows and publish two versioned, strictly validated,
  inference-ready spinup-surrogate artifacts with complete provenance and documentation.

## Fixed Controls and Release Matrix

- Ordered cases and spinup cases:
  `ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC`.
- Rows and targets: 100 members per case, 900 rows total; ordered outputs
  `TOTSOMC,TOTSOMN`.
- Feature construction: surface `PCT_SAND,PCT_CLAY,ORGANIC`; compact spinup-cycle climatology
  from `PRECTmms,FSDS,TBOT,RH`; exact frozen feature order per variant; variance and correlation
  filtering disabled during release.
- Model: one independent `MLPRegressor` per target; hidden layers `(32,)`, activation `tanh`,
  solver `lbfgs`, alpha `40`, `max_iter=800`, estimator seed `42`, provenance-only learning rate
  `1e-3`; separate X/Y `StandardScaler` objects per target.
- Reproduction gate: repeat Iter011 seed `10001`, `by_member`, train fraction `0.8`, exact split,
  cases, model, and feature order. Each recorded metric must agree with the Iter011 reference at
  `rtol=1e-10`, `atol=1e-8`.
- Full-data fit: only after reproduction passes, refit each scaler/model on all 900 rows. Full-fit
  diagnostics are not validation evidence; Iter011's 100-seed summaries remain the scientific
  performance/importance evidence.
- Locked manifest:
  `development/spinup_surrogate/slurm/iter012/iter012_releases.tsv`.

| Variant | Frozen feature count | Expected artifact |
| --- | ---: | --- |
| `drop32` | 32 | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl` |
| `drop21_corr080` | 21 | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` |

## Release Gates and Failure Rules

- Both release jobs must complete successfully; partial release is not eligible for closeout.
- Before full-data fitting, each variant must reproduce the Iter011 seed-`10001` metrics within
  the locked tolerance and preserve the exact split and feature order.
- Each artifact must have a supported release/schema version; exact ordered targets, physical
  parameters, parameter aliases/mapping, complete and selected feature orders; exact model and
  scaler keys; finite empirical ranges; parameter bounds; audited target definitions/units;
  package/source/configuration provenance; and full-data fit scope.
- Operational validation must pass fresh-process load, manifest size/hash equality,
  pre-save/post-load prediction agreement, correct single/batch shapes, finite predictions,
  identical named/positional parameter results, one real member from every training case, a
  multi-member ABBY batch, parameter-bound midpoint in named/positional forms, an empirical-range
  warning where constructible, and negative ordering/missing/extra/bounds/schema cases.
- Inference must reject missing, duplicate, extra, or misordered parameters/features and values
  outside `ensemble_pmin/pmax`; values inside declared bounds but outside empirical training
  ranges warn without blocking.
- The exact scalar aggregation and NetCDF metadata/units for `TOTSOMC` and `TOTSOMN` must be
  audited. Ambiguity is a release-blocking application/schema failure.
- The forcing bridge must validate order, shape, dtype, and design-matrix compatibility for
  `[engineered forcing | parameters | spinup]`. No forcing artifact is trained or real SR/flux
  prediction claimed.
- Application/code/schema/numerical/artifact/scientific failures stop for fresh authorization.
  Scheduler/resource interruptions may use one same-cap retry per failed job. The one separate
  validation-only correction/rerun applies only before training begins.

## Expected Artifacts

- Versioned spinup artifact binaries outside Git; colocated `artifact_manifest.json` and
  `validation_report.json`.
- Byte-identical tracked evidence copies of both JSON sidecars under
  `development/spinup_surrogate/summaries/iter012/`.
- Reusable release and inference code; canonical and variant-local Slurm material/configurations;
  hashes, logs, job mappings, accounting, and independent review evidence.
- Cross-artifact release decision JSON and forcing-bridge validation evidence.
- Updated `README.md`, `ITERATION_SUMMARY.md`, `registry.csv`, and `handoff/CURRENT.md`;
  four-record handoff-validator evidence; one authorized closeout commit.
- Pickle artifacts remain untracked. `/xdisk` is temporary and unbacked; backup remains the
  user's responsibility and is not a closeout gate.

## Provenance and Job Ledger

| Item | Canonical/submitted path and SHA-256 | Job ID | State | Notes |
| --- | --- | --- | --- | --- |
| no-training preflight | canonical `slurm/iter012/validate_iter012.slurm`; submitted `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_preflight/validate_iter012.slurm`; SHA-256 `1de6d4b1b7c6202d0e5ccd22044581890cab2d5fb7612c73dd4ec4028d4d96da` | `23445069` | `COMPLETED 0:0` | Submitted `2026-07-28 19:53 America/Phoenix`; 1 CPU / 5 minutes; completed in `00:00:25`, `TotalCPU 00:03.864`, batch MaxRSS `202660K`; no validation retry used |
| recovery no-training preflight | same canonical/submitted path and SHA; locked source-manifest SHA-256 `1225db62b484cce11ce8e633c9fe1c8e47b5095c1323f2687c9e4c6454335875` | `23445263` | `COMPLETED 0:0` | Submitted `2026-07-28 20:41 America/Phoenix`; 20 seconds, `TotalCPU 00:03.244`, batch MaxRSS `196872K`; all source and no-training gates passed |
| `drop32` release | canonical `slurm/iter012/case.release_spinup_iter012.slurm`; submitted `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/submit_drop32.slurm`; script SHA-256 `d9477729aaad5536fb7169cbbc3444cb6c33878f807d63b30231d0f2c73141e8`; config SHA-256 `f1dd92c0943dcfbd301017c42825be5ce388f2e675b3a0b4d7239368bc607938` | `23445100` | `FAILED 1:0` | Application/schema failure in target-metadata audit; no artifact or sidecar written; no retry authorized |
| `drop32` recovery retry | same script/config; corrected locked source-manifest SHA-256 `1225db62b484cce11ce8e633c9fe1c8e47b5095c1323f2687c9e4c6454335875` | `23445281` | `COMPLETED 0:0` | Submitted `2026-07-28 20:47 America/Phoenix`; 1:47, `TotalCPU 01:12.053`, batch MaxRSS `38612468K`; release gates passed |
| target-metadata diagnostic | submitted `slurm/iter012/diagnose_iter012_target_metadata.{py,slurm}` copies under `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_metadata_diagnostic/`; submitted Python SHA-256 `1b9400a07b2a954f50130d55494dab2df9a668a051b9eba6667bce3b6b543c0c`; Slurm SHA-256 `e7c76e90976cdd0edfaa82b7c2cd43cd091d894b09174efb9ae0966275290aad` | `23445192` | `OUT_OF_MEMORY 0:125` | Submitted `2026-07-28 20:18 America/Phoenix`; 29 seconds, batch MaxRSS `5242016K`; no JSON evidence written; same-cap resource retry eligible |
| target-metadata diagnostic retry | same submitted paths; corrected Python SHA-256 `2671724ebcf9e27d552425b9f0f3ff441ef638bec623ada062b1708519a4d65d`; unchanged Slurm SHA-256 `e7c76e90976cdd0edfaa82b7c2cd43cd091d894b09174efb9ae0966275290aad` | `23445233` | `COMPLETED 0:0` | Submitted `2026-07-28 20:31 America/Phoenix`; 10 seconds, `TotalCPU 00:00.682`, batch MaxRSS `30820K`; one same-cap resource retry consumed |
| `drop21_corr080` release | canonical/submitted `slurm/iter012/case.release_spinup_iter012.slurm` and `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/submit_drop21_corr080.slurm`; script SHA-256 `d9477729aaad5536fb7169cbbc3444cb6c33878f807d63b30231d0f2c73141e8`; config SHA-256 `5d30bdc30681db1128499dfea3311bde6b394fbb831fab320f735e21661c48dc` | `23445296` | `COMPLETED 0:0` | Submitted `2026-07-28 20:52 America/Phoenix`; 1:23, `TotalCPU 01:09.424`, batch MaxRSS `37314156K`; release gates passed |
| cross-artifact validation | canonical/submitted `slurm/iter012/validate_iter012_cross.slurm` and `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_validation/validate_iter012_cross.slurm`; SHA-256 `8e9e03aad7e9a2f0b1a37a9c4b8e23399a14917400ab5488c91b766eac7a5988` | `23445328` | `COMPLETED 0:0` | Submitted `2026-07-28 20:58 America/Phoenix`; 2:26, `TotalCPU 02:11.467`, batch MaxRSS `18988792K`; all cross-artifact gates passed |

## Independent Read-Only Review

- Reviewer: independent read-only subagent `/root/iter012_readonly_review`.
- Review round 1 source-manifest SHA-256:
  `a39c83e865959adaab06ab90879159d6e45cbffc292b368e3a213160755d0e1c`.
- Review round 1 outcome: `block`.
- Blocking findings: the execution source manifest pinned this mutable ledger, so the required
  review/job checkpoints would invalidate every later job's `sha256sum -c`; `N_JOBS` and
  `PRE_DISPATCH` were declared but neither passed nor recorded; the alleged ABBY batch test used
  four separate single-row calls; and negative coverage did not operationally exercise duplicate
  JSON parameter names or missing/extra/duplicate feature lists.
- Primary-agent correction: removed the mutable ledger from the immutable execution-source
  manifest; made worker controls required release-tool inputs and artifact provenance; extended
  the inference-matrix API to accept true per-row surface/climatology batches and changed the
  validator to one four-row ABBY prediction call; centralized duplicate-key-rejecting JSON
  parsing; and added order/missing/extra/duplicate feature plus duplicate-parameter negative
  gates. Static checks, source-manifest regeneration, rematerialization, and passing re-review are
  required before preflight.
- Review round 2 source-manifest SHA-256:
  `59efeec845189a7679698b03ab0ea73f47458cb85f1a51a5396136d82c8de726`.
- Review round 2 outcome: `pass`. The reviewer verified that all round-1 blockers were corrected,
  the two release copies and both validation copies are byte-identical, the five-line configs
  match the locked TSV, and the full immutable source manifest passes. No execution-affecting
  defect remains.

## Execution and Diagnostics

- Static validation: `bash -n`, Python compilation with a temporary bytecode root, TSV
  cardinality checks, `git diff --check`, full source-manifest verification, and materialized
  copy/config equality passed.
- Exact preflight submission command, executed from the locked preflight root:
  `sbatch --parsable ./validate_iter012.slurm </dev/null`; returned `23445069`.
- Immediate outside-sandbox `squeue`/`scontrol` identity checks matched
  `spinup_iter012_preflight`, `standard/chopinsong`, 1 CPU/5 GB, 5 minutes, the exact preflight
  working directory, relative submitted script, `/dev/null` stdin, and expected root-level logs.
- Preflight terminal accounting: `23445069` completed `0:0` in `00:00:25`,
  `TotalCPU 00:03.864`, batch MaxRSS `202660K`, allocation `cpu=1,mem=5G,node=1`, and cleared
  `squeue`. Stdout ended with `ITER012_PREFLIGHT_OK no_training=true` and confirmed exact
  32/21-feature manifests, seed-`10001` references, and bridge shape/dtype. Stderr contained only
  the known non-fatal upstream ArviZ future warning. No validation-only retry was used.
- Exact first-release submission command, executed from the locked `drop32` run directory:
  `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/submission_config.env ./submit_drop32.slurm </dev/null`;
  returned `23445100`.
- Immediate outside-sandbox identity checks matched job name `spinup_iter012_release`,
  `standard/chopinsong`, 10 CPUs/50 GB, 15 minutes, exact `drop32` work directory and relative
  submitted script, `/dev/null` stdin, and root-level stdout/stderr.
- `drop32` terminal accounting: `23445100` failed `1:0` after `00:01:39`,
  `TotalCPU 01:02.296`, batch MaxRSS `48489044K`, allocation `cpu=10,mem=50G,node=1`. This was
  not a scheduler/resource interruption.
- Failure diagnostic: source-manifest and provenance gates passed; case/forcing preparation
  completed. The release then stopped in `_audit_target_metadata` because restart variable
  `totsomc` in ABBY member-1 restart
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe/UQ/ABBY_ppe6_I1850CNPRDCTCBC/g00001/ABBY_ppe6_I1850CNPRDCTCBC.elm.r.0201-01-01-00000.nc`
  did not provide non-empty `units` and `long_name` values under the locked audit. Read-only
  string inspection confirms the restart stores the `totsomc`, `long_name`, and `units` metadata
  keys but does not establish usable values. No pickle, artifact manifest, or validation report
  was written.
- Classification and action: application/schema failure and release-blocking target-metadata
  ambiguity. The original contract forbade automatic code/configuration changes or retry. The
  `drop21_corr080` and cross-artifact jobs were not submitted. The user subsequently authorized
  the bounded recovery contract above; the metadata diagnostic is now the next action.
- Recovery diagnostic review round 1 outcome: `block`. The reviewer found unbounded hashing of
  every direct history-file match and incomplete strict-JSON normalization for NumPy scalar
  attributes. The primary agent capped selection deterministically at three history files per
  case with candidate/omission accounting, made NumPy scalar normalization recursive, and added
  mapping normalization.
- Recovery diagnostic review round 2 outcome: `pass`; no remaining execution-affecting defect.
  The exact submitted Python and Slurm copies match their canonical bytes. Submission command
  `sbatch --parsable ./diagnose_iter012_target_metadata.slurm </dev/null` returned `23445192`.
  Immediate identity checks matched `spinup_iter012_metadata`, `standard/chopinsong`, 1 CPU/5 GB,
  5 minutes, the exact diagnostic work directory, relative script, `/dev/null` stdin, and
  expected root-level logs.
- Diagnostic `23445192` was killed by the 5-GB cgroup after 29 seconds:
  `OUT_OF_MEMORY 0:125`, `TotalCPU 00:06.132`, batch MaxRSS `5242016K`. Stdout was empty;
  stderr recorded one Slurm OOM kill; no diagnostic JSON was written. The input case pickles are
  each about 1.8-2.1 GB and the diagnostic retained all nine, so this is a scheduler/resource
  failure with a concrete memory-retention cause. The authorized one same-cap resource retry is
  eligible. The correction removes pickle loading entirely and derives the nine already-locked
  member-1 restart paths explicitly; it does not change scientific scope or metadata gates.
- The corrected diagnostic received an independent `pass`: all nine explicit paths match
  `_restart_file` member-1 semantics and exist, all nine target components remain covered, I/O
  is bounded, and no pickle/model import, fitting, training, or scheduler call remains. Exact
  corrected submitted bytes were verified. The one same-cap retry command returned `23445233`;
  immediate identity checks matched the locked diagnostic job, 1 CPU/5 GB/5 minutes, exact
  work directory/script/stdin/logs, and `standard/chopinsong`.
- Diagnostic retry `23445233` completed `0:0` in `00:00:10`, `TotalCPU 00:00.682`,
  batch MaxRSS `30820K`, allocation `cpu=1,mem=5G,node=1`, and cleared `squeue`. Stdout reported
  `ITER012_TARGET_METADATA_DIAGNOSTIC_OK cases=9 components=9 missing_or_empty=81`; stderr was
  empty. Evidence JSON SHA-256:
  `91025494247e060558b39919aa664f0288f943b1b823565ca89153526448592e`.
- Evidence result: all 81 component/case records store explicit but empty restart `units` and
  `long_name` attributes. Across three deterministically selected colocated native ELM history
  files for each of nine cases (27 files total), the same E3SM Land Model version
  `468a9a4a84` consistently defines `TOTSOMC` as `gC/m^2`,
  `total soil organic matter carbon`, and `TOTSOMN` as `gN/m^2`,
  `total soil organic matter N`. The restart components are finite one-dimensional
  `column` arrays; the training scalar remains the exact existing `numpy.nansum` component
  aggregation.
- Evidence-supported correction: preserve and record the exact restart-component scalar
  calculation, but derive only target units and long names from three colocated native history
  diagnostics per case after requiring exact ELM source/version equality. Record raw empty
  restart attributes, history paths/hashes/shape/dimensions, and the diagnostic JSON hash in the
  artifact. No target, component, scalar calculation, value, model, data, or resource changes.
- Recovery release-audit review round 1 outcome: `block`. Although the evidence supported the
  correction and the source manifest locked both code and JSON, the audit initially rebound only
  to mutable live files while citing the locked diagnostic. The reviewer identified a
  case-mapping/TOCTOU provenance defect.
- Primary-agent correction: require exact diagnostic case identity/order, component-map
  source/path/hash, restart path/hash, component dimensions/shape/raw attributes/nansum, history
  candidate/omission counts and selected path set, history hashes, exact ELM source/version, and
  target attributes/dimensions/shape/nansum. Any live/evidence difference now stops release.
- Recovery release-audit review round 2 outcome: `pass`; the provenance binding resolves the
  blocker and no execution-affecting defect remains. Full locked source-manifest SHA-256:
  `1225db62b484cce11ce8e633c9fe1c8e47b5095c1323f2687c9e4c6454335875`.
- All static checks and the full source manifest passed; both release scripts/configs and the
  preflight/cross-validation scripts were rematerialized byte-identically. Recovery preflight
  command `sbatch --parsable ./validate_iter012.slurm </dev/null` returned `23445263`.
  Immediate identity checks matched `spinup_iter012_preflight`, `standard/chopinsong`,
  1 CPU/5 GB/5 minutes, exact preflight work directory/script, `/dev/null` stdin, and expected
  root-level logs.
- Recovery preflight `23445263` completed `0:0` in `00:00:20`, `TotalCPU 00:03.244`, batch
  MaxRSS `196872K`, allocation `cpu=1,mem=5G,node=1`, and cleared `squeue`. Stdout verified every
  locked source including the diagnostic JSON and ended with
  `ITER012_PREFLIGHT_OK no_training=true`; stderr was empty.
- Exact `drop32` recovery submission command, from the locked run directory, returned
  `23445281`. Immediate identity checks matched `spinup_iter012_release`,
  `standard/chopinsong`, 10 CPUs/50 GB/15 minutes, exact `drop32` work directory and relative
  submitted script, `/dev/null` stdin, and expected root-level logs.
- `drop32` recovery retry `23445281` completed `0:0` in `00:01:47`,
  `TotalCPU 01:12.053`, batch MaxRSS `38612468K`, allocation `cpu=10,mem=50G,node=1`, and
  cleared `squeue`. Stderr contained only the known non-fatal ArviZ future warning.
- `drop32` release evidence passed: exact Iter011 seed-`10001` reproduction for both targets;
  900-row full fit; pre-save/post-load maximum absolute prediction difference `0.0` for shape
  `[12,2]`; versioned-artifact validation; exact metadata provenance; and atomic artifact plus
  sidecars. Artifact path:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl`;
  size `80440` bytes; SHA-256
  `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`.
- Exact `drop21_corr080` submission command, from its locked run directory, returned `23445296`.
  Immediate identity checks matched `spinup_iter012_release`, `standard/chopinsong`,
  10 CPUs/50 GB/15 minutes, exact compact-variant work directory and relative submitted script,
  `/dev/null` stdin, and expected root-level logs.
- `drop21_corr080` job `23445296` completed `0:0` in `00:01:23`,
  `TotalCPU 01:09.424`, batch MaxRSS `37314156K`, allocation `cpu=10,mem=50G,node=1`, and
  cleared `squeue`. Stderr contained only the known non-fatal ArviZ future warning.
- `drop21_corr080` release evidence passed: exact Iter011 seed-`10001` reproduction for both
  targets; 900-row full fit; pre-save/post-load maximum absolute prediction difference `0.0`
  for shape `[12,2]`; versioned-artifact validation; exact metadata provenance; and atomic
  artifact plus sidecars. Artifact path:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl`;
  size `68048` bytes; SHA-256
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`.
- Exact cross-artifact validation submission command, from the locked validation directory,
  returned `23445328`. Immediate identity checks matched `spinup_iter012_validate`,
  `standard/chopinsong`, 10 CPUs/50 GB/15 minutes, exact validation work directory and relative
  submitted script, `/dev/null` stdin, and expected root-level logs.
- Cross-artifact job `23445328` completed `0:0` in `00:02:26`,
  `TotalCPU 02:11.467`, batch MaxRSS `18988792K`, allocation `cpu=10,mem=50G,node=1`, and
  cleared `squeue`. Stderr contained only the known non-fatal ArviZ future warning.
- Both variants passed fresh-process load, schema/manifest size/hash equality, one real member
  from each of nine training cases, one true four-row ABBY batch call with output shape `[4,2]`,
  named/positional midpoint equality, empirical-range warning behavior, and negative gates for
  feature order/missing/extra/duplicate, parameter missing/extra/duplicate/bounds, and schema.
  Both forcing bridges passed ordered `[engineered forcing | parameters | spinup]` construction
  with shape `[3,21]`, dtype `float64`, and ordered spinup columns `TOTSOMC,TOTSOMN`; no forcing
  artifact or real SR/flux prediction was claimed.
- Cross decision: release both user-accepted versions. `drop32` is recommended for accuracy;
  `drop21_corr080` is the compact tradeoff with its Iter011 comparative performance-gate failures
  preserved. Sidecar copies under `summaries/iter012/` are byte-identical. Release-decision
  SHA-256: `5fbabe000f9b64bb54517368c2a4329ca1473d09f23f0402a88d3c00ec973482`.
- Queue/accounting evidence: all submitted jobs are terminal and reconciled above; final
  job-scoped queue check found no active Iter012 jobs.
- Resource diagnostics: diagnostic OOM cause corrected and same-cap retry completed at 30,820K.
- Failure classification: original release remains application/schema; the bounded
  audit-provenance correction passed static validation, independent review, recovery preflight,
  both release jobs, and cross-artifact validation.

## Results and Release Decision

| Variant | Iter011 scientific evidence | Reproduction gate | Full-data artifact | Operational gates | Release decision |
| --- | --- | --- | --- | --- | --- |
| `drop32` | recommended accuracy-oriented 32-feature version | passed exactly | `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e` | passed | release, recommended |
| `drop21_corr080` | compact 21-feature tradeoff; failed Iter011 performance gates | passed exactly | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | passed | release, compact tradeoff |

- Preserved Iter011 validation headline for `drop32`: TOTSOMC/TOTSOMN median R2
  `0.827271 / 0.827497`, minimum R2 `0.699599 / 0.699270`, median RMSE
  `4150.32 / 415.26`, median RMSE ratio `0.893196 / 0.893928`, and warning fraction
  `0.25 / 0.24`.
- Preserved Iter011 validation headline for `drop21_corr080`: median R2
  `0.801217 / 0.801178`, minimum R2 `0.671361 / 0.672209`, median RMSE
  `4478.95 / 448.79`, median RMSE ratio `0.921297 / 0.921987`, and warning fraction
  `0.22 / 0.23`. It remains a compact tradeoff that failed the locked median/minimum R2 and
  median-RMSE-ratio gates.
- Forcing-bridge validation: passed for both artifacts; design-matrix compatibility only.
- Final release decision: release both user-accepted artifacts with the roles above.
- Next action: use the released artifacts or begin any forcing integration under a separate
  objective and runtime contract.

## Final Accounting and Handoff Validation

- Final job-scoped `squeue` on `2026-07-29 America/Phoenix` returned no rows for
  `23445069,23445100,23445192,23445233,23445263,23445281,23445296,23445328`.
- Final `sacct` confirmed the terminal states and accounting recorded in the ledger: the original
  release remained `FAILED 1:0`, the first metadata diagnostic remained
  `OUT_OF_MEMORY 0:125`, and all permitted recovery, release, and cross-validation jobs remained
  `COMPLETED 0:0`.
- Four-record validator:
  `python development/spinup_surrogate/slurm/iter012/validate_iter012_handoff.py --active-job-count 0`.
  Source SHA-256:
  `c21b7b1f3a877b4bd1980aa5d620e16b2542f3ed970ff1a0aba94b5401857810`.
  Result: `PASS: Iter012 four-record handoff and artifact validation`.
- Static closeout checks passed: Python compilation for all new Iter012 Python sources,
  `bash -n` for Iter012 shell/Slurm sources, and `git diff --check`.
- The login-node Python environment does not contain NumPy, so the CLI `--help` import check was
  not used as release evidence. The authorized compute-node preflight and cross-artifact job
  exercised the real NumPy/scikit-learn environment and passed.

## Proposed Next-Iteration Plan (Planning Only)

Iter012 is the terminal spinup-surrogate development release. No Iter013 experiment is proposed.
Future work, under a separate objective and runtime contract, may integrate a released spinup
artifact with a real forcing-surrogate artifact and validate actual forcing-target predictions.

## Closeout Checklist

- [x] Runtime contract and source provenance locked
- [x] Independent read-only review passed
- [x] Bounded no-training preflight completed
- [x] Both release jobs terminal and accounted
- [x] Cross-artifact validation terminal and accounted
- [x] All failures classified and permitted retries exhausted
- [x] Release gates and forcing bridge validated
- [x] Sidecars copied byte-identically to `summaries/iter012/`
- [x] `README.md`, `ITERATION_SUMMARY.md`, `registry.csv`, and `CURRENT.md` finalized
- [x] Four-record handoff validator passed with no active Iter012 jobs
- [x] One authorized closeout commit created by this final tree snapshot
