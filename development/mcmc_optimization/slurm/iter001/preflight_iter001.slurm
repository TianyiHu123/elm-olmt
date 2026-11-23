#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=mcmc_i001_preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly PYTHON_BIN=/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python
readonly CANONICAL_CONFIG="${REPO_ROOT}/development/mcmc_optimization/slurm/iter001/iter001_config.json"
readonly HASH_MANIFEST="${REPO_ROOT}/development/mcmc_optimization/slurm/iter001/execution_files.sha256"
: "${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"
test "$(cd "${REPO_ROOT}" && pwd -P)" = "${REPO_ROOT}"
test "$(git -C "${REPO_ROOT}" branch --show-current)" = "feature/mcmc-optimization"
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "547cc22b170b3262e8ead20e948372e9d59fbc98"
test "$(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" = "46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6"
test -f "${SUBMISSION_CONFIG}"
cmp "${SUBMISSION_CONFIG}" "${CANONICAL_CONFIG}"
(cd "${REPO_ROOT}" && sha256sum --check "${HASH_MANIFEST}")
test -x "${PYTHON_BIN}"
export PYTHONPATH="${REPO_ROOT}"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
cd "${REPO_ROOT}"
"${PYTHON_BIN}" -c 'import numpy, scipy, sklearn, netCDF4; import model_ELM.mcmc_prior; import model_ELM.mcmc_coupled_adapter; print("MCMC_ITER001_PREFLIGHT_IMPORT_PASS")'
"${PYTHON_BIN}" -c 'from pathlib import Path; [compile(Path(path).read_text(), path, "exec") for path in ("tests/test_mcmc_prior_iter001.py", "tests/test_mcmc_coupled_interface_iter001.py")]; print("MCMC_ITER001_PREFLIGHT_TEST_SYNTAX_PASS")'
echo MCMC_ITER001_PREFLIGHT_PASS
