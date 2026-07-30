#!/bin/bash -e
# Aggregate and evaluate the complete manifest-locked Iter011 matrix on Puma.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:15:00
#SBATCH --job-name=spinup_iter011_aggregate
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter011_aggregate_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter011_aggregate_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter011/iter011_variants.tsv"
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_surrogate/summaries/iter011"
readonly SUMMARY_TOOL="${REPO_ROOT}/summarize_spinup_stats.py"
readonly STABILITY_TOOL="${REPO_ROOT}/development/spinup_surrogate/tools/analyze_feature_stability.py"
readonly IMPORTANCE_TOOL="${REPO_ROOT}/development/spinup_surrogate/tools/aggregate_permutation_importance.py"
readonly RESULT_VALIDATOR="${REPO_ROOT}/development/spinup_surrogate/slurm/iter011/validate_iter011_results.py"
readonly PAIRED_ANALYZER="${REPO_ROOT}/development/spinup_surrogate/slurm/iter011/analyze_iter011_paired.py"
readonly DISTRIBUTION_PLOTTER="${REPO_ROOT}/development/spinup_surrogate/tools/plot_spinup_distributions.py"
readonly IMPORTANCE_PLOTTER="${REPO_ROOT}/development/spinup_surrogate/tools/plot_spinup_importance.py"
readonly CONTROL=s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf
readonly CANDIDATE=s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop
readonly JOB_CACHE_DIR="${OUTPUT_ROOT}/UQ_output/.runtime_cache/iter011/aggregate_${SLURM_JOB_ID}"

test -f "${MANIFEST}"
test -f "${SUMMARY_TOOL}"
test -f "${STABILITY_TOOL}"
test -f "${IMPORTANCE_TOOL}"
test -f "${RESULT_VALIDATOR}"
test -f "${PAIRED_ANALYZER}"
test -f "${DISTRIBUTION_PLOTTER}"
test -f "${IMPORTANCE_PLOTTER}"
test -d "${OUTPUT_ROOT}/UQ_output"
test "$(awk 'NR>1 {n++} END {print n+0}' "${MANIFEST}")" -eq 2

mkdir -p "${SUMMARY_ROOT}"
mkdir -p "${JOB_CACHE_DIR}"
export XDG_CACHE_HOME="${JOB_CACHE_DIR}"
export MPLCONFIGDIR="${JOB_CACHE_DIR}/matplotlib"
mkdir -p "${MPLCONFIGDIR}"
cd "${REPO_ROOT}"
module load micromamba

micromamba run -n OLMT_puma python "${RESULT_VALIDATOR}"

while IFS=$'\t' read -r variant rest; do
  [ "${variant}" = variant ] && continue
  stats="${OUTPUT_ROOT}/UQ_output/spinup_surrogate_iter011_${variant}/surrogate_spinup"
  files=("${stats}"/surrogate_spinup_stats_seed*.json)
  [ -e "${files[0]}" ]
  [ "${#files[@]}" -eq 100 ]
  micromamba run -n OLMT_puma python "${SUMMARY_TOOL}" \
    --stats-dir "${stats}" \
    --output-json "${SUMMARY_ROOT}/${variant}_summary.json"
  micromamba run -n OLMT_puma python "${STABILITY_TOOL}" \
    --stats-dir "${stats}" \
    --variant "${variant}" \
    --output-json "${SUMMARY_ROOT}/${variant}_feature_stability.json"
  micromamba run -n OLMT_puma python "${IMPORTANCE_TOOL}" \
    --stats-dir "${stats}" \
    --variant "${variant}" \
    --seed-count 100 \
    --permutation-repeats 8 \
    --output-json "${SUMMARY_ROOT}/${variant}_importance_100seed.json"
done < "${MANIFEST}"

micromamba run -n OLMT_puma python "${PAIRED_ANALYZER}"
micromamba run -n OLMT_puma python "${DISTRIBUTION_PLOTTER}" \
  --iteration iter011 \
  --variant "${CONTROL}" \
  --variant "${CANDIDATE}" \
  --paired-control "${CONTROL}" \
  --output-dir "${SUMMARY_ROOT}"
micromamba run -n OLMT_puma python "${IMPORTANCE_PLOTTER}" \
  --iteration iter011 \
  --variant "${CONTROL}" \
  --variant "${CANDIDATE}" \
  --label DROP32 \
  --label DROP32_corr080 \
  --output-dir "${SUMMARY_ROOT}"

echo "Iter011 exact validation, aggregation, paired analysis, gates, and plots completed"
