# iter013 - Stage A initialization-cloud comparison

Closeout identity: Iteration ID `iter013`; Status `completed`; Work type `validation`; Objective `Stage-A TIM vs Iter012 initialization-cloud comparison at ABBY and JERC`; Bounded scope `preflight; ABBY analysis; JERC analysis; aggregate; handoff validation`; Overall acceptance result `pass`; Decision `ABBY separated/diversity_dominated; JERC separated/diversity_dominated`

## Status

- Iteration ID: `iter013`
- Work type: `validation`
- Run slug: `spinup_forcing_coupling_iter013_<work_unit>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-17T17:59:47-07:00`
- Closed: `2026-08-17T18:55:00-07:00`

## Finalized Plan

- Sequential ID and work type: `iter013`; `validation`
- Evidence-derived objective and optional hypothesis: compare Iter009 TIM high-posterior
  start clouds with Iter012 production candidate-pool start clouds at ABBY and JERC, and
  test whether the Iter012 640/64 sets are high-posterior rank sets or diversity-dominated
  sets. Hypothesis: TIM walkers are a compact high-posterior neighborhood while Iter012
  pools/walkers span near-full prior width and are not the ledger top-k sets.
- Bounded scope: Stage A only; five staged units; no MCMC.
- Decision rule: locked geometry and selection classes from the Iter013 plan.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approved the complete package`; `2026-08-17T17:59:00-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Stage-A TIM vs Iter012 init-cloud comparison; 5 staged units within max 8; stop after validated closeout; no MCMC |
| Confirmed HPC system and site profile | UArizona Puma; `development/hpc/puma.md` |
| Approved output and storage policy | `.../spinup_forcing_coupling_iter013/` with `preflight/`, `analysis/{abby,jerc}/`, `aggregate/`, `handoff_validation/` |
| Lifecycle authority | Prepare through closeout; outside-sandbox `sbatch`/monitoring/`scancel`; one local closeout commit; no push |
| Resources and retry boundaries | Preflight 4/20GB/30m; analysis 16/80GB/4h; aggregate/handoff 4/20GB/1h; one preflight correction; one unchanged scheduler/resource retry per leaf; max 8 tasks |
| Closeout branch | One local closeout commit authorized; no push |

## Upstream Dependencies and Source Lock

- Repository commit at materialization: `d0e556b6cc2f261c7edcf64d0690642788af8f8f`
- Source manifest SHA-256 after authorized preflight correction: `a94bb57013d44f76db7453bff625608af7f9c80ec700dbc6be26eefd7e45efd4`
- Dependency manifest SHA-256: `e5035c9e701bc886d389a1d5fd39c18eec4bc58d5520da7a1ed2e599bb22fb99`
- Environment: `OLMT_puma` / micromamba `2.0.2-2`
- All planned TIM and Iter012 artifact hashes verified in preflight `23584377`

## Acceptance Gates and Decision Rule

- Required completeness met for both sites.
- Geometry and selection classes applied exactly as locked.
- Classes are descriptive; no posterior promotion; no initializer change; no MCMC authorized.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| preflight | `23584374` | FAILED `1:0` | stale source-manifest vs `materialize_iter013.sh`; classified `preflight_launcher_manifest`; preserved under `preflight/failed_23584374/` |
| preflight retry | `23584377` | COMPLETED `0:0` | authorized minimal manifest refresh; `PREFLIGHT_PASS`; MaxRSS 11.29 GB |
| analysis_abby | `23584383` | COMPLETED `0:0` | `ANALYZE_PASS`; `separated` / `diversity_dominated`; 00:03:52; MaxRSS 5.16 GB |
| analysis_jerc | `23584384` | COMPLETED `0:0` | `ANALYZE_PASS`; `separated` / `diversity_dominated`; 00:02:42; MaxRSS 4.83 GB |
| aggregate | `23584395` | COMPLETED `0:0` | `AGGREGATE_PASS`; 00:00:15 |
| handoff_validation | `23584405` | COMPLETED `0:0` | `ITER013_HANDOFF_VALIDATE_PASS abby=separated/diversity_dominated jerc=separated/diversity_dominated` |

## Independent Read-Only Review

