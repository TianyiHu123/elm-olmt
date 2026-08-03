#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --job-name=sfc-i001-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/preflight_iter001.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/preflight_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter001"
test "${STAGE}" = "preflight"
test "$(pwd -P)" = "${PILOT_RUN_DIR}"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/iterations/iter001.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/handoff/CURRENT.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/preflight_iter001.py"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${SOURCE_MANIFEST}"
test -f "${CASE_HASH_MANIFEST}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

module load "${MICROMAMBA_MODULE}"
echo "MICROMAMBA_MODULE_REQUESTED=${MICROMAMBA_MODULE}"
loaded_modules="$(module -t list 2>&1)"
printf '%s\n' "${loaded_modules}" | sed 's/^/LOADED_MODULE=/'
micromamba --version
resolved_micromamba="$(printf '%s\n' "${loaded_modules}" | sed -n '/^micromamba\//p' | head -n 1)"
test -n "${resolved_micromamba}"
if [[ "${MICROMAMBA_MODULE}" != */* ]]; then
  echo "MICROMAMBA_DISCOVERY_ONLY resolved=${resolved_micromamba}"
  exit 0
fi
test "${resolved_micromamba}" = "${MICROMAMBA_MODULE}"
(cd "${REPO_ROOT}" && sha256sum -c "${CASE_HASH_MANIFEST}")
micromamba env list
micromamba run -n "${MICROMAMBA_ENV}" python --version
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/tests/test_surrogate_forcing_iter001.py"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/preflight_iter001.py" \
  --expected-hashes "${CASE_HASH_MANIFEST}" \
  --output "${DEPENDENCY_MANIFEST}" \
  --micromamba-module "${MICROMAMBA_MODULE}" \
  --environment-yaml "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
