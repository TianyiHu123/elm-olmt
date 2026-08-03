# iter001 - Historical Forcing-Surrogate Offline Baseline

## Status

- Iteration ID: `iter001`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter001_pilot`,
  `spinup_forcing_coupling_iter001_baseline`, and
  `spinup_forcing_coupling_iter001_aggregate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-31T20:15:05-07:00`
- Closed: `2026-08-03T14:52:55-07:00`

## Finalized Plan

The finalized plan is the exact approved content of
`development/spinup_forcing_coupling/iterations/iter001_plan.md`, SHA-256
`74ee92bddb286d194a899785ac82de0647f74a058a74888b32f4890d88ac3433`. Its immutable
terms are summarized here without replacing that authoritative content.

- Sequential ID and work type: `iter001`; implementation.
- Objective: establish a reproducible nine-site historical forcing-surrogate offline baseline
  for `SR` before coupling to the spinup surrogate.
- Upstream dependencies and trust assumptions: the nine named local case pickles, their
  referenced forcing and restart data, ordered `ensemble_parms`, repository source, and
  `OLMT_puma`; user-owned serialized inputs are trusted to load, subject to preflight identity,
  schema, path, and provenance validation.
- Bounded scope: direct forcing-output layout; pooled and per-site train/test metrics and
  overfitting diagnostics; reproducible eight-repeat held-out permutation importance; one pilot,
  100 production seeds, aggregation, plots, validators, documentation, examples, and synthetic
  tests. Exclusions are coupling, saved-artifact inference validation, spinup/MCMC layout changes,
  feature filtering or selection, tuning beyond the historical quick grid, accuracy-driven
  retraining, and post-result gate revision.
- Acceptance and decision: the pilot and production functional/data-integrity gates in the
  approved plan are immutable. Poor but finite scores are baseline evidence; no predictive
  accuracy threshold is imposed and Iter001 cannot claim coupling readiness.
- Site and resource envelope: Puma `standard` under `chopinsong`; one 1-CPU/5-GB/15-minute
  preflight, one 120-GB/4-hour/12-worker pilot, production array `1-100%5` with 120 GB,
  4 hours, and 12 workers per leaf, and one 1-CPU/5-GB/1-hour aggregation.
- Boundaries: 103 nominal tasks and 204 hard-cap tasks; one minimal preflight correction/rerun;
  one same-scope production-index retry only for confirmed transient scheduler/node failure; no
  automatic pilot or aggregation retry and no automatic application/code/data/schema/numerical/
  OOM/timeout retry; bounded cancellation only for recorded Iter001 jobs under a proven universal
  pre-execution defect.
- Evidence: locked dependencies and source, submitted-copy/config equality, independent read-only
  review, preflight and terminal accounting, pilot artifacts, 100 production records, aggregate
  tables/plots, resource evidence, compact summary, four durable records, and cross-record
  validation.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `Approve the package as written`; accepted `2026-07-31T20:15:05-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Establish the nine-site `SR` offline baseline; 103 nominal and 204 maximum scheduler tasks; stop after terminal accounting, aggregation, immutable gate evaluation, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` SHA-256 `4391a6c4993a070687809eaece51eb718d2b8e58289a5b20c46ff4fd0c67d87b` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to children `spinup_forcing_coupling_iter001_pilot/`, `spinup_forcing_coupling_iter001_baseline/`, and `spinup_forcing_coupling_iter001_aggregate/`; retain the shared memmap/layout, pilot model/scalers, exactly 100 production JSON records, aggregate tables/plots, submitted material, logs, and accounting; production models excluded; `/xdisk` is temporary and unbacked |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact approved plan and immutable summary above; dependency content hashes and internal schemas are locked during authorized preparation/preflight before substantive execution |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, gated pilot/production/aggregation, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 1 CPU/5 GB/15 min; pilot 120 GB/4 h/12 workers; production `1-100%5`, 120 GB/4 h/12 workers per leaf; aggregation 1 CPU/5 GB/1 h; one minimal preflight correction/rerun; one confirmed-transient production retry per affected leaf; all other retries require fresh approval |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Locked `sbatch` and allowed resubmission; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits` throughout monitoring/accounting; bounded `scancel` as above |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/examples/iteration material/summaries/records only; raw outputs, memmap, models, logs, and unrelated `.README.md.swp` excluded; no push |

### Fresh Pilot OOM Amendment

- User response: exact response `Use 150GB memory and with N_JOBS=4, existing-memmap reuse, and
  four hours`; accepted `2026-08-01T13:59:39-07:00`.
- Authority: exactly one pilot-only rerun after job `23467686` OOM, with `--mem=150G`, four-hour
  limit, `N_JOBS=4`, and reuse of the existing feature memmap/layout. On Puma the 150-GB memory
  request derives 30 CPUs; one-thread math-library limits remain unchanged.
