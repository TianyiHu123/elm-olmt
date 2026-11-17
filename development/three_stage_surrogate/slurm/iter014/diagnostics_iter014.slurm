#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i014_diag
#SBATCH --output=diagnostics_%j.out
#SBATCH --error=diagnostics_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter014_execution_manifest.sha256"
readonly ATTEMPT="${ITER014_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PRODUCTS_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/products"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/runs/diagnostics"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER014_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER014_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter014/diagnostics_iter014.slurm" "${RUN_DIR}/submit_diagnostics_iter014.slurm"
test ! -e "${OUTPUT_DIR}"
test -d "${PRODUCTS_DIR}"
test -z "$(find "${PRODUCTS_DIR}" -mindepth 1 -maxdepth 1 -print -quit)"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
"${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter014/diagnostics_iter014.py" \
  --config "${CONFIG}" \
  --output "${OUTPUT_DIR}"
cp -a "${OUTPUT_DIR}/." "${PRODUCTS_DIR}/"
(
  cd "${PRODUCTS_DIR}"
  sha256sum -c evidence.sha256
)
