Offline Land Model Testbed (OLMT)
Contact:  Dan Ricciuto (ricciutodm@ornl.gov)

Updated 5/12/2026

The purpose of the Offline Land Model Testbed (OLMT) is to simplify the workflows for single site, regional and ensemble offline ELM simulations, which are otherwise cumbersome using only CIME. We have been working on a new version with an improved interface.  The user now can run a simulation using a single python run script that will perform the entire workflow.  This usually involves setting up three cases for biogeochemistry-enabled runs: the ad spinup, final spinup and transient simulations.  It is also possible to add additional cases beginning in later years where we apply treatment effects or otherwise modify forcings.  For example, in the SPRUCE study we have 10 experimental treatments (different levels of temperature and CO2 modifications) that begin in 2015.  For those point simulations, we have a single run script that launches and manages 13 cases. 
 
For each case, the runscript will perform the create_newcase, case setup, and submission.  The case.build will be performed on the first case only, and then the same executable will be used for following cases.  When submitting cases, the correct dependencies will be applied, such that the second case will start running after the first has finished, etc.
 
Users can customize the simulations to run single points, a list of lat/lon coordinates, rectangular regions or global simulations. OLMT assumes surface, land use and domain data already exist (using the defaults for specified compsets and resolution) and will extract points or regions from these data.  The user can also set custom files, for example ultra high-resolution files created from kilocraft.  For single point runs, the PFT and soil information can be set to match observations, for example at AmeriFlux sites.
 
Finally, OLMT also has the capability to perform ensemble simulations.  Users can specify a list of parameters, with allowable ranges for each. Random samples can then be created.  Alternatively, the user can provide their own files with different parameter combinations.  When this ensemble option is enabled, the cases will be set up in the same way as above, but then multiple copies of run directories will be created. We then use another MPI-enabled python script to manage the multiple simulations in parallel.  Users can also specify a list of output variables and time frequency for which to postprocess.  A matrix of output values for all ensemble members is then created at the end of the simulation, which can then be used in Uncertainty quantification applications discussed in the other epics.

Please see the wiki page for instructions and examples.

## Standalone Hybrid Forcing Surrogate

Single-case training lives in [`model_ELM/surrogate_forcing_singlecase.py`](model_ELM/surrogate_forcing_singlecase.py); multi-case training in [`model_ELM/surrogate_forcing_multicase.py`](model_ELM/surrogate_forcing_multicase.py); shared preparation, training, and inference in [`model_ELM/surrogate_NN_Forcing.py`](model_ELM/surrogate_NN_Forcing.py). On the case object, **`train_singlecase_surrogate_with_forcing`** and **`run_surrogate_forcing`** are wired through [`model_ELM/main.py`](model_ELM/main.py) (same pattern as `train_surrogate` / `run_surrogate` in [`model_ELM/surrogate_NN.py`](model_ELM/surrogate_NN.py)).

**Command-line driver** — same idea as [`manage_ensemble.py`](manage_ensemble.py): load one or more `pklfiles/<case>.pkl` files, then call the case method (single case) or the multi-case adapter (merged training).

- **`train_surrogate_forcing.py`** — preferred entry point from the OLMT repository root.

**Backward compatibility:** repo-root **`surrogate_NN_Forcing.py`** is a thin wrapper that forwards to `train_surrogate_forcing.main()`, so existing invocations of `python surrogate_NN_Forcing.py ...` keep working.

**Programmatic use:** after `import model_ELM`, a loaded `ELMcase` instance has `train_singlecase_surrogate_with_forcing(myvars, ...)` and `run_surrogate_forcing(parms, myvars, ...)` (optional full design matrix `X`, or `forcing_engineered` + `spinup` with `parms`). The training method also accepts `split_random_state`, `minimal_output` (stats-only; no models attached to the case), `stats_run_id`, and `reuse_x_memmap_path` with the same semantics as the CLI flags below.

The workflow trains a surrogate for hourly ELM outputs (for example, `GPP`, `SR`) using a hybrid feature set:

- hourly forcing variables (default: `PRECTmms`, `FSDS`, `FLDS`, `TBOT`, `RH`, `WIND`, `PSRF`)
- static ensemble parameters (`self.samples`) broadcast across timesteps
- spinup state features from restart files (`TOTSOMC`, `TOTSOMN` by default), broadcast across timesteps
- engineered forcing-memory and temporal features:
  - temperature rolling means: 24h, 7d, 30d
  - precipitation rolling sums: 24h, 7d, 30d
  - `sin(hour_of_day)`, `cos(hour_of_day)`
  - forcing anomalies defined as `forcing_t - rolling_mean_30day_t`