- Reused artifact lock: `X_forcing_memmap.dat`, 7,148,160,000 bytes, SHA-256
  `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout
  `X_forcing_memmap_layout.npz`, 73,374,948 bytes, SHA-256
  `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`.
- All original scientific scope, seed, split, grid, gates, production resources/retry limits,
  aggregation resources, cancellation boundary, and closeout terms remain unchanged.

### Conditional Pilot Timeout Amendment

- User response: exact response `If this preflight job failed by timeout, a 12 hour new preflight
  job is approved for retry. for the retry, add time diagosetics to the code, identify the most
  time consuming part and save the diagnostics with suggestions on efficiency improvements to the
  conrresponsing file.`; accepted `2026-08-01T17:33:39-07:00`.
- Interpretation: “preflight job” refers to the only active job, pilot OOM-rerun `23473876`, since
  discovery job `23467601` and full preflight job `23467631` already completed successfully. If
  that interpretation is wrong, the user may correct it before the condition is triggered.
- Conditional authority: only if job `23473876` reaches authoritative `TIMEOUT`, authorize one
  12-hour pilot retry after adding stage-level timing diagnostics, refreshing locks/submitted
  copies, static validation, and independent read-only re-review. Save measured stage durations,
  identify the longest stage, and preserve concrete efficiency suggestions in a dedicated timing
  diagnostic artifact and this iteration record. This grants no retry for OOM, application error,
  cancellation, or any other failure class and does not alter the active job.

### Fresh Pilot Validator Repair Amendment

- User response: exact response `approved`; accepted `2026-08-01T18:20:25-07:00` in response to
  the primary agent's exact repair package.
- Authority: normalize the pilot validator's class-style NumPy dtype representation and add a
  targeted test; preserve the original training source-manifest hash separately; refresh
  validation locks and submitted copies; obtain independent read-only review; and run exactly one
  validation-only Puma job at one requested CPU, Puma-derived 5 GB, and 15 minutes against the
  existing artifacts with no retraining.
- Continuation rule: if the repaired validator passes every original pilot gate, continue the
  already-approved production, aggregation, evaluation, durable-record, validation, and closeout
  lifecycle. If the validation-only job or gate fails, stop for a fresh decision. The amendment
  does not change scientific controls, production resources/retry policy, acceptance gates, or
  closeout terms.

### Fresh Production OOM Amendment

- User response: exact response `approved with only 1 change: array 1-100%10`; accepted
  `2026-08-01T18:59:30-07:00` in response to the primary agent's replacement-array package.
- Authority: exactly one full replacement production array with `--mem=150G`, `N_JOBS=4`, a
  six-hour walltime, existing read-only memmap reuse, and array `1-100%10`. All seeds, split,
  quick grid, CV, permutation importance, stats-only retention, output paths, scientific controls,
  production failure policy, aggregation, gates, and closeout terms remain unchanged.
- Lifecycle cap: amended to 206 total tasks, accounting for the earlier preflight correction,
  pilot correction, validation-only correction, failed/cancelled 100-leaf array, this replacement
  100-leaf array, and future aggregation. No second OOM/application retry is authorized.

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Nine case pickles | Training data and metadata | `pklfiles/{ABBY,JERC,OSBS,SOAP,RMNP,TALL,TEAK,WREF,YELL}_ppe6_I20TRCNPRDCTCBC.pkl` | Exact ordered `ensemble_parms`, forcing/restart identities, and schemas validated in full preflight | Present; sizes 1,892,599,187-2,208,029,300 bytes; exact hashes in the dependency manifest | User-owned local serialized cases; full compute-node identity/schema/provenance checks passed before pilot |
| Forcing trainer | Implementation source | `train_surrogate_forcing.py`, `model_ELM/surrogate_NN_Forcing.py`, `model_ELM/surrogate_forcing_multicase.py` | Repository commit plus bounded Iter001 changes | immutable training snapshot `iter001_training_source_manifest.sha256`, SHA-256 `1517679650bd28f941be68d92bff75c9064f361958053346e8ca9aaf2a64b0ee`; current execution manifest SHA-256 `1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6` | Original training provenance preserved; refreshed 30-entry replacement-production manifest passes; ledgers excluded |
| Puma environment | Runtime | `conda_envs/OLMT_puma.yml`; environment `OLMT_puma` | `micromamba/2.0.2-2`; Python `3.11.15`; exact package inventory in dependency manifest | YAML size 1,139 bytes; runtime identity passed full preflight | Validated on a Puma compute node before training |
| Workflow and plan | Lifecycle and immutable controls | `development/spinup_forcing_coupling/WORKFLOW.md`; `iterations/iter001_plan.md` | Workflow SHA-256 `6887a2bd17c30596c90e631b7988bd0617bba7fa4a8f8a7fb54ce77b44d025b6`; plan SHA-256 `74ee92bddb286d194a899785ac82de0647f74a058a74888b32f4890d88ac3433` |  — | Read and approved before initialization |

- Repository commit: `2648998d4ceb08ecf72859a7d5200c0e3a5eb41d` on
  `feature/surrogate_coupling`.
- Bounded initial source manifest: tracked tree clean at approval; untracked approved
  `iterations/iter001_plan.md`; unrelated user-owned
  `development/spinup_forcing_coupling/.README.md.swp` excluded and untouched.
- Environment identity: `OLMT_puma`; exact module/package/runtime evidence pending preflight.

## Acceptance Gates and Decision Rule

- Required completeness: one eligible pilot and exactly 100 eligible production records for
  seeds `10001-10100`, complete aggregate artifacts, and authoritative accounting for every task.
- Pilot gates: `COMPLETED 0:0`; exact cases, target, seed, split, ordered schema, and quick grid;
  finite pooled/per-site train/test R2 and RMSE; computable pooled/per-site gap, ratio, and warning;
  complete finite pooled importance; valid reusable read-only memmap/layout; valid pilot model and
  scalers; complete configuration, provenance, logs, and output records.
- Production gates: exactly 100 nonduplicate eligible seeds; matching dependency/source/config/
  seed/split/schema provenance; complete finite pooled/per-site metrics and diagnostics; complete
  finite pooled importance; valid aggregate tables/plots; authoritative accounting and classified
  failures.
- Decision rule: finite poor quality does not reject the functional baseline. Pass means technical
  offline training validation and predictive-quality characterization only, never coupling
  readiness or saved-artifact inference validation.
- Comparative aggregation: full pooled/per-site metric distributions; overfitting fraction;
  importance by test-RMSE increase, test-R2 decrease, median rank, top-10 frequency, and positive
  frequency. No candidate ranking or tie-breaker applies.
- Fresh authorization is required for any application/code/data/interface/schema/dependency/
  numerical repair after submitted execution material is locked, resource-cap or scientific-scope
  change, disallowed retry, task beyond the amended 206-task cap, or gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| module-discovery preflight | `preflight_iter001.slurm` / `24af7c6...` | `submit_preflight_iter001.slurm` / `24af7c6...`; `preflight_submission_config.env` / `ff47a1a...` | approved pilot directory; `preflight_23467601.{out,err}` | source manifest `14e7b45...`; dependency hashing deliberately gated off | commit `2648998...`; locked manifest | `23467601` | `COMPLETED 0:0` | Discovery-only first preflight attempt; resolved `micromamba/2.0.2-2`; cannot satisfy the full preflight gate; authorized pinning correction/rerun remains |
| pinned full preflight | `preflight_iter001.slurm` / `24af7c6...` | `submit_preflight_iter001.slurm` / `24af7c6...`; `preflight_submission_config.env` / `f4f941b...` | approved pilot directory; `preflight_23467631.{out,err}` | refreshed source manifest `7f8a087a...`; dependency manifest `e718a00f...` | commit `2648998...`; refreshed locked manifest | `23467631` | `COMPLETED 0:0`; gate pass | one authorized pinning correction/rerun consumed |
| pilot seed 10001 | `pilot_iter001.slurm` / `b1fdf41...` | `submit_pilot_iter001.slurm` / `b1fdf41...`; refreshed `pilot_submission_config.env` / `37fd8ea...` | approved pilot directory; `pilot_23467686.{out,err}` | source `7f8a087a...`; dependency `e718a00f...` | commit `2648998...`; refreshed locked manifest | `23467686` | `OUT_OF_MEMORY 0:125`; failed | no pilot retry or resource/config change authorized; fresh decision required |
| pilot seed 10001 OOM rerun | `pilot_iter001.slurm` / `58d6eba...` | `submit_pilot_iter001.slurm` / `58d6eba...`; `pilot_submission_config.env` / `18cd9ef...` | approved pilot directory; `pilot_23473876.{out,err}` | source manifest `15176796...`; dependency `e718a00f...`; exact reused memmap/layout hashes | commit `2648998...`; refreshed lock reviewed | `23473876` | `FAILED 1:0`; training artifacts written, post-training validator error | rerun consumed; conditional 12-hour timeout retry not triggered because terminal state was not `TIMEOUT` |
| validation-only pilot repair | `validate_pilot_iter001.slurm` / `452d855...` | `submit_validate_pilot_iter001.slurm` / `452d855...`; `validation_submission_config.env` / `53e4902...` | approved pilot directory; `validate_pilot_%j.{out,err}` | training manifest `15176796...`; validation manifest `01d0cd96...`; exact dependency/config/stats/artifact/memmap/layout hashes | commit `2648998...`; refreshed validation lock | `23475958` | `COMPLETED 0:0`; validator pass | one validation-only job consumed; no retraining |
| production seeds 10001-10100, failed array | canonical at submission `production_iter001.slurm` / `c14b295...` | preserved `submit_production_iter001_job23476014.slurm` / `c14b295...`; `submission_config_job23476014.env` / `b0aa32d...` | approved baseline directory; `production_23476014_%a.{out,err}` | pilot validation `ef651685...`; source `01d0cd96...`; dependency `e718a00f...`; validated memmap/layout | commit `2648998...`; historical lock preserved | `23476014` | terminal: leaves 1-15 OOM; leaves 16-100 cancelled before execution | universal 120-GB/12-worker resource defect |
| replacement production seeds 10001-10100 | `production_iter001.slurm` / `173e514...` | `submit_production_iter001.slurm` / `173e514...`; `submission_config.env` / `ef9b837...` | approved baseline directory; `production_%A_%a.{out,err}` | pilot validation `ef651685...`; source `1f71df1b...`; dependency `e718a00f...`; validated memmap/layout | commit `2648998...`; refreshed replacement lock | `23476164` | all 100 leaves `COMPLETED 0:0`; exact-100 eligibility pass | exactly one replacement array `1-100%10`; no second OOM/application retry |
| aggregation | `aggregate_iter001.slurm` / `c892068...` | `submit_aggregate_iter001.slurm` / `c892068...`; refreshed `submission_config.env` / `c059962...` | approved aggregate directory; `aggregate_23489654.{out,err}` | exactly 100 eligible production records and locked manifests | commit `2648998...`; refreshed locked manifest | `23489654` | `COMPLETED 0:0` in 23 s; `AGGREGATION_PASS` / `AGGREGATE_VALIDATION_PASS` | no retry authorized |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter001_readonly_review`; review started
  `2026-07-31T20:38:13-07:00`.
