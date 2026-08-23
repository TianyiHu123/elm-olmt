#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i017-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${SUBMISSION_CONFIG}"
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
test "$(pwd -P)" = "${RUN_DIR}"
test "$(sha256sum ./submit_preflight_iter017.slurm | awk '{print $1}')" = "${SUBMITTED_SCRIPT_SHA256}"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
sha256sum -c "${SOURCE_MANIFEST}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter017/preflight_iter017.py" --campaign-dir "${CAMPAIGN_DIR}"
