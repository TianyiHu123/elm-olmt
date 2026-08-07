# iter005 - Mean-spinup offline baseline vs Iter004 arms

## Status

- Iteration ID: `iter005`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter005_preflight`,
  `spinup_forcing_coupling_iter005_full`, and
  `spinup_forcing_coupling_iter005_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-06T18:53:00-0700`
- Closed: `2026-08-06T19:42:02-0700`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter004 closeout in
`handoff/CURRENT.md` and `iterations/iter004.md`, planning-body SHA-256
`e98eaadfa368b66d9e039adb032031019c2ffcc50b545c25fa9096f00a7cbc7b`.

- Sequential ID and work type: `iter005`; `implementation`.
- Objective: nine-site × 100-member offline forcing-surrogate-v1 campaign using historical
  MCMC-default site-mean ELM restart spinup (`mean_spinup_state`; spinup fixed, parameters
  member-specific); publish timeseries and SR-versus-member plots overlaying ELM, this
  mean-spinup offline arm, and Iter004's three arms with site member-median Pearson r and
  KGE annotations; write `iter005_site_metric_medians.csv` joining Iter004 medians.
  Minimize new repository code.
- Optional hypothesis: coupled-versus-mean-spinup-offline is the MCMC-relevant skill
  comparison; member-restart offline remains the Iter004 oracle baseline. MCMC wiring
  deferred to proposed `iter006`.
- Upstream dependencies: Iter002 forcing artifact; nine I20TR cases; closed Iter004
  full/summary products (read-only reuse); existing inference/eval tooling; `OLMT_puma`.
- Bounded scope: new compute = mean-spinup offline only (9×100, timeseries ON); reuse
  Iter004 arms without re-run; two annotated plots per site; joined medians CSV;
  preflight → full array `1-9` → validate. Exclusions: MCMC campaign/wiring; re-running
  Iter004 arms; retraining; feature selection; numeric skill floors; SR-versus-TOTSOM
  plots; Git of large binaries/NetCDF.
- Acceptance gates and decision rule: accounting; 9×100 completeness with metrics and
  timeseries; both plot types for all nine sites with overlays and r/KGE annotations;
  joined medians CSV; fail-closed integrity gates; durable-record agreement. Pass means
  MCMC-relevant mean-spinup offline baseline compared with Iter004 arms under the locked
  plot/summary contract; not production MCMC readiness; no accuracy threshold.
- Site and resources: Puma `chopinsong`/`standard`/`OLMT_puma`; preflight 2 CPUs / 30 min;
  full `--mem=20G` / 4 h array `1-9`; validate 1 CPU / 1 h; independent review; one
  preflight correction/rerun; one same-scope full/validate retry; bounded cancellation.
- Evidence: mean-spinup offline products, annotated plots, joined summary CSV, Slurm,
  four durable records, handoff validator.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approve complete package: plan + contract + outside sandbox authority + comit permission`; accepted `2026-08-06T18:53:00-0700`. Interpretation: approve the complete consolidated package including plan, runtime contract, outside-sandbox items 1–3, and one local closeout commit. |
| Kickoff goal, finite work-unit count, and stop conditions | Mean-spinup offline baseline vs Iter004 arms with metrics, timeseries, and locked plots/summary; 3 nominal / 5 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter005_{preflight,full,validate}/`; `/xdisk` temporary and unbacked; no Git of large binaries/NetCDF |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan above; forcing SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; closed Iter004 products for reuse; nine I20TR pickles; 100 members; mean-spinup offline only for new compute; scores characterization only |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, full, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs (derived ~10 GB) / 30 min; full array `1-9` `--mem=20G` / 4 h per leaf; validate 1 CPU (derived ~5 GB) / 1 h; one minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or validate; no automatic application/schema/numerical retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Granted: locked `sbatch` and allowed resubmission; job-scoped `squeue`/`scontrol show job`/`sacct`/`seff`/`job-history`/`job-limits`; bounded `scancel` for recorded Iter005 job IDs under contract cancellation conditions |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, NetCDF, models, logs excluded; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Forcing surrogate | Offline `SR` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release + validate pass |
| Iter004 full products | Overlay arms + join | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter004_full` | Iter004 eval schema | `iter005_iter004_reuse.sha256` | Iter004 closeout pass |
| Iter004 summary medians | CSV join | `development/spinup_forcing_coupling/summaries/iter004/iter004_site_metric_medians.csv` | Iter004 | tracked | Iter004 closeout |
| Nine case pickles | Cases / parms / ELM | `pklfiles/*_ppe6_I20TRCNPRDCTCBC.pkl` | 100 members | hashes in `iter005_case_pickles.sha256` | Same trust as Iter004 |

- Repository commit: `9a125ef3a703e1169e831f77a04636c344359024` on `feature/surrogate_coupling`
  (dirty bounded Iter005 worktree locked by source manifest).
- Bounded source manifest: `slurm/iter005/iter005_source_manifest.sha256`
  (file SHA-256 `8f9a892da36074da10aac937439c37ffc8c5b093cf67698da6b506d714217019`).
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting; full 9×100 mean-spinup products
  with timeseries and both annotated plot types; joined `iter005_site_metric_medians.csv`;
  compact `summaries/iter005/`; four durable records agreeing after closeout validation.
