#!/bin/bash -e
# Bounded Puma compute-node validation for iter009; does not load cases or train a model.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --job-name=spinup_iter009_validate

set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly VALIDATOR="${REPO_ROOT}/development/spinup_surrogate/slurm/iter009/validate_iter009.py"
readonly GLOBAL_VALIDATOR="${REPO_ROOT}/development/spinup_surrogate/tools/validate_global_feature_filter.py"
test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${REPO_ROOT}/development/spinup_surrogate/iterations/iter009.md"
test -f "${VALIDATOR}"
test -f "${GLOBAL_VALIDATOR}"
cd "${REPO_ROOT}"
module load micromamba
micromamba run -n OLMT_puma python "${GLOBAL_VALIDATOR}"
micromamba run -n OLMT_puma python "${VALIDATOR}"
