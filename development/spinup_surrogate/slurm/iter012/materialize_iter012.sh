#!/bin/bash -e

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ITER_DIR="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012"
readonly MANIFEST="${ITER_DIR}/iter012_releases.tsv"
readonly RELEASE_SCRIPT="${ITER_DIR}/case.release_spinup_iter012.slurm"
readonly PREFLIGHT_SCRIPT="${ITER_DIR}/validate_iter012.slurm"
readonly CROSS_SCRIPT="${ITER_DIR}/validate_iter012_cross.slurm"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output

test -f "${MANIFEST}"
test -f "${RELEASE_SCRIPT}"
test -f "${PREFLIGHT_SCRIPT}"
test -f "${CROSS_SCRIPT}"
test -d "${OUTPUT_ROOT}"

readonly PREFLIGHT_ROOT="${OUTPUT_ROOT}/spinup_surrogate_iter012_preflight"
readonly VALIDATION_ROOT="${OUTPUT_ROOT}/spinup_surrogate_iter012_validation"
mkdir -p "${PREFLIGHT_ROOT}" "${VALIDATION_ROOT}"
cp "${PREFLIGHT_SCRIPT}" "${PREFLIGHT_ROOT}/validate_iter012.slurm"
cp "${CROSS_SCRIPT}" "${VALIDATION_ROOT}/validate_iter012_cross.slurm"
cmp -s "${PREFLIGHT_SCRIPT}" "${PREFLIGHT_ROOT}/validate_iter012.slurm"
cmp -s "${CROSS_SCRIPT}" "${VALIDATION_ROOT}/validate_iter012_cross.slurm"

while IFS=$'\t' read -r variant feature_count feature_subset reference_stats output_artifact; do
  if [ "${variant}" = "variant" ]; then
    continue
  fi
  test -n "${variant}"
  run_dir="${OUTPUT_ROOT}/spinup_surrogate_iter012_${variant}"
  submitted_script="${run_dir}/submit_${variant}.slurm"
  config="${run_dir}/submission_config.env"
  mkdir -p "${run_dir}/surrogate_spinup"
  cp "${RELEASE_SCRIPT}" "${submitted_script}"
  config_tmp="${config}.tmp.$$"
  printf '%s\n' \
    "VARIANT=${variant}" \
    "FEATURE_COUNT=${feature_count}" \
    "FEATURE_SUBSET=${feature_subset}" \
    "REFERENCE_STATS=${reference_stats}" \
    "OUTPUT_ARTIFACT=${output_artifact}" > "${config_tmp}"
  mv "${config_tmp}" "${config}"
  cmp -s "${RELEASE_SCRIPT}" "${submitted_script}"
  test "$(wc -l < "${config}")" -eq 5
  echo "MATERIALIZED variant=${variant} run_dir=${run_dir} script_sha256=$(sha256sum "${submitted_script}" | awk '{print $1}') config_sha256=$(sha256sum "${config}" | awk '{print $1}')"
done < "${MANIFEST}"

echo "MATERIALIZED preflight_root=${PREFLIGHT_ROOT} validation_root=${VALIDATION_ROOT}"
