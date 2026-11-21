#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly COMPACT="${CAMPAIGN}/summaries/iter013"
readonly REPORT="${CAMPAIGN}/iterations/iter013.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly STABLE="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/sr_abby_jerc"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release"
readonly PLAN_SHA="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly MANIFEST_SHA="a241214075bc5adfe350969587d18a62167bf84f37ae456074943f79ce0bda0c"
readonly RELEASE_MANIFEST_SHA="3a3d3faf8ffd1aba5af1c842732e26a25470cfa320742e0b38ff7daf5f1aed4c"

[[ "${1:-}" == "--active-job-count" && "${2:-}" == "0" && $# -eq 2 ]]
[[ "$(grep -c '^iter013,' "${REGISTRY}")" -eq 1 ]]
readonly REGISTRY_ROW="$(grep '^iter013,' "${REGISTRY}")"
readonly SUMMARY_SECTION="$(awk '
  /^## iter013 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter013 - / { exit }
  capture { print }
' "${SUMMARY}")"
[[ -n "${SUMMARY_SECTION}" ]]

for source in "${REPORT}" "${HANDOFF}" "${COMPACT}/summary.md"; do
  grep -q 'sr_release_published' "${source}"
  grep -q '(96,48)' "${source}"
  grep -q 'alpha `0.01`' "${source}"
  grep -Eq '44[- ]feature' "${source}"
  grep -q 'fixed_upstream_sr_stage' "${source}"
  grep -q '100442160' "${source}"
  grep -qi 'fixed-test' "${source}"
  grep -qi 'no next iteration is proposed or authorized' "${source}"
done

grep -q 'Iteration ID: `iter013`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"
grep -q 'Last closed iteration: `iter013`' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Status/work type: `completed` / `implementation`' <<<"${SUMMARY_SECTION}"
grep -q 'sr_release_published' <<<"${SUMMARY_SECTION}"
grep -q ',completed,implementation,Characterize and publish' <<<"${REGISTRY_ROW}"
grep -q ',pass,"sr_release_published;' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=b247a206d686c501893024147e8f38488a2d0982' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Release SR surrogate artifact' <<<"${REGISTRY_ROW}"

for source in "${REPORT}" "${HANDOFF}"; do
  grep -q "${PLAN_SHA}" "${source}"
  grep -q 'Alignment: `aligned`' "${source}"
  grep -qi 'approved deviation: `none`' "${source}"
  grep -q 'Campaign-plan amendment recommendation: `none`' "${source}"
done
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}/summary.md"

for job_id in 24666357 24666388 24667839 24667881 24668984; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
done

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter013/iter013_execution_manifest.sha256" | cut -d' ' -f1)" == "${MANIFEST_SHA}" ]]
(cd "${COMPACT}" && sha256sum -c evidence.sha256)

[[ "$(jq -r '.result' "${COMPACT}/final_report.json")" == pass ]]
[[ "$(jq -r '.prediction_count' "${COMPACT}/final_report.json")" == 100442160 ]]
[[ "$(jq -r '.fixed_test_access' "${COMPACT}/final_report.json")" == false ]]
[[ "$(jq -r '.performance_gate_applied' "${COMPACT}/final_report.json")" == false ]]
[[ "$(jq -r '.raw_interface_replay_complete' "${COMPACT}/validation_report.json")" == true ]]
[[ "$(jq -r '.raw_interface_replay_count' "${COMPACT}/validation_report.json")" == 100442160 ]]
[[ "$(jq -r '.fit_member_count' "${COMPACT}/validation_report.json")" == 819 ]]
[[ "$(jq -r '.feature_count' "${COMPACT}/feature_schema.json")" == 44 ]]
[[ "$(jq -r '.fit_member_count' "${COMPACT}/artifact_manifest.json")" == 819 ]]
[[ "$(jq -r '.upstream_models_retrained' "${COMPACT}/upstream_releases.json")" == false ]]
[[ "$(wc -l < "${COMPACT}/metric_summary.csv")" -eq 169 ]]
[[ "$(wc -l < "${COMPACT}/train_validation_gap_summary.csv")" -eq 31 ]]

[[ "$(sha256sum "${STABLE}/release_0001/release_manifest.json" | cut -d' ' -f1)" == "${RELEASE_MANIFEST_SHA}" ]]
[[ "$(jq -r '.current_manifest_sha256' "${STABLE}/catalog.json")" == "${RELEASE_MANIFEST_SHA}" ]]
[[ "$(jq -r '.validation_label' "${STABLE}/catalog.json")" == fixed_upstream_sr_stage ]]
[[ "$(jq -r '.files | length' "${STABLE}/release_0001/release_manifest.json")" == 17 ]]
diff -qr "${RUN_ROOT}/staging/release_0001" "${STABLE}/release_0001" >/dev/null
while IFS=$'\t' read -r relative expected; do
  [[ "$(sha256sum "${STABLE}/release_0001/${relative}" | cut -d' ' -f1)" == "${expected}" ]]
done < <(jq -r '.files[] | [.path,.sha256] | @tsv' "${STABLE}/release_0001/release_manifest.json")

echo ITER013_FOUR_RECORD_VALIDATE_PASS
