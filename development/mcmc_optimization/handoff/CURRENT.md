# MCMC Optimization Development - Current Handoff

## Campaign Plan

- Campaign: `MCMC Optimization Development`.
- Plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`.
- Current plan SHA-256: `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`.
- Historical locked plan identities remain: Iter001
  `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`; Iter002--003
  `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`.
- Alignment: `aligned`; approved deviation `none`. The independent four-observable-first amendment
  remains authoritative and does not rewrite completed iteration identities.

## Live State

- Current status: `closed`.
- Current phase: `closed`.
- Last completed iteration: `iter004`.
- Active iteration: none.
- Active jobs: none; all 16 Iter004 submissions are terminal and job-scoped `sacct` reconciled.
- Last updated: `2026-11-26T01:18:00-07:00`.
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting
  `development/hpc/puma.md`.
- Decision: `iter004_validation_failed`.
- Authority: Iter004 is closed by the authorized local no-push closeout commit. No additional commit,
  Iter005 initialization, runtime directory, repository Python, scheduler action, retry, push, or
  merge is authorized without a fresh consolidated package and approval.

## Iter004 Closeout

- Report: `development/mcmc_optimization/iterations/iter004.md`.
- Compact summary: `development/mcmc_optimization/summaries/iter004/summary.md`.
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot`.
- Starting HEAD: `4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8`.
- Scientific baseline: PPE1, 18 parameters, ABBY/JERC independent, daily GPP, daily SR, C/N included,
  CV 0.30, full eligible 2018--2024 no-leap window, frozen releases and uncertainty.
- WU1 passed full-window Iter003 references, failure classification, deterministic replay, exact
  physical/sampling target separation, and resources. The separately locked scalar/batch tolerance
  was `rtol=1e-7`, `atol=1e-8`; strict scientific-reference and component-sum gates remained.
- Candidate search generated 1,024/1,024 unique finite eligible Stage-1 candidates per site; Stage 2
  was not triggered. Both 256-member pools and 64-walker sets pass support, uniqueness, rank 18,
  spread, condition, replay, target identity, and exact split/restart validation.
- Corrected pilots ABBY `24827188` and JERC `24827189` ran exactly 128 steps and stopped at the
  immutable fatal gate. Overall recognized out-of-support rejection was 7,079/8,192
  (`0.8641357421875`) ABBY and 7,350/8,192 (`0.897216796875`) JERC; worst-walker rate was 1.0 at
  both sites. Fatal limits were 0.50 overall and 0.90 per walker.
- No 256-step continuation occurred. No completed-backend marker or checkpoint after step 128
  exists. No scientific settings or move weights were tuned from the result. These are exploratory
  engineering pilots; no posterior convergence or calibrated credible interval is claimed.
- Diagnostics job `24827442` and final verification `24827522` completed `0:0`. Independent package
  and result reviews pass. Final validation SHA-256 is
  `c344218bd58f460f73217c0b0e75c89cf842c618dc7ac80f27710063bdf76763`.
- Final accounting SHA-256 is
  `20fe9fe77f2a81f25f07e566c3c1e5f7da9d5677f195420c15f236300d6184e8`;
  active or unaccounted jobs: zero. The absolute 16-submission ceiling was reached exactly.
- Final package identities: config `050e7405...af6cf`, checksum manifest `bf7f2080...2b760`,
  execution manifest `7bb308f1...eba4`, driver `5ae814af...67a9f`.

## Deferred Items

- Missing `pytest` in `OLMT_puma` remains unresolved. Iter004 used the proven explicit 27-test
  `unittest` inventory with zero unexpected skips.
- Removal of `load_ppe1_coupled_release()` remains deferred until separately authorized full MCMC
  pipeline finalization and general-loader equivalence validation.
- User guidance for future numerical/audit gates: predeclare evidence-based tolerances that admit
  expected floating-point reduction differences while retaining strict scientific-reference,
  component-sum, support, identity, and deterministic replay checks.

## Planning-Only Iter005 Proposal

- Proposed title: **Sampler Geometry Audit and Corrected Four-Observable Pilot Planning**.
- Use immutable Iter004 proposal ledgers to determine why valid transformed walkers generated
  86--90% physical out-of-support proposals. Audit coordinate mapping, conditional C:N support,
  boundary/overflow behavior, ensemble scale, and `DEMove`/`DESnookerMove` geometry before choosing
  whether code, transformation, initialization, or move configuration needs correction.
- Require a new bounded contract, exact acceptance thresholds, independent package review, and fresh
  approval before any execution. Do not increase chain length to mask the fatal rejection behavior.
- Historical coupling MCMC used 64 walkers with 500-step early pilots, 4,000-step follow-up,
  frequently 8,000-step diagnostics, and 32,000-step production chains. This is context, not current
  authority; Iter004's fatal 128-step result must be resolved first.
- Iter005 is not initialized and must not start automatically.

## Resume Point

1. Verify branch, HEAD, clean/expected status, current plan hash, Iter004 closeout commit, and this
   handoff.
2. Read the full workflow, amended plan, Iter004 report/summary, final validation, final accounting,
   and both proposal ledgers.
3. Prepare one consolidated planning package for the geometry audit and corrected pilot. Stop for
   fresh user approval before creating Iter005 records, executing repository Python, creating runtime
   directories, changing scheduler state, or committing.
