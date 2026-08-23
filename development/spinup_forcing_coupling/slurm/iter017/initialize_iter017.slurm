#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i017-init
#SBATCH --output=initialize_%j.out
#SBATCH --error=initialize_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${SUBMISSION_CONFIG}"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
source "${SUBMISSION_CONFIG}"
test "$(pwd -P)" = "${RUN_DIR}"
readonly SUBMITTED_SCRIPT="${SUBMITTED_SCRIPT:-${RUN_DIR}/submit_initialize_iter017.slurm}"
test "$(sha256sum "${SUBMITTED_SCRIPT}" | awk '{print $1}')" = "${SUBMITTED_SCRIPT_SHA256}"
test "$(sha256sum "${CAMPAIGN}" | awk '{print $1}')" = "${CAMPAIGN_SHA256}"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/run_optimization_campaign.py" \
  --stage initialization --campaign "${CAMPAIGN}" --output "${OUTPUT}" \
  --repository-commit "${REPOSITORY_COMMIT}" --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}"
