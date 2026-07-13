#!/bin/bash -e
#
# Perlmutter CPU batch template for spinup-surrogate overfitting iteration.
# Submit examples:
#   VARIANT=baseline sbatch examples/slurm/case.train_surrogate_spinup_iter1.slurm
#   VARIANT=no_clim sbatch examples/slurm/case.train_surrogate_spinup_iter1.slurm
#   VARIANT=reduced_clim sbatch examples/slurm/case.train_surrogate_spinup_iter1.slurm
#
#SBATCH --time=00:10:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J spinup_iter1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8GB
#SBATCH --array=1-100
#SBATCH --output=spinup_iter1_%A_%a.out
#SBATCH --error=spinup_iter1_%A_%a.err

# --- User settings ---
OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC"
SPINUP_CASE_LIST="ABBY_ppe6_I1850CNPRDCTCBC"
OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"
RUN_NAME_BASE="spinup_surrogate_iter1"

SPINUP_VARS="TOTSOMC,TOTSOMN"
SURFACE_VARS="PCT_SAND,PCT_CLAY,ORGANIC"
FORCING_VARS="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"
SPLIT_MODE="by_member"
TRAIN_FRACTION="0.8"
CLIM_FEATURE_MODE="compact"

# Optional controls via environment variables at submit time.
VARIANT="${VARIANT:-baseline}"
STATS_ONLY="${STATS_ONLY:-1}"      # 1: write stats json only (fast array sweeps)
APPLY_VARIANCE_FILTER="${APPLY_VARIANCE_FILTER:-0}"
VARIANCE_THRESHOLD="${VARIANCE_THRESHOLD:-1.0e-12}"
APPLY_CORR_FILTER="${APPLY_CORR_FILTER:-0}"
CORR_THRESHOLD="${CORR_THRESHOLD:-0.98}"
PERMUTATION_REPEATS="${PERMUTATION_REPEATS:-8}"

RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
RUN_NAME="${RUN_NAME_BASE}_${VARIANT}"

MODEL_TYPE="nn"
FEATURE_SET="all"
CLIM_FEATURE_INCLUDE="*"
QUICK_GRID_FLAG="--quick-grid"

case "${VARIANT}" in
  baseline)
    MODEL_TYPE="nn"
    FEATURE_SET="all"
    CLIM_FEATURE_INCLUDE="*"
    ;;
  tuned_nn)
    MODEL_TYPE="nn"
    FEATURE_SET="all"
    CLIM_FEATURE_INCLUDE="*"
    APPLY_VARIANCE_FILTER=1
    APPLY_CORR_FILTER=1
    ;;
  no_clim)
    MODEL_TYPE="nn"
    FEATURE_SET="params_surface"
    CLIM_FEATURE_INCLUDE="*"
    APPLY_VARIANCE_FILTER=1
    APPLY_CORR_FILTER=1
    ;;
  reduced_clim)
    MODEL_TYPE="nn"
    FEATURE_SET="all"
    CLIM_FEATURE_INCLUDE="*_clim_mean,*_clim_std,*_clim_seasonal_amp"
    APPLY_VARIANCE_FILTER=1
    APPLY_CORR_FILTER=1
    ;;
  rf_constrained)
    MODEL_TYPE="random_forest"
    FEATURE_SET="all"
    CLIM_FEATURE_INCLUDE="*"
    APPLY_VARIANCE_FILTER=1
    APPLY_CORR_FILTER=1
    ;;
  *)
    echo "Unsupported VARIANT='${VARIANT}'"
    echo "Supported: baseline | tuned_nn | no_clim | reduced_clim | rf_constrained"
    exit 2
    ;;
esac

cd "${OLMT_ROOT}"
conda activate "${CONDA_ENV}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

N_JOBS="${SLURM_CPUS_PER_TASK:-1}"

EXTRA_FLAGS=()
if [ "${STATS_ONLY}" = "1" ]; then
  EXTRA_FLAGS+=("--stats-only" "--stats-run-id" "seed${RANDOM_SEED}")
fi
if [ "${APPLY_VARIANCE_FILTER}" = "1" ]; then
  EXTRA_FLAGS+=("--apply-variance-filter" "--variance-threshold" "${VARIANCE_THRESHOLD}")
fi
if [ "${APPLY_CORR_FILTER}" = "1" ]; then
  EXTRA_FLAGS+=("--apply-corr-filter" "--corr-threshold" "${CORR_THRESHOLD}")
fi

python train_surrogate_spinup.py \
  --workdir "${OLMT_ROOT}" \
  --case "${CASE_LIST}" \
  --spinup-case "${SPINUP_CASE_LIST}" \
  --spinup-vars "${SPINUP_VARS}" \
  --surface-vars "${SURFACE_VARS}" \
  --forcing-vars "${FORCING_VARS}" \
  --model-type "${MODEL_TYPE}" \
  --feature-set "${FEATURE_SET}" \
  --clim-feature-include "${CLIM_FEATURE_INCLUDE}" \
  --split-mode "${SPLIT_MODE}" \
  --train-fraction "${TRAIN_FRACTION}" \
  --split-random-state "${RANDOM_SEED}" \
  --clim-feature-mode "${CLIM_FEATURE_MODE}" \
  --permutation-repeats "${PERMUTATION_REPEATS}" \
  ${QUICK_GRID_FLAG} \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --outputdir "${OUTPUTDIR}" \
  --run-name "${RUN_NAME}" \
  "${EXTRA_FLAGS[@]}"
