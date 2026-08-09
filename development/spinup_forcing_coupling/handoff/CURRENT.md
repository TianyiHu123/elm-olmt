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

1. Present one complete consolidated Iter008 kickoff package (single-site MCMC diagnostic
   validation) and obtain explicit user approval before initialization.

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
  `spinup_forcing_coupling_iter008_abby_campaign`,
  `spinup_forcing_coupling_iter008_jerc_campaign`, and
  `spinup_forcing_coupling_iter008_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: demonstrate that the locked coupled `drop21_corr080` framework can produce
reproducible, diagnostically interpretable **single-site** SR MCMC results for ABBY and
JERC before another joint-site calibration is considered.

Evidence basis: Iter007's joint 64×500 chain was integrity-valid but exploratory: mean
acceptance 0.1197, mean/max autocorrelation time 54.6/61.3, about 9 steps per τ, and
approximate ESS 93.8. ABBY improved relative to ELM-precal while JERC degraded strongly;
both sites had poor skill and highly autocorrelated residuals. These facts cannot distinguish
site conflict from a site-specific forward-model, observation, likelihood, or sampler issue.

Hypothesis: isolated, longer, same-seed ABBY and JERC chains with raw-chain diagnostics
will distinguish sampler limitation, likelihood limitation, and site-specific limitation
without changing coupled artifacts or scientific inputs.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Iter002 forcing-surrogate-v1 | Coupled `SR` | Immutable; SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup `drop21_corr080` | Coupled spinup state | Immutable; SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY / JERC cases and NEON v4 obs | Per-site targets and likelihood truth | Same Iter007 case pickles, observation paths, and `SR:SR_err` validity mapping; re-lock hashes at kickoff |
| Iter007 products | Baseline comparison | Characterization only; no reinterpretation of Iter007 gates |
| `OLMT_puma` / `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

Core work:

- Implement bounded sampler/diagnostic support: explicit seed control, self-describing
  raw-chain retention, and a combined raw-chain postprocessor that creates the standard
  MCMC product layout plus a comprehensive human-readable diagnostic report.
- Run one ABBY and one JERC coupled single-site chain, each with `--fit-error`, 64 walkers,
  4,000 steps, 16 worker processes, and shared `SEED=8008`. The same seed makes the two
  site runs a controlled paired comparison; no replicate ensembles or `R-hat` claim.
- The sampler job writes immutable `raw_chain.npz` (`[step, walker, parameter]`), matching
  raw log probabilities (`[step, walker]`), initial state, parameter names/bounds, seed,
  configuration, and hashes before invoking the combined postprocessor in the same job.
- The postprocessor uses all eligible raw draws for chain/posterior analysis. It derives
  discard as `max(ceil(0.20*nsteps), ceil(5*tau_max))` and thin as
  `max(5, ceil(tau_max/2))`; if τ is unavailable it records that condition and falls back
  to discard `ceil(0.20*nsteps)` and thin 5. It selects 512 predictive draws deterministically:
  8 evenly spaced eligible draws per walker; if fewer than 512 remain, use every eligible
  draw without duplication. The selection ledger records walker, step, log probability,
  and selected-draw rank.
- Standard artifacts remain required (`best_params.txt`, `clm_params_best.nc`, parameter
  PDFs, corner plot, prediction plots, diagnostics) but expensive posterior-predictive
  outputs use only the selected draws. The raw chain remains outside Git.
- The site diagnostic reports must cover reproducible setup; data/likelihood audit;
  per-walker and per-parameter trace, acceptance, τ, steps/τ, ESS, and stationarity evidence;
  posterior/identifiability and prior-edge evidence; predictive/residual diagnostics; and a
  site conclusion. The final validation tool creates a paired ABBY–JERC comparison and
  evidence-backed next-direction classification.

The current single-site `--fit-error` formulation intentionally fits one site-specific
constant `sigma_SR`. The known order-dependent bound for a **future joint** shared sigma
is excluded from Iter008: before any future joint campaign, its bound must derive from all
sites and be order-invariant. The paired reports will assess whether future joint work needs
shared sigma, site-specific sigmas, or a more substantive likelihood change.

