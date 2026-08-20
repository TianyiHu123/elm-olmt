# iter016 - multi-seed MAP ensemble operational experiment

Closeout identity: Iteration ID `iter016`; Status `completed`; Work type `implementation`; Objective `multi-seed MAP ensemble operational experiment at ABBY daily/0.50 and JERC hourly/0.75`; Bounded scope `1 preflight; 2 hybrid rebuilds; 2 production arrays (18 tasks); 1 analysis; 1 handoff validation`; Overall acceptance result `pass`; Decision `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`

## Status

- Iteration ID: `iter016`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter016_<work_unit>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-19T15:30:00-07:00`
- Closed: `2026-08-19T18:00:00-07:00`

## Finalized Plan

Approved `ITER016_PLAN_BEGIN` block in `handoff/CURRENT.md` (kickoff `2026-08-19T15:22:00-07:00`).

## Consolidated Kickoff Package and Runtime Contract

See kickoff block in `iterations/iter016.md` initialization and `handoff/CURRENT.md` at closeout.

## Provenance and Job Ledger

| Work unit | Canonical script | Job ID | State | Exit | Elapsed | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| materialization | `materialize_iter016.sh` | local | pass | — | — | `MATERIALIZE_PASS` |
| preflight | `preflight_iter016.slurm` | `23594435` | COMPLETED | `0:0` | `00:03:10` | `PREFLIGHT_PASS` |
| pool_rebuild_abby | `rebuild_pool_iter016.slurm` | `23594478` | COMPLETED | `0:0` | `00:02:49` | pool `3627bb1d…` |
| pool_rebuild_jerc | `rebuild_pool_iter016.slurm` | `23594479` | COMPLETED | `0:0` | `00:01:46` | pool `40ac807e…` |
| production_array_abby | `production_array_iter016.slurm` | `23594502` | COMPLETED | `0:0` | max `01:53:41` | 9/9 leaves |
| production_array_jerc | `production_array_iter016.slurm` | `23594503` | COMPLETED | `0:0` | max `01:36:01` | 9/9 leaves |
| analysis | `analyze_iter016.slurm` | `23595316` | COMPLETED | `0:0` | `00:04:14` | `ANALYSIS_PASS` |
| analysis (failed) | `analyze_iter016.slurm` | `23595280`, `23595293` | FAILED | `1:0` | — | tool schema fixes |
| handoff_validation | `validate_iter016_handoff.slurm` | `23595354` | COMPLETED | `0:0` | `00:00:18` | `HANDOFF_VALIDATE_PASS` |
| sr_overlay_replot | `replot_sr_overlay_iter016.slurm` | `23595515` | COMPLETED | `0:0` | `00:01:46` | valid-mask makeup |

Repository commit at materialization: `eca6014c87012075e51ec48448957395a46e52b7`.

## Independent Read-Only Review

- Outcome: `pass_with_concerns` (array-index recovery deferred; handoff validator expanded at closeout)

## Execution and Diagnostics

- Eighteen production leaves under `production/{abby,jerc}/<config>/seed_<seed>/`.
- Analysis package under `summaries/iter016/` and scratch `analysis/`.
- Tool fixes: `ensemble_common.py` MAP from chain; `plot_ensemble_sr_overlay.py` ELM baseline.

## Validation, Evaluation, and Decision

- Integrity: all gates passed.
- Tier A: ABBY 9/9; JERC 6/9 (9009, 9013, 9016 excluded).
- Diagnostics: both sites `equifinal_candidate` (informational).
- Decision: `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`.
- No posterior promotion.

## Closeout Checklist

- [x] Iteration report finalized (`summaries/iter016/ITER016_REPORT.md`)
- [x] Required evidence in `summaries/iter016/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator pass recorded (`23595354`)
- [x] Authorized closeout commit
