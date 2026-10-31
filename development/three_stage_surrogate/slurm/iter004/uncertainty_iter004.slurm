#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i004_unc
#SBATCH --output=uncertainty_%j.out
#SBATCH --error=uncertainty_%j.err

set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter004/uncertainty_iter004.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter004_execution_manifest.sha256"
readonly ATTEMPT="${ITER004_ATTEMPT:?}"
readonly SPLIT_MANIFEST="$(jq -r '.run_directories.preflight' "${CONFIG}")/attempt_${ITER004_PREFLIGHT_ATTEMPT:?}/repeated_split_manifest.json"
readonly ROBUSTNESS_DIRECTORY="$(jq -r '.run_directories.robustness' "${CONFIG}")/attempt_${ITER004_ROBUSTNESS_ATTEMPT:?}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.uncertainty' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER004_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER004_EXECUTION_MANIFEST_SHA256:?}"
test "$(sha256sum "${SPLIT_MANIFEST}" | cut -d' ' -f1)" = "${ITER004_SPLIT_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_uncertainty_iter004.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter004/aggregate_uncertainty_iter004.py" \
  --robustness-directory "${ROBUSTNESS_DIRECTORY}" \
  --split-manifest "${SPLIT_MANIFEST}" \
  --split-sha256 "${ITER004_SPLIT_SHA256}" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}"