- Acceptance gates: as finalized in the plan.
- Decision rule: pass means MCMC-relevant mean-spinup offline baseline compared with
  Iter004 arms under the locked plot/summary contract. No predictive-accuracy threshold.
  Pass does not claim production MCMC readiness.
- Comparative aggregation: per-site medians over members for mean-spinup offline; Iter004
  three-arm medians joined from locked Iter004 summary.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change; disallowed retry;
  task beyond the 5-task hard cap; gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter005.slurm`; `preflight_config.env` | byte-equal submitted copies in run dir | `spinup_forcing_coupling_iter005_preflight/`; logs `preflight_23516340.{out,err}` | forcing + cases + Iter004 reuse manifests | commit `9a125ef...`; source-manifest file `8f9a892d...` | authoritative `23516340` | `COMPLETED 0:0` elapsed 00:00:58; MaxRSS ~10.0/10 GB; `PREFLIGHT_PASS` | — |
| full | `full_iter005.slurm`; `full_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter005_full/`; logs `full_23516376_%a.{out,err}` | preflight `23516340` pass | same | `23516376` array `1-9` | all leaves `COMPLETED 0:0`; leaf elapsed max 00:12:12; MaxRSS max ~5.38/20 GB; `FULL_LEAF_PASS` | timeseries ON |
| validate | `validate_iter005.slurm`; `validate_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter005_validate/`; logs `validate_23516504.{out,err}` | full pass | same | authoritative `23516504` | `COMPLETED 0:0` elapsed 00:00:11; MaxRSS ~22 MB; `VALIDATE_PASS` | — |

## Independent Read-Only Review

- Reviewer: independent read-only agent `f6df5d44-613a-47bb-a069-f87f160112c3`
  (inherit); review completed `2026-08-06T19:05:30-0700`.
- Reviewed source hash: source-manifest file SHA-256
  `8f9a892da36074da10aac937439c37ffc8c5b093cf67698da6b506d714217019`.
- Outcome: `pass_with_concerns`.
- Findings and primary-agent response: no blockers. Concerns: (1) planning-body SHA
  fingerprint disputed by reviewer under an alternate section-hash convention; body SHA
  `e98eaadfa368b66d9e039adb032031019c2ffcc50b545c25fa9096f00a7cbc7b` was verified
  identical between closed Iter004 report and CURRENT at bootstrap, and material plan
  content matches prepared scripts — retain body SHA, proceed. (2) ledger hash field
  updated. (3) validate checks plot existence, not annotation text — accepted;
  annotations are written by the eval client. (4) full/validate do not re-hash
  forcing/Iter004 reuse — accepted for contiguous preflight→full→validate. Primary
  proceeded to preflight submission.

## Execution and Diagnostics

- Static validation: `bash -n` on Slurm scripts; `py_compile` on Python sources; source
  manifest `sha256sum -c` OK; independent review `pass_with_concerns`.
- Preflight: authoritative `23516340` `COMPLETED 0:0` elapsed 00:00:58; MaxRSS ~10.0/10 GB;
  `PREFLIGHT_PASS` (unit tests + artifact/case/Iter004-reuse identity).
- Full array `23516376` tasks 1–9: all `COMPLETED 0:0` with `FULL_LEAF_PASS`; leaf elapsed
  max 00:12:12; MaxRSS max ~5.38/20 GB; timeseries ON.
- Validate `23516504`: `COMPLETED 0:0` elapsed 00:00:11; MaxRSS ~22 MB; `VALIDATE_PASS`
  (9 sites; 900 member-rows; joined site-median CSV written).
- Failure classification: none.
- Cancellation evidence: none.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | authoritative `23516340` `COMPLETED 0:0`; `PREFLIGHT_PASS` | pass | imports, mean-spinup unit test, artifact/case/reuse identity |
| full | yes | array `23516376` leaves 1–9 all `COMPLETED 0:0`; `FULL_LEAF_PASS`; timeseries ON; annotated plots present | pass | 9×100 mean-spinup complete with Iter004 overlays |
| validate | yes | job `23516504` `COMPLETED 0:0`; `VALIDATE_PASS`; joined site medians + decision written | pass | accounting/completeness/integrity gates only |

- Objective label: Mean-spinup offline forcing baseline versus Iter004 arms
- Bounded scope label: Nine sites; mean-spinup offline 9×100 timeseries ON; overlay Iter004 three arms; two annotated plot types; joined medians CSV; no skill floor
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter005`
- Dependency identities: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Mean-spinup offline baseline compared with Iter004 arms under locked plot/summary contract; predictive scores characterized; production MCMC readiness not established
- Quantitative characterization (not pass/fail thresholds): site-median of per-site
  member-medians — offline_mean_spinup median R²≈-1.894 KGE≈0.438; Iter004 offline
  median R²≈0.850 KGE≈0.862; drop32 median R²≈0.579 KGE≈0.821; drop21_corr080 median
  R²≈0.651 KGE≈0.816; Pearson r remains high (~0.925) for mean-spinup. Compact table:
  `summaries/iter005/iter005_site_metric_medians.csv`.
