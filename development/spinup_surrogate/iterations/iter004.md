# iter004 - Source-Level Memory and I/O Debugging

## Status

- Iteration ID: `iter004`
- Iteration status: `failed`
- Round budget mode: `1 round` (iter004 only)
- Phase: `Round C fail-fast closeout complete; quality pilot and broad matrix prohibited`
- HPC confirmed: yes
- Execution approval: approved for Slurm submission and monitoring within this round
- Resource policy mode: calibrated
  - Safety caps: maximum `--mem=64GB`, maximum `--time=00:30:00`
  - Initial diagnostic request: `--mem=42GB`, `--time=00:30:00`
  - Initial pilot: one `multi_all` seed, stats-only

## Bootstrap State

Loaded:

- `development/spinup_surrogate/iteration_loop.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `development/spinup_surrogate/iterations/iter003.md`
- `development/spinup_surrogate/iterations/iter002.md`
- `development/spinup_surrogate/iterations/iter001.md`

`iter003` is treated as closed/failed. No iter003 winner is eligible for promotion and no full iter003 matrix was submitted.

## Objective

Reduce peak memory and identify the walltime bottleneck before another multicase sweep. The prior parallelism-only tests failed:

- `n_jobs=4`: one of two observed active seeds timed out at `00:20:21`.
- `n_jobs=8`: four of five retry seeds timed out at `00:20:09-00:20:22`.
- Peak memory reached `41.97/42.00 GB`.
- `seff` CPU efficiency was only `0.26-0.42%`.

The leading hypotheses are repeated forcing-data preparation/I/O and excessive queued or copied arrays during parallel GridSearchCV execution.

## Source Changes Under Test

The working tree now contains source-level diagnostic changes:

1. Added phase timing logs around:
   - per-case preparation
   - design-matrix construction
   - feature selection
   - each target's GridSearchCV fit
   - each target's permutation importance
2. Added `--pre-dispatch` to `train_surrogate_spinup.py` and passed it to `GridSearchCV`.
3. The diagnostic Slurm script uses `N_JOBS=4` and `PRE_DISPATCH=n_jobs` to limit queued fit copies while retaining the scientific setup.
4. Existing one-thread BLAS/OpenMP controls and `/usr/bin/time -v` remain enabled.
5. Tested `_load_forcing_matrix` with one combined xarray graph/load instead of converting each variable independently; this change did not improve the diagnostic result and is not promoted.

No feature, split, target, model-grid, or seed semantics are intentionally changed.

## Fixed Scientific Controls

- Cases and spinup cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL, all `ppe6_I20TRCNPRDCTCBC`
- Split mode: `by_member`
- Train fraction: `0.8`
- Targets: `TOTSOMC,TOTSOMN`
- Model class: NN
- Diagnostic variant: `multi_all` (`feature_set=all`)
- Initial diagnostic seed: `10001` (`--array=1`)
- Later quality pilot, only if diagnostic pilot is runtime-safe: seeds `10001-10005`
- Variance filter: enabled, threshold `1.0e-12`
- Correlation filter: enabled, threshold `0.98`
- Permutation repeats: `8`
- Quick grid: enabled
- Stats-only output: enabled

## Calibrated Resource Procedure

1. Run the one-seed diagnostic pilot at `42GB` and `00:30:00`.
2. Read `sacct`, `seff`, `/usr/bin/time -v`, and phase timing logs.
3. If the pilot completes, select a memory/time default with conservative headroom, staying under `64GB` and `00:30:00`.
4. If it times out or reaches the memory ceiling, stop the round under fail-fast and revise source-level memory handling before another submission.

Because NERSC Shared QOS derives allocated CPU slots partly from memory, the report must record `ReqTRES`, `MinCPUsNode`, `AllocCPUS`, and `SLURM_CPUS_PER_TASK`; `cpus-per-task` alone is not an allocation proxy.

## Pilot Gates

### Diagnostic runtime/resource gate

- The one-seed pilot must complete without timeout or failure.
- Peak memory must show meaningful headroom below the `42GB` request; a near-cap result is a failure for this objective.
- Phase timings must identify the dominant walltime component.
- Record CPU and memory efficiency with `seff`.

### Quality pilot gate

Only after the diagnostic gate passes, run a five-seed `multi_all` pilot and compare to the iter001 `tuned_nn` medians:

| target | baseline median r2_val | baseline median rmse_ratio | minimum r2_val | maximum rmse_ratio |
|---|---:|---:|---:|---:|
| TOTSOMC | 0.6383104919 | 0.9202453463 | 0.6283104919 | 0.9402453463 |
| TOTSOMN | 0.6374293334 | 0.9202145776 | 0.6274293334 | 0.9402145776 |

The quality pilot must also have no timeout and retain the same scientific controls.

## Artifact Paths

- Canonical Slurm script: `development/spinup_surrogate/slurm/iter004/case.train_surrogate_spinup_iter4_memory_debug.slurm`
- Diagnostic scratch root: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_diag_multi_all`
- Expected summary root: `development/spinup_surrogate/summaries/iter004/`
- Source files under test:
  - `model_ELM/surrogate_NN_Spinup.py`
  - `train_surrogate_spinup.py`

