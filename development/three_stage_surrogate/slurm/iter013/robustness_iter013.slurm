#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=16:00:00
#SBATCH --array=0-19%20
#SBATCH --job-name=3stage_i013_robust
#SBATCH --output=robustness_%A_%a.out
#SBATCH --error=robustness_%A_%a.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter013_execution_manifest.sha256"
readonly ATTEMPT="${ITER013_ATTEMPT:?}"
readonly SPLIT_ID="${SLURM_ARRAY_TASK_ID}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}/split_$(printf '%02d' "${SPLIT_ID}")"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release/runs/robustness"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER013_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER013_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/robustness_iter013.slurm" "${RUN_DIR}/submit_robustness_iter013.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
readonly UNIT1_DIR="$(jq -r '.run_directories.unit1' "${CONFIG}")/attempt_${ITER013_UNIT1_ATTEMPT:?}"
test -f "${UNIT1_DIR}/ELIGIBLE"
test ! -e "${OUTPUT_DIR}"
mkdir -p "${RUN_DIR}/attempt_${ATTEMPT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/attempt_${ATTEMPT}/cache_${SPLIT_ID}"
export MPLCONFIGDIR="${RUN_DIR}/attempt_${ATTEMPT}/mpl_cache_${SPLIT_ID}"
export TMPDIR="${RUN_DIR}/attempt_${ATTEMPT}/tmp_${SPLIT_ID}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/run_split_iter013.py" \
  --config "${CONFIG}" \
  --raw-directory "$(jq -r '.raw_directory' "${CONFIG}")" \
  --split-id "${SPLIT_ID}" \
  --output-directory "${OUTPUT_DIR}"
