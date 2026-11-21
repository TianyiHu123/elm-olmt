#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter010_abby_jerc_sr_refinement"
readonly UNIT1="${RUN_ROOT}/runs/unit1/attempt_2/unit1_report.json"
readonly FINAL="${RUN_ROOT}/runs/final/attempt_1"
readonly PLAN_SHA256="014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360"
readonly UNIT1_SHA256="868f9890bf55f03425086dc5a80e91b0f06bbd9433a8c55d32385b66a3808017"
readonly METRIC_SHA256="6e43c47fa6e119f528417c4f38d9dc3250421c7c5ce039f83dd1b1d1e1f9ffbf"
readonly RANKING_SHA256="948f32df02a74734d73c00f78e3951b5fe866ccdc38e2b50aec6f0ff40739e5c"
readonly SELECTION_SHA256="ebd1e5413b5aa44b7ac139510aab307f9ac67430054d5cd0b2315d619429edf5"
readonly VALIDATION_SHA256="4c883485dd9d17ba083ee4579ccb6259b028e47b2515586bb2f151a39f057617"
readonly MANIFEST_SHA256="3870eecba10cd5309c886e540170787962187b819efe043f3c993e45796f2f66"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter010.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter010/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter010/evidence.sha256"

readonly SUMMARY_SECTION="$(awk '
  /^## iter010 - / { capture=1 }
  /^## iter[0-9][0-9][0-9] - / && capture && $0 !~ /^## iter010 - / { exit }
  capture { print }
' "${SUMMARY}")"
readonly REGISTRY_ROW="$(grep '^iter010,' "${REGISTRY}")"

[[ -n "${SUMMARY_SECTION}" ]]
[[ "$(grep -c '^iter010,' "${REGISTRY}")" -eq 1 ]]

# Exact iteration identity, lifecycle, objective, and acceptance in their record-specific fields.
grep -q 'Iteration ID: `iter010`' "${REPORT}"
grep -q 'Work type: `experiment`' "${REPORT}"
grep -q 'Status: `completed`' "${REPORT}"
grep -q 'Phase: `closed`' "${REPORT}"
grep -q 'Objective: refine the Iter009 SR configuration' "${REPORT}"
grep -q 'Overall acceptance result: `pass`' "${REPORT}"

grep -q 'Last closed iteration: `iter010`' "${HANDOFF}"
grep -q 'Work type: `experiment`' "${HANDOFF}"
grep -q 'Status: `completed`' "${HANDOFF}"
grep -q 'Phase: `closed`' "${HANDOFF}"
grep -q 'Completed objective: refine the Iter009 ABBY/JERC SR surrogate configuration' "${HANDOFF}"
grep -q 'Acceptance result: `pass`' "${HANDOFF}"

grep -q 'Status/work type: `completed` / `experiment`' <<<"${SUMMARY_SECTION}"
grep -q 'Objective/result: refine the Iter009 SR configuration' <<<"${SUMMARY_SECTION}"
grep -q 'fresh development-only splits; `pass`' <<<"${SUMMARY_SECTION}"
grep -q 'Iteration/work type: `iter010` / `experiment`' "${COMPACT}"
grep -q 'Objective/result: refine the Iter009 SR configuration' "${COMPACT}"
grep -q 'fresh development-only splits; `pass`' "${COMPACT}"
grep -q ',completed,experiment,Refine the Iter009 ABBY/JERC SR surrogate configuration,' <<<"${REGISTRY_ROW}"
grep -q ',pass,sr_refined_configuration_selected;' <<<"${REGISTRY_ROW}"

# Decision, selected configuration, finalists/ranking, and matched-control gate agreement.
for source in "${REPORT}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'sr_refined_configuration_selected' "${source}"
  grep -q 'candidate 19' "${source}"
  grep -q '(96,48)' "${source}"
  grep -q 'tanh' "${source}"
  grep -q 'alpha' "${source}"
  grep -q '`1.0`' "${source}"
  grep -q 'Adam' "${source}"
  grep -q '6/6' "${source}"
