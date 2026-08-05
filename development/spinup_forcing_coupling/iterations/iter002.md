# iter002 - Forcing-Surrogate-v1 Full-Data Release

## Status

- Iteration ID: `iter002`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter002_preflight`,
  `spinup_forcing_coupling_iter002_release`, and
  `spinup_forcing_coupling_iter002_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-03T18:38:23-07:00`
- Closed: `2026-08-05T11:31:01-0700`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter001 closeout in
`handoff/CURRENT.md` and `iterations/iter001.md`, planning-body SHA-256
`229d87504ebf08307d613b21428317832ccd135762bd09ad14fe9bdf926ec9eb`.

- Sequential ID and work type: `iter002`; `implementation`.
- Objective: publish one trusted, versioned `forcing-surrogate-v1` artifact from a full-data
  refit under the locked Iter001 scientific configuration, with spinup-style saved-artifact
  inference validation and full-data in-sample feature-importance evidence.
- Upstream dependencies: closed Iter001 records/manifests; validated memmap/layout; pilot
  seed-`10001` stats/validation; nine case pickles; `OLMT_puma`; repository source locked at
  preparation.
- Bounded scope: public versioned loader/predict API; release tooling with reproduction gate,
  full-data refit, artifact/manifest/validation report, and full-data 8-repeat pooled
  permutation importance; fresh-process inference validation; iteration Slurm material and
  durable records. Exclusions: live coupling; 100-seed ensemble; feature selection/extra
  tuning; accuracy or coupling-readiness thresholds beyond functional/inference gates.
- Acceptance gates and decision rule: accounting; reproduction within `rtol=1e-10` /
  `atol=1e-8`; full-data importance; release artifact; inference; durable-record agreement.
  Pass means identity-locked inference-validated standalone artifact with full-data importance
  characterized; not live coupling readiness.
- Site and resources: Puma `chopinsong`/`standard`/`OLMT_puma`; preflight 1 CPU / derived 5 GB /
  15 min; release `--mem=120G`, `N_JOBS=4`, 10 h; validate 10 CPUs / derived ~50 GB / 1 h;
  independent review; one minimal preflight correction/rerun; one same-scope
  scheduler/resource retry per failed release or validate; bounded cancellation; stop after
  closeout branch.
- Evidence: versioned artifact, sidecars, importance products, gate JSON, public API/tests,
  Slurm material, four durable records, handoff validator.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approved, yes and yes.`; accepted `2026-08-03T18:38:23-07:00`. Interpretation: approve the package as written; authorize the three outside-sandbox authorities; authorize one local closeout commit. |
| Kickoff goal, finite work-unit count, and stop conditions | Publish identity-locked, inference-validated `forcing-surrogate-v1`; 3 nominal / 5 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md` SHA-256 `4391a6c4993a070687809eaece51eb718d2b8e58289a5b20c46ff4fd0c67d87b` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter002_preflight/`, `spinup_forcing_coupling_iter002_release/`, and `spinup_forcing_coupling_iter002_validate/`; retain validated artifact, manifest, validation report, importance tables/plots, submitted material, logs, and accounting; Iter001 memmap shared read-only; `/xdisk` temporary and unbacked; no Git of large binaries |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan above; Iter001 memmap SHA-256 `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout SHA-256 `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`; pilot validation SHA-256 `ef651685a8fbba6651a7b9fe465ef50b27a547d2fb1e3571a8f4a35241bdcc6f`; pilot stats SHA-256 `bbe1b51ece8567b54a8437a01f907506bd11658ea029506b638674c9fba5f0e8`; schema SHA-256 `cbe2daf49d74f5cc7b99caed138c8da314d42095cd8ea8a41cb762c903e93061`; repository commit and Iter002 source manifest locked during preparation |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, release, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 1 CPU / derived 5 GB / 15 min; release `--mem=120G` / `N_JOBS=4` / 10 h; validate `--cpus-per-task=10` (derived ~50 GB) / 1 h; one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed release or validate job; no automatic application/schema/numerical/OOM/timeout retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Locked `sbatch` and allowed resubmission; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits` throughout monitoring/accounting; bounded `scancel` as above |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, memmap, models, logs excluded; no push |


### Fresh Release-Retry Amendment

