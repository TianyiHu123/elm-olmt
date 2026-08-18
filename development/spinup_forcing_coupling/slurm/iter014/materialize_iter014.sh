#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014
readonly SLURM_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter014"
readonly FORCING=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly JERC_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
readonly LEDGER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz
readonly CONTROL_POOL=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_pool.npz
readonly CONTROL_EVALUATION="${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter012/jerc_evaluation_result.json"
readonly EXPECTED_LEDGER_SHA256=25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d
readonly CONTROL_POOL_SHA256=32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96
readonly TARGET_SHA256=26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196
readonly FORCING_SHA256=8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e
readonly SPINUP_SHA256=1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023
readonly JERC_OBS_SHA256=a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f
readonly MODULE=micromamba/2.0.2-2
readonly ENV_NAME=OLMT_puma
readonly POOL_RULES=(rank_dominated hybrid_high_l_maximin)
readonly SEEDS=(9009 9010 9011)

test "$(pwd -P)" = "${REPO_ROOT}"
for required in \
  "${FORCING}" \
  "${SPINUP}" \
  "${JERC_OBS}" \
  "${JERC_CASE}" \
  "${LEDGER}" \
  "${CONTROL_POOL}" \
  "${CONTROL_EVALUATION}" \
  "${SLURM_DIR}/materialize_iter014.sh" \
  "${SLURM_DIR}/preflight_iter014.py" \
  "${SLURM_DIR}/preflight_iter014.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter014.slurm" \
  "${SLURM_DIR}/production_iter014.slurm" \
  "${SLURM_DIR}/evaluate_iter014.py" \
  "${SLURM_DIR}/evaluate_iter014.slurm" \
  "${SLURM_DIR}/aggregate_iter014.py" \
  "${SLURM_DIR}/aggregate_iter014.slurm" \
  "${SLURM_DIR}/validate_iter014_handoff.py" \
  "${SLURM_DIR}/validate_iter014_handoff.slurm"
do
  test -f "${required}"
done

if [[ -f "${OUTPUT_ROOT}/package_identity.env" ]]; then
  echo "MATERIALIZE_REFUSE output root already fully materialized: ${OUTPUT_ROOT}" >&2
  exit 1
fi
if [[ -e "${OUTPUT_ROOT}" ]] && [[ ! -f "${OUTPUT_ROOT}/.materialization_incomplete" ]]; then
  echo "MATERIALIZE_REFUSE output root exists without incomplete flag: ${OUTPUT_ROOT}" >&2
  exit 1
fi

mkdir -p "${OUTPUT_ROOT}"
touch "${OUTPUT_ROOT}/.materialization_incomplete"
mkdir -p \
  "${OUTPUT_ROOT}/preflight" \
  "${OUTPUT_ROOT}/evaluation" \
  "${OUTPUT_ROOT}/aggregate" \
  "${OUTPUT_ROOT}/handoff_validation"
for rule in "${POOL_RULES[@]}"; do
  mkdir -p \
    "${OUTPUT_ROOT}/pool_rebuild/${rule}" \
    "${OUTPUT_ROOT}/evaluation/${rule}"
  for seed in "${SEEDS[@]}"; do
    mkdir -p "${OUTPUT_ROOT}/production/${rule}/seed_${seed}"
  done
done

