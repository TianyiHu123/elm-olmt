# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter004`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-06T17:59:11-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter004 closed)
- Kickoff goal and stop boundary: Offline-vs-coupled ELM `SR` comparison with metrics,
  timeseries, and locked plots; stop after terminal accounting, immutable gates, durable
  records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response
  `compelete package approved: plan + contract + outside sandbox authority.`;
  accepted `2026-08-06T16:40:50-0700`. Outside-sandbox items 1–3 granted.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with only
  `spinup_forcing_coupling_iter004_{preflight,full,validate}/`.
- Locked dependencies/gates/decision: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`;
  drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; nine I20TR cases; 100 members; offline + both coupled;
  timeseries ON; functional/integrity gates; scores characterization only.
- Outside-sandbox and closeout authorities: exhausted with Iter004 closeout (`committed`).

## Current Objective

Offline forcing versus coupled dual-variant ELM PPE SR comparison

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: Nine sites; offline + drop32 + drop21_corr080; 9×100 timeseries ON; four-figure plot package; no skill floor
- Upstream dependency identities: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter004`
- Preflight `23515370` pass; full array `23515500` 1–9 pass; validate `23515820` pass
- Characterization: site-median of per-site member-medians — offline median R²≈0.850
  KGE≈0.862; drop32 median R²≈0.579 KGE≈0.821; drop21 median R²≈0.651 KGE≈0.816;
  pearson high (~0.93); coupled negative R² at ABBY/WREF
- Acceptance result: `pass`
- Decision: Offline-versus-coupled comparison completed with metrics, timeseries, and plot package; predictive scores characterized; production MCMC readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Production MCMC readiness is not established; coupled skill lags offline at most sites.

## Next Action

1. Idle until a consolidated kickoff package for proposed `iter005` is approved.

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
- Proposed run slugs: `spinup_forcing_coupling_iter005_preflight` and
  `spinup_forcing_coupling_iter005_validate` (integration/wiring only; no PPE campaign)

### 2. Evidence-derived objective and optional hypothesis

Objective: perform MCMC integration of the Iter003 `predict_coupled_sr` primitive
(`predict_coupled_surrogate.py` / `model_ELM/coupled_surrogate.py`) so a future MCMC
driver can call the coupled spinup→forcing path as a reusable library/CLI contract,
without launching an MCMC campaign in Iter005.

Evidence basis: Iter003 delivered the MCMC-ready coupled primitive; Iter004 completed
offline-versus-coupled comparison with metrics/timeseries/plots (characterization only).
Production MCMC readiness remains unestablished.

Optional hypothesis: wiring and contract tests around the existing predict primitive are
sufficient to make coupled SR callable from MCMC scaffolding without a new PPE evaluation
campaign or numeric skill gates.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Closed Iter003/Iter004 coupled API/CLI/tests | `predict_coupled_sr` primitive | Immutable read-only scientific contract; lock repository closeout identity at kickoff |
| Iter002 forcing-surrogate-v1 artifact | Forcing `SR` predictor | Immutable; SHA-256 `8d139b32...` |
| Iter012 `drop32` / `drop21_corr080` | Spinup state surrogates | Immutable; path/hash locked at kickoff |
| Existing MCMC scaffolding in repository (if any) | Integration target | Re-verify identity and call sites at preparation; no campaign launch |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core deliverable (MCMC integration, no campaign):

- Integrate `predict_coupled_surrogate.py` / coupled library into the MCMC call path
  (adapter or direct import) with a documented `predict_coupled_sr` contract.
- Add/extend unit or smoke tests proving MCMC scaffolding can invoke coupled predict for
  a tiny fixture (not a PPE sweep).
- Preflight + validate/closeout for the integration wiring only.

Exclusions: no MCMC campaign; no PPE re-evaluation; no retraining; no feature selection;
no numeric skill floors; no expansion of ELM comparison products; no Git of large binaries.

Nominal scheduler tasks: 2 (preflight, validate). Provisional hard cap: 4 (one minimal
preflight correction/rerun and one same-scope validate retry).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. MCMC scaffolding imports and invokes the Iter003 coupled predict primitive under the
   documented `predict_coupled_sr` contract.
3. Fixture-level smoke succeeds for at least one spinup variant + forcing artifact path.
4. Negative gates for missing artifact/schema/version failures fail closed.
5. Compact `summaries/iter005/` and the four durable records agree after handoff validation.

Decision rule: pass means the coupled primitive is integrated for MCMC reuse as a callable
contract. Pass does not claim a completed MCMC campaign or production calibration readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter005_{preflight,validate}/` |
| Preflight / validate | finalize exact CPU/mem/time at kickoff from fixture sizing |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry for validate; no automatic application/numerical retry |
| Cancellation | recorded Iter005 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- MCMC adapter/wiring calling `predict_coupled_surrogate.py` / coupled library
- Fixture smoke evidence; integration tests
- Compact `summaries/iter005/`; finalized `iterations/iter005.md`; `ITERATION_SUMMARY.md`
  append; `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter005/` (created only after kickoff approval)

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter005 initialization.


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

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter004.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter004`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter004/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter004_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
