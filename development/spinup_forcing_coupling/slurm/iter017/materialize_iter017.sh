#!/usr/bin/env bash
# Create the immutable submitted-copy package; do not submit from this script.
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter017"
readonly EXAMPLE_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/examples/iter017"
readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"

test "$(pwd -P)" = "${REPO_ROOT}"
test ! -e "${OUTPUT_ROOT}"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
for file in "${ITER_DIR}"/* "${EXAMPLE_DIR}"/*.yaml; do test -f "${file}"; done

mkdir -p "${OUTPUT_ROOT}/preflight" "${OUTPUT_ROOT}/configs" "${OUTPUT_ROOT}/paths" "${OUTPUT_ROOT}/source_snapshot/model_ELM"
cp "${EXAMPLE_DIR}"/*.yaml "${OUTPUT_ROOT}/configs/"
cp "${ITER_DIR}/preflight_iter017.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter017.slurm"
cp "${ITER_DIR}/preflight_iter017.py" "${OUTPUT_ROOT}/preflight/"
cp "${ITER_DIR}/refresh_path_package_iter017.sh" "${OUTPUT_ROOT}/source_snapshot/"
cmp -s "${EXAMPLE_DIR}/abby_daily_050.yaml" "${OUTPUT_ROOT}/configs/abby_daily_050.yaml"
cmp -s "${EXAMPLE_DIR}/jerc_hourly_075.yaml" "${OUTPUT_ROOT}/configs/jerc_hourly_075.yaml"
cmp -s "${EXAMPLE_DIR}/joint_daily_050.yaml" "${OUTPUT_ROOT}/configs/joint_daily_050.yaml"
cmp -s "${EXAMPLE_DIR}/joint_hourly_075.yaml" "${OUTPUT_ROOT}/configs/joint_hourly_075.yaml"
cmp -s "${ITER_DIR}/preflight_iter017.slurm" "${OUTPUT_ROOT}/preflight/submit_preflight_iter017.slurm"
cmp -s "${ITER_DIR}/refresh_path_package_iter017.sh" "${OUTPUT_ROOT}/source_snapshot/refresh_path_package_iter017.sh"
cp "${REPO_ROOT}/initialize_pipeline.py" "${OUTPUT_ROOT}/source_snapshot/"
cp "${REPO_ROOT}/optimize_surrogate_forcing.py" "${OUTPUT_ROOT}/source_snapshot/"
cp "${REPO_ROOT}/run_optimization_campaign.py" "${OUTPUT_ROOT}/source_snapshot/"
cp "${REPO_ROOT}/report_optimization.py" "${OUTPUT_ROOT}/source_snapshot/"
cp "${REPO_ROOT}/model_ELM/MCMC_forcing.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/MCMC.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/coupling_pipeline.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/mcmc_geometry.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/mcmc_spinup_modes.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/coupled_surrogate.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/load_obs_nc.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/surrogate_NN_Forcing.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/forcing_surrogate_artifact.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/spinup_surrogate_artifact.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/mcmc_artifacts.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/mcmc_diagnostics.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
cp "${REPO_ROOT}/model_ELM/optimization_config.py" "${OUTPUT_ROOT}/source_snapshot/model_ELM/"
for source in "${OUTPUT_ROOT}/source_snapshot/"*.py "${OUTPUT_ROOT}/source_snapshot/model_ELM/"*.py; do
  relative="${source#${OUTPUT_ROOT}/source_snapshot/}"
  cmp -s "${source}" "${REPO_ROOT}/${relative}"
done
sha256sum "${OUTPUT_ROOT}/source_snapshot/"*.py \
  "${OUTPUT_ROOT}/source_snapshot/refresh_path_package_iter017.sh" \
  "${OUTPUT_ROOT}/source_snapshot/model_ELM/"*.py > "${OUTPUT_ROOT}/source_snapshot.sha256"

sha256sum \
  "${REPO_ROOT}/initialize_pipeline.py" \
  "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  "${REPO_ROOT}/run_optimization_campaign.py" \
  "${REPO_ROOT}/report_optimization.py" \
  "${REPO_ROOT}/model_ELM/MCMC_forcing.py" \
  "${REPO_ROOT}/model_ELM/MCMC.py" \
  "${REPO_ROOT}/model_ELM/coupling_pipeline.py" \
  "${REPO_ROOT}/model_ELM/mcmc_geometry.py" \
  "${REPO_ROOT}/model_ELM/mcmc_spinup_modes.py" \
  "${REPO_ROOT}/model_ELM/coupled_surrogate.py" \
  "${REPO_ROOT}/model_ELM/load_obs_nc.py" \
  "${REPO_ROOT}/model_ELM/surrogate_NN_Forcing.py" \
  "${REPO_ROOT}/model_ELM/forcing_surrogate_artifact.py" \
  "${REPO_ROOT}/model_ELM/spinup_surrogate_artifact.py" \
  "${REPO_ROOT}/model_ELM/mcmc_artifacts.py" \
  "${REPO_ROOT}/model_ELM/mcmc_diagnostics.py" \
  "${REPO_ROOT}/model_ELM/optimization_config.py" \
  "${ITER_DIR}/materialize_iter017.sh" \
  "${ITER_DIR}/refresh_path_package_iter017.sh" \
  "${ITER_DIR}/preflight_iter017.py" \
  "${ITER_DIR}/preflight_iter017.slurm" \
  "${ITER_DIR}/initialize_iter017.slurm" \
  "${ITER_DIR}/optimization_array_iter017.slurm" \
  "${ITER_DIR}/report_iter017.slurm" \
  "${ITER_DIR}/validate_iter017_handoff.py" \
  "${ITER_DIR}/validate_iter017_handoff.slurm" \
  "${EXAMPLE_DIR}"/*.yaml > "${OUTPUT_ROOT}/source_manifest.sha256"
sha256sum \
  /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl \
  /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl \
  /xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc \
  /xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc \
  "${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl" \
  "${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl" \
  /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz \
  "${REPO_ROOT}/conda_envs/OLMT_puma.yml" \
  > "${OUTPUT_ROOT}/dependency_manifest.sha256"

make_path() {
  local slug="$1" campaign="$2"
  local path_root="${OUTPUT_ROOT}/paths/${slug}"
  mkdir -p "${path_root}/initialization" "${path_root}/optimization" "${path_root}/postprocess"
  cp "${ITER_DIR}/initialize_iter017.slurm" "${path_root}/initialization/submit_initialize_iter017.slurm"
  cp "${ITER_DIR}/optimization_array_iter017.slurm" "${path_root}/optimization/submit_optimization_iter017.slurm"
  cp "${ITER_DIR}/report_iter017.slurm" "${path_root}/postprocess/submit_report_iter017.slurm"
  cmp -s "${ITER_DIR}/initialize_iter017.slurm" "${path_root}/initialization/submit_initialize_iter017.slurm"
  cmp -s "${ITER_DIR}/optimization_array_iter017.slurm" "${path_root}/optimization/submit_optimization_iter017.slurm"
  cmp -s "${ITER_DIR}/report_iter017.slurm" "${path_root}/postprocess/submit_report_iter017.slurm"
  cat > "${path_root}/initialization/submission_config.env" <<EOF
RUN_DIR=${path_root}/initialization
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${path_root}/initialization/submit_initialize_iter017.slurm" | awk '{print $1}')
CAMPAIGN=${OUTPUT_ROOT}/configs/${campaign}
CAMPAIGN_SHA256=$(sha256sum "${OUTPUT_ROOT}/configs/${campaign}" | awk '{print $1}')
OUTPUT=${path_root}/initialization
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
  cat > "${path_root}/optimization/submission_config.env" <<EOF
RUN_DIR=${path_root}/optimization
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${path_root}/optimization/submit_optimization_iter017.slurm" | awk '{print $1}')
CAMPAIGN=${OUTPUT_ROOT}/configs/${campaign}
CAMPAIGN_SHA256=$(sha256sum "${OUTPUT_ROOT}/configs/${campaign}" | awk '{print $1}')
PATH_ROOT=${path_root}
POOL=${path_root}/initialization/artifacts/candidate_pool.npz
SEEDS=(9009 9010 9011)
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
  cat > "${path_root}/postprocess/submission_config.env" <<EOF
RUN_DIR=${path_root}/postprocess
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${path_root}/postprocess/submit_report_iter017.slurm" | awk '{print $1}')
CAMPAIGN=${OUTPUT_ROOT}/configs/${campaign}
CAMPAIGN_SHA256=$(sha256sum "${OUTPUT_ROOT}/configs/${campaign}" | awk '{print $1}')
PATH_ROOT=${path_root}
EOF
}

make_path abby_daily_050 abby_daily_050.yaml
make_path jerc_hourly_075 jerc_hourly_075.yaml
make_path joint_daily_050 joint_daily_050.yaml
make_path joint_hourly_075 joint_hourly_075.yaml
mkdir -p "${OUTPUT_ROOT}/handoff"
cp "${ITER_DIR}/validate_iter017_handoff.slurm" "${OUTPUT_ROOT}/handoff/submit_validate_iter017_handoff.slurm"
cp "${ITER_DIR}/validate_iter017_handoff.py" "${OUTPUT_ROOT}/handoff/"
cmp -s "${ITER_DIR}/validate_iter017_handoff.slurm" "${OUTPUT_ROOT}/handoff/submit_validate_iter017_handoff.slurm"
cat > "${OUTPUT_ROOT}/preflight/submission_config.env" <<EOF
RUN_DIR=${OUTPUT_ROOT}/preflight
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${OUTPUT_ROOT}/preflight/submit_preflight_iter017.slurm" | awk '{print $1}')
CAMPAIGN_DIR=${OUTPUT_ROOT}/configs
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
cat > "${OUTPUT_ROOT}/handoff/submission_config.env" <<EOF
RUN_DIR=${OUTPUT_ROOT}/handoff
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${OUTPUT_ROOT}/handoff/submit_validate_iter017_handoff.slurm" | awk '{print $1}')
OUTPUT_ROOT=${OUTPUT_ROOT}
EOF
cat > "${OUTPUT_ROOT}/package_identity.env" <<EOF
ITERATION_ID=iter017
REPOSITORY_COMMIT=${COMMIT}
OUTPUT_ROOT=${OUTPUT_ROOT}
EOF
sha256sum "${OUTPUT_ROOT}/configs/"*.yaml \
  "${OUTPUT_ROOT}/preflight/submit_preflight_iter017.slurm" \
  "${OUTPUT_ROOT}/paths/"*/initialization/submit_initialize_iter017.slurm \
  "${OUTPUT_ROOT}/paths/"*/optimization/submit_optimization_iter017.slurm \
  "${OUTPUT_ROOT}/paths/"*/postprocess/submit_report_iter017.slurm \
  "${OUTPUT_ROOT}/handoff/submit_validate_iter017_handoff.slurm" > "${OUTPUT_ROOT}/submitted_copy_manifest.sha256"
echo "ITER017_MATERIALIZED root=${OUTPUT_ROOT}"
