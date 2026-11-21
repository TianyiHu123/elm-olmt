#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i004_val
#SBATCH --output=validation_%j.out
#SBATCH --error=validation_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter004/validation_iter004.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter004_execution_manifest.sha256"
readonly ATTEMPT="${ITER004_ATTEMPT:?}"
readonly FIT_PACKAGE="$(jq -r '.run_directories.release_fit' "${CONFIG}")/attempt_${ITER004_RELEASE_FIT_ATTEMPT:?}/release_0001"
test "${RUN_DIR}" = "$(jq -r '.run_directories.validation' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER004_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER004_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_validation_iter004.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter004/validate_release_iter004.py" \
  --config "${CONFIG}" \
  --fit-package "${FIT_PACKAGE}" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}"
