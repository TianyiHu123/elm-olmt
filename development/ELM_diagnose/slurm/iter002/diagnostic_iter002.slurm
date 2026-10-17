#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=01:00:00
#SBATCH --job-name=elm-diag-i002
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/iter002_sr_diagnostics.py"
test -f "${REPO_ROOT}/development/hpc/puma.md"; test -f "${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"; test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"; test -f "${TOOL}"; test -f "${CONFIG_FILE}"
source "${CONFIG_FILE}"; readonly RUN_DIR="${RUN_DIR:?missing RUN_DIR}"
test -f "${RECEIPT:?missing RECEIPT}"
cd "${REPO_ROOT}"; test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${TOOL}" --receipt "${RECEIPT}" --output "${OUTPUT_ROOT:?missing OUTPUT_ROOT}"
