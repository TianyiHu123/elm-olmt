#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=16:00:00
#SBATCH --array=1-20
#SBATCH --job-name=3stage_i008_robust
#SBATCH --output=robustness_%A_%a.out
#SBATCH --error=robustness_%A_%a.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/robustness_iter008.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter008_execution_manifest.sha256"
readonly ATTEMPT="${ITER008_ATTEMPT:?}"
readonly PREFLIGHT_DIR="$(jq -r '.run_directories.preflight' "${CONFIG}")/attempt_${ITER008_PREFLIGHT_ATTEMPT:?}"
readonly SPLIT_ID="$((SLURM_ARRAY_TASK_ID - 1))"
readonly SPLIT_PADDED="$(printf '%02d' "${SPLIT_ID}")"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly OUTPUT_DIR="${ATTEMPT_DIR}/split_${SPLIT_PADDED}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.robustness' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER008_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER008_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_robustness_iter008.slurm"
test -f "${PREFLIGHT_DIR}/ELIGIBLE"
test ! -e "${OUTPUT_DIR}"
mkdir -p "${ATTEMPT_DIR}" "${OUTPUT_DIR}_tmp"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${OUTPUT_DIR}_cache"
export TMPDIR="${OUTPUT_DIR}_tmp"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/run_split_iter008.py" \
  --config "${CONFIG}" \
  --raw-directory "$(jq -r '.raw_directory' "${CONFIG}")" \
  --split-id "${SPLIT_ID}" \
  --output-directory "${OUTPUT_DIR}"
