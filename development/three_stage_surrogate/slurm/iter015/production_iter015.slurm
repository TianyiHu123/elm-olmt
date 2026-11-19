#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --array=1-19
#SBATCH --job-name=3stage_i015_prod
#SBATCH --output=production_%A_%a.out
#SBATCH --error=production_%A_%a.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter015_execution_manifest.sha256"
readonly ATTEMPT="${ITER015_ATTEMPT:?}"
readonly SPLIT_ID="${SLURM_ARRAY_TASK_ID}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}/split_$(printf '%02d' "${SPLIT_ID}")"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly PILOT_REPORT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/pilot/attempt_1/split_00/split_report.json"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/production"
test "${SPLIT_ID}" -ge 1
test "${SPLIT_ID}" -le 19
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER015_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER015_EXECUTION_MANIFEST_SHA256:?}"
test "$(sha256sum "${PILOT_REPORT}" | cut -d' ' -f1)" = "${ITER015_PILOT_REPORT_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter015/production_iter015.slurm" "${RUN_DIR}/submit_production_iter015.slurm"
test ! -e "${OUTPUT_DIR}"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"

mkdir -p "${RUN_DIR}/attempt_${ATTEMPT}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/attempt_${ATTEMPT}/cache_${SPLIT_ID}"
export MPLCONFIGDIR="${RUN_DIR}/attempt_${ATTEMPT}/mpl_${SPLIT_ID}"
export TMPDIR="${RUN_DIR}/attempt_${ATTEMPT}/tmp_${SPLIT_ID}"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter015.run_iter015 \
  --mode split \
  --config "${CONFIG}" \
  --split-id "${SPLIT_ID}" \
  --output "${OUTPUT_DIR}"
