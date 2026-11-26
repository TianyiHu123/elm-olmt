# MCMC Optimization Iteration Summary

## iter001 - Dual-Prior Contract and Coupled Inference Preflight

- Closed `2026-11-23T00:56:47-07:00`; `completed`; implementation, validation, and benchmark.
- Implemented an exact 18-parameter PPE1/PPE2 prior interface and validated support, physical
  density, conditional normalization, inverse maps, sampling coordinates, and Jacobians. PPE2
  remains incompatible with PPE1 surrogate science.
- Validated target-free ABBY/JERC sequential inference against published PPE1 coupled
  `release_0001` manifest `4bdc91e2...543a`, including exact hard-zero GPP, unclipped SR,
  deterministic replay, schema/units, and fail-closed incompatibility handling.
- Completed all 18 bounded throughput cells and repeats. Process peak was 329336 KiB; linear
  surrogate-only projections were 232.509 s for 1,024 and 22,705.939 s for 100,000 two-site full
  evaluations. These are not approved production budgets.
- Acceptance: all seven gates `pass`; independent review `pass`; recommendation `A`; decision
  `continue_existing_inference_path`.
- Jobs: `24759169` failed harness, `24759238` completed recovery, `24773888` failed strict
  serialized comparison, `24773997` completed approved tolerance recovery, and `24773889`,
  `24774027`, `24774088` completed. No job remains active or unaccounted.
- Plan SHA-256 `46775c71...afc6`; aligned; no amendment. No protected fixed-test use and no change
  to published artifacts, history, or plan.
- Evidence: `development/mcmc_optimization/summaries/iter001/`; output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight`.
- Limitation and terminal direction: no likelihood/posterior was evaluated; rebenchmark complete
  posterior-call throughput after a likelihood adapter exists. No next iteration is proposed or
  authorized.

## iter002 - NEON Observation Preparation and Fixed-Uncertainty Release

- Closed `2026-11-24T04:26:44-07:00`; `completed`; audit, implementation, integration, validation,
  and release.
- Published immutable ABBY/JERC GPP, SR, TOTSOMC, and TOTSOMN observation `release_0001` with
  catalog `cefc9666...6bd8`, manifest `460c01d9...0fe2`, and validation report
  `19effdb0...8fef`; decision `observation_release_0001_published`.
- After the 720-hour history gate, daily coverage is ABBY/JERC GPP 514/699 days at at least 18
  paired hours and SR 1,095/2,114 days at at least 22 valid hours. Exact masks, timestamps, and
  source-hour indices are published independently for GPP and SR.
- The hourly post-average GPP zero gate changed 4,043 ABBY and 5,223 JERC hours while retaining raw
  negatives and signed DT/NT half-differences. Daily gating comparisons and coverage sensitivities
  are preserved in tables and figures.
- Integrated established 2.0-m soil C/N stocks, complete 1,024-member PPE1 depth fractions and
  covariance, unchanged Iter015 development-only flux/CN surrogate uncertainty, fixed bias
  correction, and positive-definite total C/N covariance for CV 0.20, 0.30, and 0.50. Protected
  fixed-test members were not used to estimate surrogate uncertainty.
- All nine gates pass; independent pre-publication and post-publication reviews pass; final reload
  validated 18 products and 12,243,802 combined bytes. Three diagnostic figures and their source
  tables are published.
- Jobs: preflight `24794462`/`24794655` failed and `24794902` passed; source audit
  `24794997`/`24795247` failed and `24795589` passed; `24795706` flux and `24795812` uncertainty
  passed; publication `24795941`/`24796001` failed pre-write and `24797797` passed after explicit
  correction authority; final validation `24797845` passed. No job remains active or unaccounted.
- Plan SHA-256 `b302ee65...75ab`; aligned. Iter001 retains its historical plan identity. Existing
  upstream releases and historical records were not rewritten.
- Evidence: `development/mcmc_optimization/summaries/iter002/`; release root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`.
- Limitations: original Perlmutter processing logs are unavailable on Puma; Iter015 daily flux
  surrogate errors use full 24-hour model days while observations may use 18--23 hours; fixed-test
  members are not independent evaluation data for the combined surrogate-plus-depth operator.
- Next direction is planning-only Iter003, **Complete Four-Observable Posterior Adapter and
  Validation**. No Iter003 initialization, execution, optimization, or MCMC chain is authorized.

