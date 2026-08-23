#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i011-campaign
#SBATCH --output=campaign_%A_%a.out
#SBATCH --error=campaign_%A_%a.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011/campaign_iter011.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter011; test "${STAGE}" = campaign
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
readonly ROW="$(awk -F '\t' -v task="${SLURM_ARRAY_TASK_ID}" 'NR > 1 && $1 == task { print; exit }' "${MATRIX_MANIFEST}")"
test -n "${ROW}"
IFS=$'\t' read -r array_index leaf_id site seed resolution de_scale initialization <<< "${ROW}"
test "${array_index}" = "${SLURM_ARRAY_TASK_ID}"
test "${resolution}" = "${LIKELIHOOD_RESOLUTION}"; test "${de_scale}" = "${DE_MOVE_SCALE}"
readonly CAMPAIGN_RUN_DIR="${CAMPAIGN_PARENT_DIR}/${leaf_id}"
test -d "${CAMPAIGN_RUN_DIR}"; cd "${CAMPAIGN_RUN_DIR}"
readonly CASE_NAME="${site}_ppe6_I20TRCNPRDCTCBC"
readonly OBS_PATH="/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/${site}/${site}_cdo_merge.nc"
readonly INITIAL_STATE="${INITIALIZATION_DIR}/${site,,}_${initialization}_seed${seed}.npz"
readonly BACKEND="${CAMPAIGN_RUN_DIR}/backend.h5"
test -f "${INITIAL_STATE}"
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
export ITERATION_ID=iter011 SITE_NAME="${site}" CASE_NAME OBS_PATH FORCING_ARTIFACT SPINUP_ARTIFACT
export SPINUP_MODE=coupled COUPLED_VARIANT=drop21_corr080 N_WALKERS=64 N_STEPS=8000 N_PROCESSES=16
export SEED="${seed}" ARTIFACT_HASH_MANIFEST="${DEPENDENCY_MANIFEST}"
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  --workdir "${REPO_ROOT}" --outputdir "${CAMPAIGN_RUN_DIR}" --flat-output --write-diagnostics \
  --case "${CASE_NAME}" --artifact "${FORCING_ARTIFACT}" --vars SR --obs "${OBS_PATH}" \
  --obs-err-vars SR:SR_err --spinup-mode coupled --coupled-spinup-variant drop21_corr080 \
  --nwalkers 64 --nsteps 8000 --n-processes 16 --seed "${seed}" --fit-error \
  --sampler-coordinates transformed --move-configuration de_mixture --de-move-scale "${de_scale}" \
  --likelihood-resolution "${resolution}" --initial-state "${INITIAL_STATE}" --backend "${BACKEND}" \
  --checkpoint-interval 2000
test -f "${CAMPAIGN_RUN_DIR}/raw_chain.npz"; test -f "${CAMPAIGN_RUN_DIR}/checkpoint_manifest.json"
test "${resolution}" != daily || test -f "${CAMPAIGN_RUN_DIR}/daily_index_maps.json"
echo "CAMPAIGN_PASS leaf=${leaf_id} resolution=${resolution} de_scale=${de_scale}"
