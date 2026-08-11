#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i009-validate
#SBATCH --output=validate_%j.out
#SBATCH --error=validate_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/validate_iter009.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter009; test "${STAGE}" = validate
test "$(pwd -P)" = "$(dirname "${SUBMISSION_CONFIG}")"
cmp -s "${SUBMISSION_CONFIG}" "$(dirname "${SUBMISSION_CONFIG}")/canonical_submission_config.env"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
test -f "${VALIDATOR}"
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
micromamba run -n "${MICROMAMBA_ENV}" python "${VALIDATOR}" --root "${OUTPUT_ROOT}" \
  --summary-root "${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter009"
echo VALIDATE_PASS
