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

## iter005 - Prior-Aware Bounded Sampler Reconstruction and Corrected Four-Observable Pilot

- Closed `2026-11-27T01:41:00-07:00`; `completed`; implementation, integration, numerical
  validation, and planned bounded sampling pilot. Plan SHA-256
  `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`; aligned.
- Added focused PPE1 prior-unit/logit coordinates and full Jacobian to the existing three-stage
  posterior and `emcee` sampler. Elementwise prior/surrogate bounds and conditional C:N metadata
  were compared only in development preflight; ordinary prior, release, schema, support and
  provenance checks remain. The frozen four-observable scientific target and older closed
  iterations were not changed.
- The corrected compute-node preflight passed 41/41 explicit tests with zero skips. The first
  preflight's two new test-fixture errors were preserved and fixed under the one approved narrow
  correction opportunity. The first density job exposed an overly strict cross-vector absolute
  comparison; the user's conditional authorization was used once to apply the already locked
  scalar/batch tolerance while retaining strict same-vector density and Jacobian checks.
- ABBY's 64 reused physical walkers passed identity, support, physical target and corrected
  density checks: maximum prior/Jacobian cancellation `5.68e-14`, normalized same-vector residual
  `1.82e-12`, and archived/reconstructed difference `1.20e-5` within its separate tolerance.
  The subsequent 16-step restart failed at step 2 when a proposal's prior inverse produced a
  physical value outside a marginal bound and raised an uncaught mapping error. The partial
  128-row ledger has 28 saturation rejections and 41 accepted moves; it is not a validated chain.
- This fatal mapping/restart gate blocked JERC validation and both 128-step pilots. The planned
  diagnostics job recorded `iter005_validation_failed`, missing pilot reports, and no convergence
  claim. Decision: `iter005_validation_failed`, not a mixing limitation. Movement and calibrated
  parameter estimates were not assessed.
- Five actual Slurm submissions are terminal and accounted; active/unaccounted jobs zero.
  Diagnostics SHA-256 `d1d1ec631f4d4620f4345e30ac0515010c5f2f7e40f71541211f4cec68e0479e`,
  final accounting `80cb77f33c54106521278b851c620ea34c8ab837763fd403fb3da1062762b891`,
  independent result review `06009889d7667c19f606bb34eb7877df86ed6fcf4275f1a1953c5a4f1fe0fcd6`.
  Four-record validation `ITER005_FOUR_RECORD_VALIDATE_PASS` artifact SHA-256
  `8412993640011ecbab5f0990a271eddc56856c44bd0e09606c08b21b5666f9c6`.
  Final config/checksum/execution manifest hashes are
  `4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021` /
  `2b414218813fbdbc93957f321222e3b144058595ca226a61dc40f5dd386abddc` /
  `7507fa14751efac64389655be9aea14c1cc8b4f218fea5ce2d8cfa0b2d5ea0e9`.
  Evidence root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot`.
  Diagnostics measured 1,857,767 file bytes and final accounting measured 1,908,394 bytes
  including directory metadata, both below 2 GiB.
- Missing `pytest` and PPE1-specific-loader cleanup remain deferred. Planning-only Iter006
  proposal: **Boundary-Safe Prior-Unit Mapping and Restart Feasibility**. Diagnose the
  extreme-coordinate marginal escape and move-specific saturation, make only an evidence-backed
  boundary classification correction, and revalidate ABBY/JERC exact restart with fresh backends
  before seeking a separately approved pilot. No Iter006 initialization, execution, push or merge.

## iter006 - Sampler Correction and Boundary-Event Diagnostics

- Closed `2026-11-27T05:17:54-07:00`; status `completed`; acceptance `fail`;
  decision `iter006_validation_failed`. User kickoff revised the historical Iter005
  planning-only proposal. Plan SHA-256
  `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`;
  frozen PPE1 four-observable science and release identities were preserved.
- Exact old-source/state replay recovered the Iter005 ABBY fatal event at step 3,
  uncorrected snooker split 0, walker 40: `k_s2` was two directional ULPs below
  its `0.003` lower bound, while independent higher precision is inside support.
  Bounded corrected move/map numerical fixtures passed with frozen policy SHA-256
  `931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e`.
- Stage B's mandatory test gate failed with two errors among 50 tests: an existing
  fixture compatibility regression and a wrong test working directory. Exhausted
  correction authority barred Stage C and both pilots. Stage F's own evidence
  driver failed on truthiness of empty glob iterators; no F result JSON was produced.
  Both are explicit hard-gate failures, not infrastructure retries. Five Slurm
  jobs `24840516`, `24840555`, `24840587`, `24840823`, `24840903` are terminal
  and accounted; no active job. C/D/E unsubmitted. Final accounting SHA-256
  `1863332a2246a9d7db29ad032d2966310804ee70c38e6d285b9bd5d88445c7b9`.
  Static four-record reconciliation passed for the failed closeout, SHA-256
  `c53d74570bce3d588e4939941d7aa44c95d23917ce1872736dad94643427321f`;
  Stage F in-job validation itself did not pass.
- No corrected chain, step-zero/per-step/block/cumulative boundary time history,
  retained endpoint occupancy, movement result, or convergence assessment exists;
  convergence is unassessed. Runtime evidence root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics`;
  compact summary `development/mcmc_optimization/summaries/iter006/summary.md`.
  Planning-only next proposal: fix legacy test dispatch, test cwd and F empty-glob
  check; seek a fresh bounded kickoff for B/C before any pilot.
