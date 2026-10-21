#!/bin/bash -e
#
# 20-minute 1024-member packing test using the successful AD srun line
# (2 nodes, 512 concurrent, 1 CPU/member, no --mem/--cpu-bind).
# PIO warnings stay filtered. Uses the existing ABBY I1850 final pickle.

#SBATCH --time=00:20:00
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --account=m4803
#SBATCH -J ABBY_adpack20
#SBATCH --nodes=2
#SBATCH --ntasks=512
#SBATCH --output=/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/ABBY/slurm_error_%j.out
#SBATCH --error=/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/ABBY/slurm_error_%j.err

cd /global/homes/t/tianyihu/E3SM_Hu/case_run/SOIL_project/NEON_ppe_vertc/ABBY/ABBY_ppe_vertc_I1850CNPRDCTCBC
export LD_LIBRARY_PATH=/opt/intel/oneapi/mkl/2025.3/lib:/opt/intel/oneapi/compiler/2025.3/opt/compiler/lib:/opt/intel/oneapi/compiler/2025.3/lib:/opt/cray/libfabric/2.3.1/lib64

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1

./preview_namelists

ulimit -n 2048
cd /pscratch/sd/t/tianyihu/elm-olmt
source /global/common/software/nersc/pe/conda/26.1.0/Miniforge3-25.11.0-1/etc/profile.d/conda.sh
conda activate OLMT_pm_TianyiPY311
./manage_ensemble.py --case ABBY_ppe_vertc_I1850CNPRDCTCBC