Exclusions: surrogate retraining; coupled interface, schema, feature, case, observation, or
prior changes; site weighting; joint MCMC; multi-variant campaigns; a scientific hard gate;
and Git of raw chains, NetCDF, plots, logs, or other external outputs.

Nominal scheduler tasks: 4 (preflight, ABBY campaign, JERC campaign, validate). Provisional
hard cap: 9 (one preflight rerun; one scheduler/resource retry per site; one raw-chain-only
postprocessor recovery per site). The latter recovery may use a separately submitted bounded
postprocessor only after raw-chain identity is verified; it never resamples.

### 5. Tentative acceptance gates and decision rule

Integrity pass requires all of the following:

1. Authoritative terminal accounting exists for every submitted Iter008 task and every
   failure is classified.
2. Preflight validates both sites' collocation/input identity and the bounded 32-walker ×
   20-step ABBY smoke validates the raw-chain-to-report pipeline. Unavailable τ in this
   deliberately short smoke is reported, not treated as a failure.
3. Both locked 64×4,000 single-site chains complete and their raw chains, metadata, hashes,
   standard products, selection ledgers, and human-readable reports are complete.
4. Missing artifact, observation, schema, provenance, raw-chain-shape, or checksum failures
   fail closed.
5. The paired comparison, `summaries/iter008/`, and the four durable records agree after
   handoff validation.

Sampler quality, sigma behavior, predictive skill, residual structure, and posterior
compatibility are diagnostic evidence, not scientific pass/fail gates. The report must route
the next iteration as one of: sampler-limited; likelihood-limited (including whether a future
joint model needs site-specific sigma); site-specific model/data limitation; joint-calibration
candidate; or inconclusive. A future joint candidate still requires a fresh plan and approval.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only the four run slugs above; a postprocessor recovery, if authorized by the approved package, reuses its verified site campaign directory |
| Preflight | 2 CPUs (derived 10 GB) / 30 min; both-site dry collocation plus ABBY 32×20 smoke |
| Each site campaign | 1 node / 16 CPUs (derived 80 GB) / 4 h / 16 workers; based on Iter007's post-fix 64×500 joint run (18m18s, ~13.6 GB MaxRSS) scaled eightfold with output margin |
| Campaign sequencing | Submit ABBY, verify recorded Slurm identity, then submit JERC; allowed to overlap after both identity checks (peak 32 CPUs / derived 160 GB) |
| Validate | 2 CPUs (derived 10 GB) / 1 h |
| Raw-chain-only recovery | 2 CPUs (derived 10 GB) / 2 h; only against a verified raw-chain checksum and only for an authorized postprocessor/output failure |
| Review | Independent read-only agent before substantive submission |
| Retry | One minimal preflight correction/rerun; one scheduler/resource-only retry per site that preserves model, likelihood, seed, and 64×4,000 budget; one raw-chain-only postprocessor recovery per site |
| Cancellation | Recorded Iter008 job IDs only, under a proven universal pre-execution defect |
| Stop | After terminal accounting, immutable integrity gates, diagnostic decision, durable records, cross-record validation, and the closeout branch selected only in the later kickoff package |

### 7. Expected evidence, artifacts, and record updates

- Per-site campaign directories contain submitted copies/configuration, raw-chain archive and
  metadata/checksums, selection ledger, standard products, diagnostic tables/plots, and the
  human-readable site report.
- `spinup_forcing_coupling_iter008_validate/` contains the paired ABBY–JERC report and
  final validation evidence.
- Compact copies under `summaries/iter008/`; finalized `iterations/iter008.md`;
  `ITERATION_SUMMARY.md` append; `registry.csv` row; rebuilt `handoff/CURRENT.md`; and
  handoff-validator result.
- Canonical source, scripts, manifests, postprocessors, and validators under
  `slurm/iter008/` and the appropriate reusable source locations, with tests for seed/raw-chain
  metadata, selection, and future multi-site sigma-bound order invariance where applicable.

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and states
the exact repository/source lock; approved output-root and directory authority; final resources;
all lifecycle, scheduler, monitoring, retry, cancellation, and outside-sandbox authorities;
and whether one closeout commit is authorized. Obtain one explicit user approval before any
Iter008 initialization, repository implementation, external directory creation, compute-node
Python, scheduler action, or commit.


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
