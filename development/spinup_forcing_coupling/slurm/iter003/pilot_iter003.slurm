#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=60G
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i003-pilot
#SBATCH --output=pilot_%j.out
#SBATCH --error=pilot_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/pilot_iter003.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/pilot_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter003"
test "${STAGE}" = "pilot"
test "$(pwd -P)" = "${PILOT_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${PILOT_RUN_DIR}/.cache_${SLURM_JOB_ID}"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/evaluate_coupled_surrogate.py" \
  --workdir "${WORKDIR}" \
  --cases "${CASE_NAME}" \
  --members "${MEMBERS}" \
  --spinup-drop32 "${SPINUP_DROP32}" \
  --spinup-drop21 "${SPINUP_DROP21}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --output-dir "${PILOT_RUN_DIR}/results" \
  --save-timeseries \
  --stage-label pilot
echo "PILOT_PASS"
