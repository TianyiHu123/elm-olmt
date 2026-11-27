#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --job-name=mcmc_i006_f
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/logs/f_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/logs/f_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics
readonly STAGE_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/submitted/f/attempt_001
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
printf 'stage_f job=%s node=%s host=%s workdir=%s\n' "${SLURM_JOB_ID:-unset}" "${SLURM_JOB_NODELIST:-unset}" "$(hostname -s)" "$(pwd -P)"
test -n "${SLURM_JOB_ID:-}"
test "$(pwd -P)" = "${RUNTIME_ROOT}"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = b99bd8be53265e37df171c430495a5258f6f57e3
printf '%s  %s\n' '5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0' "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | sha256sum -c -
sha256sum -c "${STAGE_ROOT}/f_source.sha256"
sha256sum -c "${STAGE_ROOT}/f_package.sha256"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
"${PYTHON}" "${STAGE_ROOT}/stage_f.py"
test "$(du -sb "${RUNTIME_ROOT}" | cut -f1)" -le 2147483648
