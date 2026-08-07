# iter004 - Offline vs Coupled Surrogate Comparison

## Status

- Iteration ID: `iter004`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter004_preflight`,
  `spinup_forcing_coupling_iter004_full`, and
  `spinup_forcing_coupling_iter004_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-06T16:40:50-0700`
- Closed: `2026-08-06T17:59:11-0700`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter003 closeout
revision in `handoff/CURRENT.md` and `iterations/iter003.md`, planning-body SHA-256
`14b0df927e297fc204198f5073b4eb958c44bd59b1cf0f15810c994191845a83`.

- Sequential ID and work type: `iter004`; `implementation`.
- Objective: compare offline forcing-surrogate-v1 (ELM restart spinup) versus coupled
  spinup→forcing (`drop32` and `drop21_corr080`) on nine I20TR sites × 100 PPE members;
  save metrics and timeseries; publish the locked four-figure plot package vs ELM `SR`.
- Upstream dependencies: Iter002 forcing artifact; Iter012 drop32/drop21; nine cases;
  Iter003 coupled API plus offline predict path; `OLMT_puma`.
- Bounded scope: offline + both coupled arms; timeseries ON; no pilot; preflight → full
  array `1-9` → validate; metrics characterization only; plot package as locked.
  Exclusions: MCMC campaign/wiring (deferred to `iter005`); retraining; skill floors;
  Git of large binaries/NetCDF.
- Acceptance gates and decision rule: accounting; 9×100 completeness with metrics and
  timeseries; plot package complete; negative fail-closed gates; durable-record agreement.
  Pass means executable offline-vs-coupled comparison evidence; not production MCMC readiness.
- Site and resources: Puma `chopinsong`/`standard`/`OLMT_puma`; preflight 2 CPUs / 30 min;
  full `--mem=20G` / 4 h array `1-9`; validate 1 CPU / 1 h; independent review; one
  preflight correction/rerun; one same-scope full/validate retry; bounded cancellation.
- Evidence: offline path, evaluation client, metrics, NetCDF, plots, summaries, Slurm,
  four durable records, handoff validator.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `compelete package approved: plan + contract + outside sandbox authority.`; accepted `2026-08-06T16:40:50-0700`. Interpretation: approve the complete consolidated package including plan, runtime contract, and outside-sandbox items 1–3. |
| Kickoff goal, finite work-unit count, and stop conditions | Offline-vs-coupled ELM `SR` comparison with metrics, timeseries, and locked plots; 3 nominal / 5 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter004_{preflight,full,validate}/`; `/xdisk` temporary and unbacked; no Git of large binaries/NetCDF |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan above; forcing SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; nine I20TR pickles; 100 members; scores characterization only |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, full, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs (derived ~10 GB) / 30 min; full array `1-9` `--mem=20G` / 4 h per leaf; validate 1 CPU (derived ~5 GB) / 1 h; one minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or validate; no automatic application/schema/numerical retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Granted: locked `sbatch` and allowed resubmission; job-scoped `squeue`/`scontrol show job`/`sacct`/`seff`/`job-history`/`job-limits`; bounded `scancel` for recorded Iter004 job IDs under contract cancellation conditions |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, NetCDF, models, logs excluded; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Forcing surrogate | Offline and coupled `SR` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release + validate pass |
| Spinup `drop32` | Coupled state | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl` | `spinup-surrogate-v1` | SHA-256 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e` | Iter012 release |
| Spinup `drop21_corr080` | Coupled compact state | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `spinup-surrogate-v1` | SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | Iter012 release |
| Nine case pickles | Cases / parms / ELM | `pklfiles/*_ppe6_I20TRCNPRDCTCBC.pkl` | 100 members | hashes in `iter004_case_pickles.sha256` | Same trust as Iter003 |

- Repository commit: `6d8391443bbd0a2612e66e17c47414a896e2ab01` on `feature/surrogate_coupling` (dirty bounded Iter004 worktree locked by source manifest).
- Bounded source manifest: `slurm/iter004/iter004_source_manifest.sha256`.
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting; full 9×100×3-arm products with
  timeseries and plots; compact `summaries/iter004/`; four durable records agreeing after
  closeout validation.
- Acceptance gates: as finalized in the plan.
- Decision rule: pass means executable offline-vs-coupled comparison with ELM evidence.
  No predictive-accuracy threshold. Pass does not claim production MCMC readiness.
