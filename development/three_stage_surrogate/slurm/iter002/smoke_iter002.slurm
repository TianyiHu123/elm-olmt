#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=3stage_i002_smoke
#SBATCH --output=smoke_%j.out
#SBATCH --error=smoke_%j.err

set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter002/smoke_iter002.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly SUBMITTED_CONFIG="${RUN_DIR}/submission_config.json"
readonly SUBMITTED_MANIFEST="${RUN_DIR}/iter002_execution_manifest.sha256"
readonly CYCLE="${ITER002_OPERATIONAL_CYCLE:?ITER002_OPERATIONAL_CYCLE is required}"
readonly CONFIG_SHA256="${ITER002_CONFIG_SHA256:?ITER002_CONFIG_SHA256 is required}"
readonly MANIFEST_SHA256="${ITER002_EXECUTION_MANIFEST_SHA256:?ITER002_EXECUTION_MANIFEST_SHA256 is required}"

test -x "${PYTHON_BIN}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.smoke' "${SUBMITTED_CONFIG}")"
test "$(sha256sum "${SUBMITTED_CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${SUBMITTED_MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_smoke_iter002.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${SUBMITTED_MANIFEST}"
"${PYTHON_BIN}" -c 'import sys; assert sys.prefix == "/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma"'
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MPLCONFIGDIR="${RUN_DIR}/matplotlib_attempt_${CYCLE}"

/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/train_three_stage_spinup.py" \
  --config "${SUBMITTED_CONFIG}" \
  --run-kind smoke \
  --attempt "${CYCLE}"
