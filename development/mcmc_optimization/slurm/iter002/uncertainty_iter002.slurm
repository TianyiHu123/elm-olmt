#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --job-name=mcmc_i002_unc
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation/logs/uncertainty_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation/logs/uncertainty_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
readonly DRIVER=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation/submitted/run_iter002.py
readonly VERIFY=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation/submitted/verify_iter002_package.sh
: "${ITER002_CONFIG:?ITER002_CONFIG is required}"
: "${ITER002_CONFIG_SHA:?ITER002_CONFIG_SHA is required}"
: "${ITER002_VERIFY_SHA:?ITER002_VERIFY_SHA is required}"
printf '%s  %s\n' "${ITER002_CONFIG_SHA}" "${ITER002_CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER002_VERIFY_SHA}" "${VERIFY}" | sha256sum -c -
bash "${VERIFY}" "${ITER002_CONFIG}" uncertainty_iter002.slurm
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" "${DRIVER}" --config "${ITER002_CONFIG}" --step uncertainty
