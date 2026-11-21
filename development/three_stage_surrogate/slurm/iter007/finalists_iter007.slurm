#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=60G
#SBATCH --time=16:00:00
#SBATCH --array=0-71%20
#SBATCH --job-name=3stage_i007_finalists
#SBATCH --output=finalists_%A_%a.out
#SBATCH --error=finalists_%A_%a.err
set -euo pipefail
readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/finalists_iter007.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly CONFIG="${RUN_DIR}/submission_config.json"
readonly MANIFEST="${RUN_DIR}/iter007_execution_manifest.sha256"
readonly ATTEMPT="${ITER007_ATTEMPT:?}"
readonly SCREEN_AGGREGATE_DIR="$(jq -r '.run_directories.screen_aggregate' "${CONFIG}")/attempt_${ITER007_SCREEN_AGGREGATE_ATTEMPT:?}"
readonly FINALIST_MANIFEST="${SCREEN_AGGREGATE_DIR}/finalist_manifest.json"
readonly EXPECTED_FINALIST_MANIFEST_SHA256="$(jq -r '.finalist_manifest_sha256' "${SCREEN_AGGREGATE_DIR}/screen_aggregate_report.json")"
readonly FINALIST_INDEX="$((SLURM_ARRAY_TASK_ID / 12))"
readonly SPLIT_INDEX="$((SLURM_ARRAY_TASK_ID % 12))"
readonly CANDIDATE_ID="$(jq -r ".finalist_candidate_ids[${FINALIST_INDEX}]" "${FINALIST_MANIFEST}")"
readonly SPLIT_ID="$(jq -r ".finalist_split_ids[${SPLIT_INDEX}]" "${FINALIST_MANIFEST}")"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${ATTEMPT}"
readonly OUTPUT_DIR="${ATTEMPT_DIR}/candidate_$(printf '%02d' "${CANDIDATE_ID}")/split_$(printf '%02d' "${SPLIT_ID}")"
test "${RUN_DIR}" = "$(jq -r '.run_directories.finalists' "${CONFIG}")"
test "$(sha256sum "${CONFIG}" | cut -d' ' -f1)" = "${ITER007_CONFIG_SHA256:?}"
test "$(sha256sum "${MANIFEST}" | cut -d' ' -f1)" = "${ITER007_EXECUTION_MANIFEST_SHA256:?}"
cmp -s "${CANONICAL}" "${RUN_DIR}/submit_finalists_iter007.slurm"
test "$(jq -r '.result' "${SCREEN_AGGREGATE_DIR}/screen_validation.json")" = "pass"
test "$(jq -r '.finalist_manifest_sha256' "${SCREEN_AGGREGATE_DIR}/screen_validation.json")" = "${EXPECTED_FINALIST_MANIFEST_SHA256}"
test "$(sha256sum "${FINALIST_MANIFEST}" | cut -d' ' -f1)" = "${EXPECTED_FINALIST_MANIFEST_SHA256}"
test ! -e "${OUTPUT_DIR}"
mkdir -p "$(dirname "${OUTPUT_DIR}")"
cd "${REPO_ROOT}"
sha256sum -c "${MANIFEST}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export XDG_CACHE_HOME="${ATTEMPT_DIR}/cache_task_${SLURM_ARRAY_TASK_ID}"
export TMPDIR="${ATTEMPT_DIR}/tmp_task_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${XDG_CACHE_HOME}" "${TMPDIR}"
/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter007/run_leaf_iter007.py" \
  --config "${CONFIG}" \
  --candidate-id "${CANDIDATE_ID}" \
  --split-id "${SPLIT_ID}" \
  --output-directory "${OUTPUT_DIR}"
