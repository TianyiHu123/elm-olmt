#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=80G
#SBATCH --time=08:00:00
#SBATCH --array=1-9
#SBATCH --job-name=sfc-i003-full
#SBATCH --output=full_%A_%a.out
#SBATCH --error=full_%A_%a.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/full_iter003.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/full_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter003"
test "${STAGE}" = "full"
test "$(pwd -P)" = "${FULL_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
test -n "${SLURM_ARRAY_TASK_ID:-}"

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export XDG_CACHE_HOME="${FULL_RUN_DIR}/.cache_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
LEAF_OUT="${FULL_RUN_DIR}/results/site_${SLURM_ARRAY_TASK_ID}"
mkdir -p "${LEAF_OUT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/evaluate_coupled_surrogate.py" \
  --workdir "${WORKDIR}" \
  --cases "${CASE_LIST}" \
  --members "${MEMBERS}" \
  --spinup-drop32 "${SPINUP_DROP32}" \
  --spinup-drop21 "${SPINUP_DROP21}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --output-dir "${LEAF_OUT}" \
  --site-index "${SLURM_ARRAY_TASK_ID}" \
  --stage-label "full_site${SLURM_ARRAY_TASK_ID}"
echo "FULL_LEAF_PASS site_index=${SLURM_ARRAY_TASK_ID}"
