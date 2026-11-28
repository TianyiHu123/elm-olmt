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
- Current phase: `iter006 reopened closeout completed; compute, independent reviews and static four-record reconciliation passed; one scoped local append commit selected`.
- Last completed iteration: `iter006`; the prior Iter006 failed closeout in commit `9f81aa9d2065339c59d86f5933231b89b7b9df2a` is historical and superseded by this continuation.
- Active iteration: none; report `development/mcmc_optimization/iterations/iter006.md`.
- Active Iter006 job: none. F `24848482` completed `0:0` for job/batch/extern;
  its evidence-only output is `diagnostics/attempt_002` and both independent
  result reviews passed.
  ABBY D `24847977` and JERC E `24847981`
  are terminal `COMPLETED 0:0`, each with 64 walkers x 128 steps, separate
  fresh backends and independently reviewed reports `pass`. C3
  `24847731` passed both-site scientific/parity/restart gates and is terminal
  `COMPLETED 0:0`; C1 `24841160` and C2 `24847546` failed and remain preserved.
  All 12 Iter006 jobs are terminal and accounted. Total submissions 12;
  additional correction retry budgets used 2/10. F source and submitted
  package hashes were independently reviewed; static four-record reconciliation
  passed with preserved output SHA-256 `e696e6a7e0d8878b9b0b1d4266b0f5e3c2d9e2d823e4ae742ec3ed4ac0a22137`.
- Last updated: `2026-11-27T20:28:52-07:00`.
  All five Iter005 and all 16 Iter004 submissions remain terminal and reconciled.
- Selected profile: `development/hpc/puma_mcmc_worktree.md`, inheriting
  `development/hpc/puma.md`.
- Last closed decision: `bounded_sampler_pilot_validated`. Current final decision: `bounded_sampler_pilot_validated`.
- Authority: the user's `ITER006 KICKOFF — SAMPLER CORRECTION AND BOUNDARY-EVENT DIAGNOSTICS`
  approves the bounded Iter006 implementation, six planned jobs, specified retries, monitoring,
  closeout and at most one local commit. Exact contract is recorded in `iterations/iter006.md`.
  No push, merge, plan amendment or Iter007 initialization is authorized.
  The user's later reopening direction grants fresh authority for focused B/F application
  corrections and completion of original C/D/E work. The user then approved
  ten additional correction retries for failed jobs, with a new approval
  request required if all ten are consumed. Original science, numerical policy,
  resources, gates, seeds and output cap remain fixed. See report reopening addendum.

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

## Historical Premature Iter006 Closeout

