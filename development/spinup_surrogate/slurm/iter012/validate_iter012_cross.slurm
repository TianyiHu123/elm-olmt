#!/bin/bash -e
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:15:00
#SBATCH --job-name=spinup_iter012_validate
#SBATCH --output=spinup_iter012_validate_%j.out
#SBATCH --error=spinup_iter012_validate_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/validate_iter012_cross.slurm"
readonly VALIDATION_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_validation
readonly SUBMITTED_SCRIPT="${VALIDATION_ROOT}/validate_iter012_cross.slurm"
readonly SOURCE_MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/iter012_source_manifest.sha256"
readonly DROP32_ARTIFACT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl
readonly DROP21_ARTIFACT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_surrogate/summaries/iter012"

test "$(pwd -P)" = "${VALIDATION_ROOT}"
test -f "${SUBMITTED_SCRIPT}"
test -f "${DROP32_ARTIFACT}"
test -f "${DROP21_ARTIFACT}"
cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
cd "${REPO_ROOT}"
sha256sum -c "${SOURCE_MANIFEST}"

readonly JOB_CACHE_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/.runtime_cache/iter012/validate_${SLURM_JOB_ID}
mkdir -p "${JOB_CACHE_DIR}"
export XDG_CACHE_HOME="${JOB_CACHE_DIR}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

module load micromamba
micromamba run -n OLMT_puma python \
  "${REPO_ROOT}/development/spinup_surrogate/tools/validate_iter012_release.py" \
  --drop32-artifact "${DROP32_ARTIFACT}" \
  --drop21-artifact "${DROP21_ARTIFACT}" \
  --summary-root "${SUMMARY_ROOT}"
