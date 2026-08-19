#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i015-rebuild
#SBATCH --output=rebuild_%j.out
#SBATCH --error=rebuild_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter015/rebuild_pool_iter015.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = iter015
test "${STAGE}" = pool_rebuild
test "${POOL_RULE}" = hybrid_high_l_maximin
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
test "$(sha256sum "${LEDGER_PATH}" | awk '{print $1}')" = "${EXPECTED_LEDGER_SHA256}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/initialize_pipeline.py" \
  --rebuild-from-ledger "${LEDGER_PATH}" \
  --expected-ledger-sha256 "${EXPECTED_LEDGER_SHA256}" \
  --pool-rule "${POOL_RULE}" \
  --high-l-quantile "${HIGH_L_QUANTILE}" \
  --site "${SITE_NAME}" \
  --resolution "${LEDGER_RESOLUTION}" \
  --cases "${CASES}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --observation "${SITE_NAME}=${OBSERVATION_PATH}" \
  --repository-commit "${REPOSITORY_COMMIT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --output "${REBUILD_OUTPUT}" \
  --seed 0 \
  --expected-physical-parameter-count 14
test -f "${REBUILD_OUTPUT}/artifacts/candidate_pool.npz"
test -f "${REBUILD_OUTPUT}/artifacts/search_contract.json"
if [[ -n "${EXPECTED_POOL_SHA256:-}" ]]; then
  test "$(sha256sum "${REBUILD_OUTPUT}/artifacts/candidate_pool.npz" | awk '{print $1}')" = "${EXPECTED_POOL_SHA256}"
fi
echo "REBUILD_SLURM_PASS site=${SITE_NAME} pool_rule=${POOL_RULE}"
