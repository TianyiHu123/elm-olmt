#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=06:00:00
#SBATCH --job-name=3stage_i009_unit1
#SBATCH --output=unit1_%j.out
#SBATCH --error=unit1_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter009_execution_manifest.sha256"
readonly ATTEMPT="${ITER009_ATTEMPT:?}"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config/runs/unit1"
test "$(sha256sum "${CONFIG}"|cut -d' ' -f1)" = "${ITER009_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}"|cut -d' ' -f1)" = "${ITER009_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/unit1_iter009.slurm" "${RUN_DIR}/submit_unit1_iter009.slurm"
test ! -e "${OUTPUT_DIR}"
cd "${REPO_ROOT}"; sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}" TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
"${PYTHON_BIN}" -m unittest tests.test_three_stage_sr_iter009
/usr/bin/time -v "${PYTHON_BIN}" "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter009/unit1_iter009.py" --config "${CONFIG}" --output-directory "${OUTPUT_DIR}"
