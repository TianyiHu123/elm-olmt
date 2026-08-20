#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=sfc-i016-replot
#SBATCH --output=replot_sr_overlay_%j.out
#SBATCH --error=replot_sr_overlay_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
test -n "${OUTPUT_ROOT:-}"
test -n "${FORCING_ARTIFACT:-}"
test -n "${SPINUP_ARTIFACT:-}"
test -n "${SUMMARY_DIR:-}"
test -n "${MICROMAMBA_MODULE:-}"
test -n "${MICROMAMBA_ENV:-}"
module load "${MICROMAMBA_MODULE}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
micromamba run -n "${MICROMAMBA_ENV}" python \
  "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter016/replot_sr_overlay_iter016.py" \
  --root "${OUTPUT_ROOT}" \
  --forcing-artifact "${FORCING_ARTIFACT}" \
  --spinup-artifact "${SPINUP_ARTIFACT}" \
  --analysis-output "${OUTPUT_ROOT}/analysis" \
  --summary-dir "${SUMMARY_DIR}"
echo "REPLOT_SR_OVERLAY_SLURM_PASS"
