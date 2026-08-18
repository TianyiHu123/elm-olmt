#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i014-production
#SBATCH --output=production_%j.out
#SBATCH --error=production_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter014/production_iter014.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = iter014
test "${STAGE}" = production
[[ "${POOL_RULE}" == "rank_dominated" || "${POOL_RULE}" == "hybrid_high_l_maximin" ]]
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
test -f "${POOL_PATH}"
module load "${MICROMAMBA_MODULE}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
export ITERATION_ID REPOSITORY_COMMIT SOURCE_MANIFEST DEPENDENCY_MANIFEST SITE_NAME CASE_NAME="${CASES}" \
  N_WALKERS=64 N_STEPS=8000 N_PROCESSES=16 SEED
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
  --de-move-scale 0.75 \
  --likelihood-resolution "${LIKELIHOOD_RESOLUTION}" \
  --candidate-pool "${POOL_PATH}" \
  --backend "${PRODUCTION_DIR}/backend.h5" \
  --checkpoint-interval 8000 \
  --workdir "${REPO_ROOT}" \
  --outputdir "${PRODUCTION_DIR}" \
  --flat-output \
  --write-diagnostics \
  --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --expected-physical-parameter-count 14
echo "PRODUCTION_SLURM_PASS pool_rule=${POOL_RULE} seed=${SEED}"
