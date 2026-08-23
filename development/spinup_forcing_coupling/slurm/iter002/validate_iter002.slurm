#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=01:00:00
#SBATCH --job-name=sfc-i002-validate
#SBATCH --output=validate_%j.out
#SBATCH --error=validate_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter002/validate_iter002.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter002/validate_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter002"
test "${STAGE}" = "validate"
test "$(pwd -P)" = "${VALIDATE_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test -f "${ARTIFACT}"
test -f "${IMPORTANCE_JSON}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${VALIDATE_RUN_DIR}/.cache_${SLURM_JOB_ID}"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/validate_iter002_release.py" \
  --artifact "${ARTIFACT}" \
  --reuse-x-memmap "${REUSE_X_MEMMAP}" \
  --importance-json "${IMPORTANCE_JSON}" \
  --summary-root "${SUMMARY_ROOT}"
