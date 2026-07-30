#!/bin/bash -e
# Aggregate the complete manifest-locked iter010 matrix on Puma.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter010_aggregate
set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project MANIFEST="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter010/iter010_variants.tsv" SUMMARY_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/summaries/iter010" SUMMARY_TOOL="/xdisk/chopinsong/tianyihu/elm-olmt/summarize_spinup_stats.py" STABILITY_TOOL="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/tools/analyze_feature_stability.py" IMPORTANCE_TOOL="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter010/aggregate_iter010_importance.py" RESULT_VALIDATOR="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter010/validate_iter010_results.py"
test -f "${MANIFEST}"; test -f "${SUMMARY_TOOL}"; test -f "${STABILITY_TOOL}"; test -f "${IMPORTANCE_TOOL}"; test -f "${RESULT_VALIDATOR}"; test -d "${OUTPUT_ROOT}/UQ_output"; test "$(awk 'NR>1{n++} END{print n+0}' "${MANIFEST}")" = 15; mkdir -p "${SUMMARY_ROOT}"; cd "${REPO_ROOT}"; module load micromamba; micromamba run -n OLMT_puma python "${RESULT_VALIDATOR}"
while IFS=$'\t' read -r variant rest; do [ "${variant}" = variant ] && continue; stats="${OUTPUT_ROOT}/UQ_output/spinup_surrogate_iter010_${variant}/surrogate_spinup"; files=("${stats}"/surrogate_spinup_stats_seed*.json); [ -e "${files[0]}" ] && [ "${#files[@]}" -eq 100 ] || { echo "Expected 100 stats: ${variant}" >&2; exit 2; }; micromamba run -n OLMT_puma python "${SUMMARY_TOOL}" --stats-dir "${stats}" --output-json "${SUMMARY_ROOT}/${variant}_summary.json"; micromamba run -n OLMT_puma python "${STABILITY_TOOL}" --stats-dir "${stats}" --variant "${variant}" --output-json "${SUMMARY_ROOT}/${variant}_feature_stability.json"; micromamba run -n OLMT_puma python "${IMPORTANCE_TOOL}" --stats-dir "${stats}" --variant "${variant}" --output-json "${SUMMARY_ROOT}/${variant}_importance_100seed.json"; done < "${MANIFEST}"
