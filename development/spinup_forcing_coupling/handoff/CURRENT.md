# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter005`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-06T19:42:02-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter005 closed)
- Kickoff goal and stop boundary: Mean-spinup offline baseline vs Iter004 arms with
  metrics, timeseries, and locked plots/summary; stop after terminal accounting,
  immutable gates, durable records, cross-record validation, and the approved closeout
  branch.
- User response and approval timestamp: exact response
  `approve complete package: plan + contract + outside sandbox authority + comit permission`;
  accepted `2026-08-06T18:53:00-0700`. Outside-sandbox items 1–3 granted.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with only
  `spinup_forcing_coupling_iter005_{preflight,full,validate}/`.
- Locked dependencies/gates/decision: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`;
  Iter004 reuse locked; nine I20TR cases; 100 members; mean-spinup offline new compute;
  timeseries ON; two annotated plot types; functional/integrity gates; scores
  characterization only.
- Outside-sandbox and closeout authorities: exhausted with Iter005 closeout (`committed`).

## Current Objective

Mean-spinup offline forcing baseline versus Iter004 arms

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: Nine sites; mean-spinup offline 9×100 timeseries ON; overlay Iter004 three arms; two annotated plot types; joined medians CSV; no skill floor
- Upstream dependency identities: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter005`
- Preflight `23516340` pass; full array `23516376` 1–9 pass; validate `23516504` pass
- Characterization: site-median of per-site member-medians — offline_mean_spinup median
  R²≈-1.894 KGE≈0.438; Iter004 offline median R²≈0.850 KGE≈0.862; drop32 median R²≈0.579
  KGE≈0.821; drop21 median R²≈0.651 KGE≈0.816; pearson high (~0.925) for mean-spinup
- Acceptance result: `pass`
- Decision: Mean-spinup offline baseline compared with Iter004 arms under locked plot/summary contract; predictive scores characterized; production MCMC readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Production MCMC readiness is not established; mean-spinup offline skill lags member-restart
  offline and coupled arms on R²/KGE at most sites.

## Next Action

1. Idle until a consolidated kickoff package for proposed `iter006` (MCMC integration of
   `predict_coupled_sr`; no campaign) is approved.


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
a single MCMC configuration can select offline mean-spinup, offline member-restart, or
coupled spinup→forcing without a PPE campaign. Prove the wiring with a bounded compute-node
preflight plus a short dry-run / single-chain smoke that exits after a few likelihood
evaluations; do not run a production MCMC campaign.

Evidence basis: Iter003–Iter004 delivered coupled and offline comparison APIs; Iter005
showed mean-spinup offline (historical MCMC default) is the skill-relevant baseline and
lags both member-restart offline and coupled arms on R²/KGE. Production MCMC readiness
remains unestablished until the sampler can call the same primitives.

Optional hypothesis: exposing `predict_coupled_sr` and mean-spinup offline through the
existing MCMC likelihood interface is sufficient for a later campaign iteration; no
retraining is required for wiring correctness.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Offline/coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop32` and/or `drop21_corr080` | Coupled state | Immutable Iter012 hashes locked at kickoff |
| `predict_offline_sr` / `predict_coupled_sr` / `mean_spinup_state` | Likelihood primitives | Lock repository identity at kickoff |
| Closed Iter005 characterization | Motivates mean-spinup as MCMC default spinup mode | Read-only |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work: MCMC wiring/integration only — CLI or config switch for spinup mode
(mean-spinup offline / member-restart offline / coupled variant); unit tests; one
preflight; one short smoke validate on a single site with a tiny evaluation budget.

Exclusions: production MCMC campaign; multi-site PPE sweeps; retraining; feature
selection; numeric skill floors; re-running Iter004/Iter005 comparison campaigns; Git of
large binaries/NetCDF/chains.

Nominal scheduler tasks: 2 (preflight, validate/smoke). Provisional hard cap: 4 (one
minimal preflight correction/rerun; one same-scope scheduler/resource retry).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. MCMC path can invoke `predict_coupled_sr` and mean-spinup offline through the locked
   interface without schema/import failures.
3. Smoke run completes the declared tiny evaluation budget and writes a compact identity
   summary under `summaries/iter006/`.
4. Negative gates for missing artifact/schema/version failures fail closed.
5. Compact `summaries/iter006/` and the four durable records agree after handoff validation.

Decision rule: pass means MCMC can call the locked coupling primitives under a declared
spinup mode. Pass does not claim a calibrated posterior or production campaign readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter006_{preflight,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Validate/smoke | 1 CPU (derived ~5 GB) / 1 h |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry; no automatic application/numerical retry |
| Cancellation | recorded Iter006 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- MCMC wiring diff with tests covering spinup-mode selection
- Compact `summaries/iter006/` smoke identity; finalized `iterations/iter006.md`;
  `ITERATION_SUMMARY.md` append; `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff
  validator result
- Canonical scripts under `slurm/iter006/` (created only after kickoff approval)
- After Iter006 closeout, next planning-only proposal is a production MCMC campaign only if
  wiring gates pass; otherwise a repair iteration

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter006 initialization.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. If an active or closed iteration exists, read its `iterations/iterXXX.md` report in full and up
   to two preceding reports. No report is expected for pre-kickoff `iter001`.
3. Read relevant registry rows and summaries.
4. Read the proposed or approved HPC profile when one exists; otherwise leave site selection
   unresolved.
5. Inspect Git state and reconcile scheduler and artifact state relevant to any recorded
   iteration.
6. For a new iteration, resolve missing decisions and seek one approval of the complete
   consolidated kickoff package. For an initialized iteration, verify and reuse its recorded,
   unexhausted package without asking again.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter005.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter005`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter005/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter005_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
