#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=3stage_i016_recover
#SBATCH --output=recover_%j.out
#SBATCH --error=recover_%j.err
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly RECOVERY_CONFIG="${RUN_DIR}/recovery_config.json"
readonly MANIFEST="${RUN_DIR}/iter016_recovery_execution_manifest.sha256"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_2"
readonly SOURCE_DIR="${RUN_DIR}/attempt_1"
readonly SOURCE_MANIFEST="${SOURCE_DIR}/artifact_package/artifact_manifest.json"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"

test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter016_abby_jerc_frozen_release_fixed_test/runs/refit"
test "$(sha256sum "${RECOVERY_CONFIG}" | cut -d' ' -f1)" = "${ITER016_RECOVERY_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER016_RECOVERY_MANIFEST_SHA256:?}"
test "$(sha256sum "${SOURCE_MANIFEST}" | cut -d' ' -f1)" = "eaed33d620711fd491042e78e6988146b16585c29b9c4904170afa1855ce1c48"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter016/recover_refit_iter016.slurm" "${RUN_DIR}/submit_recover_refit_iter016.slurm"
test -d "${SOURCE_DIR}"
test ! -e "${OUTPUT_DIR}"

cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_2"
export MPLCONFIGDIR="${RUN_DIR}/mpl_attempt_2"
export TMPDIR="${RUN_DIR}/tmp_attempt_2"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"

/usr/bin/time -v "${PYTHON_BIN}" \
  -m development.three_stage_surrogate.slurm.iter016.recover_iter016 \
  --recovery-config "${RECOVERY_CONFIG}" \
  --execution-manifest "${MANIFEST}" \
  --output "${OUTPUT_DIR}"
