#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i017-handoff
#SBATCH --output=handoff_%j.out
#SBATCH --error=handoff_%j.err
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
test "$(sha256sum ./submit_validate_iter017_handoff.slurm | awk '{print $1}')" = "${SUBMITTED_SCRIPT_SHA256}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter017/validate_iter017_handoff.py" --root "${OUTPUT_ROOT}"
