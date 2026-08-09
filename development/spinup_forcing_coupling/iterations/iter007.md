# iter007 - Joint ABBY+JERC coupled drop21_corr080 SR MCMC

## Status

- Iteration ID: `iter007`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter007_preflight`,
  `spinup_forcing_coupling_iter007_campaign`,
  `spinup_forcing_coupling_iter007_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-07T18:16:45-0700`
- Closed: `2026-08-08T15:13:30-0700`
- Bounded scope: ABBY+JERC joint; coupled drop21_corr080; SR; 64x500; flat campaign layout; suggested diagnostics; integrity-only
- Objective: Joint ABBY+JERC coupled/drop21_corr080 SR MCMC campaign
- Acceptance result: `pass`
- Decision: Joint ABBY+JERC production MCMC campaign executed successfully through the locked coupled interface and wrote required products; diagnostic contents are characterization only; calibrated scientific adequacy not claimed
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter007`
- Forcing identity: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`

## Finalized Plan

The finalized plan is the unchanged planning-only proposal recorded at Iter006 closeout /
plan refinement in `handoff/CURRENT.md` and `iterations/iter006.md`, planning-body SHA-256 (after Puma resource clarification aligned to approved package)
`009e80d547114aba2d8a9113c2515c6ad7eadf3898dc37d9aab47a230919d4b0`.

- Sequential ID and work type: `iter007`; `implementation`.
- Objective: Joint ABBY+JERC coupled/drop21_corr080 SR MCMC campaign; products under campaign run dir without
  `UQ_output/`; integrity-only gates.
- Optional hypothesis: coupled `drop21_corr080` preferred first campaign arm.
- Upstream dependencies / scope / gates / resources / evidence / approval boundary: as in
  the approved consolidated package below (plan body unchanged).

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approve for plan + contract + outside-sandbox 1–3 + closeout commit`; accepted `2026-08-07T18:16:45-0700`. Interpretation: approve the complete consolidated package including plan, runtime contract, outside-sandbox items 1–3, and one local closeout commit. |
| Kickoff goal, finite work-unit count, and stop conditions | Joint ABBY+JERC coupled/`drop21_corr080` SR MCMC; 3 nominal / 5 hard-cap scheduler tasks; stop after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |
| Confirmed HPC system and site profile | University of Arizona Puma, host `junonia.hpc.arizona.edu`; `development/hpc/puma.md` |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to `spinup_forcing_coupling_iter007_{preflight,campaign,validate}/`; `/xdisk` temporary and unbacked; no Git of large binaries/NetCDF/chains; campaign products at campaign run-dir root (no `UQ_output/`) |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact finalized plan; forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; obs ABBY `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`; obs JERC `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f`; cases `ABBY_ppe6_I20TRCNPRDCTCBC`,`JERC_ppe6_I20TRCNPRDCTCBC`; `64×500`; `--fit-error`; integrity-only |
| Lifecycle authority | Initialization, preparation, repository changes, exact external directory creation, compute-node Python, independent read-only review, preflight, campaign, validate, continuous monitoring, accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs (derived ~10 GB) / 30 min; campaign retuned to `--cpus-per-task=24` (derived ~120 GB) / 12 h / `--n-processes=16` after TIMEOUT/OOM; validate 2 CPUs (derived ~10 GB) / 1 h; one minimal preflight correction/rerun; one resource-limitation campaign retune of only `nsteps`/`nwalkers`/`mem`/`cpus`; no automatic application/numerical/diagnostic-driven retry |
| Cancellation scope | `scancel` only for recorded current-iteration job IDs when a proven universal pre-execution defect invalidates affected active work; cancellation grants no fix or retry |
| Outside-sandbox authority | Granted: locked `sbatch` and allowed resubmission; job-scoped `squeue`/`scontrol show job`/`sacct`/`seff`/`job-history`/`job-limits`; bounded `scancel` for recorded Iter007 job IDs under contract cancellation conditions |
| Closeout branch | At most one local closeout commit after terminal accounting and passing validation; bounded implementation/tests/docs/iteration material/summaries/records only; raw outputs, NetCDF, models, logs excluded; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Forcing surrogate | Coupled `SR` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release |
| Spinup `drop21_corr080` | Coupled state | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `spinup-surrogate-v1` | SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | Iter012 release |
| Obs ABBY | Likelihood | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` | NEON v4 | SHA-256 `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` | User-locked path |
| Obs JERC | Likelihood | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc` | NEON v4 | SHA-256 `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` | User-locked path |
| ABBY case | Joint target | `pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl` | 100 members | hash in `iter007_case_pickles.sha256` | Prior coupling trust |
| JERC case | Joint target | `pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl` | 100 members | hash in `iter007_case_pickles.sha256` | Prior coupling trust |