- Reviewer: independent agent `8a86b8b1-3a11-4e4e-a219-6d36041ece0e`
- Reviewed source hash: first `b39902d0...` (`block`); re-review `985cb40a...` (`pass_with_concerns`)
- Outcome: `pass_with_concerns`
- Response: P0/P2 fixed before materialize; residual P3 work-unit wording aligned; proceeded with recorded rationale.

## Execution and Diagnostics

- Static validation: `py_compile` and `bash -n` passed before review and after P0/P2 fixes.
- Preflight correction: one authorized refresh of `source_manifest.sha256` after NFS/self-hash timing mismatch on `materialize_iter013.sh`.
- Empirical-range warnings appeared during TIM common-target re-evaluation; they did not change gate results.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| ABBY analysis | yes | geometry/topk/common-target JSON + overlay | pass | `separated`; `diversity_dominated`; walker overlap 0; pool∩top640 = 0 |
| JERC analysis | yes | geometry/topk/common-target JSON + overlay | pass | `separated`; `diversity_dominated`; walker overlap 0; pool∩top640 = 0.0078125 |
| aggregate | yes | `aggregate_result.json` | pass | both-site decision recorded |

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `ABBY separated/diversity_dominated; JERC separated/diversity_dominated`
- Quantitative headline: ABBY max walker Wasserstein `0.490`, TIM pairwise `0.050` vs Iter012 walker pairwise `1.873`; JERC max walker Wasserstein `0.540`, TIM pairwise `0.069` vs Iter012 walker pairwise `1.818`. TIM median common-target logp exceeds Iter012 walker stored medians (ABBY Δ `+2216`; JERC Δ `+31578`).
- Interpretation: the Iter012 independent search did not reproduce the TIM neighborhood. Production 640/64 sets are diversity-dominated, not top-k rank sets. This supports the Iter012 JERC mixing hypothesis (initialization geometry) without authorizing a TIM revert.
- Limitations: `/xdisk` temporary; Stage A does not run MCMC; common-target TIM logp uses Iter012 targets while TIM stored chain logp remains non-comparable.

## Proposed Next-Iteration Plan (Planning Only)

<!-- ITER014_PLAN_BEGIN -->
## Proposed Iter014 plan - JERC walker-selection contrast on frozen Iter012 pool

- Sequential ID: `iter014`
- Status: `not_initialized`
- Work type: `validation`
- Objective: test whether JERC production mixing can be repaired by changing only how 64
  walkers are taken from the frozen Iter012 independent pool, without reverting to TIM or
  regenerating the pool.
- Evidence basis: Iter013 classified both sites `separated` and `diversity_dominated`. TIM
  walkers are compact and higher under the Iter012 target; Iter012 walkers span near-full
  prior width and almost never coincide with ledger top-64/top-640. Independent search remains
  the preferred production philosophy; the live question is walker placement.
- Hypothesis: selecting 64 walkers from a high-posterior membership subset of the same Iter012
  JERC pool recovers TIM-like seed agreement under `hourly/0.75`, while the current
  strata/maximin 64-walker rule does not.

### Fixed targets and dependencies

- JERC only; locked Iter012 hourly target and frozen Revision1 JERC pool/ledger hashes.
- Do not use TIM/Iter008/009/011 transferred states.
- Preserve DEMove `0.75`, 80/20 mixture, seeds `9009--9011`.

### Tentative matrix

- Control: existing Iter012 JERC production selection ledgers (no rerun required if reused as
  evidence only).
- Variant A: top-64 unique ledger states by stored physical log posterior.
- Variant B: robust high-posterior subset (e.g. top decile of the frozen pool) then maximin to 64.
- Optional short diagnostic length `64 x 8000` only; no 32k production extension in Iter014.

### Gates and exclusions

- Integrity gates only plus the Iter012 diagnostic qualification screens for cross-seed
  Wasserstein and acceptance. No posterior promotion. No pool regeneration. No ABBY. No
  likelihood change.
- Fresh consolidated kickoff required before any scaffolding or submission.
<!-- ITER014_PLAN_END -->

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter013/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
  - identity: `slurm/iter013/validate_iter013_handoff.py`; job `23584405`; output `ITER013_HANDOFF_VALIDATE_PASS abby=separated/diversity_dominated jerc=separated/diversity_dominated`
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit `74fcd59`
