#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --job-name=mcmc_i003_component
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior/logs/component_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior/logs/component_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior
readonly DRIVER=${RUNTIME_ROOT}/submitted/run_iter003.py
readonly VERIFY=${RUNTIME_ROOT}/submitted/verify_iter003_package.sh
: "${ITER003_CONFIG:?ITER003_CONFIG is required}"
: "${ITER003_CONFIG_SHA:?ITER003_CONFIG_SHA is required}"
: "${ITER003_VERIFY_SHA:?ITER003_VERIFY_SHA is required}"
printf '%s  %s\n' "${ITER003_CONFIG_SHA}" "${ITER003_CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER003_VERIFY_SHA}" "${VERIFY}" | sha256sum -c -
bash "${VERIFY}" "${ITER003_CONFIG}" component_iter003.slurm
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" -m unittest discover -s tests -p 'test_mcmc_three_stage_*_iter003.py' -v
"${PYTHON}" -m unittest discover -s tests -p 'test_mcmc_prior_iter001.py' -v
"${PYTHON}" -m unittest discover -s tests -p 'test_mcmc_coupled_interface_iter001.py' -v
"${PYTHON}" "${DRIVER}" --config "${ITER003_CONFIG}" --step component --output "${RUNTIME_ROOT}/results/component_validation.json"
