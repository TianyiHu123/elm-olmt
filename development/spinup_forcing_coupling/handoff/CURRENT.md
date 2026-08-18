# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter013`; Status `completed`; Work type `validation`; Objective `Stage-A TIM vs Iter012 initialization-cloud comparison at ABBY and JERC`; Bounded scope `preflight; ABBY analysis; JERC analysis; aggregate; handoff validation`; Overall acceptance result `pass`; Decision `ABBY separated/diversity_dominated; JERC separated/diversity_dominated`

## Live state

- Active iteration: `iter013`
- Status: `completed`
- Phase: `closed`
- Work type: `validation`
- Objective: `Stage-A TIM vs Iter012 initialization-cloud comparison at ABBY and JERC`
- Bounded scope: `preflight; ABBY analysis; JERC analysis; aggregate; handoff validation`
- Overall acceptance result: `pass`
- Decision: `ABBY separated/diversity_dominated; JERC separated/diversity_dominated`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter013`
- Last updated: `2026-08-17T18:55:00-07:00`

## Authority and stop boundary

The Iter013 kickoff package approved on `2026-08-17T17:59:00-07:00` (`approved the complete package`) is exhausted at closeout. No further Iter013 submission, retry, or cancellation is authorized. Any continuation requires a fresh consolidated kickoff.

## Best evidence

- Preflight `23584377` `PREFLIGHT_PASS` after one authorized manifest correction (`23584374` failed).
- ABBY/JERC analyses `23584383`/`23584384` and aggregate `23584395` completed `0:0`.
- Both sites: `separated` and `diversity_dominated`.
- ABBY: max walker Wasserstein `0.490`; overlaps `0`; pool∩top640 `0`; TIM pairwise `0.050` vs Iter012 `1.873`.
- JERC: max walker Wasserstein `0.540`; overlaps `0`; pool∩top640 `0.0078125`; TIM pairwise `0.069` vs Iter012 `1.818`.
- TIM walkers remain much higher under Iter012 targets (median Δ ABBY `+2216`, JERC `+31578`).

## Risks and limitations

- `/xdisk` products are temporary and unbacked.
- Stage A did not run MCMC; classes are descriptive only.
- Empirical-range warnings during TIM re-evaluation did not change gates.

## Next action

Iter013 is closed. Copy the Iter014 planning-only proposal below into a fresh consolidated kickoff package before any scaffolding or submission.

<!-- ITER014_PLAN_BEGIN -->
## Proposed Iter014 plan - JERC high-likelihood candidate-pool reconstruction

- Sequential ID: `iter014`
- Status: `not_initialized`
- Work type: `implementation`
- Objective: test whether JERC production mixing can be repaired by rebuilding the 640-member
  candidate pool from the frozen Iter012 independent search ledger under high-likelihood pool
  rules, without reverting to TIM or rerunning Sobol/L-BFGS search.
- Evidence basis: Iter013 classified both sites `separated` and `diversity_dominated`. The
  Iter012 ledger contains high-posterior states, but `choose_candidate_pool` filled most of the
  640 by maximin over the full finite unique set, so the production pool almost never coincides
  with ledger top-640 and walkers miss the TIM neighborhood. Independent search remains the
  preferred production philosophy; the live failure is pool construction, not walker sampling
  alone.
- Hypothesis: a rank-dominated or high-L-restricted hybrid 640 recovered from the same JERC
  ledger restores TIM-like seed agreement under `hourly/0.75`, while the current
  `diversity_maximin` pool does not.

### Code change (required before campaign)

- Extend reusable initialization so pool construction is selectable:
  - `diversity_maximin` — current Iter012 behavior; remain the default.
  - `rank_dominated` — Variant A.
  - `hybrid_high_l_maximin` — Variant B.
- Thread `pool_rule` (and Variant B `high_l_quantile`) through `choose_candidate_pool`,
  `initialize_candidate_pool`, and `initialize_pipeline.py`; record the rule in pool
  diagnostics / search-contract metadata.
- Iter014 execution should rebuild A/B pools from the frozen Iter012 JERC ledger (no new
  search). Full init must still honor the same rules for later campaigns.

### Fixed targets and dependencies

- JERC only; locked Iter012 hourly target and frozen Revision1 JERC ledger/pool hashes.
- Do not use TIM/Iter008/009/011 transferred states as starts.
- Preserve DEMove `0.75`, 80/20 mixture, seeds `9009--9011`.
- Keep current `select_production_walkers` so the contrast is pool policy only.

### Tentative matrix

- Control: reuse existing Iter012 JERC production/evaluation evidence only; no control MCMC
  rerun. Prefer the 8k checkpoint metrics when available for length-matched comparison against
  A/B; otherwise treat the published Iter012 screens as reference.
- Variant A (`rank_dominated`): top-640 unique ledger states by stored physical log posterior;
  then current walker selection; short diagnostic `64 x 8000` for seeds `9009--9011`.
- Variant B (`hybrid_high_l_maximin`): restrict unique finite ledger states to logp at or above
  the 0.90 quantile (top decile); if fewer than 640 uniques, widen the quantile only as needed
  to reach 640; then apply existing strata-required + maximin fill inside that high-L set;
  then current walker selection; same `64 x 8000` seeds.
- No 32k production extension in Iter014.

### Gates and exclusions

- Integrity gates plus the Iter012 diagnostic qualification screens for cross-seed Wasserstein
  and acceptance (characterization only). Retain existing pool geometry gates (full rank,
  nonzero spread, condition number) for all rules unless a rule fails them as scientific
  evidence.
- No posterior promotion. No new Sobol/L-BFGS search. No ABBY. No likelihood or DE-scale
  change. No TIM revert.
- Fresh consolidated kickoff required before any scaffolding or submission.
<!-- ITER014_PLAN_END -->

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter013.md`, and `development/hpc/puma.md`.
2. Reconcile scheduler state before diagnosing drift.
3. Do not initialize Iter014 until a fresh consolidated kickoff is approved.

## Artifact References

- Current report: `development/spinup_forcing_coupling/iterations/iter013.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter013/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter013/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter013`
