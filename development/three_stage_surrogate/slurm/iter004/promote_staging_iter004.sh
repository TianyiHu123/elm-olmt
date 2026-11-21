#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_PACKAGE="${1:?validated attempt-local release package is required}"
readonly STAGING="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter004_abby_jerc_spinup_release/staging/release_0001"

test -f "${SOURCE_PACKAGE}/release_manifest.json"
test "$(jq -r '.result' "${SOURCE_PACKAGE}/release_manifest.json")" = "validated"
test -d "${STAGING}/artifact"
test -d "${STAGING}/handoff"
test -d "${STAGING}/uncertainty"
test -d "${STAGING}/validation"
test -z "$(find "${STAGING}" -type f -print -quit)"
cp -a "${SOURCE_PACKAGE}/artifact/." "${STAGING}/artifact/"
cp -a "${SOURCE_PACKAGE}/handoff/." "${STAGING}/handoff/"
cp -a "${SOURCE_PACKAGE}/uncertainty/." "${STAGING}/uncertainty/"
cp -a "${SOURCE_PACKAGE}/validation/." "${STAGING}/validation/"
cp "${SOURCE_PACKAGE}/release_fit_report.json" "${STAGING}/release_fit_report.json"
while IFS=$'\t' read -r relative expected; do
  observed="$(sha256sum "${STAGING}/${relative}" | cut -d' ' -f1)"
  test "${observed}" = "${expected}"
done < <(jq -r '.files[] | [.path,.sha256] | @tsv' "${SOURCE_PACKAGE}/release_manifest.json")
cp "${SOURCE_PACKAGE}/release_manifest.json" "${STAGING}/release_manifest.json"
test "$(sha256sum "${STAGING}/release_manifest.json" | cut -d' ' -f1)" = \
  "$(sha256sum "${SOURCE_PACKAGE}/release_manifest.json" | cut -d' ' -f1)"
echo "ITER004_STAGING_PROMOTE_OK source=${SOURCE_PACKAGE}"
