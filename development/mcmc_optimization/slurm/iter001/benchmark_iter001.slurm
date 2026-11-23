#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=mcmc_i001_benchmark
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly PYTHON_BIN=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
: "${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/mcmc_optimization/slurm/iter001/iter001_config.json"
readonly HASH_MANIFEST="${REPO_ROOT}/development/mcmc_optimization/slurm/iter001/execution_files.sha256"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight
test "$(cd "${REPO_ROOT}" && pwd -P)" = "${REPO_ROOT}"
test "$(git -C "${REPO_ROOT}" branch --show-current)" = "feature/mcmc-optimization"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "547cc22b170b3262e8ead20e948372e9d59fbc98"
test "$(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" = "46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6"
cmp "${SUBMISSION_CONFIG}" "${CANONICAL_CONFIG}"
(cd "${REPO_ROOT}" && sha256sum --check "${HASH_MANIFEST}")
export PYTHONPATH="${REPO_ROOT}"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd "${REPO_ROOT}"
/usr/bin/time -v "${PYTHON_BIN}" development/mcmc_optimization/slurm/iter001/run_iter001.py benchmark --config "${SUBMISSION_CONFIG}" --output "${OUTPUT_ROOT}/results/benchmark/benchmark_report.json"
