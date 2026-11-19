#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=08:00:00
#SBATCH --job-name=3stage_i015_aggr
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter015_execution_manifest.sha256"
readonly ATTEMPT="${ITER015_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly PILOT_REPORT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/pilot/attempt_1/split_00/split_report.json"
readonly PRODUCTION_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/production/attempt_1"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/aggregate"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER015_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER015_EXECUTION_MANIFEST_SHA256:?}"
test "$(sha256sum "${PILOT_REPORT}" | cut -d' ' -f1)" = "${ITER015_PILOT_REPORT_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter015/aggregate_iter015.slurm" "${RUN_DIR}/submit_aggregate_iter015.slurm"
test ! -e "${OUTPUT_DIR}"
for split_id in $(seq -w 1 19); do
  test "$(jq -r '.result' "${PRODUCTION_DIR}/split_${split_id}/split_report.json")" = "pass"
  test "$(jq -r '.split_id' "${PRODUCTION_DIR}/split_${split_id}/split_report.json")" = "$((10#${split_id}))"
done

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
  -m development.three_stage_surrogate.slurm.iter015.aggregate_iter015 \
  --config "${CONFIG}" \
  --output "${OUTPUT_DIR}"
