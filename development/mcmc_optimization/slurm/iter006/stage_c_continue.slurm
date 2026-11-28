#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --job-name=mcmc_i006_c2
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/logs/c2_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/logs/c2_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics
readonly STAGE_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics/submitted/c/attempt_002
readonly PYTHON=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
printf 'stage_c2 job=%s node=%s workdir=%s\n' "${SLURM_JOB_ID:-unset}" "${SLURM_JOB_NODELIST:-unset}" "$(pwd -P)"
test -n "${SLURM_JOB_ID:-}"
test "$(pwd -P)" = "${RUNTIME_ROOT}"
test "$(git -C "${REPO_ROOT}" branch --show-current)" = feature/mcmc-optimization
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = 9f81aa9d2065339c59d86f5933231b89b7b9df2a
printf '%s  %s\n' '5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0' "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | sha256sum -c -
sha256sum -c "${STAGE_ROOT}/source.sha256"
sha256sum -c "${STAGE_ROOT}/package.sha256"
test "$(jq -r '.result' "${RUNTIME_ROOT}/validation/b_attempt_002/numerical_validation.json")" = pass
rg -Fq 'MCMC_ITER006_UNITTEST_PASS tests=52 skipped=0' "${RUNTIME_ROOT}/logs/b2_24841071.out"
rg -Fq 'stage_b2 test_status=0 numerical_status=0' "${RUNTIME_ROOT}/logs/b2_24841071.out"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="${REPO_ROOT}"
"${PYTHON}" "${STAGE_ROOT}/stage_c_continue.py"
test "$(du -sb "${RUNTIME_ROOT}" | cut -f1)" -le 2147483648
