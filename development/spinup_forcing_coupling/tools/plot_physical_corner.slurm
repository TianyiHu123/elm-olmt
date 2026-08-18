#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=20G
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-phys-corner
#SBATCH --output=physical_corner_%j.out
#SBATCH --error=physical_corner_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_physical_corner.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${STAGE}" = physical_corner
test -f "${CORNER_SPEC}"
module load "${MICROMAMBA_MODULE}"
if [[ -n "${DIAGNOSTICS_SPEC:-}" ]]; then
  test -f "${DIAGNOSTICS_SPEC}"
  test -f "${FORCING_ARTIFACT}"
  test -f "${SPINUP_ARTIFACT}"
  micromamba run -n "${MICROMAMBA_ENV}" python \
    "${REPO_ROOT}/development/spinup_forcing_coupling/tools/fixed_length_mcmc_diagnostics.py" \
    --spec "${DIAGNOSTICS_SPEC}" \
    --forcing-artifact "${FORCING_ARTIFACT}" \
    --spinup-artifact "${SPINUP_ARTIFACT}" \
    --output-dir "${OUTPUT_DIR}" \
    --overwrite
fi
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_physical_corner.py" \
  --spec "${CORNER_SPEC}" \
  --output-dir "${OUTPUT_DIR}" \
  --overwrite
echo "PHYSICAL_CORNER_SLURM_PASS output=${OUTPUT_DIR}"
