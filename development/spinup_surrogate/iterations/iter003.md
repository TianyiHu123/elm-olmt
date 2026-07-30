# iter003 - Efficiency-First Parallelism Tuning

## Status

- Iteration ID: `iter003`
- Iteration status: `failed`
- Round budget mode: `1 round` (iter003 only)
- Phase: `Round C fail-fast closeout complete; full matrix prohibited`
- Execution approval: approved for this round
- HPC confirmed: yes
- Resource policy mode: explicit
  - `#SBATCH --mem=42GB`
  - `#SBATCH --time=00:20:00`
  - initial pilot `#SBATCH --cpus-per-task=4`, `N_JOBS=4`
  - one allowed retry `#SBATCH --cpus-per-task=8`, `N_JOBS=8`
  - `--mem=42GB` dominated both allocations: Slurm reported `MinCPUsNode=23` and `AllocCPUS=24`

## Setup Bootstrap

Loaded:

- `development/spinup_surrogate/iteration_loop.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter001.md`

`iter002` is treated as closed/failed. No iter002 winner is eligible for promotion.

## Objective and Locked Strategy

Improve CPU efficiency and reduce timeout risk before another broad multicase sweep.

Primary optimization lever tested:

- Tune `GridSearchCV` parallelism from the iter002 profile to four workers, then use the one allowed retry at eight workers.
- Keep BLAS/OpenMP libraries at one thread per worker to avoid nested oversubscription.
- Add wall-clock, runtime configuration, provenance, and `/usr/bin/time -v` instrumentation.

The iter002 retry evidence motivating this profile was:

- `n_jobs=8` / 42 GB: one representative task completed in `00:13:53` at `38.6 GB` RSS.
- A sibling task timed out at `00:15:15` under the same resource policy.

## Fixed Scientific Controls

- Cases and spinup cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL, all `ppe6_I20TRCNPRDCTCBC`
- Split mode: `by_member`
- Train fraction: `0.8`
- Targets: `TOTSOMC,TOTSOMN`
- Model class: NN
- Pilot variant: `multi_all` (`feature_set=all`)
- Pilot seeds: `10001-10005` via Slurm array `1-5`
- Full seeds if promoted: `10001-10030` via Slurm array `1-30`
- Variance filter: enabled, threshold `1.0e-12`
- Correlation filter: enabled, threshold `0.98`
- Permutation repeats: `8`
- Quick grid: enabled
- Stats-only output: enabled

## Pilot Gates

The pilot must pass both gates before the full iter003 matrix is submitted.

### Runtime gate

- All pilot tasks must reach `COMPLETED`.
- No `TIMEOUT`, `FAILED`, or blocked task after the allowed retry policy.
- Walltime request/target: `00:20:00`.
- Per-task elapsed time must be at or below `00:20:00`.
- Capture `sacct` and `seff` diagnostics, including elapsed time, MaxRSS, CPU efficiency, and memory efficiency.

### Quality gate

Compare pilot medians for both `TOTSOMC` and `TOTSOMN` against the iter001 `tuned_nn` baseline:

| target | baseline median r2_val | baseline median rmse_ratio | allowed r2_val drop | allowed rmse_ratio increase |
|---|---:|---:|---:|---:|
| TOTSOMC | 0.6383104919 | 0.9202453463 | 0.01 | 0.02 |
| TOTSOMN | 0.6374293334 | 0.9202145776 | 0.01 | 0.02 |

Therefore the pilot thresholds are:

- `TOTSOMC`: median `r2_val >= 0.6283104919`, median `rmse_ratio <= 0.9402453463`
- `TOTSOMN`: median `r2_val >= 0.6274293334`, median `rmse_ratio <= 0.9402145776`

## Artifact Paths

- Canonical Slurm script: `development/spinup_surrogate/slurm/iter003/case.train_surrogate_spinup_iter3_multicase.slurm`
- Pilot scratch root: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_pilot_<VARIANT>`
- Full scratch root: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_<VARIANT>`
- Expected summary root: `development/spinup_surrogate/summaries/iter003/`

## Provenance and Submission Log

Record canonical/submitted checksum, source commit, Slurm job ID, state transitions, and final diagnostics for every submitted variant.

| phase | variant | canonical_script | canonical_sha256 | submitted_script | submitted_sha256 | commit_hash | job_id | state | notes |
|---|---|---|---|---|---|---|---|---|---|
| pilot | multi_all | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter003/case.train_surrogate_spinup_iter3_multicase.slurm` | `f9323c92b2af07c64e19df5b64bac5785bd9ed21a8e3da52a57c4a67d5d43e17` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_pilot_multi_all/case.train_surrogate_spinup_iter3_multicase.slurm` | `f9323c92b2af07c64e19df5b64bac5785bd9ed21a8e3da52a57c4a67d5d43e17` | `5a8ac36f626cb1bb0887dc63082c1347b13d76c8` | `55952433` | `CANCELLED after timeout` | Seed 10002 timed out; seed 10001 completed; remaining tasks fail-fast cancelled |
| pilot-retry | multi_all | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter003/case.train_surrogate_spinup_iter3_multicase.slurm` | `f9323c92b2af07c64e19df5b64bac5785bd9ed21a8e3da52a57c4a67d5d43e17` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter3_retry_multi_all/case.train_surrogate_spinup_iter3_multicase.slurm` | `f9323c92b2af07c64e19df5b64bac5785bd9ed21a8e3da52a57c4a67d5d43e17` | `5a8ac36f626cb1bb0887dc63082c1347b13d76c8` | `55954503` | `TIMEOUT (4/5)` | Seeds 10001,10002,10003,10005 timed out; seed 10004 completed; walltime 00:20:00 |

