#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=3stage_i008_diag
#SBATCH --output=diagnostic_%j.out
#SBATCH --error=diagnostic_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/diagnose_handoff_replay_iter008.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/diagnostic_execution_manifest.sha256"
readonly ATTEMPT="${ITER008_DIAGNOSTIC_ATTEMPT:?}"
readonly RELEASE_ATTEMPT="$(jq -r '.run_directories.release' "${CONFIG}")/attempt_1"
readonly OUTPUT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter008_abby_jerc_gpp_release/runs/diagnostic"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER008_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER008_DIAGNOSTIC_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_diagnose_handoff_replay_iter008.slurm"
test ! -e "${OUTPUT_DIR}"
mkdir -p "${RUN_DIR}/tmp_attempt_${ATTEMPT}"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${RUN_DIR}/cache_attempt_${ATTEMPT}"
export TMPDIR="${RUN_DIR}/tmp_attempt_${ATTEMPT}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter008/diagnose_handoff_replay_iter008.py" \
  --config "${CONFIG}" \
  --release-attempt "${RELEASE_ATTEMPT}" \
  --output "${OUTPUT_DIR}"
