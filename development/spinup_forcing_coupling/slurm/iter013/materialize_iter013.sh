#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter013
readonly FORCING=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly I012_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1
readonly TIM_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter009_initialize
readonly ABBY_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc
readonly JERC_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc
readonly ABBY_CASE="${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl"
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
readonly MODULE=micromamba/2.0.2-2
readonly ENV_NAME=OLMT_puma
readonly SLURM_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter013"

test "$(pwd -P)" = "${REPO_ROOT}"
for required in \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${I012_ROOT}/initialization/abby/artifacts/candidate_pool.npz" \
  "${I012_ROOT}/initialization/jerc/artifacts/candidate_pool.npz" \
  "${TIM_ROOT}/abby_high_likelihood_pool.npz" \
  "${TIM_ROOT}/jerc_high_likelihood_pool.npz"
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
  "${OUTPUT_ROOT}/analysis/abby" \
  "${OUTPUT_ROOT}/analysis/jerc" \
  "${OUTPUT_ROOT}/aggregate" \
  "${OUTPUT_ROOT}/handoff_validation"

readonly SOURCE_MANIFEST="${OUTPUT_ROOT}/preflight/source_manifest.sha256"
readonly DEPENDENCY_MANIFEST="${OUTPUT_ROOT}/preflight/dependency_manifest.sha256"
sha256sum \
  "${REPO_ROOT}/model_ELM/coupling_pipeline.py" \
  "${REPO_ROOT}/initialize_pipeline.py" \
  "${REPO_ROOT}/model_ELM/MCMC_forcing.py" \
  "${REPO_ROOT}/model_ELM/coupled_surrogate.py" \
  "${REPO_ROOT}/model_ELM/load_obs_nc.py" \
  "${REPO_ROOT}/model_ELM/surrogate_NN_Forcing.py" \
  "${REPO_ROOT}/model_ELM/forcing_surrogate_artifact.py" \
  "${REPO_ROOT}/model_ELM/spinup_surrogate_artifact.py" \
  "${SLURM_DIR}/materialize_iter013.sh" \
  "${SLURM_DIR}/preflight_iter013.py" \
  "${SLURM_DIR}/preflight_iter013.slurm" \
  "${SLURM_DIR}/analyze_iter013.py" \
  "${SLURM_DIR}/analyze_iter013.slurm" \
  "${SLURM_DIR}/aggregate_iter013.py" \
  "${SLURM_DIR}/aggregate_iter013.slurm" \
  "${SLURM_DIR}/validate_iter013_handoff.py" \
  "${SLURM_DIR}/validate_iter013_handoff.slurm" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${SOURCE_MANIFEST}"

sha256sum \
  "${FORCING}" \
  "${SPINUP}" \
  "${ABBY_OBS}" \
  "${JERC_OBS}" \
  "${ABBY_CASE}" \
  "${JERC_CASE}" \
  "${I012_ROOT}/initialization/abby/artifacts/candidate_pool.npz" \
  "${I012_ROOT}/initialization/abby/artifacts/candidate_ledger.npz" \
  "${I012_ROOT}/initialization/jerc/artifacts/candidate_pool.npz" \
  "${I012_ROOT}/initialization/jerc/artifacts/candidate_ledger.npz" \
  "${TIM_ROOT}/abby_high_likelihood_pool.npz" \
  "${TIM_ROOT}/jerc_high_likelihood_pool.npz" \
  "${TIM_ROOT}/abby_high_seed9009.npz" \
  "${TIM_ROOT}/abby_high_seed9010.npz" \
  "${TIM_ROOT}/abby_high_seed9011.npz" \
  "${TIM_ROOT}/jerc_high_seed9009.npz" \
  "${TIM_ROOT}/jerc_high_seed9010.npz" \
  "${TIM_ROOT}/jerc_high_seed9011.npz" \
  "${I012_ROOT}/production/abby/seed_9009/selection_ledger.json" \
  "${I012_ROOT}/production/abby/seed_9010/selection_ledger.json" \
  "${I012_ROOT}/production/abby/seed_9011/selection_ledger.json" \
  "${I012_ROOT}/production/jerc/seed_9009/selection_ledger.json" \
  "${I012_ROOT}/production/jerc/seed_9010/selection_ledger.json" \
  "${I012_ROOT}/production/jerc/seed_9011/selection_ledger.json" \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" > "${DEPENDENCY_MANIFEST}"

readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly SUBMISSION_SCAFFOLD_MANIFEST="${OUTPUT_ROOT}/preflight/submission_scaffold.sha256"
: > "${SUBMISSION_SCAFFOLD_MANIFEST}"

common_paths() {
  cat <<EOF
ITERATION_ID=iter013
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${SOURCE_MANIFEST}
DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}
MICROMAMBA_MODULE=${MODULE}
MICROMAMBA_ENV=${ENV_NAME}
FORCING_ARTIFACT=${FORCING}
SPINUP_ARTIFACT=${SPINUP}
ABBY_POOL=${I012_ROOT}/initialization/abby/artifacts/candidate_pool.npz
ABBY_LEDGER=${I012_ROOT}/initialization/abby/artifacts/candidate_ledger.npz
JERC_POOL=${I012_ROOT}/initialization/jerc/artifacts/candidate_pool.npz
JERC_LEDGER=${I012_ROOT}/initialization/jerc/artifacts/candidate_ledger.npz
ABBY_TIM_POOL=${TIM_ROOT}/abby_high_likelihood_pool.npz
JERC_TIM_POOL=${TIM_ROOT}/jerc_high_likelihood_pool.npz
ABBY_SELECTION_9009=${I012_ROOT}/production/abby/seed_9009/selection_ledger.json
ABBY_SELECTION_9010=${I012_ROOT}/production/abby/seed_9010/selection_ledger.json
ABBY_SELECTION_9011=${I012_ROOT}/production/abby/seed_9011/selection_ledger.json
JERC_SELECTION_9009=${I012_ROOT}/production/jerc/seed_9009/selection_ledger.json
JERC_SELECTION_9010=${I012_ROOT}/production/jerc/seed_9010/selection_ledger.json
JERC_SELECTION_9011=${I012_ROOT}/production/jerc/seed_9011/selection_ledger.json
ABBY_TIM_BUNDLE_9009=${TIM_ROOT}/abby_high_seed9009.npz
ABBY_TIM_BUNDLE_9010=${TIM_ROOT}/abby_high_seed9010.npz
ABBY_TIM_BUNDLE_9011=${TIM_ROOT}/abby_high_seed9011.npz
JERC_TIM_BUNDLE_9009=${TIM_ROOT}/jerc_high_seed9009.npz
JERC_TIM_BUNDLE_9010=${TIM_ROOT}/jerc_high_seed9010.npz
JERC_TIM_BUNDLE_9011=${TIM_ROOT}/jerc_high_seed9011.npz
EOF
}

write_submitter() {
  local run_dir="$1"
  local submitted_script="$2"
  local work_unit="$3"
  local max_attempts="$4"
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
readonly SUBMITTED_SCRIPT="${run_dir}/${submitted_script}"
readonly WORK_UNIT="${work_unit}"
readonly MAX_ATTEMPTS="${max_attempts}"
cd "\${RUN_DIR}"
test "\$(sha256sum "\${SUBMISSION_CONFIG}" | awk '{print \$1}')" = "\${SUBMISSION_CONFIG_SHA256}"
test "\$(sha256sum "\${SUBMITTED_SCRIPT}" | awk '{print \$1}')" = "${script_sha256}"
attempt=1
if [[ -f "\${RUN_DIR}/submission_attempt.env" ]]; then
  # shellcheck disable=SC1091
  source "\${RUN_DIR}/submission_attempt.env"
  attempt=\$((ATTEMPT + 1))
fi
test "\${attempt}" -le "\${MAX_ATTEMPTS}"
export SUBMISSION_CONFIG SUBMISSION_CONFIG_SHA256
job_id="\$(sbatch --parsable "\${SUBMITTED_SCRIPT}" </dev/null)"
cat > "\${RUN_DIR}/submission_attempt.env" <<INNER
ATTEMPT=\${attempt}
INNER
cat > "\${RUN_DIR}/submission_receipt_\${attempt}.env" <<INNER
WORK_UNIT=\${WORK_UNIT}
JOB_ID=\${job_id}
ATTEMPT=\${attempt}
SUBMITTED_SCRIPT=\${SUBMITTED_SCRIPT}
SUBMITTED_SCRIPT_SHA256=${script_sha256}
SUBMISSION_CONFIG=\${SUBMISSION_CONFIG}
SUBMISSION_CONFIG_SHA256=\${SUBMISSION_CONFIG_SHA256}
INNER
echo "\${job_id}"
EOF
  chmod +x "${run_dir}/submit.sh"
  sha256sum "${run_dir}/submit.sh" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
  sha256sum "${config}" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
  sha256sum "${run_dir}/${submitted_script}" >> "${SUBMISSION_SCAFFOLD_MANIFEST}"
}

