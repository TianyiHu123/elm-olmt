#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=3stage_i003_pre
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err

set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/preflight_iter003.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter003_execution_manifest.sha256"
readonly ATTEMPT="${ITER003_PREFLIGHT_ATTEMPT:?ITER003_PREFLIGHT_ATTEMPT is required}"
readonly CONFIG_SHA256="${ITER003_CONFIG_SHA256:?ITER003_CONFIG_SHA256 is required}"
readonly MANIFEST_SHA256="${ITER003_EXECUTION_MANIFEST_SHA256:?ITER003_EXECUTION_MANIFEST_SHA256 is required}"

test -x "${PYTHON_BIN}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.preflight' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_preflight_iter003.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"

"${PYTHON_BIN}" -m unittest -v tests.test_three_stage_spinup
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter003/preflight_iter003.py" \
  --config "${CONFIG}" \
  --output-directory "${RUN_DIR}/attempt_${ATTEMPT}" \
  --attempt "${ATTEMPT}"
