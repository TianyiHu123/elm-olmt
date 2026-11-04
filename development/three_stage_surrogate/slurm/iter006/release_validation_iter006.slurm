#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i006_validate
#SBATCH --output=release_validation_%j.out
#SBATCH --error=release_validation_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/release_validation_iter006.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter006_execution_manifest.sha256"
readonly ATTEMPT="${ITER006_ATTEMPT:?}"
readonly PREPARE_DIR="$(jq -r '.run_directories.prepare' "${CONFIG}")/attempt_${ITER006_PREPARE_ATTEMPT:?}"
readonly RELEASE_DIR="$(jq -r '.run_directories.release' "${CONFIG}")/attempt_${ITER006_RELEASE_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.release_validation' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER006_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER006_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_release_validation_iter006.slurm"
test "$(jq -r '.result' "${RELEASE_DIR}/release_fit_report.json")" = "pass"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/validate_release_iter006.py" \
  --config "${CONFIG}" \
  --raw-directory "${PREPARE_DIR}/raw" \
  --fit-package "${RELEASE_DIR}/release_0001" \
  --output-directory "${OUTPUT_DIR}"
