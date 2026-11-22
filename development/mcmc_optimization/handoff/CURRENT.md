# MCMC Optimization Development - Current Handoff

## Campaign Plan

- Campaign: `MCMC Optimization Development`
- Plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Current plan SHA-256: `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`
- Active iteration locked plan SHA-256: `none`
- Applicable campaign phase: pre-Iter001 campaign initialization; progression items 2--3 are the
  planning direction, not initialized work
- Alignment: `aligned`; approved deviation: `none`; amendment recommendation: `none`

## Live State

- Current status: `not_initialized`
- Current phase: `pre_kickoff`
- Active iteration: `none`
- Active jobs: `none`
- Active monitoring: `none`
- Runtime authority: `not approved`
- Selected/proposed HPC profile: `development/hpc/puma.md` (`proposed`; the active HPC session is
  not confirmed by this handoff)
- Last updated: `2026-11-22T02:52:51-07:00`

## Scientific State

- Parameter contract: exactly 18 physical parameters.
- Active scientific baseline: `prior_id=ppe1` using the original PPE1 design and compatible PPE1
  coupled surrogate.
- Optional prior support: `prior_id=ppe2` is an implementation/testing objective only; PPE2
  scientific inference is inactive until compatible PPE2 surrogate, uncertainty, and depth
  products exist.
- Target variables: GPP, SR, TOTSOMC, and TOTSOMN with site-specific inference configurations.
- Iter001 has not started. No MCMC implementation, candidate search, chain, benchmark, experiment,
  output, or iteration artifact exists.

## Upstream Dependencies (Existing, Not Produced Here)

- Coupled surrogate: published PPE1 ABBY/JERC `three_stage_abby_jerc/release_0001` under
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc`;
  validated 26-payload manifest SHA-256
  `4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a`; catalog SHA-256
  `89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da`.
- Coupled release contract: ABBY/JERC, canonical 18-parameter PPE1 schema, frozen 25/43/44 feature
  schemas, no-leap time, 720-hour history, target-free sequential inference, and `hard_zero_v1`.
- Uncertainty handoff: existing Iter015 development-only full-chain uncertainty under
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/handoff`;
  handoff SHA-256 `c9282bbad9abc2d6519329018ca9be026171f071e6e689a44fb2af102784f436`,
  products-manifest SHA-256 `293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9`,
  validation SHA-256 `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
- Provenance records: `development/three_stage_surrogate/handoff/CURRENT.md`,
  `development/three_stage_surrogate/iterations/iter015.md`, and
  `development/three_stage_surrogate/iterations/iter016.md`.
- Dependency status: read-only upstream products; no published surrogate code, release, catalog,
  manifest, uncertainty product, or historical record may be modified by this campaign.
- Storage risk: these upstream `/xdisk` products are temporary and unbacked; identities and
  availability must be revalidated in the Iter001 kickoff package and preflight.

## Active Kickoff Package and Runtime Authority

- Package state: `not approved`
- Kickoff goal and stop boundary: `none approved`
- User response and approval timestamp: `none`
- Confirmed HPC system/profile: `not confirmed`; Puma is proposed
- Approved output root/layout/creation authority/retention policy: `none`
- Locked inputs, scope, exclusions, gates, and decision rule: `none`
- Lifecycle, outside-sandbox, retry, and cancellation authority: `none`
- Closeout branch: `none`

## Iter001 Direction (Planning Only)

1. Dual-prior contract and numerical tests for PPE1 and optional PPE2, including conditional
   support, normalization, inverse maps, and coordinate Jacobians.
2. PPE1 coupled-surrogate interface validation against the published ABBY/JERC `release_0001`,
   including schema/provenance compatibility and target-free sequential inference.
3. Reproducible coupled-inference throughput and peak-memory benchmarking sufficient to project
   candidate-search and MCMC resources.

This direction is not a finalized iteration plan or runtime contract. It authorizes no report,
directory, code change, repository Python, benchmark, experiment, scheduler action, retry,
cancellation, or commit.

## Current Risks or Blockers

- The Iter001 finite work units, numerical and interface gates, benchmark matrix, exact resources,
  output root, retention limits, review plan, retry/cancellation bounds, and closeout branch remain
  to be proposed and approved.
- The selected HPC host and current availability/identity of temporary upstream products require
  live confirmation before runtime approval.
- The proposed Puma profile fixes the execution checkout at
  `/xdisk/chopinsong/tianyihu/elm-olmt`, while this branch is currently inspected at
  `/xdisk/chopinsong/tianyihu/elm-olmt-mcmc`; the consolidated Iter001 package must resolve the
  execution checkout and source identity without editing the shared profile ad hoc.

## Next Action

1. Prepare and present one consolidated Iter001 kickoff package for user approval, following
   `development/mcmc_optimization/WORKFLOW.md`. Do not create
   `development/mcmc_optimization/iterations/iter001.md` before that approval.

## Next Session Start Protocol

1. Read `MCMC_OPTIMIZATION_PLAN.md`, verify its SHA-256, then read this handoff and `WORKFLOW.md`.
2. Confirm the Git branch/worktree and review the header-only registry and cumulative summary.
3. Read `development/hpc/puma.md` and revalidate the upstream release and uncertainty identities.
4. Finalize missing Iter001 decisions and seek approval of one complete kickoff package.
5. Do not infer runtime, scheduler, directory, retry, cancellation, plan-edit, or commit authority
   from the planning direction or this handoff.

## Artifact References

- Current/latest MCMC iteration report: `none`
- Registry: `development/mcmc_optimization/registry.csv` (header only)
- Cumulative summary: `development/mcmc_optimization/ITERATION_SUMMARY.md`
- MCMC summaries, canonical scripts, submitted configs, checkpoints, chains, and scratch output:
  `none`
