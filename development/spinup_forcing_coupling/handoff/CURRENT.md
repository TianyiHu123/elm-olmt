# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter006`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-06T21:11:23-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter006 closed; Iter007 package not yet presented)
- Kickoff goal and stop boundary: Iter006 complete; awaiting Iter007 consolidated kickoff
  approval for a production MCMC campaign.
- User response and approval timestamp: Iter006 approved `2026-08-06T20:31:00-0700`;
  Iter007 none yet.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md` (for prior Iter006).
- Approved output root: none until Iter007 package approval; proposed root remains
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`.
- Locked dependencies/gates/decision: none until Iter007 approval; see proposed plan.
- Outside-sandbox and closeout authorities: none until Iter007 package approval.

## Current Objective

MCMC three-mode spinup wiring (mean / member-restart / coupled)

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: ABBY smoke; three MCMC spinup modes; coupled drop32/drop21_corr080; <=10 likelihood evals/mode; no production campaign
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter006`
- Prior evidence: Iter006 ABBY smoke exercised mean_spinup, member_restart, and coupled
  (default `drop21_corr080`) with 10 likelihood evals each; coupled `drop32` accepted
- Forcing identity: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Acceptance result: `pass`
- Decision: MCMC can select and call locked coupling/offline primitives under each declared spinup mode; mean/member-restart paths still work; production campaign readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Validate smoke approached the 5 GB memory allocation.
- Awaiting one approval of a complete Iter007 consolidated kickoff package.

## Next Action

1. Present one complete consolidated Iter007 kickoff package (production MCMC campaign)
   and obtain explicit user approval before initialization.

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

Objective: run a bounded production MCMC campaign through the Iter006 three-mode
`--spinup-mode` interface on a predeclared site set and mode choice, writing posterior
and predictive products under the locked output root, without retraining or changing the
coupling primitives.

Evidence basis: Iter006 passed wiring gates for mean_spinup, member_restart, and coupled
(`drop21_corr080` default; `drop32` accepted). Production campaign readiness remains
unestablished until a real obs-constrained sampler run completes under immutable gates.

Optional hypothesis: coupled mode with `drop21_corr080` is the preferred first campaign
arm given Iter004/005 skill characterization; confirm or revise at kickoff.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 artifact | Offline/coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop32` / `drop21_corr080` | Coupled state if selected | Immutable Iter012 hashes |
| Iter006 MCMC mode wiring | CLI/likelihood path | Lock repository identity at kickoff |
| Site obs NetCDF(s) | Likelihood truth | Paths/hashes locked at kickoff (not smoke fixtures) |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work: one production MCMC campaign using a single locked `--spinup-mode` (and coupled
variant if applicable), locked site list, walker/step budget, and obs paths; preflight;
campaign; validate/accounting. Exact site list, mode, and sampler budget locked at kickoff.

Exclusions: retraining; feature selection; multi-mode simultaneous campaigns unless
explicitly authorized; Git of large binaries/NetCDF/chains; reinterpretation of Iter006
wiring gates.

Nominal scheduler tasks: 3 (preflight, campaign, validate). Provisional hard cap: 5
(one minimal preflight correction/rerun; one same-scope scheduler/resource retry).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold:

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Campaign completes the locked walker/step budget under the locked spinup-mode without
   schema/import failures.
3. Required posterior/predictive products exist under the approved output layout.
4. Negative gates for missing artifact/obs/schema failures fail closed.
5. Compact `summaries/iter007/` and the four durable records agree after handoff validation.

Decision rule: pass means a production MCMC campaign executed successfully through the
locked three-mode interface for the predeclared mode/site budget. Pass does not by itself
claim calibrated scientific adequacy unless numeric skill floors are explicitly added at
kickoff.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter007_{preflight,campaign,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Campaign | resources locked at kickoff from walker/step/site evidence (Iter006 validate used ~5 GB) |
| Validate | 1 CPU (derived ~5 GB) / 1 h |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry; no automatic application/numerical retry |
| Cancellation | recorded Iter007 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- Campaign posterior/predictive products under approved run dirs; compact
  `summaries/iter007/`; finalized `iterations/iter007.md`; `ITERATION_SUMMARY.md` append;
  `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter007/` (created only after kickoff approval)

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, locked mode/site/obs
budget, and closeout-commit authorization. Obtain one explicit user approval before any
Iter007 initialization.

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

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter006.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter006`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter006/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter006_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
