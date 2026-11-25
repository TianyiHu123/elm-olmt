# MCMC Optimization Development - Current Handoff

## Campaign Plan

- Campaign: `MCMC Optimization Development`.
- Plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`.
- Current plan SHA-256: `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`.
- Historical Iter001 locked plan SHA-256:
  `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`.
- Alignment: `aligned`; approved deviation `none`; no amendment recommended.

## Live State

- Current status: `closed`.
- Current phase: `closed`.
- Last completed iteration: `iter003`.
- Active iteration: none.
- Active jobs: none; all eight Iter003 attempts have terminal `sacct` accounting.
- Last updated: `2026-11-25T03:24:53-07:00`.
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting
  `development/hpc/puma.md`.
- Decision: `four_observable_posterior_validated`; all ten gates `pass`.
- Authority: Iter003 closeout only. No Iter004 initialization/execution, candidate search,
  optimization, MCMC, push, or merge is authorized.

## Iter003 Decision and Implementation

- Objective completed: reusable ABBY/JERC PPE1 posterior combining the exact 18-D physical prior,
  frozen target-free three-stage surrogate, immutable Iter002 observations, fixed uncertainty,
  independent GPP/SR resolution operators, and fixed joint C/N likelihood.
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior`.
- General `load_three_stage_release()` validates explicit versioned configuration and currently
  delegates to the preserved PPE1-specific loader. Observation contexts are immutable and preserve
  exact hourly/daily forcing mappings. Pure likelihood kernels are separate from orchestration.
- Scalar and ordered batch physical-space APIs return prior, GPP, SR, C/N, total, counts, and
  provenance. The sampling-coordinate wrapper adds its Jacobian separately. `include_cn=False`
  returns C/N component `0.0`; PPE2 requests fail before surrogate inference.
- Final identities: config `0038e424d5c65f8a6ddcec78a79af2c164fa63e0776d44a7ff8badc6e5c68bcc`;
  checksum manifest `492ad4fb4380e8c3d85b23073be574b2c5b23a232c7a49bfcc271851fb46032d`;
  execution manifest `0b5f651336e30098a2b1c58d60e1d617f38ddfc2efa587d12bc7c68ba3882ba4`.

## Numerical and Performance Evidence

- Counts: ABBY GPP 15,437 hourly/514 daily, SR 26,264/1,095; JERC GPP 19,844/699,
  SR 51,162/2,114.
- Both sites pass `daily/daily`, `hourly/hourly`, `daily/hourly`, and `hourly/daily`, with exact
  resolution-component isolation and one full-window surrogate call per site reused across
  operators.
- Eight independent Gaussian and six independent joint-C/N references (both sites × CV
  0.20/0.30/0.50) pass `rtol=1e-12`, `atol=1e-10`; maximum normalized tolerance usage is
  0.000194. Posterior component-sum maximum absolute error is zero.
- Prior/support/Jacobian, exact bounded replay, scalar/batch parity and ordering, invalid-input
  handling, nonpositive C/N rejection, target-free inference, PPE2 rejection, and legacy
  compatibility pass. No protected fixed-test member was used for surrogate uncertainty or
  validation.
- Benchmark: 72 warm cells, 24 cold measurements, five repeats/cell. Annual scalar medians span
  0.0711--0.2950 seconds; annual daily/daily is 0.0785 seconds ABBY and 0.0711 seconds JERC.
  Batch-16 improves all annual configurations; projected maximum for 1,024 evaluations is
  302.06 seconds; benchmark peak RSS is 504888 KiB. No performance blocker applies. Projections
  are estimates, not approved budgets.
- Final validation job `24812698` passed; posterior evidence SHA-256 `cc21836e...e6ca`, likelihood
  references `deb2a5e0...1e4`, benchmark `36ed26fd...45d`.

## Job and Failure Accounting

- Preflight: `24811598` FAILED `1:0` on a submitted verifier-hash transcription;
  reviewed correction `24811617` COMPLETED `0:0`.
- Component: `24811658` FAILED `1:0` because locked `OLMT_puma` lacks `pytest`; after fresh user
  authority and explicit `unittest` legacy coverage, `24811705` COMPLETED `0:0`.
