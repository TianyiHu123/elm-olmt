#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=mcmc_i004_diag
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot/logs/diagnostics_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot/logs/diagnostics_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
: "${ITER004_CONFIG:?}" "${ITER004_CONFIG_SHA:?}" "${ITER004_VERIFY_SHA:?}" "${ITER004_MANIFEST_SHA:?}" "${ITER004_EXECUTION_MANIFEST_SHA:?}"
printf '%s  %s\n' "${ITER004_CONFIG_SHA}" "${ITER004_CONFIG}" | sha256sum -c -
printf '%s  %s\n' "${ITER004_VERIFY_SHA}" "${RUNTIME_ROOT}/submitted/verify_iter004_package.sh" | sha256sum -c -
printf '%s  %s\n' "${ITER004_MANIFEST_SHA}" "${RUNTIME_ROOT}/manifests/execution_files.sha256" | sha256sum -c -
printf '%s  %s\n' "${ITER004_EXECUTION_MANIFEST_SHA}" "${RUNTIME_ROOT}/submitted/execution_manifest.json" | sha256sum -c -
bash "${RUNTIME_ROOT}/submitted/verify_iter004_package.sh" "${ITER004_CONFIG}" diagnostics_iter004.slurm
for site in ABBY JERC; do
  success=0
  failure=0
  [[ -f "${RUNTIME_ROOT}/sites/${site}/pilot_report.json" ]] && success=1
  [[ -f "${RUNTIME_ROOT}/sites/${site}/pilot_validation_failure.json" ]] && failure=1
  [[ $((success + failure)) -eq 1 ]] || {
    echo "${site} pilot terminal evidence missing" >&2
    exit 2
  }
done
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 MPLBACKEND=Agg PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${REPO_ROOT}"
"${PYTHON}" "${RUNTIME_ROOT}/submitted/run_iter004.py" diagnostics --config "${ITER004_CONFIG}"
