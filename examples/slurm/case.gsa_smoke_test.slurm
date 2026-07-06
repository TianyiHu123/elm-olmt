#!/bin/bash -e
#
# Run lightweight aggregated-metric GSA smoke test on Perlmutter.
# Default smoke script location: ~/gsa_smoke_test.py
#
#SBATCH --time=01:00:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J gsa_smoke
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8GB
#SBATCH --output=gsa_smoke_%j.out
#SBATCH --error=gsa_smoke_%j.err

scontrol show job "$SLURM_JOB_ID"

# --- User settings ---
OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
SMOKE_SCRIPT="/pscratch/sd/t/tianyihu/elm-olmt/gsa_smoke_test.py"

# Optional handoff for script-level parallel settings.
# The smoke script prints per-metric checks (mean/accumulated/std or user-selected subset).
export SLURM_GSA_NJOBS="${SLURM_CPUS_PER_TASK:-1}"

# Avoid BLAS/OpenMP oversubscription.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

if [ ! -f "$SMOKE_SCRIPT" ]; then
  echo "Missing smoke script: $SMOKE_SCRIPT"
  echo "Create it first, then resubmit."
  exit 2
fi

cd "$OLMT_ROOT"
conda activate "$CONDA_ENV"
python "$SMOKE_SCRIPT"
