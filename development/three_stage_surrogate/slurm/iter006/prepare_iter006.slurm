#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=25G
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i006_prepare
#SBATCH --output=prepare_%j.out
#SBATCH --error=prepare_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/prepare_iter006.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter006_execution_manifest.sha256"
readonly ATTEMPT="${ITER006_ATTEMPT:?}"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.prepare' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER006_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER006_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_prepare_iter006.slurm"
test ! -e "${ATTEMPT_DIR}"
mkdir -p "${ATTEMPT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${ATTEMPT_DIR}/cache"
export TMPDIR="${ATTEMPT_DIR}/tmp"
mkdir -p "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/preflight_iter006.py" \
  --config "${CONFIG}" \
  --output-directory "${ATTEMPT_DIR}/preflight"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/prepare_iter006.py" \
  --config "${CONFIG}" \
  --attempt-directory "${ATTEMPT_DIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/validate_raw_iter006.py" \
  --config "${CONFIG}" \
  --raw-directory "${ATTEMPT_DIR}/raw" \
  --output "${ATTEMPT_DIR}/raw_validation_report.json"
