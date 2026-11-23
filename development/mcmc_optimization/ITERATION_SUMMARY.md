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
