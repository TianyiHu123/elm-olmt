#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i010_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter010_execution_manifest.sha256"
readonly ATTEMPT="${ITER010_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter010_abby_jerc_sr_refinement/runs/final"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER010_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER010_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter010/final_iter010.slurm" "${RUN_DIR}/submit_final_iter010.slurm"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
readonly SCREEN_ROOT="$(jq -r '.run_directories.screen' "${CONFIG}")/attempt_${ITER010_SCREEN_ATTEMPT:?}"
readonly FINALIST_ROOT="$(jq -r '.run_directories.finalists' "${CONFIG}")/attempt_${ITER010_FINALIST_ATTEMPT:?}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter010/selection_iter010.py" \
  --mode final \
  --config "${CONFIG}" \
  --screen-root "${SCREEN_ROOT}" \
  --finalist-root "${FINALIST_ROOT}" \
  --output-directory "${OUTPUT_DIR}"
"${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter010/validate_iter010.py" \
  --config "${CONFIG}" \
  --screen-root "${SCREEN_ROOT}" \
  --finalist-root "${FINALIST_ROOT}" \
  --output-directory "${OUTPUT_DIR}"
