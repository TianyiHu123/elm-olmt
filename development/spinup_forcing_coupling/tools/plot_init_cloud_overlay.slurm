#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=20G
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-init-cloud
#SBATCH --output=init_cloud_overlay_%j.out
#SBATCH --error=init_cloud_overlay_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_init_cloud_overlay.slurm"
test -n "${SUBMISSION_CONFIG:-}"
test -f "${SUBMISSION_CONFIG}"
test -n "${SUBMISSION_CONFIG_SHA256:-}"
test "$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}')" = "${SUBMISSION_CONFIG_SHA256}"
cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a
# shellcheck disable=SC1090
source "${SUBMISSION_CONFIG}"
set +a
test "${STAGE}" = init_cloud_overlay
test -f "${CLOUD_SPEC}"
test -f "${FORCING_ARTIFACT}"
test -f "${SPINUP_ARTIFACT}"
module load "${MICROMAMBA_MODULE}"
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/tools/plot_init_cloud_overlay.py" \
  --spec "${CLOUD_SPEC}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --output-dir "${OUTPUT_DIR}" \
  --overwrite
echo "INIT_CLOUD_OVERLAY_SLURM_PASS output=${OUTPUT_DIR}"
