# iter014 - JERC high-likelihood candidate-pool reconstruction

Closeout identity: Iteration ID `iter014`; Status `completed`; Work type `implementation`; Overall acceptance result `pass`; Decision `partial_repair`

## Status

- Iteration ID: `iter014`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter014_<work_unit>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-17T19:48:15-07:00`
- Closed: `2026-08-17T22:34:00-07:00`

## Finalized Plan

- Sequential ID and work type: `iter014`; `implementation`
- Evidence-derived objective and optional hypothesis: rebuild the JERC 640-member
  candidate pool from the frozen Iter012 Revision1 ledger under
  `rank_dominated` and `hybrid_high_l_maximin` (`high_l_quantile=0.90`), enable those
  rules in reusable initialization, and test whether diagnostic `64 x 8000` MCMC under
  `hourly/0.75` recovers TIM-like seed agreement versus the reused Iter012 diversity
  control. Hypothesis: high-L pool membership, not walker sampling alone, is the
  repair lever.
- Bounded scope: code change; preflight; rebuild eligible rules; hybrid-only MCMC if A
  geometry-fails; evaluate; aggregate; handoff validation. No ABBY, TIM starts, new
  search, likelihood/DE change, or 32k extension.
- Decision rule: `repair_supported` / `partial_repair` / `not_supported` /
  `geometry_gate_failed`; no posterior promotion.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | original `approved the complete package` `2026-08-17T19:48:15-07:00`; revision `approved the revised package` `2026-08-17T20:18:46-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Execute Iter014 with revised geometry-gate handling; hybrid required; A may be geometry_gate_failed without MCMC; stop after validated closeout |
| Confirmed HPC system and site profile | UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition `standard` |
| Approved output and storage policy | `/xdisk/.../spinup_forcing_coupling_iter014/` with `preflight/`, `pool_rebuild/{rank_dominated,hybrid_high_l_maximin}/`, `production/{rule}/seed_{9009,9010,9011}/`, `evaluation/`, `aggregate/`, `handoff_validation/`; `/xdisk` temporary/unbacked |
| Locked dependencies, scope, exclusions, gates, and decision rule | JERC hourly target `26e5caa0…`; ledger `25382a57…`; control pool `32d2ba5f…`; forcing `8d139b32…`; spinup `1427dc56…`; DEMove `0.75`; seeds `9009--9011`; `64x8000`; control reuse only |
| Lifecycle authority | Prepare through closeout; outside-sandbox `sbatch`/monitoring/`scancel` as contracted |
| Resources and retry boundaries | Preflight 4/30m; rebuild 8/2h; production 16/4h; evaluate/aggregate/handoff 1 attempt; max 18 tasks; revised path allows A geometry_gate_failed |
| Cancellation scope | Recorded Iter014 job IDs only; universal pre-execution defect or user-directed emergency |
| Outside-sandbox authority | Locked `sbatch`; job-scoped read-only monitoring/accounting; bounded `scancel` |
| Closeout branch | One local closeout commit authorized; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| JERC Revision1 ledger | Frozen search ledger | `.../iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz` | Iter012 Revision1 | `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d` | Iter013/012 locked |
| JERC control pool | Diversity baseline reference | same tree `candidate_pool.npz` | Iter012 Revision1 | `32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96` | evidence only |
| Hybrid rebuilt pool | Variant B init pool | `.../iter014/pool_rebuild/hybrid_high_l_maximin/artifacts/candidate_pool.npz` | Iter014 rebuild | `40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df` | preflight+rebuild |
| Forcing SR artifact | Coupled likelihood | iter002 release pickle | trusted release | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | prior campaigns |
| Spinup drop21_corr080 | Coupled spinup | Iter012 spinup release | trusted release | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | prior campaigns |
| JERC observations | Likelihood obs | NEON eval v4 | site obs | `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` | prior campaigns |
| Iter012 JERC evaluation | Control screens | `summaries/iter012/jerc_evaluation_result.json` | Iter012 closeout | mean acc≈0.187; W≈0.548 | reuse only |

- Repository commit at materialization: `440fbdc58cd449a7ca4e4a51db7f180aae04ecb5`
- Source manifest SHA-256 (final preflight): `56a21ac355fae47924d3db523361d412c497e9857f82863d1e4489c74bf85984`
- Dependency manifest SHA-256: `d1ca53ca3f28de661a5c4b83d72f8fa6a3c8e7ccf4fc9ff5e6f07f1160001003`
- Environment identity: `OLMT_puma` / micromamba `2.0.2-2`

## Acceptance Gates and Decision Rule

- Required completeness: revised path — preflight pass with hybrid eligible; hybrid rebuild;
  three hybrid production leaves; both-rule evaluation (A as geometry stub); aggregate;
  handoff validation
- Acceptance gates: integrity; pool geometry; Iter012 diagnostic screens for acceptance and
  cross-seed Wasserstein (characterization)
