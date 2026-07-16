# Spinup Surrogate - Current Handoff (iter004 failed, iter005 feature attribution next)

## Current Objective

`iter004` is closed as failed. Iter005 will return to model-performance and feature-attribution analysis across the nine-case setup; persistent caching work is explicitly deferred.

## Best Variant So Far

From the last successful iteration (`iter001` single-case), `tuned_nn` (tied with `no_clim` and `reduced_clim`) remains the best available baseline.

No winner was selected in `iter002`, `iter003`, or `iter004` because fail-fast terminated before aggregation.

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

`iter004` source-debug outcomes:

- Initial diagnostic (`55957524`) completed in `00:19:19`, but reached `41.97/42.00 GB`.
- Phase timing showed per-case preparation dominated (`53-186s` per case); design matrix, GridSearchCV, and permutation phases were negligible.
- Combined xarray forcing-load retry (`55958511`) completed in `00:26:18`, still reached `41.97/42.00 GB`, and did not improve preparation time.

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
- Closed `iter004` as failed after the diagnostic memory-headroom gate and one source-fix retry failed.
- Added source timing and `pre_dispatch` instrumentation; the combined xarray forcing-load optimization was tested but not promoted.
- Locked iter005 objective to nine-case model-performance and feature attribution using four variants and five seeds per variant.
- Explicitly deferred cache work; iter001 remains historical metric context, not valid nine-case feature-variation evidence.

## Open Risks / Unknowns

- `00:20:00` still times out for heterogeneous seeds under both tested `n_jobs` profiles.
- Peak memory is at the 42GB request ceiling, so memory reduction is required before meaningful CPU-allocation tuning.
- Very low `seff` CPU efficiency may reflect I/O/wait and/or incomplete accounting of joblib child processes; source-level timing is required.
- Repeated nine-case forcing-data preparation is the leading source-level debug hypothesis.
- The next round accepts the current approximately 30-minute per-task runtime as an operational constraint rather than opening another cache/parallelism optimization loop.
- Memory risk remains: the observed peak was approximately 42GB, so iter005 proposes `--mem=48GB` and `--time=00:30:00`.

## Next Iteration Plan (`iter005`, not started)

1. Keep the nine-case `by_member` setup and run five seeds (`10001-10005`) for each NN variant: `multi_all`, `multi_params_surface`, `multi_params_clim`, and `multi_params_only`.
2. Use `--mem=48GB`, `--time=00:30:00`, `N_JOBS=4`, and `PRE_DISPATCH=n_jobs`; record Shared-QOS `ReqTRES`, `MinCPUsNode`, `AllocCPUS`, and `SLURM_CPUS_PER_TASK`.
3. Identify important inputs using both permutation-importance stability and feature-set ablation support, reporting retention frequency, rank, magnitude, sign, IQR, and top-10 overlap across seeds and both targets.
4. Use a provisional strong-feature rule: retained in at least 4/5 seeds, top-10 permutation rank in at least 3/5 seeds, and consistent support across both targets.
5. Treat iter001 metrics as historical reference only, not a nine-case feature gate. Evaluate iter005 internally using `r2_val`, `r2_gap`, `rmse_ratio`, warning fraction, tails, IQR, and expected overfitting relief.
6. Submit all four five-seed arrays in parallel under fail-fast; do not aggregate a blocked variant or launch any larger matrix beyond this five-seed study.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter003.md`
   - `development/spinup_surrogate/iterations/iter004.md`
   - `development/spinup_surrogate/iterations/iter002.md`
   - `development/spinup_surrogate/iterations/iter001.md`
3. Review `development/spinup_surrogate/iteration_loop.md`.
4. Treat `iter004` as closed/failed; do not submit any remaining iter004 jobs.
5. Scaffold the iter005 feature-attribution plan only after the standard runtime contract confirmation.

## Ready/Blocked Status for Next Iteration

`iter004` is blocked/failed on the memory-headroom/runtime objective. Iter005 is ready for nine-case feature attribution; no execution is authorized until the new round contract is confirmed.

## Required User Decisions Before Execution (if any)

The scientific strategy is locked for iter005. Round budget, HPC confirmation, execution approval, and resource policy must still be confirmed before submission.

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
- Iter004 report: `development/spinup_surrogate/iterations/iter004.md`
- Iter004 script root: `development/spinup_surrogate/slurm/iter004/`
- Iter004 diagnostic scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_diag_multi_all`
- Iter004 source-fix scratch: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_sourcefix_multi_all`
- Iter005 report target: `development/spinup_surrogate/iterations/iter005.md`
- Iter005 script root: `development/spinup_surrogate/slurm/iter005/`
- Iter005 summary root: `development/spinup_surrogate/summaries/iter005/`

## Files Modified in Repo (latest cycle)

- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter003.md`
- `development/spinup_surrogate/iterations/iter004.md`
- `model_ELM/surrogate_NN_Spinup.py`
- `train_surrogate_spinup.py`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Failure Debug Bundle Reference (required when latest iteration status is `failed`)

See `development/spinup_surrogate/iterations/iter004.md` sections:

- `Execution Log`
- `Source-fix retry evidence`
- `Fail-Fast and Promotion Rules`
