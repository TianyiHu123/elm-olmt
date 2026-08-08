# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter006`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-07T18:10:00-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter006 closed; Iter007 plan fields resolved; package not yet
  presented)
- Kickoff goal and stop boundary: Iter006 complete; awaiting Iter007 consolidated kickoff
  approval for the joint ABBY+JERC coupled production MCMC campaign described below.
- User response and approval timestamp: Iter006 approved `2026-08-06T20:31:00-0700`;
  Iter007 none yet.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md` (proposed for Iter007).
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
- Iter006 validate smoke approached the 5 GB memory allocation; campaign uses a larger envelope.
- Iter007 planning fields are resolved; awaiting one approval of the complete consolidated
  kickoff package (plan below is planning-only until then).

## Next Action

1. Present one complete consolidated Iter007 kickoff package (joint ABBY+JERC coupled
   MCMC campaign) and obtain explicit user approval before initialization.

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
