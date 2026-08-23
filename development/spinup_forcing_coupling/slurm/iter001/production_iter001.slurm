#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=150G
#SBATCH --time=06:00:00
#SBATCH --array=1-100%10
#SBATCH --job-name=sfc-i001-production
#SBATCH --output=production_%A_%a.out
#SBATCH --error=production_%A_%a.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/production_iter001.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/production_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter001"
test "${STAGE}" = "production"
test "$(pwd -P)" = "${BASELINE_RUN_DIR}"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/iterations/iter001.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/handoff/CURRENT.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${REPO_ROOT}/train_surrogate_forcing.py"
test -f "${SOURCE_MANIFEST}"
test -f "${DEPENDENCY_MANIFEST}"
test -f "${PILOT_RUN_DIR}/pilot_validation.json"
test -f "${PILOT_RUN_DIR}/surrogate_forcing/X_forcing_memmap.dat"
test -f "${PILOT_RUN_DIR}/surrogate_forcing/X_forcing_memmap_layout.npz"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

readonly RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${BASELINE_RUN_DIR}/.cache_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
export OLMT_REPOSITORY_COMMIT="${REPOSITORY_COMMIT}"
export OLMT_SOURCE_MANIFEST_SHA256="$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}')"
export OLMT_DEPENDENCY_MANIFEST_SHA256="$(sha256sum "${DEPENDENCY_MANIFEST}" | awk '{print $1}')"
export OLMT_SUBMISSION_CONFIG_SHA256="$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/train_surrogate_forcing.py" \
  --workdir "${REPO_ROOT}" \
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
  --stats-only \
  --stats-run-id "seed${RANDOM_SEED}" \
  --reuse-x-memmap "${PILOT_RUN_DIR}/surrogate_forcing" \
  --outputdir "${OUTPUT_ROOT}" \
  --run-name "${RUN_NAME}"
