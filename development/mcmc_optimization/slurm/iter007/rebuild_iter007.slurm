#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=mcmc_i007_rebuild
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter007_observation_release_0002/logs/rebuild_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter007_observation_release_0002/logs/rebuild_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter007_observation_release_0002
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
readonly CONFIG=${RUNTIME_ROOT}/submitted/iter007_config.json
readonly VERIFY=${RUNTIME_ROOT}/submitted/verify_iter007_package.sh
readonly DRIVER=${RUNTIME_ROOT}/submitted/run_iter007.py
readonly INTEGRATE=${RUNTIME_ROOT}/submitted/integrate_iter007.py
printf '%s  %s\n' "${ITER007_CONFIG_SHA:?config hash required}" "${CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER007_VERIFY_SHA:?verifier hash required}" "${VERIFY}" | sha256sum -c -
bash "${VERIFY}" rebuild_iter007.slurm
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" "${DRIVER}" --config "${CONFIG}" --step rebuild
