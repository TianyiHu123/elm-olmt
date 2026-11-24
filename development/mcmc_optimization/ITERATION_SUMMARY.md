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
