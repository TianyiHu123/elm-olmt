#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release"
readonly AGGREGATE="${RUN_ROOT}/runs/aggregate/attempt_3"
readonly ROBUSTNESS="${RUN_ROOT}/runs/robustness/attempt_1"
readonly STABLE_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly METRICS_SHA256="0c5f13f28adc3490cec1c64f931b017261c1eb968ac513f304f388c57966a366"
readonly ESTIMATES_SHA256="2dcb974ef4c54b85f091bd5b8b97d8600542fd87da8f0946c859d636a1aae790"
readonly NETCDF_SHA256="cd0fc5a7406b7259888dc7670cc9ab070e0b7fd23d32db065a6555ebf05e92d4"
readonly REPORT_SHA256="b908b94aed612538ae1b9afc2695b2642fe483383616ce04635879d053ee0ea9"
readonly VALIDATION_SHA256="f95fccbfe676595613386be50e59e2c12c18332face59bb8b17fc7f6dbcb5d07"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly ITERATION_REPORT="${CAMPAIGN}/iterations/iter006.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter006/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter006/evidence.sha256"

for path in "${ITERATION_REPORT}" "${SUMMARY}" "${REGISTRY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter006' "${path}"
  grep -q 'implementation' "${path}"
  grep -q 'optimization_required\|Optimization required' "${path}"
  grep -q 'fail' "${path}"
done
grep -q -- '- Status: `completed`' "${ITERATION_REPORT}"
grep -q -- '- Phase: `closed`' "${ITERATION_REPORT}"
grep -q -- '- Status: `completed`' "${HANDOFF}"
grep -q -- '- Phase: `closed`' "${HANDOFF}"
grep -q -- '- Active job scope: none' "${HANDOFF}"
grep -q "${PLAN_SHA256}" "${ITERATION_REPORT}"
grep -q "${PLAN_SHA256}" "${HANDOFF}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${ITERATION_REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}"

[[ "$(grep -c '^iter006,' "${REGISTRY}")" -eq 1 ]]
grep '^iter006,' "${REGISTRY}" | grep -q ',completed,implementation,'
grep '^iter006,' "${REGISTRY}" | grep -q ',fail,Optimization required; publish no GPP artifact or SR handoff,'
grep '^iter006,' "${REGISTRY}" | grep -q 'summaries/iter006,committed'
grep '^iter006,' "${REGISTRY}" | grep -q 'validator=validate_closeout_iter006.sh'

[[ "$(sha256sum "${AGGREGATE}/metric_distribution.csv" | cut -d' ' -f1)" == "${METRICS_SHA256}" ]]
[[ "$(sha256sum "${AGGREGATE}/uncertainty_estimates.csv" | cut -d' ' -f1)" == "${ESTIMATES_SHA256}" ]]
[[ "$(sha256sum "${AGGREGATE}/gpp_uncertainty.nc" | cut -d' ' -f1)" == "${NETCDF_SHA256}" ]]
[[ "$(sha256sum "${AGGREGATE}/uncertainty_report.json" | cut -d' ' -f1)" == "${REPORT_SHA256}" ]]
[[ "$(sha256sum "${AGGREGATE}/aggregate_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
grep -q "${METRICS_SHA256}" "${EVIDENCE}"
grep -q "${VALIDATION_SHA256}" "${EVIDENCE}"

[[ "$(jq -r '.result' "${AGGREGATE}/aggregate_validation.json")" == "pass" ]]
[[ "$(jq -r '.gate.result' "${AGGREGATE}/aggregate_validation.json")" == "fail" ]]
[[ "$(jq -r '.metric_rows' "${AGGREGATE}/aggregate_validation.json")" == "240" ]]
[[ "$(jq -r '.uncertainty_rows' "${AGGREGATE}/aggregate_validation.json")" == "84" ]]
[[ "$(jq -r '.fixed_test_access' "${AGGREGATE}/aggregate_validation.json")" == "false" ]]
[[ "$(wc -l < "${AGGREGATE}/metric_distribution.csv")" -eq 241 ]]
[[ "$(wc -l < "${AGGREGATE}/uncertainty_estimates.csv")" -eq 85 ]]

for split in $(seq -w 0 19); do
  [[ "$(jq -r '.result' "${ROBUSTNESS}/split_${split}/split_report.json")" == "pass" ]]
  [[ "$(jq -r '.result' "${ROBUSTNESS}/split_${split}/reload_validation.json")" == "pass" ]]
  [[ "$(jq -r '.fixed_test_access' "${ROBUSTNESS}/split_${split}/split_report.json")" == "false" ]]
done

for job_id in 24489883 24489912 24489937 24491172 24491252 24491301; do
  grep -q "${job_id}" "${ITERATION_REPORT}"
done
grep -q '0.708444 / 0.85' "${COMPACT}"
grep -q '0.028777 / 0.75' "${COMPACT}"
grep -q 'No next iteration proposal is authorized' "${ITERATION_REPORT}"
grep -q 'Explicit terminal declaration' "${HANDOFF}"
[[ ! -e "${STABLE_ROOT}" ]]

echo "ITER006_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=fail decision=optimization_required active_jobs=0 release=absent"
