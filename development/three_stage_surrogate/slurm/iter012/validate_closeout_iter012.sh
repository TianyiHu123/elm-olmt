#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter012_abby_jerc_sr_gpp_ablation"
readonly UNIT1="${RUN_ROOT}/runs/unit1/attempt_3/unit1_report.json"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_1"
readonly PLAN_SHA256="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly MANIFEST_FILE_SHA256="bc83f399e9891769766a49f2e24cb8068640783b64d76f1f2d44249fc532d9b3"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter012.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter012"
readonly SUMMARY_SECTION="$(awk '
  /^## iter012 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter012 - / { exit }
  capture { print }
' "${SUMMARY}")"
readonly REGISTRY_ROW="$(grep '^iter012,' "${REGISTRY}")"

[[ -n "${SUMMARY_SECTION}" ]]
[[ "$(grep -c '^iter012,' "${REGISTRY}")" -eq 1 ]]

for source in "${REPORT}" "${HANDOFF}" "${COMPACT}/summary.md"; do
  grep -q 'deployable_arm_B_selected' "${source}"
  grep -q '(96,48)' "${source}"
  grep -q 'alpha `0.01`' "${source}"
  grep -q '19/20' "${source}"
  grep -q '7.727%' "${source}"
  grep -qi 'non-deployable' "${source}"
  grep -qi 'not a mathematical upper bound' "${source}"
  grep -qi 'fixed-test' "${source}"
  grep -q 'No next iteration is authorized' "${source}"
done

grep -q 'Iteration ID: `iter012`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"
grep -q 'Last closed iteration: `iter012`' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Status/work type: `completed` / `experiment`' <<<"${SUMMARY_SECTION}"
grep -q 'deployable_arm_B_selected' <<<"${SUMMARY_SECTION}"
grep -q ',completed,experiment,Determine whether same-hour predicted GPP' <<<"${REGISTRY_ROW}"
grep -q ',pass,"deployable_arm_B_selected;' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=70cd248c07b0bea9d49bfe25c55870237a5939a6' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Complete SR GPP input ablation' <<<"${REGISTRY_ROW}"
grep -q 'validator=validate_closeout_iter012.sh' <<<"${REGISTRY_ROW}"

for source in "${REPORT}" "${HANDOFF}"; do
  grep -q "${PLAN_SHA256}" "${source}"
  grep -q 'Alignment: `aligned`' "${source}"
  grep -qi 'approved deviation: `none`' "${source}"
  grep -q 'Campaign-plan amendment recommendation: `none`' "${source}"
done
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}/summary.md"

for job_id in 24618587 24621652 24623717 24623755 24630916; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
done

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA256}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter012/iter012_execution_manifest.sha256" | cut -d' ' -f1)" == "${MANIFEST_FILE_SHA256}" ]]

check_hash() {
  local expected="$1"
  local path="$2"
  [[ "$(sha256sum "${path}" | cut -d' ' -f1)" == "${expected}" ]]
  grep -q "${expected}" "${COMPACT}/evidence.sha256"
}

check_hash 69222e112397aef90030e0c0865c7674270d54e5319a835dda102597c7426d3a "${COMPACT}/feature_schemas.json"
check_hash 5203a3e280aa44bf88efbecfbc0a97e83d4d1b86878e7bd8bfe9ff2ed5850f78 "${COMPACT}/final_selection_report.json"
check_hash 22640ce201a964109331ce29ed94560e9e027c751d194120afee674a45cba89a "${COMPACT}/final_validation.json"
check_hash e1ef748c530125bd0e867977ff5f7b6fe91c10d7655b9f151fe522d903c8174e "${COMPACT}/repeated_split_manifest.json"
check_hash ea90e393226b99b2b2355b5aee46adad92ee9c032a9d3fd71a028cb6f84c02f7 "${COMPACT}/unit1_report.json"
check_hash 9f9b7c2f26e66b2844ab907ad3ee8ed2b5ae1af8cb58f88f59fad155278bea87 "${COMPACT}/validation_r2_distributions.png"
check_hash df7c725a2e9bd8642f61fad2f1f01e38c3c323204b3095980880e74d045a469a "${COMPACT}/validation_rmse_distributions.png"
check_hash bc83f399e9891769766a49f2e24cb8068640783b64d76f1f2d44249fc532d9b3 "${CAMPAIGN}/slurm/iter012/iter012_execution_manifest.sha256"
check_hash cd5f409e930d694d814d3309c295d52461508f8526ef86b605c7ee21f69d3c23 "${COMPACT}/metric_distribution.csv"
check_hash a95b424825fc91e6def5ec36c280ed7830ab692ee800264717e17ee66fc51a40 "${COMPACT}/metric_summary.csv"
check_hash 1b6ea849161bdc83a6ea8e86867a2958922eef0a7ad41632ada1cd187c0dafd4 "${COMPACT}/overall_comparison.csv"
check_hash 3b58e0fa5cd830c9e7c0220be821cf62721e5e84fb61a2752ec0fdfbe9d2b5cc "${COMPACT}/paired_comparisons.csv"
check_hash 4619e345883f449009661a1165b207a1ca1c0e80cd546bc68135da14f81cdb0b "${COMPACT}/site_validation.csv"
check_hash 084a1c38e3cb413ec1001c7c87baa37761c2845dd87d83930a6a1e7584e27a38 "${COMPACT}/train_validation_gap_distribution.csv"
check_hash fd49b530e27b8c26397015a27145050858de611b0026334b0ca36e6af7dbabba "${COMPACT}/train_validation_gap_summary.csv"

