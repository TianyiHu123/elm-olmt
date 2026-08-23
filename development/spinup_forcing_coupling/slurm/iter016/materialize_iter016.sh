#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016
readonly ITER015_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015
readonly SLURM_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016"
readonly TOOLS_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/tools"
readonly SUMMARY_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter016"
readonly FORCING=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly ABBY_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc
readonly JERC_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc
readonly ABBY_CASE="${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl"
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
readonly ABBY_LEDGER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/abby/artifacts/candidate_ledger.npz
readonly JERC_LEDGER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz
readonly ABBY_POOL_REFERENCE="${ITER015_ROOT}/pool_rebuild/abby/artifacts/candidate_pool.npz"
readonly JERC_POOL_REFERENCE="${ITER015_ROOT}/pool_rebuild/jerc/artifacts/candidate_pool.npz"
readonly FORCING_SHA256=8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e
readonly SPINUP_SHA256=1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023
readonly ABBY_OBS_SHA256=e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2
readonly JERC_OBS_SHA256=a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f
readonly ABBY_LEDGER_SHA256=ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b
readonly JERC_LEDGER_SHA256=25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d
readonly ABBY_POOL_SHA256=3627bb1df152e2f4356787a6634c96dfe533bc2ca55a30a7aa90fc4d9fd50592
readonly JERC_POOL_SHA256=40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df
readonly MODULE=micromamba/2.0.2-2
readonly ENV_NAME=OLMT_puma
readonly SEEDS=(9009 9010 9011 9012 9013 9014 9015 9016 9017)

test "$(pwd -P)" = "${REPO_ROOT}"
for required in \
  "${FORCING}" "${SPINUP}" "${ABBY_OBS}" "${JERC_OBS}" "${ABBY_CASE}" "${JERC_CASE}" \
  "${ABBY_LEDGER}" "${JERC_LEDGER}" "${ABBY_POOL_REFERENCE}" "${JERC_POOL_REFERENCE}" \
  "${SLURM_DIR}/materialize_iter016.sh" \
  "${SLURM_DIR}/preflight_iter016.py" "${SLURM_DIR}/preflight_iter016.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter016.slurm" "${SLURM_DIR}/production_array_iter016.slurm" \
  "${SLURM_DIR}/analyze_iter016.py" "${SLURM_DIR}/analyze_iter016.slurm" \
  "${SLURM_DIR}/validate_iter016_handoff.py" "${SLURM_DIR}/validate_iter016_handoff.slurm"
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

mkdir -p "${OUTPUT_ROOT}" "${OUTPUT_ROOT}/preflight" "${OUTPUT_ROOT}/analysis" "${SUMMARY_DIR}"
touch "${OUTPUT_ROOT}/.materialization_incomplete"
mkdir -p "${OUTPUT_ROOT}/pool_rebuild/abby" "${OUTPUT_ROOT}/pool_rebuild/jerc"
for seed in "${SEEDS[@]}"; do
  mkdir -p "${OUTPUT_ROOT}/production/abby/daily_0.50/seed_${seed}"
  mkdir -p "${OUTPUT_ROOT}/production/jerc/hourly_0.75/seed_${seed}"
done
mkdir -p "${OUTPUT_ROOT}/production/abby" "${OUTPUT_ROOT}/production/jerc"

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
  "${TOOLS_DIR}/ensemble_common.py" \
  "${TOOLS_DIR}/ensemble_seed_health.py" \
  "${TOOLS_DIR}/ensemble_map_inventory.py" \
  "${TOOLS_DIR}/ensemble_equifinality_diagnostics.py" \
  "${TOOLS_DIR}/plot_ensemble_sr_overlay.py" \
  "${TOOLS_DIR}/plot_ensemble_physical_corner.py" \
  "${TOOLS_DIR}/fixed_length_mcmc_diagnostics.py" \
  "${TOOLS_DIR}/plot_physical_corner.py" \
  "${SLURM_DIR}/materialize_iter016.sh" \
  "${SLURM_DIR}/preflight_iter016.py" "${SLURM_DIR}/preflight_iter016.slurm" \
  "${SLURM_DIR}/rebuild_pool_iter016.slurm" "${SLURM_DIR}/production_array_iter016.slurm" \
  "${SLURM_DIR}/analyze_iter016.py" "${SLURM_DIR}/analyze_iter016.slurm" \
  "${SLURM_DIR}/validate_iter016_handoff.py" "${SLURM_DIR}/validate_iter016_handoff.slurm" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${SOURCE_MANIFEST}"