## Provenance and Submission Log

Record canonical/submitted checksums, source `HEAD` commit plus dirty-tree state, job IDs, state transitions, `sacct`, `seff`, and timing evidence.

| phase | variant | canonical_script | canonical_sha256 | submitted_script | submitted_sha256 | source_head | tree_state | job_id | state | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| diagnostic pilot | multi_all | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter004/case.train_surrogate_spinup_iter4_memory_debug.slurm` | `9066e7c2d16a2f3ab4234e25b1194210abebbe4f33f5498c5b61d679a2aa41d3` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_diag_multi_all/case.train_surrogate_spinup_iter4_memory_debug.slurm` | `9066e7c2d16a2f3ab4234e25b1194210abebbe4f33f5498c5b61d679a2aa41d3` | `fd1a3e4` | source instrumentation uncommitted | `55957524` | COMPLETED | runtime-safe but diagnostic gate failed: 41.97/42.00 GB; per-case preparation dominated |
| source-fix retry | multi_all | `/pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter004/case.train_surrogate_spinup_iter4_memory_debug.slurm` | `9066e7c2d16a2f3ab4234e25b1194210abebbe4f33f5498c5b61d679a2aa41d3` | `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter4_sourcefix_multi_all/case.train_surrogate_spinup_iter4_memory_debug.slurm` | `9066e7c2d16a2f3ab4234e25b1194210abebbe4f33f5498c5b61d679a2aa41d3` | `fd1a3e4` | source forcing-load optimization uncommitted | `55958511` | COMPLETED | no runtime or memory improvement; source-fix retry closed |

## Execution Log

Initial diagnostic array `55957524` (`1-1`) completed. A source-fix retry was submitted as array `55958511` (`1-1`) after source/script validation and canonical/scratch checksum match. Both pilots are terminal; no quality pilot was authorized.

Initial diagnostic evidence:

- `55957524`: `COMPLETED`, elapsed `00:19:19`; `seff` CPU efficiency `0.36%`, memory efficiency `99.94%` (`41.97/42.00 GB`).
- `/usr/bin/time`: wall `19:04.85`, maximum RSS `37,195,968 KB`.
- Phase timings: case preparation ranged from `53.232s` to `185.908s` per case; design matrix `0.002s`; feature selection `0.279s`; GridSearchCV fits `10.044s` and `1.275s`; permutation importance `0.115s` and `0.113s`.
- The diagnostic runtime completed, but the memory-headroom gate failed and the combined forcing-load optimization was applied before the retry.

Source-fix retry evidence:

- `55958511`: `COMPLETED`, elapsed `00:26:18`; `seff` CPU efficiency `0.26%`, memory efficiency `99.94%` (`41.97/42.00 GB`).
- `/usr/bin/time`: wall `26:06.89`, maximum RSS `37,172,804 KB`.
- Phase timings: case preparation ranged from `52.457s` to `386.331s` per case; design matrix `0.002s`; feature selection `0.159s`; GridSearchCV fits `9.104s` and `1.116s`; permutation importance `0.114s` and `0.113s`.
- The retry was slower than the initial diagnostic (`26:18` versus `19:19`) and retained the memory ceiling. Combined forcing loading is not sufficient; no quality pilot was launched.

## Fail-Fast and Promotion Rules

- If the diagnostic pilot blocks after the allowed retry, mark iter004 `failed` in this report and `registry.csv`, cancel remaining jobs, and update `CURRENT.md`.
- Do not launch any broad matrix in iter004 from a failed diagnostic pilot.
- This diagnostic pilot failed the memory-headroom objective after the allowed source-fix retry; no quality pilot is authorized.
- Full multicase promotion requires a separate runtime-safe decision based on source timings, memory headroom, and the locked quality thresholds.

## Closeout Checklist

- [x] Runtime contract recorded
- [x] Source instrumentation and `pre_dispatch` control added
- [x] Canonical diagnostic script created
- [x] Expected summary root created
- [x] Canonical/submitted checksums recorded
- [x] Initial diagnostic pilot submitted and monitored
- [x] Diagnostic pilot runtime and resource evidence recorded
- [x] Diagnostic memory-headroom gate failed
- [x] Source-fix retry submitted and monitored
- [x] Quality pilot withheld under fail-fast policy
- [x] `registry.csv` updated
- [x] `handoff/CURRENT.md` updated
