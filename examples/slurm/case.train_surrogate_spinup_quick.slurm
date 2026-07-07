#!/bin/bash -e
#
# Standalone spinup-surrogate training example (Perlmutter-style Slurm).
#
# This script trains model_ELM/surrogate_NN_Spinup.py via train_surrogate_spinup.py
# using quick-grid settings for testing.
#
#SBATCH --time=00:10:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J spinup_surrogate
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8GB
#SBATCH --output=spinup_surr_%j.out
#SBATCH --error=spinup_surr_%j.err

scontrol show job $SLURM_JOB_ID

# --- User settings ---
OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"

# Single case or comma-separated multi-case list
CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC"
SPINUP_CASE_LIST="ABBY_ppe6_I1850CNPRDCTCBC"

OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"
RUN_NAME="spinup_surrogate_test1"

SPINUP_VARS="TOTSOMC,TOTSOMN"
SURFACE_VARS="PCT_SAND,PCT_CLAY,ORGANIC"
FORCING_VARS="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"

# Split strategy for member-level spinup targets
SPLIT_MODE="by_member"
TRAIN_FRACTION="0.8"

# Set to 1 for shape/IO smoke test only (no model fitting)
DRY_RUN=0

DRY_RUN_FLAG=""
if [ "${DRY_RUN}" = "1" ]; then
  DRY_RUN_FLAG="--dry-run"
fi

cd "${OLMT_ROOT}"
conda activate "${CONDA_ENV}"

# Avoid BLAS/OpenMP oversubscription inside joblib workers.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

# Match GridSearchCV parallelism to Slurm CPU allocation.
N_JOBS="${SLURM_CPUS_ON_NODE:-${SLURM_CPUS_PER_TASK:-1}}"

python train_surrogate_spinup.py \
  --workdir "${OLMT_ROOT}" \
  --case "${CASE_LIST}" \
  --spinup-case "${SPINUP_CASE_LIST}" \
  --spinup-vars "${SPINUP_VARS}" \
  --surface-vars "${SURFACE_VARS}" \
  --forcing-vars "${FORCING_VARS}" \
  --split-mode "${SPLIT_MODE}" \
  --train-fraction "${TRAIN_FRACTION}" \
  --clim-feature-mode compact \
  --quick-grid \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --outputdir "${OUTPUTDIR}" \
  --run-name "${RUN_NAME}" \
  ${DRY_RUN_FLAG}