- Reviewed source hash: source-manifest file SHA-256
  `14e7b45c71aa9b25996ed9d2c539ba9cdb3ba9ffbff5d0f6d1616501ecc08204`.
- Outcome: `pass` specifically for the discovery-only preflight.
- Findings and primary-agent response: the initial `pass_with_concerns` identified unpinned module
  identity, source-before-config validation, weak exact-provenance checks, and thin aggregate
  output validation. The primary moved config comparison before source, enforced exact commit and
  recomputed schema hashes, added YAML/runtime environment locking, an independent aggregate
  validator, and a 100-record synthetic end-to-end test. Refreshed review verified all corrections
  and that discovery exits before dependency hashing or Python. Pilot remains prohibited pending
  pinning, rematerialization, refreshed review, and the full preflight rerun.
- Pinned full-preflight re-review: `pass` with no blockers for exact source-manifest SHA-256
  `7f8a087a2a0af63915406dfc9c23bc431f46b0d3f4ff4a02663191935278a1fa`. The reviewer verified
  all 27 hashes, all eight canonical/submitted pairs, exact `micromamba/2.0.2-2` pins, Puma
  resources, pre-source comparisons, and the full compute-node dependency/schema/test path.
- OOM-correction review first pass: `fail` on source-manifest SHA-256 `527f1036...` because the
  exact locked dependency-manifest hash was recorded but not enforced before execution. All other
  resource, reuse, scientific-control, submitted-copy, and production-prohibition checks passed.
  The primary added `DEPENDENCY_MANIFEST_SHA256=e718a00f...`, validates it before module/Python,
  exports that locked value into stats provenance, refreshed submitted copies, and repeated all
  static checks. Corrected source-manifest SHA-256 is `1517679650bd28f941be68d92bff75c9064f361958053346e8ca9aaf2a64b0ee`;
  final re-review is pending.
- Corrected OOM-correction re-review: `pass` with no blockers for exact source-manifest SHA-256
  `1517679650bd28f941be68d92bff75c9064f361958053346e8ca9aaf2a64b0ee`. The reviewer verified
  dependency/memmap/layout identity enforcement before Python, all 27 source hashes, byte-equal
  submitted copies, 150-GB memory-only Puma shape, four workers, four hours, reuse wiring,
  unchanged scientific controls, validator coverage, and continued production prohibition.
- Validator-repair review first pass: `block` on source-manifest SHA-256 `d37d8e48...` because the
  validation job specified both one CPU and 5 GB. Per the Puma profile, the primary removed the
  redundant memory directive so one CPU derives the approved 5 GB, refreshed the submitted copy,
  and repeated hash/equality/Bash/diff checks. Corrected source-manifest SHA-256 is
  `01d0cd967e8bedf7b5bbeee9b753b88685dc14d54707b6afef54b16a81ad0a6d`; re-review pending.
- Validator-repair corrected re-review: `pass` with no blockers for exact source-manifest SHA-256
  `01d0cd967e8bedf7b5bbeee9b753b88685dc14d54707b6afef54b16a81ad0a6d`. The reviewer verified
  all 30 hashes, training snapshot `15176796...`, dtype normalization, separated training and
  validation provenance, exact artifact/config/dependency locks, byte-equal submitted copies,
  Puma-compliant one-CPU/derived-5-GB/15-minute resources, no training invocation, and continued
  production prohibition.
- Final production-readiness review: `pass` with no blockers for exact source manifest
  `01d0cd96...`, canonical/submitted production script `c14b295...`, config `b0aa32d...`, pilot
  validation `ef651685...`, and dependency manifest `e718a00f...`. The reviewer verified terminal
  validation accounting/logs, composite-pilot authority, exact artifact identities, array
  `1-100%5`, 120-GB/4-hour memory-limited shape, `N_JOBS=12`, seeds 10001-10100, stats-only
  behavior, memmap reuse, output/log paths, provenance exports, and no production model retention.
