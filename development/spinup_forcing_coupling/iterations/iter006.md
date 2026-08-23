# iter006 - MCMC three-mode spinup wiring

## Status

- Iteration ID: `iter006`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter006_preflight`,
  `spinup_forcing_coupling_iter006_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-06T20:31:00-0700`
- Closed: `2026-08-06T21:11:23-0700`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter005 closeout in
`handoff/CURRENT.md` and `iterations/iter005.md`, planning-body SHA-256
`9c548a90867e64b70092d09da3764739df1b830256fc332628310ef0883ddd38`.

- Sequential ID and work type: `iter006`; `implementation`.
- Objective: integrate `predict_coupled_sr` into the production MCMC path so a single
  CLI/config switch selects among `mean_spinup`, `member_restart`, and `coupled` without a
  PPE campaign; prove with compute-node preflight + ABBY smoke (collocation dry-run +
  ≤10 likelihood evaluations per mode).
- Optional hypothesis: exposing all three modes through the existing MCMC likelihood
  interface is sufficient for a later campaign iteration; no retraining required for
  wiring correctness.
- Upstream dependencies: Iter002 forcing-v1; Iter012 drop32 and drop21_corr080; locked
  primitives; existing mean/`--spinup-member` baselines; `OLMT_puma`.
- Bounded scope: three-mode switch; coupled variant `drop32`|`drop21_corr080` (default
  `drop21_corr080`); historical default = mean-spinup; unit tests; one preflight; one
  ABBY smoke validate. Exclusions: production MCMC campaign; multi-site sweeps;
  retraining; skill floors; Iter004/005 re-runs; Git of large binaries.
- Acceptance gates and decision rule: as in the approved package (wiring correctness;
  no calibrated posterior claim).
- Site and resources: Puma `chopinsong`/`standard`/`OLMT_puma`; preflight 2 CPUs / 30 min;
  validate 1 CPU / 1 h; independent review; one preflight correction/rerun; one
  same-scope retry; bounded cancellation.
- Evidence: wiring diff + tests; smoke identity; Slurm; four durable records; handoff
  validator.
- Approval boundary: satisfied by the exact response recorded below.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approve for plan + contract + outside-sandbox 1–3 + closeout commit`; accepted `2026-08-06T20:31:00-0700`. Interpretation: approve the complete consolidated package including plan, runtime contract, outside-sandbox items 1–3, and one local closeout commit. |
| Kickoff goal, finite work-unit count, and stop conditions | Three-mode MCMC wiring + ABBY smoke; 2 nominal / 4 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter006_{preflight,validate}/`; `/xdisk` temporary and unbacked; no Git of large binaries/NetCDF/chains |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan above; forcing SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; ABBY case pickle; wiring characterization only |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs (derived ~10 GB) / 30 min; validate 1 CPU (derived ~5 GB) / 1 h; one minimal preflight correction/rerun; one same-scope scheduler/resource retry for validate; no automatic application/schema/numerical retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Granted: locked `sbatch` and allowed resubmission; job-scoped `squeue`/`scontrol show job`/`sacct`/`seff`/`job-history`/`job-limits`; bounded `scancel` for recorded Iter006 job IDs under contract cancellation conditions |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, NetCDF, models, logs excluded; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Forcing surrogate | Offline/coupled `SR` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release |
| Spinup `drop32` | Coupled state | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl` | `spinup-surrogate-v1` | SHA-256 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e` | Iter012 release |
| Spinup `drop21_corr080` | Coupled state (default) | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `spinup-surrogate-v1` | SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | Iter012 release |
| ABBY case pickle | Smoke case | `pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl` | 100 members | hash in `iter006_case_pickles.sha256` | Prior coupling trust |

- Repository commit: `542b7d3ce74bd3baa23c48b5b4638270be12cf86` on `feature/surrogate_coupling`
  (dirty bounded Iter006 worktree locked by source manifest).
- Bounded source manifest: `slurm/iter006/iter006_source_manifest.sha256`
  (file SHA-256 `5045f20a7aeec68abfe30678215ba1cc35c568d335fadd70d877395f7124b25e`).
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting; three-mode MCMC interface;
  ABBY smoke budget for all three modes; coupled accepts both variants with default
  `drop21_corr080`; fail-closed negatives; compact `summaries/iter006/`; four durable
  records agreeing after closeout validation.
- Acceptance gates: as finalized in the plan.
- Decision rule: pass means MCMC can select and call the locked coupling/offline
  primitives under each declared spinup mode, and existing mean/member-restart paths
  still work. Pass does not claim a calibrated posterior or production campaign readiness.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change; disallowed retry;
  task beyond the 4-task hard cap; gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter006.slurm` `f4d827ae...`; `preflight_config.env` `ca25f885...` | byte-equal submitted copies in run dir | `spinup_forcing_coupling_iter006_preflight/`; logs `preflight_23516816.{out,err}` | forcing + spinup + ABBY case manifests | commit `542b7d3...`; source-manifest file `5045f20a...` | authoritative `23516816` | `COMPLETED 0:0` elapsed 00:00:34; MaxRSS ~2.47/10 GB; `PREFLIGHT_PASS` | — |
