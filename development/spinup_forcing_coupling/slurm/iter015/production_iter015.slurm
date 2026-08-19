#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i015-production
#SBATCH --output=production_%j.out
#SBATCH --error=production_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter015/production_iter015.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = iter015
test "${STAGE}" = production
test "${POOL_RULE}" = hybrid_high_l_maximin
test "${POOL_REUSE_POLICY}" = site_hybrid_pool_reuse_v1
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
test -f "${POOL_PATH}"
module load "${MICROMAMBA_MODULE}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export ITERATION_ID
export REPOSITORY_COMMIT
export SOURCE_MANIFEST
export DEPENDENCY_MANIFEST
export SITE_NAME
export CASE_NAME="${CASES}"
export N_WALKERS=64
export N_STEPS=8000
export N_PROCESSES=16
export SEED
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  --case "${CASES}" \
  --artifact "${FORCING_ARTIFACT}" \
  --vars SR \
  --obs "${SITE_NAME}:${OBSERVATION_PATH}" \
  --obs-err-vars SR:SR_err \
  --spinup-mode coupled \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --nwalkers 64 \
  --nsteps 8000 \
  --n-processes 16 \
  --seed "${SEED}" \
  --sampler-coordinates transformed \
  --move-configuration de_mixture \
  --de-move-scale "${DE_MOVE_SCALE}" \
  --likelihood-resolution "${LIKELIHOOD_RESOLUTION}" \
  --candidate-pool "${POOL_PATH}" \
  --pool-reuse-policy "${POOL_REUSE_POLICY}" \
  --backend "${PRODUCTION_DIR}/backend.h5" \
  --checkpoint-interval 2000 \
  --workdir "${REPO_ROOT}" \
  --outputdir "${PRODUCTION_DIR}" \
  --flat-output \
  --write-diagnostics \
  --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --expected-physical-parameter-count 14
test -f "${PRODUCTION_DIR}/raw_chain.npz"
test -f "${PRODUCTION_DIR}/selection_ledger.json"
test "${LIKELIHOOD_RESOLUTION}" != daily || test -f "${PRODUCTION_DIR}/daily_index_maps.json"
echo "CAMPAIGN_PASS site=${SITE_NAME} resolution=${LIKELIHOOD_RESOLUTION} de_scale=${DE_MOVE_SCALE} seed=${SEED}"
