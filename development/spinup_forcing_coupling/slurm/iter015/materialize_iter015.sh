#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015
readonly SLURM_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter015"
readonly SUMMARY_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter015"
readonly FORCING=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly ABBY_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc
readonly JERC_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc
readonly ABBY_CASE="${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl"
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
readonly ABBY_LEDGER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/abby/artifacts/candidate_ledger.npz
readonly JERC_LEDGER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz
readonly JERC_HYBRID_REFERENCE=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014/pool_rebuild/hybrid_high_l_maximin/artifacts/candidate_pool.npz
readonly FORCING_SHA256=8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e
readonly SPINUP_SHA256=1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023
readonly ABBY_OBS_SHA256=e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2
readonly JERC_OBS_SHA256=a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f
readonly ABBY_LEDGER_SHA256=ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b
readonly JERC_LEDGER_SHA256=25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d
readonly JERC_HYBRID_SHA256=40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df
readonly MODULE=micromamba/2.0.2-2
readonly ENV_NAME=OLMT_puma
readonly SITES=(ABBY JERC)
readonly RESOLUTIONS=(hourly daily)
readonly SCALES=(0.50 0.75 1.00)
readonly SEEDS=(9009 9010 9011)

test "$(pwd -P)" = "${REPO_ROOT}"
for required in \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${ABBY_LEDGER}" \
  "${JERC_LEDGER}" \
  "${JERC_HYBRID_REFERENCE}" \
  "${SLURM_DIR}/materialize_iter015.sh" \
  "${SLURM_DIR}/preflight_iter015.py" \
  "${SLURM_DIR}/preflight_iter015.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter015.slurm" \
  "${SLURM_DIR}/production_iter015.slurm" \
  "${SLURM_DIR}/analyze_iter015.py" \
  "${SLURM_DIR}/analyze_iter015.slurm" \
  "${SLURM_DIR}/validate_iter015_handoff.py" \
  "${SLURM_DIR}/validate_iter015_handoff.slurm"
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
  "${OUTPUT_ROOT}/analysis" \
  "${SUMMARY_DIR}"
for site in "${SITES[@]}"; do
  mkdir -p "${OUTPUT_ROOT}/pool_rebuild/${site,,}"
  for resolution in "${RESOLUTIONS[@]}"; do
    for scale in "${SCALES[@]}"; do
      for seed in "${SEEDS[@]}"; do
        mkdir -p "${OUTPUT_ROOT}/production/${site,,}/${resolution}_${scale}/seed_${seed}"
      done
    done
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
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_init_cloud_overlay.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/fixed_length_mcmc_diagnostics.py" \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_physical_corner.py" \
  "${SLURM_DIR}/materialize_iter015.sh" \
  "${SLURM_DIR}/preflight_iter015.py" \
  "${SLURM_DIR}/preflight_iter015.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter015.slurm" \
  "${SLURM_DIR}/production_iter015.slurm" \
  "${SLURM_DIR}/analyze_iter015.py" \
  "${SLURM_DIR}/analyze_iter015.slurm" \
  "${SLURM_DIR}/validate_iter015_handoff.py" \
  "${SLURM_DIR}/validate_iter015_handoff.slurm" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${SOURCE_MANIFEST}"

sha256sum \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${ABBY_LEDGER}" \
  "${JERC_LEDGER}" \
  "${JERC_HYBRID_REFERENCE}" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${DEPENDENCY_MANIFEST}"

test "$(sha256sum "${FORCING}" | awk '{print $1}')" = "${FORCING_SHA256}"
test "$(sha256sum "${SPINUP}" | awk '{print $1}')" = "${SPINUP_SHA256}"
test "$(sha256sum "${ABBY_OBS}" | awk '{print $1}')" = "${ABBY_OBS_SHA256}"
test "$(sha256sum "${JERC_OBS}" | awk '{print $1}')" = "${JERC_OBS_SHA256}"
test "$(sha256sum "${ABBY_LEDGER}" | awk '{print $1}')" = "${ABBY_LEDGER_SHA256}"
test "$(sha256sum "${JERC_LEDGER}" | awk '{print $1}')" = "${JERC_LEDGER_SHA256}"
test "$(sha256sum "${JERC_HYBRID_REFERENCE}" | awk '{print $1}')" = "${JERC_HYBRID_SHA256}"

readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly SUBMISSION_SCAFFOLD_MANIFEST="${OUTPUT_ROOT}/preflight/submission_scaffold.sha256"
: > "${SUBMISSION_SCAFFOLD_MANIFEST}"

write_submitter() {
  local run_dir="$1"
  local submitted_script="$2"
  local log_prefix="$3"
  local work_unit="$4"
  local max_attempts="$5"
  local config_name="${6:-submission_config.env}"
  local submitter_name="${7:-submit.sh}"
  local config="${run_dir}/${config_name}"
  local config_sha256
  local script_sha256
  config_sha256="$(sha256sum "${config}" | awk '{print $1}')"
  script_sha256="$(sha256sum "${run_dir}/${submitted_script}" | awk '{print $1}')"
  cat > "${run_dir}/${submitter_name}" <<EOF
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
  echo "package_id=iter015"
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
  echo "package_id=iter015"
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
  chmod 750 "${run_dir}/${submitter_name}"
  sha256sum \
    "${config}" \
    "${run_dir}/${submitted_script}" \
    "${run_dir}/${submitter_name}" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
}

common_paths() {
  cat <<EOF
ITERATION_ID=iter015
PACKAGE_ID=iter015
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
ABBY_OBSERVATION=${ABBY_OBS}
JERC_OBSERVATION=${JERC_OBS}
ABBY_LEDGER=${ABBY_LEDGER}
JERC_LEDGER=${JERC_LEDGER}
JERC_HYBRID_REFERENCE=${JERC_HYBRID_REFERENCE}
HIGH_L_QUANTILE=0.90
POOL_RULE=hybrid_high_l_maximin
POOL_REUSE_POLICY=site_hybrid_pool_reuse_v1
OUTPUT_ROOT=${OUTPUT_ROOT}
EOF
}

cp "${SLURM_DIR}/preflight_iter015.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter015.slurm"
{
  common_paths
  cat <<EOF
STAGE=preflight
PREFLIGHT_OUTPUT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
} > "${OUTPUT_ROOT}/preflight/submission_config.env"
write_submitter "${OUTPUT_ROOT}/preflight" "submit_preflight_iter015.slurm" "preflight" "preflight" 2

for site in "${SITES[@]}"; do
  rebuild_dir="${OUTPUT_ROOT}/pool_rebuild/${site,,}"
  cp "${SLURM_DIR}/rebuild_pool_iter015.slurm" "${rebuild_dir}/submit_rebuild_pool_iter015.slurm"
  if [[ "${site}" == ABBY ]]; then
    ledger_path="${ABBY_LEDGER}"
    ledger_sha="${ABBY_LEDGER_SHA256}"
    obs_path="${ABBY_OBS}"
    ledger_resolution=daily
    expected_pool=
    case_name=ABBY_ppe6_I20TRCNPRDCTCBC
  else
    ledger_path="${JERC_LEDGER}"
    ledger_sha="${JERC_LEDGER_SHA256}"
    obs_path="${JERC_OBS}"
    ledger_resolution=hourly
    expected_pool="${JERC_HYBRID_SHA256}"
    case_name=JERC_ppe6_I20TRCNPRDCTCBC
  fi
  {
    common_paths
    cat <<EOF
STAGE=pool_rebuild
SITE_NAME=${site}
CASES=${case_name}
OBSERVATION_PATH=${obs_path}
LEDGER_PATH=${ledger_path}
EXPECTED_LEDGER_SHA256=${ledger_sha}
LEDGER_RESOLUTION=${ledger_resolution}
REBUILD_OUTPUT=${rebuild_dir}
EXPECTED_POOL_SHA256=${expected_pool}
EOF
  } > "${rebuild_dir}/submission_config.env"
  write_submitter "${rebuild_dir}" "submit_rebuild_pool_iter015.slurm" "rebuild" "pool_rebuild_${site,,}" 2