- User response: exact response approving the corrected consolidated retry package after
  clarifications (baseline = Iter001 100-seed aggregate distribution; metric comparison
  characterization only; full-data refit only; validate keeps existing operational/negative
  gates and adds ABBY random-parameter predict with draw seed 10001; resources unchanged);
  accepted `2026-08-04T16:48:00-07:00`.
- Authority: repair release/validate tooling; one release resubmit at `--mem=120G` /
  `N_JOBS=4` / 10 h; then amended validate; no further automatic numerical retry.
- Amended decision rule: release line passes on artifact write identity plus operational
  validation; full-data vs 100-seed baseline comparison is diagnostic only.
- Historical failure `23497577` remains classified evidence; submitted copies preserved as
  `*_job23497577.*`.

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Iter001 memmap | Feature matrix reuse | `.../iter001_pilot/surrogate_forcing/X_forcing_memmap.dat` | float32; 52,560,000 x 34 | 7,148,160,000 bytes; SHA-256 `01ef038f...` | Iter001 pilot/production validated; re-verify in preflight |
| Iter001 layout | Row/schema metadata | `.../X_forcing_memmap_layout.npz` | forcing layout | 73,374,948 bytes; SHA-256 `a6ea4151...` | Iter001 validated; schema `cbe2daf...` |
| Iter001 pilot stats | Reproduction reference | `.../surrogate_forcing_stats_pilot_seed10001_rs10001.json` | `olmt-forcing-surrogate-stats-v2` | SHA-256 `bbe1b51...` | Seed-10001 pooled metrics are reproduction-gate targets |
| Iter001 pilot validation | Artifact/provenance lock | `.../pilot_validation.json` | pilot-validation-v1 | SHA-256 `ef651685...` | Composite pilot gate pass |
| Nine case pickles | Input provenance | `pklfiles/*_ppe6_I20TRCNPRDCTCBC.pkl` | ordered `ensemble_parms` | hashes in `iter002_case_pickles.sha256` | Same trust model as Iter001 |
| Puma environment | Runtime | `OLMT_puma` | `micromamba/2.0.2-2` | locked at preparation/preflight | Iter001 compute-node validated |

- Repository commit: `ce2e252fefa1a200527d5cb4ecd20b62d6006f1c` on `feature/surrogate_coupling`
  (dirty bounded Iter002 worktree locked by source manifest).
- Bounded source manifest: `slurm/iter002/iter002_source_manifest.sha256` over the locked
  Iter002 controlled paths; regenerate with `sha256sum` and re-verify after any listed-path edit.
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`; exact package inventory pending
  compute-node preflight.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting for every task; reproduction,
  importance, release-artifact, and inference gate products; compact `summaries/iter002/`;
  four durable records agreeing after closeout validation.
- Acceptance gates: as finalized in the plan (accounting; reproduction; full-data importance;
  release artifact; inference; durable-record agreement).
- Decision rule: pass means the standalone full-data forcing artifact is identity-locked and
  inference-validated for later coupling development, with full-data importance characterized.
  No predictive-accuracy threshold. Pass does not claim live coupling readiness.
- Comparative aggregation: not required beyond full-data importance characterization.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change; disallowed retry;
  task beyond the 5-task hard cap; gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter002.slurm` / `a54d70b3...`; `preflight_config.env` / `bb078aed...` | byte-equal submitted copies in preflight run dir | `spinup_forcing_coupling_iter002_preflight/`; logs `preflight_23491474.{out,err}` | memmap/layout/pilot/case locks | commit `ce2e252...`; source manifest locked | `23491474` | `COMPLETED 0:0` end `2026-08-03T19:27:21-07:00`; `PREFLIGHT_PASS` | — |
| release | `release_iter002.slurm` / `055f7db5...`; `release_config.env` / `694fbe62...` | byte-equal submitted copies (historical `*_job23497577.*` preserved) | `spinup_forcing_coupling_iter002_release/`; logs `release_23501708.{out,err}` | amended full-data + 100-seed baseline characterization; preflight `f39e7d6f...` | commit `ce2e252...`; source manifest locked | `23501708` (prior fail `23497577`) | amended `COMPLETED 0:0` 05:45:37; MaxRSS 95.31/120 GB; `ITER002_RELEASE_OK` artifact `8d139b32...` | prior `23497577` failed reproduction; amendment authorized |
| validate | `validate_iter002.slurm` / `1a97bb61...`; `validate_config.env` / `5c98eccc...` | byte-equal submitted copies in validate run dir | `spinup_forcing_coupling_iter002_validate/`; logs `validate_23507103.{out,err}` | release artifact + importance sidecars | commit `ce2e252...`; source manifest locked | authoritative `23507103` | `COMPLETED 0:0` 00:01:02; `ITER002_VALIDATE_OK` | accidental duplicates `23507104`/`23507109` completed identical; pending `23507128`/`23507129` cancelled |

