#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i012_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter012_execution_manifest.sha256"
readonly ATTEMPT="${ITER012_ATTEMPT:?}"
readonly PRODUCTION_ATTEMPT="${ITER012_PRODUCTION_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PRODUCTION_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter012_abby_jerc_sr_gpp_ablation/runs/production/attempt_${PRODUCTION_ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter012_abby_jerc_sr_gpp_ablation/runs/final"
test "${PRODUCTION_ATTEMPT}" = "1"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER012_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER012_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter012/final_iter012.slurm" "${RUN_DIR}/submit_final_iter012.slurm"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export MPLCONFIGDIR="${RUN_DIR}/mpl_cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter012.aggregate_iter012 \
  --config "${CONFIG}" \
  --production-root "${PRODUCTION_ROOT}" \
  --output-directory "${OUTPUT_DIR}"
"${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter012.validate_iter012 \
  --config "${CONFIG}" \
  --production-root "${PRODUCTION_ROOT}" \
  --output-directory "${OUTPUT_DIR}"
