#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --job-name=3stage_i015_pilot
#SBATCH --output=pilot_%j.out
#SBATCH --error=pilot_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter015_execution_manifest.sha256"
readonly ATTEMPT="${ITER015_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}/split_00"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly UNIT1_DIR="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/unit1/attempt_1"
readonly UNIT1_PREFLIGHT="${UNIT1_DIR}/preflight_report.json"
readonly UNIT1_SMOKE="${UNIT1_DIR}/smoke/split_report.json"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/pilot"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER015_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER015_EXECUTION_MANIFEST_SHA256:?}"
test "$(sha256sum "${UNIT1_PREFLIGHT}" | cut -d' ' -f1)" = "${ITER015_UNIT1_PREFLIGHT_SHA256:?}"
test "$(sha256sum "${UNIT1_SMOKE}" | cut -d' ' -f1)" = "${ITER015_UNIT1_SMOKE_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter015/pilot_iter015.slurm" "${RUN_DIR}/submit_pilot_iter015.slurm"
test ! -e "${OUTPUT_DIR}"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"

mkdir -p "${RUN_DIR}/attempt_${ATTEMPT}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/attempt_${ATTEMPT}/cache"
export MPLCONFIGDIR="${RUN_DIR}/attempt_${ATTEMPT}/mpl"
export TMPDIR="${RUN_DIR}/attempt_${ATTEMPT}/tmp"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter015.run_iter015 \
  --mode split \
  --config "${CONFIG}" \
  --split-id 0 \
  --output "${OUTPUT_DIR}"