| validate | `validate_iter006.slurm` `f87eef27...`; `validate_config.env` `f917e907...` | byte-equal submitted copies | `spinup_forcing_coupling_iter006_validate/`; logs `validate_23516840.{out,err}` | preflight `23516816` pass | same | authoritative `23516840` | `COMPLETED 0:0` elapsed 00:05:06; MaxRSS ~5.00/5 GB; `VALIDATE_PASS` | smoke fixture obs |

## Independent Read-Only Review

- Reviewer: independent read-only agent `15f0aeb0-3cca-4b32-9815-f2d1114550be`
  (inherit); review completed `2026-08-06T20:46:00-0700`.
- Reviewed source hash: source-manifest file SHA-256
  `5045f20a7aeec68abfe30678215ba1cc35c568d335fadd70d877395f7124b25e`.
- Outcome: `pass_with_concerns`.
- Findings and primary-agent response: no blockers. Concerns: (1) report ledger
  previously said submitted copies pending — updated before submission. (2)
  `predict_sr_for_mode` unit-tested while production uses `resolve_*` + direct
  `predict_coupled_sr` / offline design-matrix — accepted; smoke exercises production
  path. (3) schema/version negative thinner than wording — accepted; missing-artifact
  fail-closed covered. Primary proceeded to preflight submission.

## Execution and Diagnostics

- Static validation: `bash -n` on Slurm scripts; `py_compile` on Python sources; unit
  tests 9/9 OK; source manifest `sha256sum -c` OK; independent review
  `pass_with_concerns`.
- Preflight: authoritative `23516816` `COMPLETED 0:0` elapsed 00:00:34; MaxRSS ~2.47/10 GB;
  `PREFLIGHT_PASS` (unit tests + artifact/case identity + coupled path resolve +
  missing-spinup negative).
- Validate `23516840`: `COMPLETED 0:0` elapsed 00:05:06; MaxRSS ~5.00/5 GB;
  `VALIDATE_PASS` (ABBY dry-run + 10 likelihood evals for mean/member/coupled;
  coupled drop32 accept with 1 eval; missing-forcing negative).
- Failure classification: none.
- Cancellation evidence: none.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | authoritative `23516816` `COMPLETED 0:0`; `PREFLIGHT_PASS` | pass | imports, mode unit tests, artifact/case identity, negatives |
| validate | yes | job `23516840` `COMPLETED 0:0`; `VALIDATE_PASS`; smoke identity written | pass | three modes + drop32 accept + fail-closed missing artifact |

- Objective label: MCMC three-mode spinup wiring (mean / member-restart / coupled)
- Bounded scope label: ABBY smoke; three MCMC spinup modes; coupled drop32/drop21_corr080; <=10 likelihood evals/mode; no production campaign
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter006`
- Dependency identities: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: MCMC can select and call locked coupling/offline primitives under each declared spinup mode; mean/member-restart paths still work; production campaign readiness not established
- Quantitative characterization (not pass/fail thresholds): ABBY smoke completed 10
  likelihood evaluations for each of mean_spinup, member_restart, and coupled
  (default `drop21_corr080`); coupled `drop32` accepted with 1 eval; synthetic
  collocatable obs fixture used for wiring.
- Limitations: `/xdisk` retention temporary/unbacked; smoke obs is a collocatable
  fixture not NEON flux truth; validate MaxRSS approached the 5 GB allocation;
  production MCMC campaign not run.
- Next action: none; Iter006 closeout records are complete. Treat the workflow as idle
  until a consolidated kickoff package for `iter007` is approved.
- Four-record/precommit validator: `development/spinup_forcing_coupling/slurm/iter006/validate_iter006_handoff.py`
  with `PYTHONDONTWRITEBYTECODE=1 python3 -B ... --active-iteration-job-count 0 --phase precommit
  --expected-parent 542b7d3ce74bd3baa23c48b5b4638270be12cf86 --expected-subject "Close Iter006
  three-mode MCMC spinup wiring"`.
- Closeout identity: controlled-path manifest SHA-256
  `eb03d2c4954f63c4dbdf9574245146119f0b48763a38bad1ab2a0a9d2aeb563a` over the sorted controlled
  paths recorded in `summaries/iter006/iter006_decision.json`.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter007`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter007`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter007_preflight`,
  `spinup_forcing_coupling_iter007_campaign`,
  `spinup_forcing_coupling_iter007_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: run one joint two-site production MCMC campaign through the Iter006
`--spinup-mode=coupled` interface (`drop21_corr080`) for `SR` against NEON obs at ABBY and
JERC, writing posterior, predictive, parameter, and suggested diagnostic products under the
approved Iter007 campaign run directory (no `UQ_output/` nesting), without retraining or
changing coupling primitives.

