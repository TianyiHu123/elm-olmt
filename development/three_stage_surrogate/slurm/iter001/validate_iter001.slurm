#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH --job-name=3stage_i001_val
#SBATCH --output=validate_%j.out
#SBATCH --error=validate_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly RUN_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data/runs/iter001_abby_jerc_data_init
readonly CANONICAL_SCRIPT=${REPO_ROOT}/development/three_stage_surrogate/slurm/iter001/validate_iter001.slurm
readonly CANONICAL_CONFIG=${REPO_ROOT}/development/three_stage_surrogate/slurm/iter001/iter001_config.json
readonly EXECUTION_MANIFEST=${REPO_ROOT}/development/three_stage_surrogate/slurm/iter001/iter001_execution_manifest.sha256
readonly SUBMITTED_SCRIPT=${RUN_DIR}/submit_validate_iter001.slurm
readonly SUBMISSION_CONFIG=${RUN_DIR}/submission_config.json
readonly SUBMITTED_MANIFEST=${RUN_DIR}/iter001_execution_manifest.sha256
readonly VALIDATE_TOOL=${REPO_ROOT}/development/three_stage_surrogate/tools/validate_surrogate_input_data.py
readonly PREPARE_ATTEMPT=${ITER001_PREPARE_CYCLE:?Set ITER001_PREPARE_CYCLE to 1..4}
readonly VALIDATION_ATTEMPT=${ITER001_OPERATIONAL_CYCLE:?Set ITER001_OPERATIONAL_CYCLE to 1..4}
readonly EXPECTED_CONFIG_SHA256=${ITER001_CONFIG_SHA256:?Set reviewed ITER001_CONFIG_SHA256}
readonly EXPECTED_MANIFEST_SHA256=${ITER001_MANIFEST_SHA256:?Set reviewed ITER001_MANIFEST_SHA256}
readonly OLMT_ENV_PREFIX=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma
readonly OLMT_PYTHON=${OLMT_ENV_PREFIX}/bin/python

test -f "${REPO_ROOT}/development/three_stage_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/three_stage_surrogate/iterations/iter001.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${VALIDATE_TOOL}"
test -f "${SUBMISSION_CONFIG}"
test -f "${SUBMITTED_SCRIPT}"
test -f "${SUBMITTED_MANIFEST}"
cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
cmp -s "${EXECUTION_MANIFEST}" "${SUBMITTED_MANIFEST}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${EXPECTED_CONFIG_SHA256}"
test "$(sha256sum "${SUBMITTED_MANIFEST}" | awk '{print $1}')" = "${EXPECTED_MANIFEST_SHA256}"
test "${PREPARE_ATTEMPT}" -ge 1
test "${PREPARE_ATTEMPT}" -le 4
test "${VALIDATION_ATTEMPT}" -ge 1
test "${VALIDATION_ATTEMPT}" -le 4
cd "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"

cd "${REPO_ROOT}"
sha256sum -c "${SUBMITTED_MANIFEST}"
test "$(git rev-parse HEAD)" = 174a7f6c33acbf111ef67533d6ef69ea33c91565
test -x "${OLMT_PYTHON}"
test "$("${OLMT_PYTHON}" -c 'import sys; print(sys.prefix)')" = "${OLMT_ENV_PREFIX}"
"${OLMT_PYTHON}" --version
/usr/bin/time -v "${OLMT_PYTHON}" "${VALIDATE_TOOL}" \
  --config "${SUBMISSION_CONFIG}" \
  --run-dir "${RUN_DIR}" \
  --prepare-attempt "${PREPARE_ATTEMPT}" \
  --validation-attempt "${VALIDATION_ATTEMPT}" \
  --publish
