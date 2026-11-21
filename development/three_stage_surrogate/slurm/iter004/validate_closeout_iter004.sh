#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter004_abby_jerc_spinup_release"
readonly STABLE_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly RELEASE_SHA256="69f840f7972d640e91b1693c2fcf71b984dae2e20fee9a07f05434af0591f2dc"
readonly ARTIFACT_SHA256="9abb342d57bf81ce933f82a5750bb56df1eaeb721f55080e3766ba76fee8a809"
readonly HANDOFF_SHA256="9e2d5be4809ee7c9053baf70ad7574ca0b5cc2afc4a15b6006663a0fb8fafdb5"
readonly VALIDATION_SHA256="b39a16e30050c0261112bc3a262d13ea686cccd1f254aa857c4559ec552419b8"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter004.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter004/summary.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"

for path in "${REPORT}" "${SUMMARY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter004' "${path}"
  grep -q 'implementation' "${path}"
  grep -q 'release_0001' "${path}"
  grep -q '819' "${path}"
  grep -q 'pass' "${path}"
done
grep -q -- '- Status: `completed`' "${REPORT}"
grep -q -- '- Phase: `closed`' "${REPORT}"
grep -q -- '- Status: `completed`' "${HANDOFF}"
grep -q -- '- Phase: `closed`' "${HANDOFF}"
grep -q -- '- Active job scope: none' "${HANDOFF}"
grep -q "${PLAN_SHA256}" "${REPORT}"
grep -q "${PLAN_SHA256}" "${HANDOFF}"

readonly TMPDIR_ITER004="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_ITER004}"' EXIT
sed -n '/^### Iter005 - ABBY\/JERC GPP input and inference-interface materialization$/,/^## Closeout Checklist$/p' "${REPORT}" | sed '$d' | sed '$d' > "${TMPDIR_ITER004}/report_proposal"
sed -n '/^### Iter005 - ABBY\/JERC GPP input and inference-interface materialization$/,$p' "${HANDOFF}" > "${TMPDIR_ITER004}/handoff_proposal"
diff -u "${TMPDIR_ITER004}/report_proposal" "${TMPDIR_ITER004}/handoff_proposal"

[[ "$(grep -c '^iter004,' "${REGISTRY}")" -eq 1 ]]
grep '^iter004,' "${REGISTRY}" | grep -q ',completed,implementation,'
grep '^iter004,' "${REGISTRY}" | grep -q ',pass,Publish and authorize spinup release_0001'
grep '^iter004,' "${REGISTRY}" | grep -q 'summaries/iter004,committed'

[[ "$(sha256sum "${STABLE_ROOT}/release_0001/release_manifest.json" | cut -d' ' -f1)" == "${RELEASE_SHA256}" ]]
[[ "$(sha256sum "${RUN_ROOT}/staging/release_0001/release_manifest.json" | cut -d' ' -f1)" == "${RELEASE_SHA256}" ]]
[[ "$(sha256sum "${STABLE_ROOT}/release_0001/artifact/spinup_release_artifact.pkl" | cut -d' ' -f1)" == "${ARTIFACT_SHA256}" ]]
[[ "$(sha256sum "${STABLE_ROOT}/release_0001/handoff/spinup_predicted_cn.nc" | cut -d' ' -f1)" == "${HANDOFF_SHA256}" ]]
[[ "$(sha256sum "${RUN_ROOT}/runs/validation/attempt_1/validation_report.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
cmp -s "${RUN_ROOT}/runs/validation/attempt_1/validation_report.json" "${CAMPAIGN}/summaries/iter004/validation_report.json"

[[ "$(jq -r '.result' "${RUN_ROOT}/runs/validation/attempt_1/validation_report.json")" == "pass" ]]
[[ "$(jq -r '.fit_member_count' "${RUN_ROOT}/runs/validation/attempt_1/validation_report.json")" == "819" ]]
[[ "$(jq -r '.fixed_test_access' "${RUN_ROOT}/runs/validation/attempt_1/validation_report.json")" == "false" ]]
[[ "$(jq -r '.current_release' "${STABLE_ROOT}/catalog.json")" == "release_0001" ]]
[[ "$(jq -r '.current_manifest_sha256' "${STABLE_ROOT}/catalog.json")" == "${RELEASE_SHA256}" ]]

for job_id in 24479223 24479279 24480121 24480153 24480174 24480199; do
  grep -q "${job_id}" "${REPORT}"
done
grep -q 'ITER004_PREFLIGHT_OK' "${REPORT}"
grep -q 'ITER004_VALIDATE_OK' "${REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${HANDOFF}"

echo "ITER004_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=publish_release_0001 active_jobs=0"