## Independent Read-Only Review

- Reviewer: independent read-only agent `acdd641c-09fb-4aab-a635-e1f46bdf5191`
  (composer-2.5-fast); review completed `2026-08-03T19:10:00-07:00`.
- Reviewed source hash: source-manifest file SHA-256
  `e00abd3231ca2c98596920d63c71194ae23f3ef4bfde575efa5c66acdd140d10`.
- Outcome: `pass_with_concerns`.
- Release readiness re-review: independent agent `bfd69a05-0e8d-4738-99aa-4ea962cd37ff`
  at `2026-08-04T12:42:00-07:00`; outcome `pass`; release script SHA-256 `d26a7103e43f44094550d5ebc6fa7315ee3b33e9970e6f6d6ef2bf062cd14bce`;
  config `c061db9bfafd30c78bb016dd85acfe673d3e896a7caed96be34575c04be9ccc8`; GO for sbatch.
- Findings and primary-agent response: no blockers. Low concerns were (1) 15-minute
  preflight may be tight because it SHA-256s the 7.1 GB memmap and nine case pickles;
  (2) release 120 GB thin headroom; (3) release/validate are process-gated only. Primary
  proceeds with the locked 15-minute preflight; if authoritative `TIMEOUT`, use the one
  authorized minimal preflight correction/rerun after recording evidence. Release MaxRSS
  will be monitored; release/validate remain process-gated on prior terminal pass.
- Post-review durable-record refresh: regenerated `iter002_source_manifest.sha256` after
  recording review text; execution scripts/configs/submitted copies unchanged. Verify with
  `sha256sum -c development/spinup_forcing_coupling/slurm/iter002/iter002_source_manifest.sha256`
  immediately before submission.

## Execution and Diagnostics

- Pre-review source lock: `sha256sum -c development/spinup_forcing_coupling/slurm/iter002/iter002_source_manifest.sha256` must pass before submission.
- Static validation at `2026-08-03T19:04:08-07:00`: `python3 -m py_compile` passed for
  artifact/release/validate/preflight/test modules; `bash -n` passed for all three Slurm
  scripts; `sha256sum -c` passed for the source manifest; all six canonical/submitted
  script/config pairs are byte-equal; prohibited Puma directives absent; repository HEAD
  matches locked `REPOSITORY_COMMIT`.
- Public API and tools created: `model_ELM/forcing_surrogate_artifact.py`;
  `tools/release_forcing_surrogate.py`; `tools/validate_iter002_release.py`;
  `tests/test_forcing_surrogate_iter002.py`; canonical Iter002 Slurm material.
