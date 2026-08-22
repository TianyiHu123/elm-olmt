#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --array=0-8%2
#SBATCH --job-name=sfc-i018-opt
#SBATCH --output=optimization_%A_%a.out
#SBATCH --error=optimization_%A_%a.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
test -n "${SUBMISSION_CONFIG:-}"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${SUBMISSION_CONFIG}"
source "${SUBMISSION_CONFIG}"
test "$(pwd -P)" = "${RUN_DIR}"
test "$(sha256sum "${SUBMITTED_SCRIPT}" | awk '{print $1}')" = "${SUBMITTED_SCRIPT_SHA256}"
test "$(sha256sum "${CAMPAIGN}" | awk '{print $1}')" = "${CAMPAIGN_SHA256}"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
readonly SEED="${SEEDS[${SLURM_ARRAY_TASK_ID}]}"
readonly LEAF="${PATH_ROOT}/optimization/seed_${SEED}"
test ! -e "${LEAF}/production_result.json"
mkdir -p "${LEAF}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/run_optimization_campaign.py" \
  --stage optimization --campaign "${CAMPAIGN}" --output "${LEAF}" --pool "${POOL}" --seed "${SEED}" \
  --n-processes 16 --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" --dependency-manifest "${DEPENDENCY_MANIFEST}"