The CLI is separate from the ensemble workflow manager ([`manage_ensemble.py`](manage_ensemble.py)) but uses the same pickle convention. By default it resolves case pickles from:

`<workdir>/pklfiles/<case>.pkl`

(`--workdir` defaults to the current directory; run from the OLMT root where `pklfiles/` lives.) For multi-case training, pass a comma-separated case list to `--case`.

### Recent updates

- forcing is explicitly converted to no-leap calendar using `convert_calendar('noleap')` and coarsened to hourly with `coarsen(time=2).mean()`
- **Time collocation simplified:** forcing and observation time axes are both kept on the no-leap `cftime` calendar floored to the hour, so collocation is a direct match on overlapping hourly timestamps (the previous `"%Y-%m-%dT%H"` string-key workaround and the forcing `noleap -> standard` round-trip were removed); leap-day observations are excluded, consistent with the model's 365-day calendar
- spinup restart path is resolved using `case.dependcase` and `case.finidat` naming, improving compatibility when restart files are sourced from dependent cases
- spinup variables support aggregated sums through `SPINUP_VAR_SUM` (for example `TOTSOMC`, `TOTSOMN`)
- anomaly features skip selected state/meteorology variables (`FLDS`, `QBOT`, `WIND`, `PSRF`, `RH`)
- `--outputdir` is the exact parent of **`<case-or-run-name>/surrogate_forcing/`** (the default is the current directory); no implicit `UQ_output` component is inserted
- multi-case runs can set `--run-name` to choose a short output folder directly under `--outputdir`, which also controls where the merged `X_forcing_memmap.dat` is saved
- **Train/validation robustness:** `split_mode=random_time_window` draws a random contiguous time window per case (seed with `split_random_state` / `--split-random-state`) so you can study sensitivity to the temporal split
- **Stats-only runs:** `--stats-only` skips plots and `surrogate_forcing_artifacts.pkl` and writes a small JSON metrics file per run (`surrogate_forcing_stats_*.json`), with filenames keyed off SLURM array/job env vars or `--stats-run-id` so array jobs do not overwrite each other
- **Complete diagnostics:** every run writes pooled and per-site train/test R2 and RMSE, R2 gap,
  RMSE ratio, and the documented overfitting warning; full runs also write the same JSON record
- **Held-out importance:** `--permutation-repeats` controls reproducible permutation importance
  for every ordered forcing, parameter, and spinup feature (default: 8), reported as test-R2
  decrease and physical-unit test-RMSE increase