sha256sum \
  "${FORCING}" "${SPINUP}" "${ABBY_OBS}" "${JERC_OBS}" "${ABBY_CASE}" "${JERC_CASE}" \
  "${ABBY_LEDGER}" "${JERC_LEDGER}" "${ABBY_POOL_REFERENCE}" "${JERC_POOL_REFERENCE}" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${DEPENDENCY_MANIFEST}"

test "$(sha256sum "${FORCING}" | awk '{print $1}')" = "${FORCING_SHA256}"
test "$(sha256sum "${SPINUP}" | awk '{print $1}')" = "${SPINUP_SHA256}"
test "$(sha256sum "${ABBY_OBS}" | awk '{print $1}')" = "${ABBY_OBS_SHA256}"
test "$(sha256sum "${JERC_OBS}" | awk '{print $1}')" = "${JERC_OBS_SHA256}"
test "$(sha256sum "${ABBY_LEDGER}" | awk '{print $1}')" = "${ABBY_LEDGER_SHA256}"
test "$(sha256sum "${JERC_LEDGER}" | awk '{print $1}')" = "${JERC_LEDGER_SHA256}"
test "$(sha256sum "${ABBY_POOL_REFERENCE}" | awk '{print $1}')" = "${ABBY_POOL_SHA256}"
test "$(sha256sum "${JERC_POOL_REFERENCE}" | awk '{print $1}')" = "${JERC_POOL_SHA256}"

readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly SUBMISSION_SCAFFOLD_MANIFEST="${OUTPUT_ROOT}/preflight/submission_scaffold.sha256"
: > "${SUBMISSION_SCAFFOLD_MANIFEST}"

write_submitter() {
  local run_dir="$1" submitted_script="$2" log_prefix="$3" work_unit="$4" max_attempts="$5"
  local config_name="${6:-submission_config.env}" submitter_name="${7:-submit.sh}"
  local array_flag="${8:-}"
  local config="${run_dir}/${config_name}"
  local config_sha256 script_sha256
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
if [[ -e "\${RUN_DIR}/submission_attempt_1.env" ]] && [[ ! -e "\${RUN_DIR}/submission_receipt_1.env" ]]; then
  echo "SUBMISSION_REFUSE unreconciled first attempt" >&2
  exit 1
fi
if [[ -e "\${RUN_DIR}/submission_receipt_1.env" ]]; then
  test "\${MAX_ATTEMPTS}" -ge 2
  attempt_number=2
  test "\${1:-}" = "--retry"
fi
attempt_time="\$(date --iso-8601=seconds)"
attempt="\${RUN_DIR}/submission_attempt_\${attempt_number}.env"
receipt="\${RUN_DIR}/submission_receipt_\${attempt_number}.env"
{
  echo "state=submitting"
  echo "package_id=iter016"
  echo "work_unit=\${WORK_UNIT}"
  echo "attempt_number=\${attempt_number}"
  echo "submission_time=\${attempt_time}"
} > "\${attempt}"
job_id=\$(sbatch --parsable ${array_flag} \
  --chdir="\${RUN_DIR}" \
  --export="ALL,SUBMISSION_CONFIG=\${SUBMISSION_CONFIG},SUBMISSION_CONFIG_SHA256=\${SUBMISSION_CONFIG_SHA256}" \
  "./${submitted_script}" </dev/null)
test -n "\${job_id}"
{
  echo "state=submitted"
  echo "package_id=iter016"
  echo "work_unit=\${WORK_UNIT}"
  echo "attempt_number=\${attempt_number}"
  echo "job_id=\${job_id}"
  echo "submission_time=\${attempt_time}"
} > "\${receipt}"
echo "SUBMITTED job_id=\${job_id} work_unit=\${WORK_UNIT}"
EOF
  chmod 750 "${run_dir}/${submitter_name}"
  sha256sum "${config}" "${run_dir}/${submitted_script}" "${run_dir}/${submitter_name}" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
}

common_paths() {
  cat <<EOF
ITERATION_ID=iter016
PACKAGE_ID=iter016
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
ABBY_POOL_REFERENCE=${ABBY_POOL_REFERENCE}
JERC_POOL_REFERENCE=${JERC_POOL_REFERENCE}
HIGH_L_QUANTILE=0.90
POOL_RULE=hybrid_high_l_maximin
POOL_REUSE_POLICY=site_hybrid_pool_reuse_v1
OUTPUT_ROOT=${OUTPUT_ROOT}
EOF
}

cp "${SLURM_DIR}/preflight_iter016.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter016.slurm"
{
  common_paths
  cat <<EOF
STAGE=preflight
PREFLIGHT_OUTPUT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
} > "${OUTPUT_ROOT}/preflight/submission_config.env"
write_submitter "${OUTPUT_ROOT}/preflight" "submit_preflight_iter016.slurm" "preflight" "preflight" 2

