#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i008-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/preflight_iter008.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/preflight_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter008"
test "${STAGE}" = "preflight"
test "$(pwd -P)" = "${PREFLIGHT_RUN_DIR}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
module load "${MICROMAMBA_MODULE}"
test "$(micromamba run -n "${MICROMAMBA_ENV}" python --version >/dev/null; echo $?)" = 0
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter008/preflight_iter008.py" \
  --artifact-hashes "${ARTIFACT_HASH_MANIFEST}" \
  --case-hashes "${CASE_HASH_MANIFEST}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --preflight-run-dir "${PREFLIGHT_RUN_DIR}" \
  --python "${PYTHON_EXECUTABLE}"
echo "PREFLIGHT_PASS"
