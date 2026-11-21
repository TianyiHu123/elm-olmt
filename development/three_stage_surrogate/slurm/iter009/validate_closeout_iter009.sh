#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config"
readonly UNIT1="${RUN_ROOT}/runs/unit1/attempt_1/unit1_report.json"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_1"
readonly PLAN_SHA256="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly UNIT1_SHA256="c85d288fdacbaa802f77ea76b8bc74cbfb5027f6ea16c807554ac51eca226c41"
readonly METRIC_SHA256="dfd2e2b4ec2a015bac6d2db592467f8fb47a657a6bce00f51f56084cbccf9f14"
readonly RANKING_SHA256="5666be8923f751ad4948d757471e37262a910bb8d49a4f0f0d085985dca91378"
readonly SELECTION_SHA256="4c41478468f0d0706b843a1207540325840e8491df3c42ce282647401080931c"
readonly VALIDATION_SHA256="8a0138fe390d37d2fd42e4825b7718c2b5d3b7e68be9b7a1f492d8871673967f"
readonly MANIFEST_SHA256="dbcd4d68eb355d6613fc7e75f042b04ec88f0bc7c6060bc192147aaad583ee15"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter009.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter009/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter009/evidence.sha256"

for path in "${REPORT}" "${SUMMARY}" "${REGISTRY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter009' "${path}"
  grep -q 'implementation' "${path}"
  grep -q 'sr_configuration_selected' "${path}"
  grep -q 'candidate 21' "${path}"
done

grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q '014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360' "${REPORT}"
grep -q '014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360' "${HANDOFF}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}"

[[ "$(grep -c '^iter009,' "${REGISTRY}")" -eq 1 ]]
grep '^iter009,' "${REGISTRY}" | grep -q ',completed,implementation,'
grep '^iter009,' "${REGISTRY}" | grep -q ',pass,sr_configuration_selected;'
grep '^iter009,' "${REGISTRY}" | grep -q 'summaries/iter009,committed'
grep '^iter009,' "${REGISTRY}" | grep -q 'validator=validate_closeout_iter009.sh'

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA256}" ]]
[[ "$(sha256sum "${UNIT1}" | cut -d' ' -f1)" == "${UNIT1_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_metric_distribution.csv" | cut -d' ' -f1)" == "${METRIC_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_ranking.csv" | cut -d' ' -f1)" == "${RANKING_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_selection_report.json" | cut -d' ' -f1)" == "${SELECTION_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter009/iter009_execution_manifest.sha256" | cut -d' ' -f1)" == "${MANIFEST_SHA256}" ]]
for hash in "${UNIT1_SHA256}" "${METRIC_SHA256}" "${RANKING_SHA256}" "${SELECTION_SHA256}" "${VALIDATION_SHA256}" "${MANIFEST_SHA256}"; do
  grep -q "${hash}" "${EVIDENCE}"
done

[[ "$(jq -r '.result' "${UNIT1}")" == "pass" ]]
[[ "$(jq -r '.features' "${UNIT1}")" == "44" ]]
[[ "$(jq -r '.fixed_test_access' "${UNIT1}")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_selection_report.json")" == "pass" ]]
[[ "$(jq -r '.decision' "${FINAL}/final_selection_report.json")" == "sr_configuration_selected" ]]
[[ "$(jq -r '.best_candidate_id' "${FINAL}/final_selection_report.json")" == "21" ]]
[[ "$(jq -r '.performance_gate_applied' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.best_candidate_id' "${FINAL}/final_validation.json")" == "21" ]]
[[ "$(jq -r '.recomputed_metric_rows' "${FINAL}/final_validation.json")" == "240" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(wc -l < "${FINAL}/final_metric_distribution.csv")" -eq 241 ]]
[[ "$(wc -l < "${FINAL}/final_ranking.csv")" -eq 7 ]]
[[ "$(awk -F, 'NR==2 {print $2}' "${FINAL}/final_ranking.csv")" == "21" ]]

for job_id in 24524508 24524587 24536618 24548424; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${COMPACT}"
done

echo "ITER009_FOUR_RECORD_VALIDATE_PASS"
