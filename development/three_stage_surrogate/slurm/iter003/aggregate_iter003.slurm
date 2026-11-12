#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i003_agg
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/aggregate_iter003.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter003_execution_manifest.sha256"
readonly ATTEMPT="${ITER003_AGGREGATE_ATTEMPT:?ITER003_AGGREGATE_ATTEMPT is required}"
readonly CONFIG_SHA256="${ITER003_CONFIG_SHA256:?}"
readonly MANIFEST_SHA256="${ITER003_EXECUTION_MANIFEST_SHA256:?}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.aggregate' "${CONFIG}")"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_aggregate_iter003.slurm"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
"${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/aggregate_iter003.py" \
  --screen-root "$(jq -r '.run_directories.screen' "${CONFIG}")" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}"
