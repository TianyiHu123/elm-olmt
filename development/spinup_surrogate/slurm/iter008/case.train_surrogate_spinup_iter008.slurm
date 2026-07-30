#!/bin/bash -e
# Canonical Puma iter008 script.  Submit only a variant-local self-describing copy.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter008
#SBATCH --array=1-5

set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ITERATION_RECORD="${REPO_ROOT}/development/spinup_surrogate/iterations/iter008.md"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly CASE_LIST=ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC
readonly FEATURE_SUBSET=parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp

test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${ITERATION_RECORD}"
test -d "${OUTPUT_ROOT}/UQ_output"
readonly SUBMISSION_CONFIG="${SUBMISSION_CONFIG:?Set variant-local SUBMISSION_CONFIG}"
test -f "${SUBMISSION_CONFIG}"
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
readonly VARIANT="${VARIANT:?Variant config must set VARIANT}"
readonly RUN_NAME="spinup_surrogate_iter008_${VARIANT}"
readonly RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
readonly N_JOBS="${N_JOBS:-4}"
readonly PRE_DISPATCH="${PRE_DISPATCH:-n_jobs}"
readonly JOB_CACHE_DIR="${OUTPUT_ROOT}/UQ_output/.runtime_cache/iter008/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${JOB_CACHE_DIR}"
export XDG_CACHE_HOME="${JOB_CACHE_DIR}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
cd "${REPO_ROOT}"
echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} config_sha256=$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}') commit=$(git rev-parse HEAD)"
module load micromamba
cmd=(micromamba run -n OLMT_puma python "${REPO_ROOT}/train_surrogate_spinup.py"
  --workdir "${REPO_ROOT}" --case "${CASE_LIST}" --spinup-case "${CASE_LIST}"
  --spinup-vars TOTSOMC,TOTSOMN --surface-vars PCT_SAND,PCT_CLAY,ORGANIC
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF --model-type nn --feature-set all
  --clim-feature-include '*' --feature-subset "${FEATURE_SUBSET}"
  --feature-subset-policy "${FEATURE_SUBSET_POLICY}" --split-mode by_member --train-fraction 0.8
  --split-random-state "${RANDOM_SEED}" --clim-feature-mode compact --permutation-repeats 8
  --cv-folds 3 --n-jobs "${N_JOBS}" --pre-dispatch "${PRE_DISPATCH}"
  --mlp-hidden-layer-sizes "${MLP_HIDDEN_LAYER_SIZES}" --mlp-activation "${MLP_ACTIVATION}"
  --mlp-solver "${MLP_SOLVER}" --mlp-alpha "${MLP_ALPHA}" --mlp-learning-rate-init "${MLP_LEARNING_RATE_INIT}"
  --stats-only --stats-run-id "seed${RANDOM_SEED}" --outputdir "${OUTPUT_ROOT}" --run-name "${RUN_NAME}")
if [ "${APPLY_CORR_FILTER}" = true ]; then cmd+=(--apply-corr-filter --corr-threshold "${CORR_THRESHOLD}"); fi
"${cmd[@]}"
