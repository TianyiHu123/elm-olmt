#!/usr/bin/env bash
set -euo pipefail
readonly ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release"
readonly SOURCE="${ROOT}/runs/release_validation/attempt_${ITER006_RELEASE_VALIDATION_ATTEMPT:?}/release_0001"
readonly TARGET="${ROOT}/staging/release_0001"
test "$(jq -r '.result' "${SOURCE}/release_manifest.json")" = "validated"
test ! -e "${TARGET}"
cp -a "${SOURCE}" "${TARGET}"
while IFS=$'\t' read -r relative expected; do test "$(sha256sum "${TARGET}/${relative}" | cut -d' ' -f1)" = "${expected}"; done < <(jq -r '.files[] | [.path,.sha256] | @tsv' "${TARGET}/release_manifest.json")
echo "ITER006_STAGING_PROMOTE_OK manifest=$(sha256sum "${TARGET}/release_manifest.json" | cut -d' ' -f1)"
