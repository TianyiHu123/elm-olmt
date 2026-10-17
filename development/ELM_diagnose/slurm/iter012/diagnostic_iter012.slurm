#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
#SBATCH --job-name=elm-diag-i012-diagnostic
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOOL=${REPO_ROOT}/development/ELM_diagnose/tools/oat_sensitivity.py
readonly VALIDATOR=${REPO_ROOT}/development/ELM_diagnose/slurm/iter012/validate_iter012_artifacts.py
readonly CONFIG_FILE=${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}

source "${CONFIG_FILE}"
source "${ARGUMENTS_FILE:?missing ARGUMENTS_FILE}"
test "$(pwd -P)" = "${RUN_DIR:?missing RUN_DIR}"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${VALIDATOR}" | awk '{print $1}')" = "${VALIDATOR_SHA256:?missing VALIDATOR_SHA256}"
test "$(sha256sum "${ARGUMENTS_FILE}" | awk '{print $1}')" = "${ARGUMENTS_SHA256:?missing ARGUMENTS_SHA256}"
test "$(sha256sum "${INPUT_MANIFEST}" | awk '{print $1}')" = "${INPUT_MANIFEST_SHA256:?missing INPUT_MANIFEST_SHA256}"
test ! -e "${OUTPUT_DIR:?missing OUTPUT_DIR}"
test ! -e "${STAGING_DIR:?missing STAGING_DIR}"
test ! -e "${RUN_DIR}/diagnostic_time.txt"

module load micromamba/2.0.2-2
/usr/bin/time -v -o "${RUN_DIR}/diagnostic_time.txt" \
  micromamba run -n OLMT_puma python "${TOOL}" "${OAT_ARGS[@]}" \
  --output "${STAGING_DIR}" \
  --manifest "${INPUT_MANIFEST}"
micromamba run -n OLMT_puma python "${VALIDATOR}" \
  --input-manifest "${INPUT_MANIFEST}" \
  --results "${STAGING_DIR}"
mv "${STAGING_DIR}" "${OUTPUT_DIR}"
echo "ITER012_ATOMIC_PUBLICATION_PASS output=${OUTPUT_DIR}"
