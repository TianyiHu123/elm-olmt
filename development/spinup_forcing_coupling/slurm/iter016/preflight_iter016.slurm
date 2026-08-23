#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i016-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016/preflight_iter016.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = iter016
test "${STAGE}" = preflight
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016/preflight_iter016.py" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --abby-observation "${ABBY_OBSERVATION}" \
  --jerc-observation "${JERC_OBSERVATION}" \
  --abby-ledger "${ABBY_LEDGER}" \
  --jerc-ledger "${JERC_LEDGER}" \
  --abby-pool-reference "${ABBY_POOL_REFERENCE}" \
  --jerc-pool-reference "${JERC_POOL_REFERENCE}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --output "${PREFLIGHT_OUTPUT}"
test -f "${PREFLIGHT_OUTPUT}"
echo "PREFLIGHT_SLURM_PASS"
