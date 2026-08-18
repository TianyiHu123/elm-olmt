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
