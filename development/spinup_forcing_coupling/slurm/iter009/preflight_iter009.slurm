#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i009-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err

set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/preflight_iter009.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter009
test "${STAGE}" = preflight
cmp -s "${SUBMISSION_CONFIG}" "${PREFLIGHT_RUN_DIR}/canonical_submission_config.env"
test "$(pwd -P)" = "${PREFLIGHT_RUN_DIR}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
test -f "${MATRIX_ROOT}/spinup_forcing_coupling_iter009_b_campaign/matrix.tsv"
for arm in b t i m tim; do
  ARM_MATRIX="${MATRIX_ROOT}/spinup_forcing_coupling_iter009_${arm}_campaign/matrix.tsv"
  test "$(awk 'END {print NR - 1}' "${ARM_MATRIX}")" = 6
  cmp <(cut -f 1-6 "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/iter009_matrix.tsv") \
    <(cut -f 1-6 "${ARM_MATRIX}")
  case "${arm}" in
    b) expected=$'B\tphysical\tuniform\tstretch' ;;
    t) expected=$'T\ttransformed\tuniform\tstretch' ;;
    i) expected=$'I\tphysical\thigh\tstretch' ;;
    m) expected=$'M\tphysical\tuniform\tde_mixture' ;;
    tim) expected=$'TIM\ttransformed\thigh\tde_mixture' ;;
  esac
  test "$(tail -n +2 "${ARM_MATRIX}" | cut -f 7-10 | sort -u)" = "${expected}"
done
test "$(for arm in b t i m tim; do tail -n +2 "${MATRIX_ROOT}/spinup_forcing_coupling_iter009_${arm}_campaign/matrix.tsv"; done | wc -l)" = 30
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
test -f "${FORCING_ARTIFACT}"
test -f "${SPINUP_ARTIFACT}"
sha256sum -c "${DEPENDENCY_MANIFEST}"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter009/preflight_iter009.py" \
  --output-root "${PREFLIGHT_SMOKE_ROOT}"
test -f "${PREFLIGHT_SMOKE_ROOT}/preflight_result.json"
echo "PREFLIGHT_PASS"
