#!/usr/bin/env bash
# Copy this script into ${PATH_ROOT}/postprocess/ before submission.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-report
#SBATCH --output=report_%j.out
#SBATCH --error=report_%j.err
set -euo pipefail

test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
source "${SUBMISSION_CONFIG}"
readonly RUN_DIR="${PATH_ROOT}/postprocess"

test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/report_optimization.py"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${CAMPAIGN}"
test -d "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"
test ! -e "${PATH_ROOT}/reports/report_manifest.json"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/report_optimization.py" \
  --campaign "${CAMPAIGN}" \
  --path-root "${PATH_ROOT}"