- Replacement-production review: `pass` with no blockers for source manifest `1f71df1b...`,
  canonical/submitted script `173e514...`, and config `ef9b837...`. All 30 hashes, Bash syntax,
  diff checks, and submitted equality passed. The reviewer confirmed only the approved 120-to-150
  GB, four-to-six-hour, `%5`-to-`%10`, and 12-to-4-worker changes; preserved historical copies;
  Puma-compliant memory-only shape; unchanged scientific/provenance/output controls; pilot and
  dependency locks; zero preexisting records; one replacement authority; and the 206-task cap.

## Execution and Diagnostics

- Static validation: source-manifest `sha256sum -c` passed for all entries; `git diff --check`
  passed; `bash -n` passed for all four Slurm scripts; prohibited Puma directives and config-based
  `REPO_ROOT` overrides were absent; all eight canonical/submitted script/config comparisons
  returned byte-equal. After pinning, the refreshed source-manifest file SHA-256 is
  `7f8a087a2a0af63915406dfc9c23bc431f46b0d3f4ff4a02663191935278a1fa`; all checks passed again.
  Repository Python remains reserved for the compute-node preflight.
- Preflight: discovery-only job `23467601` submitted `2026-07-31T20:48:52-07:00` and completed
  `0:0` in 11 seconds on `r7u02n2`; stdout resolved `micromamba/2.0.2-2` with micromamba
  version `2.0.2`. Full preflight remains pending after pinning and refreshed review.
- Exact submission command: from the approved pilot directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_pilot/preflight_submission_config.env ./submit_preflight_iter001.slurm </dev/null`; returned `23467601`. Login-shell `.bashrc` emitted nonfatal sandbox-context `module: command not found` warnings before `sbatch` returned the job ID.
- Job identity checks: immediate outside-sandbox `squeue`/`scontrol show job` confirmed job name
  `sfc-i001-preflight`, account `chopinsong`, partition `standard`, one CPU/derived 5 GB,
  15-minute limit, submitted command/cwd, and log paths exactly match the lock.
- Pinned full preflight: job `23467631` submitted at `2026-07-31T20:56:47-07:00` with the same
  exact command against the refreshed config. Immediate outside-sandbox identity checks confirmed
  `sfc-i001-preflight`, `chopinsong/standard`, one CPU/derived 5 GB, 15 minutes, exact submitted
  command/cwd/log paths, and `PENDING (Priority)`.
- Pinned full-preflight result: `COMPLETED 0:0` on `r7u02n2`; elapsed `00:02:09`, total CPU
  `00:58.659`, batch MaxRSS `5241948K`, and 5 GB requested. Puma-resolved
  `/usr/local/bin/seff` reported 45.47% CPU efficiency and 99.98% memory efficiency. The log
  records all nine case hashes `OK`, Python `3.11.15`, seven tests `OK`, and
  `PREFLIGHT_PASS cases=9`; dependency-manifest SHA-256 is
  `e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9` with schema
  `spinup-forcing-coupling-iter001-dependencies-v1`, exact module/environment/YAML identity,
  90 installed distributions, nine ordered cases, 14 ordered parameters, seven forcing variables,
  two spinup variables, and per-file/per-schema provenance.
- HPC diagnostic: `/usr/bin/seff` was absent on the Puma login node; after consulting
  `development/hpc/puma.md`, `command -v seff` resolved `/usr/local/bin/seff`. This path issue did
  not affect the job. Full-preflight memory headroom was effectively zero but the gate completed
  without OOM; pilot and production have their separately approved 120-GB memory shape.
- Pilot submission: from the approved pilot directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_pilot/pilot_submission_config.env ./submit_pilot_iter001.slurm`; returned `23467686` at `2026-07-31T21:06:22-07:00`.
  Immediate `squeue`/`scontrol` identity matched `sfc-i001-pilot`, `chopinsong/standard`, exact
  command/cwd/logs, 120 GB memory, Puma-derived 24 CPUs, four-hour limit, and `PENDING (Priority)`.
- Pilot failure: authoritative `sacct` recorded parent and batch `OUT_OF_MEMORY 0:125` on
  `r4u35n2` after `00:03:16`; total CPU `03:48.787`, 24 allocated CPUs, 120 GB requested, and
  batch MaxRSS `125830156K`. Slurm stderr records two OOM-kill events. The job completed input
  loading, created the 7,148,160,000-byte float32 feature memmap and 73,374,948-byte layout, split
  52,560,000 rows into 42,048,000 training and 10,512,000 validation rows, then OOM-killed at
  `Training variable: SR` before any model, scaler, stats, or pilot validation artifact existed.
  The partial memmap/layout are retained but are not accepted as validated pilot artifacts.
- Failure classification: scheduler/resource failure. The approved package authorizes no pilot
  retry, and changing 120 GB, 12 workers, script reuse behavior, or execution material requires
  fresh approval. No pilot resubmission, production job, cancellation, or code/config change was
  performed after the failure.
- Fresh OOM authority: user approved exactly one rerun at `2026-08-01T13:59:39-07:00` using
  150 GB, four hours, four GridSearch workers, and the existing locked memmap/layout. Canonical
  pilot config/script now record those terms; refreshed source-manifest SHA-256 is
  `1517679650bd28f941be68d92bff75c9064f361958053346e8ca9aaf2a64b0ee` after the reviewer-required
  exact dependency-manifest lock. Submitted copies and static validation pass; final read-only
  re-review passed with no blockers.
