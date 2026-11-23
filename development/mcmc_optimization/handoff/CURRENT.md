# MCMC Optimization Development - Current Handoff

## Campaign Plan

- Campaign: `MCMC Optimization Development`
- Plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Current and Iter001 locked SHA-256: `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`
- Applicable phase: Iter001 progression items 2--3 completed
- Alignment: `aligned`; approved deviation `none`; amendment recommendation `none`

## Live State

- Current status: `completed`
- Current phase: `closed`
- Active iteration: none; latest closed iteration is `iter001`
- Active jobs: none; all seven submitted job IDs have terminal accounting
- Active monitoring: none
- Runtime authority: `closed`; no unused Iter001 execution, retry, cancellation, or commit authority
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Last updated: `2026-11-23T00:56:47-07:00`

## Current Objective and Evidence

- Objective and scope: completed the reusable 18-parameter PPE1/PPE2 prior contract, PPE1
  ABBY/JERC coupled-interface validation, and an 18-cell bounded throughput benchmark. No
  likelihood, MCMC chain, training, optimization, or PPE2 scientific inference occurred.
- Prior result: PPE1/PPE2 support, normalized densities, inverse maps, transformations, and
  Jacobians pass; serialization-aware inverse-map tolerance is `rtol=1e-10`, `atol=1e-12`.
- Interface result: published PPE1 `release_0001` manifest `4bdc91e2...543a`; target-free
  sequential ABBY/JERC inference, exact hard-zero, finite unclipped SR, deterministic replay,
  schema/unit identity, and incompatibility rejection pass.
- Benchmark result: 18/18 cells and five repeats; process peak 329336 KiB. Linear surrogate-only
  projections are 232.509 s for 1,024 and 22,705.939 s for 100,000 two-site full evaluations.
- Gate result and decision: all seven gates `pass`; independent review `pass`; recommendation `A`;
  decision `continue_existing_inference_path`.
- Report hashes: prior `29bd1e2f...5c3b`; interface `7fc10ed5...e253`; benchmark
  `f7f15068...2176`; reviewed decision `705fe383...53fe`; final `4526f8b5...4e93`.

## Dependencies and Boundaries

- Authoritative PPE1/PPE2 sources remain read-only and hash-locked in the Iter001 report and
  execution manifest.
- Coupled surrogate: PPE1 ABBY/JERC `three_stage_abby_jerc/release_0001`; manifest
  `4bdc91e2...543a`; catalog `89a636b9...85da`.
- Iter015 uncertainty handoff/products/validation: `c9282bba...436`, `293277a8...7e9`,
  `fed360f8...e2b6`; read-only and used only for compatibility/provenance validation.
- No protected fixed-test input was used for fitting, tuning, priors, uncertainty, or validation.
  Published artifacts, historical records, and the campaign plan remain unchanged.
- PPE2 scientific inference remains prohibited until compatible PPE2 surrogate and uncertainty
  products exist. Full posterior-call throughput must be rebenchmarked after a likelihood adapter
  exists; the Iter001 projections are not production budgets.

## Job and Failure Accounting

- Preflight `24759169` FAILED `1:0` because `pytest` was unavailable; approved unittest recovery
  `24759238` COMPLETED `0:0`.
- Prior `24773888` FAILED `1:0` at the original serialized inverse-map tolerance; user-authorized,
  independently reviewed tolerance recovery `24773997` COMPLETED `0:0`.
- Interface `24773889`, benchmark `24774027`, and final validation `24774088` COMPLETED `0:0`.
- No job is active or unaccounted; neither failure was retried without fresh authority.

## Closeout and Next Action

- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight`; retained, 464 KiB at closeout; no deletion.
- Closeout: one scoped local no-push commit, expected parent
  `547cc22b170b3262e8ead20e948372e9d59fbc98`, subject
  `Complete MCMC optimization Iter001 preflight`; no push or merge.
- Next action: none. Iter001 is terminal.

## Next Iteration Plan (Terminal Declaration)

No next iteration is proposed or authorized. Any Iter002, likelihood construction, candidate
screening, posterior sampling, performance optimization, or PPE2 scientific inference requires
fresh user direction and a complete consolidated kickoff package.

## Next Session Start Protocol

1. Read and verify `MCMC_OPTIMIZATION_PLAN.md`, then read this handoff and `WORKFLOW.md`.
2. Read `iterations/iter001.md`, its registry row, cumulative summary, and compact evidence.
3. Confirm no active scheduler work and inspect Git identity before considering new planning.
4. Do not initialize Iter002 or execute work without a fresh consolidated kickoff approval.

## Artifact References

- Report: `development/mcmc_optimization/iterations/iter001.md`
- Registry: `development/mcmc_optimization/registry.csv`
- Cumulative summary: `development/mcmc_optimization/ITERATION_SUMMARY.md`
- Compact evidence: `development/mcmc_optimization/summaries/iter001/`
- Canonical execution package: `development/mcmc_optimization/slurm/iter001/`
- External results: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight`
