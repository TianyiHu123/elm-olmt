#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly BASE=${REPO_ROOT}/development/ELM_diagnose
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs
readonly RESULTS=${ROOT}/results
readonly PREFLIGHT=${ROOT}/preflight/attempt_4
readonly ATTEMPT=${ROOT}/diagnostic/attempt_1
readonly INPUT_MANIFEST=${PREFLIGHT}/artifacts/input_manifest.json
readonly MANIFEST=${RESULTS}/output_manifest.json

cd "${REPO_ROOT}"
for record in \
  "${BASE}/iterations/iter013.md" \
  "${BASE}/summaries/iter013/ITER013_RESULT.md" \
  "${BASE}/ITERATION_SUMMARY.md" \
  "${BASE}/registry.csv" \
  "${BASE}/handoff/CURRENT.md"
do
  test -s "${record}"
done

grep -Fq 'Status: `completed`' "${BASE}/iterations/iter013.md"
grep -Fq 'Overall acceptance result: `pass`' "${BASE}/iterations/iter013.md"
grep -Fq 'Status: `completed`; overall acceptance: `pass`' "${BASE}/summaries/iter013/ITER013_RESULT.md"
grep -Fq '## Iter013' "${BASE}/ITERATION_SUMMARY.md"
grep -Fq 'Most recent closed iteration: `iter013`' "${BASE}/handoff/CURRENT.md"
grep -Fq 'Status: `workflow_complete`' "${BASE}/handoff/CURRENT.md"
grep -Fq 'Active monitoring: none' "${BASE}/handoff/CURRENT.md"

awk '
function fields(line, i, char, quoted, count) {
  quoted = 0
  count = 1
  for (i = 1; i <= length(line); i++) {
    char = substr(line, i, 1)
    if (char == "\"") {
      if (quoted && substr(line, i + 1, 1) == "\"") i++
      else quoted = !quoted
    } else if (char == "," && !quoted) count++
  }
  if (quoted) return -1
  return count
}
NR == 1 && fields($0) != 14 {exit 1}
/^iter013,/ {if (fields($0) != 14) exit 1; matches++}
END {if (matches != 1) exit 1}
' "${BASE}/registry.csv"

test "$(sha256sum "${INPUT_MANIFEST}" | awk '{print $1}')" = 808ec4f0870f13f6c947a65e9d466c3bb80cd036708bbb32648075bbd3863225
test "$(jq -r '.schema' "${INPUT_MANIFEST}")" = elm_oat_input_manifest_v6
test "$(jq -r '.status' "${INPUT_MANIFEST}")" = pass
jq -e '(.parameters | length == 27) and (.member_count_per_parameter == 100) and (.expected_hours == 61320) and (.require_complete_spinup_ratios == true) and ([.restart_cases[] | (.members == 100 and .support.DECOMP_CN_RATIO.valid_members == 100 and .support.DECOMP_CN_RATIO.rejected_members == 0 and .support.DECOMP_CP_RATIO.valid_members == 100 and .support.DECOMP_CP_RATIO.rejected_members == 0)] | all)' "${INPUT_MANIFEST}" >/dev/null

test "$(sha256sum "${MANIFEST}" | awk '{print $1}')" = 99d84254e00f8bb0f49312ff99413a4b87b4249d0eadedb3b3dad53a7878539d
test "$(jq -r '.schema' "${MANIFEST}")" = elm_oat_output_manifest_v6
test "$(jq -r '.status' "${MANIFEST}")" = pass
test "$(jq -r '.input_manifest_sha256' "${MANIFEST}")" = 808ec4f0870f13f6c947a65e9d466c3bb80cd036708bbb32648075bbd3863225
test "$(jq '[.row_counts[]] | add' "${MANIFEST}")" -eq 109113
test "$(jq -r '.figure_count' "${MANIFEST}")" -eq 13
test "$(jq '.artifacts | length' "${MANIFEST}")" -eq 24

while IFS=$'\t' read -r name bytes sha256; do
  test -f "${RESULTS}/${name}"
  test "$(stat -c %s "${RESULTS}/${name}")" -eq "${bytes}"
  test "$(sha256sum "${RESULTS}/${name}" | awk '{print $1}')" = "${sha256}"
done < <(jq -r '.artifacts | to_entries[] | [.key, .value.bytes, .value.sha256] | @tsv' "${MANIFEST}")

while IFS=$'\t' read -r name expected; do
  test "$(( $(wc -l < "${RESULTS}/${name}") - 1 ))" -eq "${expected}"
done < <(jq -r '.row_counts | to_entries[] | [.key, .value] | @tsv' "${MANIFEST}")

test "$(find "${RESULTS}" -maxdepth 1 -type f -name '*.png' | wc -l)" -eq 13
test ! -e "${ATTEMPT}/.staging"
test "$(sha256sum "${ATTEMPT}/diagnostic_time.txt" | awk '{print $1}')" = e8adb695d1b19172740eea70bf1cb9b30b0b426806501c1a64b0355bf77c47a2
grep -Fq 'Maximum resident set size (kbytes): 6413020' "${ATTEMPT}/diagnostic_time.txt"
grep -Fq 'Swaps: 0' "${ATTEMPT}/diagnostic_time.txt"
grep -Fq 'Exit status: 0' "${ATTEMPT}/diagnostic_time.txt"
test "$(sha256sum "${BASE}/tools/oat_sensitivity.py" | awk '{print $1}')" = 3b48732ffd847eba8d4d7aa3e190730ea55c1aee54315bfacdb709b298a06183
test "$(sha256sum "${BASE}/slurm/iter013/validate_iter013_artifacts.py" | awk '{print $1}')" = dc47b85368cbc6648a64ca368e9a5ca0e6b506d67cc145f4d8ddc14a07e0465f
test "$(sha256sum "${BASE}/slurm/iter013/diagnostic_iter013.slurm" | awk '{print $1}')" = e0db7869a4da3705eb5806fcf1d001ea77cd833cfad53fc6bca3979a0e464eac
cmp "${BASE}/slurm/iter013/diagnostic_iter013.slurm" "${ATTEMPT}/submit_diagnostic_iter013.slurm"
cmp "${BASE}/slurm/iter013/oat_args.sh" "${ATTEMPT}/oat_args.sh"
bash -n "${BASE}"/slurm/iter013/*.slurm "${BASE}/slurm/iter013/"*.sh
git diff --check

echo 'ITER013_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=13 csv_rows=109113 transient_scores=135 spinup_scores=135 terminal_jobs=3 next_state=workflow_complete'
