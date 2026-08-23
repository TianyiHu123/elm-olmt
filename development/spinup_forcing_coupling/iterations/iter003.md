# iter003 - Coupled Spinup–Forcing ELM Comparison

## Status

- Iteration ID: `iter003`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter003_preflight`,
  `spinup_forcing_coupling_iter003_pilot`,
  `spinup_forcing_coupling_iter003_full`, and
  `spinup_forcing_coupling_iter003_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-05T19:13:40-0700`
- Closed: `2026-08-05T20:30:09-0700`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter002 closeout /
planning revision in `handoff/CURRENT.md` and `iterations/iter002.md`, planning-body SHA-256
`dd52979e7c37c0b469d44bcead0c9d39383fc5688f6e298ea9afda1931448b00`.

- Sequential ID and work type: `iter003`; `implementation`.
- Objective: build a reusable coupled spinup→forcing interface compatible with both released
  `spinup-surrogate-v1` variants (`drop32` and `drop21_corr080`) and the closed Iter002
  `forcing-surrogate-v1` artifact; run coupled `SR` predictions against pickle-linked ELM PPE
  histories; publish per-site/per-member metrics, feedback diagnostic plots, and optional
  timeseries; ship a public CLI/library primitive reusable later by MCMC.
- Upstream dependencies: locked Iter002 forcing artifact; Iter012 `drop32` and
  `drop21_corr080`; nine I20TR case pickles and linked PPE ELM histories; `OLMT_puma`.
- Bounded scope: MCMC-ready predict primitive + PPE batch client; preflight; ABBY×5×both
  pilot with timeseries ON; nine sites × 100 members × both full campaign with timeseries
  OFF; metrics R²/RMSE/bias/MAE/Pearson r/KGE; feedback plots; validate/closeout.
  Exclusions: MCMC campaign; retraining; feature selection; numeric skill floors; Git of
  large binaries.
- Acceptance gates and decision rule: accounting; dual-variant + forcing load; pilot and
  full completeness with finite products; negative fail-closed gates; durable-record
  agreement. Pass means executable dual-variant coupled path with ELM comparison evidence;
  scores characterize only; not production MCMC readiness.
- Site and resources: Puma `chopinsong`/`standard`/`OLMT_puma`; preflight 1 CPU / derived
  5 GB / 30 min; pilot `--mem=60G` / 4 h; full array `1-9` `--mem=80G` / 8 h per leaf;
  validate 1 CPU / derived 5 GB / 1 h; independent review; one minimal preflight
  correction/rerun; one same-scope scheduler/resource retry per failed pilot/full/validate;
  bounded cancellation; stop after closeout branch.
- Evidence: CLI/library, pilot NetCDF, metrics/plots, summaries, Slurm material, four
  durable records, handoff validator.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approved with one revision: for full run slurm array, don't need to do 9%3, just directly use 1-9.`; accepted `2026-08-05T19:13:40-0700`. Interpretation: approve the consolidated package as written except full array is `1-9` (no `%3` throttle). Outside-sandbox grant: exact response `Outside-sandbox sbatch/monitor/scancel is authorized.`; accepted `2026-08-05T19:16:12-0700` (items 1–3 granted). |
