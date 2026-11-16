#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=06:00:00
#SBATCH --job-name=3stage_i013_final
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter013_execution_manifest.sha256"
readonly ATTEMPT="${ITER013_ATTEMPT:?}"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
test "${RUN_DIR}" = "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release/runs/final"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER013_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER013_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/final_iter013.slurm" "${RUN_DIR}/submit_final_iter013.slurm"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
readonly RELEASE_DIR="$(jq -r '.run_directories.release' "${CONFIG}")/attempt_${ITER013_RELEASE_ATTEMPT:?}"
test "$(jq -r '.result' "${RELEASE_DIR}/release_fit_report.json")" = "pass"
test "$(jq -r '.convergence_warning_count' "${RELEASE_DIR}/release_fit_report.json")" = "0"
test ! -e "${ATTEMPT_DIR}"
mkdir -p "${ATTEMPT_DIR}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${ATTEMPT_DIR}/cache"
export MPLCONFIGDIR="${ATTEMPT_DIR}/mpl_cache"
export TMPDIR="${ATTEMPT_DIR}/tmp"
mkdir -p "${XDG_CACHE_HOME}" "${MPLCONFIGDIR}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/final_iter013.py" \
  --config "${CONFIG}" \
  --release-core "${RELEASE_DIR}/release_0001" \
  --attempt-directory "${ATTEMPT_DIR}"
bash "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter013/publish_iter013.sh" \
  "${ATTEMPT_DIR}/validation/release_0001" \
  "$(jq -r '.output_root' "${CONFIG}")/staging" \
  "$(jq -r '.stable_product_root' "${CONFIG}")"
