#!/bin/bash -e
#
# Canonical Puma iter007 fixed-feature MLP-tuning script.
# Submit one array per locked variant only after the iter007 pre-submit ledger is complete.
#
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter007_mlp
#SBATCH --array=1-5
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter007_%A_%a.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter007_%A_%a.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_surrogate/slurm/iter007/case.train_surrogate_spinup_iter007_mlp_tuning.slurm"
readonly ITERATION_RECORD="${REPO_ROOT}/development/spinup_surrogate/iterations/iter007.md"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly CASE_LIST=ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC
readonly FEATURE_SUBSET=parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp

test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${ITERATION_RECORD}"
test -f "${CANONICAL_SCRIPT}"
test -d "${OUTPUT_ROOT}/UQ_output"
cd "${REPO_ROOT}"

readonly VARIANT="${VARIANT:?Set one locked iter007 VARIANT before submission}"
readonly RUN_NAME="spinup_surrogate_iter007_${VARIANT}"
readonly N_JOBS="${N_JOBS:-4}"
readonly PRE_DISPATCH="${PRE_DISPATCH:-n_jobs}"
readonly PERMUTATION_REPEATS="${PERMUTATION_REPEATS:-8}"

MLP_HIDDEN_LAYER_SIZES=""
MLP_ACTIVATION=""
MLP_SOLVER=""
MLP_ALPHA=""
MLP_LEARNING_RATE_INIT=""
case "${VARIANT}" in
  s08_tanh_adam_a10_lr1e3) MLP_HIDDEN_LAYER_SIZES=8; MLP_ACTIVATION=tanh; MLP_SOLVER=adam; MLP_ALPHA=10; MLP_LEARNING_RATE_INIT=1e-3 ;;
  s16_tanh_adam_a50_lr1e3) MLP_HIDDEN_LAYER_SIZES=16; MLP_ACTIVATION=tanh; MLP_SOLVER=adam; MLP_ALPHA=50; MLP_LEARNING_RATE_INIT=1e-3 ;;
  s24_relu_adam_a50_lr5e4) MLP_HIDDEN_LAYER_SIZES=24; MLP_ACTIVATION=relu; MLP_SOLVER=adam; MLP_ALPHA=50; MLP_LEARNING_RATE_INIT=5e-4 ;;
  s32_tanh_lbfgs_a10_lr1e3) MLP_HIDDEN_LAYER_SIZES=32; MLP_ACTIVATION=tanh; MLP_SOLVER=lbfgs; MLP_ALPHA=10; MLP_LEARNING_RATE_INIT=1e-3 ;;
  d08_08_tanh_adam_a10_lr1e3) MLP_HIDDEN_LAYER_SIZES=8,8; MLP_ACTIVATION=tanh; MLP_SOLVER=adam; MLP_ALPHA=10; MLP_LEARNING_RATE_INIT=1e-3 ;;
  d16_08_tanh_adam_a50_lr1e3) MLP_HIDDEN_LAYER_SIZES=16,8; MLP_ACTIVATION=tanh; MLP_SOLVER=adam; MLP_ALPHA=50; MLP_LEARNING_RATE_INIT=1e-3 ;;
  d16_16_relu_adam_a50_lr5e4) MLP_HIDDEN_LAYER_SIZES=16,16; MLP_ACTIVATION=relu; MLP_SOLVER=adam; MLP_ALPHA=50; MLP_LEARNING_RATE_INIT=5e-4 ;;
  d32_16_tanh_adam_a100_lr1e3) MLP_HIDDEN_LAYER_SIZES=32,16; MLP_ACTIVATION=tanh; MLP_SOLVER=adam; MLP_ALPHA=100; MLP_LEARNING_RATE_INIT=1e-3 ;;
  *) echo "Unsupported locked VARIANT='${VARIANT}'" >&2; exit 2 ;;
esac

readonly RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
readonly START_EPOCH="$(date +%s)"
readonly START_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
trap 'rc=$?; end_epoch="$(date +%s)"; end_utc="$(date -u "+%Y-%m-%dT%H:%M:%SZ")"; echo "RUN_END_UTC=${end_utc} wall_seconds=$((end_epoch-START_EPOCH)) exit_code=${rc}"; if [ "${rc}" -ne 0 ]; then echo "FAIL_FAST_BLOCKED variant=${VARIANT} seed=${RANDOM_SEED} exit_code=${rc}" >&2; fi' EXIT

readonly JOB_CACHE_DIR="${OUTPUT_ROOT}/UQ_output/.runtime_cache/iter007/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${JOB_CACHE_DIR}"
export XDG_CACHE_HOME="${JOB_CACHE_DIR}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

readonly SCRIPT_SHA256="$(sha256sum "${CANONICAL_SCRIPT}" | awk '{print $1}')"
readonly GIT_COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
TREE_STATE=clean
if [ -n "$(git -C "${REPO_ROOT}" status --porcelain --untracked-files=all | sed -n '1p')" ]; then
  TREE_STATE=dirty
fi
echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} canonical_script=${CANONICAL_SCRIPT} script_sha256=${SCRIPT_SHA256} commit_hash=${GIT_COMMIT} tree_state=${TREE_STATE}"
echo "RUNTIME_CONFIG profile=puma_iter007_fixed_mlp slurm_cpus=${SLURM_CPUS_PER_TASK:-unknown} n_jobs=${N_JOBS} pre_dispatch=${PRE_DISPATCH} omp=${OMP_NUM_THREADS} run_name=${RUN_NAME}"
echo "CACHE_CONFIG xdg_cache_home=${XDG_CACHE_HOME}"
echo "MLP_CONFIG hidden_layer_sizes=${MLP_HIDDEN_LAYER_SIZES} activation=${MLP_ACTIVATION} solver=${MLP_SOLVER} alpha=${MLP_ALPHA} learning_rate_init=${MLP_LEARNING_RATE_INIT}"
echo "RUN_START_UTC=${START_UTC}"

module load micromamba
/usr/bin/time -v micromamba run -n OLMT_puma python "${REPO_ROOT}/train_surrogate_spinup.py" \
  --workdir "${REPO_ROOT}" \
  --case "${CASE_LIST}" \
  --spinup-case "${CASE_LIST}" \
  --spinup-vars TOTSOMC,TOTSOMN \
  --surface-vars PCT_SAND,PCT_CLAY,ORGANIC \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --model-type nn \
  --feature-set all \
  --clim-feature-include '*' \
  --feature-subset "${FEATURE_SUBSET}" \
  --split-mode by_member \
  --train-fraction 0.8 \
  --split-random-state "${RANDOM_SEED}" \
  --clim-feature-mode compact \
  --permutation-repeats "${PERMUTATION_REPEATS}" \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --pre-dispatch "${PRE_DISPATCH}" \
  --mlp-hidden-layer-sizes "${MLP_HIDDEN_LAYER_SIZES}" \
  --mlp-activation "${MLP_ACTIVATION}" \
  --mlp-solver "${MLP_SOLVER}" \
  --mlp-alpha "${MLP_ALPHA}" \
  --mlp-learning-rate-init "${MLP_LEARNING_RATE_INIT}" \
  --stats-only \
  --stats-run-id "seed${RANDOM_SEED}" \
  --outputdir "${OUTPUT_ROOT}" \
  --run-name "${RUN_NAME}"
