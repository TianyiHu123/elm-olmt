#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i012-aggregate
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/aggregate_iter012.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter012; test "${STAGE}" = aggregate
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/aggregate_iter012.py" \
  --canonical-abby "${CANONICAL_ABBY_EVALUATION_DIR}" \
  --canonical-jerc "${CANONICAL_JERC_EVALUATION_DIR}" \
  --legacy-abby "${LEGACY_ABBY_EVALUATION_DIR}" \
  --legacy-jerc "${LEGACY_JERC_EVALUATION_DIR}" \
  --output "${AGGREGATE_OUTPUT}"
