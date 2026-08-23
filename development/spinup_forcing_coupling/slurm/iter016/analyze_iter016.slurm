#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i016-analysis
#SBATCH --output=analysis_%j.out
#SBATCH --error=analysis_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016/analyze_iter016.slurm"
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
test "${STAGE}" = analysis
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
test "$(find "${OUTPUT_ROOT}/production" -name raw_chain.npz | wc -l)" -eq 18
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016/analyze_iter016.py" \
  --root "${OUTPUT_ROOT}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --analysis-output "${ANALYSIS_OUTPUT}" \
  --summary-dir "${SUMMARY_DIR}"
test -f "${ANALYSIS_OUTPUT}/aggregate_result.json"
test -f "${SUMMARY_DIR}/ITER016_REPORT.md"
echo "ANALYSIS_SLURM_PASS"