done
grep -q 'sr_refined_configuration_selected' <<<"${SUMMARY_SECTION}"
grep -q 'candidate 19' <<<"${SUMMARY_SECTION}"
grep -q '(96,48)' <<<"${SUMMARY_SECTION}"
grep -q 'tanh' <<<"${SUMMARY_SECTION}"
grep -q 'alpha' <<<"${SUMMARY_SECTION}"
grep -q '`1.0`' <<<"${SUMMARY_SECTION}"
grep -q 'Adam' <<<"${SUMMARY_SECTION}"
grep -q '6/6' <<<"${SUMMARY_SECTION}"
grep -q 'candidate 19 (96x48 tanh alpha 1.0 frozen Adam controls)' <<<"${REGISTRY_ROW}"
grep -q '6/6 components and neither resolution was both worse' <<<"${REGISTRY_ROW}"
grep -q 'neither resolution both worse' "${REPORT}"
grep -q 'neither resolution had both worse' "${HANDOFF}"
grep -q 'no both-worse resolution' <<<"${SUMMARY_SECTION}"
grep -q 'neither resolution both worse' "${COMPACT}"
for source in "${REPORT}" "${HANDOFF}" "${COMPACT}"; do
  grep -Eq '\[0, *23, *19, *26, *11, *15\]' "${source}"
  grep -q '19,23,15,26,11,0' "${source}"
done
grep -Eq '\[0, *23, *19, *26, *11, *15\]' <<<"${SUMMARY_SECTION}"
grep -q '19,23,15,26,11,0' <<<"${SUMMARY_SECTION}"

# Plan identity/alignment are required to agree between report and live handoff.
for source in "${REPORT}" "${HANDOFF}"; do
  grep -q "${PLAN_SHA256}" "${source}"
  grep -q 'Alignment: `aligned`' "${source}"
  grep -qi 'approved deviation: `none`' "${source}"
done

# Scope boundaries and terminal direction agree across every durable closeout record.
for source in "${REPORT}" "${HANDOFF}" "${COMPACT}"; do
  grep -qi 'fixed-test' "${source}"
  grep -q 'all-819' "${source}"
  grep -qi 'release' "${source}"
  grep -q 'No next iteration is authorized' "${source}"
done
grep -qi 'fixed-test' <<<"${SUMMARY_SECTION}"
grep -q 'all-819' <<<"${SUMMARY_SECTION}"
grep -qi 'release' <<<"${SUMMARY_SECTION}"
grep -q 'No next iteration is authorized' <<<"${SUMMARY_SECTION}"
grep -q 'No fixed-test all-819 SR fit uncertainty or release' <<<"${REGISTRY_ROW}"
grep -q 'no next iteration authorized' <<<"${REGISTRY_ROW}"
grep -q 'no job is active or unaccounted' "${HANDOFF}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${REPORT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${HANDOFF}"
grep -q 'Campaign-plan amendment recommendation: `none`' <<<"${SUMMARY_SECTION}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${COMPACT}"

# Fixed registry schema and closeout branch identity.
grep -q 'summaries/iter010,committed' <<<"${REGISTRY_ROW}"
grep -q 'expected_parent=414faa231c083435acbe97f6e79131ba4b00e68b' <<<"${REGISTRY_ROW}"
grep -q 'expected_subject=Refine SR surrogate configuration' <<<"${REGISTRY_ROW}"
grep -q 'validator=validate_closeout_iter010.sh' <<<"${REGISTRY_ROW}"

