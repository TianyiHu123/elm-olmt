#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=sfc-i003-validate
#SBATCH --output=validate_%j.out
#SBATCH --error=validate_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/validate_iter003.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/validate_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter003"
test "${STAGE}" = "validate"
test "$(pwd -P)" = "${VALIDATE_RUN_DIR}"
test -f "${SOURCE_MANIFEST}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter003/validate_iter003.py" \
  --pilot-dir "${PILOT_RUN_DIR}" \
  --full-dir "${FULL_RUN_DIR}" \
  --summary-root "${SUMMARY_ROOT}"