- OOM rerun submission: from the approved pilot directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_pilot/pilot_submission_config.env ./submit_pilot_iter001.slurm`; returned `23473876` at `2026-08-01T14:07:05-07:00`.
  Immediate `squeue`/`scontrol` identity matched `sfc-i001-pilot`, `chopinsong/standard`, exact
  command/cwd/logs, 150 GB memory, Puma-derived 30 CPUs, four-hour limit, and
  `PENDING (Priority)`.
- OOM-rerun result: authoritative `sacct` records parent and batch `FAILED 1:0` on `r7u12n2`
  after `03:50:38`; total CPU `07:55:39`, 30 allocated CPUs, 150 GB requested, and batch MaxRSS
  `104576412K`. Puma-resolved `/usr/local/bin/seff` reports 6.87% CPU efficiency and 99.73 GB
  peak memory, 66.49% of the request. Training itself completed and wrote the pilot stats and
  model/scaler artifact. Pooled metrics are train R2 `0.9613383558`, test R2 `0.9455845286`,
  train RMSE `0.1610536918`, and test RMSE `0.2127959883`, with no pooled overfitting warning.
- Post-training validator failure: `validate_iter001_pilot.py` reached its memmap byte-size check
  and called `np.dtype(layout["dtype_str"])`; the locked layout contains
  `"<class 'numpy.float32'>"`, which NumPy does not accept as a dtype string, causing `TypeError`
  before `pilot_validation.json` was written. Read-only diagnosis shows the validator lacks a
  normalization path for the class-style dtype representation emitted by the training layout.
  This is an application-code failure, not a training, resource, data, schema, OOM, or timeout
  failure.
- Conditional timeout handling: the 12-hour retry condition was not triggered because job
  `23473876` ended `FAILED 1:0`, not `TIMEOUT`. No retry, source repair, production submission, or
  scheduler-state change was performed. A validator repair also needs a separate immutable
  training-manifest snapshot or explicit expected training-manifest hash: mutating the current
  source manifest would otherwise invalidate the already-written stats provenance hash
  `1517679650bd28f941be68d92bff75c9064f361958053346e8ca9aaf2a64b0ee`.
- Queue and terminal accounting: `PENDING (Priority)` at `2026-07-31T20:49:03-07:00`, then
  `COMPLETED 0:0`; elapsed `00:00:11`, total CPU `00:00.356`, one allocated CPU, 5 GB requested,
  and batch MaxRSS `7656K` on `r7u02n2`.
- Resource diagnostics: Puma quota observed at approval as 17.1/19.5 TB for
  `/xdisk/chopinsong`; `job-limits chopinsong` showed ample group capacity. These observations are
  pre-submit context, not job evidence.
- Pre-validation quota refresh: the sandbox `uquota` call failed only because its synthetic UID
  was unresolved; outside-sandbox `/usr/bin/uquota` authoritatively reported
  `/xdisk/chopinsong` at 17.0/19.5 TB, `/groups/chopinsong` at 473.5/500 GB, and `/home` at
  36.9/50 GB.
- Pre-production capacity: `job-limits chopinsong` reported group standard usage 185/16998 GB,
  37/3290 CPUs, and 22 submitted jobs; user standard usage 10/16998 GB and 2/3290 CPUs. The
  approved five-way 120-GB array concurrency fits current limits.
- Pre-replacement capacity: `/usr/bin/uquota` remained `/xdisk/chopinsong` 17.0/19.5 TB.
  `job-limits chopinsong` reported group standard usage 150/16998 GB and 30/3290 CPUs; the
  replacement `%10` maximum of 1.5 TB and 300 derived CPUs fits current limits.
- Validation-only submission: from the approved pilot directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_pilot/validation_submission_config.env ./submit_validate_pilot_iter001.slurm`; returned job `23475958` at
  `2026-08-01T18:27:08-07:00`. Login-shell `.bashrc` emitted the previously observed nonfatal
  `module: command not found` warnings before `sbatch` returned the parseable job ID; compute-node
  module loading remains inside the submitted script.
- Immediate validation-job identity: `squeue` and `scontrol show job 23475958` confirm
  `sfc-i001-pval`, `chopinsong/standard`, one node/task/CPU, Slurm-derived 5 GB, 15-minute limit,
  exact submitted command and pilot working directory, `/dev/null` stdin, exact log paths, and
  `PENDING (Priority)`.
- Validation-only result: job `23475958` ran on `r7u09n2` and completed `0:0` in `00:00:44`;
  total CPU was `00:15.380`, one CPU and derived 5 GB were allocated, and batch MaxRSS was
  `5241912K`. `/usr/local/bin/seff` reports 34.95% CPU efficiency and 99.98% memory efficiency.
  The memory headroom was effectively zero but the job completed without OOM. All 30 source
  hashes and eight tests passed, then the validator printed `PILOT_VALIDATION_PASS`.
- Pilot validation artifact: `pilot_validation.json` SHA-256
  `ef651685a8fbba6651a7b9fe465ef50b27a547d2fb1e3571a8f4a35241bdcc6f` records gate `pass`, stats
  SHA `bbe1b51...`, artifact SHA `bd3ecb0...`, 7,148,160,000-byte memmap, layout SHA `a6ea415...`,
  ordered schema SHA `cbe2daf...`, training manifest `15176796...`, and validation manifest
  `01d0cd96...`.
- Production submission: from the approved baseline directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_baseline/submission_config.env ./submit_production_iter001.slurm`; returned parent job `23476014` at
  `2026-08-01T18:37:53-07:00`. Login-shell module warnings were the same nonfatal login-context
  messages observed at prior successful submissions.
- Immediate production identity: `squeue` and `scontrol show job 23476014` confirmed array
  `1-100%5`, job name `sfc-i001-production`, `chopinsong/standard`, 120 GB deriving 24 CPUs per
  leaf, four-hour limit, exact submitted command/baseline working directory, `/dev/null` stdin,
  array log pattern, and `PENDING (Priority)`.
- Production failure and cancellation: at the scheduled `2026-08-01T18:54:25-07:00` check,
  leaves 1-15 had all left the queue and authoritative `sacct` classified all 15 as
  `OUT_OF_MEMORY 0:125` after `00:01:33`-`00:01:48`, each at 120 GB on multiple nodes. No leaf
  reached stats output. This 15-for-15 identical resource failure proved a universal defect, so
  the primary used the contract's emergency-cancellation authority and issued
  `/usr/bin/scancel 23476014` before any further leaves started.
- Cancellation reconciliation: `squeue --job=23476014` became empty. Final top-level leaf
  accounting contains exactly 100 tasks: leaves 1-15 `OUT_OF_MEMORY 0:125`, and leaves 16-100
  `CANCELLED by 49065` with zero elapsed time and no node allocation. No production stats JSON
  exists. Representative `/usr/local/bin/seff` reports leaf 1 at 1:42, 6.13% CPU efficiency, and
  120.00 GB/100% memory; leaf 15 at 1:35, 7.15% CPU efficiency, and 120.00 GB/100% memory.
- Failure classification: scheduler/resource failure with a proven universal 120-GB/12-worker
  defect. The approved retry applies only to confirmed transient scheduler/node failures, not
  OOM. Cancellation grants no fix or retry. Any new production array requires fresh resource and
  retry authority and must explicitly account for the amended lifecycle task cap.
- Replacement production submission: from the approved baseline directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_baseline/submission_config.env ./submit_production_iter001.slurm`; returned parent job `23476164` at
  `2026-08-01T19:02:14-07:00`. Login-shell module warnings were the same nonfatal login-context
  messages observed at prior successful submissions.
