# MCMC Optimization Development - Current Handoff

## Campaign Plan

- Campaign: `MCMC Optimization Development`
- Plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Current plan SHA-256: `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`
- Historical Iter001 locked plan SHA-256: `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`
- Alignment: `aligned`; approved deviation `none`.
- Workflow clarification: surrogate training/tuning/uncertainty remain development-only; the final
  PPE1 depth observation operator, residual mean, and covariance use the complete 1,024-member
  preprocessing ensemble. The 205 fixed-test members are not independent evaluation data for the
  combined surrogate-plus-depth operator.

## Live State

- Current status: `closed`
- Current phase: `closed`
- Last completed iteration: `iter002`
- Active iteration: none
- Active jobs: none; every submitted Iter002 attempt has terminal `sacct` accounting
- Last updated: `2026-11-24T04:26:44-07:00`
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Closeout authority: user-approved one local no-push commit; no push, merge, or Iter003 authority

## Iter002 Decision and Release

- Objective completed: immutable ABBY/JERC GPP, SR, TOTSOMC, and TOTSOMN observation and fixed-
  uncertainty release.
- Decision: `observation_release_0001_published`; all nine acceptance gates pass.
- Release root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`.
- Catalog SHA-256: `cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8`.
- Release-manifest SHA-256:
  `460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2`.
- Validation-report SHA-256:
  `19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef`.
- Final package config SHA-256:
  `44b7950cd8fab968ed0b03b18eca7c3cd99db30ac139ca14295027cf3876cbc3`.
- Final validation reloaded 18 products; combined runtime/publication storage is 12,243,802 bytes.
- Independent pre-publication and post-publication reviews: `pass`.

## Scientific Contract Preserved

- GPP daily rule: at least 18 paired hours; gate `max(0,(GPP_DT+GPP_NT)/2)` hourly before daily
  averaging; retain raw values, signed half-difference, gate-after-daily comparison, and exact masks.
- SR daily rule: at least 22 valid hours with an independent mask/window. ABBY uses valid measured
  `SR_err`; JERC uses the documented 10% relative plus 0.05 `gC/m^2/day` floor fallback.
- Daily observation sigma is RMS over retained hourly sigmas, never divided by `sqrt(n)` or
  `sqrt(24)`. The GPP absolute floor is also 0.05 `gC/m^2/day`.
- Coverage after history: ABBY/JERC GPP 514/699 days; SR 1,095/2,114 days.
- Soil observations retain established processed 2.0-m stocks. Full 1,024-member PPE1 depth
  fractions/covariance and unchanged Iter015 development-only surrogate uncertainty are published.
- Fixed-test access for surrogate uncertainty is false. PPE2 inference, posterior implementation,
  optimization, MCMC chains, surrogate changes, and upstream release rewrites were excluded.

## Job and Failure Accounting

- Preflight: `24794462` FAILED `2:0`; `24794655` FAILED `1:0`; `24794902` COMPLETED `0:0`.
- Source audit: `24794997` FAILED `1:0`; `24795247` FAILED `1:0`; `24795589` COMPLETED `0:0`.
- Flux preparation: `24795706` COMPLETED `0:0`.
- Uncertainty integration: `24795812` COMPLETED `0:0`.
- Publication: `24795941` FAILED `1:0`; `24796001` FAILED `1:0`; after explicit correction
  authority, `24797797` COMPLETED `0:0`.
- Final validation: `24797845` COMPLETED `0:0`.
- Every failure is classified in `iterations/iter002.md`; failed publication attempts stopped before
  any publication write. No scheduler job remains active or unaccounted.

## Limitations

- Original Perlmutter processing logs are unavailable on Puma; transferred products and scripts are
  hash-locked.
- Iter015 daily GPP/SR surrogate errors use complete 24-hour model days, whereas published
  observation daily means may use 18--23 available hours. Iter002 did not recompute uncertainty.
- The 205 fixed-test members are not independent evaluation data for the combined surrogate-plus-
  depth operator.

## Proposed Iter003 - Planning Only

Proposed title: **Complete Four-Observable Posterior Adapter and Validation**.

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

## Next Session Start Protocol

1. Verify the current campaign-plan hash and read this handoff, workflow, Iter002 report, registry,
   cumulative summary, and compact closeout evidence.
2. Confirm the Iter002 closeout commit identity and immutable release catalog/manifest identities.
3. Do not initialize Iter003 until one complete consolidated kickoff package receives explicit user
   approval.

## Artifact References

- Final report: `development/mcmc_optimization/iterations/iter002.md`
- Compact evidence: `development/mcmc_optimization/summaries/iter002/summary.md`
- Registry: `development/mcmc_optimization/registry.csv`
- Cumulative summary: `development/mcmc_optimization/ITERATION_SUMMARY.md`
- Canonical package: `development/mcmc_optimization/slurm/iter002/`
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation`
- Release root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`
- Existing untracked `mcmc_depth_operator_full_ppe1_amendment.patch` remains user material and is
  untouched and excluded from Iter002.
