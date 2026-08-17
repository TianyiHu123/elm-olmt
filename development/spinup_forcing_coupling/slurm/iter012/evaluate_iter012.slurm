#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i012-evaluate
#SBATCH --output=evaluate_%j.out
#SBATCH --error=evaluate_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter012; test "${STAGE}" = evaluation
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
extra_args=()
if [[ "${ALLOW_MOVE_MISMATCH}" = "true" ]]; then
  extra_args+=(--allow-move-mismatch)
fi
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter012/evaluate_iter012.py" \
  --site "${SITE_NAME}" \
  --resolution "${LIKELIHOOD_RESOLUTION}" \
  --cases "${CASES}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --production-root "${PRODUCTION_ROOT}" \
  --pool "${POOL_PATH}" \
  --repository-commit "${PRODUCTION_REPOSITORY_COMMIT}" \
  --source-manifest "${PRODUCTION_SOURCE_MANIFEST}" \
  --dependency-manifest "${PRODUCTION_DEPENDENCY_MANIFEST}" \
  --output "${EVALUATION_DIR}" \
  --evidence-role "${EVIDENCE_ROLE}" \
  --required-move-configuration de_mixture \
  --target-schema "${TARGET_SCHEMA}" \
  --daily-map-schema "${DAILY_MAP_SCHEMA}" \
  "${extra_args[@]}"
