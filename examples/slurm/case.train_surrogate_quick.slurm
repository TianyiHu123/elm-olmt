#!/bin/bash -e
#
# Perlmutter shared QOS: allocated logical CPUs depend on max(--mem, ntasks*cpus-per-task)
# vs MemoryPerCpu (see NERSC "Example Jobs" > Shared). After a successful run, check
# `seff` peak RSS and consider lowering --mem with margin to avoid idle reserved cores.
#
#SBATCH --time=01:00:00
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --account=m4803
#SBATCH -J ABBY_surrogate_forcing
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=40GB
#SBATCH --output=surr_%j.out
#SBATCH --error=surr_%j.err

scontrol show job $SLURM_JOB_ID

cd /global/u1/t/tianyihu/elm-olmt
conda activate OLMT_pm_Tianyi

# Avoid BLAS/OpenMP oversubscription inside each joblib GridSearchCV worker (hurts CPU efficiency).
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

# Match GridSearchCV parallelism to Slurm's CPU set (shared QOS may exceed --cpus-per-task).
N_JOBS="${SLURM_CPUS_ON_NODE:-${SLURM_CPUS_PER_TASK:-1}}"

python train_surrogate_forcing.py \
  --case ABBY_ppe1_I20TRCNPRDCTCBC,JERC_ppe1_I20TRCNPRDCTCBC,OSBS_ppe1_I20TRCNPRDCTCBC,YELL_ppe1_I20TRCNPRDCTCBC \
  --vars SR \
  --outputdir /pscratch/sd/t/tianyihu/E3SM_out/SOIL_project \
  --run-name multisite_test1 \
  --split-mode by_time_block \
  --train-fraction 0.7 \
  --quick-grid \
  --cv-folds 3 \
  --n-jobs "${N_JOBS}" \
  --dtype float32