- Immediate replacement identity: `squeue` and `scontrol show job 23476164` confirmed array
  `1-100%10`, `chopinsong/standard`, 150 GB deriving 30 CPUs per leaf, six-hour limit, exact
  submitted command/baseline working directory/log pattern, and throttle 10. Leaves 1-3 started on
  `r4u26n1`/`r3u31n1`; leaves 4-100 remained pending by priority.
- Early replacement safety check: leaves 1-3 remained `RUNNING` at 3:02, beyond the failed
  array's universal 1:33-1:48 OOM window. Representative stdout confirms exact read-only memmap
  reuse, 52,560,000 rows, the unchanged split, and entry into `Training variable: SR`; stderr has
  only the known ArviZ future warning and no OOM/application marker.
- Scheduled replacement check at `2026-08-01T19:22:32-07:00`: leaves 1-3 remained `RUNNING` at
  19:55 with no failed leaf; leaves 4-100 remained pending by priority. The corrected shape has
  sustained more than ten times the failed array's universal OOM lifetime.
- Scheduled replacement check at `2026-08-01T19:37:44-07:00`: leaves 1-3 remained `RUNNING` at
  35:24 with no failed leaf; leaves 4-100 remained pending by priority.
- Scheduled replacement check at `2026-08-01T19:53:00-07:00`: leaves 1-3 remained `RUNNING` at
  50:27 with no failed leaf; leaves 4-100 remained pending by priority.
- Monitoring cadence amendment: after the 19:53 checkpoint, the user changed the standing
  job-check cadence from 15 to 30 minutes and explicitly pre-approved those checks without
  further confirmation.
- Scheduled replacement check at `2026-08-01T20:23:26-07:00`: leaves 1-3 remained `RUNNING` at
  1:20:52, leaves 4-5 were `RUNNING` at 2:58, and leaves 6-100 remained pending by priority.
  Leaves 4-5 independently reached SR training with exact read-only memmap reuse and only the
  known ArviZ warning; no failed leaf or OOM/application marker was present.
- Scheduled replacement check at `2026-08-01T20:53:24-07:00`: leaves 1-3 remained `RUNNING` at
  1:50:43, leaves 4-5 at 32:49, leaf 6 at 1:44, and leaves 7-100 remained pending by priority.
  Leaf 6 independently reached SR training with exact read-only memmap reuse and only the known
  ArviZ warning; no failed leaf or OOM/application marker was present.
- Scheduled replacement check at `2026-08-01T21:23:36-07:00`: leaves 1-10 were all `RUNNING`,
  ranging from 2:20:55 for leaves 1-3 to 0:50 for newly started leaf 10. Leaves 11-100 were
  pending solely for `JobArrayTaskLimit`, confirming the approved `%10` throttle was fully used;
  no leaf had failed or left the queue.
- Scheduled replacement check at `2026-08-01T21:54:09-07:00`: leaf 2 had left the queue and leaf
  11 replaced it at the full `%10` throttle. `sacct` classified leaf 2 (internal job `23476184`)
  `COMPLETED 0:0` in 2:37:47; its batch step used 92,852,528 K MaxRSS against 150 GB. The expected
  stats-only artifact `surrogate_forcing/surrogate_forcing_stats_seed10002_rs10002.json` exists,
  SHA-256 `96255ce2ed7e788f8c8fc7916d74c7deba8247980ee4d4dd476b46dd1fdd95f8`, and carries schema
  `olmt-forcing-surrogate-stats-v2` plus the exact locked source/dependency/config hashes. It is
  one production-record candidate pending the exact-100 aggregation validator; leaves 12-100
  remained pending for `JobArrayTaskLimit`.
- Scheduled replacement check at `2026-08-01T22:23:42-07:00`: leaf 1 had left the queue, leaves
  3-11 remained `RUNNING`, and leaves 12-100 were still pending for `JobArrayTaskLimit` before
  scheduler backfill. `sacct` classified leaf 1 (internal job `23476183`) `COMPLETED 0:0` in
  3:20:43; its batch step used 93,174,540 K MaxRSS against 150 GB. The expected stats-only
  artifact `surrogate_forcing/surrogate_forcing_stats_seed10001_rs10001.json` exists, SHA-256
  `fd22facacc125594c552a3fac287b508b81d0ad7115a20e6c9b57ad8359abc80`, and carries the exact
  locked schema and source/dependency/config hashes. The campaign now has two production-record
  candidates pending exact-100 aggregation validation.
- Scheduled replacement check at `2026-08-01T22:53:45-07:00`: leaf 3 had left the queue, leaves
  4-13 were `RUNNING` at the full `%10` throttle, and leaves 14-100 remained pending for
  `JobArrayTaskLimit`. `sacct` classified leaf 3 (internal job `23476185`) `COMPLETED 0:0` in
  3:40:12; its batch step used 102,582.50 M MaxRSS against 150 GB. The expected stats artifact
  `surrogate_forcing/surrogate_forcing_stats_seed10003_rs10003.json` exists, SHA-256
  `0c52fbcaa5721ea5821196f9f0f4502cf96bca270478206c80be6befbdae0542`, and carries the exact
  locked schema and source/dependency/config hashes. The campaign now has three production-record
  candidates pending exact-100 aggregation validation.
- Scheduled replacement check at `2026-08-01T23:23:20-07:00`: leaves 4-13 remained `RUNNING` at
  the full `%10` throttle, ranging from 3:03:02 for leaves 4-5 to 38:57 for leaf 13. Leaves
  14-100 remained pending solely for `JobArrayTaskLimit`; no additional leaf had failed or left
  the queue. The candidate count remains three pending exact-100 aggregation validation.
- Scheduled replacement check at `2026-08-01T23:54:01-07:00`: leaf 5 had left the queue, leaves
  4 and 6-14 were `RUNNING` at the full `%10` throttle, and leaves 15-100 remained pending for
  `JobArrayTaskLimit`. `sacct` classified leaf 5 (internal job `23477614`) `COMPLETED 0:0` in
  3:14:21; its batch step used 91,868,656 K MaxRSS against 150 GB. The expected stats artifact
  `surrogate_forcing/surrogate_forcing_stats_seed10005_rs10005.json` exists, SHA-256
  `3c09e3035e03b249d8d5bb7ca28fb2b3340f99296ee7cd9541feb3d5e6b97a5e`, and carries the exact
  locked schema and source/dependency/config hashes. The campaign now has four production-record
  candidates pending exact-100 aggregation validation.
