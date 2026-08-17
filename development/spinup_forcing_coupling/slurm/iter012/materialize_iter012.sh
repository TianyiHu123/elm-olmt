#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1
readonly LEGACY_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012
readonly FORCING=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly OBS_ROOT=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4
readonly ABBY_OBS="${OBS_ROOT}/ABBY/ABBY_cdo_merge.nc"
readonly JERC_OBS="${OBS_ROOT}/JERC/JERC_cdo_merge.nc"
readonly ABBY_CASE="${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl"
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
readonly MODULE=micromamba/2.0.2-2
readonly ENV_NAME=OLMT_puma

test "$(pwd -P)" = "${REPO_ROOT}"
for required in \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${LEGACY_ROOT}/preflight/source_manifest.sha256" \
  "${LEGACY_ROOT}/preflight/dependency_manifest.sha256"
do
  test -f "${required}"
done
if [[ -e "${OUTPUT_ROOT}" ]]; then
  if [[ -f "${OUTPUT_ROOT}/.materialization_incomplete" ]] \
    && [[ ! -f "${OUTPUT_ROOT}/package_identity.env" ]]; then
    rm -rf "${OUTPUT_ROOT}"
  else
    echo "MATERIALIZE_REFUSE output root already exists: ${OUTPUT_ROOT}" >&2
    exit 1
  fi
fi

mkdir -p "${OUTPUT_ROOT}"
touch "${OUTPUT_ROOT}/.materialization_incomplete"
mkdir -p \
  "${OUTPUT_ROOT}/preflight" \
  "${OUTPUT_ROOT}/initialization/abby" \
  "${OUTPUT_ROOT}/initialization/jerc" \
  "${OUTPUT_ROOT}/pool_validation" \
  "${OUTPUT_ROOT}/evaluation/canonical/abby" \
  "${OUTPUT_ROOT}/evaluation/canonical/jerc" \
  "${OUTPUT_ROOT}/legacy_comparison/evaluation/abby" \
  "${OUTPUT_ROOT}/legacy_comparison/evaluation/jerc" \
  "${OUTPUT_ROOT}/aggregate/result" \
  "${OUTPUT_ROOT}/handoff_validation"
for site in abby jerc; do
  for seed in 9009 9010 9011; do
    mkdir -p "${OUTPUT_ROOT}/production/${site}/seed_${seed}"
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
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/materialize_iter012.sh" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/preflight_iter012.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/preflight_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/initialize_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/production_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_pools_iter012.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_pools_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/aggregate_iter012.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/aggregate_iter012.slurm" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_iter012_handoff.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_iter012_handoff.slurm" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${SOURCE_MANIFEST}"
sha256sum \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${DEPENDENCY_MANIFEST}"

readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly LEGACY_COMMIT=6246e920c6329ee28bda4e813613628bbc3ac852
readonly LEGACY_SOURCE_MANIFEST="${LEGACY_ROOT}/preflight/source_manifest.sha256"
readonly LEGACY_DEPENDENCY_MANIFEST="${LEGACY_ROOT}/preflight/dependency_manifest.sha256"
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
  echo "package_id=general_pipeline_v2"
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
  echo "package_id=general_pipeline_v2"
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

cat > "${OUTPUT_ROOT}/preflight/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=preflight
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
PREFLIGHT_OUTPUT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
cp \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/preflight_iter012.slurm" \
  "${OUTPUT_ROOT}/preflight/submit_preflight_iter012.slurm"
write_submitter "${OUTPUT_ROOT}/preflight" "submit_preflight_iter012.slurm" "preflight" "v2_preflight" 1

for spec in \
  "ABBY daily 12012 abby ${ABBY_OBS}" \
  "JERC hourly 12013 jerc ${JERC_OBS}"
