#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=20:00:00
#SBATCH --job-name=3stage_i008_release
#SBATCH --output=release_%j.out
#SBATCH --error=release_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/release_iter008.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter008_execution_manifest.sha256"
readonly ATTEMPT="${ITER008_ATTEMPT:?}"
readonly ROBUSTNESS_DIR="$(jq -r '.run_directories.robustness' "${CONFIG}")/attempt_${ITER008_ROBUSTNESS_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.release' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER008_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER008_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_release_iter008.slurm"
for split_id in $(seq -w 0 19); do
  test "$(jq -r '.result' "${ROBUSTNESS_DIR}/split_${split_id}/split_report.json")" = "pass"
  test "$(jq -r '.result' "${ROBUSTNESS_DIR}/split_${split_id}/reload_validation.json")" = "pass"
done
test ! -e "${OUTPUT_DIR}"
mkdir -p "${RUN_DIR}/tmp_attempt_${ATTEMPT}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/release_iter008.py" \
  --config "${CONFIG}" \
  --raw-directory "$(jq -r '.raw_directory' "${CONFIG}")" \
  --output-directory "${OUTPUT_DIR}"
