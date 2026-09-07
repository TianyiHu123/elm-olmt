#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=01:00:00
#SBATCH --job-name=elm-diag-i003
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/flux_diagnostics.py"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${CONFIG_FILE}" && test -f "${TOOL}"
source "${CONFIG_FILE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${YAML_CONFIG:?missing YAML_CONFIG}" | awk '{print $1}')" = "${YAML_SHA256:?missing YAML_SHA256}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${TOOL}" --config "${YAML_CONFIG}" --output "${OUTPUT_ROOT:?missing OUTPUT_ROOT}"
