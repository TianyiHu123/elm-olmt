#!/bin/bash -e
# Bounded no-training Puma validation for iter010.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --job-name=spinup_iter010_validate
set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt VALIDATOR="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/slurm/iter010/validate_iter010.py" GLOBAL_VALIDATOR="/xdisk/chopinsong/tianyihu/elm-olmt/development/spinup_surrogate/tools/validate_global_feature_filter.py"
test -f "${REPO_ROOT}/train_surrogate_spinup.py"; test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"; test -f "${REPO_ROOT}/development/hpc/puma.md"; test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"; test -f "${REPO_ROOT}/development/spinup_surrogate/iterations/iter010.md"; test -f "${VALIDATOR}"; test -f "${GLOBAL_VALIDATOR}"
cd "${REPO_ROOT}"; module load micromamba; micromamba run -n OLMT_puma python "${GLOBAL_VALIDATOR}"; micromamba run -n OLMT_puma python "${VALIDATOR}"
