#!/bin/bash -e
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --job-name=spinup_iter012_preflight
#SBATCH --output=spinup_iter012_preflight_%j.out
#SBATCH --error=spinup_iter012_preflight_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/validate_iter012.slurm"
readonly PREFLIGHT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_preflight
readonly SUBMITTED_SCRIPT="${PREFLIGHT_ROOT}/validate_iter012.slurm"
readonly SOURCE_MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/iter012_source_manifest.sha256"

test "$(pwd -P)" = "${PREFLIGHT_ROOT}"
test -f "${SUBMITTED_SCRIPT}"
cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
cd "${REPO_ROOT}"
sha256sum -c "${SOURCE_MANIFEST}"
module load micromamba
micromamba run -n OLMT_puma python \
  "${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/validate_iter012.py"