- Scheduled replacement check at `2026-08-02T00:23:48-07:00`: leaves 4 and 6 had left the queue,
  leaves 7-16 were `RUNNING` at full `%10` throttle, and leaves 17-100 remained pending for
  `JobArrayTaskLimit`. Both completed `0:0`: leaf 4/internal `23477613` in 3:37:34 with
  93,128,528 K MaxRSS, and leaf 6/internal `23477731` in 3:28:34 with 104,572,520 K MaxRSS,
  each against 150 GB. Their seed-10004/10006 stats records exist at SHA-256
  `efe3ff842245521d06fb4421d7d2f36e0582671b24255f36fe853fe898f0acb7` and
  `63c5d58d062053c5d90f932737cab93819db557e9a678cd8c313089445c8b6a9`, with exact locked
  schema/provenance. The campaign now has six candidates pending exact-100 validation.
- Scheduled replacement check at `2026-08-02T00:54:15-07:00`: leaves 7-8 had left the queue,
  leaves 9-18 were `RUNNING` at full `%10` throttle, and leaves 19-100 remained pending for
  `JobArrayTaskLimit`. Both completed `0:0`: leaf 7/internal `23477747` in 3:33:45 with
  105,966,376 K MaxRSS, and leaf 8/internal `23477802` in 3:12:22 with 81,714,888 K, each against
  150 GB. Their seed-10007/10008 records exist at SHA-256 `cb319f25b481f5f07603f923ddc45dce7b1c1ec6b5bd09b4028e3d40947b4fad`
  and `026c0b15891a0684d7ecc05b17d0135ddd184496fad987e16731ae08c88a3fa8`, with exact locked
  schema/provenance. Candidate count is eight pending exact-100 validation.
- Scheduled replacement check at `2026-08-02T01:24:50-07:00`: leaves 9-10 had left the queue,
  leaves 11-20 were `RUNNING` at full `%10` throttle, and leaves 21-100 remained pending for
  `JobArrayTaskLimit`. Both completed `0:0`: leaf 9/internal `23477803` in 4:00:09 with
  80,080,108 K MaxRSS, and leaf 10/internal `23477852` in 3:51:21 with 105,748,220 K MaxRSS,
  each against 150 GB. Their seed-10009/10010 records exist at SHA-256
  `548509d89dce7ecd61e35dae43ad18ad8d85c096cd4d563e4c9d76e89f6e1ac1` and
  `68d26830274bca72df3e99ce06ca0cb9cee25e0317c44e99770a3a5e5f3a15d1`, with exact locked
  schema/provenance. Candidate count is ten pending exact-100 validation.
- Resumed replacement check at `2026-08-02T14:50:56-07:00`: leaves 11-46 had left the queue,
  leaves 47-56 were `RUNNING` at full `%10` throttle, and leaves 57-100 remained pending for
  `JobArrayTaskLimit`. Authoritative `sacct` classified every leaf 11-46 `COMPLETED 0:0`, with
  elapsed times from 2:50:02 to 4:37:43 and batch MaxRSS from 78,719,148 K to 105,976,960 K
  against 150 GB. A bulk check of the exact 36 expected seed-10011 through seed-10046 stats
  records returned true: all split seeds were unique and complete across the range, with schema
  `olmt-forcing-surrogate-stats-v2` and the exact locked source/dependency/config hashes. Their
  individual SHA-256 values were also captured during the check. Candidate count is 46 pending
  exact-100 validation.
- Read-only aggregation readiness check at `2026-08-02T14:53:33-07:00`: canonical and submitted
  copies of `aggregate_iter001.slurm` and `aggregate_config.env` are byte-identical at SHA-256
  `c89206884ca34c046b3a4199e2b49fd743f0cf617d402d2405afccab0de9e9e9` and
  `c059962a8bb87c9bce381ec31c7b196d30fac9e0a966625b589b27c2311e1d0b`; Bash syntax passes;
  and all 30 entries in `iter001_source_manifest.sha256` verify. The aggregation submission gate
  remains closed until all 100 production leaves and records are terminal-success eligible.
- Full read-only candidate validation at `2026-08-02T14:56:07-07:00` returned
  `FULL_CANDIDATE_VALIDATION_PASS seeds=10001-10046 count=46`. In addition to exact file/seed and
  provenance identity, it recomputed every ordered-feature schema hash; checked the exact cases,
  target, split, output label, and repository commit; required finite pooled and ordered nine-site
  metrics/diagnostics with positive row counts; and required complete finite eight-repeat
  permutation importance in schema order. Eligibility remains provisional until the exact-100
  aggregation and independent aggregate validator pass.
- Read-only storage refresh at `2026-08-02T14:57:45-07:00`: `uquota` reported
  `/xdisk/chopinsong` at 17.0/19.5 TB. The complete coupling output tree used 6.8 GB and the
  prepared aggregation directory 16 KB, so the remaining aggregation/closeout artifacts have
  ample space on the selected output filesystem.
- Closeout-protocol audit found a non-self-referential identity inconsistency: the coupling
  `README.md` currently defines committed `registry.csv.closeout_identity` as the observed commit
  SHA, while `WORKFLOW.md` correctly prohibits editing tracked records to embed their own commit.
  A commit cannot contain its own SHA. Do not modify the locked workflow/source-manifest inputs
  before aggregation. After aggregate validation, apply the minimal lifecycle-only correction:
  record expected subject, parent HEAD, and controlled-path manifest before the one commit, then
  verify the observed SHA and those invariants from Git after commit without editing the commit.
- An unlocked two-phase handoff-validator scaffold was added at
  `slurm/iter001/validate_iter001_handoff.py`, current draft SHA-256 `27fb30d9...`, and passed a
  standard-library AST parse. It is intentionally absent from the active source manifest, so it
  does not alter production/aggregation provenance. The draft independently checks every record's
  full finite pooled/site diagnostics and permutation-importance structure. The final validator
  identity will be recorded only after aggregate-derived assertions and the controlled path set
  are fixed.
- Scheduled replacement check at `2026-08-02T15:20:49-07:00`: leaves 47-49 and 53 had left the
  queue, leaves 50-52 and 54-60 were `RUNNING` at full `%10` throttle, and leaves 61-100 remained
  pending for `JobArrayTaskLimit`. All four completed `0:0`: leaf 47/internal `23481135` in
  4:23:51 at 80,079,820 K MaxRSS; leaf 48/internal `23481399` in 3:39:30 at 80,123,948 K; leaf
  49/internal `23481432` in 3:14:33 at 79,368,644 K; and leaf 53/internal `23481618` in 2:33:19
  at 78,802,992 K, each against 150 GB. Their seed-10047/10048/10049/10053 records passed the full
  candidate gate at SHA-256 `8fd2cb122f2b8e97c73fadbaa3e997975da58ef8e32ab74da44a885e940b5f1e`,
  `0bea6df13b08e78b549f4eb3e58ee9a0a57d8a116991f12f49264bb2c320b518`,
  `71957231fb4aef395c528e06b5b0769971be13dff6f74f9dd316d095978bcaed`, and
  `a1f469c12eb713115e2aa95dcda6f78e410384b13692cc67ff4b525420aefe75`.
  Candidate count is 50 pending exact-100 validation.
