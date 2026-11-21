#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i005_prepare
#SBATCH --output=prepare_%j.out
#SBATCH --error=prepare_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/prepare_iter005.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter005_execution_manifest.sha256"
readonly ATTEMPT="${ITER005_ATTEMPT:?}"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PREPARED_DIR="${ATTEMPT_DIR}/prepared"
test "${RUN_DIR}" = "$(jq -r '.run_directories.prepare' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER005_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER005_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_prepare_iter005.slurm"
test ! -e "${ATTEMPT_DIR}"
mkdir -p "${ATTEMPT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${ATTEMPT_DIR}/cache"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/preflight_iter005.py" \
  --config "${CONFIG}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/prepare_iter005.py" \
  --config "${CONFIG}" \
  --output-directory "${PREPARED_DIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter005/validate_prepared_iter005.py" \
  --config "${CONFIG}" \
  --prepared-directory "${PREPARED_DIR}" \
  --output "${ATTEMPT_DIR}/prepared_validation_report.json"
touch "${ATTEMPT_DIR}/ELIGIBLE"