[[ "$(sha256sum "${CAMPAIGN}/PLAN.md" | cut -d' ' -f1)" == "${PLAN_SHA256}" ]]
[[ "$(sha256sum "${UNIT1}" | cut -d' ' -f1)" == "${UNIT1_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_metric_distribution.csv" | cut -d' ' -f1)" == "${METRIC_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_ranking.csv" | cut -d' ' -f1)" == "${RANKING_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_selection_report.json" | cut -d' ' -f1)" == "${SELECTION_SHA256}" ]]
[[ "$(sha256sum "${FINAL}/final_validation.json" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
[[ "$(sha256sum "${CAMPAIGN}/slurm/iter010/iter010_execution_manifest.sha256" | cut -d' ' -f1)" == "${MANIFEST_SHA256}" ]]
for hash in "${UNIT1_SHA256}" "${METRIC_SHA256}" "${RANKING_SHA256}" "${SELECTION_SHA256}" "${VALIDATION_SHA256}" "${MANIFEST_SHA256}"; do
  grep -q "${hash}" "${EVIDENCE}"
done

[[ "$(jq -r '.result' "${UNIT1}")" == "pass" ]]
[[ "$(jq -r '.features' "${UNIT1}")" == "44" ]]
[[ "$(jq -r '.fresh_splits' "${UNIT1}")" == "20" ]]
[[ "$(jq -r '.candidate_count' "${UNIT1}")" == "33" ]]
[[ "$(jq -r '.fixed_test_access' "${UNIT1}")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_selection_report.json")" == "pass" ]]
[[ "$(jq -r '.decision' "${FINAL}/final_selection_report.json")" == "sr_refined_configuration_selected" ]]
[[ "$(jq -r '.best_ranked_candidate_id' "${FINAL}/final_selection_report.json")" == "19" ]]
[[ "$(jq -r '.selected_candidate_id' "${FINAL}/final_selection_report.json")" == "19" ]]
[[ "$(jq -r '.challenger_improved_component_count' "${FINAL}/final_selection_report.json")" == "6" ]]
[[ "$(jq -r '.replacement_gate_pass' "${FINAL}/final_selection_report.json")" == "true" ]]
[[ "$(jq -r '.performance_gate_applied' "${FINAL}/final_selection_report.json")" == "true" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_selection_report.json")" == "false" ]]
[[ "$(jq -r '.result' "${FINAL}/final_validation.json")" == "pass" ]]
[[ "$(jq -r '.selected_candidate_id' "${FINAL}/final_validation.json")" == "19" ]]
[[ "$(jq -r '.recomputed_metric_rows' "${FINAL}/final_validation.json")" == "240" ]]
[[ "$(jq -r '.fixed_test_access' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(jq -r '.release_created' "${FINAL}/final_validation.json")" == "false" ]]
[[ "$(wc -l < "${FINAL}/final_metric_distribution.csv")" -eq 241 ]]
[[ "$(wc -l < "${FINAL}/final_ranking.csv")" -eq 7 ]]
[[ "$(awk -F, 'NR==2 {print $2}' "${FINAL}/final_ranking.csv")" == "19" ]]
[[ "$(wc -l < "${CAMPAIGN}/slurm/iter010/iter010_execution_manifest.sha256")" -eq 20 ]]

# Job identities, terminal success, and the classified Unit1 failure agree across records.
for job_id in 24578833 24578853 24579541 24590678 24595272; do
  grep -q "${job_id}" "${REPORT}"
  grep -q "${job_id}" "${HANDOFF}"
  grep -q "${job_id}" "${COMPACT}"
  grep -q "${job_id}" <<<"${SUMMARY_SECTION}"
  grep -q "${job_id}" <<<"${REGISTRY_ROW}"
done
grep -q '24578833.*FAILED 1:0' "${REPORT}"
grep -q '24578833.*failed' "${HANDOFF}"
grep -q '24578833.*failed' "${COMPACT}"
grep -q '24578833.*failed' <<<"${SUMMARY_SECTION}"
grep -q '24578833 failed pre-substantive' <<<"${REGISTRY_ROW}"
grep -q '24578853.*COMPLETED 0:0' "${REPORT}"
grep -q '24578853.*completed `0:0`' "${HANDOFF}"
grep -q 'corrected Unit1 retry completed `0:0`' "${COMPACT}"
grep -q 'corrected Unit1 `24578853`' <<<"${SUMMARY_SECTION}"
grep -q 'final `24595272` completed `0:0`' <<<"${SUMMARY_SECTION}"
grep -q '24578853 plus arrays 24579541 and 24590678 and final 24595272 completed 0:0' <<<"${REGISTRY_ROW}"

echo "ITER010_FOUR_RECORD_VALIDATE_PASS"
