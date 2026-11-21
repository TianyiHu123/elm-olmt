#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=3stage_i007_screenagg
#SBATCH --output=screen_aggregate_%j.out
#SBATCH --error=screen_aggregate_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/screen_aggregate_iter007.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter007_execution_manifest.sha256"
readonly ATTEMPT="${ITER007_ATTEMPT:?}"
readonly SCREEN_RUN_DIR="$(jq -r '.run_directories.screen' "${CONFIG}")"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
IFS=',' read -r -a SCREEN_ATTEMPTS <<< "${ITER007_SCREEN_ATTEMPTS:?}"
SCREEN_ROOT_ARGS=()
for leaf_attempt in "${SCREEN_ATTEMPTS[@]}"; do
  [[ "${leaf_attempt}" =~ ^[1-9][0-9]*$ ]]
  SCREEN_ROOT_ARGS+=(--screen-root "${SCREEN_RUN_DIR}/attempt_${leaf_attempt}")
done
test "${#SCREEN_ROOT_ARGS[@]}" -ge 2
test "${RUN_DIR}" = "$(jq -r '.run_directories.screen_aggregate' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER007_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER007_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_screen_aggregate_iter007.slurm"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/selection_iter007.py" \
  --mode screen \
  --config "${CONFIG}" \
  "${SCREEN_ROOT_ARGS[@]}" \
  --output-directory "${OUTPUT_DIR}"
"${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/validate_iter007.py" \
  --mode screen \
  --config "${CONFIG}" \
  "${SCREEN_ROOT_ARGS[@]}" \
  --output-directory "${OUTPUT_DIR}"
