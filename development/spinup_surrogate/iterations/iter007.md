# iter007 - Fixed-Feature MLP Hyperparameter Tuning

## Status

- Iteration ID: `iter007`
- Run slug: `spinup_surrogate_iter007_<variant>`
- Status: `completed`
- Phase: `selection and closeout complete`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-20T23:13:09Z`
- Closed: `2026-07-21T03:08:49Z`

## Runtime Contract

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One locked 8-variant, five-seed matrix (40 tasks). Stop after terminal accounting; stop for any application/code/configuration failure, or after the single permitted scheduler/resource retry. |
| HPC confirmed | Yes: `wentletrap.hpc.arizona.edu` (Puma login host), checked 2026-07-20. |
| Submission/monitoring authority | User approved preparation, Slurm submission, monitoring, and one retry for a scheduler/resource failure within this contract. |
| Resource policy and caps | Puma `standard`, account `chopinsong`, one node/task, `--cpus-per-task=10` (50 GB implied), `--time=00:30:00`, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-threaded BLAS/OpenMP. Do not set `--mem` or `--mem-per-cpu`. |
| Closeout commit authority | Approved: at most one closeout commit after all closeout artifacts are complete. |

The approval request named `development/hpc/puma.md`, the 40-task finite matrix, the resource
profile, the one-retry limit, and the requirement for fresh authorization after an application or
code/configuration failure. The user replied `approved` on 2026-07-20.

### Retry Contract (2026-07-20)

Following the shared ArviZ cache race, the user explicitly authorized the two-leaf retry scope:
`s24_relu_adam_a50_lr5e4` seed `10005` and `d16_16_relu_adam_a50_lr5e4` seed `10002` only. The
active host was rechecked as `wentletrap.hpc.arizona.edu` and the selected profile remains
`development/hpc/puma.md`. The retry uses the canonical per-array-task `XDG_CACHE_HOME` isolation
without changing the matrix, model controls, account, partition, CPU count, or walltime. The user
authorized preparation, submission, continuous monitoring, successful-path aggregation,
selection, closeout, and amendment of the existing iter007 closeout commit. Each retried leaf may
receive at most one additional attempt only after a scheduler/resource interruption; any
application/code/configuration failure stops for fresh authorization.

### Aggregation-Fix Authority (2026-07-21)

The user authorized the exact requested aggregation-only fix: change the one incorrect
`d16_08_tanh_adam_a50_lr5e4` directory suffix to `d16_08_tanh_adam_a50_lr1e3`, rerun the tracked
aggregation script on Puma `standard` with 10 CPUs and a 30-minute cap, monitor it to terminal
accounting, perform the already-defined selection and closeout if successful, and amend the
existing iter007 closeout commit. No training leaf, matrix control, or resource profile may change.

## Context and Objective

- Prior baseline and evidence: iter006 `all_control` used the best-performing 45-feature set
  (`TOTSOMC`/`TOTSOMN` median `r2_val=0.5892`) and no reduced set passed its gates.
- Hypothesis: with inputs fixed, modest MLP architecture and regularization changes may improve
  validation performance without increasing tail risk or overfitting warnings.
- Objective: select the best eligible fixed-hyperparameter MLP configuration against the external
  iter006 `all_control` baseline.

## Fixed Controls and Variant Matrix

- Cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL; all `ppe6_I20TRCNPRDCTCBC`
- Split mode and train fraction: `by_member`, `0.8`
- Targets: `TOTSOMC,TOTSOMN`
- Seed range: `10001-10005` through a Slurm array `1-5`
- Features: the exact iter006 `all_control` 45-feature list; explicit-subset enforcement enabled;
  variance and correlation filters disabled.
- Model/output controls: NN, fixed MLP controls, `cv_folds=3` retained but unused for fixed MLP
  fits, permutation repeats `8`, stats-only output.

| Variant | Fixed MLP settings | Expected output path |
| --- | --- | --- |
| `s08_tanh_adam_a10_lr1e3` | `(8,)`, `tanh`, `adam`, alpha `10`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_s08_tanh_adam_a10_lr1e3/` |
| `s16_tanh_adam_a50_lr1e3` | `(16,)`, `tanh`, `adam`, alpha `50`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_s16_tanh_adam_a50_lr1e3/` |
| `s24_relu_adam_a50_lr5e4` | `(24,)`, `relu`, `adam`, alpha `50`, LR `5e-4` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_s24_relu_adam_a50_lr5e4/` |
| `s32_tanh_lbfgs_a10_lr1e3` | `(32,)`, `tanh`, `lbfgs`, alpha `10`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_s32_tanh_lbfgs_a10_lr1e3/` |
| `d08_08_tanh_adam_a10_lr1e3` | `(8,8)`, `tanh`, `adam`, alpha `10`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_d08_08_tanh_adam_a10_lr1e3/` |
| `d16_08_tanh_adam_a50_lr1e3` | `(16,8)`, `tanh`, `adam`, alpha `50`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_d16_08_tanh_adam_a50_lr1e3/` |
| `d16_16_relu_adam_a50_lr5e4` | `(16,16)`, `relu`, `adam`, alpha `50`, LR `5e-4` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_d16_16_relu_adam_a50_lr5e4/` |
| `d32_16_tanh_adam_a100_lr1e3` | `(32,16)`, `tanh`, `adam`, alpha `100`, LR `1e-3` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter007_d32_16_tanh_adam_a100_lr1e3/` |

`learning_rate_init` is recorded for every candidate; scikit-learn's `lbfgs` solver does not use
it, so it is not an `lbfgs` tuning dimension.

The frozen explicit subset is:

`parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp`

## Decision and Retry Rules

- Required seeds and eligible variant states: all five seeds must complete and produce readable
  stats JSONs for both targets. No partially completed variant is eligible.
- Target-combination and ranking rule: first apply every gate independently to `TOTSOMC` and
  `TOTSOMN`; then rank passers by mean of their two median `r2_val` values, lower mean median
  `rmse_ratio`, then fewer hidden units/layers.
- Acceptance gates against iter006 `all_control`: each target's median `r2_val` must be no more
  than `0.01` lower; minimum `r2_val` no more than `0.02` lower; `r2_val` IQR may not exceed the
  baseline IQR by more than `0.02`; median `rmse_ratio` may not exceed the baseline by more than
  `0.02`; no overfit warnings. Baseline medians are 0.5892 (`r2_val`), 1.0000 (`TOTSOMC`
  `rmse_ratio`) and 1.0008 (`TOTSOMN` `rmse_ratio`).
- Scientific-rejection rule: a complete variant that fails a gate is recorded as `rejected` and
  excluded from ranking; independent variants continue.
- Retryable failure classes, maximum retries, and fail-fast behavior: the fresh 2026-07-20
  contract authorizes one cache-isolated rerun for each of the two listed failed leaves. After
  that rerun, permit at most one further manual retry per leaf only for a scheduler/resource
  interruption within the stated resource cap. An application/code/configuration failure stops
  iter007 for fresh user authorization; no automatic code change or retry. If an allowed retry
  fails, mark the iteration blocked and cancel remaining active work.
- Changes that require fresh user authorization: any resource increase, change to the fixed
  matrix/features/scientific controls, code/configuration change after a failure, new round, or
  any additional submission beyond this matrix and its single permitted retry.

## Provenance and Job Ledger

Initial submission provenance is retained below. Retry provenance is recorded in
`development/spinup_surrogate/iterations/iter007_retry_source_manifest.txt` before submission.
The retry script sets a unique `XDG_CACHE_HOME` under
`UQ_output/.runtime_cache/iter007/<array-job>_<array-task>` before importing ArviZ. The canonical
post-success aggregation script is
`development/spinup_surrogate/slurm/iter007/aggregate_iter007_mlp_tuning.slurm`.

Exact submission command template, once for each locked variant:

```bash
/usr/bin/sbatch --export=ALL,VARIANT=<locked-variant>,N_JOBS=4,PRE_DISPATCH=n_jobs \
  development/spinup_surrogate/slurm/iter007/case.train_surrogate_spinup_iter007_mlp_tuning.slurm
