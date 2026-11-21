#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter007_abby_jerc_gpp_config"
readonly SCREEN_AGG="${RUN_ROOT}/runs/screen_aggregate/attempt_1"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_1"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly FINALIST_SHA256="f0a97d89040c1b9f2d0f82c31b7989b7796cda3fba0ff59272f2ba74b7dc24ad"
readonly METRICS_SHA256="abf7e60ef8030c0e4043841bbd6b2e4663578444aeeaf9d960e06cc12cb0b662"
readonly RANKING_SHA256="0beaac63e6ee6817ec078ef928af32d7b8cd7fe126c6453041bd614e03ec8c63"
readonly SELECTION_SHA256="d90cf503ac52181213dee0ab91ed2518879208f84192a32292cc950d1314e745"
readonly VALIDATION_SHA256="6edaf171f1c536081915bf4d9a9883b3174ee5b51a17299ac385c8703fadd728"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter007.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter007/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter007/evidence.sha256"

for path in "${REPORT}" "${SUMMARY}" "${REGISTRY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter007' "${path}"
  grep -q 'experiment' "${path}"
  grep -q 'configuration_selected_gate_pass' "${path}"
  grep -q 'candidate 21\|Candidate 21' "${path}"
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

[[ "$(grep -c '^iter007,' "${REGISTRY}")" -eq 1 ]]
grep '^iter007,' "${REGISTRY}" | grep -q ',completed,experiment,'
grep '^iter007,' "${REGISTRY}" | grep -q ',pass,configuration_selected_gate_pass; select candidate 21 for fresh robustness; no release authorized,'
grep '^iter007,' "${REGISTRY}" | grep -q 'summaries/iter007,committed'
grep '^iter007,' "${REGISTRY}" | grep -q 'validator=validate_closeout_iter007.sh'

[[ "$(sha256sum "${SCREEN_AGG}/finalist_manifest.json" | cut -d' ' -f1)" == "${FINALIST_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_metric_distribution.csv" | cut -d' ' -f1)" == "${METRICS_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_ranking.csv" | cut -d' ' -f1)" == "${RANKING_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/selection_report.json" | cut -d' ' -f1)" == "${SELECTION_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
grep -q "${METRICS_SHA256}" "${EVIDENCE}"
grep -q "${VALIDATION_SHA256}" "${EVIDENCE}"
[[ "$(sha256sum "${CAMPAIGN}/summaries/iter007/finalist_manifest.json" | cut -d' ' -f1)" == "${FINALIST_SHA256}" ]]
cmp -s <(tr -d '\r' < "${FINAL}/final_metric_distribution.csv") "${CAMPAIGN}/summaries/iter007/final_metric_distribution.csv"
cmp -s <(tr -d '\r' < "${FINAL}/final_ranking.csv") "${CAMPAIGN}/summaries/iter007/final_ranking.csv"
cmp -s <(tr -d '\r' < "${SCREEN_AGG}/screen_ranking.csv") "${CAMPAIGN}/summaries/iter007/screen_ranking.csv"
[[ "$(sha256sum "${CAMPAIGN}/summaries/iter007/selection_report.json" | cut -d' ' -f1)" == "${SELECTION_SHA256}" ]]
[[ "$(sha256sum "${CAMPAIGN}/summaries/iter007/final_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]

[[ "$(jq -r '.result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.best_candidate_id' "${FINAL}/final_validation.json")" == "21" ]]
[[ "$(jq -r '.selection_gate_result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.decision' "${FINAL}/final_validation.json")" == "configuration_selected_gate_pass" ]]
[[ "$(jq -r '.independently_recomputed_leaf_count' "${FINAL}/final_validation.json")" == "120" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.release_authorized' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.best_candidate.hidden_layer_sizes | join(",")' "${FINAL}/selection_report.json")" == "64,32" ]]
[[ "$(jq -r '.best_candidate.activation' "${FINAL}/selection_report.json")" == "tanh" ]]
[[ "$(jq -r '.best_candidate.alpha' "${FINAL}/selection_report.json")" == "0.0001" ]]
[[ "$(wc -l < "${FINAL}/final_metric_distribution.csv")" -eq 481 ]]
[[ "$(wc -l < "${FINAL}/final_ranking.csv")" -eq 7 ]]
[[ "$(awk -F, 'NR==2 {print $2}' "${FINAL}/final_ranking.csv")" == "21" ]]

for job_id in 24494841 24494873 24494900 24506893 24507062 24512103; do
  grep -q "${job_id}" "${REPORT}"
done
grep -q 'Batch job submission failed: Job dependency problem' "${REPORT}"
grep -q '268 allocations' "${REPORT}"
grep -q 'This proposal grants no runtime authority' "${REPORT}"
grep -q 'This proposal grants no runtime authority' "${HANDOFF}"
grep -q 'This proposal grants no runtime authority' "${COMPACT}"

echo "ITER007_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=configuration_selected_gate_pass best=21 active_jobs=0 release=absent"
