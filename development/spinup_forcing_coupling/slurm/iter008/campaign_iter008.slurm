#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i008-campaign
#SBATCH --output=campaign_%j.out
#SBATCH --error=campaign_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/campaign_iter008.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
readonly SUBMISSION_CONFIG_NAME="$(basename "${SUBMISSION_CONFIG}")"
case "${SUBMISSION_CONFIG_NAME}" in
  submission_config_abby.env) readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/abby_campaign_config.env" ;;
  submission_config_jerc.env) readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/jerc_campaign_config.env" ;;
  *) echo "unexpected submitted config name: ${SUBMISSION_CONFIG_NAME}" >&2; exit 2 ;;
esac
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter008"
test "${STAGE}" = "campaign"
test "${SUBMISSION_CONFIG_NAME}" = "submission_config_${SITE_NAME,,}.env"
test "$(pwd -P)" = "${CAMPAIGN_RUN_DIR}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
(cd / && sha256sum -c "${ARTIFACT_HASH_MANIFEST}")
(cd "${REPO_ROOT}" && sha256sum -c "${CASE_HASH_MANIFEST}")
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  --workdir "${REPO_ROOT}" \
  --outputdir "${CAMPAIGN_RUN_DIR}" \
  --flat-output --write-diagnostics \
  --case "${CASE_NAME}" \
  --artifact "${FORCING_ARTIFACT}" \
  --vars SR \
  --obs "${OBS_PATH}" \
  --obs-err-vars SR:SR_err \
  --spinup-mode "${SPINUP_MODE}" \
  --coupled-spinup-variant "${COUPLED_VARIANT}" \
  --nwalkers "${N_WALKERS}" --nsteps "${N_STEPS}" \
  --n-processes "${N_PROCESSES}" --seed "${SEED}" --fit-error
for required in raw_chain.npz raw_chain_metadata.json raw_chain_hashes.json selection_ledger.json diagnostic_report.md best_params.txt clm_params_best.nc diagnostics/diagnostics_index.json diagnostics/chain_health.json diagnostics/walker_acceptance.csv diagnostics/parameter_chain_health.csv; do
  test -f "${CAMPAIGN_RUN_DIR}/${required}"
done
test ! -e "${CAMPAIGN_RUN_DIR}/UQ_output"
echo "CAMPAIGN_PASS site=${SITE_NAME}"
