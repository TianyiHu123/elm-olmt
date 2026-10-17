#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly BASE=${REPO_ROOT}/development/ELM_diagnose
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter012_abby_ctrlvertc_oat_spinup
readonly RESULTS=${ROOT}/results
readonly ATTEMPT=${ROOT}/diagnostic/attempt_2
readonly MANIFEST=${RESULTS}/output_manifest.json

cd "${REPO_ROOT}"
for record in \
  "${BASE}/iterations/iter012.md" \
  "${BASE}/summaries/iter012/ITER012_RESULT.md" \
  "${BASE}/ITERATION_SUMMARY.md" \
  "${BASE}/registry.csv" \
  "${BASE}/handoff/CURRENT.md"
do
  test -s "${record}"
done

grep -Fq 'Status: `completed`' "${BASE}/iterations/iter012.md"
grep -Fq 'Overall acceptance result: `pass`' "${BASE}/iterations/iter012.md"
grep -Fq 'Status: `completed`; overall acceptance: `pass`' "${BASE}/summaries/iter012/ITER012_RESULT.md"
grep -Fq '## Iter012' "${BASE}/ITERATION_SUMMARY.md"
grep -Fq 'Most recent closed iteration: `iter012`' "${BASE}/handoff/CURRENT.md"
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
/^iter012,/ {if (fields($0) != 14) exit 1; matches++}
END {if (matches != 1) exit 1}
' "${BASE}/registry.csv"

test "$(sha256sum "${MANIFEST}" | awk '{print $1}')" = a24daac2c93c868182ed347e400938252f28a815645cb7cba41d7d61e01ec0ae
test "$(jq -r '.schema' "${MANIFEST}")" = elm_oat_output_manifest_v5
test "$(jq -r '.input_manifest_sha256' "${MANIFEST}")" = 2d041f0d3e952bc9c22bb757ca0533ded4baecd80d8b56daa998e9a0b3ae6977
test "$(jq '[.row_counts[]] | add' "${MANIFEST}")" -eq 103114
test "$(jq -r '.figure_count' "${MANIFEST}")" -eq 11
test "$(jq '.artifacts | length' "${MANIFEST}")" -eq 21

while IFS=$'\t' read -r name bytes sha256; do
  test -f "${RESULTS}/${name}"
  test "$(stat -c %s "${RESULTS}/${name}")" -eq "${bytes}"
  test "$(sha256sum "${RESULTS}/${name}" | awk '{print $1}')" = "${sha256}"
done < <(jq -r '.artifacts | to_entries[] | [.key, .value.bytes, .value.sha256] | @tsv' "${MANIFEST}")

while IFS=$'\t' read -r name expected; do
  test "$(( $(wc -l < "${RESULTS}/${name}") - 1 ))" -eq "${expected}"
done < <(jq -r '.row_counts | to_entries[] | [.key, .value] | @tsv' "${MANIFEST}")

test "$(find "${RESULTS}" -maxdepth 1 -type f -name '*.png' | wc -l)" -eq 11
test ! -e "${ATTEMPT}/.staging"
test "$(sha256sum "${ATTEMPT}/diagnostic_time.txt" | awk '{print $1}')" = 42989f6035fccc5017611e3965727f00d4ea6bc827131814de1d0de3374036da
grep -Fq 'Maximum resident set size (kbytes): 6408012' "${ATTEMPT}/diagnostic_time.txt"
grep -Fq 'Swaps: 0' "${ATTEMPT}/diagnostic_time.txt"
grep -Fq 'Exit status: 0' "${ATTEMPT}/diagnostic_time.txt"
test "$(sha256sum "${BASE}/slurm/iter012/validate_iter012_artifacts.py" | awk '{print $1}')" = cf3d4b60e5d0220cf8be290ec74e258120b2a21d5a21d34cbc2d5b8aa97d6420
test "$(sha256sum "${BASE}/slurm/iter012/diagnostic_iter012.slurm" | awk '{print $1}')" = 6428b18dea1d059bc170e23708f5a84ef7b2693f2664bfcd712619584ae07b51
cmp "${BASE}/slurm/iter012/diagnostic_iter012.slurm" "${ATTEMPT}/submit_diagnostic_iter012.slurm"
cmp "${BASE}/slurm/iter012/oat_args.sh" "${ATTEMPT}/oat_args.sh"
bash -n "${BASE}"/slurm/iter012/*.slurm "${BASE}/slurm/iter012/"*.sh
git diff --check

echo 'ITER012_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=103114 transient_scores=135 spinup_scores=81 terminal_jobs=5 next_state=workflow_complete'
