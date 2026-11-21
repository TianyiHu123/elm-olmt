#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=3stage_i014_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter014_execution_manifest.sha256"
readonly ATTEMPT="${ITER014_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly INTEGRATION_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/runs/integration/attempt_3"
readonly PRODUCTS_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/products"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference/runs/final"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER014_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER014_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter014/final_iter014.slurm" "${RUN_DIR}/submit_final_iter014.slurm"
test ! -e "${OUTPUT_DIR}"
test -f "${INTEGRATION_DIR}/integration_report.json"
test -f "${PRODUCTS_DIR}/diagnostics_manifest.json"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
"${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter014/validate_iter014.py" \
  --config "${CONFIG}" \
  --integration "${INTEGRATION_DIR}" \
  --products "${PRODUCTS_DIR}" \
  --output "${OUTPUT_DIR}"
