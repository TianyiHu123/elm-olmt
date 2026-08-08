# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter007`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-08T15:13:30-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter007 closed; Iter008 package not yet presented)
- Kickoff goal and stop boundary: Iter007 complete; awaiting Iter008 consolidated kickoff
  approval for diagnostic-driven MCMC improvement.
- User response and approval timestamp: Iter007 approved `2026-08-07T18:16:45-0700`;
  Iter008 none yet.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md` (for prior Iter007).
- Approved output root: none until Iter008 package approval; proposed root remains
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`.
- Locked dependencies/gates/decision: none until Iter008 approval; see proposed plan.
- Outside-sandbox and closeout authorities: none until Iter008 package approval.

## Current Objective

Joint ABBY+JERC coupled/drop21_corr080 SR MCMC campaign

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: ABBY+JERC joint; coupled drop21_corr080; SR; 64x500; flat campaign layout; suggested diagnostics; integrity-only
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter007`
- Prior evidence: Preflight `23520801` pass; campaign `23523645` `CAMPAIGN_PASS`
  (after TIMEOUT/OOM `23520817` and postprocess fail `23523589`); validate `23523701`
  `VALIDATE_PASS`; mean acceptance ≈0.120; approx ESS ≈94
- Forcing identity: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Acceptance result: `pass`
- Decision: Joint ABBY+JERC production MCMC campaign executed successfully through the locked coupled interface and wrote required products; diagnostic contents are characterization only; calibrated scientific adequacy not claimed

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Iter007 chain health and predictive skill remain weak (characterization only).
- Awaiting one approval of a complete Iter008 consolidated kickoff package.

## Next Action

1. Present one complete consolidated Iter008 kickoff package (diagnostic-driven MCMC
   improvement) and obtain explicit user approval before initialization.

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter008`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter008`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter008_preflight`,
  `spinup_forcing_coupling_iter008_campaign`,
  `spinup_forcing_coupling_iter008_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: improve Iter007 joint ABBY+JERC coupled/`drop21_corr080` SR MCMC chain health
and predictive characterization under the same locked coupling primitives, using
diagnostic-driven sampler budget changes (walkers/steps/thin/discard and optional
site weighting or error model), without retraining surrogates or changing the coupled
interface schema.

Evidence basis: Iter007 passed integrity gates (`CAMPAIGN_PASS`/`VALIDATE_PASS`) with
mean acceptance ≈0.120, approx ESS ≈94, and negative R²/KGE for optimized SR at both
sites; ABBY ΔlogL vs ELM-precal positive while JERC ΔlogL strongly negative.

Optional hypothesis: longer, better-mixed chains and/or site-aware likelihood weighting
will yield more usable posterior predictive characterization without changing coupling
artifacts.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 | Coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop21_corr080` | Coupled spinup state | Immutable; SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| Iter007 campaign products | Baseline diagnostics | Reuse characterization only; do not reinterpret Iter007 gates |
| Cases / obs | Joint targets | Same ABBY+JERC cases and NEON v4 obs paths; re-lock hashes at kickoff |
| `OLMT_puma` / `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work:

- One diagnostic-driven joint MCMC campaign on ABBY+JERC under coupled/`drop21_corr080`.
- Allowed changes: `nwalkers`/`nsteps`/discard/thin, optional obs-error / site-weight
  configuration already supported by the MCMC forcing path, and resource retune from
  Iter007 seff evidence (~14 GB / 24 CPUs wall ~18 min for 64×500).
- Retain flat campaign layout and suggested diagnostics; integrity-only gates unless the
  kickoff package explicitly adds numeric floors.
- Ladder: preflight → campaign → validate/accounting.

Exclusions: surrogate retraining; coupling schema changes; multi-variant campaigns;
reinterpretation of Iter007 integrity gates; Git of large binaries/NetCDF/chains.

Nominal scheduler tasks: 3 (preflight, campaign, validate). Provisional hard cap: 5
(one minimal preflight correction; one resource-limitation campaign retune).

### 5. Tentative acceptance gates and decision rule

Pass only if all hold (integrity only unless kickoff adds floors):

1. Authoritative terminal accounting exists for every task; every failure is classified.
2. Campaign completes the locked sampler budget under coupled/`drop21_corr080`.
3. Required products exist under the approved campaign layout including diagnostics.
4. Negative gates for missing artifact/obs/schema failures fail closed.
5. Compact `summaries/iter008/` and the four durable records agree after handoff validation.

Decision rule: pass means the diagnostic-driven joint campaign executed successfully and
wrote required products; skill/ESS/acceptance remain characterization unless explicitly
gated at kickoff.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter008_{preflight,campaign,validate}/` |
| Preflight | 2 CPUs (derived ~10 GB) / 30 min |
| Campaign | start from Iter007 seff (~24 CPUs / ≥40 GB / wall sized to locked budget) |
| Validate | 2 CPUs (derived ~10 GB) / 1 h |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one resource-limitation campaign retune |
| Cancellation | recorded Iter008 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

- Campaign products under `spinup_forcing_coupling_iter008_campaign/`; compact
  `summaries/iter008/`; finalized `iterations/iter008.md`; `ITERATION_SUMMARY.md` append;
  `registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result
- Canonical scripts under `slurm/iter008/`

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, locked sampler budget,
and closeout-commit authorization. Obtain one explicit user approval before any Iter008
initialization.


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

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter007.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter007`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter007/`
- Submitted scripts/configurations: under each `spinup_forcing_coupling_iter007_*` run dir
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
