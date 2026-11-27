#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --job-name=mcmc_i005_preflight
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot/logs/preflight_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot/logs/preflight_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
: "${ITER005_CONFIG:?}" "${ITER005_CONFIG_SHA:?}" "${ITER005_VERIFY_SHA:?}" "${ITER005_MANIFEST_SHA:?}" "${ITER005_EXECUTION_MANIFEST_SHA:?}"
printf '%s  %s\n' "${ITER005_CONFIG_SHA}" "${ITER005_CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER005_VERIFY_SHA}" "${RUNTIME_ROOT}/submitted/verify_iter005_package.sh" | sha256sum -c -
printf '%s  %s\n' "${ITER005_MANIFEST_SHA}" "${RUNTIME_ROOT}/manifests/execution_files.sha256" | sha256sum -c -
printf '%s  %s\n' "${ITER005_EXECUTION_MANIFEST_SHA}" "${RUNTIME_ROOT}/submitted/execution_manifest.json" | sha256sum -c -
bash "${RUNTIME_ROOT}/submitted/verify_iter005_package.sh" "${ITER005_CONFIG}" preflight_iter005.slurm
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" "${RUNTIME_ROOT}/submitted/run_iter005_tests.py"
"${PYTHON}" "${RUNTIME_ROOT}/submitted/run_iter005.py" preflight --config "${ITER005_CONFIG}"
