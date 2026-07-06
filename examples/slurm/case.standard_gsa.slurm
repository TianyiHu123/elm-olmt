#!/bin/bash -e
#
# Run standard GSA CLI on Perlmutter.
#
#SBATCH --time=02:00:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J standard_gsa
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24GB
#SBATCH --output=standard_gsa_%j.out
#SBATCH --error=standard_gsa_%j.err

scontrol show job "$SLURM_JOB_ID"

# --- User settings ---
OLMT_ROOT="/pscratch/sd/t/tianyihu/elm-olmt"
CONDA_ENV="OLMT_pm_Tianyi"
CASE_NAME="JERC_ppe1_I20TRCNPRDCTCBC"
GSA_MODE="both"  # existing (PAWN) | surrogate (Sobol) | both
GSA_VARS="SR"
GSA_METRICS="mean,accumulated,std"
SURROGATE_ARTIFACT="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/multisite_test1/surrogate_forcing"
GSA_OUTPUT_DIR="/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/GSA/standard"
SALTELLI_N=1024
SPINUP_VARS="TOTSOMC,TOTSOMN"
SEED=42
FORCING_EXECUTOR="thread"   # thread | process | serial
SOBOL_EXECUTOR="thread"     # thread | process | serial (process falls back to thread in analysis helpers)
PAWN_EXECUTOR="thread"      # thread | process | serial (process falls back to thread in analysis helpers)
PAWN_VAR_EXECUTOR="serial"  # serial | thread | process (process falls back to thread)
FORCING_CHUNK_SIZE=128      # tune upward for throughput, downward for memory spikes

# Match joblib/SALib parallelism to Slurm allocation.
N_JOBS="${SLURM_CPUS_ON_NODE:-${SLURM_CPUS_PER_TASK:-1}}"

# Avoid BLAS/OpenMP oversubscription.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

cd "$OLMT_ROOT"
conda activate "$CONDA_ENV"

CMD=(
  python run_standard_gsa.py
  --workdir "$OLMT_ROOT"
  --case "$CASE_NAME"
  --vars "$GSA_VARS"
  --metrics "$GSA_METRICS"
  --mode "$GSA_MODE"
  --spinup-vars "$SPINUP_VARS"
  --saltelli-n "$SALTELLI_N"
  --seed "$SEED"
  --n-jobs "$N_JOBS"
  --forcing-executor "$FORCING_EXECUTOR"
  --sobol-executor "$SOBOL_EXECUTOR"
  --pawn-executor "$PAWN_EXECUTOR"
  --pawn-var-executor "$PAWN_VAR_EXECUTOR"
  --forcing-chunk-size "$FORCING_CHUNK_SIZE"
  --output-folder "$GSA_OUTPUT_DIR"
)

if [ "$GSA_MODE" = "surrogate" ] || [ "$GSA_MODE" = "both" ]; then
  CMD+=(--artifact "$SURROGATE_ARTIFACT")
fi

echo "Running standard GSA:"
printf ' %q' "${CMD[@]}"
echo
"${CMD[@]}"

# Memory guidance:
# - If job nears OOM, lower SALTELLI_N and/or FORCING_CHUNK_SIZE.
# - If CPU utilization is low, increase --cpus-per-task and keep N_JOBS aligned.