done

for site in "${SITES[@]}"; do
  if [[ "${site}" == ABBY ]]; then
    obs_path="${ABBY_OBS}"
    case_name=ABBY_ppe6_I20TRCNPRDCTCBC
  else
    obs_path="${JERC_OBS}"
    case_name=JERC_ppe6_I20TRCNPRDCTCBC
  fi
  pool_path="${OUTPUT_ROOT}/pool_rebuild/${site,,}/artifacts/candidate_pool.npz"
  for resolution in "${RESOLUTIONS[@]}"; do
    for scale in "${SCALES[@]}"; do
      for seed in "${SEEDS[@]}"; do
        production_dir="${OUTPUT_ROOT}/production/${site,,}/${resolution}_${scale}/seed_${seed}"
        cp "${SLURM_DIR}/production_iter015.slurm" "${production_dir}/submit_production_iter015.slurm"
        {
          common_paths
          cat <<EOF
STAGE=production
SITE_NAME=${site}
CASES=${case_name}
OBSERVATION_PATH=${obs_path}
LIKELIHOOD_RESOLUTION=${resolution}
DE_MOVE_SCALE=${scale}
SEED=${seed}
POOL_PATH=${pool_path}
PRODUCTION_DIR=${production_dir}
EOF
        } > "${production_dir}/submission_config.env"
        write_submitter \
          "${production_dir}" \
          "submit_production_iter015.slurm" \
          "production" \
          "production_${site,,}_${resolution}_${scale}_${seed}" \
          2
      done
    done
  done
done

cp "${SLURM_DIR}/analyze_iter015.slurm" "${OUTPUT_ROOT}/analysis/submit_analyze_iter015.slurm"
{
  common_paths
  cat <<EOF
STAGE=analysis
ANALYSIS_OUTPUT=${OUTPUT_ROOT}/analysis
SUMMARY_DIR=${SUMMARY_DIR}
EOF
} > "${OUTPUT_ROOT}/analysis/submission_config.env"
write_submitter "${OUTPUT_ROOT}/analysis" "submit_analyze_iter015.slurm" "analysis" "analysis" 2

cp "${SLURM_DIR}/validate_iter015_handoff.slurm" "${OUTPUT_ROOT}/analysis/submit_validate_iter015_handoff.slurm"
{
  common_paths
  cat <<EOF
STAGE=handoff_validation
AGGREGATE_RESULT=${OUTPUT_ROOT}/analysis/aggregate_result.json
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
EOF
} > "${OUTPUT_ROOT}/analysis/handoff_submission_config.env"
write_submitter \
  "${OUTPUT_ROOT}/analysis" \
  "submit_validate_iter015_handoff.slurm" \
  "handoff_validate" \
  "handoff_validation" \
  2 \
  "handoff_submission_config.env" \
  "submit_handoff.sh"

cat > "${OUTPUT_ROOT}/accounting.csv" <<EOF
package_id,work_unit,job_id,state,exit_code,classification,run_dir,elapsed,maxrss
EOF

{
  echo "schema=spinup-forcing-coupling-iter015-package-v1"
  echo "repository_commit=${COMMIT}"
  echo "source_manifest_sha256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "dependency_manifest_sha256=$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
  echo "submission_scaffold_sha256=$(sha256sum "${SUBMISSION_SCAFFOLD_MANIFEST}" | awk '{print $1}')"
  echo "output_root=${OUTPUT_ROOT}"
  echo "pool_reuse_policy=site_hybrid_pool_reuse_v1"
} > "${OUTPUT_ROOT}/package_identity.env"

rm -f "${OUTPUT_ROOT}/.materialization_incomplete"
echo "MATERIALIZE_PASS output_root=${OUTPUT_ROOT} commit=${COMMIT}"
