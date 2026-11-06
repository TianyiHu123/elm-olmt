#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=16:00:00
#SBATCH --array=0-191%20
#SBATCH --job-name=3stage_i009_screen
#SBATCH --output=screen_%A_%a.out
#SBATCH --error=screen_%A_%a.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"; readonly RUN_DIR="$(pwd -P)"; readonly CONFIG="${RUN_DIR}/submission_config.json"; readonly MANIFEST="${RUN_DIR}/iter009_execution_manifest.sha256"; readonly ATTEMPT="${ITER009_ATTEMPT:?}"; readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly CANDIDATE_ID="$((SLURM_ARRAY_TASK_ID/8))"; readonly SPLIT_INDEX="$((SLURM_ARRAY_TASK_ID%8))"; readonly SPLIT_ID="$(jq -r ".screen_split_ids[${SPLIT_INDEX}]" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/candidate_manifest.json")"; readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}/candidate_$(printf '%02d' "${CANDIDATE_ID}")/split_$(printf '%02d' "${SPLIT_ID}")"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config/runs/screen"
test "$(sha256sum "${CONFIG}"|cut -d' ' -f1)" = "${ITER009_CONFIG_SHA256:?}"; test "$(sha256sum "${MANIFEST}"|cut -d' ' -f1)" = "${ITER009_EXECUTION_MANIFEST_SHA256:?}"; cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/screen_iter009.slurm" "${RUN_DIR}/submit_screen_iter009.slurm"; test ! -e "${OUTPUT_DIR}"; mkdir -p "$(dirname "${OUTPUT_DIR}")"; cd "${REPO_ROOT}"; sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 XDG_CACHE_HOME="${RUN_DIR}/attempt_${ATTEMPT}/cache_${SLURM_ARRAY_TASK_ID}" TMPDIR="${RUN_DIR}/attempt_${ATTEMPT}/tmp_${SLURM_ARRAY_TASK_ID}"; mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/run_leaf_iter009.py" --config "${CONFIG}" --candidate-id "${CANDIDATE_ID}" --split-id "${SPLIT_ID}" --output-directory "${OUTPUT_DIR}"
