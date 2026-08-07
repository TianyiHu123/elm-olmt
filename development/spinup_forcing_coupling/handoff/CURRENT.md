# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter004`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-06T18:46:47-0700`

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

1. Idle until a consolidated kickoff package for proposed `iter005` (mean-spinup offline
   baseline vs Iter004 arms) is approved.


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