rebuild_site() {
  local site="$1" ledger_path="$2" ledger_sha="$3" obs_path="$4" ledger_resolution="$5"
  local expected_pool="$6" case_name="$7"
  local rebuild_dir="${OUTPUT_ROOT}/pool_rebuild/${site,,}"
  cp "${SLURM_DIR}/rebuild_pool_iter016.slurm" "${rebuild_dir}/submit_rebuild_pool_iter016.slurm"
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
  write_submitter "${rebuild_dir}" "submit_rebuild_pool_iter016.slurm" "rebuild" "pool_rebuild_${site,,}" 2
}

rebuild_site ABBY "${ABBY_LEDGER}" "${ABBY_LEDGER_SHA256}" "${ABBY_OBS}" daily "${ABBY_POOL_SHA256}" ABBY_ppe6_I20TRCNPRDCTCBC
rebuild_site JERC "${JERC_LEDGER}" "${JERC_LEDGER_SHA256}" "${JERC_OBS}" hourly "${JERC_POOL_SHA256}" JERC_ppe6_I20TRCNPRDCTCBC

production_array_site() {
  local site="$1" site_lower="$2" config_dir="$3" resolution="$4" scale="$5" obs_path="$6" case_name="$7"
  local array_dir="${OUTPUT_ROOT}/production/${site_lower}"
  cp "${SLURM_DIR}/production_array_iter016.slurm" "${array_dir}/submit_production_array_iter016.slurm"
  {
    common_paths
    cat <<EOF
STAGE=production
SITE_NAME=${site}
SITE_LOWER=${site_lower}
CONFIG_DIR=${config_dir}
CASES=${case_name}
OBSERVATION_PATH=${obs_path}
LIKELIHOOD_RESOLUTION=${resolution}
DE_MOVE_SCALE=${scale}
POOL_PATH=${OUTPUT_ROOT}/pool_rebuild/${site_lower}/artifacts/candidate_pool.npz
EOF
  } > "${array_dir}/submission_config.env"
  write_submitter "${array_dir}" "submit_production_array_iter016.slurm" "production" "production_array_${site_lower}" 2 "" "submit.sh" "--array=0-8"
}

production_array_site ABBY abby daily_0.50 daily 0.50 "${ABBY_OBS}" ABBY_ppe6_I20TRCNPRDCTCBC
production_array_site JERC jerc hourly_0.75 hourly 0.75 "${JERC_OBS}" JERC_ppe6_I20TRCNPRDCTCBC

cp "${SLURM_DIR}/analyze_iter016.slurm" "${OUTPUT_ROOT}/analysis/submit_analyze_iter016.slurm"
{
  common_paths
  cat <<EOF
STAGE=analysis
ANALYSIS_OUTPUT=${OUTPUT_ROOT}/analysis
SUMMARY_DIR=${SUMMARY_DIR}
EOF
} > "${OUTPUT_ROOT}/analysis/submission_config.env"
write_submitter "${OUTPUT_ROOT}/analysis" "submit_analyze_iter016.slurm" "analysis" "analysis" 2

cp "${SLURM_DIR}/validate_iter016_handoff.slurm" "${OUTPUT_ROOT}/analysis/submit_validate_iter016_handoff.slurm"
{
  common_paths
  cat <<EOF
STAGE=handoff_validation
AGGREGATE_RESULT=${OUTPUT_ROOT}/analysis/aggregate_result.json
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
EOF
} > "${OUTPUT_ROOT}/analysis/handoff_submission_config.env"
write_submitter "${OUTPUT_ROOT}/analysis" "submit_validate_iter016_handoff.slurm" "handoff_validate" "handoff_validation" 2 "handoff_submission_config.env" "submit_handoff.sh"

cat > "${OUTPUT_ROOT}/accounting.csv" <<EOF
package_id,work_unit,job_id,state,exit_code,classification,run_dir,elapsed,maxrss
EOF

{
  echo "schema=spinup-forcing-coupling-iter016-package-v1"
  echo "repository_commit=${COMMIT}"
  echo "source_manifest_sha256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "dependency_manifest_sha256=$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
  echo "submission_scaffold_sha256=$(sha256sum "${SUBMISSION_SCAFFOLD_MANIFEST}" | awk '{print $1}')"
  echo "output_root=${OUTPUT_ROOT}"
  echo "pool_reuse_policy=site_hybrid_pool_reuse_v1"
  echo "seeds=${SEEDS[*]}"
} > "${OUTPUT_ROOT}/package_identity.env"

rm -f "${OUTPUT_ROOT}/.materialization_incomplete"
echo "MATERIALIZE_PASS output_root=${OUTPUT_ROOT} commit=${COMMIT}"