| Kickoff goal, finite work-unit count, and stop conditions | Build MCMC-ready coupled spinup→forcing interface with dual-variant ELM PPE `SR` comparison (pilot then full); 4 nominal / 7 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter003_{preflight,pilot,full,validate}/`; retain metrics, plots, pilot NetCDFs, submitted material, logs, accounting; `/xdisk` temporary and unbacked; no Git of large binaries |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan above; forcing artifact SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 SHA-256 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; nine `*_ppe6_I20TRCNPRDCTCBC.pkl`; 100 members/case; repository commit and Iter003 source manifest locked during preparation |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, pilot, full, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 1 CPU / derived 5 GB / 30 min; pilot `--mem=60G` / 4 h; full array `1-9` `--mem=80G` / 8 h per leaf; validate 1 CPU / derived 5 GB / 1 h; one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed pilot/full/validate; no automatic application/schema/numerical/OOM/timeout retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Granted: locked `sbatch` and allowed resubmission; job-scoped `squeue`/`scontrol show job`/`sacct`/`seff`/`job-history`/`job-limits`; bounded `scancel` for recorded Iter003 job IDs under contract cancellation conditions |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, NetCDF, models, logs excluded; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Forcing surrogate | `SR` predictor | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | 108409 bytes; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release + validate pass |
| Spinup `drop32` | State surrogate | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl` | `spinup-surrogate-v1` | 80440 bytes; SHA-256 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e` | Iter012 release |
| Spinup `drop21_corr080` | Compact state surrogate | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `spinup-surrogate-v1` | 68048 bytes; SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | Iter012 release |
| Nine case pickles | Cases / parms / ELM `SR` | `pklfiles/*_ppe6_I20TRCNPRDCTCBC.pkl` | ordered `ensemble_parms`; 100 members | present; hashes locked at preparation | Same trust model as Iter001/002 |

- Repository commit: `7b70aa42d8d6b351255266690adcc0d97871d268` on
  `feature/surrogate_coupling` (dirty bounded Iter003 worktree locked by source manifest).
- Bounded source manifest: `slurm/iter003/iter003_source_manifest.sha256` over the locked
  Iter003 controlled paths; regenerate with `sha256sum` and re-verify after any listed-path edit.
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`; verified on compute-node preflight.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting for every task; pilot and full
  products; compact `summaries/iter003/`; four durable records agreeing after closeout
  validation.
- Acceptance gates: as finalized in the plan (accounting; loads; pilot; full; negative
  gates; durable-record agreement).
- Decision rule: pass means the coupled interface is executable, dual-variant compatible,
  ELM-compared, and evidence-complete for later MCMC reuse. No predictive-accuracy
  threshold. Pass does not claim production MCMC readiness.
- Comparative aggregation: per-site medians over members in summary report; full
  per-member tables retained.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change; disallowed retry;
  task beyond the 7-task hard cap; gate reinterpretation; outside-sandbox grant if still
  pending at first submit.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter003.slurm`; `preflight_config.env` | byte-equal submitted copies; historical fail `*_job23510366.*` preserved | `spinup_forcing_coupling_iter003_preflight/`; logs `preflight_23510375.{out,err}` | locked artifacts/cases | commit `7b70aa4...`; source manifest locked | authoritative `23510375` (prior fail `23510366`) | `COMPLETED 0:0` elapsed 00:01:01; MaxRSS ~5.0/5 GB; `PREFLIGHT_PASS` | one authorized correction/rerun for test `sys.path` |
| pilot | `pilot_iter003.slurm`; `pilot_config.env` | byte-equal submitted copies; historical fail `*_job23510415.*` preserved | `spinup_forcing_coupling_iter003_pilot/`; logs `pilot_23510419.{out,err}` | preflight `23510375` pass | commit `7b70aa4...`; exec source manifest excludes live ledgers | authoritative `23510419` (prior fail `23510415` source-hash drift) | `COMPLETED 0:0` elapsed 00:02:10; MaxRSS 3.94/60 GB; `PILOT_PASS` | one packaging/lock refresh + resubmit after CURRENT.md hash drift |
| full | `full_iter003.slurm`; `full_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter003_full/`; logs `full_23510434_%a.{out,err}` | pilot `23510419` pass | commit `7b70aa4...`; exec source manifest | `23510434` array `1-9` | all leaves `COMPLETED 0:0`; leaf elapsed max 00:36:24; MaxRSS max ~4.89/80 GB; `FULL_LEAF_PASS` sites 1–9 | no % throttle |
| validate | `validate_iter003.slurm`; `validate_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter003_validate/`; logs `validate_23510503.{out,err}` | full pass | commit `7b70aa4...`; exec source manifest | authoritative `23510503` | `COMPLETED 0:0` elapsed 00:00:11; MaxRSS ~15 MB; `VALIDATE_PASS` | — |

Compact ledger: `summaries/iter003/iter003_accounting.csv`.

## Independent Read-Only Review

- Reviewer: independent read-only agent `8d17da72-e806-4fd3-ae4b-4632c365a98c`
  (inherit); review completed `2026-08-05T19:24:00-0700`.
- Reviewed source hash: source-manifest file SHA-256
  `7201fc71557e844920275a18b1d379daa51db5ac0a99bdddf0822fd900826d4f`.
- Outcome: `pass`.
- Findings and primary-agent response: no blockers. Confirmed predicted-spinup coupling
  path, array `1-9` without throttle, Puma resource shapes, timeseries ON/OFF policy,
  dual-variant + KGE contract alignment, manifest and `bash -n` checks. Primary proceeds
  to preflight submission after refreshing the source manifest for this review record.

## Execution and Diagnostics

- Static validation: repository syntax/`bash -n` and source-manifest checks at preparation;
  independent review pass before substantive submit.
- Preflight: historical fail `23510366` (`ModuleNotFoundError: model_ELM` in tests);
  authoritative pass `23510375` after `sys.path` correction.
- Pilot: historical fail `23510415` (CURRENT.md source-hash drift); authoritative pass
  `23510419` after packaging/lock refresh.
- Full array `23510434` tasks 1–9: all `COMPLETED 0:0` with `FULL_LEAF_PASS`.
- Validate `23510503`: `COMPLETED 0:0` with `VALIDATE_PASS` (9 sites; 1800 full
  member-rows; site-median CSV written).
- Failure classification: both historical fails were application/packaging defects under
  the one-retry contract; not scheduler/OOM/timeout.
- Cancellation evidence: none.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | authoritative `23510375` `COMPLETED 0:0`; `PREFLIGHT_PASS`; historical fail `23510366` classified | pass | imports, dual-variant + forcing identity, cases, and API smoke passed |
| pilot | yes | authoritative `23510419` `COMPLETED 0:0`; metrics/plots/NetCDF present; `PILOT_PASS`; historical fail `23510415` classified | pass | ABBY×5×both with timeseries ON |
| full | yes | array `23510434` leaves 1–9 all `COMPLETED 0:0`; `FULL_LEAF_PASS`; timeseries OFF | pass | nine sites × 100 members × both variants complete |
| validate | yes | job `23510503` `COMPLETED 0:0`; `VALIDATE_PASS`; site medians + decision summary written | pass | accounting/completeness/integrity gates only |

- Objective label: Coupled spinup–forcing dual-variant ELM PPE SR comparison
- Bounded scope label: Nine sites; both spinup variants; ABBY×5 pilot timeseries ON; 9×100×both full timeseries OFF; MCMC-ready CLI; ELM compare; no skill floor
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter003`
- Dependency identities: forcing
  `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32
  `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Executable dual-variant coupled path demonstrated with ELM comparison evidence; predictive scores characterized; production MCMC readiness not established
- Quantitative characterization (not pass/fail thresholds): site-median of per-site
  member-medians — `drop32` median R²≈0.579 / KGE≈0.821; `drop21_corr080` median
  R²≈0.651 / KGE≈0.816; Pearson r high (~0.93); negative R² at ABBY and WREF for both
  variants. Compact table:
  `summaries/iter003/iter003_site_metric_medians.csv`.
- Limitations: `/xdisk` retention temporary/unbacked; predictive skill is characterization
  only (no skill floor); some sites show negative R² despite high Pearson correlation;
  production MCMC readiness is not established; closeout is `committed` at
  `930bd335ad071faa890541199f4b46be8f5bda83` (records reconciled after an initial
  deferred-commit label).
- Next action: none; Iter003 closeout records are complete. Treat the workflow as idle
  until a consolidated kickoff package for `iter004` is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter003/validate_iter003_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent 7b70aa42d8d6b351255266690adcc0d97871d268 --expected-subject "Close Iter003
  coupled spinup-forcing ELM comparison"`. Result:
  `PASS: Iter003 records, artifacts, accounting, and precommit closeout identity validated`.
  Post-commit verification against closeout commit
  `930bd335ad071faa890541199f4b46be8f5bda83` satisfies the authorized committed branch.
- Closeout identity: controlled-path manifest SHA-256
  `2e1326657f72378c873a605bafd0daa8ca55c55706edacb6e5c0ad21fca2123c` over the sorted controlled
  paths recorded in `summaries/iter003/iter003_decision.json`; observed closeout commit
  `930bd335ad071faa890541199f4b46be8f5bda83`.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter004`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter004`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter004_preflight`,
  `spinup_forcing_coupling_iter004_full`, and
  `spinup_forcing_coupling_iter004_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: compare offline forcing-surrogate-v1 (ELM restart spinup) versus the coupled
spinup→forcing path (`drop32` and `drop21_corr080`) on all nine I20TR sites × 100 PPE
members; save metrics and timeseries for both frameworks; publish the locked per-site plot
package against ELM `SR`.

Evidence basis: Iter003 closed `pass` with executable dual-variant coupled ELM comparison,
MCMC-ready CLI delivered, and predictive scores characterized (site-median R²/KGE and high
Pearson r; some sites negative R²). Iter003 full ran timeseries OFF; this iteration turns
timeseries ON for the offline-versus-coupled comparison. Production MCMC readiness remains
unestablished; MCMC integration is deferred to proposed `iter005`.

Optional hypothesis: holding the forcing artifact fixed, ELM-restart versus predicted-spinup
inputs produce separable skill and structure in metrics and the plot package; scores remain
characterization only.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Offline and coupled `SR` predictor | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 `drop32` / `drop21_corr080` | Coupled spinup state surrogates only | Immutable; path/hash locked at kickoff |
| Nine I20TR case pickles + linked ELM PPE histories | Cases, parms, ELM `SR` and restart spinup | Same trust model as Iter003 |
| Iter003 coupled API/CLI plus offline predict path | Evaluation client | Lock repository identity at kickoff; extend/reuse as needed |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Prediction arms (plus ELM truth):

1. Offline: forcing-surrogate-v1 with ELM restart TOTSOMC/TOTSOMN.
2. Coupled `drop32`.
3. Coupled `drop21_corr080`.

Campaign: nine sites × 100 members; timeseries ON for all sites; no pilot — preflight →
full array `1-9` → validate/closeout.

Metrics versus ELM `SR` (characterization only; no skill floor): `r2`, `rmse`, `bias`,
`mae`, `pearson_r`, `kge`.

Plot package — four figures per site:

1. Timeseries: ELM + offline + coupled `drop32` + coupled `drop21_corr080`; member-mean
   line with ± std shaded band; absolute SR; alpha=0.5.
2. SR versus ensemble member: all four series; dots with temporal-std error bars; no
   connectors between dots; alpha=0.5; y = time-mean SR.
3. SR versus TOTSOMC — three subplots: (ELM + offline, shared ELM-restart x) |
   (ELM + coupled `drop32`) | (ELM + coupled `drop21_corr080`); Iter003-style layout with
   the new marker/alpha/no-connector requirements; y = time-mean SR ± temporal std.
4. SR versus TOTSOMN — same three-subplot pattern as (3).

Exclusions: MCMC campaign; MCMC wiring/integration (deferred to `iter005`); retraining;
feature selection; numeric skill floors; Git of large binaries/NetCDF.

Nominal scheduler tasks: 3 (preflight, full, validate). Provisional hard cap: 5 (one
minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or
validate).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Offline and both coupled arms complete 9×100 with finite metrics and timeseries products.
3. The locked four-figure plot package exists for all nine sites under the approved layout
   and style rules.
4. Negative gates for missing artifact/schema/version failures fail closed.
5. Compact `summaries/iter004/` and the four durable records agree after handoff validation.

Decision rule: pass means the offline-versus-coupled comparison is executable and
evidence-complete (metrics, timeseries, plots). Pass does not claim production MCMC
readiness or impose a predictive-accuracy threshold.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

Resources are evidence-derived from Iter003 accounting (preflight MaxRSS 5.0 GB at the
1-CPU ceiling; pilot timeseries-ON MaxRSS 3.9 GB; full timeseries-OFF leaf max MaxRSS
4.9 GB / elapsed 36:24; validate MaxRSS ~15 MB). Iter004 adds an offline arm (~1.5×
predict work versus two coupled variants), timeseries ON, and a richer plot package.

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter004_{preflight,full,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min — Iter003 1-CPU preflight saturated ~5 GB |
| Full (array `1-9`) | `--mem=20G` / 4 h per leaf — observed ~5 GB and ~36 min at 100×2 timeseries-OFF; 20 GB / 4 h covers three arms + timeseries ON + plots |
| Validate | 1 CPU (derived ~5 GB) / 1 h — unchanged; light accounting |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry for full or validate; no automatic application/numerical retry |
| Cancellation | recorded Iter004 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- Offline predict path and dual-framework evaluation client (metrics, timeseries, plots)
- Per-site/per-member metrics; NetCDF timeseries; nine-site four-figure plot set
- Compact `summaries/iter004/`; finalized `iterations/iter004.md`; `ITERATION_SUMMARY.md`
  append; `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter004/` (created only after kickoff approval)
- After Iter004 closeout, the next planning-only proposal is `iter005` MCMC integration of
  the Iter003 `predict_coupled_sr` primitive (no campaign), deferred from the prior plan

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter004 initialization.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter003/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: `committed` at `930bd335ad071faa890541199f4b46be8f5bda83` (precommit validated; observed closeout commit recorded)
