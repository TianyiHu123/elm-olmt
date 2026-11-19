#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00
#SBATCH --job-name=3stage_i015_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter015_execution_manifest.sha256"
readonly ATTEMPT="${ITER015_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly AGGREGATE_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/aggregate/attempt_1"
readonly AGGREGATE_REPORT="${AGGREGATE_DIR}/aggregate_report.json"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/final"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER015_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER015_EXECUTION_MANIFEST_SHA256:?}"
test "$(sha256sum "${AGGREGATE_REPORT}" | cut -d' ' -f1)" = "${ITER015_AGGREGATE_REPORT_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter015/final_iter015.slurm" "${RUN_DIR}/submit_final_iter015.slurm"
test "$(jq -r '.result' "${AGGREGATE_REPORT}")" = "pass"
test ! -e "${OUTPUT_DIR}"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter015.final_iter015 \
  --config "${CONFIG}" \
  --aggregate "${AGGREGATE_DIR}" \
  --output "${OUTPUT_DIR}"
