# iter004 - Initial Candidate Search and Four-Observable MCMC Pilot

## Status

- Iteration ID: `iter004`
- Work type: `implementation | integration | candidate search | sampling pilot | numerical validation`
- Run slug: `iter004_candidate_search_mcmc_pilot`
- Status: `completed`
- Phase: `closeout`
- HPC profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Started: `2026-11-25T05:47:26-07:00`
- Closed: `2026-11-26T01:18:00-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Locked plan SHA-256: `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`
- Applicable campaign phase: prior-aware candidate search, diversified initialization, and a
  short engineering MCMC pilot using the validated complete four-observable posterior.
- Alignment: `aligned`
- Approved deviation: `none`
- Starting repository HEAD: `4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8`

## Consolidated Kickoff Package and Runtime Contract

- User direction: `MCMC Optimization — Iter004 Kickoff`, received `2026-11-25`.
- User approval: `full package approved,`, received after the complete consolidated package at
  `2026-11-25T05:47:26-07:00`.
- Goal: implement and validate one bounded, site-independent ABBY/JERC candidate-search,
  initialization, checkpoint/restart, and four-observable MCMC engineering pilot; close Iter004
  and stop without starting Iter005.
- Work units: WU1 posterior readiness; WU2 scrambled-Sobol scoring; WU3 pool/walkers; WU4
  checkpointed pilots; WU5 diagnostics, independent review, verification, and closeout.
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot`.
- Storage cap: 10 GiB. Project-path capacity was 8.1/19.5 TiB used at kickoff. Authoritative
  project-expiration confirmation is a hard pre-submission gate because the user-facing `xdisk`
  query exposes no personal allocation and the project-identity query returned `403 Forbidden`.
- Storage-expiration gate: user confirmed at `2026-11-25T15:41:37-07:00` that the project will
  remain valid for the Iter004 execution window.
- Puma: account `chopinsong`, partition `standard`, CPU-only `OLMT_puma`; one node/task and
  single-thread numerical libraries. Standard memory is derived as 5 GB/requested CPU.
- Planned jobs: WU1 2 CPU/45 min; ABBY search 4 CPU/2 h; JERC search 4 CPU/2 h; pool/walker/restart
  4 CPU/1 h; ABBY pilot 4 CPU/6 h; JERC pilot 4 CPU/6 h; diagnostics 4 CPU/2 h; final 2 CPU/30 min.
- Maximum two substantive site jobs concurrently. No scientific dependency is satisfied solely
  by Slurm exit status.
- Retry budget after fresh user-authorized reallocation: two reviewed preflight corrections/reruns,
  one fail-closed preflight numerical diagnostic, and two shared unchanged-scope
  scheduler/node/preemption/transport retries. The original one-plus-four allocation was revised
  after diagnosed preflight failures. Absolute submission ceiling: 13. No automatic application,
  numerical, scientific,
  schema, dependency, OOM, timeout, storage, or performance retry.
- Monitoring: exact job-scoped `squeue` while active and terminal `sacct` for every attempt; empty
  `squeue` is not completion.
- Cancellation: exact recorded Iter004 jobs only for duplicate submission, identity drift, wrong
  scope, leakage, output collision, published-release write risk, storage threat, or explicit user
  direction; terminal accounting remains required.
- Closeout: at most one scoped local no-push commit with expected parent
  `4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8` and proposed subject
  `Complete MCMC optimization Iter004 candidate search and pilot`. No push or merge.

## Recovery and Locked Dependencies

- Correct worktree, remote, branch, clean status, and amended-plan HEAD were verified. The
  standalone four-observable-first amendment is commit `4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8`,
  immediately after Iter003 closeout commit `b02493742806eca50361d02aa14b7b5b62ad877f`.
- Iter003 decision: `four_observable_posterior_validated`; all ten gates pass.
- All 27 recorded Iter001--003 parent jobs have terminal `sacct` accounting and no active
  `squeue` entry.
- PPE1 generator/metadata: `c3b64ebd...cf88cf2` / `80a6ed84...400e0a`; design seed `2026`.
- Coupled release manifest/catalog: `4bdc91e2...543a` / `89a636b9...285da`.
- Forcing snapshot/member split: `39b05495...187a` / `99467dea...fce`.
- Iter015 uncertainty handoff/manifest/validation: `c9282bba...436`, `293277a8...7e9`,
  `fed360f8...e2b6`.
- Observation catalog/manifest/validation: `cefc9666...6bd8`, `460c01d9...0fe2`,
  `19effdb0...8fef`.
- Iter003 posterior/reference/benchmark evidence: `cc21836e...e6ca`, `deb2a5e0...1e4`,
  `36ed26fd...45d`.
