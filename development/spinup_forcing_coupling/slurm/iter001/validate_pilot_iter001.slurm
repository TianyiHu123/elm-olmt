#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --job-name=sfc-i001-pval
#SBATCH --output=validate_pilot_%j.out
#SBATCH --error=validate_pilot_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_pilot_iter001.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_pilot_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter001"
test "${STAGE}" = "pilot_validation"
test "$(pwd -P)" = "${PILOT_RUN_DIR}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
test -f "${VALIDATION_SOURCE_MANIFEST}"
test -f "${TRAINING_SOURCE_MANIFEST}"
test "$(sha256sum "${TRAINING_SOURCE_MANIFEST}" | awk '{print $1}')" = "${TRAINING_SOURCE_MANIFEST_SHA256}"
test -f "${DEPENDENCY_MANIFEST}"
test "$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')" = "${DEPENDENCY_MANIFEST_SHA256}"
test -f "${PILOT_TRAINING_CONFIG}"
test "$(sha256sum "${PILOT_TRAINING_CONFIG}" | awk '{print $1}')" = "${PILOT_TRAINING_CONFIG_SHA256}"
test "$(sha256sum "${PILOT_ARTIFACT_DIR}/surrogate_forcing_stats_pilot_seed10001_rs10001.json" | awk '{print $1}')" = "${PILOT_STATS_SHA256}"
test "$(sha256sum "${PILOT_ARTIFACT_DIR}/surrogate_forcing_artifacts.pkl" | awk '{print $1}')" = "${PILOT_ARTIFACT_SHA256}"
test "$(sha256sum "${PILOT_ARTIFACT_DIR}/X_forcing_memmap.dat" | awk '{print $1}')" = "${PILOT_MEMMAP_SHA256}"
test "$(sha256sum "${PILOT_ARTIFACT_DIR}/X_forcing_memmap_layout.npz" | awk '{print $1}')" = "${PILOT_LAYOUT_SHA256}"
(cd "${REPO_ROOT}" && sha256sum -c "${VALIDATION_SOURCE_MANIFEST}")

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${PILOT_RUN_DIR}/.cache_validation_${SLURM_JOB_ID}"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/tests/test_surrogate_forcing_iter001.py"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_iter001_pilot.py" \
  --pilot-dir "${PILOT_ARTIFACT_DIR}" \
  --source-manifest "${TRAINING_SOURCE_MANIFEST}" \
  --validation-source-manifest "${VALIDATION_SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --pilot-config "${PILOT_TRAINING_CONFIG}"
test -s "${PILOT_RUN_DIR}/pilot_validation.json"
