#!/bin/bash -e
# Canonical Puma Iter012 release script. Submit only a variant-local byte-identical copy.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:15:00
#SBATCH --job-name=spinup_iter012_release
#SBATCH --output=spinup_iter012_release_%j.out
#SBATCH --error=spinup_iter012_release_%j.err

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ITERATION_RECORD="${REPO_ROOT}/development/spinup_surrogate/iterations/iter012.md"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/case.release_spinup_iter012.slurm"
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/iter012_releases.tsv"
readonly SOURCE_MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter012/iter012_source_manifest.sha256"
readonly RELEASE_TOOL="${REPO_ROOT}/development/spinup_surrogate/tools/release_spinup_surrogate.py"
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
readonly CASE_LIST=ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC

test -f "${REPO_ROOT}/predict_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
test -f "${ITERATION_RECORD}"
test -f "${CANONICAL_SCRIPT}"
test -f "${MANIFEST}"
test -f "${SOURCE_MANIFEST}"
test -f "${RELEASE_TOOL}"
test -d "${OUTPUT_ROOT}"

readonly SUBMISSION_CONFIG="${SUBMISSION_CONFIG:?Set variant-local SUBMISSION_CONFIG}"
test -f "${SUBMISSION_CONFIG}"
mapfile -t config_lines < "${SUBMISSION_CONFIG}"
test "${#config_lines[@]}" -eq 5
[[ "${config_lines[0]}" == VARIANT=* ]]
[[ "${config_lines[1]}" == FEATURE_COUNT=* ]]
[[ "${config_lines[2]}" == FEATURE_SUBSET=* ]]
[[ "${config_lines[3]}" == REFERENCE_STATS=* ]]
[[ "${config_lines[4]}" == OUTPUT_ARTIFACT=* ]]

readonly VARIANT="${config_lines[0]#VARIANT=}"
readonly FEATURE_COUNT="${config_lines[1]#FEATURE_COUNT=}"
readonly FEATURE_SUBSET="${config_lines[2]#FEATURE_SUBSET=}"
readonly REFERENCE_STATS="${config_lines[3]#REFERENCE_STATS=}"
readonly OUTPUT_ARTIFACT="${config_lines[4]#OUTPUT_ARTIFACT=}"

readonly LOCK_MATCH_COUNT="$(awk -F '\t' \
  -v v="${VARIANT}" \
  -v n="${FEATURE_COUNT}" \
  -v f="${FEATURE_SUBSET}" \
  -v r="${REFERENCE_STATS}" \
  -v o="${OUTPUT_ARTIFACT}" \
  'NR>1 && $1==v && $2==n && $3==f && $4==r && $5==o {count++}
   END {print count+0}' "${MANIFEST}")"
test "${LOCK_MATCH_COUNT}" -eq 1

readonly RUN_NAME="spinup_surrogate_iter012_${VARIANT}"
readonly RUN_DIR="${OUTPUT_ROOT}/${RUN_NAME}"
readonly SUBMITTED_SCRIPT="${RUN_DIR}/submit_${VARIANT}.slurm"
test "$(pwd -P)" = "${RUN_DIR}"
test "${SUBMISSION_CONFIG}" = "${RUN_DIR}/submission_config.env"
test "${OUTPUT_ARTIFACT}" = "${RUN_DIR}/surrogate_spinup/spinup_surrogate_iter012_${VARIANT}.pkl"
test -f "${SUBMITTED_SCRIPT}"
test -f "${REFERENCE_STATS}"
cmp -s "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")

readonly N_JOBS=4
readonly PRE_DISPATCH=n_jobs
readonly JOB_CACHE_DIR="${OUTPUT_ROOT}/.runtime_cache/iter012/${SLURM_JOB_ID}"
mkdir -p "${JOB_CACHE_DIR}"
export XDG_CACHE_HOME="${JOB_CACHE_DIR}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1

cd "${REPO_ROOT}"
echo "PROVENANCE variant=${VARIANT} config_sha256=$(sha256sum "${SUBMISSION_CONFIG}" | awk '{print $1}') canonical_sha256=$(sha256sum "${CANONICAL_SCRIPT}" | awk '{print $1}') source_manifest_sha256=$(sha256sum "${SOURCE_MANIFEST}" | awk '{print $1}') commit=$(git rev-parse HEAD)"
module load micromamba
micromamba run -n OLMT_puma python \
  "${RELEASE_TOOL}" \
  --variant "${VARIANT}" \
  --case-list "${CASE_LIST}" \
  --spinup-case-list "${CASE_LIST}" \
  --feature-subset "${FEATURE_SUBSET}" \
  --reference-stats "${REFERENCE_STATS}" \
  --output-artifact "${OUTPUT_ARTIFACT}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --submission-config "${SUBMISSION_CONFIG}" \
  --n-jobs "${N_JOBS}" \
  --pre-dispatch "${PRE_DISPATCH}"
