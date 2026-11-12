#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i005_validate
#SBATCH --output=validation_%j.out
#SBATCH --error=validation_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/validation_iter005.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter005_execution_manifest.sha256"
readonly ATTEMPT="${ITER005_ATTEMPT:?}"
readonly PREPARE_DIR="$(jq -r '.run_directories.prepare' "${CONFIG}")/attempt_${ITER005_PREPARE_ATTEMPT:?}"
readonly BASELINE_DIR="$(jq -r '.run_directories.baseline' "${CONFIG}")/attempt_${ITER005_BASELINE_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.validation' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER005_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER005_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_validation_iter005.slurm"
test -f "${PREPARE_DIR}/ELIGIBLE"
test "$(jq -r '.result' "${BASELINE_DIR}/baseline_report.json")" = "pass"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/validate_iter005.py" \
  --config "${CONFIG}" \
  --prepared-directory "${PREPARE_DIR}/prepared" \
  --baseline-directory "${BASELINE_DIR}" \
  --output-directory "${OUTPUT_DIR}"