- Integrated: `24811719` COMPLETED `0:0` but independent review found incomplete Gate 5 C/N
  reference coverage; after fresh authority, corrected `24812674` COMPLETED `0:0`.
- Benchmark `24811738` and final `24812698` COMPLETED `0:0`.
- All failures/corrections are preserved in `iterations/iter003.md`. No job is active or
  unaccounted. Shared unchanged-scope scheduler retries consumed: zero of four.

## Limitations and Scientific Assumptions

- Iter015 daily surrogate errors were estimated for complete model days, while some observed daily
  means contain only 18--23 valid hours. Iter003 did not recalibrate uncertainty.
- The complete 1,024-member PPE1 population defines the frozen depth operator; the 205 fixed-test
  members are not independent validation data for the combined surrogate-plus-depth operator.
- Posterior values are adapter/validation evidence, not calibrated scientific inference. No
  candidate search, optimization, walker initialization, or chain was run.

## Unresolved Issues

- **Missing `pytest` in `OLMT_puma`: unresolved.** Historical
  `tests/test_mcmc_iter009_geometry.py` cannot import in the locked environment. Iter003 provides
  equivalent explicit standard-library `unittest` regression coverage. A later authorized
  environment-maintenance or campaign iteration must either install and lock compatible `pytest`
  or use another supported test package/framework and migrate the affected tests. Keep this
  reminder until resolved.

## Deferred Technical Debt

- **Remove PPE-Specific Three-Stage Surrogate Loader After Full MCMC Pipeline Finalization** —
  `Deferred`.
- Preserve `load_ppe1_coupled_release()` and historical artifacts. Remove it only after a
  separately authorized cleanup makes all release/prior/schema/snapshot/uncertainty identities
  explicit, migrates every MCMC consumer, and proves PPE1 numerical equivalence.

## Proposed Next-Iteration Plan (Planning Only)

**Title:** Initial Candidate Search and MCMC Pilot Planning.

- Objective: design, but do not yet execute, a bounded PPE1 ABBY/JERC candidate-search and initial
  MCMC pilot using site-independent contexts and the validated `daily/daily`, `include_cn=True`,
  CV 0.30 baseline, while retaining alternative resolution and flux-only comparison interfaces.
- Locked dependencies: Iter003 decision `four_observable_posterior_validated`; final config
  `0038e424...8bcc`; PPE1 prior; coupled release; forcing snapshot; Iter002 observation release;
  fixed uncertainty; hard-zero GPP, unclipped SR, target-free, fixed-test, and provenance contracts.
- Proposed work units: choose deterministic candidate generation/ranking; define bounded local
  refinement and diversified walker initialization without changing the posterior; derive
  compute/storage from measured Iter003 performance; specify checkpoint/restart/convergence,
  independent review, failure, and scientific non-interpretation gates; present one consolidated
  kickoff package.
- Required planning decisions: candidate count/seed/batch size, site separation, walkers and
  geometry, pilot length/checkpoints/moves, acceptance/ESS/autocorrelation evidence, exact
  resources/submissions/storage, retry budgets, and stop rule.
- Exclusions until fresh approval: no candidate generation, optimization, walker initialization,
  `emcee`, chain, interpretation, PPE2 science, uncertainty changes, artifact rewrites, loader
  cleanup, or Iter004 scaffold. Resolve or explicitly route around missing `pytest` in the package.
- Approval boundary: recover this closed state under Workflow Section 4A and obtain fresh
  consolidated approval before any Iter004 record, repository Python, runtime directory, job, or
  commit. This proposal grants no authority.

## Artifact References

- Final report: `development/mcmc_optimization/iterations/iter003.md`.
- Compact evidence: `development/mcmc_optimization/summaries/iter003/summary.md`.
- Registry: `development/mcmc_optimization/registry.csv`.
- Cumulative summary: `development/mcmc_optimization/ITERATION_SUMMARY.md`.
- Canonical package: `development/mcmc_optimization/slurm/iter003/`.
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior`.
- Final accounting: runtime `manifests/final_job_accounting.json`.
- Existing unrelated user material remains untouched and excluded.