- Decision rule: `repair_supported` if integrity and mean acceptance ≥0.25 and W≤0.05;
  `partial_repair` if integrity and improvement vs control on acceptance and/or W without
  full repair; `geometry_gate_failed` if A fails geometry before MCMC; else `not_supported`.
  No posterior promotion.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `slurm/iter014/preflight_iter014.*` | `.../preflight/` | `.../preflight/` | locked deps | `440fbdc` + source `56a21ac…` | `23584865` | FAILED `1:0` | A geometry; preserved |
| preflight | same | same | same | same | stale validate path | `23584908` | FAILED `1:0` | launcher/manifest; preserved |
| preflight | same | refreshed manifest | same | same | `56a21ac…` | `23584912` | COMPLETED `0:0` | hybrid eligible; A geometry_gate_failed |
| rebuild_rank_dominated | n/a | n/a | `.../pool_rebuild/rank_dominated/` | ledger | n/a | `rejected_geometry_rank_rebuild` | rejected | revised package; no MCMC path |
| production A × seeds | n/a | n/a | `.../production/rank_dominated/...` | n/a | n/a | `rejected_geometry_rank_9009..9011` | rejected | no A MCMC |
| rebuild_hybrid | `rebuild_pool_iter014.slurm` | `.../pool_rebuild/hybrid_high_l_maximin/` | same | ledger | `440fbdc` | `23584917` | COMPLETED `0:0` | pool `40ac807e…` |
| production hybrid ×3 | `production_iter014.slurm` | `.../production/hybrid_high_l_maximin/seed_*` | same | hybrid pool | `440fbdc` | `23584923`–`23584925` | COMPLETED `0:0` | FIXED_PRODUCTION_PASS |
| evaluate | `evaluate_iter014.*` | `.../evaluation/` | same | productions | `440fbdc` | `23585172` | COMPLETED `0:0` | EVALUATION_PASS |
| aggregate | `aggregate_iter014.*` | `.../aggregate/` | same | evaluations | `440fbdc` | `23585173` | COMPLETED `0:0` | overall `partial_repair` |
| handoff_validation | `validate_iter014_handoff.*` | `.../handoff_validation/` | same | four records | closeout | `23585174` | COMPLETED `0:0` | `ITER014_HANDOFF_VALIDATE_PASS` |

## Independent Read-Only Review

- Reviewer: independent agent `ee82d52d-eb92-4bad-a21f-b1509c2d1d75`
- Reviewed source hash: first `0ac79e15...` / materialize `31f7922b...` (`block`); re-review coupling `1167594f...` / materialize `78bffbd2...` (`pass`)
- Outcome: `pass`
- Findings and primary-agent response: P1 atomic rebuild and max-18 attempt envelope fixed before materialize; P2 aggregate policy string, handoff ceiling, and explicit evaluate observation fixed; quantile widening retained per locked plan with preflight diagnostics.

## Execution and Diagnostics

- Static validation: `py_compile` / `bash -n` on pipeline + Iter014 package passed before review
- Preflight `23584865` FAILED on `rank_dominated` condition `1.72e7 > 1e6`; classified application/scientific
- Revised package authorized; preflight `23584908` FAILED on stale source-manifest entry for
  `validate_iter014_handoff.py`; corrected then `23584912` COMPLETED with
  `eligible=hybrid_high_l_maximin`, hybrid condition ≈359, A `geometry_gate_failed`
- Hybrid rebuild `23584917` COMPLETED; productions `23584923`/`23584924`/`23584925` COMPLETED
  (`00:57:46` / `01:10:01` / `01:48:40`; MaxRSS ~5.9–8.1 GB)
- Evaluate `23585172` and aggregate `23585173` COMPLETED `0:0`

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| rank_dominated | geometry fail; no MCMC | preflight condition `1.72e7` | fail geometry | `geometry_gate_failed` |
| hybrid_high_l_maximin | yes | integrity pass; mean acc `0.1898`; W `0.4365` vs control `0.1866`/`0.5484` | integrity pass; not full repair | `partial_repair` |
| aggregate | yes | `aggregate_result.json` | pass | overall `partial_repair` |

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `partial_repair`
- Hybrid seed acceptances: `0.0891` / `0.2211` / `0.2591`; diagnostic label
  `fixed_length_inconclusive`; no posterior promotion
- Limitations: A is scientifically infeasible under locked geometry gates; hybrid improves
  cross-seed W modestly but remains far from the `W≤0.05` and `acc≥0.25` repair thresholds;
  short `64×8000` diagnostics only; `/xdisk` temporary/unbacked
- Next action: authorized local closeout commit (no push)
- Four-record validator: job `23585174`; command
  `python3 .../validate_iter014_handoff.py --aggregate .../aggregate_result.json --accounting .../accounting.csv`;
  output `ITER014_HANDOFF_VALIDATE_PASS overall=partial_repair rank_dominated=geometry_gate_failed hybrid_high_l_maximin=partial_repair`

## Proposed Next-Iteration Plan (Planning Only)

Planning-only Iter015: treat high-L pool membership as a partial but insufficient lever at
JERC, and test whether longer fixed-length hybrid chains and/or a milder high-L quantile /
proposal-scale tweak can clear the remaining Wasserstein gap without reverting to TIM or
reopening search. Do not initialize until a fresh consolidated kickoff.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter014/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified local closeout commit (no push)
