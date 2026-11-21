#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=16:00:00
#SBATCH --array=0-71%20
#SBATCH --job-name=3stage_i009_finalists
#SBATCH --output=finalists_%A_%a.out
#SBATCH --error=finalists_%A_%a.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"; readonly RUN_DIR="$(pwd -P)"; readonly CONFIG="${RUN_DIR}/submission_config.json"; readonly MANIFEST="${RUN_DIR}/iter009_execution_manifest.sha256"; readonly ATTEMPT="${ITER009_ATTEMPT:?}"; readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config/runs/finalists"
test "$(sha256sum "${CONFIG}"|cut -d' ' -f1)" = "${ITER009_CONFIG_SHA256:?}"; test "$(sha256sum "${MANIFEST}"|cut -d' ' -f1)" = "${ITER009_EXECUTION_MANIFEST_SHA256:?}"; cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/finalists_iter009.slurm" "${RUN_DIR}/submit_finalists_iter009.slurm"; cd "${REPO_ROOT}"; sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 XDG_CACHE_HOME="${RUN_DIR}/attempt_${ATTEMPT}/cache_${SLURM_ARRAY_TASK_ID}" TMPDIR="${RUN_DIR}/attempt_${ATTEMPT}/tmp_${SLURM_ARRAY_TASK_ID}"; mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
readonly SCREEN_ROOT="$(jq -r '.run_directories.screen' "${CONFIG}")/attempt_${ITER009_SCREEN_ATTEMPT:?}"
readonly MAP_JSON="$(${PYTHON_BIN} "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/selection_iter009.py" --mode map --config "${CONFIG}" --screen-root "${SCREEN_ROOT}" --task-id "${SLURM_ARRAY_TASK_ID}")"; readonly CANDIDATE_ID="$(jq -r '.candidate_id' <<<"${MAP_JSON}")"; readonly SPLIT_ID="$(jq -r '.split_id' <<<"${MAP_JSON}")"; readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}/candidate_$(printf '%02d' "${CANDIDATE_ID}")/split_$(printf '%02d' "${SPLIT_ID}")"
test ! -e "${OUTPUT_DIR}"; mkdir -p "${OUTPUT_DIR}"; printf '%s\n' "${MAP_JSON}" > "${OUTPUT_DIR}/task_map.json"
# fit_leaf requires a nonexistent output path; preserve the map beside it.
mv "${OUTPUT_DIR}/task_map.json" "$(dirname "${OUTPUT_DIR}")/task_map_$(printf '%02d' "${SPLIT_ID}").json"; rmdir "${OUTPUT_DIR}"
/usr/bin/time -v "${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/run_leaf_iter009.py" --config "${CONFIG}" --candidate-id "${CANDIDATE_ID}" --split-id "${SPLIT_ID}" --output-directory "${OUTPUT_DIR}"
