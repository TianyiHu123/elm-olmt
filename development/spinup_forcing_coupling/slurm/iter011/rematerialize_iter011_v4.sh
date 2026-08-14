#!/usr/bin/env bash
# Preserve unsubmitted v3 copies after the authorized minimal preflight correction.
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011"
readonly PREFLIGHT_DIR="${ROOT}/spinup_forcing_coupling_iter011_preflight"
readonly INIT_DIR="${ROOT}/spinup_forcing_coupling_iter009_initialize"
readonly FORCING="${ROOT}/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
mv "${PREFLIGHT_DIR}/source_manifest.sha256" "${PREFLIGHT_DIR}/source_manifest_v3.sha256"
sha256sum "${REPO_ROOT}/optimize_surrogate_forcing.py" "${REPO_ROOT}/model_ELM/MCMC_forcing.py" "${REPO_ROOT}/model_ELM/mcmc_geometry.py" "${ITER_DIR}/campaign_iter011.slurm" "${ITER_DIR}/preflight_iter011.py" "${ITER_DIR}/preflight_iter011.slurm" "${ITER_DIR}/iter011_matrix.tsv" > "${PREFLIGHT_DIR}/source_manifest.sha256"
sha256sum -c "${PREFLIGHT_DIR}/source_manifest.sha256"; sha256sum -c "${PREFLIGHT_DIR}/dependency_manifest.sha256"
refresh() { local dir="$1" script="$2" source="$3"; mv "${dir}/${script}" "${dir}/${script%.slurm}_v3.slurm"; mv "${dir}/submission_config.env" "${dir}/submission_config_v3.env"; mv "${dir}/canonical_submission_config.env" "${dir}/canonical_submission_config_v3.env"; cp "${source}" "${dir}/${script}"; }
refresh "${PREFLIGHT_DIR}" submit_preflight_iter011.slurm "${ITER_DIR}/preflight_iter011.slurm"
printf '%s\n' "ITERATION_ID=iter011" "STAGE=preflight" "REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)" "SOURCE_MANIFEST=${PREFLIGHT_DIR}/source_manifest.sha256" "MICROMAMBA_MODULE=micromamba/2.0.2-2" "MICROMAMBA_ENV=OLMT_puma" "DEPENDENCY_MANIFEST=${PREFLIGHT_DIR}/dependency_manifest.sha256" "INITIALIZATION_DIR=${INIT_DIR}" "PREFLIGHT_OUTPUT=${PREFLIGHT_DIR}/result_v4" "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" > "${PREFLIGHT_DIR}/submission_config.env"
cp "${PREFLIGHT_DIR}/submission_config.env" "${PREFLIGHT_DIR}/canonical_submission_config.env"
for parent in "${ROOT}"/spinup_forcing_coupling_iter011_*_campaign; do
  tag="$(basename "${parent}")"; resolution="${tag#spinup_forcing_coupling_iter011_}"; resolution="${resolution%%_*}"; scale="${tag#*_scale}"; scale="${scale%%_*}"; case "${scale}" in 050) numeric=0.50;;075) numeric=0.75;;100) numeric=1.00;;esac
  refresh "${parent}" "submit_${resolution}_scale${scale}_campaign.slurm" "${ITER_DIR}/campaign_iter011.slurm"
  printf '%s\n' "ITERATION_ID=iter011" "STAGE=campaign" "REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)" "SOURCE_MANIFEST=${PREFLIGHT_DIR}/source_manifest.sha256" "MICROMAMBA_MODULE=micromamba/2.0.2-2" "MICROMAMBA_ENV=OLMT_puma" "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" "DEPENDENCY_MANIFEST=${PREFLIGHT_DIR}/dependency_manifest.sha256" "INITIALIZATION_DIR=${INIT_DIR}" "CAMPAIGN_PARENT_DIR=${parent}" "MATRIX_MANIFEST=${parent}/matrix.tsv" "LIKELIHOOD_RESOLUTION=${resolution}" "DE_MOVE_SCALE=${numeric}" > "${parent}/submission_config.env"
  cp "${parent}/submission_config.env" "${parent}/canonical_submission_config.env"
done
echo REMATERIALIZE_V4_PASS