- Comparative aggregation: per-site medians over members by arm in summary report.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change; disallowed retry;
  task beyond the 5-task hard cap; gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter004.slurm`; `preflight_config.env` | byte-equal submitted copies in run dir | `spinup_forcing_coupling_iter004_preflight/`; logs `preflight_23515370.{out,err}` | locked artifacts/cases | commit `6d83914...`; source-manifest file `335e318f...` | authoritative `23515370` | `COMPLETED 0:0` elapsed 00:01:40; MaxRSS ~10.0/10 GB; `PREFLIGHT_PASS` | — |
| full | `full_iter004.slurm`; `full_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter004_full/`; logs `full_23515500_%a.{out,err}` | preflight `23515370` pass | same | `23515500` array `1-9` | all leaves `COMPLETED 0:0`; leaf elapsed max 00:48:51; MaxRSS max ~5.33/20 GB; `FULL_LEAF_PASS` | timeseries ON |
| validate | `validate_iter004.slurm`; `validate_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter004_validate/`; logs `validate_23515820.{out,err}` | full pass | same | authoritative `23515820` | `COMPLETED 0:0` elapsed 00:00:10; MaxRSS ~17 MB; `VALIDATE_PASS` | — |

## Independent Read-Only Review

- Reviewer: independent read-only agent `b170e0ac-beba-4dc6-b0fc-8371bd372af9`
  (inherit); review completed `2026-08-06T16:44:24-0700`.
- Reviewed source hash: source-manifest file SHA-256
  `335e318f5938f94dc5d4d57174cf001af6a5a544e609fb1002c62c93c906fde2`.
- Outcome: `pass_with_concerns`.
- Findings and primary-agent response: no blockers. Concerns: ledger still said
  pending materialization (updated now); preflight does not import the evaluate client
  (accepted — unit tests + py_compile cover primitives; full job exercises the client).
  Primary proceeds to preflight submission.

## Execution and Diagnostics

- Static validation: `bash -n` on Slurm scripts; `py_compile` on Python sources; source
  manifest `sha256sum -c` OK; independent review `pass_with_concerns`.
- Preflight: authoritative `23515370` `COMPLETED 0:0` elapsed 00:01:40; MaxRSS ~10.0/10 GB;
  `PREFLIGHT_PASS` (unit tests + artifact/case identity).
- Full array `23515500` tasks 1–9: all `COMPLETED 0:0` with `FULL_LEAF_PASS`; leaf elapsed
  max 00:48:51; MaxRSS max ~5.33/20 GB; timeseries ON.
- Validate `23515820`: `COMPLETED 0:0` elapsed 00:00:10; MaxRSS ~17 MB; `VALIDATE_PASS`
  (9 sites; 2700 member-rows; site-median CSV written).
- Failure classification: none.
- Cancellation evidence: none.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | authoritative `23515370` `COMPLETED 0:0`; `PREFLIGHT_PASS` | pass | imports, dual-arm primitives, artifact/case identity |
| full | yes | array `23515500` leaves 1–9 all `COMPLETED 0:0`; `FULL_LEAF_PASS`; timeseries ON; plots present | pass | 9×100×3 arms complete |
| validate | yes | job `23515820` `COMPLETED 0:0`; `VALIDATE_PASS`; site medians + decision written | pass | accounting/completeness/integrity gates only |

- Objective label: Offline forcing versus coupled dual-variant ELM PPE SR comparison
- Bounded scope label: Nine sites; offline + drop32 + drop21_corr080; 9×100 timeseries ON; four-figure plot package; no skill floor
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter004`
- Dependency identities: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Offline-versus-coupled comparison completed with metrics, timeseries, and plot package; predictive scores characterized; production MCMC readiness not established
- Quantitative characterization (not pass/fail thresholds): site-median of per-site
  member-medians — offline median R²≈0.850 KGE≈0.862; drop32 median R²≈0.579 KGE≈0.821;
  drop21_corr080 median R²≈0.651 KGE≈0.816; Pearson r high (~0.93) for all arms; negative
  R² at ABBY/WREF for coupled arms. Compact table:
  `summaries/iter004/iter004_site_metric_medians.csv`.
- Limitations: `/xdisk` retention temporary/unbacked; predictive skill is characterization
  only; offline skill exceeds coupled at most sites; production MCMC readiness not established.
- Next action: none; Iter004 closeout records are complete. Treat the workflow as idle until
  a consolidated kickoff package for `iter005` is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter004/validate_iter004_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent 6d8391443bbd0a2612e66e17c47414a896e2ab01 --expected-subject "Close Iter004
  offline-versus-coupled comparison"`. Result:
  `PASS: Iter004 records, artifacts, accounting, and precommit closeout identity validated`.
- Closeout identity: controlled-path manifest SHA-256
  `d258132a71a8fba4e4291cdc4d2cffc0f3b2b7acba41ae0e08da70283ed419c2` over the sorted controlled
  paths recorded in `summaries/iter004/iter004_decision.json`.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter005`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter005`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter005_preflight`,
  `spinup_forcing_coupling_iter005_full`, and
  `spinup_forcing_coupling_iter005_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: run a nine-site × 100-member offline forcing-surrogate-v1 campaign using the
