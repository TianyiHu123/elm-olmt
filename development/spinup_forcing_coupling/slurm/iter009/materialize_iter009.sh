#!/usr/bin/env bash
# Create exactly the approved Iter009 run directories and immutable submitted copies.
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009"
readonly HEAD="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
readonly MODULE=micromamba/2.0.2-2
readonly ENV=OLMT_puma
readonly FORCING="${ROOT}/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
readonly SPINUP=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly ABBY_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc
readonly JERC_OBS=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc
readonly ABBY_RAW="${ROOT}/spinup_forcing_coupling_iter008_abby_campaign/raw_chain.npz"
readonly JERC_RAW="${ROOT}/spinup_forcing_coupling_iter008_jerc_campaign/raw_chain.npz"
readonly INIT_DIR="${ROOT}/spinup_forcing_coupling_iter009_initialize"
readonly PREFLIGHT_DIR="${ROOT}/spinup_forcing_coupling_iter009_preflight"

for unit in preflight initialize b_campaign t_campaign i_campaign m_campaign tim_campaign validate; do
  mkdir -p "${ROOT}/spinup_forcing_coupling_iter009_${unit}"
done

# These are approved identities, not a self-referential snapshot of whatever happens to be present.
readonly DEPENDENCY_MANIFEST="${PREFLIGHT_DIR}/dependency_manifest.sha256"
printf '%s  %s\n' \
  8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e "${FORCING}" \
  1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023 "${SPINUP}" \
  e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2 "${ABBY_OBS}" \
  a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f "${JERC_OBS}" \
  5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87 "${ABBY_RAW}" \
  34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080 "${JERC_RAW}" \
  > "${DEPENDENCY_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
cp "${DEPENDENCY_MANIFEST}" "${INIT_DIR}/iter008_raw_manifest.sha256"

write_config() {
  local run_dir="$1"
  shift
  printf '%s\n' "$@" > "${run_dir}/submission_config.env"
  cp "${run_dir}/submission_config.env" "${run_dir}/canonical_submission_config.env"
}

for arm in B T I M TIM; do
  lower="$(tr '[:upper:]' '[:lower:]' <<< "${arm}")"
  run="${ROOT}/spinup_forcing_coupling_iter009_${lower}_campaign"
  cp "${ITER_DIR}/campaign_iter009.slurm" "${run}/submit_${lower}_campaign.slurm"
  cp "${ITER_DIR}/iter009_matrix.tsv" "${run}/matrix.tsv"
  case "${arm}" in
    B) coordinates=physical; initialization=uniform; move=stretch ;;
    T) coordinates=transformed; initialization=uniform; move=stretch ;;
    I) coordinates=physical; initialization=high; move=stretch ;;
    M) coordinates=physical; initialization=uniform; move=de_mixture ;;
    TIM) coordinates=transformed; initialization=high; move=de_mixture ;;
  esac
  awk -F '\t' -v a="${arm}" -v coord="${coordinates}" -v init="${initialization}" -v move="${move}" \
    'BEGIN{OFS="\t"} NR==1 {print; next} {$7=a; $8=coord; $9=init; $10=move; print}' \
    "${run}/matrix.tsv" > "${run}/matrix.tmp"
  mv "${run}/matrix.tmp" "${run}/matrix.tsv"
  while IFS=$'\t' read -r array_index leaf_id site seed uniform_seed maximin_seed ignored; do
    [[ "${array_index}" == "array_index" ]] && continue
    mkdir -p "${run}/${leaf_id}"
  done < "${run}/matrix.tsv"
  write_config "${run}" \
    "ITERATION_ID=iter009" "STAGE=campaign" "REPOSITORY_COMMIT=${HEAD}" \
    "SOURCE_MANIFEST=${ITER_DIR}/iter009_source_manifest.sha256" "MICROMAMBA_MODULE=${MODULE}" \
    "MICROMAMBA_ENV=${ENV}" "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" \
    "DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}" "INITIALIZATION_DIR=${INIT_DIR}" \
    "CAMPAIGN_PARENT_DIR=${run}" "MATRIX_MANIFEST=${run}/matrix.tsv" "ARM=${arm}"
done

cp "${ITER_DIR}/preflight_iter009.slurm" "${PREFLIGHT_DIR}/submit_preflight_iter009.slurm"
write_config "${PREFLIGHT_DIR}" \
  "ITERATION_ID=iter009" "STAGE=preflight" "REPOSITORY_COMMIT=${HEAD}" \
  "SOURCE_MANIFEST=${ITER_DIR}/iter009_source_manifest.sha256" "MICROMAMBA_MODULE=${MODULE}" \
  "MICROMAMBA_ENV=${ENV}" "PREFLIGHT_RUN_DIR=${PREFLIGHT_DIR}" "MATRIX_ROOT=${ROOT}" \
  "FORCING_ARTIFACT=${FORCING}" "SPINUP_ARTIFACT=${SPINUP}" "DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}" \
  "PREFLIGHT_SMOKE_ROOT=${PREFLIGHT_DIR}/smoke"

cp "${ITER_DIR}/initialize_iter009.slurm" "${INIT_DIR}/submit_initialize_iter009.slurm"
write_config "${INIT_DIR}" \
  "ITERATION_ID=iter009" "STAGE=initialize" "REPOSITORY_COMMIT=${HEAD}" \
  "SOURCE_MANIFEST=${ITER_DIR}/iter009_source_manifest.sha256" "MICROMAMBA_MODULE=${MODULE}" \
  "MICROMAMBA_ENV=${ENV}" "ABBY_RAW=${ABBY_RAW}" "JERC_RAW=${JERC_RAW}" \
  "ITER008_RAW_MANIFEST=${INIT_DIR}/iter008_raw_manifest.sha256" "INITIALIZATION_DIR=${INIT_DIR}"

readonly VALIDATE_DIR="${ROOT}/spinup_forcing_coupling_iter009_validate"
cp "${ITER_DIR}/validate_iter009.slurm" "${VALIDATE_DIR}/submit_validate_iter009.slurm"
write_config "${VALIDATE_DIR}" \
  "ITERATION_ID=iter009" "STAGE=validate" "REPOSITORY_COMMIT=${HEAD}" \
  "SOURCE_MANIFEST=${ITER_DIR}/iter009_source_manifest.sha256" "MICROMAMBA_MODULE=${MODULE}" \
  "MICROMAMBA_ENV=${ENV}" "VALIDATOR=${ITER_DIR}/validate_iter009.py" "OUTPUT_ROOT=${ROOT}" \
  "DEPENDENCY_MANIFEST=${DEPENDENCY_MANIFEST}"

echo "MATERIALIZE_PASS root=${ROOT} head=${HEAD}"
