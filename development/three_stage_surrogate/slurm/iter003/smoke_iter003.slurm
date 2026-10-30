#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i003_smoke
#SBATCH --output=smoke_%j.out
#SBATCH --error=smoke_%j.err

set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/smoke_iter003.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly CANDIDATES="${RUN_DIR}/candidate_manifest.json"
readonly SPLITS="${RUN_DIR}/repeated_split_manifest.json"
readonly MANIFEST="${RUN_DIR}/iter003_execution_manifest.sha256"
readonly ATTEMPT="${ITER003_SMOKE_ATTEMPT:?ITER003_SMOKE_ATTEMPT is required}"
readonly CONFIG_SHA256="${ITER003_CONFIG_SHA256:?ITER003_CONFIG_SHA256 is required}"
readonly MANIFEST_SHA256="${ITER003_EXECUTION_MANIFEST_SHA256:?ITER003_EXECUTION_MANIFEST_SHA256 is required}"
readonly CANDIDATE_SHA256="${ITER003_CANDIDATE_MANIFEST_SHA256:?ITER003_CANDIDATE_MANIFEST_SHA256 is required}"
readonly SPLIT_SHA256="${ITER003_SPLIT_MANIFEST_SHA256:?ITER003_SPLIT_MANIFEST_SHA256 is required}"

test "${RUN_DIR}" = "$(jq -r '.run_directories.smoke' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
test "$(sha256sum "${CANDIDATES}" | cut -d' ' -f1)" = "${CANDIDATE_SHA256}"
test "$(sha256sum "${SPLITS}" | cut -d' ' -f1)" = "${SPLIT_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_smoke_iter003.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"

for candidate_id in 15 84 90; do
  hidden_layers="$(jq -r --argjson id "${candidate_id}" '.candidates[$id].config.hidden_layer_sizes | map(tostring) | join(",")' "${CANDIDATES}")"
  activation="$(jq -r --argjson id "${candidate_id}" '.candidates[$id].config.activation' "${CANDIDATES}")"
  alpha="$(jq -r --argjson id "${candidate_id}" '.candidates[$id].config.alpha' "${CANDIDATES}")"
  /usr/bin/time -v "${PYTHON_BIN}" "${REPO_ROOT}/screen_three_stage_spinup.py" \
    --config "${CONFIG}" \
    --candidate-manifest "${CANDIDATES}" \
    --split-manifest "${SPLITS}" \
    --candidate-id "${candidate_id}" \
    --hidden-layers "${hidden_layers}" \
    --activation "${activation}" \
    --solver lbfgs \
    --alpha "${alpha}" \
    --max-iter 800 \
    --random-state 42 \
    --attempt "${ATTEMPT}" \
    --split-limit 1 \
    --output-directory "${RUN_DIR}/attempt_${ATTEMPT}/candidate_$(printf '%03d' "${candidate_id}")"
done
echo "ITER003_SMOKE_OK attempt=${ATTEMPT} candidates=15,84,90 splits=1"
