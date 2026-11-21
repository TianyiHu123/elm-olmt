#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=06:00:00
#SBATCH --job-name=3stage_i015_unit1
#SBATCH --output=unit1_%j.out
#SBATCH --error=unit1_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter015_execution_manifest.sha256"
readonly ATTEMPT="${ITER015_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness/runs/unit1"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER015_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER015_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter015/unit1_iter015.slurm" "${RUN_DIR}/submit_unit1_iter015.slurm"
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
export ITER014_CONFIG="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter014/iter014_config.json"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

"${PYTHON_BIN}" -m unittest \
  tests.test_three_stage_inference_iter014 \
  tests.test_three_stage_full_chain_iter015

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter015.run_iter015 \
  --mode preflight \
  --config "${CONFIG}" \
  --output "${OUTPUT_DIR}"