readonly SOURCE_MANIFEST="${OUTPUT_ROOT}/preflight/source_manifest.sha256"
readonly DEPENDENCY_MANIFEST="${OUTPUT_ROOT}/preflight/dependency_manifest.sha256"
sha256sum \
  "${REPO_ROOT}/model_ELM/coupling_pipeline.py" \
  "${REPO_ROOT}/initialize_pipeline.py" \
  "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  "${REPO_ROOT}/model_ELM/MCMC_forcing.py" \
  "${REPO_ROOT}/model_ELM/mcmc_geometry.py" \
  "${REPO_ROOT}/model_ELM/coupled_surrogate.py" \
  "${REPO_ROOT}/model_ELM/load_obs_nc.py" \
  "${REPO_ROOT}/model_ELM/surrogate_NN_Forcing.py" \
  "${REPO_ROOT}/model_ELM/MCMC.py" \
  "${REPO_ROOT}/model_ELM/mcmc_diagnostics.py" \
  "${REPO_ROOT}/model_ELM/forcing_surrogate_artifact.py" \
  "${REPO_ROOT}/model_ELM/spinup_surrogate_artifact.py" \
  "${REPO_ROOT}/model_ELM/surrogate_NN_Spinup.py" \
  "${SLURM_DIR}/materialize_iter014.sh" \
  "${SLURM_DIR}/preflight_iter014.py" \
  "${SLURM_DIR}/preflight_iter014.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter014.slurm" \
  "${SLURM_DIR}/production_iter014.slurm" \
  "${SLURM_DIR}/evaluate_iter014.py" \
  "${SLURM_DIR}/evaluate_iter014.slurm" \
  "${SLURM_DIR}/aggregate_iter014.py" \
  "${SLURM_DIR}/aggregate_iter014.slurm" \
  "${SLURM_DIR}/validate_iter014_handoff.py" \
  "${SLURM_DIR}/validate_iter014_handoff.slurm" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${SOURCE_MANIFEST}"

sha256sum \
  "${FORCING}" \
  "${SPINUP}" \
  "${JERC_OBS}" \
  "${JERC_CASE}" \
  "${LEDGER}" \
  "${CONTROL_POOL}" \
  "${CONTROL_EVALUATION}" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${DEPENDENCY_MANIFEST}"

test "$(sha256sum "${FORCING}" | awk '{print $1}')" = "${FORCING_SHA256}"
test "$(sha256sum "${SPINUP}" | awk '{print $1}')" = "${SPINUP_SHA256}"
test "$(sha256sum "${JERC_OBS}" | awk '{print $1}')" = "${JERC_OBS_SHA256}"
test "$(sha256sum "${LEDGER}" | awk '{print $1}')" = "${EXPECTED_LEDGER_SHA256}"
test "$(sha256sum "${CONTROL_POOL}" | awk '{print $1}')" = "${CONTROL_POOL_SHA256}"

readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly SUBMISSION_SCAFFOLD_MANIFEST="${OUTPUT_ROOT}/preflight/submission_scaffold.sha256"
: > "${SUBMISSION_SCAFFOLD_MANIFEST}"