- User-approved kickoff revised the historical planning-only Iter006 proposal. Frozen science
  and plan SHA-256 `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`
  were preserved. Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics`.
- Stage A exact old-source/state ABBY replay identified the original fatal proposal:
  step 3, uncorrected snooker split 0, walker 40, `k_s2` two directional ULPs below its
  `0.003` lower bound. Higher precision places the original stored-unit mapping inside
  support. Stage B's bounded independent numerical report passed under policy SHA-256
  `931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e`.
- Stage B job `24840823` failed its mandatory test gate: 50 tests ran, two errors,
  including a modified-posterior legacy fixture regression and test working-directory
  error. The approved correction budget was exhausted. Stage C and both pilots were
  withheld. Stage F `24840903` also failed on its own truthy empty-glob check, falsely
  reporting an absent pilot backend; no F result JSON exists. Neither failure is an
  infrastructure interruption. Independent read-only result reviews agree.
- Final accounting `accounting/final_iter006_jobs.psv` SHA-256
  `1863332a2246a9d7db29ad032d2966310804ee70c38e6d285b9bd5d88445c7b9`;
  five terminal submissions and no active jobs. Runtime size 3,638,392 bytes under 2 GiB.
  Static four-record reconciliation passed (`ITER006_FOUR_RECORD_VALIDATE_PASS`, SHA-256
  `c53d74570bce3d588e4939941d7aa44c95d23917ce1872736dad94643427321f`) and records this failed decision separately from the failed
  Stage F in-job evidence validation. No corrected site boundary histories or movement
  assessment exist. The legacy replay does not establish convergence; convergence is unassessed.
- Planning-only next proposal: repair the legacy fixture dispatch, test launch cwd and F
  empty-glob check, then seek a new bounded kickoff for numerical, both-site restart and
  pilot gates in that order. Do not resume old backends, extend chains, tune moves, push,
  merge or initialize Iter007 under this handoff.

## Active Iter006 Reopening Resume Point

- User reopening direction at `2026-11-27T05:31:25-07:00` supersedes the historical
  premature closeout for the live iteration. `WORKFLOW.md` section 4.E requires fresh
  approval for application/code corrections; this user direction supplies it for the
  focused B and F fixes and completion of originally planned C, D and E work units.
- Preserve all five terminal jobs `24840516`, `24840555`, `24840587`, `24840823`,
  `24840903`, failed packages, accounting and old validator. Parent commit for an
  append closeout is `9f81aa9d2065339c59d86f5933231b89b7b9df2a`.
- Remaining planned submissions: B attempt 002, C attempt 001, ABBY D attempt 001,
  JERC E attempt 001, F attempt 002, in that gate order; maximum ten total jobs.
  No additional retry is reserved. Run repository Python only in reviewed Slurm jobs;
  preserve unchanged frozen science and numerical policy. Reconcile current package,
  site/account availability and independent reviews before submission. Stop for fresh
  user approval if a further application failure makes the five-job continuation
  impossible. The existing registry/cumulative closeout remains historical pending
  final four-record reconciliation.
- B attempt 002 package `submitted/b/attempt_002` is frozen with driver
  `2cd3d44a842972d1e603dd99f1be5b9656872f8be992aa608bb1cba7f6c82893`,
  script `963a1a6066cd4cec8abf5d26e108bc6a1ccc7b024f590565e2c05e77ee9523d7`,
  source manifest `2be3004ad18a5f9c7d87b8b14230d9e125d56fb03203a2c305bc62c53377fb5c`,
  package manifest `6ea85ec10ffb8312b24c5f3187e1822fe7b970f5246b21355142c65abee87c7f`.
  Two independent read-only B2 package reviews passed. B2 job `24841071`
  completed with 52/52 unit tests and bounded numerical validation pass;
  accounting `40d2945422532a7d78e65ffb3b860722f4a83fc717ca0601ccffdc77e308f68a`.
  Prepare and independently review C before submission. D/E/F remain gated.
- C attempt 001 package is frozen under `submitted/c/attempt_001`: driver
  `602b7ee8e75e7ff695901bdf4c9f47a4c402d3f9b5d5f5bf654c320142122567`,
  script `7b333bc391e603ff2ce5f806b95df47e9e63205655d85c5a8f401f5725541ace`,
  source manifest `39f8665228826eb9b501f337e66fe458a883be4959214b1cc4b745e44e35af97`,
  package manifest `cdf3c70333e384bf11d8acc5c572b8f277288b1eacc8f8ba73769b2ae5f94058`.
  Both independent frozen-package reviews passed. C job `24841160` is terminal
  `FAILED 1:0` after 12m11s, with batch failed and extern completed; saved
  accounting is `accounting/c_attempt_001_24841160.psv`. ABBY full and split
  restart output was generated, but the job stopped at JERC archived versus
  reconstructed `log_likelihood_sr` parity, walker 30. The combined assertion
  did not state which subcomparison failed or its magnitude. This is an
  application validation failure requiring diagnosis; no pilots are authorized
  to proceed. Seven submissions have been used. At least four more submissions
  (corrected C, D, E, F) are needed, exceeding the ten-job ceiling. Keep Iter006
  open, preserve C attempt 001, and seek a specific ceiling/correction approval
  before any further submission. Stage F source remains under static review.
- C attempt 002 is frozen at `submitted/c/attempt_002`, driver SHA-256
  `3f15beed3e900d6bd698146d0cddb9481d82f4ed103cb13fdc5c260d28770450`,
  script `245a6a53f11d815802d3d87a4fc4d307e62cf4c1c3a3661f006e760fb124f7a2`,
  source manifest `d51b92162a58eb568938b3fb7f2eb7849fb847337c94793901d1454c3dadefd4`,
  package manifest `d736b22b1cd610072095027de1ef22123fd3287518c59bdfecfa8c32a867b606`.
  It preserves C1 and writes separate same-vector/cross-vector JERC parity evidence
  before assertion. Both independent frozen-package reviews pass; the requested
  ceiling extension was subsequently approved as ten additional correction
  retry budgets; stop and ask again if all ten are consumed. C2 is the first
  correction retry. Original D/E/F gates, science, resources, review and
  accounting obligations remain. Live `standard` partition and
  `chopinsong/standard` association were reconfirmed; no duplicate queued job.
- C2 job `24847546` is terminal `FAILED 1:0` after 12m51s (batch failed,
  extern completed). Accounting `accounting/c_attempt_002_24847546.psv`
  SHA-256 `01ab4e7304179e27f3db35069ce788312369040bd013796bfd945d8d00a4be30`.
  JERC walker 30's archived and current SR log likelihood agree exactly at
  the archived physical vector (`-3157.038457662321`), but the z-reconstructed
  vector gives `-3157.039540711637`, a `0.001083049316` cross-vector difference
  above the locked tolerance. C2's separate diagnostics are preserved; no
  tolerance or science setting changed. Correction retry 1/10 is consumed;
  nine remain. Independently review the result and prepare a deterministic,
  physical-only initial-z refinement with fresh identities before any C3 job.
  D/E/F remain gated; do not create an approved C pointer yet.
- C3 canonical source is in static review. It uses a uniform physical-only
  bounded search for initial z from archived theta, records each refinement,
  then reruns unchanged support, scientific parity, endpoint and restart gates
  in fresh attempt-003 outputs. The locked map, K, tolerances, science and
  seeds remain fixed. Both independent C3 frozen-package reviews passed.
  Job `24847731` was submitted as ninth total job and correction retry 2/10;
  eight correction budgets remain. It is terminal `COMPLETED 0:0` for job/batch/
  extern after 23m10s; accounting SHA-256
  `ce049f1d76a45fab88a7da73ba39b3bfd7d1c04d0a9e47dcbc632845aa10203c`.
  C3 report SHA-256 `8eb51642d0c94bc9baff11a416be3980205e5998b35b1625eb491e2c9127b044`
  reports both-site strict scientific parity, exact 16-vs-8+8 backend/logical
  restart, zero failed/unexamined proposals, and synthetic accepted endpoint.
  Both independent C3 result reviews pass, including all 320/site component
  rows, effective-map bit equality, exact backend/logical restart and full
  generated proposal accounting. One JERC unit saturation in the restart
  fixture was explicitly recorded and rejected. The C scientific gate is open;
  create and independently review the immutable approved-C pointer, then
  freeze/review D/E packages before pilot submission.
- The exclusive approved-C pointer `validation/approved_c_gate.json` now exists,
  SHA-256 `b991f8ce81903270a5dadf7b987e982e3886f316facd8eadecbf8d776514f7ee`.
  It selects C3 and preserves C1/C2 failed provenance. Both independent
  pointer reviews pass against live bytes and terminal Slurm steps. D/E remain
  unsubmitted. Separate D/E attempt-001 packages are now frozen, shared driver
  SHA-256 `72a4568a76b6855c530bc4388d34a33689abd8694befe81cb98b42e2a297fa4d`,
  package manifests D `84cee2e6b3f9b59c80beba46efc6efaa4751169686e81f776401b1d5116c2b27`
  and E `c14f065097c5020751eb93b9f2002b87d2116a7f6e901c5965d5e8d5226e7cb1`.
  Both independent frozen-package reviews passed. ABBY D job `24847977` is
  submitted as the tenth total job (planned pilot, no correction retry). JERC
  E remains to be submitted from its separate reviewed package; at most two
  site pilots may run concurrently. Monitor both exact jobs to terminal.
- JERC E job `24847981` is also submitted, eleventh total submission and the
  second planned pilot. D `24847977` and E `24847981` have separate output
  roots; neither uses a correction retry. Monitor both through job/batch/extern
  terminal `sacct` and preserve complete pilot reports before F preparation.
  Correction retries used remain 2/10.
- Both D `24847977` and E `24847981` transitioned from scheduler priority
  queue to `RUNNING` with separate 4-CPU/20G allocations. Monitor to terminal
  job/batch/extern accounting; queue departure alone is not completion. Keep
  F and closeout gated on both complete 128-step results.

## Iter006 Reopened Final Closeout

- The user's reopening direction superseded the premature failed closeout in
  parent commit `9f81aa9d2065339c59d86f5933231b89b7b9df2a` and authorized
  ten additional focused correction retries; 2/10 were used. Historical
  failures and packages remain preserved. The current report, registry,
  cumulative summary and compact summary record the corrected final decision.
- Exact old-source replay identified the Iter005 ABBY snooker step-3/split-0/
  walker-40 `k_s2` escape by two directional ULPs below `0.003`. Corrected
  snooker and physical mapping policy SHA-256
  `931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e`
  passed bounded numerical references. B2 52 tests and C3 both-site strict
  target, exact restart and synthetic accepted-endpoint/original-z tests passed.
- Fresh ABBY/JERC 64-walker, 128-step pilots both passed with checkpoints at
  64/128 and 8192 generated/examined/completed proposals each. Acceptance was
  `0.10888671875`/`0.083251953125`; no declared movement check failed.
  Pilot physical repairs, accepted physical endpoints, retained exact
  endpoints and corrected-run material mapping failures were zero. Natural
  endpoint/unit saturation proposal vectors were ABBY 22/48 and JERC 26/125.
  Descriptive original-z near-boundary occupancy rose 34/64 to 64/64 ABBY
  and 31/64 to 62/64 JERC. Late-block acceptance declined to 50/1024 and
  18/1024. These short-run findings warrant later sensitivity review;
  convergence and calibrated posterior intervals remain unassessed.
- F `24848482` completed evidence-only aggregation; both independent result
  reviews passed all separate legacy, restart and pilot histories, figures,
  frozen identities and counts. Final F report SHA-256
  `143f4b1ab4e063a76d3aab5ecb8b2b7ea99ff8f4ca534ccde2fcacd13d5d034e`.
  All 12 jobs/36 Slurm rows are terminal, including seven preserved failed
  attempts and five completions. Combined accounting SHA-256
  `9aaa24d1988c3b645360e064a87395ec99e7a09c98d0b9b9423e9f28b27d1509`;
  post-validation root size `179569612` bytes <2 GiB. No active or unaccounted job remains.
- Static continuation validator source SHA-256
  `5699f004fc2f35f3f63af7829c4aadd4ec60005ba5d6237d9a15c02812250714`
  passed two independent read-only source reviews. Its first static run
  caught a compact-summary punctuation marker mismatch; the trace is
  preserved externally. After the text correction it produced
  `ITER006_CONTINUATION_FOUR_RECORD_VALIDATE_PASS`, output SHA-256
  `e696e6a7e0d8878b9b0b1d4266b0f5e3c2d9e2d823e4ae742ec3ed4ac0a22137`.
  The static check also passed against final record text; the one authorized
  scoped local append commit records this closeout. Do not push, merge, edit the
  campaign plan or initialize Iter007.
- One planning-only next proposal: seek a separately approved ABBY/JERC
  independent-initialization convergence and boundary-sensitivity iteration
  under the same frozen science, corrected move and numerical policy. Derive
  finite chain/resource budgets from measured pilot throughput, and predeclare
  independent seeds, prior-unit occupancy, late-block movement,
  autocorrelation/ESS where estimable and component/posterior-predictive
  diagnostics. Assess whether early near-boundary occupancy and declining
  late-block acceptance persist. This proposal grants no runtime authority.
