#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter008_abby_jerc_gpp_release"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_2"
readonly DIAGNOSTIC="${RUN_ROOT}/runs/diagnostic/attempt_2/diagnostic_report.json"
readonly RELEASE_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc"
readonly RELEASE="${RELEASE_ROOT}/release_0001"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly DIAGNOSTIC_SHA256="13b0d9ce9a5d2acaf5a06175ab016ad81053ea29fa8d2fce72f62f2c9aca0cda"
readonly FINAL_SHA256="48d518d9b31defb33892c5d6b4d93c0700f7bc7f55a90dd0206e0b9a57602893"
readonly ARTIFACT_SHA256="67214897f16e536f450b34275e5fd19e435e4cc657048fc3194beca500928ec9"
readonly HANDOFF_SHA256="c905fc60803405ba80b1ee7e4d7b489d1aeb3edc1b918ca2f07d8df9b0d198bb"
readonly RELEASE_SHA256="57cc18b063ab46a4cd07a3bd4e03ab1bfd05fb81894b097277d3c667135370d1"
readonly CATALOG_SHA256="ad48809596e416276483d1a9d223d813cc59708cb3b045036723e255663e2665"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter008.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter008/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter008/evidence.sha256"

for path in "${REPORT}" "${SUMMARY}" "${REGISTRY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter008' "${path}"
  grep -q 'implementation' "${path}"
  grep -q 'gpp_release_published' "${path}"
  grep -q 'pass' "${path}"
done
grep -q -- '- Status: `completed`' "${REPORT}"
grep -q -- '- Phase: `closed`' "${REPORT}"
grep -q -- '- Status: `completed`' "${HANDOFF}"
grep -q -- '- Phase: `closed`' "${HANDOFF}"
grep -q -- '- Active job scope: none' "${HANDOFF}"
grep -q "${PLAN_SHA256}" "${REPORT}"
grep -q "${PLAN_SHA256}" "${HANDOFF}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}"

[[ "$(grep -c '^iter008,' "${REGISTRY}")" -eq 1 ]]
grep '^iter008,' "${REGISTRY}" | grep -q ',completed,implementation,'
grep '^iter008,' "${REGISTRY}" | grep -q ',pass,gpp_release_published;'
grep '^iter008,' "${REGISTRY}" | grep -q 'summaries/iter008,committed'
grep '^iter008,' "${REGISTRY}" | grep -q 'validator=validate_closeout_iter008.sh'

[[ "$(sha256sum "${DIAGNOSTIC}" | cut -d' ' -f1)" == "${DIAGNOSTIC_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_report.json" | cut -d' ' -f1)" == "${FINAL_SHA256}" ]]
[[ "$(sha256sum "${RELEASE}/artifact/gpp_surrogate_artifact.pkl" | cut -d' ' -f1)" == "${ARTIFACT_SHA256}" ]]
[[ "$(sha256sum "${RELEASE}/handoff/gpp_predicted_for_sr.nc" | cut -d' ' -f1)" == "${HANDOFF_SHA256}" ]]
[[ "$(sha256sum "${RELEASE}/release_manifest.json" | cut -d' ' -f1)" == "${RELEASE_SHA256}" ]]
[[ "$(sha256sum "${RELEASE_ROOT}/catalog.json" | cut -d' ' -f1)" == "${CATALOG_SHA256}" ]]
for hash in "${DIAGNOSTIC_SHA256}" "${FINAL_SHA256}" "${ARTIFACT_SHA256}" "${HANDOFF_SHA256}" "${RELEASE_SHA256}" "${CATALOG_SHA256}"; do
  grep -q "${hash}" "${EVIDENCE}"
done

[[ "$(jq -r '.result' "${FINAL}/final_report.json")" == "pass" ]]
[[ "$(jq -r '.metric_rows' "${FINAL}/final_report.json")" == "240" ]]
[[ "$(jq -r '.uncertainty_rows' "${FINAL}/final_report.json")" == "84" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_report.json")" == "false" ]]
[[ "$(jq -r '.performance_gate_applied' "${FINAL}/final_report.json")" == "false" ]]
[[ "$(jq -r '.result' "${RELEASE}/uncertainty/aggregate_validation.json")" == "pass" ]]
[[ "$(jq -r '.gate.result' "${RELEASE}/uncertainty/aggregate_validation.json")" == "not_applicable" ]]
[[ "$(jq -r '.gate.applied' "${RELEASE}/uncertainty/aggregate_validation.json")" == "false" ]]
[[ "$(jq -r '.result' "${RELEASE}/validation/validation_report.json")" == "pass" ]]
[[ "$(jq -r '.fit_member_count' "${RELEASE}/validation/validation_report.json")" == "819" ]]
[[ "$(jq -r '.handoff_prediction_count' "${RELEASE}/validation/validation_report.json")" == "100442160" ]]
[[ "$(jq -r '.fixed_test_access' "${RELEASE}/validation/validation_report.json")" == "false" ]]
[[ "$(jq -r '.current_manifest_sha256' "${RELEASE_ROOT}/catalog.json")" == "${RELEASE_SHA256}" ]]
[[ "$(wc -l < "${RELEASE}/uncertainty/metric_distribution.csv")" -eq 241 ]]
[[ "$(wc -l < "${RELEASE}/uncertainty/uncertainty_estimates.csv")" -eq 85 ]]

verified=0
while IFS=$'\t' read -r expected relative expected_size; do
  [[ "$(sha256sum "${RELEASE}/${relative}" | cut -d' ' -f1)" == "${expected}" ]]
  [[ "$(stat -c '%s' "${RELEASE}/${relative}")" == "${expected_size}" ]]
  verified=$((verified + 1))
done < <(jq -r '.files[] | [.sha256,.path,.size_bytes] | @tsv' "${RELEASE}/release_manifest.json")
[[ "${verified}" -eq 13 ]]

for job_id in 24512852 24513943 24520151 24523438 24523491 24523514 24523529; do
  grep -q "${job_id}" "${REPORT}"
done
grep -q 'No next iteration proposal is authorized' "${REPORT}"
grep -qi 'Explicit terminal declaration' "${HANDOFF}"
grep -q 'No next iteration is authorized' "${COMPACT}"

echo "ITER008_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=gpp_release_published active_jobs=0 release=release_0001 files=13"
