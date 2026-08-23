#!/usr/bin/env bash
# Preserve the failed aggregate v1 launcher materials, then make the approved configuration-only v2 correction.
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011"
readonly AGGREGATE_DIR="${ROOT}/spinup_forcing_coupling_iter011_aggregate"
readonly PREFLIGHT_DIR="${ROOT}/spinup_forcing_coupling_iter011_preflight"
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter011"
readonly FORCING="${ROOT}/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly ABBY_CASE="${REPO_ROOT}/pklfiles/ABBY_ppe6_I20TRCNPRDCTCBC.pkl"
readonly JERC_CASE="${REPO_ROOT}/pklfiles/JERC_ppe6_I20TRCNPRDCTCBC.pkl"
test -f "${AGGREGATE_DIR}/identity_record.env"; test ! -e "${AGGREGATE_DIR}/identity_record_v1.env"; test ! -e "${SUMMARY_ROOT}"
for name in source_manifest.sha256 dependency_manifest.sha256 submit_aggregate_iter011.slurm; do
  cp "${AGGREGATE_DIR}/${name}" "${AGGREGATE_DIR}/${name%.*}_v1.${name##*.}"
done
for name in submission_config.env canonical_submission_config.env identity_record.env; do
  cp "${AGGREGATE_DIR}/${name}" "${AGGREGATE_DIR}/${name%.env}_v1.env"
done
readonly SOURCE_MANIFEST="${AGGREGATE_DIR}/source_manifest.sha256"
sha256sum "${REPO_ROOT}/optimize_surrogate_forcing.py" "${REPO_ROOT}/model_ELM/__init__.py" "${REPO_ROOT}/model_ELM/MCMC_forcing.py" "${REPO_ROOT}/model_ELM/mcmc_geometry.py" "${REPO_ROOT}/model_ELM/coupled_surrogate.py" "${REPO_ROOT}/model_ELM/load_obs_nc.py" "${REPO_ROOT}/model_ELM/surrogate_NN_Forcing.py" "${REPO_ROOT}/model_ELM/surrogate_NN_Spinup.py" "${REPO_ROOT}/model_ELM/forcing_surrogate_artifact.py" "${REPO_ROOT}/model_ELM/spinup_surrogate_artifact.py" "${ITER_DIR}/aggregate_iter011.py" "${ITER_DIR}/aggregate_iter011.slurm" > "${SOURCE_MANIFEST}"
sha256sum -c "${SOURCE_MANIFEST}"
readonly DEPENDENCY_MANIFEST="${AGGREGATE_DIR}/dependency_manifest.sha256"
cat "${PREFLIGHT_DIR}/dependency_manifest.sha256" > "${DEPENDENCY_MANIFEST}"
sha256sum "${ABBY_CASE}" "${JERC_CASE}" >> "${DEPENDENCY_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
cp "${ITER_DIR}/aggregate_iter011.slurm" "${AGGREGATE_DIR}/submit_aggregate_iter011.slurm"
printf '%s\n' \
  'ITERATION_ID=iter011' 'STAGE=aggregate' "REPOSITORY_COMMIT=$(git -C "${REPO_ROOT}" rev-parse HEAD)" \
  "SOURCE_MANIFEST=${SOURCE_MANIFEST}" "DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}" \
  'MICROMAMBA_MODULE=micromamba/2.0.2-2' 'MICROMAMBA_ENV=OLMT_puma' \
  "OUTPUT_ROOT=${ROOT}" "AGGREGATE_OUTPUT=${AGGREGATE_DIR}/result" "SUMMARY_ROOT=${SUMMARY_ROOT}" \
  "VALIDATOR=${ITER_DIR}/aggregate_iter011.py" \
  "CAMPAIGN_PARENTS='${ROOT}/spinup_forcing_coupling_iter011_hourly_scale050_campaign ${ROOT}/spinup_forcing_coupling_iter011_hourly_scale075_campaign ${ROOT}/spinup_forcing_coupling_iter011_hourly_scale100_campaign ${ROOT}/spinup_forcing_coupling_iter011_daily_scale050_campaign ${ROOT}/spinup_forcing_coupling_iter011_daily_scale075_campaign ${ROOT}/spinup_forcing_coupling_iter011_daily_scale100_campaign'" > "${AGGREGATE_DIR}/submission_config.env"
cp "${AGGREGATE_DIR}/submission_config.env" "${AGGREGATE_DIR}/canonical_submission_config.env"
cmp -s "${ITER_DIR}/aggregate_iter011.slurm" "${AGGREGATE_DIR}/submit_aggregate_iter011.slurm"
cmp -s "${AGGREGATE_DIR}/submission_config.env" "${AGGREGATE_DIR}/canonical_submission_config.env"
printf '%s\n' "canonical_script_sha256=$(sha256sum "${ITER_DIR}/aggregate_iter011.slurm" | awk '{print $1}')" "submitted_script_sha256=$(sha256sum "${AGGREGATE_DIR}/submit_aggregate_iter011.slurm" | awk '{print $1}')" "config_sha256=$(sha256sum "${AGGREGATE_DIR}/submission_config.env" | awk '{print $1}')" > "${AGGREGATE_DIR}/identity_record.env"
echo AGGREGATE_REMATERIALIZE_V2_PASS
