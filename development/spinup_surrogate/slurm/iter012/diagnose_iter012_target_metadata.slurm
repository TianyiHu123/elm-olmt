#!/bin/bash -e
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --job-name=spinup_iter012_metadata
#SBATCH --output=spinup_iter012_metadata_%j.out
#SBATCH --error=spinup_iter012_metadata_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ITER_DIR="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012"
readonly DIAGNOSTIC_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_metadata_diagnostic
readonly CANONICAL_SCRIPT="${ITER_DIR}/diagnose_iter012_target_metadata.slurm"
readonly CANONICAL_PYTHON="${ITER_DIR}/diagnose_iter012_target_metadata.py"
readonly SUBMITTED_SCRIPT="${DIAGNOSTIC_ROOT}/diagnose_iter012_target_metadata.slurm"
readonly SUBMITTED_PYTHON="${DIAGNOSTIC_ROOT}/diagnose_iter012_target_metadata.py"

test "$(pwd -P)" = "${DIAGNOSTIC_ROOT}"
test -f "${SUBMITTED_SCRIPT}"
test -f "${SUBMITTED_PYTHON}"
cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
cmp -s "${CANONICAL_PYTHON}" "${SUBMITTED_PYTHON}"
cd "${REPO_ROOT}"
module load micromamba
micromamba run -n OLMT_puma python "${SUBMITTED_PYTHON}"
