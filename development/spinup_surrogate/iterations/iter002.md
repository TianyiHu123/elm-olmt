# iter002 - Multicase Feature Attribution (Plan Locked)

## Status

- Iteration ID: `iter002`
- Iteration status: `failed`
- Round budget mode: `1 round` (iter002 only)
- Phase: `Round C fail-fast closeout complete`
- Retry budget status: one retry consumed (`55950336`), still blocked
- Execution approval: approved for this round
- Resource policy mode: explicit
  - `#SBATCH --mem=42GB`
  - `#SBATCH --time=00:05:00`

## Setup Bootstrap (This Session)

Loaded:

- `development/spinup_surrogate/iteration_loop.md` (controlling loop program)
- `development/spinup_surrogate/handoff/CURRENT.md`
- Last 3 iteration reports (all available): `development/spinup_surrogate/iterations/iter001.md`

### Current Objective

Evaluate multicase (`by_member`) NN behavior to test whether surface and forcing-derived climatology features become informative with case diversity.

### Best Evidence So Far

From iter001 single-case (`ABBY_ppe6_I20TRCNPRDCTCBC`, 100 seeds):

- `tuned_nn`/`no_clim`/`reduced_clim` tied at top (`TOTSOMC` median `r2_val=0.6383`, `rmse_ratio=0.9202`)
- `baseline` weaker median fit (`r2_val=0.6056`) but lower warning fraction (`0.30` vs `0.41`)
- Diagnostics showed only parameter features retained, motivating multicase expansion

### Open Risks

- Potential instability/overfit increase in multicase runs.
- 9-case workload has materially higher memory pressure than iter001 single-case baseline.
- If any variant blocks after one retry, fail-fast policy terminates iter002 as failed.

### iter002 Plan (Locked)

- Keep split mode `by_member`, train fraction `0.8`, targets `TOTSOMC,TOTSOMN`.
- Use 9-case multisite list: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL.
- Run seeds `10001-10030` (30 seeds).
- NN attribution variant matrix:
  - `multi_all` -> `feature_set=all`
  - `multi_params_surface` -> `feature_set=params_surface`
  - `multi_params_clim` -> `feature_set=params_clim`
  - `multi_params_only` -> `feature_set=params_only`

## Next Iteration ID and Scaffold Targets

Confirmed next iteration ID: `iter002`

Scaffold targets:

- Iteration report: `development/spinup_surrogate/iterations/iter002.md`
- Canonical Slurm root: `development/spinup_surrogate/slurm/iter002/`
- Canonical Slurm script: `development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm`
- Summary output root (repo): `development/spinup_surrogate/summaries/iter002/`
- Scratch outputs: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`

## Fixed Controls (Round-A Lock)

- Cases (`--case`):
  - `ABBY_ppe6_I20TRCNPRDCTCBC`
  - `JERC_ppe6_I20TRCNPRDCTCBC`
  - `OSBS_ppe6_I20TRCNPRDCTCBC`
  - `SOAP_ppe6_I20TRCNPRDCTCBC`
  - `RMNP_ppe6_I20TRCNPRDCTCBC`
  - `TALL_ppe6_I20TRCNPRDCTCBC`
  - `TEAK_ppe6_I20TRCNPRDCTCBC`
  - `WREF_ppe6_I20TRCNPRDCTCBC`
  - `YELL_ppe6_I20TRCNPRDCTCBC`
- Spinup cases (`--spinup-case`): same 9-case list/order as `--case`
- Split mode: `by_member`
- Train fraction: `0.8`
- Targets: `TOTSOMC,TOTSOMN`
- Seeds: `10001-10030` via Slurm array `1-30` (`seed=10000+SLURM_ARRAY_TASK_ID`)
- Variants: `multi_all|multi_params_surface|multi_params_clim|multi_params_only`
- Model class: NN only
- Diagnostics: variance filter + corr filter + permutation importance enabled

## Required Files/Paths Validation (Setup Phase)

Validated present:

- `development/spinup_surrogate/iteration_loop.md`
- `development/spinup_surrogate/handoff/CURRENT.md`
- `development/spinup_surrogate/iterations/iter001.md`
- `train_surrogate_spinup.py`
- `development/spinup_surrogate/slurm/iter002/` (created in this session)
- `development/spinup_surrogate/summaries/iter002/` (created in this session)
- All required multicase pkl files exist for the 9 `ppe6` `I20TRCNPRDCTCBC` cases.

## Fail-Fast and Provenance Requirements (Locked)

Fail-fast:

- If any variant is blocked after one retry, mark iter002 `failed`, stop remaining variants, and produce debug handoff.

Provenance logging required before/at submission for each variant:

- Variant name
- Canonical script path and checksum
- Submitted script path and checksum
- Source commit hash
- Slurm `job_id`, state transitions, and diagnostics

### Submission Log Template (Round B)

| variant | canonical_script | canonical_sha256 | submitted_script | submitted_sha256 | commit_hash | job_id | state | notes |
|---|---|---|---|---|---|---|---|---|
| multi_all | /pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_all/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | 461ece375094f8f738c4d1487272715fd7d6975a | 55918399 | mixed (5 completed, 25 timeout) | array terminal; see Round B diagnostics |
| multi_params_surface | /pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_params_surface/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | 461ece375094f8f738c4d1487272715fd7d6975a | 55919047 | mixed (4 completed, 26 timeout) | array terminal; see Round B diagnostics |
| multi_params_clim | /pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_params_clim/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | 461ece375094f8f738c4d1487272715fd7d6975a | 55919049 | mixed (4 completed, 26 timeout) | array terminal; see Round B diagnostics |
| multi_params_only | /pscratch/sd/t/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_params_only/case.train_surrogate_spinup_iter2_multicase.slurm | 61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4 | 461ece375094f8f738c4d1487272715fd7d6975a | 55919050 | mixed (4 completed, 26 timeout) | array terminal; see Round B diagnostics |

## Round B Execution Log

- Status: arrays complete with widespread timeout failures; fail-fast closeout executed
- Submission mode: parallel across variants (current default policy)
- Retry policy: max one retry for blocked variant
- `multi_all` submitted as array job `55918399` (`1-30`), terminal mix: `5 COMPLETED`, `25 TIMEOUT`.
- `multi_params_surface` submitted as array job `55919047` (`1-30`), terminal mix: `4 COMPLETED`, `26 TIMEOUT`.
- `multi_params_clim` submitted as array job `55919049` (`1-30`), terminal mix: `4 COMPLETED`, `26 TIMEOUT`.
- `multi_params_only` submitted as array job `55919050` (`1-30`), terminal mix: `4 COMPLETED`, `26 TIMEOUT`.
- Parallel queue monitor reached terminal state for all arrays (`ALL_DONE` marker observed), with final `sacct` diagnostics captured.

### Round B Terminal Diagnostics Snapshot

- `squeue` now empty for job IDs `55918399,55919047,55919049,55919050`.
- Representative failure pattern from `sacct`:
  - task state `TIMEOUT`
  - `.batch` step state `CANCELLED` with exit code `0:15`
  - many timed-out tasks near walltime limit (`~00:05:xx`)
- This pattern indicates dominant walltime pressure under current explicit `#SBATCH --time=00:05:00`.

## Round C Fail-Fast Handling (Executed)

- Trigger condition: every variant array produced substantial `TIMEOUT` task failures under the fixed walltime policy.
- Retry allowance check: the round contract locked explicit `#SBATCH --time=00:05:00`; no resource-adaptive retry was executed in this round scope.
- Blocked decision: mark iter002 blocked/failed due walltime-driven array instability under locked resources.
- Active-job cancellation check: no active/pending jobs remained at fail-fast time (`squeue` empty), so no `scancel` action was required.
- Aggregation/comparison and winner selection were skipped per fail-fast policy.