- Failure, rejection, retry, or cancellation evidence: pilot `23467686` OOM; authorized corrected
  pilot `23473876` ended `FAILED 1:0` at the post-training validator; no cancellation or further
  retry occurred.
- Resume recovery at `2026-08-03T14:49:08-07:00` on `wentletrap.hpc.arizona.edu` after the prior
  Codex session stopped for usage limits. Groups `student,chopinsong` are present. Branch
  `feature/surrogate_coupling` remains at commit `2648998d...` with the expected uncommitted
  Iter001 worktree. The recorded kickoff package and amendments remain complete, unexhausted, and
  unchanged for aggregation through closeout.
- Terminal replacement accounting for array `23476164`: `squeue` reports the array absent after
  completion; authoritative `sacct` classifies every leaf `1-100` as `COMPLETED 0:0`. Batch-leaf
  summary: mean elapsed 3.46 h; shortest leaf 53 at 2.56 h / 75.2 GiB MaxRSS; longest leaf 74 at
  4.70 h / 75.7 GiB; highest MaxRSS leaf 28 at 3.62 h / 101.1 GiB against 150 GB. No post-start
  replacement leaf failed.
- Exact-100 eligibility validation at `2026-08-03T14:49:08-07:00` returned
  `FULL_CANDIDATE_VALIDATION_PASS seeds=10001-10100 count=100`. Every stats file matches the
  locked schema, split, cases, target, output label, repository commit, source manifest
  `1f71df1b...`, dependency `e718a00f...`, production config `ef9b837...`, recomputed ordered
  34-feature schema `cbe2daf...`, finite pooled/site diagnostics, and complete eight-repeat
  importance. Aggregate script/config remain byte-equal at `c892068...`/`c059962...`; all 30
  source-manifest hashes and aggregate Bash syntax pass. Aggregation submission is now open.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | job `23467631`, dependency manifest `e718a00f...`, seven tests passed | pass | all locked source, runtime, dependency, input, and schema checks passed |
| pilot | yes, by approved composite correction | training/artifacts from `23473876`; validation job `23475958` `COMPLETED 0:0`; `pilot_validation.json` `ef651685...` | pass | approved validation-only amendment combines the preserved successful training evidence with an independently completed validator; every artifact/data-integrity gate passes |
| production | yes | original array `23476014`: 15 OOM and 85 cancelled; approved replacement `23476164`: all 100 leaves `COMPLETED 0:0`; exact-100 eligibility pass at `2026-08-03T14:49:08-07:00` | pass | replacement terminal accounting and locked provenance/schema/metrics/importance completeness satisfy the functional production gate; failed first array remains classified historical evidence |
| aggregation | yes | job `23489654` `COMPLETED 0:0`; aggregate SHA `b75510b4...`; validation SHA `63a0b23b...`; gate `pass` | pass | exact-100 eligible records aggregated; tables/plots and independent aggregate validator passed |

- Objective label: Historical nine-site SR forcing-surrogate offline baseline
- Bounded scope label: Nine sites; SR; random_time_window; seeds 10001-10100; pooled/per-site metrics; eight-repeat pooled permutation importance; no coupling or saved-artifact inference
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter001`
- Dependency identities: source
  `1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6`; dependency
  `e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9`; production config
  `ef9b837bcdeb85ea96438ac6e9321a37623aa13ac9156d9ed96d5c942c104246`.
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Technical offline baseline validated; predictive quality characterized; coupling readiness not established
- Limitations: no saved-artifact inference or coupling validation is in scope.
- Aggregation submission: from the approved aggregate directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter001_aggregate/submission_config.env ./submit_aggregate_iter001.slurm </dev/null`
  returned `23489654` at `2026-08-03T14:49:51-07:00`. Immediate identity matched
  `sfc-i001-aggregate`, `chopinsong/standard`, one CPU/derived 5 GB, one-hour limit, and exact
  working directory/command/log paths.
- Aggregation result: `COMPLETED 0:0` on `r7u16n1` after `00:00:23`; batch MaxRSS `152168K`;
  `/usr/local/bin/seff` reports 8.85% CPU efficiency and 2.9% memory efficiency. Log records
  `AGGREGATION_PASS seeds=100 warning_fraction=0.000000` and `AGGREGATE_VALIDATION_PASS`.
- Predictive-quality characterization: pooled test R2 mean/median `0.945275` / `0.945557`;
  pooled test RMSE mean/median `0.210745` / `0.209810`; pooled R2 gap mean/median `0.012502` /
  `0.012155`; pooled RMSE ratio mean/median `1.254273` / `1.244005`; pooled overfitting warning
  fraction `0.0`. Top importance features by mean held-out RMSE increase include `TOTSOMN`,
  `k_s4`, `FSDS`, `FSDS_anom_30d`, and `rf_s3s4`.
- Next action: none; Iter001 closeout is complete. Treat the workflow as idle until a new
  consolidated kickoff package is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter001/validate_iter001_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent 2648998d4ceb08ecf72859a7d5200c0e3a5eb41d --expected-subject "Close Iter001
  historical forcing-surrogate offline baseline"`. Result:
  `PASS: Iter001 records, artifacts, accounting, and precommit closeout identity validated`.
  A one-line validator fix preserved porcelain leading spaces (`stdout.rstrip("\n")` instead of
  `strip()`), required for exact controlled-path comparison; the path remains outside the training
  source manifest.
- Closeout identity: controlled-path manifest SHA-256
  `034d2a350ebdacccb67ab972b933771ee96d85a2d0196f33c1e65660b81f1f35` over the 35 sorted controlled
  paths recorded in `summaries/iter001/iter001_decision.json`.
- Post-commit verification: same validator with `--phase postcommit` returned
  `PASS: Iter001 records, artifacts, accounting, and postcommit closeout identity validated`.
  The authorized local closeout branch is satisfied.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed before Iter001 evidence is evaluated.
No next iteration is proposed.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter001/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted at initialization
- [x] Authorized closeout branch satisfied: one verified local commit