- Repository parent at closeout: `4051e875bff93742bdf5ccfb69a94a9ce10468c1` (dirty bounded Iter007 worktree locked by source manifest before commit).
- Bounded source manifest: `slurm/iter007/iter007_source_manifest.sha256`.
- Environment identity: `OLMT_puma` / `micromamba/2.0.2-2`.

## Acceptance Gates and Decision Rule

- Required completeness: authoritative terminal accounting; campaign products under approved
  layout; suggested diagnostics present; four durable records agree after closeout validation.
- Acceptance gates: integrity only (as finalized plan).
- Decision rule: pass means the joint ABBY+JERC production MCMC campaign executed
  successfully through the locked coupled interface and wrote the required products.
  Diagnostic contents are characterization, not numeric floors.
- Changes requiring fresh authorization: application/code/interface/schema/data/dependency/
  numerical repair after locks; resource-cap or scientific-scope change beyond one authorized
  resource-limitation retune; task beyond the 5-task hard cap; gate reinterpretation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter007.slurm`; `preflight_config.env` | byte-equal submitted copies in run dir | `spinup_forcing_coupling_iter007_preflight/`; logs `preflight_23520801.{out,err}` | forcing + spinup + obs + cases | parent `4051e87…`; source manifest | `23520801` | COMPLETED 0:0 elapsed 00:01:11; MaxRSS ~9.05/10 GB; `PREFLIGHT_PASS` | — |
| campaign | `campaign_iter007.slurm`; `campaign_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter007_campaign/`; logs `campaign_23523645.{out,err}` | preflight `23520801` pass | same + MP/prior fixes | `23520817`, `23523589`, `23523645` | `23520817` TIMEOUT+OOM; `23523589` FAILED postprocess OOB; `23523645` COMPLETED 0:0 elapsed 00:18:18; MaxRSS ~13.59/120 GB; `CAMPAIGN_PASS` | one authorized resource retune (24 CPUs); prior `-inf` + `POSTPROCESS_FILTER` fix before third attempt (hard-cap 4/5) |
| validate | `validate_iter007.slurm`; `validate_config.env` | byte-equal submitted copies | `spinup_forcing_coupling_iter007_validate/`; logs `validate_23523701.{out,err}` | campaign `23523645` pass | same | `23523701` | COMPLETED 0:0 elapsed 00:00:11; MaxRSS ~12 MB; `VALIDATE_PASS` | hard-cap task 5/5 |

## Independent Read-Only Review

- Reviewer: independent read-only agent (re-review after authority/resource/negative fixes)
- Reviewed source hash: source-manifest file SHA-256 recorded at preflight submission.
- Outcome: `pass_with_concerns` then proceed; residual concerns tracked through execution.
- Findings and primary-agent response: Prior blocks repaired before preflight. Runtime
  hang/OOM and postprocess OOB classified and repaired within approved resource retune /
  application-fix path authorized by user directives and remaining hard-cap room.

## Execution and Diagnostics

- Static validation: `bash -n` Slurm OK; `py_compile` OK; source manifest `sha256sum -c` OK.
- Preflight `23520801`: `PREFLIGHT_PASS`; collocation ABBY 26280 / JERC 52560.
- Campaign `23520817`: TIMEOUT 12:00:08; batch OUT_OF_MEMORY (49 oom_kill); never `run_mcmc done`;
  classified scheduler/resource hang from pickling full ELM cases into Pool workers.
- Campaign `23523589`: MCMC completed (`run_mcmc done`, flat samples 5120×15) then FAILED in
  postprocess (`Parameters outside ensemble_pmin/pmax`); prior used finite sentinel; classified
  application/numerical failure; fixed with `-np.inf` OOB reject + in-bounds postprocess filter.
- Campaign `23523645`: `CAMPAIGN_PASS`; `POSTPROCESS_FILTER kept=5120/5120`; mean acceptance
  0.1197; approx ESS 93.8; products at campaign root without `UQ_output/`.
- Validate `23523701`: `VALIDATE_PASS`; compact summaries under `development/spinup_forcing_coupling/summaries/iter007`.
- Characterization (not gates): ABBY optimized_best RMSE 5.33 / R² -3.12; JERC optimized_best
  RMSE 2.46 / R² -7.36; ABBY ΔlogL vs ELM-precal +1.42e5; JERC ΔlogL -4.47e7.

### Code bug / fix log (campaign)

| Job | Failure class | Symptom | Root cause | Fix | Files |
| --- | --- | --- | --- | --- | --- |
| `23520817` | Scheduler/resource hang → TIMEOUT + OOM | 12 h wall with AveCPU stuck ~7.5 min; MaxRSS at 80 GB ceiling; 49 `oom_kill`; never `run_mcmc done` | emcee `Pool` workers received full coupled site payloads including ~GB-scale ELM case objects; repeated pickling/shipping of those objects hung progress and exhausted memory | Pre-extract slim arrays (`prepare_coupled_site_arrays` / `predict_coupled_sr_prepared`); pass arrays + artifact paths only; `Pool(initializer=...)` so workers load shared state once; keep `n_processes=16` (no serial fallback) | `model_ELM/coupled_surrogate.py`, `model_ELM/MCMC_forcing.py` |
| `23523589` | Application/numerical postprocess failure | MCMC finished (`run_mcmc done`, flat samples 5120×15) then FAILED writing predictive outputs: `ValueError: Parameters outside ensemble_pmin/pmax`; chain means polluted (~1e42) while best-fit looked in-bounds | OOB proposals returned a finite prior sentinel instead of `-inf`, so emcee retained invalid walkers that later broke `normalize_physical_parameters` | `log_posterior_forcing` returns `-np.inf` on OOB; filter flat samples to in-bounds + finite log-prob (`POSTPROCESS_FILTER`) before `_mcmc_write_outputs` / diagnostics | `model_ELM/MCMC_forcing.py` |
| `23523645` | — (success) | `CAMPAIGN_PASS`; `POSTPROCESS_FILTER kept=5120/5120` | — | Confirms both fixes under the same 64×500 / 16-worker coupled path | — |

Notes: the TIMEOUT was not under-provisioned CPUs; it was a multiprocessing payload bug. The 24-CPU / 120 GB retune was an authorized resource response during the hang/OOM path and proved oversized once the pickle fix landed.

### Campaign resource usage and recommended allocation (2-site)

Observed `seff` / `sacct` for the three campaign attempts (joint ABBY+JERC, coupled/`drop21_corr080`, `64×500`, `--n-processes=16`):

| Job | Allocated | Wall | Memory used | CPU efficiency | Outcome |
| --- | --- | --- | --- | --- | --- |
| `23520817` | 16 CPUs / 80 GB / 12 h | 12:00:08 | 80.00 GB (100% of request) | 0.07% | TIMEOUT + OOM (pre-fix) |
| `23523589` | 24 CPUs / 120 GB / 12 h | 00:05:54 | 11.10 GB (9.3%) | 38.4% | MCMC OK; FAILED postprocess |
| `23523645` | 24 CPUs / 120 GB / 12 h | 00:18:18 | 13.59 GB (11.3%) | 20.4% | `CAMPAIGN_PASS` |

Recommended allocation for the same 2-site MCMC shape (after the payload fix):

| Setting | Recommendation | Rationale |
| --- | --- | --- |
| CPUs | 16 (`--cpus-per-task=16`, `--n-processes=16`) | Match worker count; 24 was unused headroom |
| Memory | 32–40 GB | Observed ~14 GB; ~2–3× headroom for peaks / plot postprocess |
| Walltime | 1–2 h | Observed ~18 min; leave margin for longer chains |
| Nodes | 1 | Single-node `Pool` |

Do not re-request 80–120 GB for this shape unless slim payloads regress. Scale walltime first when increasing `nsteps` or site count.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | authoritative `23520801` `COMPLETED 0:0`; `PREFLIGHT_PASS` | pass | hashes, imports, dry-run collocation, negatives |
| campaign | yes | authoritative `23523645` `COMPLETED 0:0`; `CAMPAIGN_PASS`; required products present | pass | locked 64×500 coupled/`drop21_corr080` completed after authorized resource retune + postprocess fix |
| validate | yes | authoritative `23523701` `COMPLETED 0:0`; `VALIDATE_PASS` | pass | layout + diagnostics integrity; no `UQ_output` nesting |

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: Joint ABBY+JERC production MCMC campaign executed successfully through the locked coupled interface and wrote required products; diagnostic contents are characterization only; calibrated scientific adequacy not claimed
- Limitations: temporary `/xdisk` retention; acceptance≈0.12 and ESS≈94 indicate limited mixing;
  predictive skill remains poor vs obs (characterization only); JERC optimized ΔlogL worse than
  ELM-precal; no numeric skill floors applied.
- Next action: closeout commit after four-record validator pass; then present Iter008 package.

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


## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter007/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
