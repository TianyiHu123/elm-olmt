#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=04:00:00
#SBATCH --job-name=elm-diag-i011-validate
#SBATCH --output=slurm_validator_only_%j.out
#SBATCH --error=slurm_validator_only_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly VALIDATOR=${REPO_ROOT}/development/ELM_diagnose/slurm/iter011/validate_iter011_artifacts.py
readonly CONFIG_FILE=${VALIDATOR_ONLY_CONFIG:?VALIDATOR_ONLY_CONFIG is required}

source "${CONFIG_FILE}"
test "$(pwd -P)" = "${RUN_DIR:?missing RUN_DIR}"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${VALIDATOR}" | awk '{print $1}')" = "${VALIDATOR_SHA256:?missing VALIDATOR_SHA256}"
test "$(sha256sum "${INPUT_MANIFEST}" | awk '{print $1}')" = "${INPUT_MANIFEST_SHA256:?missing INPUT_MANIFEST_SHA256}"
test "$(sha256sum "${STAGING_DIR}/output_manifest.json" | awk '{print $1}')" = "${STAGED_OUTPUT_MANIFEST_SHA256:?missing STAGED_OUTPUT_MANIFEST_SHA256}"
test -d "${STAGING_DIR:?missing STAGING_DIR}"
test ! -e "${OUTPUT_DIR:?missing OUTPUT_DIR}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${VALIDATOR}" \
  --input-manifest "${INPUT_MANIFEST}" \
  --results "${STAGING_DIR}"
mv "${STAGING_DIR}" "${OUTPUT_DIR}"
echo "ITER011_VALIDATOR_ONLY_ATOMIC_PUBLICATION_PASS output=${OUTPUT_DIR}"
