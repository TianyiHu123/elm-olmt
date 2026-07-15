# Spinup Surrogate - Current Handoff (iter002 failed, iter003 planned)

## Current Objective

Start `iter003` as an efficiency-first debug iteration to improve CPU efficiency and remove walltime-driven instability before another full multicase sweep.

## Best Variant So Far

From the last successful iteration (`iter001` single-case), `tuned_nn` (tied with `no_clim` and `reduced_clim`) remains the best available baseline.

No winner was selected in `iter002` because fail-fast terminated before aggregation.

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

## What Changed in Latest Iteration

- Closed `iter002` as `failed` with full debug bundle and provenance.
- Recorded failed status in `development/spinup_surrogate/registry.csv`.
- Completed a grilling session and locked `iter003` planning direction:
  - success gate: runtime + quality
  - optimization priority: parallelism tuning first
  - quality tolerance: tight (`r2_val` drop `<=0.01`, `rmse_ratio` increase `<=0.02`)
  - runtime target: no timeout with walltime target `<=00:20:00` in pilot

## Open Risks / Unknowns

- `00:15:00` can still timeout for some seeds; likely heterogeneity by seed/case combination.
- CPU efficiency is currently low; nested or imbalanced parallelism may be wasting cores.
- Need to improve execution efficiency without degrading validation quality versus iter001 baseline.

## Next Iteration Plan (`iter003`)

1. Keep scientific setup comparable (same 9-case list, split mode `by_member`, train fraction `0.8`, targets `TOTSOMC,TOTSOMN`).
2. Implement efficiency-first changes (parallelism tuning + runtime instrumentation) before broad rerun.
3. Run pilot gate first (small seed subset, `multi_all`) with target walltime `<=00:20:00`.
4. Promote to full iter003 matrix only if both pass:
   - runtime gate (no timeout), and
   - quality gate (tight tolerance vs iter001 baseline).
5. If pilot fails, keep iter003 in debug mode and do not launch full matrix.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load iteration reports:
   - `development/spinup_surrogate/iterations/iter002.md`
   - `development/spinup_surrogate/iterations/iter001.md`
3. Review `development/spinup_surrogate/iteration_loop.md`.
4. Scaffold `iter003` artifacts (`iterations/iter003.md`, `slurm/iter003/`) and lock gates from this handoff.
5. Proceed with iter003 pilot-first execution only after standard runtime contract confirmation.

## Ready/Blocked Status for Next Iteration

Ready to start `iter003` planning/execution workflow. `iter002` is closed as failed.

## Required User Decisions Before Execution (if any)

None pending on strategy/gates for iter003 (already locked via grilling).

Standard session run-contract confirmations still apply before any new submissions.

## Artifact Paths

- Failed iteration report: `development/spinup_surrogate/iterations/iter002.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Current handoff: `development/spinup_surrogate/handoff/CURRENT.md`
- Iter002 script root: `development/spinup_surrogate/slurm/iter002/`
- Iter002 scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`
- Planned iter003 report path: `development/spinup_surrogate/iterations/iter003.md`
- Planned iter003 script root: `development/spinup_surrogate/slurm/iter003/`

## Files Modified in Repo (latest cycle)

- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/registry.csv`
- `development/spinup_surrogate/handoff/CURRENT.md`

## Failure Debug Bundle Reference (required when latest iteration status is `failed`)

See `development/spinup_surrogate/iterations/iter002.md` sections:

- `Round C Fail-Fast Handling (Executed)`
- `Failure Debug Bundle`
- `Retry Execution Log (Post-fail-fast Debug Unblock)`
