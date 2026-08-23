#!/usr/bin/env bash
# Preserve unsubmitted v1 copies and replace the active Iter011 materialization after review block.
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011"
readonly PREFLIGHT_DIR="${ROOT}/spinup_forcing_coupling_iter011_preflight"
readonly INIT_DIR="${ROOT}/spinup_forcing_coupling_iter009_initialize"
readonly FORCING="${ROOT}/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
for file in source_manifest.sha256 dependency_manifest.sha256; do mv "${PREFLIGHT_DIR}/${file}" "${PREFLIGHT_DIR}/${file%.sha256}_v1.sha256"; done
sha256sum "${REPO_ROOT}/optimize_surrogate_forcing.py" "${REPO_ROOT}/model_ELM/MCMC_forcing.py" "${REPO_ROOT}/model_ELM/mcmc_geometry.py" "${ITER_DIR}/campaign_iter011.slurm" "${ITER_DIR}/preflight_iter011.py" "${ITER_DIR}/preflight_iter011.slurm" "${ITER_DIR}/iter011_matrix.tsv" > "${PREFLIGHT_DIR}/source_manifest.sha256"
printf '%s  %s\n' \
  8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e "${FORCING}" \
  1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023 "${SPINUP}" \
  e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2 "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc" \
  a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f "/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc" \
  37f51011638e93ef1420d092d7f97bbd8e6bfa24342d205fcc09b9d5a9d8716a "${INIT_DIR}/abby_high_seed9009.npz" \
  49a32268e72a183414e2ba684717b1b7675c84f4ebf12b2ffd23df850c9f69cb "${INIT_DIR}/abby_high_seed9010.npz" \
  8c30198df99da7225f9c3235866c3020fef8d1e7a9349494149ddcfa11d14e0c "${INIT_DIR}/abby_high_seed9011.npz" \
  394902f2c2378a6793196f226c7cf136872a2631012f559ba857c989c47bd8fe "${INIT_DIR}/jerc_high_seed9009.npz" \
  86fa8a3a732be080454bb451ab025cf604c1c8c0a98ffbdce26ed2b46d3870d6 "${INIT_DIR}/jerc_high_seed9010.npz" \
  fa19ed47a533f540e88992c1eac6346f46478192ed85b1132222ac08599f063e "${INIT_DIR}/jerc_high_seed9011.npz" > "${PREFLIGHT_DIR}/dependency_manifest.sha256"
sha256sum -c "${PREFLIGHT_DIR}/source_manifest.sha256"; sha256sum -c "${PREFLIGHT_DIR}/dependency_manifest.sha256"
refresh() { local dir="$1" script="$2"; shift 2; mv "${dir}/${script}" "${dir}/${script%.slurm}_v1.slurm"; mv "${dir}/submission_config.env" "${dir}/submission_config_v1.env"; mv "${dir}/canonical_submission_config.env" "${dir}/canonical_submission_config_v1.env"; cp "$@" "${dir}/${script}"; }
refresh "${PREFLIGHT_DIR}" submit_preflight_iter011.slurm "${ITER_DIR}/preflight_iter011.slurm"
printf '%s\n' "ITERATION_ID=iter011" "STAGE=preflight" "REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)" "SOURCE_MANIFEST=${PREFLIGHT_DIR}/source_manifest.sha256" "MICROMAMBA_MODULE=micromamba/2.0.2-2" "MICROMAMBA_ENV=OLMT_puma" "DEPENDENCY_MANIFEST=${PREFLIGHT_DIR}/dependency_manifest.sha256" "INITIALIZATION_DIR=${INIT_DIR}" "PREFLIGHT_OUTPUT=${PREFLIGHT_DIR}/result_v2" "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" > "${PREFLIGHT_DIR}/submission_config.env"
cp "${PREFLIGHT_DIR}/submission_config.env" "${PREFLIGHT_DIR}/canonical_submission_config.env"
for parent in "${ROOT}"/spinup_forcing_coupling_iter011_*_campaign; do
  script="$(basename "${parent}")"; resolution="${script#spinup_forcing_coupling_iter011_}"; resolution="${resolution%%_*}"; scale="${script#*_scale}"; scale="${scale%%_*}"; case "${scale}" in 050) numeric=0.50;;075) numeric=0.75;;100) numeric=1.00;;esac
  refresh "${parent}" "submit_${resolution}_scale${scale}_campaign.slurm" "${ITER_DIR}/campaign_iter011.slurm"
  printf '%s\n' "ITERATION_ID=iter011" "STAGE=campaign" "REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)" "SOURCE_MANIFEST=${PREFLIGHT_DIR}/source_manifest.sha256" "MICROMAMBA_MODULE=micromamba/2.0.2-2" "MICROMAMBA_ENV=OLMT_puma" "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" "DEPENDENCY_MANIFEST=${PREFLIGHT_DIR}/dependency_manifest.sha256" "INITIALIZATION_DIR=${INIT_DIR}" "CAMPAIGN_PARENT_DIR=${parent}" "MATRIX_MANIFEST=${parent}/matrix.tsv" "LIKELIHOOD_RESOLUTION=${resolution}" "DE_MOVE_SCALE=${numeric}" > "${parent}/submission_config.env"
  cp "${parent}/submission_config.env" "${parent}/canonical_submission_config.env"
done
echo REMATERIALIZE_V2_PASS
