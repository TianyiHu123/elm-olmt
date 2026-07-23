#!/bin/bash -e
# Aggregate the complete, manifest-locked iter008 matrix on Puma.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter008_aggregate

set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter008/iter008_variants.tsv"
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_surrogate/summaries/iter008"
readonly SUMMARY_TOOL="${REPO_ROOT}/summarize_spinup_stats.py"
readonly STABILITY_TOOL="${REPO_ROOT}/development/spinup_surrogate/analyze_feature_stability.py"
test -f "${MANIFEST}"
test -f "${SUMMARY_TOOL}"
test -f "${STABILITY_TOOL}"
test -d "${OUTPUT_ROOT}/UQ_output"
test "$(awk 'NR > 1 { count++ } END { print count + 0 }' "${MANIFEST}")" = 18
mkdir -p "${SUMMARY_ROOT}"
cd "${REPO_ROOT}"
module load micromamba
while IFS=$'\t' read -r variant rest; do
  if [ "${variant}" = "variant" ]; then continue; fi
  stats_dir="${OUTPUT_ROOT}/UQ_output/spinup_surrogate_iter008_${variant}/surrogate_spinup"
  stats_files=("${stats_dir}"/surrogate_spinup_stats_seed*.json)
  if [ ! -e "${stats_files[0]}" ] || [ "${#stats_files[@]}" -ne 5 ]; then
    echo "Expected exactly five stats files for ${variant}; found ${#stats_files[@]}" >&2
    exit 2
  fi
  micromamba run -n OLMT_puma python "${SUMMARY_TOOL}" --stats-dir "${stats_dir}" \
    --output-json "${SUMMARY_ROOT}/${variant}_summary.json"
  micromamba run -n OLMT_puma python "${STABILITY_TOOL}" --stats-dir "${stats_dir}" \
    --variant "${variant}" --output-json "${SUMMARY_ROOT}/${variant}_feature_stability.json"
done < "${MANIFEST}"
