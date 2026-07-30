#!/bin/bash -e
#
# Canonical iter006 nine-case feature-settling script.
#
# Submit one array per variant:
#   VARIANT=all_control sbatch --array=1-5 \
#     case.train_surrogate_spinup_iter6_feature_settle.slurm
#
#SBATCH --time=00:30:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J spinup_iter6_feature
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48GB
#SBATCH --array=1-5
#SBATCH --output=spinup_iter6_%A_%a.out
#SBATCH --error=spinup_iter6_%A_%a.err

set -o pipefail

OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
CASE_LIST="ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC"
SPINUP_CASE_LIST="${CASE_LIST}"
OUTPUTDIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project"
RUN_NAME_BASE="${RUN_NAME_BASE:-spinup_surrogate_iter6}"

SPINUP_VARS="TOTSOMC,TOTSOMN"
SURFACE_VARS="PCT_SAND,PCT_CLAY,ORGANIC"
FORCING_VARS="PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"
SPLIT_MODE="by_member"
TRAIN_FRACTION="0.8"
CLIM_FEATURE_MODE="compact"

VARIANT="${VARIANT:-all_control}"
STATS_ONLY="${STATS_ONLY:-1}"
N_JOBS="${N_JOBS:-4}"
PRE_DISPATCH="${PRE_DISPATCH:-n_jobs}"
PERMUTATION_REPEATS="${PERMUTATION_REPEATS:-8}"
APPLY_VARIANCE_FILTER="${APPLY_VARIANCE_FILTER:-1}"
VARIANCE_THRESHOLD="${VARIANCE_THRESHOLD:-1.0e-12}"
APPLY_CORR_FILTER="${APPLY_CORR_FILTER:-1}"
CORR_THRESHOLD="${CORR_THRESHOLD:-0.98}"

ALL_PARAMS=""
for idx in $(seq 0 13); do
  if [ -z "${ALL_PARAMS}" ]; then
    ALL_PARAMS="parm_${idx}"
  else
    ALL_PARAMS="${ALL_PARAMS},parm_${idx}"
  fi
done
CORE_PARAMS="parm_6,parm_9,parm_10,parm_12,parm_13"
ALL_SURFACE="PCT_SAND,PCT_CLAY,ORGANIC"
CORE_CLIM="FSDS_clim_mean,PRECTmms_clim_mean,RH_clim_seasonal_amp"

ALL_CLIM=""
for forcing_var in PRECTmms FSDS FLDS TBOT RH WIND PSRF; do
  for suffix in mean std min max seasonal_amp; do
    fname="${forcing_var}_clim_${suffix}"
    if [ -z "${ALL_CLIM}" ]; then
      ALL_CLIM="${fname}"
    else
      ALL_CLIM="${ALL_CLIM},${fname}"
    fi
  done
done

FEATURE_SET="all"
EXPLICIT_FEATURE_SUBSET=""
case "${VARIANT}" in
  all_control)
    ;;
  core_params_all_surface_all_clim)
    EXPLICIT_FEATURE_SUBSET="${CORE_PARAMS},${ALL_SURFACE},${ALL_CLIM}"
    ;;
  all_params_all_surface_core_clim)
    EXPLICIT_FEATURE_SUBSET="${ALL_PARAMS},${ALL_SURFACE},${CORE_CLIM}"
    ;;
  core_tri_group)
    EXPLICIT_FEATURE_SUBSET="${CORE_PARAMS},${ALL_SURFACE},${CORE_CLIM}"
    ;;
  *)
    echo "Unsupported VARIANT='${VARIANT}'" >&2
    echo "Supported: all_control | core_params_all_surface_all_clim | all_params_all_surface_core_clim | core_tri_group" >&2
    exit 2
    ;;
esac

RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
RUN_NAME="${RUN_NAME_BASE}_${VARIANT}"
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
TREE_STATE="clean"
if git -C "${OLMT_ROOT}" status --porcelain --untracked-files=all | rg -q '.'; then
  TREE_STATE="dirty"
fi
echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} script_path=${SCRIPT_PATH} script_sha256=${SCRIPT_SHA256} commit_hash=${GIT_COMMIT} tree_state=${TREE_STATE}"
echo "RUNTIME_CONFIG profile=iter6_feature_settle slurm_cpus=${SLURM_CPUS_PER_TASK:-unknown} n_jobs=${N_JOBS} pre_dispatch=${PRE_DISPATCH} omp=${OMP_NUM_THREADS} run_name=${RUN_NAME}"
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
if [ -n "${EXPLICIT_FEATURE_SUBSET}" ]; then
  EXTRA_FLAGS+=("--feature-subset" "${EXPLICIT_FEATURE_SUBSET}")
fi

/usr/bin/time -v python train_surrogate_spinup.py \
  --workdir "${OLMT_ROOT}" \
  --case "${CASE_LIST}" \
  --spinup-case "${SPINUP_CASE_LIST}" \
  --spinup-vars "${SPINUP_VARS}" \
  --surface-vars "${SURFACE_VARS}" \
  --forcing-vars "${FORCING_VARS}" \
  --model-type nn \
  --feature-set "${FEATURE_SET}" \
  --clim-feature-include "*" \
  --split-mode "${SPLIT_MODE}" \
  --train-fraction "${TRAIN_FRACTION}" \
  --split-random-state "${RANDOM_SEED}" \
  --clim-feature-mode "${CLIM_FEATURE_MODE}" \
  --permutation-repeats "${PERMUTATION_REPEATS}" \
  --quick-grid \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --pre-dispatch "${PRE_DISPATCH}" \
  --outputdir "${OUTPUTDIR}" \
  --run-name "${RUN_NAME}" \
  "${EXTRA_FLAGS[@]}"
