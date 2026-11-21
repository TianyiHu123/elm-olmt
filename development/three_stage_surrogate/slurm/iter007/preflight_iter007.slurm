#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=25G
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i007_preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/preflight_iter007.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter007_execution_manifest.sha256"
readonly ATTEMPT="${ITER007_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.preflight' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER007_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER007_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_preflight_iter007.slurm"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/preflight_iter007.py" \
  --config "${CONFIG}" \
  --output-directory "${OUTPUT_DIR}"