### Failure Debug Bundle

- Blocked variant (representative): `multi_all` (`job_id=55918399`)
- Affected variants: `multi_all`, `multi_params_surface`, `multi_params_clim`, `multi_params_only`
- Canonical script: `development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm`
- Canonical checksum: `61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4`
- Source commit hash: `0713e8e73aa7e415adc20c1f97c0a71e0b793c3e`
- Final per-array outcomes:
  - `multi_all` (`55918399`): `5 COMPLETED`, `25 TIMEOUT`
  - `multi_params_surface` (`55919047`): `4 COMPLETED`, `26 TIMEOUT`
  - `multi_params_clim` (`55919049`): `4 COMPLETED`, `26 TIMEOUT`
  - `multi_params_only` (`55919050`): `4 COMPLETED`, `26 TIMEOUT`
- Key diagnostics snippets:
  - `squeue -j 55918399,55919047,55919049,55919050` at closeout returned header-only (no active jobs).
  - `sacct` representative rows:
    - `55919047_4|TIMEOUT|0:0|00:05:31`
    - `55919049_3|TIMEOUT|0:0|00:05:25`
    - `55919050_3|TIMEOUT|0:0|00:05:31`
    - paired `.batch` steps commonly recorded `CANCELLED` with exit code `0:15`.
- Partial stats artifacts written before timeout:
  - `multi_all`: `6` stats JSON files
  - `multi_params_surface`: `4` stats JSON files
  - `multi_params_clim`: `4` stats JSON files
  - `multi_params_only`: `4` stats JSON files
- Next debug hypothesis:
  - Dominant bottleneck is walltime (`00:05:00`) for multicase seed workload.
  - Next unblock attempt should raise walltime conservatively (for example `00:08:00` to `00:10:00`) while keeping memory at `42GB`, then re-run a pilot subset before full matrix retry.

## Prepared Retry Scaffold (Reference)

The following commands were prepared for debug retry. Pilot path was executed (see retry log below); full-matrix retry was not launched.

Canonical script:

- `development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm`

Pilot retry command used:

```bash
SCR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_all"
cd "$SCR"
VARIANT=multi_all sbatch --time=00:15:00 --mem=42GB --array=1-5 case.train_surrogate_spinup_iter2_multicase.slurm
```

Full-matrix retry command (not executed due pilot timeout):

```bash
for VAR in multi_all multi_params_surface multi_params_clim multi_params_only; do
  SCR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_${VAR}"
  (cd "$SCR" && VARIANT="$VAR" sbatch --time=00:15:00 --mem=42GB --array=1-30 case.train_surrogate_spinup_iter2_multicase.slurm)
done
```

## Retry Execution Log (Post-fail-fast Debug Unblock)

- Decision applied: default retry approved with walltime override to `00:15:00` (memory kept at `42GB`).
- Retry mode: pilot-first.
- Pilot submission:
  - variant: `multi_all`
  - submit script: `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_multi_all/case.train_surrogate_spinup_iter2_multicase.slurm`
  - checksum status: canonical/submitted match (`61c7906c3b4404e1ab75f0b4d3d18031e66293fe0448cd37c9165ad6ce07e4d4`)
  - source commit: `0713e8e73aa7e415adc20c1f97c0a71e0b793c3e`
  - `sbatch` overrides: `--time=00:15:00 --mem=42GB --array=1-5`
  - job_id: `55950336`
  - terminal outcome: `1 COMPLETED`, `1 TIMEOUT`, remaining pending tasks cancelled by fail-fast (`55950336_[5] CANCELLED`)
- Representative retry failure rows:
  - `55950336_2|TIMEOUT|0:0|00:15:15`
  - `55950336_2.batch|CANCELLED|0:15|00:15:20`
- Fail-fast action after retry failure:
  - cancelled remaining retry tasks (`scancel 55950336`)
  - no further retry launched (one-retry budget exhausted)
  - iteration remains `failed` and blocked pending new user decision
