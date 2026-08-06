# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter002`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-05T19:05:00-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter002 closed)
- Kickoff goal and stop boundary: publish identity-locked, inference-validated
  `forcing-surrogate-v1`; stop after terminal accounting, immutable gates, durable
  records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response `approved, yes and yes.`; accepted
  `2026-08-03T18:38:23-07:00`. Release-retry amendment accepted `2026-08-04T16:48:00-07:00`.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with Iter002 run dirs only.
- Locked dependencies/gates/decision: amended package (full-data refit; 100-seed aggregate
  baseline characterization only; inference + ABBY operational validate).
- Outside-sandbox and closeout authorities: exhausted with Iter002 closeout.

## Current Objective

Identity-locked forcing-surrogate-v1 full-data release with inference validation

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: Nine sites; SR; full-data forcing-surrogate-v1; 8-repeat full-data importance; inference validation; ABBY operational predict; no live coupling
- Upstream dependency identities: source-manifest `ea7ec3f35b452c78b21ac710079004dcd083867c95d4262342c6bc4a8bf46ab2`; memmap
  `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`; artifact `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; inference summary
  `44e493d65b770aedec83ef2d75978c2ff7857f49fe0c79550df848c87af3c20e`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter002`
- Preflight `23491474` pass; historical release `23497577` fail (reproduction); amended
  release `23501708` pass; authoritative validate `23507103` pass
- Acceptance result: `pass`
- Decision: Standalone forcing-surrogate-v1 artifact identity-locked and inference-validated; full-data importance characterized; live coupling readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Accidental validate multi-submit is classified and closed (pending duplicates cancelled).

## Next Action

1. Idle until a consolidated kickoff package for proposed `iter003` is approved.

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
  `spinup_forcing_coupling_iter003_pilot`,
  `spinup_forcing_coupling_iter003_full`, and
  `spinup_forcing_coupling_iter003_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: build a reusable coupled spinup→forcing interface compatible with both released
`spinup-surrogate-v1` variants (`drop32` and `drop21_corr080`) and the closed Iter002
`forcing-surrogate-v1` artifact; run coupled `SR` predictions against pickle-linked ELM PPE
histories; publish per-site/per-member metrics, feedback diagnostic plots, and optional
timeseries; ship a public CLI/library primitive reusable later by MCMC.

Evidence basis: Iter002 closed `pass` with identity-locked full-data artifact
SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` and
inference/`ABBY` operational validation; spinup Iter012 released both variants but validated
only forcing-bridge design-matrix compatibility, with no real SR coupling.

Optional hypothesis: a MCMC-ready predict primitive plus a PPE batch client (pilot then full
9-site campaign) is sufficient to demonstrate executable coupled skill characterization
against ELM without numeric accuracy gates or an MCMC campaign in Iter003.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Closed Iter002 artifact/manifest/validation/importance | Forcing surrogate | Immutable read-only; lock artifact SHA-256 `8d139b32...` |
| Iter012 `drop32` spinup-surrogate-v1 | Spinup state surrogate | Immutable; path/hash locked at kickoff |
| Iter012 `drop21_corr080` spinup-surrogate-v1 | Compact spinup variant | Immutable; path/hash locked at kickoff |
| Nine case pickles and linked PPE ELM histories | Cases, parms, ELM `SR` reference | Same trust model as prior coupling iterations; re-verify identity in preflight |
| `forcing_surrogate_artifact` / `spinup_surrogate_artifact` APIs | Public load/predict | Repository commit and source manifest locked at preparation |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core deliverable (MCMC-ready):

- Public library API plus CLI `predict_coupled_surrogate.py`.
- Primitive contract:
  `(case, parameter vector(s), spinup variant, forcing artifact) → predicted TOTSOMC/TOTSOMN + SR timeseries (+ time axis)`.
- PPE evaluation, ELM compare, metrics, and plots are a separate batch client on top of that
  primitive (not PPE-only glue).

Evaluation ladder (same iteration):

1. Preflight: imports, artifact identity, API smoke.
2. Pilot: `ABBY` × ensemble members 1–5 × both spinup variants; timeseries save **ON**.
3. Full: nine sites × all PPE members × both spinup variants; timeseries save **OFF**.
4. Validate / aggregate / closeout: accounting, durable records, handoff validation.

ELM reference: PPE histories already referenced by the nine case pickles.

Metrics (characterization only): R², RMSE, bias, MAE, Pearson r, KGE — persisted per site and
per member within site; summary report shows only per-site medians over members.

Diagnostic plots (required for both pilot and full; per site × spinup variant):

1. Mean `SR` ± temporal std vs ensemble member index (ELM vs coupled overlay).
2. Mean `SR` ± temporal std vs `TOTSOMC` and vs `TOTSOMN` (coupled x-axis uses
   spinup-surrogate-predicted states; ELM x-axis uses ELM spinup states).

Timeseries storage: compressed NetCDF when `--save-timeseries` (or equivalent) is enabled —
dims `(member, time)` with `SR_coupled`, `SR_elm`, time axis, and spinup scalars. Pilot ON;
full OFF. Full run still writes metrics tables, member summary columns needed for plots, and
figures.

Exclusions: MCMC optimization campaign; retraining either surrogate; feature selection;
numeric accuracy or coupling-readiness thresholds beyond functional/integrity gates; Git of
large binaries; expanding beyond the declared pilot/full populations.

Nominal scheduler tasks: 4. Provisional hard cap: 7 (one minimal preflight correction/rerun
and one same-scope scheduler/resource retry across pilot/full/validate).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Both spinup variants and the forcing artifact load under their versioned APIs.
3. Pilot completes for `ABBY` members 1–5 × both variants with finite coupled `SR`, ELM
   alignment, metrics, plots, and NetCDF timeseries.
4. Full campaign completes for nine sites × all PPE members × both variants with finite
   metrics, member summaries, and plots (no full timeseries writes).
5. Negative gates for schema/version/load failures fail closed.
6. Compact `summaries/iter003/` and the four durable records agree after handoff validation.

Decision rule: pass means the coupled interface is executable, dual-variant compatible,
ELM-compared, and evidence-complete for later MCMC reuse. Predictive scores and feedback
plots are characterization only. Pass does not claim production MCMC readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter003_{preflight,pilot,full,validate}/` |
| Preflight / pilot / full / validate | finalize exact CPU/mem/time at kickoff from fixture and full-campaign sizing |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed pilot/full/validate; no automatic application/numerical retry |
| Cancellation | recorded Iter003 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- `predict_coupled_surrogate.py` and library API under repository paths locked at preparation
- Pilot NetCDF timeseries (ABBY × 5 members × both variants)
- Per-site/per-member metrics tables; summary tables with per-site medians over members
- Feedback diagnostic plots for pilot and full
- Compact `summaries/iter003/`; finalized `iterations/iter003.md`; `ITERATION_SUMMARY.md`
  append; `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter003/` (created only after kickoff approval)

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter003 initialization.


## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Read `iterations/iter002.md` in full and up to two preceding reports.
3. Read registry/summary evidence and the proposed plan above.
4. Inspect Git state and reconcile scheduler/artifact state before any new kickoff.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter002.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter002/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter002/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
