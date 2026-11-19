#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly COMPACT="${CAMPAIGN}/summaries/iter015"
readonly REPORT="${CAMPAIGN}/iterations/iter015.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly EXT_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness"
readonly PRODUCTS="${EXT_ROOT}/products"
readonly EXT_HANDOFF="${EXT_ROOT}/handoff"
readonly FINAL_REPORT="${EXT_ROOT}/runs/final/attempt_1/final_validation_report.json"
readonly PLAN_SHA="6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d"
readonly EXECUTION_MANIFEST_SHA="ff075e65031b8cd2cb4fc19558799c35b989e1d00711aa0096f368762a525b9b"
readonly AGGREGATE_REPORT_SHA="c06454a70020e0b5ad141baade9dcf7e6242c08cc8af99540f59b0e113610744"
readonly FINAL_REPORT_SHA="fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6"
readonly PRODUCTS_MANIFEST_SHA="293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9"
readonly DECISION="full_chain_robustness_characterized"

[[ "${1:-}" == "--active-job-count" && "${2:-}" == "0" && $# -eq 2 ]]
[[ "$(grep -c '^iter015,' "${REGISTRY}")" -eq 1 ]]
readonly REGISTRY_ROW="$(grep '^iter015,' "${REGISTRY}")"
readonly SUMMARY_SECTION="$(awk '
  /^## iter015 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter015 - / { exit }
  capture { print }
' "${SUMMARY}")"
[[ -n "${SUMMARY_SECTION}" ]]

for source in "${REPORT}" "${HANDOFF}" "${COMPACT}/summary.md"; do
  grep -q "${DECISION}" "${source}"
  grep -qi 'no next iteration is proposed or authorized' "${source}"
  grep -qi 'fixed-test' "${source}"
  grep -qi 'all-development fit\|all-development refit' "${source}"
  grep -q "${PLAN_SHA}" "${source}"
done

grep -q 'Iteration ID: `iter015`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${REPORT}"
! grep -q 'independent review pending\|independent result review pending' "${REPORT}"
grep -q 'Last closed iteration: `iter015`' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Alignment: `aligned`' "${HANDOFF}"
grep -q 'approved deviation: `none`' "${HANDOFF}"
grep -q 'Status/work type: `completed` / `experiment`' <<<"${SUMMARY_SECTION}"
grep -q "${DECISION}" <<<"${SUMMARY_SECTION}"
grep -q ',completed,experiment,Characterize ABBY/JERC full-chain robustness' <<<"${REGISTRY_ROW}"
grep -q ',pass,"full_chain_robustness_characterized;' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=1338f8aa11afb5cedbf51797d965ee928890702b' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Complete full-chain surrogate robustness' <<<"${REGISTRY_ROW}"

for job_id in 24700507 24700675 24711922 24717714 24717815; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
  grep -q "^${job_id}," "${COMPACT}/job_accounting.csv"
done

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter015/iter015_execution_manifest.sha256" | cut -d' ' -f1)" == "${EXECUTION_MANIFEST_SHA}" ]]
[[ "$(sha256sum "${FINAL_REPORT}" | cut -d' ' -f1)" == "${FINAL_REPORT_SHA}" ]]
[[ "$(sha256sum "${PRODUCTS}/products_manifest.json" | cut -d' ' -f1)" == "${PRODUCTS_MANIFEST_SHA}" ]]
[[ "$(sha256sum "${PRODUCTS}/aggregate_report.json" | cut -d' ' -f1)" == "${AGGREGATE_REPORT_SHA}" ]]
(cd "${COMPACT}" && sha256sum -c evidence.sha256)

[[ "$(jq -r '.result' "${FINAL_REPORT}")" == pass ]]
[[ "$(jq -r '.split_count' "${FINAL_REPORT}")" == 20 ]]
[[ "$(jq -r '.gpp_output_policy' "${FINAL_REPORT}")" == hard_zero_v1 ]]
[[ "$(jq -r '.joint_density_grid_shape | join("x")' "${FINAL_REPORT}")" == 200x200 ]]
[[ "$(jq -r '.fixed_test_access,.all_development_fit,.cross_fitting,.release_modified,.performance_threshold_applied' "${FINAL_REPORT}" | paste -sd / -)" == false/false/false/false/false ]]
[[ "$(jq -r '.aggregate_output_hash_count,.staged_product_files,.cn_covariance_rows,.cn_member_balanced_covariance_rows,.propagation_correlation_rows,.balanced_propagation_correlation_rows,.gpp_sr_correlation_rows,.density_panels' "${FINAL_REPORT}" | paste -sd / -)" == 27/28/160/8/180/9/120/6 ]]
[[ "$(jq -r '.result' "${COMPACT}/final_validation.json")" == pass ]]
[[ "$(jq -r '.decision' "${COMPACT}/final_validation.json")" == "${DECISION}" ]]
[[ "$(wc -l < "${COMPACT}/selected_metrics.csv")" -eq 17 ]]
[[ "$(wc -l < "${COMPACT}/job_accounting.csv")" -eq 6 ]]
[[ "$(find "${PRODUCTS}" -maxdepth 1 -type f | wc -l)" -eq 29 ]]
[[ "$(find "${EXT_HANDOFF}" -maxdepth 1 -type f | wc -l)" -eq 3 ]]

echo ITER015_FOUR_RECORD_VALIDATE_PASS