- Installed sampler: `emcee 3.1.6`, conda build `pyhd8ed1ab_1`; package metadata and exact move
  and HDF-backend implementation hashes are frozen in the execution manifest and rechecked by
  compute-node preflight.

## Prepared Execution Package

- Canonical package: `development/mcmc_optimization/slurm/iter004/`.
- Configuration SHA-256: `7c264fab14b722105ec9ecccc94d6c2ae6fc3595260652c5486bfc5ba1f407d8`.
- Execution checksum-manifest SHA-256:
  `049cbffcf97bb5a014ab77adccc23e22eee71be0dfa7796bbdb0b7355c438761`.
- Execution-manifest SHA-256:
  `576d937a237c11644491289af846671ae6f8a5846b770d1d184149f40930f16f`.
- Static checks: checksum replay, JSON parsing, shell/Slurm syntax, and `git diff --check` pass.
  Repository Python and the 27-test `unittest` inventory remain reserved for compute-node WU1.

## Frozen Scientific Configuration

- Sites: ABBY and JERC with independent targets, candidate sequences, pools, walkers, chains,
  checkpoints, seeds, and directories.
- `prior_id=ppe1`; exactly 18 physical parameters in canonical order. PPE2 scientific requests
  against the PPE1 release fail before inference.
- Full eligible no-leap window: forcing indices `[720, 61320)`.
- GPP/SR resolution: `daily/daily`; `include_cn=True`; C/N observational CV `0.30`.
- Frozen target-free three-stage PPE1 `release_0001`; `hard_zero_v1` GPP and unclipped SR.
- Fixed Iter015 development-only uncertainty, full 1,024-member PPE1 depth operator, fixed
  covariance, and fixed bias correction. The 205 protected members are not independent combined-
  operator evaluation data and are not used for fitting, selection, or surrogate uncertainty.
- Physical ranking excludes the sampling-coordinate Jacobian. Transformed-coordinate sampling
  adds the exact analytical Jacobian.
- Alternative hourly/daily combinations, flux-only comparison, and CV 0.20/0.50 remain supported
  but are not executed as scientific sensitivity campaigns.

## Numerical Failure Classification

- `outside_prior_support`: `-inf` before surrogate evaluation.
- Row-attributable `nonpositive_or_nonfinite_cn_prediction`, `nonfinite_gpp_prediction`, or
  `nonfinite_sr_prediction`: `-inf` with stable reason code.
- Exact transformation-boundary points are never clipped or perturbed; nonfinite transformed
  candidates are ineligible for pool/walker use and retain a recorded reason.
- Unexpected surrogate exceptions; unattributable batch failures; invalid covariance, source,
  context, parameter shape, or configuration; target leakage; and scheduler/process/transport/
  filesystem/backend failures fail closed.
- No broad arbitrary-exception conversion to numerical rejection is allowed. Valid batch rows
  preserve values and ordering when a recognized row-local rejection occurs.

## WU1 Readiness Gates

- Reference vector for each site: `Prior18.inverse_unit(np.full(18, 0.5))`.
- Full-window component references: ABBY prior/GPP/SR/CN
  `24.323430/-3151.364059/-4591.367822/-2.957532`; JERC
  `24.323430/-3381.363805/-19704.520779/-14.475787`.
- Identities, schemas, counts, ordering, and reason codes: exact.
- Prior, components, total, scalar/batch, and sampling equivalence: `rtol=1e-12`, `atol=1e-10`.
- Component sum: `rtol=0`, `atol=1e-10`; deterministic arrays/checksums exact.
- Mixed batch: midpoint, `frootcn=leafcn` invalid row, and a second fixed in-support vector.
- Initialization <=15 min/site; warm scalar median <=2 s; batch-16 per-candidate improves over
  scalar; batch-16/64 exact scalar equivalence; projected 1,024/2,048 search <=60/110 min per
  site; WU1 peak <=8 GiB; later projected peak <=18 GiB; projected 256-step pilot <=5.5 h/site.
- Any parity, unexpected-exception, or resource failure stops before candidate search.

## Candidate, Pool, and Walker Contract

- Scrambled Sobol seeds: ABBY `420041`, JERC `420042`; Stage 1 1,024, optional nested Stage 2
  1,024, maximum 2,048. Use the same Sobol engine prefix and `Prior18.inverse_unit` only.
- Stage 2 runs only if Stage 1 has fewer than 512 unique finite pool-eligible candidates, finite
  rate below 90%, unit-space rank below 18 or condition above 1,000, any dimension with 5th--95th
  percentile span below 0.75 or fewer than 8/10 occupied bins, or a failing provisional pool.
- Candidate records retain unit/physical coordinates, all components, total physical posterior,
  validity/reason, source and target identities, site, and index.
