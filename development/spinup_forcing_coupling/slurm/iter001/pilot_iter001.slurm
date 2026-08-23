#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=150G
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i001-pilot
#SBATCH --output=pilot_%j.out
#SBATCH --error=pilot_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/pilot_iter001.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/pilot_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter001"
test "${STAGE}" = "pilot"
test "$(pwd -P)" = "${PILOT_RUN_DIR}"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/iterations/iter001.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/handoff/CURRENT.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${REPO_ROOT}/train_surrogate_forcing.py"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_iter001_pilot.py"
test -f "${SOURCE_MANIFEST}"
test -f "${DEPENDENCY_MANIFEST}"
test "$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')" = "${DEPENDENCY_MANIFEST_SHA256}"
test -f "${REUSE_X_MEMMAP}/X_forcing_memmap.dat"
test -f "${REUSE_X_MEMMAP}/X_forcing_memmap_layout.npz"
test "$(stat -c %s "${REUSE_X_MEMMAP}/X_forcing_memmap.dat")" = "7148160000"
test "$(stat -c %s "${REUSE_X_MEMMAP}/X_forcing_memmap_layout.npz")" = "73374948"
test "$(sha256sum "${REUSE_X_MEMMAP}/X_forcing_memmap.dat" | awk '{print $1}')" = "${REUSE_X_MEMMAP_SHA256}"
test "$(sha256sum "${REUSE_X_MEMMAP}/X_forcing_memmap_layout.npz" | awk '{print $1}')" = "${REUSE_X_LAYOUT_SHA256}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${PILOT_RUN_DIR}/.cache_${SLURM_JOB_ID}"
export OLMT_REPOSITORY_COMMIT="${REPOSITORY_COMMIT}"
export OLMT_SOURCE_MANIFEST_SHA256="$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
export OLMT_DEPENDENCY_MANIFEST_SHA256="${DEPENDENCY_MANIFEST_SHA256}"
export OLMT_SUBMISSION_CONFIG_SHA256="$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/train_surrogate_forcing.py" \
  --workdir "${REPO_ROOT}" \
  --reuse-x-memmap "${REUSE_X_MEMMAP}" \
  --case "${CASE_LIST}" \
  --vars "${TARGET}" \
  --forcing-vars PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF \
  --spinup-vars TOTSOMC,TOTSOMN \
  --split-mode "${SPLIT_MODE}" \
  --train-fraction "${TRAIN_FRACTION}" \
  --split-random-state "${RANDOM_SEED}" \
  --quick-grid \
  --cv-folds "${CV_FOLDS}" \
  --n-jobs "${N_JOBS}" \
  --permutation-repeats "${PERMUTATION_REPEATS}" \
  --dtype float32 \
  --stats-run-id pilot_seed10001 \
  --outputdir "${OUTPUT_ROOT}" \
  --run-name "${RUN_NAME}"

micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_iter001_pilot.py" \
  --pilot-dir "${PILOT_RUN_DIR}/surrogate_forcing" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --pilot-config "${SUBMISSION_CONFIG}"
