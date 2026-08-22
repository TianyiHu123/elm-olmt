#!/usr/bin/env bash
# Copy this script into ${PATH_ROOT}/optimization/ before submission.
# Keep the explicit array range synchronized with the SEEDS list below.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --array=0-2%2
#SBATCH --job-name=sfc-opt
#SBATCH --output=optimization_%A_%a.out
#SBATCH --error=optimization_%A_%a.err
set -euo pipefail

# The Slurm script, not campaign.yaml, owns the multi-seed ensemble.
readonly SEEDS=(9009 9010 9011)
readonly ARRAY_INDEX="${SLURM_ARRAY_TASK_ID:?Slurm array task ID is required}"
test "${ARRAY_INDEX}" -ge 0
test "${ARRAY_INDEX}" -lt "${#SEEDS[@]}"
readonly SEED="${SEEDS[${ARRAY_INDEX}]}"

test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
source "${SUBMISSION_CONFIG}"
readonly RUN_DIR="${PATH_ROOT}/optimization"
readonly LEAF="${RUN_DIR}/seed_${SEED}"

test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/run_optimization_campaign.py"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${CAMPAIGN}"
test -f "${POOL}"
test -d "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"
test ! -e "${LEAF}/production_result.json"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
mkdir -p "${LEAF}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/run_optimization_campaign.py" \
  --stage optimization \
  --campaign "${CAMPAIGN}" \
  --output "${LEAF}" \
  --pool "${POOL}" \
  --seed "${SEED}" \
  --n-processes "${N_PROCESSES}" \
  --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}"
