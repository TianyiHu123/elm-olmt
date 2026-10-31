#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --array=0-95
#SBATCH --job-name=3stage_i003_screen
#SBATCH --output=screen_%A_%a.out
#SBATCH --error=screen_%A_%a.err

set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/screen_iter003.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly CANDIDATES="${RUN_DIR}/candidate_manifest.json"
readonly SPLITS="${RUN_DIR}/repeated_split_manifest.json"
readonly MANIFEST="${RUN_DIR}/iter003_execution_manifest.sha256"
readonly ATTEMPT="${ITER003_SCREEN_ATTEMPT:?ITER003_SCREEN_ATTEMPT is required}"
readonly CANDIDATE_ID="${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"
readonly CONFIG_SHA256="${ITER003_CONFIG_SHA256:?ITER003_CONFIG_SHA256 is required}"
readonly MANIFEST_SHA256="${ITER003_EXECUTION_MANIFEST_SHA256:?ITER003_EXECUTION_MANIFEST_SHA256 is required}"
readonly CANDIDATE_SHA256="${ITER003_CANDIDATE_MANIFEST_SHA256:?ITER003_CANDIDATE_MANIFEST_SHA256 is required}"
readonly SPLIT_SHA256="${ITER003_SPLIT_MANIFEST_SHA256:?ITER003_SPLIT_MANIFEST_SHA256 is required}"

test "${RUN_DIR}" = "$(jq -r '.run_directories.screen' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
test "$(sha256sum "${CANDIDATES}" | cut -d' ' -f1)" = "${CANDIDATE_SHA256}"
test "$(sha256sum "${SPLITS}" | cut -d' ' -f1)" = "${SPLIT_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_screen_iter003.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_${SLURM_ARRAY_JOB_ID}_${CANDIDATE_ID}"

hidden_layers="$(jq -r --argjson id "${CANDIDATE_ID}" '.candidates[$id].config.hidden_layer_sizes | map(tostring) | join(",")' "${CANDIDATES}")"
activation="$(jq -r --argjson id "${CANDIDATE_ID}" '.candidates[$id].config.activation' "${CANDIDATES}")"
alpha="$(jq -r --argjson id "${CANDIDATE_ID}" '.candidates[$id].config.alpha' "${CANDIDATES}")"
candidate_label="$(printf '%03d' "${CANDIDATE_ID}")"

/usr/bin/time -v "${PYTHON_BIN}" "${REPO_ROOT}/screen_three_stage_spinup.py" \
  --config "${CONFIG}" \
  --candidate-manifest "${CANDIDATES}" \
  --split-manifest "${SPLITS}" \
  --candidate-id "${CANDIDATE_ID}" \
  --hidden-layers "${hidden_layers}" \
  --activation "${activation}" \
  --solver lbfgs \
  --alpha "${alpha}" \
  --max-iter 800 \
  --random-state 42 \
  --attempt "${ATTEMPT}" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}/candidate_${candidate_label}"
