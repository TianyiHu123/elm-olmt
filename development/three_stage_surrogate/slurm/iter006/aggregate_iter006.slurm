#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i006_aggregate
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/aggregate_iter006.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter006_execution_manifest.sha256"
readonly ATTEMPT="${ITER006_ATTEMPT:?}"
readonly ROBUSTNESS_DIR="$(jq -r '.run_directories.robustness' "${CONFIG}")/attempt_${ITER006_ROBUSTNESS_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.aggregate' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER006_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER006_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_aggregate_iter006.slurm"
test ! -e "${OUTPUT_DIR}"
for split in $(seq -w 0 19); do test "$(jq -r '.result' "${ROBUSTNESS_DIR}/split_${split}/split_report.json")" = "pass"; test "$(jq -r '.result' "${ROBUSTNESS_DIR}/split_${split}/reload_validation.json")" = "pass"; done
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/aggregate_iter006.py" \
  --config "${CONFIG}" \
  --robustness-directory "${ROBUSTNESS_DIR}" \
  --output-directory "${OUTPUT_DIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter006/validate_aggregate_iter006.py" \
  --config "${CONFIG}" \
  --robustness-directory "${ROBUSTNESS_DIR}" \
  --aggregate-directory "${OUTPUT_DIR}"