write_submitter() {
  local run_dir="$1"
  local submitted_script="$2"
  local log_prefix="$3"
  local work_unit="$4"
  local max_attempts="$5"
  local config="${run_dir}/submission_config.env"
  local config_sha256
  local script_sha256
  config_sha256="$(sha256sum "${config}" | awk '{print $1}')"
  script_sha256="$(sha256sum "${run_dir}/${submitted_script}" | awk '{print $1}')"
  cat > "${run_dir}/submit.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
readonly RUN_DIR="${run_dir}"
readonly SUBMISSION_CONFIG="${config}"
readonly SUBMISSION_CONFIG_SHA256="${config_sha256}"
readonly SUBMITTED_SCRIPT_SHA256="${script_sha256}"
readonly WORK_UNIT="${work_unit}"
readonly MAX_ATTEMPTS="${max_attempts}"
cd "\${RUN_DIR}"
test "\$(pwd -P)" = "\${RUN_DIR}"
test "\$(sha256sum "\${SUBMISSION_CONFIG}" | awk '{print \$1}')" = "\${SUBMISSION_CONFIG_SHA256}"
test "\$(sha256sum "./${submitted_script}" | awk '{print \$1}')" = "\${SUBMITTED_SCRIPT_SHA256}"
attempt_number=1
retry_authorization_sha256=
prior_job_id=
retry_classification=
retry_terminal_state=
retry_terminal_exit_code=
if [[ -e "\${RUN_DIR}/submission_attempt_1.env" ]] \
  && [[ ! -e "\${RUN_DIR}/submission_receipt_1.env" ]]; then
  echo "SUBMISSION_REFUSE unreconciled first attempt" >&2
  exit 1
fi
if [[ -e "\${RUN_DIR}/submission_receipt_1.env" ]]; then
  if [[ "\${MAX_ATTEMPTS}" -lt 2 ]]; then
    echo "SUBMISSION_REFUSE work unit has no retry authority" >&2
    exit 1
  fi
  attempt_number=2
  test "\${1:-}" = "--retry"
  test ! -e "\${RUN_DIR}/submission_attempt_2.env"
  test ! -e "\${RUN_DIR}/submission_receipt_2.env"
  readonly RETRY_AUTHORIZATION="\${RUN_DIR}/retry_authorization.env"
  test -f "\${RETRY_AUTHORIZATION}"
  unset PRIOR_JOB_ID PRIOR_RECEIPT_SHA256 CLASSIFICATION TERMINAL_STATE TERMINAL_EXIT_CODE
  set -a
  # shellcheck disable=SC1090
  source "\${RETRY_AUTHORIZATION}"
  set +a
  test "\${CLASSIFICATION}" = "scheduler_resource"
  test "\${PRIOR_JOB_ID}" = "\$(awk -F= '\$1 == "job_id" {print \$2}' "\${RUN_DIR}/submission_receipt_1.env")"
  test "\${PRIOR_RECEIPT_SHA256}" = "\$(sha256sum "\${RUN_DIR}/submission_receipt_1.env" | awk '{print \$1}')"
  case "\${TERMINAL_STATE}" in
    TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|CANCELLED) ;;
    *) echo "SUBMISSION_REFUSE retry state is not a terminal scheduler/resource failure" >&2; exit 1 ;;
  esac
  test -n "\${TERMINAL_EXIT_CODE}"
  test "\${TERMINAL_EXIT_CODE}" != "0:0"
  retry_authorization_sha256="\$(sha256sum "\${RETRY_AUTHORIZATION}" | awk '{print \$1}')"
  prior_job_id="\${PRIOR_JOB_ID}"
  retry_classification="\${CLASSIFICATION}"
  retry_terminal_state="\${TERMINAL_STATE}"
  retry_terminal_exit_code="\${TERMINAL_EXIT_CODE}"
elif [[ -n "\${1:-}" ]]; then
  echo "SUBMISSION_REFUSE retry requested without a prior receipt" >&2
  exit 1
fi
attempt_time="\$(date --iso-8601=seconds)"
attempt_tmp="\${RUN_DIR}/submission_attempt_\${attempt_number}.env.tmp"
attempt="\${RUN_DIR}/submission_attempt_\${attempt_number}.env"
receipt_tmp="\${RUN_DIR}/submission_receipt_\${attempt_number}.env.tmp"
receipt="\${RUN_DIR}/submission_receipt_\${attempt_number}.env"
test ! -e "\${attempt_tmp}"
test ! -e "\${attempt}"
test ! -e "\${receipt_tmp}"
test ! -e "\${receipt}"
{
  echo "state=submitting"
  echo "package_id=iter014"
  echo "work_unit=\${WORK_UNIT}"
  echo "attempt_number=\${attempt_number}"
  echo "retry_authorization_sha256=\${retry_authorization_sha256}"
  echo "prior_job_id=\${prior_job_id}"
  echo "retry_classification=\${retry_classification}"
  echo "retry_terminal_state=\${retry_terminal_state}"
  echo "retry_terminal_exit_code=\${retry_terminal_exit_code}"
  echo "submission_time=\${attempt_time}"
  echo "run_dir=\${RUN_DIR}"
  echo "submission_config=\${SUBMISSION_CONFIG}"
  echo "submission_config_sha256=\${SUBMISSION_CONFIG_SHA256}"
  echo "submitted_script=\${RUN_DIR}/${submitted_script}"
  echo "submitted_script_sha256=\${SUBMITTED_SCRIPT_SHA256}"
  echo "stdout_path=${run_dir}/${log_prefix}_%j.out"
  echo "stderr_path=${run_dir}/${log_prefix}_%j.err"
} > "\${attempt_tmp}"
mv "\${attempt_tmp}" "\${attempt}"
job_id=\$(sbatch --parsable \
  --chdir="\${RUN_DIR}" \
  --output="${run_dir}/${log_prefix}_%j.out" \
  --error="${run_dir}/${log_prefix}_%j.err" \
  --export="ALL,SUBMISSION_CONFIG=\${SUBMISSION_CONFIG},SUBMISSION_CONFIG_SHA256=\${SUBMISSION_CONFIG_SHA256}" \
  "./${submitted_script}" </dev/null)
