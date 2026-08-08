#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=12:00:00
#SBATCH --job-name=sfc-i007-campaign
#SBATCH --output=campaign_%j.out
#SBATCH --error=campaign_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter007/campaign_iter007.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter007/campaign_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter007"
test "${STAGE}" = "campaign"
test "$(pwd -P)" = "${CAMPAIGN_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
(cd / && sha256sum -c "${ARTIFACT_HASH_MANIFEST}")
(cd "${REPO_ROOT}" && sha256sum -c "${CASE_HASH_MANIFEST}")

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"

# Avoid BLAS/OpenMP oversubscription inside the job allocation.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  --workdir "${REPO_ROOT}" \
  --outputdir "${CAMPAIGN_RUN_DIR}" \
  --flat-output \
  --write-diagnostics \
  --case "${CASE_LIST}" \
  --artifact "${FORCING_ARTIFACT}" \
  --vars "${VARS}" \
  --obs "${OBS_SPEC}" \
  --obs-err-vars "${OBS_ERR_VARS}" \
  --spinup-mode "${SPINUP_MODE}" \
  --coupled-spinup-variant "${COUPLED_VARIANT}" \
  --nwalkers "${NWALKERS}" \
  --nsteps "${NSTEPS}" \
  --n-processes "${N_PROCESSES}" \
  --fit-error

test -f "${CAMPAIGN_RUN_DIR}/best_params.txt"
test -f "${CAMPAIGN_RUN_DIR}/clm_params_best.nc"
test -d "${CAMPAIGN_RUN_DIR}/plots/pdfs"
test -d "${CAMPAIGN_RUN_DIR}/plots/corner"
test -d "${CAMPAIGN_RUN_DIR}/plots/predictions/ABBY"
test -d "${CAMPAIGN_RUN_DIR}/plots/predictions/JERC"
test -f "${CAMPAIGN_RUN_DIR}/diagnostics/diagnostics_index.json"
echo "CAMPAIGN_PASS"
