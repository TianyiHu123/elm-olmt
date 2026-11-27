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
- Current phase: `iter005 closeout complete; iter006 planning only`.
- Last completed iteration: `iter005`.
- Active iteration: none. Iter005 report `development/mcmc_optimization/iterations/iter005.md`.
- Active jobs: none. All five Iter005 and all 16 Iter004 submissions are terminal and reconciled.
- Last updated: `2026-11-27T01:41:00-07:00`.
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting
  `development/hpc/puma.md`.
- Last decision: `iter005_validation_failed`.
- Authority: user approved the complete Iter005 kickoff package and separately conditionally authorized
  a diagnosed too-strict floating-point tolerance correction after correct-implementation evidence.
  Exact scope, tests, resources, ten-submission ceiling, retries, cancellation, and closeout are in
  `iterations/iter005.md`. No push, merge, or Iter006 initialization is authorized.

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

## Historical Planning-Only Iter005 Proposal

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
- This was the closed Iter004 planning proposal. The later user direction approved direct prior-unit/logit
  reconstruction with bounded diagnostics, recorded in the active Iter005 report. Iter004 remains immutable.

## Iter005 Closeout

- Status `completed`; closed `2026-11-27T01:41:00-07:00`; acceptance `fail`;
  decision `iter005_validation_failed`. Report: `development/mcmc_optimization/iterations/iter005.md`;
  compact summary: `development/mcmc_optimization/summaries/iter005/summary.md`.
- Frozen PPE1 18-parameter four-observable target, ABBY/JERC independent, daily GPP/SR,
  include-C/N CV 0.30, window `[720,61320)`, coupled surrogate and observation `release_0001`,
  and Iter015 uncertainty remained unchanged. Development-only prior/surrogate bounds and
  conditional C:N checks passed; no elementwise operational bounds check was added.
- Preflight passed 41/41 tests after one reviewed test-fixture correction. ABBY's 64 reused
  physical walkers passed source, support, physical-target and strict prior/Jacobian density
  checks. The cross-vector validation tolerance was corrected once under the user's conditional
  authority and independent re-review. Same-vector prior/Jacobian cancellation peaked at
  `5.68e-14`; normalized density at `1.82e-12`; archived/reconstructed difference at `1.20e-5`
  for walker 63, inside the predeclared parity criterion.
- The ABBY 16-step restart fixture failed at step 2 when a proposed prior-unit/logit coordinate
  mapped outside a PPE1 marginal bound and raised an uncaught `RuntimeError`. The partial ledger
  has 128 proposals, 28 numerical saturations and 41 accepted moves. This is a fatal mapping and
  exact-restart gate. JERC validation and both 128-step pilots were not run; no movement or
  convergence result exists. The partial backend/ledger must not be resumed as a validated chain.
- All five actual Slurm submissions are terminal; active or unaccounted jobs: zero. The approved
  one preflight correction and one conditional tolerance correction were used, with zero
  infrastructure retries. The diagnostics job `24838734` completed `0:0` and recorded
  `iter005_validation_failed`, missing pilot reports, and no convergence claim.
- External evidence root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot`.
  Final config SHA-256 `4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021`;
  checksum manifest `2b414218813fbdbc93957f321222e3b144058595ca226a61dc40f5dd386abddc`;
  execution manifest `7507fa14751efac64389655be9aea14c1cc8b4f218fea5ce2d8cfa0b2d5ea0e9`.
  Diagnostics SHA-256 `d1d1ec631f4d4620f4345e30ac0515010c5f2f7e40f71541211f4cec68e0479e`;
  final accounting `80cb77f33c54106521278b851c620ea34c8ab837763fd403fb3da1062762b891`;
  independent result review `06009889d7667c19f606bb34eb7877df86ed6fcf4275f1a1953c5a4f1fe0fcd6`;
  four-record validation `ITER005_FOUR_RECORD_VALIDATE_PASS` artifact
  `8412993640011ecbab5f0990a271eddc56856c44bd0e09606c08b21b5666f9c6`.
  Diagnostics counted 1,857,767 file bytes; later accounting `du -sb` counted 1,908,394 bytes
  including directory metadata. Both are under the 2 GiB cap.
- Historical failures, retries, logs, source copies, numerical residuals, partial backend and
  ledger, and terminal accounting remain in the external root. No push or merge occurred.

## Planning-Only Iter006 Proposal

**Boundary-Safe Prior-Unit Mapping and Restart Feasibility.** Reproduce the failed
extreme-coordinate proposal on a compute node and measure its physical-bound ULP distance.
Distinguish roundoff saturation from a larger prior mapping defect; preserve the physical
prior and avoid clipping, reflection or hidden resampling. Independently review a targeted
geometry correction, then validate strict mapping, Jacobian, density, release identity,
source hashes, and exact ABBY/JERC 16 versus 8+8 restart using fresh backends. Measure
move-specific saturation before deciding whether a later 128-step pilot is scientifically
feasible. A provisional three-job 2-CPU, 10-GB, 1-hour each plan needs a separately reviewed
kickoff package and explicit approval. Do not initialize, execute, retry, push or merge Iter006.

## Resume Point

Iter005 is closed with `iter005_validation_failed`. Review the fatal mapping evidence and
planning-only Iter006 proposal before seeking a fresh complete kickoff approval. Do not
resume the Iter005 partial backend or submit either withheld pilot under this closed contract.