check_hash d2ccbca35327239266b0cd31b1f8c451746259e6ca72098375e8307030261c73 "${FINAL}/metric_distribution.csv"
check_hash c687726c84675a0f782e6295d72c473efeec92c9f231e543695368631a251d9d "${FINAL}/metric_summary.csv"
check_hash 2c9a04eda3b48d7e1aaddb938a2bb657eee7a1d3a19f5f4b03f59acd0adf0c5a "${FINAL}/overall_comparison.csv"
check_hash 9cecb397d44b60f2d14f513f09e72ef0a9a8f2985c9ab3f3d8830135890e6c06 "${FINAL}/paired_comparisons.csv"
check_hash 1ed2dbea861b223629b9ea1d1f1faeeddb7d7646ba577c749d4706f50e029d2f "${FINAL}/site_validation.csv"
check_hash b5c3665644e8bb9c0881343c900498f9895520f4dc1a6ba13bb901d40dcef7db "${FINAL}/train_validation_gap_distribution.csv"
check_hash 6f587311982ce126d5ddab72e1a72b15ed358d09b283cade514351d5247eac32 "${FINAL}/train_validation_gap_summary.csv"

[[ "$(jq -r '.result' "${UNIT1}")" == "pass" ]]
[[ "$(jq -r '.fresh_splits' "${UNIT1}")" == "20" ]]
[[ "$(jq -r '.production_fit_count' "${UNIT1}")" == "60" ]]
[[ "$(jq -r '.fixed_test_access' "${UNIT1}")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_selection_report.json")" == "pass" ]]
[[ "$(jq -r '.decision' "${FINAL}/final_selection_report.json")" == "deployable_arm_B_selected" ]]
[[ "$(jq -r '.selected_deployable_arm' "${FINAL}/final_selection_report.json")" == "B" ]]
[[ "$(jq -r '.retained_deployable_arm' "${FINAL}/final_selection_report.json")" == "B" ]]
[[ "$(jq -r '.production_fit_count' "${FINAL}/final_selection_report.json")" == "60" ]]
[[ "$(jq -r '.validation_metric_rows' "${FINAL}/final_selection_report.json")" == "360" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.true_gpp_substantially_more_informative' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.oracle_is_mathematical_upper_bound' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.decision_reproduced' "${FINAL}/final_validation.json")" == "true" ]]
[[ "$(jq -r '.recomputed_validation_metric_rows' "${FINAL}/final_validation.json")" == "360" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.spinup_execution' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.gpp_execution' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.all_development_fit' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_validation.json")" == "false" ]]

[[ "$(wc -l < "${COMPACT}/metric_distribution.csv")" -eq 721 ]]
[[ "$(wc -l < "${COMPACT}/metric_summary.csv")" -eq 37 ]]
[[ "$(wc -l < "${COMPACT}/overall_comparison.csv")" -eq 7 ]]
[[ "$(wc -l < "${COMPACT}/site_validation.csv")" -eq 13 ]]
[[ "$(wc -l < "${COMPACT}/paired_comparisons.csv")" -eq 73 ]]
[[ "$(wc -l < "${COMPACT}/train_validation_gap_distribution.csv")" -eq 361 ]]
[[ "$(wc -l < "${COMPACT}/train_validation_gap_summary.csv")" -eq 19 ]]

echo "ITER012_FOUR_RECORD_VALIDATE_PASS"
