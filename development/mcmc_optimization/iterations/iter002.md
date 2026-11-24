# iter002 - NEON Observation Preparation and Fixed-Uncertainty Release

## Status

- Iteration ID: `iter002`
- Work type: `audit | implementation | integration | validation | release`
- Run slug: `iter002_neon_observation_preparation`
- Status: `completed`
- Phase: `closeout`
- HPC profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Started: `2026-11-23T22:44:55-07:00`
- Closed: `2026-11-24T04:26:44-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Locked plan SHA-256: `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`
- Applicable campaign phase: observation and flux-likelihood preparation plus fixed C/N inputs
- Alignment: `aligned`; approved deviation: `none`
- Historical Iter001 remains locked to plan `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`.

## Consolidated Kickoff Approval and Runtime Contract

- User direction: `MCMC Optimization — Iter002 Kickoff`, received `2026-11-23`.
- User approval: `approve this complete package`, received after the consolidated package at
  `2026-11-23T22:44:55-07:00`.
- Goal: publish one immutable ABBY/JERC observation and fixed-uncertainty release for GPP, SR,
  TOTSOMC, and TOTSOMN; stop after Iter002 closeout with a planning-only Iter003 proposal.
- Work units: source audit; strict loading and flux preparation; soil C/N and fixed uncertainty
  integration; staged validation and catalog-last publication.
- Exclusions: no posterior, Sobol search, optimization, MCMC, surrogate retraining, PPE2 science,
  ELM/spinup preprocessing, Iter015 replay, redundant depth figures, historical-record edits, push,
  merge, or Iter003 implementation.
- Runtime root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation`.
- Publication root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`.
- Storage cap: 5 GiB of new Iter002 runtime plus publication products; no automatic cleanup.
- Puma: account `chopinsong`, partition `standard`, CPU-only, `OLMT_puma`, one node/task,
  2 CPUs and approximately 10 GB per job, one-thread numerical libraries.
- Planned jobs: preflight 10 min; source audit 15 min; flux preparation 30 min; uncertainty 15 min;
  publication 15 min; final validation 15 min.
- Submission cap: six planned attempts, one bounded minimal preflight correction, and at most two
  scheduler-only retries, for at most nine attempts. No automatic application, schema, data,
  scientific, numerical, OOM, or timeout retry.
- Subsequent user authority on 2026-11-23 added one preflight recovery and a shared three-retry
  pool for all later jobs. That later pool is exhausted after two source-audit retries and one
  publication retry; no further application submission is authorized.
- Monitoring: job-scoped `squeue` while active and terminal `sacct` for every attempt. Empty queue
  state is not completion.
- Cancellation: exact recorded Iter002 jobs only for identity drift, output collision, protected
  member misuse, storage breach, wrong scope, or explicit user direction; account afterward.
- Closeout: at most one scoped local no-push commit; the pre-existing untracked amendment patch is
  excluded and untouched.

## Locked Scientific Configuration

- GPP source: site `*_neon_eval_hourly.nc`; paired finite `GPP_DT` and `GPP_NT`; source units
  `gC/m^2/s`; normalize `HH:15` to `HH:00` by removing minutes; convert by exactly 86400.
- GPP hourly values: `raw=(DT+NT)/2`, `halfdiff=(DT-NT)/2`, `gated=max(0,raw)`; gate hourly before
  daily aggregation while retaining raw and gate-after-daily diagnostics.
- GPP daily eligibility: at least 18 paired hours; daily value is the mean over those exact hours.
- SR daily eligibility: at least 22 valid hours; preserve its independent window and mask.
- GPP observation sigma: `max(abs(halfdiff), 0.10*abs(raw), 0.05)` in `gC/m^2/day`.
- SR sigma: valid positive `SR_err` where present, else `max(0.10*abs(SR), 0.05)` in the same units.
- Daily observation sigma: RMS of retained hourly sigmas; never divide by `sqrt(n)` or `sqrt(24)`.
- Strict loading fails on calendar conversion, duplicates, unsorted time, dimension/shape/unit
  mismatch, invalid configured errors without declared fallback, or silent truncation. Legacy entry
  points retain legacy behavior and tests.
- Soil observations: transferred processed CSV SHA-256
  `1869761ef73ac9b7c7789d29c516523cfd0895d6c0c53031e6bf4a147ac22afa`.
- PPE1 depth inputs: ABBY `82261198...b358`, JERC `c6fa8500...f61`; use all 1,024 members with
  sample covariance estimator `N-1` and preserve the non-independence caveat.
- C/N observation CV cases: 0.20, 0.30 baseline, 0.50; diagonal log variance `log(1+CV^2)`.
- Surrogate uncertainty: Iter015 handoff `c9282bb...436`, product manifest `293277a8...7e9`, final
  validation `fed360f8...e2b6`; fixed-test access false; no refit or recalibration.
- Flux surrogate RMSE is reused unchanged, with no flux bias correction. C/N uses the fixed sum of
  development-only surrogate mean log error and full-ensemble depth mean log error.
- Iter015 daily surrogate errors use full 24-hour model days; applying them to 18--23 observed-hour
  means is a documented approximation, not recomputation authority.

## Immutable Acceptance Gates and Decision

1. Source integrity and provenance match every locked hash/schema; critical absence or drift fails.
2. Time/unit validation passes for minute removal, no-leap conversion, uniqueness, masks,
   site-specific windows, 720-hour history, and exact 86400 conversion.
3. GPP identities and hourly zero gate pass at `rtol=1e-12`, `atol=1e-12`; raw negatives remain.
4. Daily indices, masks, counts, means, RMS errors, and 18/20/22/24 diagnostics reproduce at
   `rtol=1e-12`, `atol=1e-12`; SR is independently defined.
5. Observation-error precedence, positive floors, source flags, and JERC fallback pass; no
   undocumented square-root reduction occurs.
6. Soil stocks/depths and full-ensemble fractions, means, and covariance pass at `rtol=1e-12`,
   `atol=1e-12`, with agreement to prior printed precision and no duplicate preprocessing.
7. Iter015 products are reused unchanged and remain development-only for surrogate uncertainty.
8. NetCDF/JSON schemas, reloads, hashes, manifest/catalog, covariance symmetry `<=1e-14`, and
   Cholesky tests pass.
9. Three figures/tables, independent reviews, terminal accounting, durable records, and four-record
   validation pass.

All gates pass -> `observation_release_0001_published`. Any failure -> no catalog/publication,
classify and stop. Gate relaxation or source/scientific-contract change requires fresh approval.

## Provenance and Work-Unit Ledger

| Work unit | Canonical material | Job scope | State | Notes |
| --- | --- | --- | --- | --- |
| preparation | `development/mcmc_optimization/slurm/iter002/` | none | complete | canonical/submitted identity chain verified |
| preflight | script `1b241672...7edb` | `24794462`; `24794655`; `24794902` | passed on attempt 3 | two classified harness failures; `24794902` COMPLETED `0:0` |
| source audit | `results/source_audit.json` | `24794997`; `24795247`; `24795589` | passed on retry 2 | two fail-closed expectation/diagnostic failures; `24795589` COMPLETED `0:0` |
| flux preparation | staged flux products and two figures | `24795706` | passed | COMPLETED `0:0`; 514/699 GPP and 1095/2114 SR eligible days |
| uncertainty | staged C/N products and uncertainty figure | `24795812` | passed | COMPLETED `0:0`; full 1,024-member depth and unchanged Iter015 inputs |
| publication | catalog-last transaction | `24795941`; `24796001`; `24797797` | passed | two classified pre-write validator failures; authorized correction; `24797797` COMPLETED `0:0` |
| final validation | published reload and gate validation | `24797845` | passed | COMPLETED `0:0`; 18 products and 12,243,802 combined bytes validated |

## Independent Read-Only Review

- Initial package review: independent read-only reviewer `/root/iter002_package_review` returned
  `block`. It identified missing pre-Python runtime identity checks, unverified Iter015 numerical
  tables, incomplete independent daily/depth validation and diagnostics, missing source timestamps,
  non-atomic publication, insufficient strict-loader tests, and unenforced storage.
- Primary response: all eight blocking findings were corrected without changing the approved
  scientific contract. The refreshed package verifies config/verifier/checksum/source identity
  before repository Python; locks the three Iter015 tables; independently reconstructs daily and
  depth gates; expands all figures; preserves source/normalized/excluded timestamps; uses same-
  filesystem temporary publication plus atomic promotion; broadens strict tests; and enforces 5 GiB.
- Refreshed identities: config `a894cfab...8058`, execution manifest `15b4aad3...9043`, checksum
  manifest `c0da0142...1710`; all submitted copies match canonical files.
- Package re-review: `pass` from `/root/iter002_package_review`; every prior blocker resolved,
  canonical/submitted identities match, static shell/JSON/diff checks pass, and no new blocker was
  found. The reviewer made no edits and performed no Python or scheduler action.
- Final-result review: independent read-only `pass`; all staging schemas, masks, rules, source
  identities, Iter015 products, 1,024-member depth statistics, positive-definite covariances,
  figures, and storage limits passed. The reviewer found the staged release ready for catalog-last
  publication and made no edits or scheduler changes.
- A blocking finding requires correction and passing re-review within existing authority or a stop
  for fresh authority when the correction changes the locked contract.

## Results and Closeout

- Static validation: pending.
- Preflight attempt 1: job `24794462` FAILED `2:0` after 7 s, 2 CPUs/~10 GB, batch MaxRSS
  3980K. Config, verifier, and package checksum checks passed; `cmp` then targeted nonexistent
  canonical `slurm_script` because Slurm rewrites `$0`. No repository Python ran. Logs SHA-256:
  stdout `c872da7f...a5a0`, stderr `656431cb...70b4`.
- Preflight correction: consume the one approved minimal correction by passing each literal
  submitted-script basename to the verifier. No science, source, test, resource, tolerance, or
  numerical logic changed. Refreshed config `f5db4687...39b9`, verifier `8f162c87...6c10`,
  execution manifest `06ae52f0...501d`, checksum manifest `2a09a058...33b3`.
- Correction-package review: independent read-only `pass`; the reviewer confirmed the reverse
  transform exactly reproduces prior hashes, no science/test/resource change occurred, canonical
  and submitted files match, and the recovery attempt is eligible.
- Preflight recovery: job `24794655` FAILED `1:0` after 38 s, TotalCPU 5.459 s, 2 CPUs/~10 GB,
  batch MaxRSS 461964K. All execution-identity checks and all nine strict-loader tests passed. The
  external submitted driver then raised `ModuleNotFoundError: No module named 'model_ELM'` because
  Python placed the submitted-copy directory, rather than the repository root, on `sys.path`.
  Logs: stdout SHA-256 `12bdbe66...e2b2`, stderr `89f1320b...834c`.
- Failure class: application launch-path failure; not scientific, numerical, schema/data, OOM,
  timeout, or scheduler/resource failure. The approved single preflight correction is exhausted.
- Proposed fresh recovery only: add the literal repository root to `PYTHONPATH` in all six Slurm
  scripts before Python, refresh identities/submitted copies, obtain read-only re-review, and
  authorize one same-resource preflight attempt 3. No Python code, test, science, tolerance,
  source, resource, downstream job, or publication rule would change.
- Fresh recovery authority: user response `Approved correction and you have three more total retry
  budgets for all the rest of the jobs.` The import-path correction and preflight attempt 3 are
  authorized; a shared budget of three additional retries applies across all subsequent Iter002
  jobs. The three-retry budget is unconsumed at this point.
- Import-path correction: all six Slurm scripts export the literal repository root through
  `PYTHONPATH` before Python. Refreshed config `c7a4cba4...c51c`, execution manifest
  `d50d1e77...3d94`, checksum manifest `a8c14a99...5aa8`; verifier remains
  `8f162c87...6c10`. Canonical and submitted copies match.
- Import-path correction review: independent read-only `pass`; the reviewer confirmed the single
  added `PYTHONPATH` line reverse-transforms to every previously approved Slurm hash and attempt 3
  is eligible.
- Preflight attempt 3: `24794902` COMPLETED `0:0` in 26 s; all nine strict-loader tests and
  `MCMC_ITER002_PREFLIGHT_PASS` passed.
- Source audit first attempt `24794997` FAILED `1:0` because the fail-closed coverage message did
  not expose the observed JERC values. Retry 1 `24795247` FAILED `1:0` after reporting unchanged
  source identity and observed JERC SR 18/20/22/24-hour counts 2157/2152/2144/2076 versus the
  mistaken all-2190 expectation. The diagnostic message and factual expectations were separately
  independently reviewed; the approved at-least-22-hour SR rule never changed.
- Source audit retry 2 `24795589` COMPLETED `0:0` in 16 s. It validated all locked source hashes,
  28 annual GPP rows, both 61,320-hour no-leap forcing windows, and remaining provenance limits.
- Flux preparation `24795706` COMPLETED `0:0` in 28 s. After the 720-hour history gate, ABBY/JERC
  daily counts are GPP 514/699 at 18 hours and SR 1095/2114 at 22 hours. JERC is explicitly
  fallback-only for SR error. Both flux figures and their tables passed.
- Uncertainty integration `24795812` COMPLETED `0:0` in 27 s. Full-ensemble PPE1 depth fractions,
  paired covariances, unchanged Iter015 uncertainties, CV 0.20/0.30/0.50 totals, and the third
  figure passed; staged storage is approximately 5.9 MB.
- Independent final-result review: `pass`, including independent daily/gating checks, all 19
  source identities, Iter015 manifest hashes, complete 1,024-member depth statistics, six positive-
  definite total C/N covariances, figure inspection, fixed-test exclusion, and non-overwrite state.
- Publication `24795941` FAILED `1:0` in 22 s before any publication write: decoded timestamp
  subtraction produced `timedelta64`, but the validator compared it to an integer. The independently
  reviewed correction uses `np.timedelta64(15, "m")` only.
- Publication retry `24796001` FAILED `1:0` in 21 s before any publication write: the next validator
  asserts two excluded GPP entries, while the products correctly preserve 48 hourly timestamps for
  two leap days. `release_0001`, catalog, release manifest, validation report, and temporary
  publication roots remain absent; only the empty parent directory exists.
- Retry accounting: shared later-job retry pool 3/3 consumed (two source-audit retries and one
  publication retry). All submitted jobs have terminal accounting; no active job remains.
- Current identities: config `26adade8...907c`, driver `5ee6c1de...033e`, execution manifest
  `4d98cc38...8dfe`, checksum manifest `e12917fb...3c29`, verifier `8f162c87...6c10`.
- Intermediate gate state before fresh recovery authority: `blocked_before_publication`; Gates 1--7 and pre-publication portions of
  Gates 8--9 pass, but immutable publication and published reload validation are incomplete.
- Intermediate decision: no release published; do not close Iter002 or start Iter003.
- Proposed recovery that required fresh authority: change only the GPP excluded-hour validation count
  from `2` to `48`, refresh and independently review identities, allow one same-resource publication
  retry, then run the already-approved final validation and closeout. No product, science, source,
  tolerance, or resource change is proposed.
- Fresh authority: user response `correction approved. resume now` authorized the excluded-hour
  validator correction and one same-resource publication retry. The assertion now checks 48 hourly
  timestamps, matching two complete leap days; independent correction review passed.
- Publication recovery `24797797` COMPLETED `0:0` in 27 s, 2 CPUs/~10 GB, batch MaxRSS 404808K,
  with `MCMC_ITER002_PUBLICATION_PASS`. The immutable catalog-last release was published at
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`.
- Release identities: catalog `cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8`;
  manifest `460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2`;
  validation report `19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef`.