Evidence basis: Iter006 passed wiring gates for mean_spinup, member_restart, and coupled
(`drop21_corr080` default; `drop32` accepted). Production campaign readiness remains
unestablished until a real obs-constrained sampler run completes under immutable gates.

Optional hypothesis: coupled `drop21_corr080` is the preferred first campaign arm given
Iter004/005 skill characterization.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop21_corr080` | Coupled spinup state | Immutable; SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| Iter006 MCMC mode wiring | CLI/likelihood path | Lock repository identity at kickoff |
| Cases | Joint targets | `ABBY_ppe6_I20TRCNPRDCTCBC`, `JERC_ppe6_I20TRCNPRDCTCBC` |
| Site obs NetCDF(s) | Likelihood truth | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/{ABBY,JERC}/{SITE}_cdo_merge.nc`; `--obs-err-vars SR:SR_err` with existing code default of 10% of \|obs\| if `SR_err` missing; lock path hashes at kickoff |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work:

- One joint multi-site MCMC (shared parameter vector) over ABBY + JERC.
- Mode: `--spinup-mode=coupled --coupled-spinup-variant=drop21_corr080`; `--vars SR`;
  `--fit-error` on; nominal `--nwalkers 64 --nsteps 500` (discard `nsteps//5`, thin 5).
- Diagnostic-driven sampler retune is deferred to a later iteration; Iter007 does not
  retune for ESS/acceptance/skill.
- Implementation: write campaign products at the campaign run-dir root (no `UQ_output/`);
  predictive plots include obs, best-fit, median, 95% CI with `alpha=0.3`, and ELM
  pre-calibration (ensemble-mean `case.output['SR']` on the collocated window); parameter
  PDFs/corner retained; emit suggested diagnostics under `diagnostics/`.
- Ladder: preflight → campaign → validate/accounting.

Required campaign layout under `spinup_forcing_coupling_iter007_campaign/`:

```text
best_params.txt
clm_params_best.nc
plots/pdfs/
plots/corner/
plots/predictions/{ABBY,JERC}/
diagnostics/
```

Suggested diagnostics (required products; integrity-only, no skill floors): collocation
audit; chain health (acceptance, ESS/autocorr, log-prob trace); skill table (optimized vs
ELM-precal vs obs); ΔlogL vs ELM-precal when comparable; residual summary; posterior
summary CSV; prior-edge occupancy. Optional diagnostics (leave-one-site, full residual QQ)
are out of scope.

Exclusions: retraining; feature selection; multi-mode or multi-variant campaigns;
surrogate-precalibrated overlay; scientific/diagnostic-driven nsteps/nwalkers retune;
Git of large binaries/NetCDF/chains; reinterpretation of Iter006 wiring gates; numeric
skill floors.

Nominal scheduler tasks: 3 (preflight, campaign, validate). Provisional hard cap: 5
(one minimal preflight correction/rerun; one resource-limitation campaign retune/resubmit
that may adjust only `nsteps`/`nwalkers`/`mem`/`cpus` when the failure is classified as
OOM, walltime, or equivalent scheduler/resource limit—not for mixing/skill).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold (integrity only):

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Campaign completes the locked walker/step budget under coupled/`drop21_corr080` without
   schema/import failures (or completes after one authorized resource-limitation retune
   within the hard cap).
3. Required products exist under the approved campaign layout: `best_params.txt`,
   `clm_params_best.nc`, predictive/parameter plots, and suggested `diagnostics/` files.
4. Negative gates for missing artifact/obs/schema failures fail closed.
5. Compact `summaries/iter007/` and the four durable records agree after handoff validation.

Decision rule: pass means the joint ABBY+JERC production MCMC campaign executed
successfully through the locked coupled interface and wrote the required products.
Pass does not claim calibrated scientific adequacy; diagnostic contents are
characterization, not numeric pass/fail floors.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter007_{preflight,campaign,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Campaign | 16 CPUs / 40 GB / 12 h; `--n-processes=16` (provisional; may be optimized later from seff evidence) |
| Validate | 1 CPU / ≥8 GB / 1 h (raise above Iter006 ~5 GB ceiling) |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one resource-limitation campaign retune of only `nsteps`/`nwalkers`/`mem`/`cpus`; no automatic application/numerical/diagnostic-driven retry |
| Cancellation | recorded Iter007 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- Campaign products under `spinup_forcing_coupling_iter007_campaign/` as above; compact
  `summaries/iter007/`; finalized `iterations/iter007.md`; `ITERATION_SUMMARY.md` append;
  `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter007/` (created only after kickoff approval)
- Code path change: MCMC forcing outputs write to the approved run dir without `UQ_output/`

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, locked mode/site/obs
budget, and closeout-commit authorization. Obtain one explicit user approval before any
Iter007 initialization.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter006/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
