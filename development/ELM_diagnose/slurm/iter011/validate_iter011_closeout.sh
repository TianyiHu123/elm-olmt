#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly BASE=${REPO_ROOT}/development/ELM_diagnose
readonly RESULTS=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/results
readonly ATTEMPT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/diagnostic/attempt_1
readonly MANIFEST=${RESULTS}/output_manifest.json

cd "${REPO_ROOT}"
for record in \
  "${BASE}/iterations/iter011.md" \
  "${BASE}/summaries/iter011/ITER011_RESULT.md" \
  "${BASE}/ITERATION_SUMMARY.md" \
  "${BASE}/registry.csv" \
  "${BASE}/handoff/CURRENT.md"
do
  test -s "${record}"
done

grep -Fq 'Status: `completed`' "${BASE}/iterations/iter011.md"
grep -Fq 'Overall acceptance result: `pass`' "${BASE}/iterations/iter011.md"
grep -Fq 'Status: `completed`; overall acceptance: `pass`' "${BASE}/summaries/iter011/ITER011_RESULT.md"
grep -Fq '## Iter011' "${BASE}/ITERATION_SUMMARY.md"
grep -Fq 'Most recent closed iteration: `iter011`' "${BASE}/handoff/CURRENT.md"
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
/^iter011,/ {if (fields($0) != 14) exit 1; matches++}
END {if (matches != 1) exit 1}
' "${BASE}/registry.csv"

test "$(sha256sum "${MANIFEST}" | awk '{print $1}')" = 0e13dfa6168c0df852f0f19aa5a2c7db8549e43e17345a579014ffb5224e577a
test "$(jq -r '.schema' "${MANIFEST}")" = elm_oat_output_manifest_v5
test "$(jq '[.row_counts[]] | add' "${MANIFEST}")" -eq 80200
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
test ! -e "${ATTEMPT}/results_staging"
test "$(sha256sum "${BASE}/slurm/iter011/validate_iter011_artifacts.py" | awk '{print $1}')" = 708d6e82cb336b89929bfed6abc10efe446f6e5a30e4d147e550c17e36100f6c
test "$(sha256sum "${BASE}/slurm/iter011/validate_only_iter011.slurm" | awk '{print $1}')" = c06d8593abb9b2ecea3430cf63d1ff8192ba526a7d70649f97bb875cf87b0842
test "$(sha256sum "${BASE}/slurm/iter011/validator_only_submission_config.env" | awk '{print $1}')" = 5baf0fbd6228c69bb20a91b5d2b5422d8e3ebd2aedb62fd2d1b6dbdb176e528b
cmp "${BASE}/slurm/iter011/validate_only_iter011.slurm" "${ATTEMPT}/submit_validator_only_iter011.slurm"
cmp "${BASE}/slurm/iter011/validator_only_submission_config.env" "${ATTEMPT}/validator_only_submission_config.env"
bash -n "${BASE}"/slurm/iter011/*.slurm "${BASE}/slurm/iter011/oat_args.sh"
git diff --check

echo 'ITER011_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=80200 transient_scores=105 spinup_scores=63 terminal_jobs=4 next_state=workflow_complete'