```

| Variant | Canonical script and SHA-256 | Submitted script and SHA-256 | Commit | Dirty diff/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `s08_tanh_adam_a10_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346006` | COMPLETED (5/5) | none |
| `s16_tanh_adam_a50_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346007` | COMPLETED (5/5) | none |
| `s24_relu_adam_a50_lr5e4` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346008` | FAILED (4/5) | `23346008_5` exit 1: ArviZ cache race |
| `s32_tanh_lbfgs_a10_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346009` | COMPLETED (5/5) | none |
| `d08_08_tanh_adam_a10_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346010` | COMPLETED (5/5) | none |
| `d16_08_tanh_adam_a50_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346011` | COMPLETED (5/5) | none |
| `d16_16_relu_adam_a50_lr5e4` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346012` | FAILED (4/5) | `23346012_2` exit 1: ArviZ cache race |
| `d32_16_tanh_adam_a100_lr1e3` | canonical / `bcdeaa12...b9baa8` | same canonical path / `bcdeaa12...b9baa8` | `b4db7a7` | `iter007_source_manifest.txt` / `386fcdd9...d45d8e4` | `23346013` | COMPLETED (5/5) | none |

| Retry leaf | Canonical retry script and SHA-256 | Commit | Retry source manifest | Job ID | State | Retry policy |
| --- | --- | --- | --- | --- | --- |
| `s24_relu_adam_a50_lr5e4` seed `10005` (array `5`) | `case.train_surrogate_spinup_iter007_mlp_tuning.slurm` / `904ce98e...8c6a` | `7cb12968...5f2c` | `iter007_retry_source_manifest.txt` / tracked diff `e549c9d7...d65a` | `23346857_5` | COMPLETED, exit `0:0`, `00:02:13`, MaxRSS `52427076K` | cache isolation confirmed; further retry unused |
| `d16_16_relu_adam_a50_lr5e4` seed `10002` (array `2`) | `case.train_surrogate_spinup_iter007_mlp_tuning.slurm` / `904ce98e...8c6a` | `7cb12968...5f2c` | `iter007_retry_source_manifest.txt` / tracked diff `e549c9d7...d65a` | `23346858_2` | COMPLETED, exit `0:0`, `00:02:04`, MaxRSS `52427136K` | cache isolation confirmed; further retry unused |

Post-success aggregation submission: the first `sbatch` invocation returned no job ID and created
no queue, accounting, log, or summary artifact while Slurm accounting was transiently unavailable;
it is recorded as an unconfirmed non-submission, not a job retry. Confirmed aggregation job
`23346866` was then submitted with `sbatch --parsable` using
`aggregate_iter007_mlp_tuning.slurm` (`SHA-256=475ecbed...ba89`) under the same authorized Puma
standard/10-CPU/30-minute resource profile.

Aggregation terminal diagnostic: job `23346866` received the expected `billing=10,cpu=10,mem=50G`
allocation but failed with exit `2:0` after `00:00:15` (MaxRSS `39700K`). It successfully wrote
summary and stability JSON files for the first five variants, then stopped because the canonical
aggregation script incorrectly formed the `d16_08_tanh_adam_a50_lr1e3` stats directory as
`d16_08_tanh_adam_a50_lr5e4`. This is a script/configuration error, not a scheduler or resource
failure. The three remaining variants were not aggregated, and no automatic rerun is authorized.
Fresh user authorization on 2026-07-21 now permits only the documented one-suffix correction and
aggregation rerun. Retry provenance is frozen in
`development/spinup_surrogate/iterations/iter007_aggregation_fix_manifest.txt`: corrected script
SHA-256 `2340dc95...db42`, source head `7cb12968...5f2c`, and tracked-diff SHA-256
`97c4f956...cac4`. Corrected aggregation rerun job `23346902` was submitted with
`sbatch --parsable` and completed successfully with exit `0:0` after `00:00:15` (MaxRSS `71596K`).

## Execution and Diagnostics

- Exact submission commands: the locked `/usr/bin/sbatch --export=ALL,VARIANT=...` template above;
  all eight variants were submitted together on 2026-07-20 as jobs `23346006-23346013`.
- Queue/accounting evidence: all 40 leaves reached terminal state. `sacct` reported 38
  `COMPLETED` leaves and two `FAILED` leaves (`23346008_5`, `23346012_2`), both exit `1:0`.
- Resource diagnostics: completed leaves elapsed `00:13:38-00:20:03`; failed leaves elapsed
  `00:13:15` and `00:12:44`. The immediate terminal accounting query reported `billing=1+` but
  did not yet expose MaxRSS; job logs confirm `SLURM_CPUS_PER_TASK=10` for the submitted shape.
- Failure or rejection evidence: both failures occurred before training at the same ArviZ cache
  update: `FileNotFoundError` replacing
  `/home/u32/tianyihu/.cache/arviz/daily_warning.tmp` with `daily_warning`. Concurrent startup
  also logged `micromamba` cache-lock contention at `/home/u32/tianyihu/.cache/mamba/proc`.
  This is an application/environment shared-cache race, not a resource or scheduler failure.
- Retry submission: array index `5` for `s24_relu_adam_a50_lr5e4` is job `23346857_5`; array
  index `2` for `d16_16_relu_adam_a50_lr5e4` is job `23346858_2`. The primary agent is actively
  monitoring both jobs through terminal accounting. Any allowed scheduler/resource retry will be
  appended here before aggregation.
- Retry terminal evidence: both leaves completed successfully. Their logs record unique cache
  paths, respectively `.../.runtime_cache/iter007/23346857_5` and
  `.../.runtime_cache/iter007/23346858_2`, with `RUN_END` exit `0`. The five-seed artifact check
  now passes for all eight variants (40 readable stats JSON files total).
- Aggregation terminal evidence: corrected job `23346902` completed with exit `0:0`, wrote all
  eight compact summaries and all eight feature-stability reports, and used the expected
  `billing=10,cpu=10,mem=50G` allocation.

## Monitoring Interruption Review

- Event: After submitting jobs `23346006-23346013`, the primary agent returned a terminal
  user-facing response instead of retaining an active monitoring loop through terminal accounting.
- Impact: terminal-state review was delayed until prompted. It later found the two application
  failures above. No retry, aggregation, code/configuration change, or scientific decision was
  performed while the failure state was unobserved.
- Root cause: the approved runtime contract authorized monitoring, but the operational workflow
  did not explicitly require the primary agent to remain active after submission until a
  contract-defined stop condition. The optional unattended-monitoring wording was interpreted as
  permission to end the active turn.
- Corrective procedure: `WORKFLOW.md` now requires bounded concurrent monitoring through terminal
  accounting, prohibits a terminal handoff while jobs remain active, and requires a forced
  interruption to be logged and resumed from `CURRENT.md` with `squeue`/`sacct`.

## Results and Decision

| Variant | Eligible | Key metrics | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `s08_tanh_adam_a10_lr1e3` | yes | median r2 `0.5892/0.5892`, min `0.4922/0.4930`, IQR `0.0745/0.0746`, median rmse ratio `1.0000/1.0008`, warnings `0/0` | pass | exactly matches all_control and every target gate |
| `s16_tanh_adam_a50_lr1e3` | no | median r2 `0.4082/0.4080`, min `0.3109/0.3116` | reject | median and minimum r2 gates fail for both targets |
| `s24_relu_adam_a50_lr5e4` | no | median r2 `0.3326/0.3341`, min `0.2660/0.2673` | reject | median and minimum r2 gates fail for both targets |
| `s32_tanh_lbfgs_a10_lr1e3` | no | median r2 `0.9043/0.9045`, median rmse ratio `1.2244/1.2176`, warnings `0.4/0.4` | reject | both rmse-ratio caps and no-warning gate fail |
| `d08_08_tanh_adam_a10_lr1e3` | no | median r2 `0.5588/0.5586`, min `0.4051/0.4057` | reject | median and minimum r2 gates fail for both targets |
| `d16_08_tanh_adam_a50_lr1e3` | no | median r2 `0.2666/0.2652`, min `0.2201/0.2210` | reject | median and minimum r2 gates fail for both targets |
| `d16_16_relu_adam_a50_lr5e4` | no | median r2 `0.2016/0.2030`, min `0.1108/0.1121` | reject | median and minimum r2 gates fail for both targets |
| `d32_16_tanh_adam_a100_lr1e3` | no | median r2 `0.1785/0.1795`, min `0.1080/0.1084` | reject | median and minimum r2 gates fail for both targets |

- Selected fixed MLP: `s08_tanh_adam_a10_lr1e3`. It is the only eligible configuration and
  numerically reproduces the iter006 `all_control` baseline (mean median r2 `0.5892` across the
  two targets). The eight stability reports preserve the frozen 45-feature evidence; for the
  selected variant, cross-target strong top-10 features include `FSDS_clim_mean`, `PCT_SAND`,
  `PRECTmms_clim_mean`, `RH_clim_seasonal_amp`, `parm_6`, `parm_9`, `parm_10`, `parm_12`, and
  `parm_13`.
- Next action: retain `s08_tanh_adam_a10_lr1e3` as the iter007 result and start any new iteration
  only under a new runtime contract.

## Closeout Checklist

- [x] Iteration report scaffolded
- [x] Fixed MLP controls and canonical script created
- [x] Runtime contract recorded
- [x] Matrix submitted and monitored to terminal accounting
- [x] Retry leaves submitted and monitored to terminal accounting
- [x] Summary/stability aggregation completed (corrected job `23346902`)
- [x] `registry.csv` updated to completed status
- [x] `handoff/CURRENT.md` updated at final status
- [x] Existing iter007 closeout commit amended after finalization
