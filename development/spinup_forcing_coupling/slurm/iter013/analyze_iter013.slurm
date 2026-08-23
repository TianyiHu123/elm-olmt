#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --job-name=sfc-i013-analyze
#SBATCH --output=analyze_%j.out
#SBATCH --error=analyze_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter013/analyze_iter013.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = iter013
test "${STAGE}" = analysis
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter013/analyze_iter013.py" \
  --site "${SITE}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --output-dir "${ANALYSIS_OUTPUT}" \
  --abby-pool "${ABBY_POOL}" \
  --abby-ledger "${ABBY_LEDGER}" \
  --abby-tim-pool "${ABBY_TIM_POOL}" \
  --abby-selection-9009 "${ABBY_SELECTION_9009}" \
  --abby-selection-9010 "${ABBY_SELECTION_9010}" \
  --abby-selection-9011 "${ABBY_SELECTION_9011}" \
  --abby-tim-bundle-9009 "${ABBY_TIM_BUNDLE_9009}" \
  --abby-tim-bundle-9010 "${ABBY_TIM_BUNDLE_9010}" \
  --abby-tim-bundle-9011 "${ABBY_TIM_BUNDLE_9011}" \
  --jerc-pool "${JERC_POOL}" \
  --jerc-ledger "${JERC_LEDGER}" \
  --jerc-tim-pool "${JERC_TIM_POOL}" \
  --jerc-selection-9009 "${JERC_SELECTION_9009}" \
  --jerc-selection-9010 "${JERC_SELECTION_9010}" \
  --jerc-selection-9011 "${JERC_SELECTION_9011}" \
  --jerc-tim-bundle-9009 "${JERC_TIM_BUNDLE_9009}" \
  --jerc-tim-bundle-9010 "${JERC_TIM_BUNDLE_9010}" \
  --jerc-tim-bundle-9011 "${JERC_TIM_BUNDLE_9011}"
