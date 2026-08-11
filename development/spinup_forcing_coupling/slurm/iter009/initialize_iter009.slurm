#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=sfc-i009-initialize
#SBATCH --output=initialize_%j.out
#SBATCH --error=initialize_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/initialize_iter009.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter009; test "${STAGE}" = initialize
test "$(pwd -P)" = "${INITIALIZATION_DIR}"
cmp -s "${SUBMISSION_CONFIG}" "${INITIALIZATION_DIR}/canonical_submission_config.env"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${ITER008_RAW_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/initialize_iter009.py" --abby-raw "${ABBY_RAW}" --jerc-raw "${JERC_RAW}" --outdir "${INITIALIZATION_DIR}"
echo INITIALIZE_PASS