# Preflight
cp "${SLURM_DIR}/preflight_iter013.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter013.slurm"
{
  common_paths
  cat <<EOF
STAGE=preflight
PREFLIGHT_OUTPUT=${OUTPUT_ROOT}/preflight/preflight_result.json
EOF
} > "${OUTPUT_ROOT}/preflight/submission_config.env"
write_submitter "${OUTPUT_ROOT}/preflight" "submit_preflight_iter013.slurm" "preflight" 2

# Analyses
for site in abby jerc; do
  SITE_U="${site^^}"
  cp "${SLURM_DIR}/analyze_iter013.slurm" "${OUTPUT_ROOT}/analysis/${site}/submit_analyze_iter013.slurm"
  {
    common_paths
    cat <<EOF
STAGE=analysis
SITE=${SITE_U}
ANALYSIS_OUTPUT=${OUTPUT_ROOT}/analysis/${site}/result
EOF
  } > "${OUTPUT_ROOT}/analysis/${site}/submission_config.env"
  write_submitter "${OUTPUT_ROOT}/analysis/${site}" "submit_analyze_iter013.slurm" "analysis_${site}" 2
done

# Aggregate
cp "${SLURM_DIR}/aggregate_iter013.slurm" "${OUTPUT_ROOT}/aggregate/submit_aggregate_iter013.slurm"
{
  common_paths
  cat <<EOF
STAGE=aggregate
ABBY_ANALYSIS_DIR=${OUTPUT_ROOT}/analysis/abby/result
JERC_ANALYSIS_DIR=${OUTPUT_ROOT}/analysis/jerc/result
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
AGGREGATE_OUTPUT=${OUTPUT_ROOT}/aggregate/result
EOF
} > "${OUTPUT_ROOT}/aggregate/submission_config.env"
write_submitter "${OUTPUT_ROOT}/aggregate" "submit_aggregate_iter013.slurm" "aggregate" 2

# Handoff validation
cp "${SLURM_DIR}/validate_iter013_handoff.slurm" "${OUTPUT_ROOT}/handoff_validation/submit_validate_iter013_handoff.slurm"
{
  common_paths
  cat <<EOF
STAGE=handoff_validation
AGGREGATE_RESULT=${OUTPUT_ROOT}/aggregate/result/aggregate_result.json
ACCOUNTING_CSV=${OUTPUT_ROOT}/accounting.csv
EOF
} > "${OUTPUT_ROOT}/handoff_validation/submission_config.env"
write_submitter "${OUTPUT_ROOT}/handoff_validation" "submit_validate_iter013_handoff.slurm" "handoff_validation" 2

cat > "${OUTPUT_ROOT}/accounting.csv" <<EOF
package_id,work_unit,job_id,state,exit_code,classification,run_dir,elapsed,maxrss
EOF

{
  echo "OUTPUT_ROOT=${OUTPUT_ROOT}"
  echo "REPOSITORY_COMMIT=${COMMIT}"
  echo "SOURCE_MANIFEST_SHA256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
  echo "DEPENDENCY_MANIFEST_SHA256=$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
  echo "SUBMISSION_SCAFFOLD_SHA256=$(sha256sum "${SUBMISSION_SCAFFOLD_MANIFEST}" | awk '{print $1}')"
} > "${OUTPUT_ROOT}/package_identity.env"

rm -f "${OUTPUT_ROOT}/.materialization_incomplete"
echo "MATERIALIZE_PASS root=${OUTPUT_ROOT} commit=${COMMIT}"