- Pool: exactly 256/site. Select 96 by descending physical posterior then candidate index; add 160
  by greedy maximin prior-unit distance, ties by posterior then index. Exact physical duplicates
  retain the lowest index.
- Pool gates: unique/finite/supported; rank 18; condition <=100; per-dimension range >=0.50 and
  standard deviation >=0.10; independent posterior replay at WU1 tolerances.
- Walkers: 64/site; selection seeds ABBY `430041`, JERC `430042`; PCG64 seeded permutation/ties;
  16 score-focused then 48 maximin.
- Walker gates: unique, finite, supported, independently finite posterior, finite transformed
  coordinates/Jacobian; rank 18; condition <=100; range >=0.25; standard deviation >=0.05;
  minimum pairwise unit-space distance >=0.20.
- Local L-BFGS-B refinement is disabled.

## Sampler, Restart, and Continuation Contract

- `emcee 3.1.6`; 64 walkers; transformed coordinates; 128 mandatory steps and up to 128
  conditional additional steps; checkpoints every 64.
- Move mixture: `DEMove(sigma=1e-5, gamma0=None)` weight 0.80 and
  `DESnookerMove(gammas=1.7)` weight 0.20.
- Restart-test seeds ABBY/JERC `440041`/`440042`; pilot seeds `450041`/`450042`.
- Restart fixture is 16 steps/site: uninterrupted 16 versus 8 + checkpoint + resumed 8. Require
  bitwise-identical positions, log probabilities, structured blobs, acceptance accounting,
  random-state continuation, iteration, and identity chain.
- Vectorized batch evaluation must pass exact scalar and installed-`emcee` compatibility checks;
  no silent execution-shape fallback is allowed.
- Record every proposal with step, walker, move, sampling/physical coordinates, component values
  or reason, and accepted flag. Audited wrappers must prove fixed-seed equivalence to the installed
  base moves.
- Mutable active HDF backends get immutable non-overwriting 64-step snapshots and SHA-256
  manifests. Completed markers prohibit reset, overwrite, or append. Resume requires an exact
  matching incomplete identity.
- Continue after 128 only with matching identities; no unexpected failure; finite supported
  states; at least 19 unique current states; rank 18; condition <=1e12; recognized rejection <=50%
  overall and <=90% per walker; RSS <=18 GiB; projected total <=5.5 h; projected storage <=4 GiB
  per site and <=9 GiB total; and valid checkpoint/restart/proposal accounting.
- At 256, acceptance outside `[0.05,0.80]`, more than 25% zero-move walkers, or severe nonfatal
  conditioning is a mixing limitation. Short-chain inability to establish convergence is expected.

## Immutable Gates and Decision Rule

1. Plan, repository, dependency, software, profile, and storage identity.
2. WU1 correctness and failure classification.
3. Sobol mapping, nested determinism, support, scoring, and coverage.
4. Pool/walker finiteness, uniqueness, diversity, rank, condition, and replay.
5. Physical/transformed target and Jacobian correctness.
6. Restart equivalence, checkpoint integrity, backend protection, and proposal ledger.
7. Bounded ABBY/JERC pilots and continuation compliance.
8. Complete diagnostics and explicit convergence limitations.
9. Resource, retry, storage, provenance, monitoring, and terminal accounting compliance.
10. Independent package/result review and four-record closeout.

- `mcmc_pilot_validated`: all required gates pass and both pilots complete their approved
  conditional scope without a material performance/mixing limitation.
- `mcmc_pilot_validated_with_limitations`: correctness passes but a predefined nonfatal
  continuation, performance, or mixing limitation prevents recommending production settings.
- `iter004_validation_failed`: a required numerical, scientific, identity, compatibility,
  restart, leakage, or record gate fails.
- `blocked`: unresolved authority, storage expiration, dependency, or infrastructure prevents
  legitimate completion.

## Authorized Paths and Exclusions

- Implementation: modify `model_ELM/mcmc_three_stage_posterior.py`; add
  `model_ELM/mcmc_three_stage_initialization.py`, `mcmc_three_stage_sampler.py`,
  `mcmc_three_stage_artifacts.py`, and `mcmc_three_stage_diagnostics.py`; add focused
  `tests/test_mcmc_three_stage_iter004_*.py`.
- Canonical/records: this report, `slurm/iter004/`, `summaries/iter004/`, `registry.csv`,
  `ITERATION_SUMMARY.md`, and `handoff/CURRENT.md`.
- Runtime layout: `config/`, `manifests/`, `submitted/`, `runs/`, `logs/`, `reviews/`, `results/`,
  and site-specific `candidates/`, `pool/`, `walkers/`, `restart/`, `pilot/`, `checkpoints/`, and
  `diagnostics/`.
