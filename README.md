Offline Land Model Testbed (OLMT)
Contact:  Dan Ricciuto (ricciutodm@ornl.gov)

Updated 2/25/2025

The purpose of the Offline Land Model Testbed (OLMT) is to simplify the workflows for single site, regional and ensemble offline ELM simulations, which are otherwise cumbersome using only CIME. We have been working on a new version with an improved interface.  The user now can run a simulation using a single python run script that will perform the entire workflow.  This usually involves setting up three cases for biogeochemistry-enabled runs: the ad spinup, final spinup and transient simulations.  It is also possible to add additional cases beginning in later years where we apply treatment effects or otherwise modify forcings.  For example, in the SPRUCE study we have 10 experimental treatments (different levels of temperature and CO2 modifications) that begin in 2015.  For those point simulations, we have a single run script that launches and manages 13 cases. 
 
For each case, the runscript will perform the create_newcase, case setup, and submission.  The case.build will be performed on the first case only, and then the same executable will be used for following cases.  When submitting cases, the correct dependencies will be applied, such that the second case will start running after the first has finished, etc.
 
Users can customize the simulations to run single points, a list of lat/lon coordinates, rectangular regions or global simulations. OLMT assumes surface, land use and domain data already exist (using the defaults for specified compsets and resolution) and will extract points or regions from these data.  The user can also set custom files, for example ultra high-resolution files created from kilocraft.  For single point runs, the PFT and soil information can be set to match observations, for example at AmeriFlux sites.
 
Finally, OLMT also has the capability to perform ensemble simulations.  Users can specify a list of parameters, with allowable ranges for each. Random samples can then be created.  Alternatively, the user can provide their own files with different parameter combinations.  When this ensemble option is enabled, the cases will be set up in the same way as above, but then multiple copies of run directories will be created. We then use another MPI-enabled python script to manage the multiple simulations in parallel.  Users can also specify a list of output variables and time frequency for which to postprocess.  A matrix of output values for all ensemble members is then created at the end of the simulation, which can then be used in Uncertainty quantification applications discussed in the other epics.

Please see the wiki page for instructions and examples.

## Standalone Hybrid Forcing Surrogate

Training logic lives in [`model_ELM/surrogate_NN_Forcing.py`](model_ELM/surrogate_NN_Forcing.py) and is exposed on the case object as **`train_surrogate_with_forcing`** and **`run_surrogate_forcing`** (same pattern as `train_surrogate` / `run_surrogate` in [`model_ELM/surrogate_NN.py`](model_ELM/surrogate_NN.py), wired through [`model_ELM/main.py`](model_ELM/main.py)).

**Command-line driver** — same idea as [`manage_ensemble.py`](manage_ensemble.py): load `pklfiles/<case>.pkl`, then call the case method.

- **`train_surrogate_forcing.py`** — preferred entry point from the OLMT repository root.

**Backward compatibility:** repo-root **`surrogate_NN_Forcing.py`** is a thin wrapper that forwards to `train_surrogate_forcing.main()`, so existing invocations of `python surrogate_NN_Forcing.py ...` keep working.

**Programmatic use:** after `import model_ELM`, a loaded `ELMcase` instance has `train_surrogate_with_forcing(myvars, ...)` and `run_surrogate_forcing(parms, myvars, ...)` (optional full design matrix `X`, or `forcing_engineered` + `spinup` with `parms`).

The workflow trains a surrogate for hourly ELM outputs (for example, `GPP`, `SR`) using a hybrid feature set:

- hourly forcing variables (default: `PRECTmms`, `FSDS`, `FLDS`, `TBOT`, `RH`, `WIND`, `PSRF`)
- static ensemble parameters (`self.samples`) broadcast across timesteps
- spinup state features from restart files (`TOTSOMC`, `TOTSOMN` by default), broadcast across timesteps
- engineered forcing-memory and temporal features:
  - temperature rolling means: 24h, 7d, 30d
  - precipitation rolling sums: 24h, 7d, 30d
  - `sin(hour_of_day)`, `cos(hour_of_day)`
  - forcing anomalies defined as `forcing_t - rolling_mean_30day_t`

The CLI is separate from the ensemble workflow manager ([`manage_ensemble.py`](manage_ensemble.py)) but uses the same pickle convention. By default it resolves the case pickle from:

`<workdir>/pklfiles/<case>.pkl`

(`--workdir` defaults to the current directory; run from the OLMT root where `pklfiles/` lives.)

### Recent updates

- forcing is explicitly converted to no-leap calendar using `convert_calendar('noleap')` and coarsened to hourly with `coarsen(time=2).mean()`
- spinup restart path is resolved using `case.dependcase` and `case.finidat` naming, improving compatibility when restart files are sourced from dependent cases
- spinup variables support aggregated sums through `SPINUP_VAR_SUM` (for example `TOTSOMC`, `TOTSOMN`)
- anomaly features skip selected state/meteorology variables (`FLDS`, `QBOT`, `WIND`, `PSRF`, `RH`)
- output root is configurable with `--outputdir` (default: current directory, i.e. **`./UQ_output/<case>/surrogate_forcing/`** under that base; set an absolute path on HPC when needed)

### Key capabilities

- standalone CLI via **`train_surrogate_forcing.py`** (`--case`, `--vars`, `--workdir`, forcing/spinup options, and the same flags as before)
- split modes for validation:
  - `by_member`
  - `by_site`
  - `by_time_block` (continuous time split)
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
  - `<outputdir>/UQ_output/<case>/surrogate_forcing/`
  - including `surrogate_forcing_artifacts.pkl`, diagnostic plots (`*_surrogate_forcing.png`), and the memmap-backed feature matrix used during training
- after training, the case object holds **`surrogate_forcing`**, **`x_scaler_forcing`**, **`y_scaler_forcing`**, and **`forcing_surrogate_training`** metadata for **`run_surrogate_forcing`**
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
