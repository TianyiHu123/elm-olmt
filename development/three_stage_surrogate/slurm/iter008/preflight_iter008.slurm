#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=25G
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i008_preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/preflight_iter008.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter008_execution_manifest.sha256"
readonly ATTEMPT="${ITER008_ATTEMPT:?}"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.preflight' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER008_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER008_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_preflight_iter008.slurm"
test ! -e "${ATTEMPT_DIR}"
mkdir -p "${ATTEMPT_DIR}/tmp"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${ATTEMPT_DIR}/cache"
export TMPDIR="${ATTEMPT_DIR}/tmp"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/preflight_iter008.py" \
  --config "${CONFIG}" \
  --attempt-directory "${ATTEMPT_DIR}"
