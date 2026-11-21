#!/usr/bin/env bash
set -euo pipefail

readonly STAGING="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter004_abby_jerc_spinup_release/staging/release_0001"
readonly PRODUCT_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc"
readonly RELEASE="${PRODUCT_ROOT}/release_0001"
readonly CATALOG="${PRODUCT_ROOT}/catalog.json"

test -f "${STAGING}/release_manifest.json"
test "$(jq -r '.result' "${STAGING}/release_manifest.json")" = "validated"
test ! -e "${RELEASE}"
test ! -e "${CATALOG}"
mkdir -p "${PRODUCT_ROOT}"
cp -a "${STAGING}" "${RELEASE}"
while IFS=$'\t' read -r relative expected; do
  observed="$(sha256sum "${RELEASE}/${relative}" | cut -d' ' -f1)"
  test "${observed}" = "${expected}"
done < <(jq -r '.files[] | [.path,.sha256] | @tsv' "${RELEASE}/release_manifest.json")
readonly MANIFEST_SHA256="$(sha256sum "${RELEASE}/release_manifest.json" | cut -d' ' -f1)"
readonly TEMP_CATALOG="${PRODUCT_ROOT}/.catalog.json.tmp"
jq -n \
  --arg release "release_0001" \
  --arg manifest "release_0001/release_manifest.json" \
  --arg sha256 "${MANIFEST_SHA256}" \
  '{schema:"three-stage-spinup-product-catalog-v1",current_release:$release,current_manifest:$manifest,current_manifest_sha256:$sha256,storage_note:"temporary unbacked /xdisk operational publication"}' \
  > "${TEMP_CATALOG}"
mv "${TEMP_CATALOG}" "${CATALOG}"
echo "ITER004_PUBLISH_OK release=release_0001 manifest_sha256=${MANIFEST_SHA256}"
