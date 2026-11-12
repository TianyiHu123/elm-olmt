#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i003_val
#SBATCH --output=validation_%j.out
#SBATCH --error=validation_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/validate_iter003.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter003_execution_manifest.sha256"
readonly ATTEMPT="${ITER003_VALIDATION_ATTEMPT:?ITER003_VALIDATION_ATTEMPT is required}"
readonly CONFIG_SHA256="${ITER003_CONFIG_SHA256:?}"
readonly MANIFEST_SHA256="${ITER003_EXECUTION_MANIFEST_SHA256:?}"
readonly CANDIDATE_SHA256="${ITER003_CANDIDATE_MANIFEST_SHA256:?}"
readonly SPLIT_SHA256="${ITER003_SPLIT_MANIFEST_SHA256:?}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.validation' "${CONFIG}")"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_validate_iter003.slurm"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
"${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/validate_iter003.py" \
  --screen-root "$(jq -r '.run_directories.screen' "${CONFIG}")" \
  --aggregate-directory "$(jq -r '.run_directories.aggregate' "${CONFIG}")/attempt_${ITER003_AGGREGATE_ATTEMPT:?}" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}" \
  --candidate-sha256 "${CANDIDATE_SHA256}" \
  --split-sha256 "${SPLIT_SHA256}" \
  --candidate-manifest "$(jq -r '.run_directories.screen' "${CONFIG}")/candidate_manifest.json" \
  --split-manifest "$(jq -r '.run_directories.screen' "${CONFIG}")/repeated_split_manifest.json" \
  --global-split "$(jq -r '.snapshot_root' "${CONFIG}")/splits/member_split_1024_v1.json"
