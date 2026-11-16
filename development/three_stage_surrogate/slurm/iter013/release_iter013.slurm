#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=20:00:00
#SBATCH --job-name=3stage_i013_release
#SBATCH --output=release_%j.out
#SBATCH --error=release_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter013_execution_manifest.sha256"
readonly ATTEMPT="${ITER013_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release/runs/release"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER013_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER013_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/release_iter013.slurm" "${RUN_DIR}/submit_release_iter013.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
readonly AGGREGATE_DIR="$(jq -r '.run_directories.aggregate' "${CONFIG}")/attempt_${ITER013_AGGREGATE_ATTEMPT:?}"
test "$(jq -r '.result' "${AGGREGATE_DIR}/iter013_aggregate_report.json")" = "pass"
test ! -e "${OUTPUT_DIR}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export MPLCONFIGDIR="${RUN_DIR}/mpl_cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/release_iter013.py" \
  --config "${CONFIG}" \
  --raw-directory "$(jq -r '.raw_directory' "${CONFIG}")" \
  --aggregate-directory "${AGGREGATE_DIR}" \
  --output-directory "${OUTPUT_DIR}"