- Tests use explicit standard-library `unittest`; the locked 27-test inventory/count is reviewed and
  enforced, with zero failures/errors and zero unexpected skips.
- No PPE2 science, upstream fitting/recalibration/rewrite, observation changes, depth replay,
  production MCMC, sensitivity campaign, nuisance parameters, multisite inference, full ELM,
  legacy removal, PPE1-loader cleanup, Iter005 initialization, push, or merge.

## Provenance and Work-Unit Ledger

| Work unit | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- |
| initialization | records and approved contract | complete | no repository Python or scheduler action |
| preparation | implementation, tests, canonical package, manifests | complete | static/read-only checks pass |
| package review | independent read-only review | complete | initial block corrected; final re-review pass |
| WU1 | compute-node readiness | complete | corrected attempt `24826328` passed strict references, batch-2/16/64 equivalence, resources, and all 27 tests |
| WU2 ABBY/JERC | candidate search | complete | both 1,024-candidate Stage 1 searches pass; Stage 2 not triggered |
| WU3 | pool, walkers, restart gate | complete | corrected job `24826962`; both 256-member pools and 64-walker sets pass, restart exact |
| WU4 ABBY/JERC | conditional 128/256-step pilots | failed at locked gate | jobs `24827188`/`24827189` stopped after 128 steps; fatal numerical rejection, no continuation |
| WU5 | diagnostics, result review, final verification | complete | jobs `24827442`/`24827522` passed; decision preserved as `iter004_validation_failed` |

## Independent Read-Only Review

- Initial package review: `block`. The read-only reviewer identified incomplete frozen
  initialization identities/ledgers, fatal continuation failures being eligible for limitation
  labeling, bypassable downstream hash/review/accounting gates, incomplete WU5 evidence, and
  insufficient regression coverage. No runtime or scheduler action had occurred.
- Consolidated preparation correction: added immutable target/source/search manifests and
  per-candidate identities; component-complete pool/walker artifacts and selection ledgers;
  fatal-versus-nonfatal continuation classification; downstream artifact/sampler hash gates;
  semantic retry/accounting and independent-result-review prerequisites; parameter traces,
  preliminary ESS where estimable, checkpoint I/O timing, component/high-score diagnostics,
  fixed C/N provenance, peak RSS and production projections; 27-test inventory; and a canonical
  four-record closeout validator.
- Package re-review: `pass` at `2026-11-25T15:40:04-07:00` against config
  `1bd229dc...3a5e`, checksum manifest `eebb36c1...b4c42`, and execution manifest
  `1cefd6f1...be5c4`. The reviewer verified all prior findings resolved, full checksum replay,
  shell/Slurm syntax, the static 27-test inventory, and closeout-accounting rejection fixtures.
- Result reviewer: pending.

## Preflight Failure and Authorized Correction

- Submission 1, WU1 job `24820985`: terminal `FAILED 1:0`, elapsed `00:00:50`, peak batch RSS
  `1271880K`, node `r4u10n2`. Package identity and checksum verification passed; 26 of 27 tests
  passed before the test runner stopped. No WU1 readiness result was written.
- Classification: authorized preflight-only test-harness defect. The synthetic `FakePosterior`
  used by the split/restart test raised when an emcee proposal mapped beyond strict physical
  bounds, while the production posterior contract returns a row-local
  `outside_prior_support/-inf` result.
- Narrow correction: change only the fake restart fixture to reproduce the production rejection
  contract. No scientific target, production implementation, resource, or scheduler setting
  changed. Corrected test SHA-256 `36c9f920...b8f`; corrected package identities are checksum
  `a9b47e88...b79a` and execution manifest `c5351a86...dcc0`.
- Retry accounting: the single preflight correction/rerun allowance will be consumed by the
  reviewed rerun; all four shared infrastructure retries remain unused.
- Independent correction review: `pass`; correction rerun submitted as job `24825410` at
  `2026-11-25T22:07:49-07:00` with `retry_class=preflight_correction`.
- Correction rerun `24825410`: terminal `FAILED 1:0`, elapsed `00:00:52`, peak batch RSS
  `1276676K`, node `r7u08n1`. All 27 tests executed; 26 passed and the split/restart test had one
  assertion failure. Chain positions, log probabilities, blobs, and acceptance accounting were
  bitwise identical; only `random_state_equal(...)` returned false.
- Root cause: application compatibility helper `random_state_equal` requires both values to be
  tuples, but installed `emcee 3.1.6` `HDFBackend.random_state` deliberately returns a list. The
  helper therefore rejects two backend-loaded states before element-wise comparison. This affects
  the production WU3 restart gate as well as its test.
