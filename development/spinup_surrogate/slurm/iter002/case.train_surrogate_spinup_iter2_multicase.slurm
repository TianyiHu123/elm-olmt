#!/bin/bash -e
#
# Canonical iter002 multicase spinup-surrogate script.
# Submission examples (Round B, not executed in Round A):
#   VARIANT=multi_all sbatch development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm
#   VARIANT=multi_params_surface sbatch development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm
#   VARIANT=multi_params_clim sbatch development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm
#   VARIANT=multi_params_only sbatch development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm
#
#SBATCH --time=00:05:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J spinup_iter2_multicase
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=42GB
#SBATCH --array=1-30
#SBATCH --output=spinup_iter2_%A_%a.out
#SBATCH --error=spinup_iter2_%A_%a.err

set -o pipefail

# --- User settings ---
OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC"
SPINUP_CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC"
OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"
RUN_NAME_BASE="spinup_surrogate_iter2"

SPINUP_VARS="TOTSOMC,TOTSOMN"
SURFACE_VARS="PCT_SAND,PCT_CLAY,ORGANIC"
FORCING_VARS="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"
SPLIT_MODE="by_member"
TRAIN_FRACTION="0.8"
CLIM_FEATURE_MODE="compact"

# Optional controls via environment variables at submit time.
VARIANT="${VARIANT:-multi_all}"
STATS_ONLY="${STATS_ONLY:-1}"      # 1: write stats json only (seed sweeps)
APPLY_VARIANCE_FILTER="${APPLY_VARIANCE_FILTER:-1}"
VARIANCE_THRESHOLD="${VARIANCE_THRESHOLD:-1.0e-12}"
APPLY_CORR_FILTER="${APPLY_CORR_FILTER:-1}"
CORR_THRESHOLD="${CORR_THRESHOLD:-0.98}"
PERMUTATION_REPEATS="${PERMUTATION_REPEATS:-8}"

RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
RUN_NAME="${RUN_NAME_BASE}_${VARIANT}"

MODEL_TYPE="nn"
FEATURE_SET="all"
CLIM_FEATURE_INCLUDE="*"
QUICK_GRID_FLAG="--quick-grid"

case "${VARIANT}" in
  multi_all)
    FEATURE_SET="all"
    ;;
  multi_params_surface)
    FEATURE_SET="params_surface"
    ;;
  multi_params_clim)
    FEATURE_SET="params_clim"
    ;;
  multi_params_only)
    FEATURE_SET="params_only"
    ;;
  *)
    echo "Unsupported VARIANT='${VARIANT}'"
    echo "Supported: multi_all | multi_params_surface | multi_params_clim | multi_params_only"
    exit 2
    ;;
esac

trap 'rc=$?; if [ "${rc}" -ne 0 ]; then echo "FAIL_FAST_BLOCKED variant=${VARIANT} seed=${RANDOM_SEED} exit_code=${rc}" >&2; fi' EXIT

cd "${OLMT_ROOT}"
conda activate "${CONDA_ENV}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

N_JOBS="${SLURM_CPUS_PER_TASK:-1}"

SCRIPT_PATH="$(realpath "$0" 2>/dev/null || echo "$0")"
SCRIPT_SHA256="$(sha256sum "${SCRIPT_PATH}" | awk '{print $1}')"
GIT_COMMIT="$(git -C "${OLMT_ROOT}" rev-parse HEAD 2>/dev/null || echo unknown)"
echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} script_path=${SCRIPT_PATH} script_sha256=${SCRIPT_SHA256} commit_hash=${GIT_COMMIT}"

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
