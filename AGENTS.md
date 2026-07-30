# Repository Agent Guidance

These instructions apply to the entire repository.

## Execution Safety

- Before running repository Python/scripts or changing scheduler state, confirm that the active
  session is on HPC and obtain explicit execution authority for the stated runtime contract.
- Treat read-only inspection and static validation as non-execution. Do not use that exception to
  launch training, model runs, data generation, or scheduler operations.
- Run large, long, multi-CPU, high-memory, or sweep workloads through the selected HPC scheduler;
  do not run them directly on a login node.
- Do not submit or cancel jobs, retry application/code failures, or create commits unless the
  applicable runtime contract or user instruction explicitly authorizes the action.

## Spinup-Surrogate Workflow

- Use `development/spinup_surrogate/WORKFLOW.md` as the canonical lifecycle policy.
- Start each session from `development/spinup_surrogate/handoff/CURRENT.md`, then read the recent
  iteration records and the selected profile under `development/hpc/`.
- Keep one primary agent as the sole writer and scheduler operator. Any reviewer must remain
  read-only unless the user explicitly changes that ownership.
- Preserve historical iteration reports and Slurm scripts as provenance. Put new site facts in a
  shared HPC profile instead of rewriting completed iterations.

The existing `.cursor/rules/` files remain the Cursor-specific expression of these safeguards.
