# Spinup Surrogate - Current Handoff (iter003 failed, source-level debug next)

## Current Objective

`iter003` is closed as failed. The next iteration must profile and reduce source-level memory/I/O overhead before another multicase sweep.

## Best Variant So Far

From the last successful iteration (`iter001` single-case), `tuned_nn` (tied with `no_clim` and `reduced_clim`) remains the best available baseline.

No winner was selected in `iter002` or `iter003` because fail-fast terminated before aggregation.

## Evidence (key metrics and failure signals)

`iter002` initial matrix outcomes (30 seeds planned per variant):

- `multi_all` (`55918399`): `5 COMPLETED`, `25 TIMEOUT`
- `multi_params_surface` (`55919047`): `4 COMPLETED`, `26 TIMEOUT`
- `multi_params_clim` (`55919049`): `4 COMPLETED`, `26 TIMEOUT`
- `multi_params_only` (`55919050`): `4 COMPLETED`, `26 TIMEOUT`

One approved retry pilot at `--time=00:15:00`:

- job `55950336` (`multi_all`, `--array=1-5`)
- result: `1 COMPLETED`, `1 TIMEOUT`, remaining pending retry tasks cancelled by fail-fast
- representative rows:
  - `55950336_2|TIMEOUT|0:0|00:15:15`
  - `55950336_2.batch|CANCELLED|0:15|00:15:20`

`iter003` pilot outcomes at `--time=00:20:00`:

- Initial `n_jobs=4` pilot (`55952433`): seed 10001 completed at `00:18:13`, seed 10002 timed out at `00:20:21`; remaining tasks were fail-fast cancelled.
- Retry `n_jobs=8` pilot (`55954503`): 4/5 tasks timed out (`00:20:09-00:20:22`); only seed 10004 completed at `00:18:19`.
- `seff`: memory reached `41.97/42.00 GB` on the largest tasks; CPU efficiency was only `0.26-0.42%`.

## What Changed in Latest Iteration

- Closed `iter002` as `failed` with full debug bundle and provenance.
- Recorded failed status in `development/spinup_surrogate/registry.csv`.
- Completed a grilling session and locked `iter003` planning direction:
  - success gate: runtime + quality
  - optimization priority: parallelism tuning first
  - quality tolerance: tight (`r2_val` drop `<=0.01`, `rmse_ratio` increase `<=0.02`)
  - runtime target: no timeout with walltime target `<=00:20:00` in pilot
- Closed `iter003` as failed after both the initial pilot and one retry failed the runtime gate.
- Corrected the NERSC Shared-QOS resource interpretation: `42GB` memory forces approximately `23` hyperthread CPUs, rounded to `AllocCPUS=24` / `12` physical cores, regardless of `cpus-per-task=4` versus `8`.
- Preserved partial retry stats for seeds 10003 and 10004 in scratch; skipped aggregation and winner selection.

## Open Risks / Unknowns

- `00:20:00` still times out for heterogeneous seeds under both tested `n_jobs` profiles.
- Peak memory is at the 42GB request ceiling, so memory reduction is required before meaningful CPU-allocation tuning.
- Very low `seff` CPU efficiency may reflect I/O/wait and/or incomplete accounting of joblib child processes; source-level timing is required.
- Repeated nine-case forcing-data preparation is the leading source-level debug hypothesis.

## Next Iteration Plan (`iter004`, not started)

1. Add source-level timing around case loading, forcing-data discovery/read, design-matrix construction, GridSearchCV, and permutation importance.
2. Identify and reduce repeated forcing-data reads and peak in-memory copies.
3. Keep the same nine-case scientific setup and compare memory peak plus phase timings on a tiny pilot.
4. Do not launch a broad matrix until a new pilot has no timeout with adequate memory headroom.
5. Reapply the locked quality gate only after a runtime-safe pilot completes.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter003.md`
   - `development/spinup_surrogate/iterations/iter002.md`
   - `development/spinup_surrogate/iterations/iter001.md`
3. Review `development/spinup_surrogate/iteration_loop.md`.
4. Treat `iter003` as closed/failed; do not submit any remaining iter003 jobs.
5. Scaffold a source-debug iter004 plan only after the standard runtime contract confirmation.

## Ready/Blocked Status for Next Iteration

`iter003` is blocked/failed on the runtime gate. The next session is ready for source-level memory/I/O debugging; no full matrix is authorized.

## Required User Decisions Before Execution (if any)

No new strategy decision is pending; standard session run-contract confirmations still apply before any iter004 submission.

Standard session run-contract confirmations still apply before any new submissions.

## Artifact Paths

- Prior failed iteration report: `development/spinup_surrogate/iterations/iter002.md`
- Latest failed iteration report: `development/spinup_surrogate/iterations/iter003.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter002 script root: `development/spinup_surrogate/slurm/iter002/`
- Iter002 scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`
- Iter003 report path: `development/spinup_surrogate/iterations/iter003.md`
- Iter003 script root: `development/spinup_surrogate/slurm/iter003/`
- Iter003 retry scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_retry_multi_all`

## Files Modified in Repo (latest cycle)

- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter003.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Failure Debug Bundle Reference (required when latest iteration status is `failed`)

See `development/spinup_surrogate/iterations/iter003.md` sections:

- `Pilot Execution Log`
- `Retry diagnostics`
- `Resource interpretation correction`