do
  read -r site resolution initialization_seed key observation_path <<< "${spec}"
  initialization_dir="${OUTPUT_ROOT}/initialization/${key}"
  cat > "${initialization_dir}/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=initialization
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
SITE_NAME=${site}
LIKELIHOOD_RESOLUTION=${resolution}
CASES=${site}_ppe6_I20TRCNPRDCTCBC
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
OBSERVATION_PATH=${observation_path}
INITIALIZATION_SEED=${initialization_seed}
INITIALIZATION_DIR=${initialization_dir}
EOF
  cp \
    "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/initialize_iter012.slurm" \
    "${initialization_dir}/submit_initialize_iter012.slurm"
  write_submitter "${initialization_dir}" "submit_initialize_iter012.slurm" "initialize" "v2_initialization_${key}" 2

  for seed in 9009 9010 9011; do
    production_dir="${OUTPUT_ROOT}/production/${key}/seed_${seed}"
    cat > "${production_dir}/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=production
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
SITE_NAME=${site}
LIKELIHOOD_RESOLUTION=${resolution}
SEED=${seed}
CASES=${site}_ppe6_I20TRCNPRDCTCBC
OBSERVATION_PATH=${observation_path}
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
POOL_PATH=${initialization_dir}/artifacts/candidate_pool.npz
PRODUCTION_DIR=${production_dir}
EOF
    cp \
      "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/production_iter012.slurm" \
      "${production_dir}/submit_production_iter012.slurm"
    write_submitter "${production_dir}" "submit_production_iter012.slurm" "production" "v2_production_${key}_${seed}" 2
  done
done

cat > "${OUTPUT_ROOT}/pool_validation/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=pool_validation
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
ABBY_POOL_DIR=${OUTPUT_ROOT}/initialization/abby/artifacts
JERC_POOL_DIR=${OUTPUT_ROOT}/initialization/jerc/artifacts
POOL_VALIDATION_OUTPUT=${OUTPUT_ROOT}/pool_validation/pool_validation_result.json
EOF
cp \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_pools_iter012.slurm" \
  "${OUTPUT_ROOT}/pool_validation/submit_validate_pools_iter012.slurm"
write_submitter "${OUTPUT_ROOT}/pool_validation" "submit_validate_pools_iter012.slurm" "pool" "v2_pool_validation" 2

for spec in \
  "ABBY daily abby ${ABBY_OBS}" \
  "JERC hourly jerc ${JERC_OBS}"
do
  read -r site resolution key observation_path <<< "${spec}"
  canonical_dir="${OUTPUT_ROOT}/evaluation/canonical/${key}"
  cat > "${canonical_dir}/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=evaluation
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
SITE_NAME=${site}
LIKELIHOOD_RESOLUTION=${resolution}
CASES=${site}_ppe6_I20TRCNPRDCTCBC
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
PRODUCTION_ROOT=${OUTPUT_ROOT}/production/${key}
POOL_PATH=${OUTPUT_ROOT}/initialization/${key}/artifacts/candidate_pool.npz
EVALUATION_DIR=${canonical_dir}
EVIDENCE_ROLE=canonical
ALLOW_MOVE_MISMATCH=false
TARGET_SCHEMA=coupled-target-v1
DAILY_MAP_SCHEMA=coupled-daily-map-v1
PRODUCTION_REPOSITORY_COMMIT=${COMMIT}
PRODUCTION_SOURCE_MANIFEST=${SOURCE_MANIFEST}
PRODUCTION_DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
EOF
  cp \
    "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.slurm" \
    "${canonical_dir}/submit_evaluate_iter012.slurm"
  write_submitter "${canonical_dir}" "submit_evaluate_iter012.slurm" "evaluate" "v2_evaluation_canonical_${key}" 2

  legacy_dir="${OUTPUT_ROOT}/legacy_comparison/evaluation/${key}"
  legacy_pool_dir="${LEGACY_ROOT}/initialization/jerc"
  if [[ "${site}" = "ABBY" ]]; then
    legacy_pool_dir="${LEGACY_ROOT}/initialization/abby_retry_23569844_revised"
  fi
  cat > "${legacy_dir}/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=evaluation
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
SITE_NAME=${site}
LIKELIHOOD_RESOLUTION=${resolution}
CASES=${site}_ppe6_I20TRCNPRDCTCBC
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
PRODUCTION_ROOT=${LEGACY_ROOT}/production/${key}
POOL_PATH=${legacy_pool_dir}/candidate_pool.npz
EVALUATION_DIR=${legacy_dir}
EVIDENCE_ROLE=legacy
ALLOW_MOVE_MISMATCH=true
TARGET_SCHEMA=spinup-forcing-coupling-iter012-target-v1
DAILY_MAP_SCHEMA=spinup-forcing-coupling-iter012-daily-map-v1
PRODUCTION_REPOSITORY_COMMIT=${LEGACY_COMMIT}
PRODUCTION_SOURCE_MANIFEST=${LEGACY_SOURCE_MANIFEST}
PRODUCTION_DEPENDENCY_MANIFEST=${LEGACY_DEPENDENCY_MANIFEST}
EOF
  cp \
    "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.slurm" \
    "${legacy_dir}/submit_evaluate_iter012.slurm"
  write_submitter "${legacy_dir}" "submit_evaluate_iter012.slurm" "evaluate" "v2_evaluation_legacy_${key}" 2
