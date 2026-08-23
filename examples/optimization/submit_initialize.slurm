#!/usr/bin/env bash
# Copy this script into ${PATH_ROOT}/initialization/ before submission.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-init
#SBATCH --output=initialize_%j.out
#SBATCH --error=initialize_%j.err
set -euo pipefail

test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
source "${SUBMISSION_CONFIG}"
readonly RUN_DIR="${PATH_ROOT}/initialization"

test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/run_optimization_campaign.py"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${CAMPAIGN}"
test -d "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/run_optimization_campaign.py" \
  --stage initialization \
  --campaign "${CAMPAIGN}" \
  --output "${RUN_DIR}" \
  --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}"
