#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE="${1:?validated release source required}"
readonly STAGING_ROOT="${2:?staging root required}"
readonly PRODUCT_ROOT="${3:?product root required}"
readonly STAGING_RELEASE="${STAGING_ROOT}/release_0001"
readonly PUBLISHED_RELEASE="${PRODUCT_ROOT}/release_0001"
readonly STAGING_TEMP="${STAGING_ROOT}/.release_0001_${SLURM_JOB_ID:?}"
readonly PUBLISH_TEMP="${PRODUCT_ROOT}/.release_0001_${SLURM_JOB_ID}"
test "$(jq -r '.result' "${SOURCE}/release_manifest.json")" = "validated"
test ! -e "${STAGING_RELEASE}"
test ! -e "${PUBLISHED_RELEASE}"
test ! -e "${PRODUCT_ROOT}/catalog.json"
mkdir -p "${STAGING_ROOT}" "${PRODUCT_ROOT}"
cp -a "${SOURCE}" "${STAGING_TEMP}"
mv "${STAGING_TEMP}" "${STAGING_RELEASE}"
cp -a "${STAGING_RELEASE}" "${PUBLISH_TEMP}"
mv "${PUBLISH_TEMP}" "${PUBLISHED_RELEASE}"
while IFS=$'\t' read -r relative expected; do
  test "$(sha256sum "${PUBLISHED_RELEASE}/${relative}" | cut -d' ' -f1)" = "${expected}"
done < <(jq -r '.files[] | [.path,.sha256] | @tsv' "${PUBLISHED_RELEASE}/release_manifest.json")
readonly MANIFEST_SHA256="$(sha256sum "${PUBLISHED_RELEASE}/release_manifest.json" | cut -d' ' -f1)"
readonly CATALOG_TEMP="${PRODUCT_ROOT}/.catalog_${SLURM_JOB_ID}.json"
jq -n \
  --arg release "release_0001" \
  --arg manifest "release_0001/release_manifest.json" \
  --arg sha256 "${MANIFEST_SHA256}" \
  '{schema:"three-stage-gpp-product-catalog-v1",current_release:$release,current_manifest:$manifest,current_manifest_sha256:$sha256,release_basis:"iter007_best_configuration",performance_gate_applied:false,storage_note:"temporary unbacked /xdisk operational publication"}' \
  > "${CATALOG_TEMP}"
mv "${CATALOG_TEMP}" "${PRODUCT_ROOT}/catalog.json"
echo "ITER008_PUBLISH_OK release=release_0001 manifest_sha256=${MANIFEST_SHA256}"
