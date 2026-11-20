#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i016_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/final_config.json"
readonly MANIFEST="${RUN_DIR}/iter016_final_execution_manifest.sha256"
readonly ATTEMPT="${ITER016_FINAL_ATTEMPT:?}"
readonly OUTPUT="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter016_abby_jerc_frozen_release_fixed_test/runs/final"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER016_FINAL_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER016_FINAL_MANIFEST_SHA256:?}"
test ! -e "${OUTPUT}"
test ! -e "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc/catalog.json"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter016/final_iter016.slurm" "${RUN_DIR}/submit_final_iter016.slurm"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_1" MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_1" TMPDIR="${RUN_DIR}/tmp_attempt_1"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter016.final_iter016 \
  --config "${CONFIG}" \
  --output "${OUTPUT}"