test -n "\${job_id}"
{
  echo "state=submitted"
  echo "package_id=iter014"
  echo "work_unit=\${WORK_UNIT}"
  echo "attempt_number=\${attempt_number}"
  echo "retry_authorization_sha256=\${retry_authorization_sha256}"
  echo "prior_job_id=\${prior_job_id}"
  echo "retry_classification=\${retry_classification}"
  echo "retry_terminal_state=\${retry_terminal_state}"
  echo "retry_terminal_exit_code=\${retry_terminal_exit_code}"
  echo "job_id=\${job_id}"
  echo "submission_time=\${attempt_time}"
  echo "run_dir=\${RUN_DIR}"
  echo "submission_config=\${SUBMISSION_CONFIG}"
  echo "submission_config_sha256=\${SUBMISSION_CONFIG_SHA256}"
  echo "submitted_script=\${RUN_DIR}/${submitted_script}"
  echo "submitted_script_sha256=\${SUBMITTED_SCRIPT_SHA256}"
  echo "stdout_path=${run_dir}/${log_prefix}_\${job_id}.out"
  echo "stderr_path=${run_dir}/${log_prefix}_\${job_id}.err"
} > "\${receipt_tmp}"
mv "\${receipt_tmp}" "\${receipt}"
echo "SUBMITTED job_id=\${job_id} run_dir=\${RUN_DIR}"
EOF
  chmod 750 "${run_dir}/submit.sh"
  sha256sum \
    "${config}" \
    "${run_dir}/${submitted_script}" \
    "${run_dir}/submit.sh" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
}

common_paths() {
  cat <<EOF
ITERATION_ID=iter014
PACKAGE_ID=iter014
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
OBSERVATION_PATH=${JERC_OBS}
CASES=JERC_ppe6_I20TRCNPRDCTCBC
SITE_NAME=JERC
LIKELIHOOD_RESOLUTION=hourly
LEDGER_PATH=${LEDGER}
EXPECTED_LEDGER_SHA256=${EXPECTED_LEDGER_SHA256}
CONTROL_POOL_PATH=${CONTROL_POOL}
CONTROL_POOL_SHA256=${CONTROL_POOL_SHA256}
TARGET_SHA256=${TARGET_SHA256}
CONTROL_EVALUATION=${CONTROL_EVALUATION}
HIGH_L_QUANTILE=0.90
EOF
}

# Preflight
cp "${SLURM_DIR}/preflight_iter014.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter014.slurm"
{
  common_paths
  cat <<EOF
STAGE=preflight
PREFLIGHT_OUTPUT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
} > "${OUTPUT_ROOT}/preflight/submission_config.env"
write_submitter "${OUTPUT_ROOT}/preflight" "submit_preflight_iter014.slurm" "preflight" "preflight" 1

# Pool rebuilds
for rule in "${POOL_RULES[@]}"; do
  rebuild_dir="${OUTPUT_ROOT}/pool_rebuild/${rule}"
  cp "${SLURM_DIR}/rebuild_pool_iter014.slurm" "${rebuild_dir}/submit_rebuild_pool_iter014.slurm"
  {
    common_paths
    cat <<EOF
STAGE=pool_rebuild
POOL_RULE=${rule}
REBUILD_OUTPUT=${rebuild_dir}
EOF
  } > "${rebuild_dir}/submission_config.env"
  write_submitter "${rebuild_dir}" "submit_rebuild_pool_iter014.slurm" "rebuild" "pool_rebuild_${rule}" 1
