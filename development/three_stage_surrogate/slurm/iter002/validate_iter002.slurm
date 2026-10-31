#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=3stage_i002_val
#SBATCH --output=validation_%j.out
#SBATCH --error=validation_%j.err

set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/three_stage_surrogate/slurm/iter002/validate_iter002.slurm"
readonly PYTHON_BIN="/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python"
readonly RUN_DIR="$(pwd -P)"
readonly SUBMITTED_CONFIG="${RUN_DIR}/submission_config.json"
readonly SUBMITTED_MANIFEST="${RUN_DIR}/iter002_execution_manifest.sha256"
readonly CYCLE="${ITER002_OPERATIONAL_CYCLE:?ITER002_OPERATIONAL_CYCLE is required}"
readonly SMOKE_ATTEMPT="${ITER002_SMOKE_ATTEMPT:?ITER002_SMOKE_ATTEMPT is required}"
readonly OPERATIONAL_ATTEMPT="${ITER002_OPERATIONAL_ATTEMPT:?ITER002_OPERATIONAL_ATTEMPT is required}"
readonly CONFIG_SHA256="${ITER002_CONFIG_SHA256:?ITER002_CONFIG_SHA256 is required}"
readonly MANIFEST_SHA256="${ITER002_EXECUTION_MANIFEST_SHA256:?ITER002_EXECUTION_MANIFEST_SHA256 is required}"
readonly SNAPSHOT_ROOT="$(jq -r '.snapshot_root' "${SUBMITTED_CONFIG}")"
readonly SPLIT_FILE="${SNAPSHOT_ROOT}/splits/member_split_1024_v1.json"
readonly OPERATIONAL_RUN_DIR="$(jq -r '.run_directories.operational' "${SUBMITTED_CONFIG}")"
readonly ARTIFACT_DIR="${OPERATIONAL_RUN_DIR}/attempt_${OPERATIONAL_ATTEMPT}/package/artifact"
readonly ATTEMPT_DIR="${RUN_DIR}/attempt_${CYCLE}"

test -x "${PYTHON_BIN}"
test "${RUN_DIR}" = "$(jq -r '.run_directories.validation' "${SUBMITTED_CONFIG}")"
test "$(sha256sum "${SUBMITTED_CONFIG}" | cut -d' ' -f1)" = "${CONFIG_SHA256}"
test "$(sha256sum "${SUBMITTED_MANIFEST}" | cut -d' ' -f1)" = "${MANIFEST_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "${RUN_DIR}/submit_validate_iter002.slurm"
test ! -e "${ATTEMPT_DIR}"
mkdir -p "${ATTEMPT_DIR}/members"
jq -r '.development_member_ids_ranked[655]' "${SPLIT_FILE}" > "${ATTEMPT_DIR}/members/single.txt"
jq -r '.development_member_ids_ranked[655:662][]' "${SPLIT_FILE}" > "${ATTEMPT_DIR}/members/subset.txt"
jq -r '.development_member_ids_ranked[655:675][]' "${SPLIT_FILE}" > "${ATTEMPT_DIR}/members/smoke20.txt"
jq -r '.development_member_ids_ranked[655:][]' "${SPLIT_FILE}" > "${ATTEMPT_DIR}/members/operational164.txt"

cd "${REPO_ROOT}"
sha256sum -c "${SUBMITTED_MANIFEST}"
"${PYTHON_BIN}" -c 'import sys; assert sys.prefix == "/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma"'
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MPLCONFIGDIR="${RUN_DIR}/matplotlib_attempt_${CYCLE}"

for name in single subset smoke20 operational164; do
  /usr/bin/time -v "${PYTHON_BIN}" \
    "${REPO_ROOT}/predict_three_stage_spinup.py" \
    --artifact-dir "${ARTIFACT_DIR}" \
    --snapshot-root "${SNAPSHOT_ROOT}" \
    --members-file "${ATTEMPT_DIR}/members/${name}.txt" \
    --sites ABBY,JERC \
    --output "${ATTEMPT_DIR}/predict_${name}.nc"
done

/usr/bin/time -v "${PYTHON_BIN}" \
  "${REPO_ROOT}/development/three_stage_surrogate/slurm/iter002/validate_iter002.py" \
  --config "${SUBMITTED_CONFIG}" \
  --smoke-attempt "${SMOKE_ATTEMPT}" \
  --operational-attempt "${OPERATIONAL_ATTEMPT}" \
  --validation-attempt "${CYCLE}" \
  --validation-dir "${RUN_DIR}"
