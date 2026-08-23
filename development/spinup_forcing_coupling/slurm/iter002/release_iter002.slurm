#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=120G
#SBATCH --time=10:00:00
#SBATCH --job-name=sfc-i002-release
#SBATCH --output=release_%j.out
#SBATCH --error=release_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter002/release_iter002.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter002/release_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter002"
test "${STAGE}" = "release"
test "$(pwd -P)" = "${RELEASE_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test -f "${REUSE_X_MEMMAP}/X_forcing_memmap.dat"
test -f "${REUSE_X_MEMMAP}/X_forcing_memmap_layout.npz"
test "$(stat -c %s "${REUSE_X_MEMMAP}/X_forcing_memmap.dat")" = "7148160000"
test "$(sha256sum "${REUSE_X_MEMMAP}/X_forcing_memmap.dat" | awk '{print $1}')" = "${REUSE_X_MEMMAP_SHA256}"
test "$(sha256sum "${REUSE_X_MEMMAP}/X_forcing_memmap_layout.npz" | awk '{print $1}')" = "${REUSE_X_LAYOUT_SHA256}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${RELEASE_RUN_DIR}/.cache_${SLURM_JOB_ID}"
export OLMT_REPOSITORY_COMMIT="${REPOSITORY_COMMIT}"
export OLMT_SOURCE_MANIFEST_SHA256="$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
export OLMT_SUBMISSION_CONFIG_SHA256="$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
mkdir -p "$(dirname "${OUTPUT_ARTIFACT}")"
test -f "${BASELINE_AGGREGATE}"
test "$(sha256sum "${BASELINE_AGGREGATE}" | awk '{print $1}')" = "${BASELINE_AGGREGATE_SHA256}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/release_forcing_surrogate.py" \
  --case-list "${CASE_LIST}" \
  --reuse-x-memmap "${REUSE_X_MEMMAP}" \
  --baseline-aggregate "${BASELINE_AGGREGATE}" \
  --output-artifact "${OUTPUT_ARTIFACT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --submission-config "${SUBMISSION_CONFIG}" \
  --importance-outdir "${IMPORTANCE_OUTDIR}" \
  --n-jobs "${N_JOBS}" \
  --memmap-sha256 "${REUSE_X_MEMMAP_SHA256}" \
  --layout-sha256 "${REUSE_X_LAYOUT_SHA256}" \
  --schema-sha256 "${SCHEMA_SHA256}"
