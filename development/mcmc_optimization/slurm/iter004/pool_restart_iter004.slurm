#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --job-name=mcmc_i004_pool_restart
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot/logs/pool_restart_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot/logs/pool_restart_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
: "${ITER004_CONFIG:?}" "${ITER004_CONFIG_SHA:?}" "${ITER004_VERIFY_SHA:?}" "${ITER004_MANIFEST_SHA:?}" "${ITER004_EXECUTION_MANIFEST_SHA:?}"
printf '%s  %s\n' "${ITER004_CONFIG_SHA}" "${ITER004_CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER004_VERIFY_SHA}" "${RUNTIME_ROOT}/submitted/verify_iter004_package.sh" | sha256sum -c -
printf '%s  %s\n' "${ITER004_MANIFEST_SHA}" "${RUNTIME_ROOT}/manifests/execution_files.sha256" | sha256sum -c -
printf '%s  %s\n' "${ITER004_EXECUTION_MANIFEST_SHA}" "${RUNTIME_ROOT}/submitted/execution_manifest.json" | sha256sum -c -
bash "${RUNTIME_ROOT}/submitted/verify_iter004_package.sh" "${ITER004_CONFIG}" pool_restart_iter004.slurm
[[ -f "${RUNTIME_ROOT}/sites/ABBY/candidates/search_report.json" && -f "${RUNTIME_ROOT}/sites/JERC/candidates/search_report.json" ]] || { echo "search gates missing" >&2; exit 2; }
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" "${RUNTIME_ROOT}/submitted/run_iter004_tests.py"
"${PYTHON}" "${RUNTIME_ROOT}/submitted/run_iter004.py" pool-restart --config "${ITER004_CONFIG}"
