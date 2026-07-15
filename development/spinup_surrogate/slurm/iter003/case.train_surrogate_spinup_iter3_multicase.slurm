#!/bin/bash -e
#
# Canonical iter003 efficiency-first multicase spinup-surrogate script.
#
# Pilot:
#   VARIANT=multi_all RUN_NAME_BASE=spinup_surrogate_iter3_pilot \
#     sbatch --array=1-5 case.train_surrogate_spinup_iter3_multicase.slurm
#
# Full matrix, submitted only after the pilot gates pass:
#   for VAR in multi_all multi_params_surface multi_params_clim multi_params_only; do
#     VARIANT="$VAR" sbatch --array=1-30 \
#       case.train_surrogate_spinup_iter3_multicase.slurm
#   done
#
# Parallelism profile:
#   4 GridSearchCV workers, one BLAS thread per worker. This is intentional:
#   iter002 used 8 workers and reached ~38.6 GB RSS under a 42 GB request.
#
#SBATCH --time=00:20:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J spinup_iter3_multicase
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=42GB
#SBATCH --array=1-5
#SBATCH --output=spinup_iter3_%A_%a.out
#SBATCH --error=spinup_iter3_%A_%a.err

set -o pipefail

OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC"
SPINUP_CASE_LIST="${CASE_LIST}"
OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"
RUN_NAME_BASE="${RUN_NAME_BASE:-spinup_surrogate_iter3}"

SPINUP_VARS="TOTSOMC,TOTSOMN"
SURFACE_VARS="PCT_SAND,PCT_CLAY,ORGANIC"
FORCING_VARS="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"
SPLIT_MODE="by_member"
TRAIN_FRACTION="0.8"
CLIM_FEATURE_MODE="compact"

VARIANT="${VARIANT:-multi_all}"
STATS_ONLY="${STATS_ONLY:-1}"
APPLY_VARIANCE_FILTER="${APPLY_VARIANCE_FILTER:-1}"
VARIANCE_THRESHOLD="${VARIANCE_THRESHOLD:-1.0e-12}"
APPLY_CORR_FILTER="${APPLY_CORR_FILTER:-1}"
CORR_THRESHOLD="${CORR_THRESHOLD:-0.98}"
PERMUTATION_REPEATS="${PERMUTATION_REPEATS:-8}"
N_JOBS="${N_JOBS:-${SLURM_CPUS_PER_TASK:-1}}"
PARALLELISM_PROFILE="${PARALLELISM_PROFILE:-gridsearch_njobs4_blas1}"

RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
RUN_NAME="${RUN_NAME_BASE}_${VARIANT}"

MODEL_TYPE="nn"
FEATURE_SET="all"
CLIM_FEATURE_INCLUDE="*"

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
    echo "Unsupported VARIANT='${VARIANT}'" >&2
    echo "Supported: multi_all | multi_params_surface | multi_params_clim | multi_params_only" >&2
    exit 2
    ;;
esac

START_EPOCH="$(date +%s)"
START_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
trap 'rc=$?; END_EPOCH="$(date +%s)"; END_UTC="$(date -u "+%Y-%m-%dT%H:%M:%SZ")"; echo "RUN_END_UTC=${END_UTC} wall_seconds=$((END_EPOCH-START_EPOCH)) exit_code=${rc}"; if [ "${rc}" -ne 0 ]; then echo "FAIL_FAST_BLOCKED variant=${VARIANT} seed=${RANDOM_SEED} exit_code=${rc}" >&2; fi' EXIT

cd "${OLMT_ROOT}"
conda activate "${CONDA_ENV}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

SCRIPT_PATH="$(realpath "$0" 2>/dev/null || echo "$0")"
SCRIPT_SHA256="$(sha256sum "${SCRIPT_PATH}" | awk '{print $1}')"
GIT_COMMIT="$(git -C "${OLMT_ROOT}" rev-parse HEAD 2>/dev/null || echo unknown)"
echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} script_path=${SCRIPT_PATH} script_sha256=${SCRIPT_SHA256} commit_hash=${GIT_COMMIT}"
echo "RUNTIME_CONFIG profile=${PARALLELISM_PROFILE} slurm_cpus=${SLURM_CPUS_PER_TASK:-unknown} n_jobs=${N_JOBS} omp=${OMP_NUM_THREADS} run_name=${RUN_NAME}"
echo "RUN_START_UTC=${START_UTC}"

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

/usr/bin/time -v python train_surrogate_spinup.py \
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
  --quick-grid \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --outputdir "${OUTPUTDIR}" \
  --run-name "${RUN_NAME}" \
  "${EXTRA_FLAGS[@]}"