## iter003 - Complete Four-Observable Posterior Adapter and Validation

- Closed `2026-11-25T03:24:53-07:00`; `completed`; implementation, integration, numerical
  validation, and bounded benchmark.
- Implemented a strict general three-stage release interface, immutable observation contexts, pure
  Gaussian/joint-CN kernels, and reusable physical/sampling-coordinate scalar/batch posterior APIs.
  The validated PPE1 loader remains as a temporary compatibility layer; PPE2 science fails closed.
- Both ABBY and JERC pass daily/daily, hourly/hourly, daily/hourly, and hourly/daily evaluation
  with exact variable-specific alignment, component isolation, target-free replay, and complete
  provenance. Full counts are ABBY GPP 15,437/514 and SR 26,264/1,095 hourly/daily; JERC GPP
  19,844/699 and SR 51,162/2,114.
- Eight independent flux references and six joint-C/N references across CV 0.20/0.30/0.50 pass;
  posterior component-sum error is zero. Prior/support/Jacobian, scalar/batch ordering,
  determinism, failure handling, PPE2 rejection, and legacy compatibility pass.
- The benchmark completed 72 warm cells, 24 cold measurements, and five repeats/cell. Annual
  scalar medians span 0.0711--0.2950 s; batch-16 improves all annual configurations; peak is
  504888 KiB. No material performance blocker applies and projections are not execution budgets.
- All ten gates pass; independent package and result reviews pass after preserved corrections;
  decision `four_observable_posterior_validated`.
- Jobs: preflight `24811598` failed identity transcription and `24811617` passed; component
  `24811658` failed missing pytest and authorized `24811705` passed; integrated `24811719` exposed
  incomplete Gate 5 reference evidence and authorized `24812674` passed; benchmark `24811738` and
  final `24812698` passed. All attempts are terminal; no shared scheduler retry was consumed.
- Plan SHA-256 `b302ee65...75ab`; aligned; no amendment. Evidence is under
  `development/mcmc_optimization/summaries/iter003/` and runtime root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior`.
- Unresolved: `pytest` is absent from locked `OLMT_puma`; later work must install/lock it or use a
  supported alternative. Deferred: retain the PPE1-specific loader until full-pipeline cleanup is
  separately authorized.
- Next direction is planning-only **Initial Candidate Search and MCMC Pilot Planning**, using the
  validated daily/daily, include-C/N, CV 0.30 baseline. No Iter004 work is authorized.

## iter004 - Initial Candidate Search and Four-Observable MCMC Pilot

- Closed `2026-11-26T01:18:00-07:00`; `completed`; implementation, integration, candidate search,
  sampling pilot, and numerical validation. Amended plan SHA-256 `5ee74c52...60c0`.
- WU1 passed full-window four-observable references and resources. Both scrambled-Sobol searches
  retained 1,024/1,024 unique finite candidates without Stage 2. Deterministic 256-member pools and
  64-walker sets pass support, diversity, rank 18, replay, and exact split/restart continuation.
- Corrected pilots ran exactly 128 steps. ABBY numerical rejection was 7,079/8,192
  (`0.8641357421875`); JERC was 7,350/8,192 (`0.897216796875`); both had a worst-walker rate of
  1.0. All were classified `outside_prior_support`. The locked fatal limits were 0.50 overall and
  0.90 per walker, so neither site continued to 256.
- State geometry, identity, checkpoints, memory, runtime, and storage remained valid: 64 unique
  states, rank 18, condition 4.599/3.498, peak RSS about 1.55/1.56 GiB, and exact step-64/128
  snapshots. The result is not a convergence claim.
- Failure-compatible diagnostics and independent result review pass. Final verification evidence
  SHA-256 is `c344218b...6763`; runtime evidence is about 55.7 MB against 10 GiB.
- All 16 submissions are terminal and reconciled; no job is active or unaccounted. Decision:
  `iter004_validation_failed`. This fatal numerical gate is not a nonfatal mixing limitation.
- Missing `pytest` and PPE1-specific-loader cleanup remain deferred. Iter005 is planning-only:
  audit proposal geometry and transformed-to-physical support before any corrected pilot or longer
  chain. No Iter005 initialization, execution, push, or merge is authorized.
