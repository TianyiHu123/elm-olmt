#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly COMPACT="${CAMPAIGN}/summaries/iter014"
readonly REPORT="${CAMPAIGN}/iterations/iter014.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly PRODUCTS="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/products"
readonly PLAN_SHA="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly EXECUTION_MANIFEST_SHA="affa9318a266dba32681e863173c43fcb9bf5452959cc4943490b4bbd51937d1"
readonly DECISION="three_stage_inference_ready_for_robustness"

[[ "${1:-}" == "--active-job-count" && "${2:-}" == "0" && $# -eq 2 ]]
[[ "$(grep -c '^iter014,' "${REGISTRY}")" -eq 1 ]]
readonly REGISTRY_ROW="$(grep '^iter014,' "${REGISTRY}")"
readonly SUMMARY_SECTION="$(awk '
  /^## iter014 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter014 - / { exit }
  capture { print }
' "${SUMMARY}")"
[[ -n "${SUMMARY_SECTION}" ]]

for source in "${REPORT}" "${HANDOFF}" "${COMPACT}/summary.md"; do
  grep -q "${DECISION}" "${source}"
  grep -qi 'no next iteration is proposed or authorized' "${source}"
  grep -qi 'fixed-test' "${source}"
  grep -qi 'full-819 engine' "${source}"
done

grep -q 'Iteration ID: `iter014`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Work type: `integration`' "${HANDOFF}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"
grep -q 'Last closed iteration: `iter014`' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Status/work type: `completed` / `integration`' <<<"${SUMMARY_SECTION}"
grep -q "${DECISION}" <<<"${SUMMARY_SECTION}"
grep -q ',completed,integration,Implement and validate' <<<"${REGISTRY_ROW}"
grep -q ',pass,"three_stage_inference_ready_for_robustness;' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=ef49c6f4bfefcba0ef1c782b1ff6a3e8e685e14b' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Add three-stage inference engine' <<<"${REGISTRY_ROW}"

for source in "${REPORT}" "${HANDOFF}"; do
  grep -q "${PLAN_SHA}" "${source}"
  grep -q 'Alignment: `aligned`' "${source}"
  grep -qi 'approved deviation: `none`' "${source}"
  grep -q 'Campaign-plan amendment recommendation: `none`' "${source}"
done
grep -q 'amendment recommendation `none`' "${COMPACT}/summary.md"

for job_id in 24678619 24678718 24678814 24678875 24678937 24680350 24680395 24680459 24680504 24691748; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
  grep -q "^${job_id}," "${COMPACT}/job_accounting.csv"
done

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter014/iter014_execution_manifest.sha256" | cut -d' ' -f1)" == "${EXECUTION_MANIFEST_SHA}" ]]
(cd "${COMPACT}" && sha256sum -c evidence.sha256)
(cd "${PRODUCTS}" && sha256sum -c evidence.sha256)

[[ "$(jq -r '.result' "${COMPACT}/preflight_report.json")" == pass ]]
[[ "$(jq -r '.spinup_features,.gpp_features,.sr_features' "${COMPACT}/preflight_report.json" | paste -sd / -)" == 25/43/44 ]]
[[ "$(jq -r '.result' "${COMPACT}/integration_report.json")" == pass ]]
[[ "$(jq -r '.comparison_counts.TOTSOMC,.comparison_counts.TOTSOMN,.comparison_counts.GPP,.comparison_counts.SR' "${COMPACT}/integration_report.json" | paste -sd / -)" == 18/18/2592/2592 ]]
[[ "$(jq -r '.published_replay_failed_comparisons' "${COMPACT}/integration_report.json")" == 0 ]]
[[ "$(jq -r '.handoff_replay_rtol,.handoff_replay_atol,.direct_chunk_rtol,.direct_chunk_atol' "${COMPACT}/integration_report.json" | paste -sd / -)" == 0.000001/0.0001/0.000001/0.000001 ]]
[[ "$(jq -r '.serialized_outputs | length' "${COMPACT}/integration_report.json")" == 6 ]]
[[ "$(jq -r '.result' "${COMPACT}/diagnostics_manifest.json")" == pass ]]
[[ "$(jq -r '.evidence_class' "${COMPACT}/diagnostics_manifest.json")" == in_sample_development_descriptive ]]
[[ "$(jq -r '.performance_gate_applied' "${COMPACT}/diagnostics_manifest.json")" == false ]]
[[ "$(jq -r '.result' "${COMPACT}/final_validation.json")" == pass ]]
[[ "$(jq -r '.decision' "${COMPACT}/final_validation.json")" == "${DECISION}" ]]
[[ "$(jq -r '.fixed_test_access,.training_or_fitting,.full_819_engine' "${COMPACT}/final_validation.json" | paste -sd / -)" == false/false/false ]]
[[ "$(wc -l < "${COMPACT}/exact_metrics.csv")" -eq 13 ]]
[[ "$(wc -l < "${COMPACT}/gpp_sr_correlations.csv")" -eq 7 ]]
[[ "$(wc -l < "${COMPACT}/gpp_sr_conditional_bins.csv")" -eq 121 ]]
[[ "$(wc -l < "${COMPACT}/gpp_sr_night_near_zero.csv")" -eq 13 ]]
[[ "$(wc -l < "${COMPACT}/job_accounting.csv")" -eq 11 ]]

echo ITER014_FOUR_RECORD_VALIDATE_PASS
