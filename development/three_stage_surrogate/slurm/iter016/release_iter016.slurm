#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=3stage_i016_release
#SBATCH --output=release_%j.out
#SBATCH --error=release_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/release_config.json"
readonly MANIFEST="${RUN_DIR}/iter016_release_execution_manifest.sha256"
readonly OUTPUT="${RUN_DIR}/attempt_1"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter016_abby_jerc_frozen_release_fixed_test/runs/release"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER016_RELEASE_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER016_RELEASE_MANIFEST_SHA256:?}"
test ! -e "${OUTPUT}"
test ! -e "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter016/release_iter016.slurm" "${RUN_DIR}/submit_release_iter016.slurm"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_1" MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_1" TMPDIR="${RUN_DIR}/tmp_attempt_1"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter016.release_iter016 \
  --config "${CONFIG}" \
  --output "${OUTPUT}"