- Proposed narrow correction, not yet authorized: accept list or tuple random-state sequences and
  retain exact element-wise array/scalar comparison; add a regression assertion for backend-list
  representation; refresh hashes and obtain independent review. No target, sampler mathematics,
  seed, resource, or scientific setting would change.
- Authority boundary: the sole preflight correction/rerun is exhausted. No further edit or
  submission is authorized. A clean accounting option is to reallocate one of four unused shared
  infrastructure retries to a second reviewed preflight application correction, leaving three
  shared retries and the absolute 13-submission ceiling unchanged; this requires explicit user
  approval.
- Fresh user authorization: granted at `2026-11-25T22:15:40-07:00` for the diagnosed list/tuple
  compatibility correction, independent review, and one additional WU1 rerun. One unused shared
  retry is reallocated, leaving three shared infrastructure retries; ceiling 13 is unchanged.
- Authorized correction applied: `random_state_equal` now accepts list or tuple state containers
  and preserves exact element-wise scalar/array comparison. An in-place regression assertion
  covers list/tuple equality and an unequal terminal state. Sampler SHA-256 `3b0f456e...65488`;
  test SHA-256 `98f2afd3...27e0e`; review pending.
- Truthful accounting classification: failed correction `24825410` is
  `preflight_application_compatibility`, permitted only for preflight scope and as the predecessor
  to the freshly authorized second correction. Python accounting, shell closeout, and the exact
  three-attempt regression fixture now share this token.
- Reviewer makes no edits and performs no scheduler operation.
- Independent second-correction review: `pass`; corrected package identities config
  `3d44e719...e228`, checksum `bc3eb21b...bbea2`, execution manifest `ce66a3f0...c1560`.
- Second correction rerun `24825557`: terminal `FAILED 1:0`, elapsed `00:00:52`, peak batch RSS
  `1197548K`, node `r7u17n2`. The complete 27-test inventory passed with zero skips, failures, or
  errors. The subsequent full-window ABBY WU1 evaluation failed at the locked transformed-
  coordinate scalar/batch log-posterior parity assertion. No `wu1_readiness.json` was written.
- Failure classification: `preflight_numerical_parity`. The current fail-closed driver did not
  persist the compared values, so the discrepancy magnitude and component attribution are not
  established. No candidate-search submission is permitted.
- Authority boundary: both preflight correction opportunities are consumed. The three remaining
  shared opportunities are restricted to unchanged-scope scheduler/node/preemption/transport
  failures and do not authorize numerical diagnostics, code changes, or another WU1 submission.
- Fresh diagnostic authority: granted after the clear failure report request at
  `2026-11-25T22:34:46-07:00`. One of the three remaining shared opportunities is reallocated to
  exactly one `preflight_diagnostic`, leaving two shared infrastructure retries and the absolute
  ceiling of 13 unchanged. This authority permits diagnostic instrumentation, refreshed hashes,
  independent read-only review, and one WU1 diagnostic submission only; it does not authorize a
  tolerance change, scientific/application correction, candidate search, or a further retry.
- Diagnostic reporting contract: before enforcing transformed scalar/batch parity, write a
  non-overwriting artifact for each evaluated site containing job, site, gate, source identities,
  exact scalar/batch posterior components and transformed totals, Jacobians, absolute and relative
  deltas, normalized tolerance usage, and locked tolerances. A failure also emits the artifact path
  and complete comparison payload to stderr. Terminal Slurm resource/accounting fields and log and
  artifact hashes remain mandatory.
- Diagnostic review: initial `block` identified missing exact predecessor binding, incomplete
  Jacobian deltas, and a path that could create readiness. All three were corrected. Final
  independent read-only review is `pass`: predecessor job `24825557` is exact, Jacobian evidence is
  complete, both sites are evaluated, and diagnostic-only mode returns with
  `candidate_search_authorized=false` while proving `wu1_readiness.json` remains absent.
- Diagnostic job `24825862`: terminal `COMPLETED 0:0`, elapsed `00:01:00`, batch MaxRSS
  `1122504K`, node `r7u08n1`; all 27 tests pass. The midpoint is bitwise equal in every component
  at both sites. For the second locked vector, ABBY differs only in GPP likelihood by
  `9.113814212469151e-05` (`29810.66` times its allowed component delta), propagating unchanged to
  physical and transformed totals. JERC differs in GPP by `6.058181497792248e-06` and SR by
  `3.306566213723272e-06`; partial cancellation yields total/transformed delta
  `2.751614374574274e-06` (`125.11` times the transformed-target allowance).
- Attribution: prior, C/N, and analytical Jacobian values are exact for both vectors and sites.
  The discrepancy is confined to batch-size-dependent surrogate flux arithmetic: GPP at both sites
  and SR at JERC. It is not a prior, conditional-support, C/N, coordinate-transform, or Jacobian
  error. Both site parity results are `fail`; diagnostic artifact hashes are ABBY
  `f3acafcc...4d3d5`, JERC `216b5a9b...6e2d`, combined `b41d11ed...033b1`.