- **Observation unit conversion:** NetCDF observations loaded by [`model_ELM/load_obs_nc.py`](model_ELM/load_obs_nc.py) are converted to daily flux units (`gC/m^2/day`, `gN/m^2/day`, `gP/m^2/day`, or `mm/day`) to match postprocessed surrogate training targets; see [Observation NetCDF units](#observation-netcdf-units) below
- **Reuse of the design matrix:** after one full training run, **`X_forcing_memmap_layout.npz`** is written next to **`X_forcing_memmap.dat`**. Later runs can pass **`--reuse-x-memmap`** to open the memmap read-only and skip met forcing and restart spinup IO; targets are still loaded from the case pickle(s). `--forcing-vars` and `--spinup-vars` must match the original build; multi-case reuse requires the same case list **order** as in the layout file

### Key capabilities

- standalone CLI via **`train_surrogate_forcing.py`** (`--case`, `--vars`, `--workdir`, forcing/spinup options, `--split-random-state`, `--stats-only`, `--stats-run-id`, `--reuse-x-memmap`, and the same flags as before)
- multi-case training by passing a comma-separated case list to `--case`
- split modes for validation:
  - `by_member` — for each case, split across ensemble members inside that case
  - `by_site` — hold out entire site/case labels for validation
  - `by_time_block` — for each case, split across the time dimension inside that case (earlier times train, later times validate)
  - `random_time_window` — for each case, one **random contiguous** block of time indices is used for training; the rest is validation (use `--split-random-state` for reproducibility across SLURM array tasks)
- parallel hyperparameter search with `MLPRegressor + GridSearchCV`
- HPC-oriented controls:
  - `--n-jobs`
  - `--cv-folds`
  - `--quick-grid`
  - `--chunk-size`
  - `--permutation-repeats`
  - `--dtype` (`float32` default)
- memory-aware training:
  - dry-run size/memory estimate
  - disk-backed feature matrix via `numpy.memmap`
  - warnings for potentially aggressive parallel settings
- outputs saved to:
  - `<outputdir>/<case-or-run-name>/surrogate_forcing/`
  - **Full training (default):** `surrogate_forcing_artifacts.pkl`, memmap-backed design matrix `X_forcing_memmap.dat`, companion **`X_forcing_memmap_layout.npz`** (row layout and feature metadata for reuse), and diagnostic plots `*_surrogate_forcing.png`
  - **`--stats-only`:** `surrogate_forcing_stats_<id>.json` only (no pickle, no plots); the run id defaults from `SLURM_ARRAY_JOB_ID` / `SLURM_ARRAY_TASK_ID` when present, else `SLURM_JOB_ID` or process id, optionally suffixed with `_rs<split_random_state>`
- multi-case diagnostics are saved case by case (one plot set per case/site) under the merged training run output folder
- after a **full** (non-`--stats-only`) training run, the case object holds **`surrogate_forcing`**, **`x_scaler_forcing`**, **`y_scaler_forcing`**, and **`forcing_surrogate_training`** metadata for **`run_surrogate_forcing`**; stats-only runs do not populate the trained models on the case object
- batch example: [`examples/slurm/case.submit_surrogate_forcing`](examples/slurm/case.submit_surrogate_forcing) uses `train_surrogate_forcing.py` with an explicit `--outputdir`

### Example commands

Dry-run (recommended first):

```bash
python train_surrogate_forcing.py --case <CASE_NAME> --vars GPP,SR --dry-run
```

Equivalent backward-compatible invocation:

```bash
python surrogate_NN_Forcing.py --case <CASE_NAME> --vars GPP,SR --dry-run
```

Quick test training:

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --quick-grid \
  --split-mode by_time_block \
  --train-fraction 0.8 \
  --n-jobs 8 \
  --cv-folds 3 \
  --dtype float32
```

Multi-case training with a user-defined output folder label:

```bash
python train_surrogate_forcing.py \
  --case <CASE_A>,<CASE_B>,<CASE_C> \
  --vars GPP,SR \
  --split-mode by_site \
  --train-fraction 0.67 \
  --run-name multicase_flux_sites \
  --outputdir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project
```

Full training (example with explicit scratch output root):

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --tair-var TBOT \
  --precip-var PRECTmms \
  --spinup-vars TOTSOMC,TOTSOMN \
  --split-mode by_member \
  --train-fraction 0.8 \
  --n-jobs 16 \
  --cv-folds 5 \
  --dtype float32 \
  --outputdir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project
```

One-site continuous time split example:

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP \
  --split-mode by_time_block \
  --train-fraction 0.8
```

### Random time-window split (robustness to train/val choice)

Use a different contiguous training window each run; fix the RNG for reproducible array jobs:

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --split-mode random_time_window \
  --train-fraction 0.8 \
  --split-random-state 10042
```

### Stats-only jobs (no plots, no surrogate pickle)

Useful when submitting many jobs to sample a distribution of validation metrics:

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --split-mode random_time_window \
  --train-fraction 0.8 \
  --split-random-state 2026 \
  --stats-only
```

Optional explicit label for the stats filename (overrides SLURM-based default):

```bash
python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP \
  --stats-only \
  --stats-run-id my_batch_run_07
```

### Reusing `X_forcing_memmap.dat` (skip forcing and spinup IO)

1. Run **one full** training once (no `--stats-only`, no `--reuse-x-memmap`) so the directory contains **`X_forcing_memmap.dat`** and **`X_forcing_memmap_layout.npz`**.
2. Point **`--reuse-x-memmap`** at that directory (or at the `.dat` file). Use the **same** `--forcing-vars`, `--spinup-vars`, `--vars`, `--dtype`, and case list **order** (multi-case) as the original run. The memmap stores the design matrix **X** only; hourly targets are always read from **`pklfiles/<case>.pkl`** (`case.output`), so the pickle must still match the experiment used to build **X**.

```bash
MEMMAP_DIR="/path/to/output/<CASE_OR_RUN_NAME>/surrogate_forcing"

python train_surrogate_forcing.py \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --spinup-vars TOTSOMC,TOTSOMN \
  --dtype float32 \
  --reuse-x-memmap "${MEMMAP_DIR}" \
  --split-mode random_time_window \
  --train-fraction 0.8 \
  --split-random-state 555 \
  --stats-only
```

**Multi-case:** `--case` must list cases in the **same order** as stored in `case_names` inside the layout file from the original merged training run.

### SLURM array example (stats + random split + memmap reuse)

Assume `MEMMAP_DIR` points at the folder from a prior full train. Each array task gets a unique `--split-random-state` (here tied to the array index) and relies on default stats filenames (`array_<SLURM_ARRAY_JOB_ID>_<SLURM_ARRAY_TASK_ID>_rs<seed>.json` when the seed is set):

```bash
#!/bin/bash
#SBATCH --array=0-99
#SBATCH ...

MEMMAP_DIR="/path/to/output/<CASE_NAME>/surrogate_forcing"
SEED=$((10000 + SLURM_ARRAY_TASK_ID))

python train_surrogate_forcing.py \
  --workdir /path/to/elm-olmt \
  --case <CASE_NAME> \
  --vars GPP,SR \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --spinup-vars TOTSOMC,TOTSOMN \
  --dtype float32 \
  --outputdir /path/to/scratch \
  --reuse-x-memmap "${MEMMAP_DIR}" \
  --split-mode random_time_window \
  --train-fraction 0.8 \
  --split-random-state "${SEED}" \
  --stats-only \
  --quick-grid \
  --n-jobs 8
```

Stats JSON files are written under **`/path/to/scratch/<CASE_NAME>/surrogate_forcing/`** (or under `--run-name` when you use it). Aggregate those JSON files offline to summarize R² distributions.

## Standalone Spinup Surrogate

Standalone spinup-state surrogate training is provided by [`train_surrogate_spinup.py`](train_surrogate_spinup.py) and implemented in [`model_ELM/surrogate_NN_Spinup.py`](model_ELM/surrogate_NN_Spinup.py).

### Final spinup-surrogate models

Iter012 publishes two trusted-source, versioned `spinup-surrogate-v1` artifacts. Both use one
independent `(32,)`, `tanh`, `lbfgs`, alpha-40 `MLPRegressor` per target, separate X/Y
`StandardScaler` objects, estimator seed 42, and a full-data fit over 900 rows from ABBY, JERC,
OSBS, SOAP, RMNP, TALL, TEAK, WREF, and YELL. The full-data diagnostics are not validation
metrics: scientific performance remains the Iter011 100-seed `by_member` evidence.

| Version | Role | Features | Artifact |
| --- | --- | ---: | --- |
| `drop32` | Recommended accuracy-oriented release | 32 | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl` |
| `drop21_corr080` | Compact tradeoff accepted by the user | 21 | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` |

These artifact paths are temporary Puma locations, not permanent or portable release URLs.
When the artifacts move to another HPC system, update the paths and examples in this section to
the new site-specific storage locations. Puma `/xdisk` storage is temporary and unbacked, so keep
any required durable copy separately.

Ordered outputs are `TOTSOMC` in `gC/m^2` and `TOTSOMN` in `gN/m^2`. The trained scalars are,
respectively, `numpy.nansum(totsomc[:])` and the sum of `numpy.nansum` over
`litr1n,litr2n,litr3n,cwdn,soil1n,soil2n,soil3n,soil4n`. Restart component attributes are empty;
the aggregate names and units are provenance-bound to 27 colocated native ELM history records
from the exact same ELM version. See
`development/spinup_surrogate/summaries/iter012/iter012_release_decision.json`.

Both versions accept 14 physical parameters in this exact order:
`k_l1,k_l2,k_l3,k_s1,k_s2,k_s3,k_s4,k_frag,rf_l1s1,rf_l2s2,rf_l3s3,rf_s1s2,rf_s2s3,rf_s3s4`.
Their artifact aliases are `parm_0` through `parm_13`. Inputs also include surface fields
`PCT_SAND,PCT_CLAY,ORGANIC` and compact climatology features engineered from
`PRECTmms,FSDS,TBOT,RH`. The 21-feature version omits `PCT_CLAY` and additional correlated
climatology columns. Exact selected order is mandatory:

```text
drop32:
parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp

drop21_corr080:
parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,FSDS_clim_mean,TBOT_clim_std,RH_clim_seasonal_amp
```

Predict existing members with a trusted artifact:

```bash
python predict_surrogate_spinup.py \
  --workdir /xdisk/chopinsong/tianyihu/elm-olmt \
  --case ABBY_ppe6_I20TRCNPRDCTCBC \
  --artifact /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup \
  --feature-subset parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp \
  --members 1,2
```

For new parameters, `--parameters-json` accepts a JSON **file path only**. A named
`params.json` file for one parameter set has this form (the values below are illustrative and
must be replaced with values inside the artifact's stored `ensemble_pmin/pmax`):

```json
{
  "k_l1": 0.5,
  "k_l2": 0.5,
  "k_l3": 0.5,
  "k_s1": 0.5,
  "k_s2": 0.5,
  "k_s3": 0.5,
  "k_s4": 0.5,
  "k_frag": 0.5,
  "rf_l1s1": 0.5,
  "rf_l2s2": 0.5,
  "rf_l3s3": 0.5,
  "rf_s1s2": 0.5,
  "rf_s2s3": 0.5,
  "rf_s3s4": 0.5
}
```

Run it with:

```bash
python predict_surrogate_spinup.py \
  --workdir /xdisk/chopinsong/tianyihu/elm-olmt \
  --case ABBY_ppe6_I20TRCNPRDCTCBC \
  --artifact /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup \
  --feature-subset parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp \
  --parameters-json params.json \
  --output-json spinup_predictions.json
```

A positional batch file is also supported. Each row must contain exactly 14 values in the
physical order listed above:

```json
[
  [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
  [0.6, 0.4, 0.7, 0.3, 0.6, 0.8, 0.4, 0.5, 0.4, 0.6, 0.5, 0.7, 0.3, 0.6]
]
```

Use the batch with `--parameters-json params_batch.json`. Values outside stored
`ensemble_pmin/pmax` are rejected; values inside those bounds but outside the empirical training
range emit warnings. Missing, duplicate, extra, or misordered parameters/features are rejected
with the required order. Inline JSON is intentionally not accepted.

Artifacts are Python pickles: loading can execute code. Load only trusted artifacts, verify the
colocated manifest SHA-256, and use a compatible Python/scikit-learn environment. The validated
domain is the nine training sites and their parameter bounds; new sites and extrapolation beyond
the observed feature ranges are not established.

The validated future forcing bridge is:

```text
parameters + surface + compact climatology
  -> spinup surrogate -> ordered [TOTSOMC,TOTSOMN]
  -> compose_forcing_surrogate_design_matrix(
       engineered_forcing, parameters, spinup,
       {"n_forcing_cols": ..., "n_params": 14, "n_spinup": 2})
  -> forcing surrogate
```

Iter012 validated only the order, shape, and `float64` design-matrix contract. No forcing
artifact was available, no forcing model was trained, and no real SR/flux prediction was made.

### Key points

- selectable backend with `--model-type`:
  - `nn` (default, `MLPRegressor`)
  - `random_forest` (`RandomForestRegressor`)
- conservative default hyperparameter grids are used for both `nn` and `random_forest` to reduce overfitting risk on small spinup datasets
- split modes `by_member`, `by_site`, and `by_case` now randomize group selection by `--train-fraction`
- set `--split-random-state` to make those randomized splits reproducible
- training prints a warning when potential overfitting is detected from train-vs-validation metric gaps
- feature ablation and diagnostics controls:
  - `--feature-set all|params_only|params_surface|params_clim`
  - `--clim-feature-include <glob1,glob2,...>` to keep a climatology subset
  - `--apply-variance-filter --variance-threshold <v>`
  - `--apply-corr-filter --corr-threshold <r>`
  - permutation importance written in stats JSON via `--permutation-repeats`
- stats JSON now includes:
  - selected input feature list and full feature list
  - `feature_diagnostics` (variance/correlation/filter decisions)
  - per-target `permutation_importance_rmse`

### Typical commands

Dry-run (shape/IO check only):

```bash
python train_surrogate_spinup.py \
  --case <CASE_NAME> \
  --spinup-case <SPINUP_CASE_NAME> \
  --split-mode by_member \
  --train-fraction 0.8 \
  --split-random-state 2026 \
  --model-type nn \
  --dry-run
```

Random-forest training example:

```bash
python train_surrogate_spinup.py \
  --case <CASE_NAME> \
  --spinup-case <SPINUP_CASE_NAME> \
  --spinup-vars TOTSOMC,TOTSOMN \
  --surface-vars PCT_SAND,PCT_CLAY,ORGANIC \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --split-mode by_member \
  --train-fraction 0.8 \
  --split-random-state 2026 \
  --model-type random_forest \
  --quick-grid \
  --n-jobs 8 \
  --cv-folds 3 \
  --outputdir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project \
  --run-name spinup_surrogate_rf_test
```

Feature-ablation / diagnostics example (`params+surface`, no climatology block):

```bash
python train_surrogate_spinup.py \
  --case <CASE_NAME> \
  --spinup-case <SPINUP_CASE_NAME> \
  --model-type nn \
  --feature-set params_surface \
  --apply-variance-filter \
  --variance-threshold 1.0e-10 \
  --apply-corr-filter \
  --corr-threshold 0.98 \
  --permutation-repeats 8 \
  --split-mode by_member \
  --train-fraction 0.8 \
  --split-random-state 2026 \
  --stats-only \
  --run-name spinup_surrogate_ablation_ps
```

Reduced-climatology example (keep only mean/std/seasonal amplitude metrics):

```bash
python train_surrogate_spinup.py \
  --case <CASE_NAME> \
  --spinup-case <SPINUP_CASE_NAME> \
  --model-type nn \
  --feature-set all \
  --clim-feature-include "*_clim_mean,*_clim_std,*_clim_seasonal_amp" \
  --apply-corr-filter \
  --corr-threshold 0.98 \
  --permutation-repeats 8 \
  --split-random-state 2026 \
  --stats-only \
  --run-name spinup_surrogate_reduced_clim
```

Batch templates:
- [`examples/slurm/case.train_surrogate_spinup_quick.slurm`](examples/slurm/case.train_surrogate_spinup_quick.slurm)
- [`examples/slurm/case.train_surrogate_spinup_iter1.slurm`](examples/slurm/case.train_surrogate_spinup_iter1.slurm) (seed-array + variant-driven overfitting diagnostics)

Stats aggregation helper:

```bash
python summarize_spinup_stats.py \
  --stats-dir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/<RUN_NAME>/surrogate_spinup \
  --glob "surrogate_spinup_stats_seed*.json" \
  --output-json /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/<RUN_NAME>/surrogate_spinup/summary.json
```

### HPC validation checklist

1. Dry-run shape/IO checks for both model backends:
   - `--model-type nn --dry-run`
   - `--model-type random_forest --dry-run`
2. Split reproducibility checks:
   - run the same command twice with fixed `--split-random-state` and verify matching `split_details` in `surrogate_spinup_stats_*.json`
   - rerun with a different seed and verify changed split group IDs
3. Overfitting warning checks:
   - inspect stdout/stderr for `Warning: potential overfitting ...`
   - confirm `overfit_warning`, `r2_gap`, and `rmse_ratio` fields in stats JSON
4. Inference compatibility:
   - load `surrogate_spinup_artifacts.pkl` with `load_surrogate_spinup_artifacts(...)`
   - run `predict_spinup_state(...)` and confirm finite predictions for each requested spinup variable

### Perlmutter GSA smoke test (new GSA functions)

Use this quick flow to validate:
- given-data PAWN on aggregated metrics (`GSA_given_data_pawn`)
- forcing-fixed, params+spinup Sobol on aggregated metrics (`GSA_forcing_timeseries`)

1) Copy the smoke script to your home directory and edit placeholders:

```bash
cd /global/u1/t/tianyihu/elm-olmt
cp examples/gsa_smoke_test.py ~/gsa_smoke_test.py
```

Edit in `~/gsa_smoke_test.py`:
- `repo`
- `case_name`
- `test_vars` (recommend 1-2 vars for smoke test)
- `metrics` (for example `["mean"]` or `["accumulated", "std"]`)

2) Interactive run:

```bash
cd /global/u1/t/tianyihu/elm-olmt
conda activate OLMT_pm_Tianyi
python ~/gsa_smoke_test.py
```

3) Batch run (Slurm):

```bash
cd /global/u1/t/tianyihu/elm-olmt
sbatch examples/slurm/case.gsa_smoke_test.slurm
```

The script writes outputs to `~/gsa_test_output/<case_name>/` by default and prints metric-by-metric shape/finite-value checks for quick pass/fail.

### Standard GSA CLI (`run_standard_gsa.py`)

Use this CLI to run standardized GSA with a unified interface for:
- existing model outputs using PAWN (`--mode existing`)
- forcing surrogate outputs using Sobol (`--mode surrogate`)
- both (`--mode both`)

By default, spinup variables are included (`--spinup-vars TOTSOMC,TOTSOMN`).

Required inputs:
- `--case`
- `--vars`
- `--mode`
- `--artifact` when mode is `surrogate` or `both`

Outputs are written under:
- `<output-folder>/existing/` (existing-output PAWN files, e.g. `pawn_<var>.npz`)
- `<output-folder>/surrogate/` (forcing-surrogate Sobol files)
- `<output-folder>/run_metadata.json` (run configuration + summary)

If `--output-folder` is omitted, the default is `./UQ_output/<case>/GSA/`.

Single command example:

```bash
python run_standard_gsa.py \
  --workdir /global/u1/t/tianyihu/elm-olmt \
  --case JERC_ppe1_I20TRCNPRDCTCBC \
  --vars SR \
  --metrics mean,accumulated,std \
  --mode both \
  --artifact /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/multisite_test1/surrogate_forcing \
  --spinup-vars TOTSOMC,TOTSOMN \
  --saltelli-n 1024 \
  --n-jobs 8 \
  --output-folder /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/GSA/standard
```

Smoke test helper:

```bash
python examples/gsa_standard_smoke_test.py
```

Batch (Slurm) example:

```bash
sbatch examples/slurm/case.standard_gsa.slurm
```

## Forcing Surrogate MCMC Optimization

After training a forcing surrogate (which saves `surrogate_forcing_artifacts.pkl` under `<outputdir>/<case-or-run-name>/surrogate_forcing/`), you can optimize (calibrate) parameters with MCMC against observations stored in a NetCDF file. Observations are collocated to the surrogate's hourly time axis before likelihood evaluation.

### Coupled pipeline workflow

For a reproducible single-site or joint-site campaign, submit the stages manually in this order:

1. **Initialization** builds or validates the shared candidate pool and writes its immutable artifact manifest.
2. **Optimization** runs one seeded MCMC leaf per configured seed against that pool.
3. **Reporting** is a separate job that reads completed leaves and writes standardized products under the job-submission root, rather than into the repository.

Use one YAML file with `shared`, `initialization`, `optimization`, and `reporting` sections. Each stage consumes `shared` plus its own section and records its source/dependency identities in a stage manifest; do not alter the YAML between stages. The reviewed examples are in [`development/spinup_forcing_coupling/examples/iter017/`](development/spinup_forcing_coupling/examples/iter017/).

The report directory contains `plots/physical_corner.png`, per-seed default corner and posterior time-series plots in `per_seed/`, and `best_parameters/parameter_sets.{csv,txt}`. It also copies one exact model-ready `clm_params_seed_<seed>.nc` file per seed in `best_parameters/clm_params/`; NetCDF parameter files are deliberately not merged. A report is always written even if no seed meets the configured descriptive retention rule, in which case its manifest says `status: insufficient_retained` and no posterior is promoted.

The Iter017 integrity regression tested three seeds (`9009`--`9011`) at `64 × 2000` for ABBY daily/0.50, JERC hourly/0.75, and joint ABBY+JERC daily/0.50 and hourly/0.75. These are pipeline examples, not convergence settings or scientific calibration results.

### Observation NetCDF units

Observations are loaded by [`model_ELM/load_obs_nc.py`](model_ELM/load_obs_nc.py). Flux variables are converted to **daily units** to match surrogate training targets (the same daily flux units produced by ELM postprocessing, e.g. `gC/m^2/day` for carbon fluxes such as `GPP`/`NEE`/`NPP`, and `mm/day` for water fluxes such as `QRUNOFF`).

Each observation variable (and its error variable, if provided) should include a NetCDF **`units`** attribute. Conversion rules:

| `units` attribute | Behavior |
|---|---|
| `gC/m^2/s`, `gN/m^2/s`, `gP/m^2/s`, `mm/s` (and common CF variants) | multiply by 86400 → daily units |
| `gC/m^2/day`, `g.C/m2/day`, `mm/day`, etc. | no scaling (already daily) |
| missing / empty | assume per-second flux, multiply by 86400, and print a warning |
| unrecognized (e.g. `umol/m2/s`) | print a warning and raise `ValueError` |

Sub-hourly data are averaged to hourly before unit conversion. Error variables use the same conversion path as their paired observation variable.

When preparing observation files, set `units` explicitly rather than relying on the missing-units default.

### CLI: `optimize_surrogate_forcing.py`

This driver will:

- load the explicit optimization target cases from `--case` (`pklfiles/<case>.pkl`)
- load a trained forcing surrogate from `surrogate_forcing_artifacts.pkl`
- use artifact `training_layout` metadata as the schema contract (forcing features, spinup vars, parameter count)
- rebuild forcing-engineered inputs from each target `case.metdir` using that artifact metadata
- compute spinup features from restart files (default: **mean across ensemble members**; or choose one member)
- read observations from a NetCDF file (`--obs`) with their time axis
- collocate forcing and observations by **exact overlapping hourly timestamps** (both axes on the no-leap calendar, floored to the hour) before likelihood evaluation
- run MCMC using the forcing surrogate forward model
- write outputs to `./UQ_output/<casename>/MCMC_forcing_output/`:
  - `best_params.txt`
  - `clm_params_best.nc`
  - posterior PDFs, posterior predictive plots, and a corner plot (same post-processing style as `model_ELM/MCMC.py`)

Posterior predictive plots also overlay **pre-calibration ELM** output when available:

- **`MCMC()` (parameter surrogate):** reads `case.output[var]` from the case pickle. The baseline series must have the **same length** as `obs[var]` used in MCMC (same postprocessing/averaging). Use a non-ensemble baseline run saved in the pickle before ensemble postprocessing fills `output` with multiple members.
- **`MCMC_forcing()`:** collocated hourly `obs` often differ in length from typical annual/monthly `case.output`. Pass pre-aligned baseline fluxes in `forcing_context[site]["baseline_output"]` as a dict `{var: 1d_array}` with one value per collocated time step. If lengths do not match, the plot skips the baseline curve and prints a warning.

#### Single-site example

```bash
# Paths
WORKDIR="/path/to/elm-olmt"
CASE="<CASE_NAME>"

# Artifact from forcing-surrogate training
ARTIFACT="/path/to/output/<CASE_OR_RUN_NAME>/surrogate_forcing/surrogate_forcing_artifacts.pkl"

# Observations (NetCDF): variables must match --vars (e.g., GPP, SR)
OBS_NC="/path/to/obs_${CASE}.nc"

python optimize_surrogate_forcing.py \
  --workdir "${WORKDIR}" \
  --case "${CASE}" \
  --artifact "${ARTIFACT}" \
  --vars GPP,SR \
  --obs "${OBS_NC}" \
  --obs-err-vars "GPP:GPP_SE,SR:SR_SE" \
  --nwalkers 32 \
  --nsteps 100 \
  --spinup-member 1
```

Notes:
- Observation variables must use `units` compatible with the table above so values match surrogate training outputs in daily flux units.
- If an error variable is not provided (or missing in the file), observation uncertainty defaults to **10% of |obs|**.
- Missing/invalid observations should be encoded as `-9999` (they are masked during likelihood evaluation).
- The optimizer prints per-site overlap diagnostics (`forcing rows`, `obs rows`, `overlap rows`, overlap time window).
- To show the pre-calibration ELM curve on forcing MCMC plots, include `baseline_output` in each site's `forcing_context` entry (see above).

#### Dry-run collocation check (recommended)

Use `--dry-run-collocation` to verify forcing/obs overlap sizes and windows before launching MCMC:

```bash
python optimize_surrogate_forcing.py \
  --workdir "${WORKDIR}" \
  --case "${CASE}" \
  --artifact "${ARTIFACT}" \
  --vars GPP,SR \
  --obs "${OBS_NC}" \
  --obs-err-vars "GPP:GPP_SE,SR:SR_SE" \
  --spinup-member 1 \
  --dry-run-collocation
```

This mode performs all per-site loading and time-overlap collocation, prints a summary, and exits without sampling.

#### Multi-site / multi-case example (shared artifact, per-site obs paths)

The optimizer treats the `--case` list as the authoritative optimization targets. You can pass one observation file for all cases/sites, or provide a per-site/per-case mapping:

```bash
python optimize_surrogate_forcing.py \
  --workdir "${WORKDIR}" \
  --case "<CASE_SITEA>,<CASE_SITEB>" \
  --artifact "${ARTIFACT}" \
  --vars SR \
  --obs "US-UMB:/path/to/obs_US-UMB.nc,US-MOz:/path/to/obs_US-MOz.nc" \
  --obs-err-vars "SR:SR_SE" \
  --nwalkers 48 \
  --nsteps 200
```

Notes:
- Artifact metadata in `training_layout` must remain available; model/scaler-only payloads are not sufficient for rebuilding inputs.
- Each case in `--case` should map to a unique site label (via `case.site`) for per-site diagnostics and outputs.

### Choosing CPUs and walkers (practical guidance)

MCMC cost scales roughly with:

- \(n_{walkers} \\times n_{steps} \\times n_{sites} \\times n_{vars} \\times n_{time}\)

Key points:

- **Walkers**: For `emcee` ensemble sampling, a safe minimum is **\(2 \\times n_{dim}\)** where \(n_{dim} = n_{params} (+ n_{vars} \\text{ if fitting } \\sigma_{var})\). In practice, start with:
  - **32 walkers** for smaller problems (tens of parameters)
  - **48–128 walkers** for higher-dimensional calibration
- **CPUs / processes**: This implementation can parallelize `emcee` log-prob evaluations via a multiprocessing pool (use `--n-processes`, defaulting to `SLURM_CPUS_PER_TASK` when set). Scaling is typically best up to ~`min(nwalkers, n-processes)`, and can be limited by surrogate inference cost and per-site/time-series length.
- **Avoid oversubscription**: If your environment uses threaded BLAS/OpenMP, set:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
```

Suggested starting point on HPC:
- **`--cpus-per-task=1` to `4`** (unless you have a specific reason to allocate more)
- **increase `--nwalkers` first** if you need better mixing or higher effective sample size
- do a short smoke test (`--nsteps 20`) before longer runs
