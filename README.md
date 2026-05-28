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
- spinup restart path is resolved using `case.dependcase` and `case.finidat` naming, improving compatibility when restart files are sourced from dependent cases
- spinup variables support aggregated sums through `SPINUP_VAR_SUM` (for example `TOTSOMC`, `TOTSOMN`)
- anomaly features skip selected state/meteorology variables (`FLDS`, `QBOT`, `WIND`, `PSRF`, `RH`)
- output root is configurable with `--outputdir` (default: current directory, i.e. **`./UQ_output/<case>/surrogate_forcing/`** under that base; set an absolute path on HPC when needed)
- multi-case runs can set `--run-name` to choose a short output folder label under `UQ_output/`, which also controls where the merged `X_forcing_memmap.dat` is saved
- **Train/validation robustness:** `split_mode=random_time_window` draws a random contiguous time window per case (seed with `split_random_state` / `--split-random-state`) so you can study sensitivity to the temporal split
- **Stats-only runs:** `--stats-only` skips plots and `surrogate_forcing_artifacts.pkl` and writes a small JSON metrics file per run (`surrogate_forcing_stats_*.json`), with filenames keyed off SLURM array/job env vars or `--stats-run-id` so array jobs do not overwrite each other
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
  - `--dtype` (`float32` default)
- memory-aware training:
  - dry-run size/memory estimate
  - disk-backed feature matrix via `numpy.memmap`
  - warnings for potentially aggressive parallel settings
- outputs saved to:
  - `<outputdir>/UQ_output/<case-or-run-name>/surrogate_forcing/`
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
MEMMAP_DIR="/path/to/UQ_output/<CASE_OR_RUN_NAME>/surrogate_forcing"

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

MEMMAP_DIR="/path/to/UQ_output/<CASE_NAME>/surrogate_forcing"
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

Stats JSON files are written under **`/path/to/scratch/UQ_output/<CASE_NAME>/surrogate_forcing/`** (or under `--run-name` when you use it). Aggregate those JSON files offline to summarize R² distributions.

## Forcing Surrogate MCMC Optimization

After training a forcing surrogate (which saves `surrogate_forcing_artifacts.pkl` under `UQ_output/<case-or-run-name>/surrogate_forcing/`), you can optimize (calibrate) parameters with MCMC against hourly observations stored in a NetCDF file.

### CLI: `optimize_surrogate_forcing.py`

This driver will:

- load `pklfiles/<case>.pkl` to get parameter bounds and case metadata
- load a trained forcing surrogate from `surrogate_forcing_artifacts.pkl`
- rebuild the forcing-engineered inputs from `case.metdir` using the artifact metadata
- compute spinup features from restart files (default: **mean across ensemble members**; or choose one member)
- read observations from a NetCDF file (`--obs`) with their time axis
- collocate forcing and observations by **overlapping hourly timestamps** before likelihood evaluation
- run MCMC using the forcing surrogate forward model
- write outputs to `./UQ_output/<casename>/MCMC_forcing_output/`:
  - `best_params.txt`
  - `clm_params_best.nc`
  - posterior PDFs, posterior predictive plots, and a corner plot (same post-processing style as `model_ELM/MCMC.py`)

#### Single-site example

```bash
# Paths
WORKDIR="/path/to/elm-olmt"
CASE="<CASE_NAME>"

# Artifact from forcing-surrogate training
ARTIFACT="/path/to/UQ_output/<CASE_OR_RUN_NAME>/surrogate_forcing/surrogate_forcing_artifacts.pkl"

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
- If an error variable is not provided (or missing in the file), observation uncertainty defaults to **10% of |obs|**.
- Missing/invalid observations should be encoded as `-9999` (they are masked during likelihood evaluation).
- The optimizer prints per-site overlap diagnostics (`forcing rows`, `obs rows`, `overlap rows`, overlap time window).

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

#### Multi-site example (shared artifact, per-site obs paths)

If `case.all_sites` contains multiple sites, the optimizer will loop over them. You can pass one observation file for all sites, or provide a per-site/per-case mapping:

```bash
python optimize_surrogate_forcing.py \
  --workdir "${WORKDIR}" \
  --case "<CASE_SITEA>" \
  --artifact "${ARTIFACT}" \
  --vars SR \
  --obs "US-UMB:/path/to/obs_US-UMB.nc,US-MOz:/path/to/obs_US-MOz.nc" \
  --obs-err-vars "SR:SR_SE" \
  --nwalkers 48 \
  --nsteps 200
```

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