- Stop boundary: `wu1_readiness.json` remains absent and candidate search remains unauthorized.
  The sole diagnostic opportunity is consumed. A numerical/application correction, tolerance
  revision, refreshed package/review, or another WU1 attempt requires fresh user authorization;
  the two remaining shared retries remain infrastructure-only.
- Conditional member-chunk direction: the user authorized `member_chunk=1` only if it were confined
  to preflight and could not affect operational performance. That condition is false: the shared
  `load_posterior(...)` constructs preflight, candidate-search, pool/replay, pilot, and diagnostics
  posteriors with the same `member_chunk=16`. No member-chunk change or rerun is therefore
  authorized by that conditional direction.
- Future-iteration guidance from the user: numerical/audit gates should distinguish benign
  floating-point reduction differences from incorrect code and consider a separately locked,
  evidence-based scalar/batch tolerance that admits expected floating-point error. Preserve strict
  source/reference, component-sum, support, identity, and deterministic replay gates. This guidance
  is prospective and does not revise Iter004's already locked tolerance without explicit current-
  iteration authorization.
- Current tolerance correction authority: explicitly granted at `2026-11-25T22:57:24-07:00`.
  Retain operational `member_chunk=16`; retain strict full-window Iter003 reference tolerance
  `rtol=1e-12`, `atol=1e-10` and component-sum `rtol=0`; introduce only a separately named
  scalar/batch-equivalence tolerance `rtol=1e-7`, `atol=1e-8`. Add non-overwriting component-level
  batch-16 and batch-64 reports before each gate. Reallocate one infrastructure opportunity to a
  third reviewed preflight correction after diagnostic job `24825862`, leaving one shared
  infrastructure retry and the 13-submission ceiling unchanged. No automatic further relaxation
  is authorized.
- Third correction review: `pass`; package identities config `7c264fab...407d8`, checksum
  `049cbffc...8761`, execution manifest `576d937a...f16f`. Corrected WU1 job `24826328` completed
  `0:0` in `00:02:25`, batch MaxRSS `1995608K`, node `r7u07n2`. All 27 tests and strict Iter003
  reference/component-sum gates pass. Sampling batch-2 and physical batch-16/64 pass; maximum
  normalized tolerance usage is `0.7736532446468659` (ABBY batch-64), below 1.
- WU1 resources pass: initialization `1.57/1.67 s`, warm scalar medians about `0.286/0.287 s`,
  batch-16 per-candidate `0.276/0.243 s`, stage-one projections `228.86/260.25 s`, maximum-search
  projections `457.72/520.50 s` for ABBY/JERC, and process peak `1.561 GiB`. Readiness SHA-256 is
  `7b9a7b07...6f3fb`. WU2 may begin under the approved two-site concurrency limit.
- WU2 jobs ABBY `24826412` and JERC `24826413` completed `0:0` in `4:07` and `6:57`, with batch
  MaxRSS `2197508K` and `2201872K`. Each generated 1,024 unique finite eligible candidates with no
  numerical rejection, full rank 18, candidate condition `1.048/1.006`, all 18 deciles occupied,
  and 5th--95th spans about 0.899. Both provisional 256-pools pass with condition `1.476/1.385`;
  Stage 2 was correctly not triggered. Throughput was `4.572/s` ABBY and `2.601/s` JERC.
- WU3 job `24826641`: terminal `FAILED 1:0`, elapsed `00:01:06`, batch MaxRSS `2008304K`, node
  `r7u12n1`. ABBY candidate identity, pool selection, support, uniqueness, unit transform, and
  geometry completed; component replay then failed first at `log_likelihood_gpp`. Candidate scores
  were generated in original Sobol-order batches of 64, while WU3 regrouped the selected score and
  diversity pool into new batches of 64. This is consistent with the diagnosed batch-composition
  floating-point behavior, but the current WU3 gate used the original strict `1e-12/1e-10`
  comparison and did not persist exact values before raising. No pool, walker, restart, or combined
  gate artifact was written; pilots remain prohibited.
- At `2026-11-25T23:34:14-07:00`, the user authorized one exact WU3 correction and three additional
  retry opportunities for following jobs. The WU3 correction extends only the already approved
  scalar/batch equivalence tolerance (`rtol=1e-7`, `atol=1e-8`) to stored candidate-score versus
  regrouped pool replay, and must publish all 256 stored/replayed component comparisons before its
  gate can fail. Strict reference, support, transform, geometry, component-sum, and exact restart
  gates remain unchanged. Accounting is locked to three preflight corrections, one preflight
  diagnostic, one exact WU3 correction with predecessor `24826641`, and three shared unchanged-scope
  later-job infrastructure retries. The absolute submission ceiling is 16; application or scientific
  corrections beyond this exact WU3 change still require fresh authority.
