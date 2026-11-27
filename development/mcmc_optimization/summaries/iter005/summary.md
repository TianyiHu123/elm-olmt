# iter005 compact closeout summary

- Closed: `2026-11-27T01:41:00-07:00`; status `completed`; acceptance `fail`;
  decision `iter005_validation_failed`.
- Work type: `implementation | integration | numerical validation | sampling pilot`.
- Objective: reconstruct PPE1 prior-unit/logit sampler coordinates and validate the unchanged
  ABBY/JERC daily-GPP, daily-SR, include-C/N CV 0.30 four-observable posterior before a bounded
  128-step pilot. Plan SHA-256 `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`;
  aligned, with no approved deviation.
- Frozen dependencies: PPE1 prior, coupled surrogate `release_0001`, immutable observation
  `release_0001`, Iter015 uncertainty, full PPE1 depth operator, full `[720,61320)` window.
  Protected fixed-test restrictions and PPE2 release rejection remain in force.
- Reusable geometry maps `z -> sigmoid(z) -> Prior18.inverse_unit(u)` with full Jacobian, strict
  prior support, distinct finite-coordinate saturation, and no clipping or reflection. Operational
  prior/release/schema checks remain. The elementwise prior/snapshot bounds and conditional C:N
  equivalence check was recorded only as development validation.
- Compute-node preflight passed 41/41 tests with zero skips after one reviewed test-fixture
  correction. The original failed attempt and its source package were preserved. No prior,
  likelihood, release, or legacy SR-only geometry mathematics changed.
- The initial density job's `1e-9` absolute check compared likelihoods evaluated at archived and
  round-tripped physical vectors. A user-authorized, independently reviewed tolerance correction
  applied the predeclared `rtol=1e-7`, `atol=1e-8` only to this cross-vector comparison; strict
  same-vector reference and Jacobian checks remained.
- ABBY's 64 physical initial walkers passed source identity, support, physical-target replay and
  strict density checks. Maximum prior/Jacobian cancellation residual was `5.68e-14`; same-vector
  normalized-density residual was `1.82e-12`; archived/reconstructed total difference peaked at
  `1.20e-5` for walker 63 and passed its predeclared parity criterion.
- The 16-step ABBY restart fixture failed at step 2: a sampler proposal raised an uncaught
  `RuntimeError` because the `Prior18.inverse_unit` result was outside a PPE1 marginal bound.
  The partial ledger contains 128 proposals, 28 numerical saturation rejections, and 41 accepted
  moves. This is a fatal mapping/restart gate; the partial backend is not a validated chain.
  JERC validation and both site pilots were not run. Movement and convergence were not assessed.
- Diagnostics job `24838734` completed `0:0` and recorded missing pilot reports, storage
  `1,857,767` file bytes, no convergence claim, and decision
  `iter005_validation_failed`. Diagnostics SHA-256
  `d1d1ec631f4d4620f4345e30ac0515010c5f2f7e40f71541211f4cec68e0479e`.
- Independent read-only package and result reviews pass for faithful failure closeout. Final
  result review SHA-256 `06009889d7667c19f606bb34eb7877df86ed6fcf4275f1a1953c5a4f1fe0fcd6`.
  Four-record validation `ITER005_FOUR_RECORD_VALIDATE_PASS` artifact SHA-256
  `8412993640011ecbab5f0990a271eddc56856c44bd0e09606c08b21b5666f9c6`.
- All five actual Slurm submissions are terminal; scoped `squeue` is empty. One preflight
  correction and one user-authorized tolerance correction were used; no site pilots or shared
  infrastructure retries were submitted. Final accounting SHA-256
  `80cb77f33c54106521278b851c620ea34c8ab837763fd403fb3da1062762b891`.
  Final-accounting `du -sb` was 1,908,394 bytes including directory metadata, measured later
  than the diagnostics file-only tally. Both are below 2 GiB.
- Runtime evidence root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot`.
  Final package config SHA-256 `4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021`,
  checksum manifest `2b414218813fbdbc93957f321222e3b144058595ca226a61dc40f5dd386abddc`,
  execution manifest `7507fa14751efac64389655be9aea14c1cc8b4f218fea5ce2d8cfa0b2d5ea0e9`.
- Missing `pytest` and the PPE1-specific loader cleanup remain deferred. No posterior
  convergence or calibrated parameter estimate is claimed.
- Planning-only Iter006 direction: **Boundary-Safe Prior-Unit Mapping and Restart Feasibility**.
  Reproduce the extreme-coordinate escape and measure ULP distance to bounds; distinguish
  numerical saturation from a larger mapping defect without clipping or prior changes. Then
  test any justified geometry fix, revalidate ABBY/JERC exact restart with fresh backends, and
  measure move-specific saturation. A new bounded pilot would require a separate decision and
  approval. Provisional three 2-CPU, 10-GB, 1-hour jobs need their own reviewed package and
  explicit authority. No Iter006 initialization, execution, push, or merge is authorized.