- Final validation `24797845` COMPLETED `0:0` in 18 s, 2 CPUs/~10 GB, batch MaxRSS 258404K.
  It reloaded 18 products, validated 12,243,802 combined runtime/publication bytes, and emitted
  `MCMC_ITER002_FINAL_PASS decision=observation_release_0001_published`.
- Final independent read-only publication review: `pass`; every manifested product hash and byte
  size, exact inventory, catalog-last order, reload validation, diagnostic PNG, fixed-test
  exclusion, absence of temporary directories, storage cap, and terminal accounting passed.
- Overall gate result: all nine gates `pass`.
- Decision: `observation_release_0001_published`.

## Proposed Next-Iteration Plan (Planning Only)

Proposed Iter003 title: **Complete Four-Observable Posterior Adapter and Validation**.

- Objective: implement and validate one site-specific ABBY/JERC posterior interface that jointly
  consumes GPP, SR, TOTSOMC, and TOTSOMN from immutable observation `release_0001` and the frozen
  PPE1 coupled surrogate, without running optimization or production chains.
- Core scope: load the published release by catalog/manifest identity; align GPP and SR predictions
  to their independent published daily masks and exact observed-hour indices; apply fixed flux
  observation/surrogate scales without additional square-root reduction; apply the bivariate-log
  C/N likelihood for CV 0.20/0.30/0.50 with fixed surrogate/depth covariance and bias correction;
  combine all four likelihood contributions with the existing 18-parameter prior; expose component
  log densities and a deterministic batch API; validate scalar/batch parity, site separation,
  finite-domain rejection, covariance algebra, reproducibility, and target-free smoke performance.
- Required boundaries: PPE1 only; no PPE2 inference; no surrogate retraining or uncertainty
  recalibration; no use of the 205 fixed-test members for fitting, selection, uncertainty, or
  robustness; no observation-rule changes; no Sobol search, optimization, MCMC chains, posterior
  scientific conclusions, or modification of this release.
- Proposed gates: immutable dependency hashes; exact mask/hour-index replay; independently
  recomputed GPP/SR and joint C/N log-likelihood parity; prior-plus-likelihood decomposition;
  scalar/batch determinism; fail-closed invalid-input behavior; bounded CPU/memory smoke evidence;
  independent review and four-record closeout.
- Authority: planning only. Iter003 initialization, repository execution, scheduler work, directory
  creation, retry budget, publication, and commit require a fresh consolidated kickoff approval.

## Closeout Checklist

- [x] Final report and compact evidence complete
- [x] Registry, cumulative summary, and handoff reconciled
- [x] All jobs terminal and failures classified
- [x] Independent result review and publication validation pass
- [x] Four-record validator identity/output preserved
- [x] At most one authorized local no-push commit created
