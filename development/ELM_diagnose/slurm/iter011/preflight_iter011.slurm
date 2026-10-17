#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=02:00:00
#SBATCH --job-name=elm-diag-i011-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOOL=${REPO_ROOT}/development/ELM_diagnose/tools/oat_sensitivity.py
readonly FIXTURE=${REPO_ROOT}/development/ELM_diagnose/slurm/iter011/test_oat_iter011.py
readonly VALIDATOR=${REPO_ROOT}/development/ELM_diagnose/slurm/iter011/validate_iter011_artifacts.py
readonly ENV_FILE=${REPO_ROOT}/conda_envs/OLMT_puma.yml
readonly CONFIG_FILE=${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}

source "${CONFIG_FILE}"
source "${ARGUMENTS_FILE:?missing ARGUMENTS_FILE}"
test "$(pwd -P)" = "${RUN_DIR:?missing RUN_DIR}"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${FIXTURE}" | awk '{print $1}')" = "${FIXTURE_SHA256:?missing FIXTURE_SHA256}"
test "$(sha256sum "${VALIDATOR}" | awk '{print $1}')" = "${VALIDATOR_SHA256:?missing VALIDATOR_SHA256}"
test "$(sha256sum "${ARGUMENTS_FILE}" | awk '{print $1}')" = "${ARGUMENTS_SHA256:?missing ARGUMENTS_SHA256}"
test "$(sha256sum "${ENV_FILE}" | awk '{print $1}')" = "${ENV_FILE_SHA256:?missing ENV_FILE_SHA256}"
test "$(sha256sum "${CONTROL_PARAMFILE}" | awk '{print $1}')" = "${CONTROL_PARAMFILE_SHA256:?missing CONTROL_PARAMFILE_SHA256}"
test "$(sha256sum "${OBSERVATION_FILE}" | awk '{print $1}')" = "${OBSERVATION_FILE_SHA256:?missing OBSERVATION_FILE_SHA256}"
test "$(find "${CONFIG_DIR}" -maxdepth 1 -type f -name '*.cfg' | wc -l)" -eq 21
test "$(find "${PARAMETER_DIR}" -maxdepth 1 -type f -name '*paramfile*' | wc -l)" -eq 21
sha256sum -c "${PROVENANCE_CHECKSUMS:?missing PROVENANCE_CHECKSUMS}"
test ! -e "${OUTPUT_DIR:?missing OUTPUT_DIR}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python -m py_compile "${TOOL}" "${FIXTURE}" "${VALIDATOR}"
micromamba run -n OLMT_puma python "${FIXTURE}"
micromamba run -n OLMT_puma python "${TOOL}" "${OAT_ARGS[@]}" \
  --output "${OUTPUT_DIR}" \
  --validate-only