- Preflight: pending independent review, then submission
- Exact submission command: preflight from approved preflight directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_preflight/preflight_submission_config.env ./submit_preflight_iter002.slurm </dev/null`;
  returned `23491474` at `2026-08-03T19:21:17-07:00`.
- Immediate identity: `sfc-i002-preflight`, `chopinsong/standard`, 1 CPU / derived 5 GB,
  15-minute limit, exact workdir/command/log paths, `PENDING (Priority)`.
- Preflight terminal accounting: authoritative `sacct` `COMPLETED 0:0` elapsed `00:01:18`
  on `r4u10n1`; batch MaxRSS `5241884K`; `/usr/local/bin/seff` 47.73% CPU efficiency and
  99.98% memory efficiency of 5 GB. Log records tests OK and `PREFLIGHT_PASS cases=9`;
  preflight-manifest SHA-256 `f39e7d6f1e895b00d123da09ed926bf68abf34ee625a6c8a5b1ddd71ea3d8ca9`.
- Exact submission command: release from approved release directory,
  `/usr/bin/sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/release_submission_config.env ./submit_release_iter002.slurm </dev/null`;
  returned `23497577` at `2026-08-04T12:40:21-07:00`.
- Immediate release identity: `sfc-i002-release`, `chopinsong/standard`, 120 GB deriving
  24 CPUs, 10-hour limit, exact workdir/command/log paths, `PENDING (Priority)`.
- Exact amended release submission: returned `23501708` at `2026-08-04T16:50:32-07:00` from release run dir with
  `SUBMISSION_CONFIG=.../release_submission_config.env`; identity `sfc-i002-release`,
  120 GB/24 CPUs, 10 h, `PENDING (Priority)`.
- Exact validate submission: returned authoritative `23507103` at `2026-08-05T11:23:08-07:00`
  from validate run dir with `SUBMISSION_CONFIG=.../validate_submission_config.env`;
  identity `sfc-i002-validate`, 10 CPUs / derived 50 GB, 1 h.
- Accidental duplicate validate submits `23507104`, `23507109`, `23507128`, `23507129`
  occurred during an interrupted agent update/submit step; pending duplicates cancelled.
- Release failure classification: application/numerical failure at the reproduction gate,
  not scheduler/resource/OOM/timeout. Authoritative `sacct` `FAILED 1:0` elapsed
  `03:01:25` on `r3u12n1`; batch MaxRSS `96020688K` (~91.57 GB) against 120 GB
  (76.31% memory efficiency). Stderr:
  `ValueError: Reproduction mismatch SR.r2_train: observed=0.9499368935897443, expected=0.9613383558172671`.
  Expected pilot best_params were
  `{activation: relu, alpha: 1e-4, hidden_layer_sizes: [128], learning_rate: adaptive, solv## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | job `23491474` `COMPLETED 0:0`; `PREFLIGHT_PASS`; manifest `f39e7d6f...` | pass | imports, case/memmap/layout/pilot identity, synthetic API fixture, and tests passed |
| release (historical) | yes (classified fail) | job `23497577` `FAILED 1:0`; reproduction mismatch; MaxRSS 91.57/120 GB | fail | numerical reproduction gate failed under original package; not resource failure |
| release (amended) | yes | job `23501708` `COMPLETED 0:0` 05:45:37; MaxRSS 95.31/120 GB; `ITER002_RELEASE_OK`; artifact `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | pass | full-data fit + importance + pre/post-load identity; 100-seed baseline comparison characterization only |
| validate | yes | authoritative job `23507103` `COMPLETED 0:0` 00:01:02; `ITER002_VALIDATE_OK`; inference summary `44e493d65b770aedec83ef2d75978c2ff7857f49fe0c79550df848c87af3c20e` | pass | manifest/fresh-process/negative gates/batch predict and ABBY operational predict passed |

- Objective label: Identity-locked forcing-surrogate-v1 full-data release with inference validation
- Bounded scope label: Nine sites; SR; full-data forcing-surrogate-v1; 8-repeat full-data importance; inference validation; ABBY operational predict; no live coupling
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter002`
- Dependency identities: release-time source-manifest file SHA-256 `ea7ec3f35b452c78b21ac710079004dcd083867c95d4262342c6bc4a8bf46ab2`;
  memmap `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`; artifact `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; inference
  summary `44e493d65b770aedec83ef2d75978c2ff7857f49fe0c79550df848c87af3c20e`; importance JSON `703197af132dd44b29339fd9c84f8917253cec47f151d2012a512259d8ef3c0b`; baseline comparison
  `65cc33449eb6386496ea1dd75abdde9333db4ec43564f3b98f403584fdc6fd50`; Iter001 aggregate baseline `b75510b4f1fc64109d5be942e93d4af1662bd1c7a2a07c565f065245ce69f0a3`.
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Standalone forcing-surrogate-v1 artifact identity-locked and inference-validated; full-data importance characterized; live coupling readiness not established
- Quantitative characterization (not pass/fail thresholds): full-data in-sample r2=`0.957720`
  rmse=`0.170592` (rows=`52560000`); vs 100-seed train-r2 mean `0.957777` (delta
  `-5.6e-5`). Top full-data in-sample importance by mean RMSE increase: `TOTSOMN`,
  `FSDS`, `k_s4`, `FSDS_anom_30d`, `rf_s3s4`.
- Amended release terminal accounting: job `23501708` `COMPLETED 0:0` elapsed 05:45:37
  end `2026-08-04T22:42:28` on `r4u39n2`; seff mem 79.42% of 120 GB / CPU 9.25%; markers
  `FULL_DATA_FIT_OK`, `BASELINE_COMPARISON_RECORDED`, `FULL_DATA_IMPORTANCE_PASS`,
  `ITER002_RELEASE_OK`.
- Validate terminal accounting: authoritative job `23507103` `COMPLETED 0:0` elapsed
  00:01:02 on `r4u06n1`; MaxRSS ~5.61 GB / 50 GB; seff mem 11.22%. Accidental multi-submit
  produced completed duplicates `23507104` and `23507109` with byte-identical stdout to the
  authoritative log, plus pending `23507128`/`23507129` cancelled at `2026-08-05T11:28:19`
  after user-directed fix (risk of overwriting authenticated summary after gate pass).
  Hard-cap note: authorized substantive tasks remained within the 5-task hard cap;
  duplicates are classified unauthorized extras, not approved work units.
- Limitations: `/xdisk` retention temporary/unbacked; no live spinup–forcing coupling; full-data
  importance is in-sample characterization only; original seed-10001 reproduction gate was
  amended to characterization-only baseline comparison under approved release-retry package.
- Next action: none; Iter002 closeout is complete. Treat the workflow as idle until a new
  consolidated kickoff package for `iter003` is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter002/validate_iter002_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent ce2e252fefa1a200527d5cb4ecd20b62d6006f1c --expected-subject "Close Iter002
  forcing-surrogate-v1 full-data release"`. Result:
  `PASS: Iter002 records, artifacts, accounting, and precommit closeout identity validated`.
- Closeout identity: controlled-path manifest SHA-256
  `a19ff37aae6ca6397cf53738e337c92516bdadfa602ef2a2f7fc150534c167e5` over the sorted controlled
  paths recorded in `summaries/iter002/iter002_decision.json`.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter003`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter003`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter003_preflight`,
  `spinup_forcing_coupling_iter003_bridge`, and
  `spinup_forcing_coupling_iter003_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: couple the closed Iter002 `forcing-surrogate-v1` artifact with an existing
locked spinup-surrogate artifact to produce and validate real forcing-target (`SR`)
predictions through the forcing bridge, replacing design-matrix-only bridge checks.

Evidence basis: Iter002 closed `pass` with identity-locked full-data artifact
SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` and
inference/`ABBY` operational validation; spinup handoff still records forcing-bridge
checks as column-order/shape/dtype only, awaiting a real forcing artifact.

Optional hypothesis: loading both versioned artifacts and exercising the bridge on a
bounded site/member fixture is sufficient to establish an executable coupling path
without MCMC, PPE sweeps, or accuracy thresholds.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Closed Iter002 artifact/manifest/validation/importance | Forcing surrogate | Immutable read-only; lock artifact SHA-256 `8d139b32...` |
| Closed Iter001 memmap/layout (if still needed for fixtures) | Optional fixture support | Read-only; reuse locked hashes only if required |
| Locked spinup-surrogate release named at kickoff | Spinup state surrogate | Immutable; exact path/hash chosen in kickoff package |
| `forcing_surrogate_artifact` / spinup loader APIs | Public load/predict | Repository commit and source manifest locked at preparation |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

In scope: wire real forcing-surrogate predictions into the forcing bridge; bounded
preflight; one bridge execution work unit on a declared site/member/fixture; positive
and negative gates for schema/version/load failures; durable records and closeout.

Exclusions: MCMC/PPE campaigns; accuracy or coupling-readiness numeric thresholds beyond
functional/inference integrity; retraining either surrogate; feature selection; expanding
beyond the kickoff-declared fixture set.

Nominal scheduler tasks: 3. Provisional hard cap: 5.

### 5. Tentative acceptance gates and decision rule

Pass only if terminal accounting exists; both artifacts load under their versioned APIs;
bridge returns finite `SR` for the declared fixture; negative gates fail closed; durable
records agree after handoff validation. Pass means an executable forcing–spinup coupling
path is demonstrated on the fixture; it does not claim production MCMC readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter003_{preflight,bridge,validate}/` |
| Preflight / bridge / validate | finalize exact CPU/mem/time at kickoff from fixture size |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed bridge/validate; no automatic application/numerical retry |
| Cancellation | recorded Iter003 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

Bridge prediction/report JSON under the approved Iter003 run dirs; compact
`summaries/iter003/`; finalized `iterations/iter003.md`; `ITERATION_SUMMARY.md` append;
`registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result.

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter003 initialization.


## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter002/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: precommit validated; postcommit verification pending until commit