historical MCMC-default **site-mean ELM restart spinup** (`mean_spinup_state` over members
`1..nsamples`; spinup fixed while parameters remain member-specific); publish timeseries and
SR-versus-member plots that overlay ELM, this mean-spinup offline arm, and Iter004's three
arms (member-restart offline, coupled `drop32`, coupled `drop21_corr080`) with site
member-median Pearson r and KGE annotations; write `iter005_site_metric_medians.csv` that
also includes Iter004 metric medians. Minimize new repository code by reusing existing
inference/eval paths and Iter004 on-disk products.

Evidence basis: Iter004 compared member-restart offline versus coupled arms; historical
`optimize_surrogate_forcing.py` MCMC defaults omit `--spinup-member` and therefore use
`mean_spinup_state`. Production MCMC readiness remains unestablished; MCMC wiring is deferred
to proposed `iter006`.

Optional hypothesis: the coupled-versus-mean-spinup-offline gap is the MCMC-relevant skill
comparison; member-restart offline remains the oracle baseline already characterized in
Iter004.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Offline `SR` predictor | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Nine I20TR case pickles + linked ELM restarts/histories | Mean spinup, member params, ELM `SR` | Same trust model as Iter004 |
| Closed Iter004 full/summary products | Reuse three-arm metrics/series for overlays and CSV join | Read-only; identity locked at kickoff |
| Existing `build_forcing_inference_inputs` / `mean_spinup_state` / Iter004 eval tooling | Prefer extend-in-place | Lock repository identity at kickoff; minimize new code |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core compute (new): mean-spinup offline arm only — nine sites × 100 members; timeseries ON;
preflight → full array `1-9` → validate/closeout.

Reuse without re-run: Iter004 member-restart offline, `drop32`, and `drop21_corr080` metrics
and series for plot overlays and summary join.

Plots — two figures per site:

1. Timeseries: ELM + mean-spinup offline + Iter004 three arms; member-mean ± std shade;
   absolute SR; annotate site member-median Pearson r and KGE per predictor arm.
2. SR versus ensemble member: same five series; dots + temporal-std error bars; no
   connectors; annotate site member-median Pearson r and KGE per predictor arm.

Summary: `summaries/iter005/iter005_site_metric_medians.csv` includes the new mean-spinup
offline medians and Iter004's three-arm medians, clearly labeled by arm.

Code posture: minimize added repository code; reuse existing functions and Iter004 products;
add or extend code only when necessary or when it clearly eases future MCMC work.

Exclusions: MCMC campaign; MCMC wiring/integration (deferred to `iter006`); re-running
Iter004 coupled/member-offline campaigns; retraining; feature selection; numeric skill
floors; SR-versus-TOTSOM plots; Git of large binaries/NetCDF.

Nominal scheduler tasks: 3 (preflight, full, validate). Provisional hard cap: 5 (one
minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or
validate).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Mean-spinup offline completes 9×100 with finite metrics and timeseries products.
3. Both locked plot types exist for all nine sites with required overlays and r/KGE
   annotations.
4. `iter005_site_metric_medians.csv` includes mean-spinup offline medians and Iter004's
   three-arm medians.
5. Negative gates for missing artifact/schema/version failures fail closed.
6. Compact `summaries/iter005/` and the four durable records agree after handoff validation.

Decision rule: pass means the MCMC-relevant mean-spinup offline baseline is compared with
Iter004 arms under the locked plot/summary contract. Pass does not claim production MCMC
readiness or impose a predictive-accuracy threshold.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

Resources follow Iter004 evidence with lighter full-leaf work (one new predict arm plus
overlays rather than three live predicts).

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter005_{preflight,full,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Full (array `1-9`) | `--mem=20G` / 4 h per leaf |
| Validate | 1 CPU (derived ~5 GB) / 1 h |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or validate; no automatic application/numerical retry |
| Cancellation | recorded Iter005 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- Mean-spinup offline products (metrics, timeseries) via minimal reuse-oriented code changes
- Per-site annotated timeseries and SR-versus-member plots overlaying Iter004 arms
- Compact `summaries/iter005/` including joined `iter005_site_metric_medians.csv`; finalized
  `iterations/iter005.md`; `ITERATION_SUMMARY.md` append; `registry.csv` row; rebuilt
  `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter005/` (created only after kickoff approval)
- After Iter005 closeout, the next planning-only proposal is `iter006` MCMC integration of
  the `predict_coupled_sr` primitive (no campaign)

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter005 initialization.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter004/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one local closeout commit (precommit then postcommit)
