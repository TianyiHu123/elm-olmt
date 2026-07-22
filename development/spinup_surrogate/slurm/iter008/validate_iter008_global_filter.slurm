#!/bin/bash -e
# Bounded Puma compute-node validation for iter008 filtering invariants; no training.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --job-name=spinup_iter008_validate

set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly VALIDATOR="${REPO_ROOT}/development/spinup_surrogate/validate_iter008_global_filter.py"
test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${VALIDATOR}"
cd "${REPO_ROOT}"
module load micromamba
micromamba run -n OLMT_puma python "${VALIDATOR}"
