#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=sfc-i001-aggregate
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/aggregate_iter001.slurm"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/aggregate_config.env"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
cmp -s "${CANONICAL_CONFIG}" "${SUBMISSION_CONFIG}"
set -a
source "${SUBMISSION_CONFIG}"
set +a
test "${ITERATION_ID}" = "iter001"
test "${STAGE}" = "aggregate"
test "$(pwd -P)" = "${AGGREGATE_RUN_DIR}"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/iterations/iter001.md"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/handoff/CURRENT.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/aggregate_iter001.py"
test -f "${SOURCE_MANIFEST}"
test -f "${DEPENDENCY_MANIFEST}"
test -f "${PRODUCTION_CONFIG}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/aggregate_iter001.py" \
  --input-dir "${BASELINE_STATS_DIR}" \
  --output-dir "${AGGREGATE_RUN_DIR}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --production-config "${PRODUCTION_CONFIG}"

micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter001/validate_iter001_aggregate.py" \
  --output-dir "${AGGREGATE_RUN_DIR}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --dependency-manifest "${DEPENDENCY_MANIFEST}" \
  --production-config "${PRODUCTION_CONFIG}"
