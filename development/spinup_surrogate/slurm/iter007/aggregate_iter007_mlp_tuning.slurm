#!/bin/bash -e
#
# Canonical Puma iter007 post-success aggregation script. Submit only after all 40
# leaves have completed and their stats JSON artifacts have been checked.
#
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --job-name=spinup_iter007_aggregate
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter007_aggregate_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter007_aggregate_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_surrogate/summaries/iter007"
readonly SUMMARY_TOOL="${REPO_ROOT}/summarize_spinup_stats.py"
readonly STABILITY_TOOL="${REPO_ROOT}/development/spinup_surrogate/analyze_feature_stability.py"

test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${SUMMARY_TOOL}"
test -f "${STABILITY_TOOL}"
test -d "${OUTPUT_ROOT}/UQ_output"
cd "${REPO_ROOT}"
mkdir -p "${SUMMARY_ROOT}"

readonly GIT_COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
echo "PROVENANCE commit_hash=${GIT_COMMIT} aggregate_script_sha256=$(sha256sum "$0" | awk '{print $1}')"

readonly VARIANTS=(
  s08_tanh_adam_a10_lr1e3
  s16_tanh_adam_a50_lr1e3
  s24_relu_adam_a50_lr5e4
  s32_tanh_lbfgs_a10_lr1e3
  d08_08_tanh_adam_a10_lr1e3
  d16_08_tanh_adam_a50_lr1e3
  d16_16_relu_adam_a50_lr5e4
  d32_16_tanh_adam_a100_lr1e3
)

module load micromamba
for variant in "${VARIANTS[@]}"; do
  stats_dir="${OUTPUT_ROOT}/UQ_output/spinup_surrogate_iter007_${variant}/surrogate_spinup"
  stats_files=("${stats_dir}"/surrogate_spinup_stats_seed*.json)
  if [ ! -e "${stats_files[0]}" ] || [ "${#stats_files[@]}" -ne 5 ]; then
    echo "Expected exactly five stats files for ${variant}; found ${#stats_files[@]} in ${stats_dir}" >&2
    exit 2
  fi
  micromamba run -n OLMT_puma python "${SUMMARY_TOOL}" \
    --stats-dir "${stats_dir}" \
    --output-json "${SUMMARY_ROOT}/${variant}_summary.json"
  micromamba run -n OLMT_puma python "${STABILITY_TOOL}" \
    --stats-dir "${stats_dir}" \
    --variant "${variant}" \
    --output-json "${SUMMARY_ROOT}/${variant}_feature_stability.json"
done
