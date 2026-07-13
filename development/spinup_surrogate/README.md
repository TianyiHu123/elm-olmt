# Spinup Surrogate Development Log

This folder tracks iterative development for the standalone spinup surrogate.

## Goals

- Keep an auditable history of each iteration (changes, results, decisions).
- Separate lightweight tracked metadata (Git) from heavy run outputs (`/pscratch/...`).
- Enable smooth handoff to new chat sessions with minimal context loss.

## Structure

- `registry.csv`: one-row summary per iteration.
- `iterations/iterXXX.md`: detailed notes for each iteration.
- `summaries/`: copied small summary JSON files used for comparisons.
- `slurm/`: iteration-specific Slurm scripts (or references).
- `handoff/CURRENT.md`: single source of truth for the next session.

## Standard Iteration Loop

1. Define objective + variant matrix in `iterations/iterXXX.md`.
2. Run variants on HPC via Slurm.
3. Aggregate metrics (`summarize_spinup_stats.py`) per variant.
4. Copy summary JSONs into `summaries/iterXXX/`.
5. Decide next action and update:
   - `registry.csv`
   - `handoff/CURRENT.md`

## Metric Focus

Track for `TOTSOMC` and `TOTSOMN`:

- median `r2_val`
- median `r2_gap`
- median `rmse_ratio`
- `overfit_warning_fraction`
- tails (`min r2_val`, `max rmse_ratio`)
