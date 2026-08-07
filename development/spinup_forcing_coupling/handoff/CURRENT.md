# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `none` (proposed `iter006`, not initialized)
- Status: `not_initialized`
- Phase: `ready_for_kickoff_approval`
- Active job IDs: none
- Site profile: `development/hpc/puma.md` (proposed; not yet locked by kickoff approval)
- Last updated: `2026-08-06T20:20:23-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `not approved` (Iter005 package exhausted; Iter006 consolidated package
  presented for one-shot approval after plan finalization)
- Kickoff goal and stop boundary: pending user approval of the consolidated Iter006 package
  below (MCMC three-mode wiring; no campaign).
- User response and approval timestamp: none yet for Iter006.
- Confirmed HPC system and profile: proposed Puma; `development/hpc/puma.md`.
- Approved output root: none until Iter006 package approval; proposed root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with only
  `spinup_forcing_coupling_iter006_{preflight,validate}/`.
- Locked dependencies/gates/decision: none until approval; see proposed plan.
- Outside-sandbox and closeout authorities: none until Iter006 package approval.

## Current Objective

MCMC three-mode spinup wiring (mean / member-restart / coupled) — planning only

## Best Evidence So Far

- Work type: `implementation` (proposed)
- Prior evidence: Iter005 mean-spinup offline median R²≈-1.894 KGE≈0.438 vs Iter004
  member-restart offline R²≈0.850 KGE≈0.862; coupled intermediate
- Forcing identity: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Acceptance result: pending Iter006
- Decision: pending Iter006

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Awaiting one approval of the complete Iter006 consolidated kickoff package.

## Next Action

1. Await one explicit user approval of the complete consolidated Iter006 kickoff package
   (plan + contract + outside-sandbox items 1–3 + closeout branch). Do not initialize
   until that approval is recorded.

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
