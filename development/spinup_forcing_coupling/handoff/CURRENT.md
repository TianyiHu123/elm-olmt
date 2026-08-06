# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter003`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-06T16:30:44-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter003 closed)
- Kickoff goal and stop boundary: MCMC-ready coupled spinup→forcing dual-variant ELM PPE
  `SR` comparison (pilot then full); stop after terminal accounting, immutable gates,
  durable records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response
  `approved with one revision: for full run slurm array, don't need to do 9%3, just directly use 1-9.`;
  accepted `2026-08-05T19:13:40-0700`. Revision applied: full array `1-9` (no `%3`).
  Outside-sandbox grant: exact response `Outside-sandbox sbatch/monitor/scancel is authorized.`;
  accepted `2026-08-05T19:16:12-0700` (items 1–3 granted).
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
  with only `spinup_forcing_coupling_iter003_{preflight,pilot,full,validate}/`.
- Locked dependencies/gates/decision: forcing
  `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32
  `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; nine I20TR cases;
  100 members; functional/integrity gates; scores characterization only.
- Outside-sandbox and closeout authorities: exhausted with Iter003 closeout
  (`committed`; observed `930bd335ad071faa890541199f4b46be8f5bda83`).

## Current Objective

Coupled spinup–forcing dual-variant ELM PPE SR comparison

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: Nine sites; both spinup variants; ABBY×5 pilot timeseries ON; 9×100×both full timeseries OFF; MCMC-ready CLI; ELM compare; no skill floor
- Upstream dependency identities: forcing
  `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32
  `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter003`
- Preflight `23510375` pass (historical fail `23510366`); pilot `23510419` pass
  (historical fail `23510415`); full array `23510434` 1–9 pass; validate `23510503` pass
- Characterization: site-median of per-site member-medians — drop32 median R²≈0.579
  KGE≈0.821; drop21 median R²≈0.651 KGE≈0.816; pearson high (~0.93); some sites
  negative R²
- Acceptance result: `pass`
- Decision: Executable dual-variant coupled path demonstrated with ELM comparison evidence; predictive scores characterized; production MCMC readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Production MCMC readiness is not established; some sites show negative R².

## Next Action

1. Idle until a consolidated kickoff package for proposed `iter004` (offline-versus-coupled
   comparison) is approved.

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

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter003.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter003`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter003/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter003_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
