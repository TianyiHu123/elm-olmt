#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter011_abby_jerc_sr_capacity_regularization"
readonly UNIT1="${RUN_ROOT}/runs/unit1/attempt_2/unit1_report.json"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_2"
readonly PLAN_SHA256="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly UNIT1_SHA256="bb6356c4b4e316914c5b33d5862e763a46307948ba5c856f2c59426a00ab14b0"
readonly METRIC_SHA256="c9cb43c5567fe3498c51605ba74c68bdafb075061b952fef3760a1dbd5c58af8"
readonly CANDIDATE_SHA256="6cf0da8069f9759acf7b4d20807aabbbfba8cf537de9e0026dee99351bef89bb"
readonly SITE_SHA256="dc66af0ec5c2dc8f8a43772dbea8b51cd85e26e1c32d380ad33bb09b54d1b559"
readonly PAIRED_SHA256="a29206a841313f5ef0ac825e97552ecbb7b8fa8254ee073da7ec60e88c0a5e80"
readonly GAP_SHA256="7d1e17306fee6f0e3829215bc283bb3add906839088c2adbf4256f1652306614"
readonly SELECTION_SHA256="9eacff033dbe0e81f04172e78dded604c16b3413b52cfc79c628a2782a551865"
readonly VALIDATION_SHA256="f7bf0d1ea4a06bfae6550d99d98a176f63ff2956a75c746c2a59ab69c214ae26"
readonly MANIFEST_SHA256="7e05b0728ef80feb873cb3ea851568887c8c85ba783f6f96fad4f357c88d7b47"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter011.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter011/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter011/evidence.sha256"
readonly SUMMARY_SECTION="$(awk '
  /^## iter011 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter011 - / { exit }
  capture { print }
' "${SUMMARY}")"
readonly REGISTRY_ROW="$(grep '^iter011,' "${REGISTRY}")"

[[ -n "${SUMMARY_SECTION}" ]]
[[ "$(grep -c '^iter011,' "${REGISTRY}")" -eq 1 ]]

for source in "${REPORT}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'sr_capacity_regularization_configuration_selected' "${source}"
  grep -q '(96,48)' "${source}"
  grep -q 'alpha `0.01`' "${source}"
  grep -qi 'weaker regularization' "${source}"
  grep -qi 'capacity.*not supported' "${source}"
  grep -qi 'fixed-test' "${source}"
  grep -q 'No next iteration is' "${source}"
done

grep -q 'Iteration ID: `iter011`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"
grep -q 'Last closed iteration: `iter011`' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Status/work type: `completed` / `experiment`' <<<"${SUMMARY_SECTION}"
grep -q 'sr_capacity_regularization_configuration_selected' <<<"${SUMMARY_SECTION}"
grep -q ',completed,experiment,Compare SR MLP capacity and L2 regularization' <<<"${REGISTRY_ROW}"
grep -q ',pass,sr_capacity_regularization_configuration_selected;' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=d67845c371678db632b3844a25e344b268389199' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Complete SR capacity regularization experiment' <<<"${REGISTRY_ROW}"
grep -q 'validator=validate_closeout_iter011.sh' <<<"${REGISTRY_ROW}"

for source in "${REPORT}" "${HANDOFF}"; do
  grep -q "${PLAN_SHA256}" "${source}"
  grep -q 'Alignment: `aligned`' "${source}"
  grep -qi 'approved deviation: `none`' "${source}"
  grep -q 'Campaign-plan amendment recommendation: `none`' "${source}"
done
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}"

for job_id in 24607609 24607628 24607646 24617562 24617685; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
done

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA256}" ]]
[[ "$(sha256sum "${UNIT1}" | cut -d' ' -f1)" == "${UNIT1_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/metric_distribution.csv" | cut -d' ' -f1)" == "${METRIC_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/candidate_comparison.csv" | cut -d' ' -f1)" == "${CANDIDATE_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/site_performance.csv" | cut -d' ' -f1)" == "${SITE_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/paired_comparisons.csv" | cut -d' ' -f1)" == "${PAIRED_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/train_validation_gap_summary.csv" | cut -d' ' -f1)" == "${GAP_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_selection_report.json" | cut -d' ' -f1)" == "${SELECTION_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter011/iter011_execution_manifest.sha256" | cut -d' ' -f1)" == "${MANIFEST_SHA256}" ]]
for hash in "${UNIT1_SHA256}" "${METRIC_SHA256}" "${CANDIDATE_SHA256}" "${SITE_SHA256}" \
  "${PAIRED_SHA256}" "${GAP_SHA256}" "${SELECTION_SHA256}" "${VALIDATION_SHA256}" "${MANIFEST_SHA256}"; do
  grep -q "${hash}" "${EVIDENCE}"
done

[[ "$(jq -r '.result' "${UNIT1}")" == "pass" ]]
[[ "$(jq -r '.fresh_splits' "${UNIT1}")" == "20" ]]
[[ "$(jq -r '.candidate_count' "${UNIT1}")" == "5" ]]
[[ "$(jq -r '.fixed_test_access' "${UNIT1}")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_selection_report.json")" == "pass" ]]
[[ "$(jq -r '.decision' "${FINAL}/final_selection_report.json")" == "sr_capacity_regularization_configuration_selected" ]]
[[ "$(jq -r '.selected_candidate_id' "${FINAL}/final_selection_report.json")" == "B" ]]
[[ "$(jq -r '.effect_attribution' "${FINAL}/final_selection_report.json")" == "weaker_regularization_supported_capacity_not_supported" ]]
[[ "$(jq -r '.regularization_effect_supported' "${FINAL}/final_selection_report.json")" == "true" ]]
[[ "$(jq -r '.capacity_effect_supported' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.production_fit_count' "${FINAL}/final_selection_report.json")" == "100" ]]
[[ "$(jq -r '.validation_metric_rows' "${FINAL}/final_selection_report.json")" == "600" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.selected_candidate_id' "${FINAL}/final_validation.json")" == "B" ]]
[[ "$(jq -r '.recomputed_validation_metric_rows' "${FINAL}/final_validation.json")" == "600" ]]
[[ "$(wc -l < "${FINAL}/metric_distribution.csv")" -eq 1201 ]]
[[ "$(wc -l < "${FINAL}/candidate_comparison.csv")" -eq 21 ]]
[[ "$(wc -l < "${FINAL}/site_performance.csv")" -eq 41 ]]
[[ "$(wc -l < "${FINAL}/paired_comparisons.csv")" -eq 193 ]]
[[ "$(wc -l < "${CAMPAIGN}/slurm/iter011/iter011_execution_manifest.sha256")" -eq 20 ]]

echo "ITER011_FOUR_RECORD_VALIDATE_PASS"