done

cat > "${OUTPUT_ROOT}/aggregate/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=aggregate
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
CANONICAL_ABBY_EVALUATION_DIR=${OUTPUT_ROOT}/evaluation/canonical/abby/artifacts
CANONICAL_JERC_EVALUATION_DIR=${OUTPUT_ROOT}/evaluation/canonical/jerc/artifacts
LEGACY_ABBY_EVALUATION_DIR=${OUTPUT_ROOT}/legacy_comparison/evaluation/abby/artifacts
LEGACY_JERC_EVALUATION_DIR=${OUTPUT_ROOT}/legacy_comparison/evaluation/jerc/artifacts
AGGREGATE_OUTPUT=${OUTPUT_ROOT}/aggregate/result
EOF
cp \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/aggregate_iter012.slurm" \
  "${OUTPUT_ROOT}/aggregate/submit_aggregate_iter012.slurm"
write_submitter "${OUTPUT_ROOT}/aggregate" "submit_aggregate_iter012.slurm" "aggregate" "v2_aggregate" 2

cat > "${OUTPUT_ROOT}/handoff_validation/submission_config.env" <<EOF
ITERATION_ID=iter012
PACKAGE_ID=general_pipeline_v2
STAGE=handoff_validation
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
AGGREGATE_RESULT=${OUTPUT_ROOT}/aggregate/result/aggregate_result.json
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
EOF
cp \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/validate_iter012_handoff.slurm" \
  "${OUTPUT_ROOT}/handoff_validation/submit_validate_iter012_handoff.slurm"
write_submitter "${OUTPUT_ROOT}/handoff_validation" "submit_validate_iter012_handoff.slurm" "handoff" "v2_handoff_validation" 2

{
  echo "schema=spinup-forcing-coupling-general-pipeline-package-v2"
  echo "repository_commit=${COMMIT}"
  echo "source_manifest_sha256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "dependency_manifest_sha256=$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
  echo "submission_scaffold_sha256=$(sha256sum "${SUBMISSION_SCAFFOLD_MANIFEST}" | awk '{print $1}')"
  echo "legacy_source_manifest_sha256=$(sha256sum "${LEGACY_SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "legacy_dependency_manifest_sha256=$(sha256sum "${LEGACY_DEPENDENCY_MANIFEST}" | awk '{print $1}')"
} > "${OUTPUT_ROOT}/package_identity.env"

rm "${OUTPUT_ROOT}/.materialization_incomplete"
echo "MATERIALIZE_PASS output_root=${OUTPUT_ROOT}"
