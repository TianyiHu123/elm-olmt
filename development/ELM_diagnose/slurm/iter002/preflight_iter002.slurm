#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:15:00
#SBATCH --job-name=elm-diag-i002-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
readonly PREFLIGHT_TOOL="${REPO_ROOT}/development/ELM_diagnose/slurm/iter001/preflight_iter001.py"
readonly ENV_FILE="${REPO_ROOT}/conda_envs/OLMT_puma.yml"
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"
test -f "${PUMA_PROFILE}"; test -f "${WORKFLOW_FILE}"; test -f "${PREFLIGHT_TOOL}"; test -f "${ENV_FILE}"; test -f "${CONFIG_FILE}"
source "${CONFIG_FILE}"
readonly RUN_DIR="${RUN_DIR:?missing RUN_DIR}"
readonly OUTPUT="${RUN_DIR}/${OUTPUT:?missing OUTPUT}"
cd "${REPO_ROOT}"; test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${PREFLIGHT_TOOL}" | awk '{print $1}')" = "${PREFLIGHT_TOOL_SHA256:?missing PREFLIGHT_TOOL_SHA256}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python \
  "${PREFLIGHT_TOOL}" \
  --output "${OUTPUT}"
