#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i018-report
#SBATCH --output=report_%j.out
#SBATCH --error=report_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
source "${SUBMISSION_CONFIG}"
test "$(pwd -P)" = "${RUN_DIR}"
test "$(sha256sum "${SUBMITTED_SCRIPT}" | awk '{print $1}')" = "${SUBMITTED_SCRIPT_SHA256}"
test "$(sha256sum "${CAMPAIGN}" | awk '{print $1}')" = "${CAMPAIGN_SHA256}"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
cd "${REPO_ROOT}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/report_optimization.py" \
  --campaign "${CAMPAIGN}" --path-root "${PATH_ROOT}"