done

# Production
for rule in "${POOL_RULES[@]}"; do
  for seed in "${SEEDS[@]}"; do
    production_dir="${OUTPUT_ROOT}/production/${rule}/seed_${seed}"
    cp "${SLURM_DIR}/production_iter014.slurm" "${production_dir}/submit_production_iter014.slurm"
    {
      common_paths
      cat <<EOF
STAGE=production
POOL_RULE=${rule}
SEED=${seed}
POOL_PATH=${OUTPUT_ROOT}/pool_rebuild/${rule}/artifacts/candidate_pool.npz
PRODUCTION_DIR=${production_dir}
EOF
    } > "${production_dir}/submission_config.env"
    write_submitter "${production_dir}" "submit_production_iter014.slurm" "production" "production_${rule}_${seed}" 2
  done
done

# Evaluation (both pool rules in one job)
cp "${SLURM_DIR}/evaluate_iter014.slurm" "${OUTPUT_ROOT}/evaluation/submit_evaluate_iter014.slurm"
{
  common_paths
  cat <<EOF
STAGE=evaluation
PRODUCTION_ROOT=${OUTPUT_ROOT}/production
POOL_REBUILD_ROOT=${OUTPUT_ROOT}/pool_rebuild
EVALUATION_ROOT=${OUTPUT_ROOT}/evaluation
PREFLIGHT_RESULT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
} > "${OUTPUT_ROOT}/evaluation/submission_config.env"
write_submitter "${OUTPUT_ROOT}/evaluation" "submit_evaluate_iter014.slurm" "evaluate" "evaluate" 1

# Aggregate
cp "${SLURM_DIR}/aggregate_iter014.slurm" "${OUTPUT_ROOT}/aggregate/submit_aggregate_iter014.slurm"
{
  common_paths
  cat <<EOF
STAGE=aggregate
EVALUATION_ROOT=${OUTPUT_ROOT}/evaluation
AGGREGATE_OUTPUT=${OUTPUT_ROOT}/aggregate/result
SUMMARY_DIR=${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter014
EOF
} > "${OUTPUT_ROOT}/aggregate/submission_config.env"
write_submitter "${OUTPUT_ROOT}/aggregate" "submit_aggregate_iter014.slurm" "aggregate" "aggregate" 1

# Handoff validation
cp "${SLURM_DIR}/validate_iter014_handoff.slurm" "${OUTPUT_ROOT}/handoff_validation/submit_validate_iter014_handoff.slurm"
{
  common_paths
  cat <<EOF
STAGE=handoff_validation
AGGREGATE_RESULT=${OUTPUT_ROOT}/aggregate/result/aggregate_result.json
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
EOF
} > "${OUTPUT_ROOT}/handoff_validation/submission_config.env"
write_submitter "${OUTPUT_ROOT}/handoff_validation" "submit_validate_iter014_handoff.slurm" "handoff" "handoff_validation" 1

cat > "${OUTPUT_ROOT}/accounting.csv" <<EOF
package_id,work_unit,job_id,state,exit_code,classification,run_dir,elapsed,maxrss
EOF

{
  echo "schema=spinup-forcing-coupling-iter014-package-v1"
  echo "repository_commit=${COMMIT}"
  echo "source_manifest_sha256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "dependency_manifest_sha256=$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
  echo "submission_scaffold_sha256=$(sha256sum "${SUBMISSION_SCAFFOLD_MANIFEST}" | awk '{print $1}')"
  echo "ledger_sha256=${EXPECTED_LEDGER_SHA256}"
  echo "control_pool_sha256=${CONTROL_POOL_SHA256}"
  echo "target_sha256=${TARGET_SHA256}"
  echo "output_root=${OUTPUT_ROOT}"
} > "${OUTPUT_ROOT}/package_identity.env"

rm -f "${OUTPUT_ROOT}/.materialization_incomplete"
echo "MATERIALIZE_PASS output_root=${OUTPUT_ROOT} commit=${COMMIT}"
