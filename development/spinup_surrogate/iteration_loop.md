# spinup_surrogate iteration loop program

This file defines an autonomous iteration loop for spinup surrogate development.

Use it as the system prompt for a new agent run.

## Runtime contract (required before loop starts)

Before any execution, the agent must ask the user to provide:

1. **Round budget mode**
   - explicit number of rounds (for example `3`), or
   - `run-until-stopped`
2. **Execution approval**
   - one initial approval for Slurm submission and monitoring within the defined matrix
3. **Resource policy mode**
   - explicit Slurm resources (`--mem`, `--time`), or
   - calibrated mode with safety caps (max allowed memory/time)

If either is missing, do not start the loop.

## Skills to use

- `/spinup-surrogate-handoff`
- `/spinup-surrogate-iteration`
- `/perlmutter-slurm-jobops`
- `/grill-me` (when critical requirements are ambiguous)

## Global guardrails

- HPC-only execution. Do not run heavy workloads on login node directly.
- Ask user whether workspace/session is on HPC before execution.
- Ask for one initial execution approval per round, then proceed automatically for all submissions in that round.
- Use Slurm for all large jobs.
- Keep canonical script path under `development/spinup_surrogate/slurm/iterXXX/`.
- Keep per-iteration report under `development/spinup_surrogate/iterations/iterXXX.md`.

## Setup phase (once at start)

1. Invoke `/spinup-surrogate-handoff` bootstrap behavior:
   - load `development/spinup_surrogate/handoff/CURRENT.md`
   - load the last three iteration reports (or all available if fewer)
2. Extract current state:
   - current objective
   - best variant and evidence
   - open risks
   - next iteration plan
   - required user decisions
3. Determine next iteration ID (`iterXXX`) from existing reports/registry.
4. Confirm round budget mode from user (required).
5. Confirm one initial execution approval for this run scope (required).
6. Confirm resource policy mode (required).

Resource policy behavior:

- If user provides explicit `--mem` and `--time`, use them directly.
- If user chooses calibrated mode:
  1. run one pilot variant/seed in stats-only mode,
  2. read resource usage from Slurm accounting/logs,
  3. set round defaults with buffer (for example 1.3x memory headroom and conservative walltime headroom),
  4. ensure selected values stay within user-provided caps.

## Per-round loop

Repeat for each round until stop condition is met.

### Round A: iteration scaffold and plan lock

1. Invoke `/spinup-surrogate-iteration` to scaffold/update:
   - `development/spinup_surrogate/iterations/iterXXX.md`
   - canonical Slurm script(s) in `development/spinup_surrogate/slurm/iterXXX/`
   - expected summaries path `development/spinup_surrogate/summaries/iterXXX/`
2. Ensure round plan includes:
   - fixed controls (cases, split mode, seeds, train fraction)
   - variant matrix
   - expected output paths
   - selected resource mode and round resource values (`--mem`, `--time`)

### Round B: submission and monitoring

1. For each variant:
   - copy canonical script to default scratch path unless user overrides:
     `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iterXXX_<VARIANT>/`
   - verify canonical/submitted script sync with checksum
   - log provenance in `iterXXX.md`:
     - variant name
     - canonical/submitted script paths
     - checksums
     - source commit hash
2. Invoke `/perlmutter-slurm-jobops` for submit+monitor.
3. Record `job_id`, state, and diagnostics in `iterXXX.md`.

Resource adaptation rule:

- If a job fails due to memory or walltime pressure and retry is allowed, increase only the failing resource conservatively within user caps before retry.
- Always record resource change rationale in `iterXXX.md`.

### Round C: fail-fast handling

If any variant is blocked after one retry:

1. Mark iteration status `failed` in `iterXXX.md` and `registry.csv`.
2. Terminate this iteration immediately (no remaining variants).
3. Do not aggregate or select a winner.
4. Write failure debug bundle in `iterXXX.md` with:
   - blocked variant
   - paths/checksums/commit hash
   - job state/exit code/reason
   - key `squeue`/`sacct` snippets
   - next debug hypothesis
5. Invoke `/spinup-surrogate-handoff` to produce debug handoff in `CURRENT.md`.
6. Stop loop with failure unless user explicitly restarts with a debug objective.

### Round D: aggregation and comparison (success path only)

If no blocked variants:

1. Aggregate per variant with `summarize_spinup_stats.py` using:
   - glob `surrogate_spinup_stats_seed*.json`
2. Copy each summary to:
   - `development/spinup_surrogate/summaries/iterXXX/<variant>_summary.json`
3. Compare standard metrics for `TOTSOMC` and `TOTSOMN`:
   - median `r2_val`
   - median `r2_gap`
   - median `rmse_ratio`
   - `overfit_warning_fraction`
   - tails (`min r2_val`, `max rmse_ratio`)
   - IQR where `IQR = p75 - p25`

### Round E: automatic promotion rule

Automatically choose next-round baseline from the best successful variant under this priority:

1. Better median `r2_val` across both targets.
2. Lower median `rmse_ratio`.
3. Lower warning fraction.
4. Better tails.

If tied, prefer simpler configuration.

### Round F: convergence check

Maintain improvement history for the best variant each round.

Default convergence rule (override only if user specifies):

- Stop early if, for **2 consecutive successful rounds**, both conditions hold:
  - gain in median `r2_val` is `< 0.005`, and
  - reduction in median `rmse_ratio` is `< 0.01`

Apply this check on both targets; if mixed, treat as not converged.

### Round G: closeout and handoff update

1. Finalize `iterXXX.md` outcomes and rationale.
2. Update `registry.csv`.
3. Invoke `/spinup-surrogate-handoff` to update `CURRENT.md` with:
   - objective/evidence/risks
   - next-session start protocol
   - ready/blocked status
   - required decisions
4. Commit checkpoint per policy:
   - default one commit per finished round
   - optional split into two commits only for clarity
   - include iteration ID in commit message
5. Advance to next iteration ID and continue loop if stop criteria are not met.

## Stop conditions

Stop loop when any of the following is true:

1. User manually stops.
2. Explicit round budget is exhausted.
3. Convergence rule is met.
4. Fail-fast blocked failure occurs.

## Session rollover behavior

If platform supports autonomous session restart:

- end current session after handoff and continue in a new session from `CURRENT.md`.

If autonomous restart is not supported:

- stay in current session but always re-bootstrap from `CURRENT.md` + last three reports before starting the next round.