- Limitations: `/xdisk` retention temporary/unbacked; predictive skill is characterization
  only; mean-spinup offline skill is substantially worse than member-restart offline and
  worse than coupled arms on R²/KGE at most sites; production MCMC readiness not established.
- Next action: none; Iter005 closeout records are complete. Treat the workflow as idle until
  a consolidated kickoff package for `iter006` is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter005/validate_iter005_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent 9a125ef3a703e1169e831f77a04636c344359024 --expected-subject "Close Iter005
  mean-spinup offline baseline comparison"`. Result:
  `PASS: Iter005 records, artifacts, accounting, and precommit closeout identity validated`.
- Closeout identity: controlled-path manifest SHA-256
  `45039a40b7abef1a99211e419638bee6cf3cc63e1e859e8d84e1d029a5a94f9e` over the sorted controlled
  paths recorded in `summaries/iter005/iter005_decision.json`.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter006`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter006`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter006_preflight`,
  `spinup_forcing_coupling_iter006_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: integrate the locked `predict_coupled_sr` primitive into the production MCMC
path in `optimize_surrogate_forcing.py` (or the minimal shared helper it already uses) so
a single CLI/config switch selects among three parallel spinup modes — offline mean-spinup,
offline member-restart, and coupled spinup→forcing — without a PPE campaign. Adding coupled
must not break existing mean-spinup or member-restart behavior. Prove the wiring with a
bounded compute-node preflight plus a short ABBY smoke that exercises all three modes
(collocation dry-run + ≤10 likelihood evaluations per mode, then exit); do not run a
production MCMC campaign.

Evidence basis: Iter003–Iter004 delivered coupled and offline comparison APIs; Iter005
showed mean-spinup offline (historical MCMC default) is the skill-relevant baseline and
lags both member-restart offline and coupled arms on R²/KGE. Production MCMC readiness
remains unestablished until the sampler can call the same primitives under an explicit
mode switch.

Optional hypothesis: exposing all three modes through the existing MCMC likelihood
interface is sufficient for a later campaign iteration; no retraining is required for
wiring correctness.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Offline/coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop32` and `drop21_corr080` | Coupled state; both selectable | Immutable Iter012 hashes locked at kickoff; smoke default `drop21_corr080` |
| `predict_offline_sr` / `predict_coupled_sr` / `mean_spinup_state` | Likelihood primitives | Lock repository identity at kickoff |
| Existing MCMC mean / `--spinup-member` paths | Regression baselines | Must remain selectable and smoke-verified |
| Closed Iter005 characterization | Motivates mean-spinup as default mode | Read-only |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work: MCMC wiring/integration only — one CLI/config switch for spinup mode with
three parallel options (`mean_spinup` offline, `member_restart` offline, `coupled`);
coupled variant selectable as `drop32` or `drop21_corr080` with default `drop21_corr080`;
keep historical default mode = mean-spinup when no mode flag is set; unit tests covering
mode selection and non-regression of mean/member-restart; one preflight; one ABBY smoke
validate that runs all three modes with a tiny evaluation budget (≤10 likelihood
evaluations per mode after collocation dry-run).

Exclusions: production MCMC campaign; multi-site PPE sweeps; retraining; feature
selection; numeric skill floors; re-running Iter004/Iter005 comparison campaigns; Git of
large binaries/NetCDF/chains.

Nominal scheduler tasks: 2 (preflight, validate/smoke). Provisional hard cap: 4 (one
minimal preflight correction/rerun; one same-scope scheduler/resource retry).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. MCMC path can invoke all three modes (`mean_spinup`, `member_restart`, `coupled`)
   through the locked interface without schema/import failures; coupled accepts both
   `drop32` and `drop21_corr080` with default `drop21_corr080`.
3. ABBY smoke completes the declared tiny evaluation budget for all three modes and
   writes a compact identity summary under `summaries/iter006/`.
4. Negative gates for missing artifact/schema/version failures fail closed.
5. Compact `summaries/iter006/` and the four durable records agree after handoff validation.

Decision rule: pass means MCMC can select and call the locked coupling/offline
primitives under each declared spinup mode, and existing mean/member-restart paths still
work. Pass does not claim a calibrated posterior or production campaign readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter006_{preflight,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Validate/smoke | 1 CPU (derived ~5 GB) / 1 h; site `ABBY`; ≤10 likelihood evals per mode |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry; no automatic application/numerical retry |
| Cancellation | recorded Iter006 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- MCMC wiring diff with tests covering three-mode selection and mean/member-restart
  non-regression; coupled variant switch (`drop32` / `drop21_corr080`, default
  `drop21_corr080`)
- Compact `summaries/iter006/` smoke identity for all three modes; finalized
  `iterations/iter006.md`; `ITERATION_SUMMARY.md` append; `registry.csv` row; rebuilt
  `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter006/` (created only after kickoff approval)
- After Iter006 closeout, next planning-only proposal is a production MCMC campaign only if
  wiring gates pass; otherwise a repair iteration

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter006 initialization.


## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter005/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