- Independent correction review first returned `block` because nonfinite replay values could prevent
  evidence serialization and shared retries were not restricted to later jobs. Both findings were
  corrected: nonfinite comparisons are JSON-safe with row-local rejection metadata, and shared
  retries are limited to the two pilots, diagnostics, and final verification. Re-review passed with
  config `ff852a31...b89d`, checksum `6d661f4b...80f1`, execution manifest `43f65cbc...45e`, and
  driver `387db93b...0980`. Corrected WU3 job `24826855` was submitted as sequence 9 with
  `retry_class=wu3_correction` and exact predecessor `24826641`.
- WU3 correction job `24826855` passed package identity and all 27 tests, then failed before pool
  replay at ABBY target-manifest equality. The target payload embeds the same `source_hashes` map as
  the separately checked source manifest; the reviewed accounting-only compatibility transition was
  applied only to the latter. Thus the stored nested artifact-control hash `a142fa4a...84f89` was
  compared directly with current `b984b415...d4ffa`. All scientific source hashes are unchanged;
  no pool, walker, restart, or pilot artifact was created. Controller state is `FAILED 1:0`, elapsed
  `00:00:53`, node `r4u03n1`; `sacct` reconciliation is pending because the accounting database is
  returning a transport error. Detailed evidence is `results/wu3_identity_failure_24826855.json`.
  The iteration is stopped pending fresh authority for a reviewed target-identity packaging fix and
  retry reallocation; the three later-job infrastructure retries do not authorize this application fix.
- At `2026-11-25T23:54:45-07:00`, the user authorized the exact target-identity packaging correction.
  One of the three later-job retry opportunities is reallocated to one WU3 identity correction tied
  exclusively to predecessor `24826855` and classification `wu3_target_identity_packaging`; two
  later-job infrastructure retries remain and the absolute ceiling stays 16. The correction compares
  every non-source target field exactly, requires the stored target/source source maps to be identical,
  and applies the same one-file accounting-only hash transition separately to both manifests.
- Independent re-review passed with config `414f5851...f6aee`, checksum `faca059b...cfae5`, execution
  manifest `459db406...20752`, and driver `23e322d4...e1fa6`. WU3 identity-correction job `24826962`
  was submitted as sequence 10 with exact predecessor `24826855`.
- WU3 job `24826962` completed controller state `COMPLETED 0:0` in `00:05:37`. Both sites have
  passing 256-row pool replay, full-rank pool/walker geometry, unique supported walkers, and exact
  split/restart equivalence. ABBY/JERC walker condition numbers are `2.3757/2.4348`; maximum pool
  replay normalized tolerance uses are `0.8250/0.6297`. Planned ABBY/JERC pilot jobs `24827059` and
  `24827061` were submitted as sequences 11/12 under the approved two-site concurrency limit.
- Both pilots failed before sampling: ABBY `24827059` was `FAILED 1:0` after `00:00:26` on
  `r4u06n2`; JERC `24827061` was `FAILED 1:0` after `00:00:27` on `r4u10n1`. Runtime initialization
  had precreated empty `sites/<SITE>/pilot` directories at `2026-11-25T15:42:29-07:00`, while
  `run_sampler_block(..., resume=False)` requires the directory to be absent. Each job raised
  `FileExistsError` at its first `root.mkdir`; no backend, identity, ledger, checkpoint, posterior
  evaluation, or MCMC step exists. Detailed evidence is
  `results/pilot_startup_failure_24827059_24827061.json`. This is an application compatibility
  failure, not infrastructure; downstream work is stopped pending fresh authority.

## Pilot Result, Diagnostics, and Final Decision

- The user authorized the narrow empty-directory compatibility correction and reallocated the last
  two opportunities to the site pilots. Independent review passed. Corrected jobs ABBY `24827188`
  and JERC `24827189` created identity-locked HDF backends, durable proposal ledgers, and immutable
  checkpoints at steps 64 and 128.
- Both 128-step blocks preserved 64 unique states, rank 18, and acceptable state geometry. ABBY
  condition number was `4.5990`, peak RSS `1.548 GiB`, and projected 256-step runtime `0.201 h`;
  JERC was `3.4981`, `1.562 GiB`, and `0.164 h`. Runtime, memory, storage, identity, checkpoint,
  and restart gates passed.
