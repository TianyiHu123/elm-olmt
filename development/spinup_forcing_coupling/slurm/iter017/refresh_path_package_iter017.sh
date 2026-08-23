#!/usr/bin/env bash
# Materialize one non-destructive corrected package for a failed Iter017 path.
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter017"
readonly EXAMPLE_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/examples/iter017"
readonly RECOVERY_ID=recovery_1

test "$(pwd -P)" = "${REPO_ROOT}"
test "$#" = 1
readonly SLUG="$1"
case "${SLUG}" in
  abby_daily_050|jerc_hourly_075|joint_daily_050|joint_hourly_075) ;;
  *) echo "unsupported Iter017 path: ${SLUG}" >&2; exit 2 ;;
esac
readonly PATH_ROOT="${OUTPUT_ROOT}/paths/${SLUG}"
readonly INIT_ROOT="${PATH_ROOT}/initialization"
readonly RECOVERY_ROOT="${PATH_ROOT}/${RECOVERY_ID}"
readonly CAMPAIGN="${OUTPUT_ROOT}/configs/${SLUG}.yaml"

test -d "${INIT_ROOT}/artifacts"
test ! -e "${INIT_ROOT}/stage_manifest.json"
test ! -e "${RECOVERY_ROOT}"
test -f "${CAMPAIGN}"
test -f "${OUTPUT_ROOT}/dependency_manifest.sha256"
for file in "${ITER_DIR}"/*.sh "${ITER_DIR}"/*.slurm "${ITER_DIR}"/*.py "${EXAMPLE_DIR}"/*.yaml; do test -f "${file}"; done

mkdir -p "${RECOVERY_ROOT}/source_snapshot/model_ELM" "${RECOVERY_ROOT}/optimization"
cp "${ITER_DIR}/initialize_iter017.slurm" "${INIT_ROOT}/submit_initialize_iter017_${RECOVERY_ID}.slurm"
cmp -s "${ITER_DIR}/initialize_iter017.slurm" "${INIT_ROOT}/submit_initialize_iter017_${RECOVERY_ID}.slurm"
cp "${ITER_DIR}/optimization_array_iter017.slurm" "${RECOVERY_ROOT}/optimization/submit_optimization_iter017_${RECOVERY_ID}.slurm"
cmp -s "${ITER_DIR}/optimization_array_iter017.slurm" "${RECOVERY_ROOT}/optimization/submit_optimization_iter017_${RECOVERY_ID}.slurm"

readonly SOURCE_FILES=(
  initialize_pipeline.py
  optimize_surrogate_forcing.py
  run_optimization_campaign.py
  report_optimization.py
  model_ELM/MCMC_forcing.py
  model_ELM/MCMC.py
  model_ELM/coupling_pipeline.py
  model_ELM/mcmc_geometry.py
  model_ELM/mcmc_spinup_modes.py
  model_ELM/coupled_surrogate.py
  model_ELM/load_obs_nc.py
  model_ELM/surrogate_NN_Forcing.py
  model_ELM/forcing_surrogate_artifact.py
  model_ELM/spinup_surrogate_artifact.py
  model_ELM/mcmc_artifacts.py
  model_ELM/mcmc_diagnostics.py
  model_ELM/optimization_config.py
  development/spinup_forcing_coupling/slurm/iter017/materialize_iter017.sh
  development/spinup_forcing_coupling/slurm/iter017/refresh_path_package_iter017.sh
  development/spinup_forcing_coupling/slurm/iter017/preflight_iter017.py
  development/spinup_forcing_coupling/slurm/iter017/preflight_iter017.slurm
  development/spinup_forcing_coupling/slurm/iter017/initialize_iter017.slurm
  development/spinup_forcing_coupling/slurm/iter017/optimization_array_iter017.slurm
  development/spinup_forcing_coupling/slurm/iter017/report_iter017.slurm
  development/spinup_forcing_coupling/slurm/iter017/validate_iter017_handoff.py
  development/spinup_forcing_coupling/slurm/iter017/validate_iter017_handoff.slurm
  development/spinup_forcing_coupling/examples/iter017/abby_daily_050.yaml
  development/spinup_forcing_coupling/examples/iter017/jerc_hourly_075.yaml
  development/spinup_forcing_coupling/examples/iter017/joint_daily_050.yaml
  development/spinup_forcing_coupling/examples/iter017/joint_hourly_075.yaml
)
for source in "${SOURCE_FILES[@]}"; do
  destination="${RECOVERY_ROOT}/source_snapshot/${source}"
  mkdir -p "$(dirname "${destination}")"
  cp "${REPO_ROOT}/${source}" "${destination}"
  cmp -s "${REPO_ROOT}/${source}" "${destination}"
done
: > "${RECOVERY_ROOT}/source_manifest.sha256"
for source in "${SOURCE_FILES[@]}"; do
  sha256sum "${REPO_ROOT}/${source}" >> "${RECOVERY_ROOT}/source_manifest.sha256"
done
sha256sum -c "${RECOVERY_ROOT}/source_manifest.sha256"
cp "${OUTPUT_ROOT}/dependency_manifest.sha256" "${RECOVERY_ROOT}/dependency_manifest.sha256"
cmp -s "${OUTPUT_ROOT}/dependency_manifest.sha256" "${RECOVERY_ROOT}/dependency_manifest.sha256"
sha256sum -c "${RECOVERY_ROOT}/dependency_manifest.sha256"

cat > "${RECOVERY_ROOT}/submission_config.env" <<EOF
RUN_DIR=${INIT_ROOT}
SUBMITTED_SCRIPT=${INIT_ROOT}/submit_initialize_iter017_${RECOVERY_ID}.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${INIT_ROOT}/submit_initialize_iter017_${RECOVERY_ID}.slurm" | awk '{print $1}')
CAMPAIGN=${CAMPAIGN}
CAMPAIGN_SHA256=$(sha256sum "${CAMPAIGN}" | awk '{print $1}')
OUTPUT=${INIT_ROOT}
REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)
SOURCE_MANIFEST=${RECOVERY_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${RECOVERY_ROOT}/dependency_manifest.sha256
EOF
cat > "${RECOVERY_ROOT}/optimization/submission_config.env" <<EOF
RUN_DIR=${RECOVERY_ROOT}/optimization
SUBMITTED_SCRIPT=${RECOVERY_ROOT}/optimization/submit_optimization_iter017_${RECOVERY_ID}.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${RECOVERY_ROOT}/optimization/submit_optimization_iter017_${RECOVERY_ID}.slurm" | awk '{print $1}')
CAMPAIGN=${CAMPAIGN}
CAMPAIGN_SHA256=$(sha256sum "${CAMPAIGN}" | awk '{print $1}')
PATH_ROOT=${PATH_ROOT}
POOL=${INIT_ROOT}/artifacts/candidate_pool.npz
SEEDS=(9009 9010 9011)
REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)
SOURCE_MANIFEST=${RECOVERY_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${RECOVERY_ROOT}/dependency_manifest.sha256
EOF
sha256sum "${RECOVERY_ROOT}/submission_config.env" \
  "${RECOVERY_ROOT}/optimization/submission_config.env" \
  "${RECOVERY_ROOT}/source_manifest.sha256" \
  "${RECOVERY_ROOT}/dependency_manifest.sha256" \
  "${INIT_ROOT}/submit_initialize_iter017_${RECOVERY_ID}.slurm" \
  "${RECOVERY_ROOT}/optimization/submit_optimization_iter017_${RECOVERY_ID}.slurm" \
  > "${RECOVERY_ROOT}/package_manifest.sha256"
echo "ITER017_PATH_PACKAGE_REFRESHED slug=${SLUG} recovery=${RECOVERY_ID}"