## Pilot Execution Log

Initial pilot array `55952433` (`1-5`) was submitted with four workers. It was fail-fast cancelled after seed `10002` timed out. A single allowed retry was submitted as array `55954503` (`1-5`) with eight workers.

Initial pilot diagnostics:

- `55952435` / seed `10001`: `COMPLETED`, elapsed `00:18:13`; `seff` CPU efficiency `0.41%`, memory efficiency `99.93%` (`41.97/42.00 GB`).
- `55952436` / seed `10002`: `TIMEOUT`, elapsed `00:20:21`; `seff` CPU efficiency `0.37%`, memory efficiency `99.94%` (`41.97/42.00 GB`).
- `55953039` / seed `10003`: cancelled by fail-fast at `00:13:18`.
- `55953740` / seed `10004`: completed before cancellation, elapsed `00:04:17`.
- `55952433_5`: pending and cancelled by fail-fast.

The initial pilot failed the runtime gate. The one allowed retry also failed the runtime gate, so no quality-gate decision was made and the full matrix was not submitted.

Retry diagnostics:

- `55954505` / seed `10001`: `TIMEOUT`, elapsed `00:20:22`; `seff` CPU efficiency `0.31%`, memory efficiency `99.94%` (`41.97/42.00 GB`).
- `55954506` / seed `10002`: `TIMEOUT`, elapsed `00:20:16`; `seff` CPU efficiency `0.26%`, memory efficiency `99.94%` (`41.97/42.00 GB`).
- `55955160` / seed `10003`: `TIMEOUT`, elapsed `00:20:09`; `seff` CPU efficiency `0.42%`, memory efficiency `86.88%` (`36.49/42.00 GB`).
- `55955325` / seed `10004`: `COMPLETED`, elapsed `00:18:19`; `seff` CPU efficiency `0.42%`, memory efficiency `89.03%` (`37.39/42.00 GB`).
- `55954503_5` / seed `10005`: `TIMEOUT`, elapsed `00:20:22`; `seff` CPU efficiency `0.30%`, memory efficiency `85.77%` (`36.02/42.00 GB`).

The retry produced only partial stats artifacts for seeds `10003` and `10004`. They remain in the scratch output for debugging; no summaries were copied or aggregated because fail-fast requires skipping aggregation after a blocked pilot.

Resource interpretation correction:

- Under NERSC Shared QOS, `42GB` memory requires approximately `23` hyperthread CPUs (`1952 MB` per CPU), rounded by Slurm to `AllocCPUS=24` / `12` physical cores.
- Changing `cpus-per-task` from `4` to `8` therefore changed `n_jobs`, but did not change the memory-determined allocation.
- Both profiles remained near the memory limit and had very low reported CPU efficiency, so the evidence does not support a pure GridSearchCV parallelism fix.

Next debug hypothesis: reduce peak memory and profile/collapse repeated nine-case forcing-data preparation before another pilot. Source-level caching/data-layout changes are now warranted; do not broaden the matrix first.

## Full Matrix Promotion

The pilot did not pass both gates. Do not submit these variants.

- `multi_all`
- `multi_params_surface`
- `multi_params_clim`
- `multi_params_only`

Each full variant uses seeds `10001-10030`, the same four-worker profile, and walltime `00:20:00`.

Iter003 is marked `failed`/blocked. Preserve diagnostics and update the handoff with the source-level memory/I/O debug hypothesis.

## Aggregation and Comparison

On the success path only, aggregate each variant with:

```bash
python summarize_spinup_stats.py \
  --stats-dir <scratch-root>/surrogate_spinup \
  --glob 'surrogate_spinup_stats_seed*.json' \
  --output-json development/spinup_surrogate/summaries/iter003/<variant>_summary.json
```

Compare median `r2_val`, median `r2_gap`, median `rmse_ratio`, warning fraction, tails, and IQR for both targets. Apply the controlling loop's automatic promotion priority.

## Closeout Checklist

- [x] Pilot submitted with canonical/submitted checksum match
- [x] Pilot job states and `seff` diagnostics recorded
- [x] Runtime gate evaluated and failed
- [x] Full matrix withheld under fail-fast policy
- [x] Partial scratch artifacts preserved; aggregation skipped
- [x] `registry.csv` updated
- [x] `handoff/CURRENT.md` updated
