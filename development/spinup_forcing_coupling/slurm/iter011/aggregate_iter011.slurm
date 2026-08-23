#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=20G
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i011-aggregate
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011/aggregate_iter011.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter011; test "${STAGE}" = aggregate
test "$(pwd -P)" = "$(dirname "${SUBMISSION_CONFIG}")"
cmp -s "${SUBMISSION_CONFIG}" "$(dirname "${SUBMISSION_CONFIG}")/canonical_submission_config.env"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
for parent in ${CAMPAIGN_PARENTS}; do
  test -f "${parent}/submission_config.env"; test -f "${parent}/matrix.tsv"
  for leaf in "${parent}"/leaf_*; do test -f "${leaf}/raw_chain.npz"; test -f "${leaf}/checkpoint_manifest.json"; done
  test "$(grep -l '^CAMPAIGN_PASS ' "${parent}"/campaign_*.out | wc -l)" -eq 6
done
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
micromamba run -n "${MICROMAMBA_ENV}" python "${VALIDATOR}" --repo "${REPO_ROOT}" --root "${OUTPUT_ROOT}" --output "${AGGREGATE_OUTPUT}" --summary "${SUMMARY_ROOT}"
echo AGGREGATE_PASS
