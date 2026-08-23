#!/bin/bash -e
#
# Forcing surrogate MCMC optimization example (Perlmutter-style Slurm).
#
# Notes:
# - MCMC can parallelize log-prob evaluation using emcee's multiprocessing pool.
#   Use --n-processes to match (or be slightly below) --cpus-per-task.
# - Avoid BLAS/OpenMP oversubscription (set threads to 1).
#
#SBATCH --time=02:00:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J forcing_mcmc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16GB
#SBATCH --output=forcing_mcmc_%j.out
#SBATCH --error=forcing_mcmc_%j.err

scontrol show job $SLURM_JOB_ID

# --- User settings ---
OLMT_ROOT="/global/u1/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"

# Explicit optimization target case(s). Use comma-separated values for multi-case runs.
CASE_LIST="ABBY_ens3_I20TRCNPRDCTCBC"
OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"

# Artifact produced by train_surrogate_forcing.py (or multi-case training).
# Keep artifact metadata (training_layout) available; model/scaler-only payloads are not sufficient.
ARTIFACT="${OUTPUTDIR}/ABBY_ens3_I20TRCNPRDCTCBC/surrogate_forcing/surrogate_forcing_artifacts.pkl"

# Observation NetCDF:
# - Single file for all cases/sites: OBS_NC="/path/to/all_sites_obs.nc"
# - Per-site/per-case mapping:      OBS_NC="US-UMB:/path/to/obs_US-UMB.nc,US-MOz:/path/to/obs_US-MOz.nc"
OBS_NC="/path/to/ABBY_ens3_I20TRCNPRDCTCBC_obs.nc"

VARS="GPP,SR"
OBS_ERR_VARS="GPP:GPP_SE,SR:SR_SE"

NWALKERS=32
NSTEPS=100

# Optional: choose one ensemble member restart for spinup features.
# If omitted, optimizer uses mean spinup across ensemble members.
SPINUP_MEMBER=1

# Parallel worker processes for emcee pool (cap to allocated CPUs)
N_PROCS="${SLURM_CPUS_PER_TASK:-4}"

# Set to 1 to run overlap diagnostics only (no MCMC sampling).
DRY_RUN_COLLOCATION=1

DRY_RUN_FLAG=""
if [ "${DRY_RUN_COLLOCATION}" = "1" ]; then
  DRY_RUN_FLAG="--dry-run-collocation"
fi

cd "${OLMT_ROOT}"
conda activate "${CONDA_ENV}"

# Avoid BLAS/OpenMP oversubscription inside the job allocation.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

python optimize_surrogate_forcing.py \
  --workdir "${OLMT_ROOT}" \
  --outputdir "${OUTPUTDIR}" \
  --case "${CASE_LIST}" \
  --artifact "${ARTIFACT}" \
  --vars "${VARS}" \
  --obs "${OBS_NC}" \
  --obs-err-vars "${OBS_ERR_VARS}" \
  --nwalkers "${NWALKERS}" \
  --nsteps "${NSTEPS}" \
  --n-processes "${N_PROCS}" \
  --spinup-member "${SPINUP_MEMBER}" \
  ${DRY_RUN_FLAG}
