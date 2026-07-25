#!/bin/bash -e
# Canonical Puma iter010 script. Submit only a variant-local self-describing copy.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter010
#SBATCH --array=1-100
set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ITERATION_RECORD="${REPO_ROOT}/development/spinup_surrogate/iterations/iter010.md"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_surrogate/slurm/iter010/case.train_surrogate_spinup_iter010.slurm"
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter010/iter010_variants.tsv"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly CASE_LIST=ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC
readonly FULL45=parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp
readonly DROP32=parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp
test -f "${REPO_ROOT}/train_surrogate_spinup.py"; test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"; test -f "${REPO_ROOT}/development/hpc/puma.md"; test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"; test -f "${ITERATION_RECORD}"; test -f "${CANONICAL_SCRIPT}"; test -f "${MANIFEST}"; test -d "${OUTPUT_ROOT}/UQ_output"
readonly SUBMISSION_CONFIG="${SUBMISSION_CONFIG:?Set variant-local SUBMISSION_CONFIG}"; test -f "${SUBMISSION_CONFIG}"
mapfile -t config_lines < "${SUBMISSION_CONFIG}"; test "${#config_lines[@]}" = 7
[[ "${config_lines[0]}" == VARIANT=* && "${config_lines[1]}" == MLP_ALPHA=* && "${config_lines[2]}" == FEATURE_POLICY=* && "${config_lines[3]}" == FORCING_VARS=* && "${config_lines[4]}" == FEATURE_SUBSET_POLICY=* && "${config_lines[5]}" == APPLY_CORR_FILTER=* && "${config_lines[6]}" == CORR_THRESHOLD=* ]]
readonly VARIANT="${config_lines[0]#VARIANT=}" MLP_ALPHA="${config_lines[1]#MLP_ALPHA=}" FEATURE_POLICY="${config_lines[2]#FEATURE_POLICY=}" FORCING_VARS="${config_lines[3]#FORCING_VARS=}" FEATURE_SUBSET_POLICY="${config_lines[4]#FEATURE_SUBSET_POLICY=}" APPLY_CORR_FILTER="${config_lines[5]#APPLY_CORR_FILTER=}" CORR_THRESHOLD="${config_lines[6]#CORR_THRESHOLD=}"
readonly LOCK_MATCH_COUNT="$(awk -F '\t' -v v="${VARIANT}" -v a="${MLP_ALPHA}" -v p="${FEATURE_POLICY}" -v f="${FORCING_VARS}" -v s="${FEATURE_SUBSET_POLICY}" -v c="${APPLY_CORR_FILTER}" -v t="${CORR_THRESHOLD}" 'NR>1 && $1==v && $2==a && $3==p && $4==f && $5==s && $6==c && $7==t {n++} END {print n+0}' "${MANIFEST}")"; test "${LOCK_MATCH_COUNT}" = 1
case "${FEATURE_POLICY}" in full45|corr080_prioritydrop) readonly FEATURE_SUBSET="${FULL45}";; drop_flds_wind_psrf) readonly FEATURE_SUBSET="${DROP32}";; *) exit 2;; esac
readonly RUN_NAME="spinup_surrogate_iter010_${VARIANT}"
readonly RUN_DIR="${OUTPUT_ROOT}/UQ_output/${RUN_NAME}"
readonly SUBMITTED_SCRIPT="${RUN_DIR}/submit_${VARIANT}.slurm"
test "$(pwd -P)" = "${RUN_DIR}"; test "${SUBMISSION_CONFIG}" = "${RUN_DIR}/submission_config.env"; test -f "${SUBMITTED_SCRIPT}"; cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
readonly RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID)) N_JOBS=4 PRE_DISPATCH=n_jobs JOB_CACHE_DIR="${OUTPUT_ROOT}/UQ_output/.runtime_cache/iter010/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${JOB_CACHE_DIR}"; export XDG_CACHE_HOME="${JOB_CACHE_DIR}"; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
cd "${REPO_ROOT}"; echo "PROVENANCE variant=${VARIANT} seed=${RANDOM_SEED} config_sha256=$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}') canonical_sha256=$(sha256sum "${CANONICAL_SCRIPT}" | awk '{print $1}') commit=$(git rev-parse HEAD)"
module load micromamba
cmd=(micromamba run -n OLMT_puma python "${REPO_ROOT}/train_surrogate_spinup.py" --workdir "${REPO_ROOT}" --case "${CASE_LIST}" --spinup-case "${CASE_LIST}" --spinup-vars TOTSOMC,TOTSOMN --surface-vars PCT_SAND,PCT_CLAY,ORGANIC --forcing-vars "${FORCING_VARS}" --model-type nn --feature-set all --clim-feature-include '*' --feature-subset "${FEATURE_SUBSET}" --feature-subset-policy "${FEATURE_SUBSET_POLICY}" --split-mode by_member --train-fraction 0.8 --split-random-state "${RANDOM_SEED}" --clim-feature-mode compact --permutation-repeats 8 --cv-folds 3 --n-jobs "${N_JOBS}" --pre-dispatch "${PRE_DISPATCH}" --mlp-hidden-layer-sizes 32 --mlp-activation tanh --mlp-solver lbfgs --mlp-alpha "${MLP_ALPHA}" --mlp-learning-rate-init 1e-3 --stats-only --stats-run-id "seed${RANDOM_SEED}" --outputdir "${OUTPUT_ROOT}" --run-name "${RUN_NAME}")
if [ "${APPLY_CORR_FILTER}" = true ]; then cmd+=(--apply-corr-filter --corr-threshold "${CORR_THRESHOLD}"); fi
"${cmd[@]}"
