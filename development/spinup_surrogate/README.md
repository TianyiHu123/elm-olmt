# Spinup Surrogate Development Log

This folder tracks iterative development for the standalone spinup surrogate.

## Goals

- Keep an auditable history of each iteration (changes, results, decisions).
- Separate lightweight tracked metadata (Git) from heavy run outputs (`/pscratch/...`).
- Enable smooth handoff to new chat sessions with minimal context loss.
- Use one repository-tracked workflow instead of project-specific agent skills.

Site path note: heavy run outputs use `/pscratch/...` on Perlmutter and `/xdisk/...` on Puma.

## Structure

- `WORKFLOW.md`: canonical instructions for planning, execution, closeout, and portability.
- `registry.csv`: one-row summary per iteration.
- `iterations/iterXXX.md`: detailed notes for each iteration.
- `summaries/`: copied small summary JSON files used for comparisons.
- `slurm/`: iteration-specific Slurm scripts (or references).
- `tools/`: reusable analysis and validation utilities shared across iterations.
- `migrations/`: site-transition-specific migration utilities outside the iteration lifecycle.
- `handoff/CURRENT.md`: live control record for the active iteration and next session.
- `templates/`: blank iteration and handoff scaffolds; not runtime artifacts.
- `../hpc/`: shared site profiles, beginning with `perlmutter.md`.

## Records

`CURRENT.md` is the source of truth for current phase, active job IDs, and next action.
`iterations/iterXXX.md` files are the permanent detailed evidence records. Start new sessions
from the handoff, then read the latest report in full plus preceding reports and registry rows
to avoid repeating work.

Follow [`WORKFLOW.md`](WORKFLOW.md) for the complete lifecycle and use the selected
[`development/hpc/`](../hpc/) profile for scheduler-specific behavior.
