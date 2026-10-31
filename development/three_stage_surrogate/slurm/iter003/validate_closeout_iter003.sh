#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly OUTPUT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter003_abby_jerc_spinup_config"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly AGGREGATE_SHA256="eae3ef79d12d49d5d2c2b9eef71b1699d1e15628f2c19ccab876ee5e8cab4ab7"
readonly RANKING_SHA256="63c864b4539a939c625605bd714ac39e9a6739ffd15f060a98c7ebe4ff6c65ae"
readonly VALIDATION_SHA256="27f6a5431f09f77250c789c16bb60bec45265eed3618cbd17c3351f68a2d9d38"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter003.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter003/summary.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"

for path in "${REPORT}" "${SUMMARY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter003' "${path}"
  grep -q 'experiment' "${path}"
  grep -q 'candidate 74' "${path}"
  grep -q '819' "${path}"
  grep -q '205' "${path}"
  grep -q 'pass' "${path}"
done
grep -q -- '- Status: `completed`' "${REPORT}"
grep -q -- '- Phase: `closed`' "${REPORT}"
grep -q -- '- Status: `completed`' "${HANDOFF}"
grep -q -- '- Phase: `closed`' "${HANDOFF}"
grep -q -- '- Active job scope: none' "${HANDOFF}"
grep -q "${PLAN_SHA256}" "${REPORT}"
grep -q "${PLAN_SHA256}" "${HANDOFF}"

readonly TMPDIR_ITER003="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_ITER003}"' EXIT
sed -n '/^### Iter004 - ABBY\/JERC frozen spinup artifact and GPP handoff$/,/^## Closeout Checklist$/p' "${REPORT}" | sed '$d' | sed '$d' > "${TMPDIR_ITER003}/report_proposal"
sed -n '/^### Iter004 - ABBY\/JERC frozen spinup artifact and GPP handoff$/,$p' "${HANDOFF}" > "${TMPDIR_ITER003}/handoff_proposal"
diff -u "${TMPDIR_ITER003}/report_proposal" "${TMPDIR_ITER003}/handoff_proposal"

[[ "$(grep -c '^iter003,' "${REGISTRY}")" -eq 1 ]]
grep '^iter003,' "${REGISTRY}" | grep -q ',completed,experiment,'
grep '^iter003,' "${REGISTRY}" | grep -q ',pass,Freeze candidate 74'
grep '^iter003,' "${REGISTRY}" | grep -q 'summaries/iter003,committed'

[[ "$(sha256sum "${OUTPUT}/runs/aggregate/attempt_1/aggregate.json" | cut -d' ' -f1)" == "${AGGREGATE_SHA256}" ]]
[[ "$(sha256sum "${OUTPUT}/runs/aggregate/attempt_1/candidate_ranking.csv" | cut -d' ' -f1)" == "${RANKING_SHA256}" ]]
[[ "$(sha256sum "${OUTPUT}/runs/validation/attempt_1/validation_report.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
cmp -s "${OUTPUT}/runs/validation/attempt_1/validation_report.json" "${CAMPAIGN}/summaries/iter003/validation_report.json"

[[ "$(jq -r '.result' "${OUTPUT}/runs/validation/attempt_1/validation_report.json")" == "pass" ]]
[[ "$(jq -r '.selected_candidate_id' "${OUTPUT}/runs/validation/attempt_1/validation_report.json")" == "74" ]]
[[ "$(jq -r '.fixed_test_access' "${OUTPUT}/runs/validation/attempt_1/validation_report.json")" == "false" ]]
[[ "$(jq -r '.model_artifacts_created' "${OUTPUT}/runs/validation/attempt_1/validation_report.json")" == "false" ]]
[[ "$(jq -r '.selected_candidate_id' "${OUTPUT}/runs/aggregate/attempt_1/aggregate.json")" == "74" ]]
[[ "$(jq -r '.eligible_count' "${OUTPUT}/runs/aggregate/attempt_1/aggregate.json")" == "42" ]]

for job_id in 24472427 24472428 24472431 24475235 24475275; do
  grep -q "${job_id}" "${REPORT}"
done
grep -q 'ITER003_PREFLIGHT_OK' "${REPORT}"
grep -q 'ITER003_VALIDATE_OK' "${REPORT}"

echo "ITER003_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=freeze_candidate_74 active_jobs=0"