- The locked numerical-rejection gate failed fatally. ABBY recorded 7,079 recognized rejections in
  8,192 proposals (`0.8641357421875`) and JERC 7,350/8,192 (`0.897216796875`); both had maximum
  per-walker rejection `1.0`. Every rejected proposal was classified `outside_prior_support`; no
  unexpected surrogate, scheduler, transport, filesystem, or backend exception was hidden in the
  count. The fatal thresholds were overall `>0.50` or per-walker `>0.90`.
- Neither site continued to 256 steps. No completed-backend marker exists, no checkpoint later than
  128 exists, and no move weights, target settings, tolerances, or scientific configuration were
  tuned from the outcome. These are partial exploratory engineering pilots, not converged chains.
- Failure-compatible diagnostics job `24827442` completed `0:0` in `00:00:37`, peak batch RSS
  `1283088K`. It retained candidate, pool, walker, raw-chain, log-probability, likelihood-component,
  trace, bound-occupancy, prediction/residual, fixed C/N provenance, checkpoint, rejection, and
  performance evidence. Runtime storage was `55,704,872` bytes, far below 10 GiB.
  `convergence_claimed=false`.
- Independent result review passed. Final verification job `24827522` completed `0:0` in
  `00:00:26`, peak batch RSS `293076K`. Final validation SHA-256 is
  `c344218bd58f460f73217c0b0e75c89cf842c618dc7ac80f27710063bdf76763`.
- Decision: `iter004_validation_failed`. A fatal readiness, integrity, or numerical gate is not a
  nonfatal mixing limitation. No posterior convergence or calibrated credible interval is claimed.

## Final Accounting and Package Identities

- All 16 submissions are terminal and job-scoped `sacct` reconciled; active or unaccounted jobs:
  zero. Final accounting SHA-256 is
  `20fe9fe77f2a81f25f07e566c3c1e5f7da9d5677f195420c15f236300d6184e8`.
- Final reviewed package identities: config `050e7405...af6cf`, checksum manifest
  `bf7f2080...2b760`, execution manifest `7bb308f1...eba4`, driver `5ae814af...67a9f`.
- Retry use: three preflight corrections, one diagnostic-only preflight, one WU3 replay correction,
  one WU3 identity correction, and two site-specific pilot startup corrections. Shared unchanged-
  scope infrastructure retries used: zero. The absolute 16-submission ceiling was reached exactly.
- Repository closeout is authorized as one local no-push commit with expected parent
  `4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8`, subject
  `Complete MCMC optimization Iter004 candidate search and pilot`, and validator
  `validate_closeout_iter004.sh`. No push, merge, or Iter005 initialization is authorized.

## Deferred Technical Debt

- Missing `pytest` remains unresolved in locked `OLMT_puma`; Iter004 uses explicit `unittest`
  coverage.
- Removal of `load_ppe1_coupled_release()` remains deferred until separately authorized full MCMC
  pipeline cleanup.

## Explicit Stop Conditions

Stop on storage-expiration uncertainty before submission; identity drift; target leakage; an
unauthorized path need; application/data/schema/scientific/numerical failure; unapproved resource
change; exhausted retry/submission limit; storage threat; immutable-gate failure; unaccounted job
state; or closeout validation failure. Otherwise continue through terminal accounting, independent
review, four-record validation, and the authorized no-push closeout commit. Do not begin Iter005.

## Proposed Next-Iteration Plan (Planning Only)

- Title: **Sampler Geometry Audit and Corrected Four-Observable Pilot Planning**.
- First determine why valid, diverse transformed-coordinate walkers generated 86--90% physical
  out-of-support proposals. Audit proposal-level transformed-to-physical mapping, conditional C:N
  support, overflow/boundary behavior, ensemble scale, and `DEMove`/`DESnookerMove` geometry using
  immutable Iter004 ledgers. Distinguish an implementation/transform defect from an expected but
  unsuitable move-scale interaction before proposing any correction.
- Predeclare a bounded audit, exact acceptance criteria, fresh package review, and new runtime/retry
  contract. Only after an independently validated correction should a fresh short pilot be proposed;
  chain length must not be increased merely to overcome the fatal rejection rate.
- Historical `development/spinup_forcing_coupling` context used 64 walkers with 500-step early
  pilots, 4,000-step follow-up, commonly 8,000-step diagnostics, and 32,000-step production chains.
  Those lengths are context only: Iter004's fatal 128-step geometry result must be resolved before
  any longer MCMC proposal. Iter005 remains uninitialized and requires fresh consolidated approval.

## Closeout Checklist

- [x] Final report and compact evidence complete
- [x] Registry, cumulative summary, and handoff reconciled
- [x] All jobs terminal and every failure/rejection classified
- [x] Independent package and result reviews pass
- [x] Four-record validator identity/output preserved
- [x] Deferred `pytest` and PPE1-loader debt carried forward
- [x] One authorized local no-push closeout commit created after final validation
