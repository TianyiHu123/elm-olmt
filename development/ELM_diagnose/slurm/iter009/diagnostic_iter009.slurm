#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=04:00:00
#SBATCH --job-name=elm-diag-i009-diagnostic
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
readonly ITERATION_FILE="${REPO_ROOT}/development/ELM_diagnose/iterations/iter009.md"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/oat_nutrient_diagnostics.py"
readonly VALIDATOR="${REPO_ROOT}/development/ELM_diagnose/slurm/iter009/validate_iter009_artifacts.py"
readonly ENV_FILE="${REPO_ROOT}/conda_envs/OLMT_puma.yml"
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"

test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${ITERATION_FILE}"
test -f "${TOOL}"
test -f "${VALIDATOR}"
test -f "${ENV_FILE}"
test -f "${CONFIG_FILE}"
source "${CONFIG_FILE}"

readonly RUN_DIR="${RUN_DIR:?missing RUN_DIR}"
readonly OUTPUT_DIR="${OUTPUT_DIR:?missing OUTPUT_DIR}"
readonly STAGING_DIR="${STAGING_DIR:?missing STAGING_DIR}"
readonly PICKLE_DIR="${PICKLE_DIR:?missing PICKLE_DIR}"
readonly CONFIG_DIR="${CONFIG_DIR:?missing CONFIG_DIR}"
readonly PARAMETER_DIR="${PARAMETER_DIR:?missing PARAMETER_DIR}"
readonly CONTROL_PARAMFILE="${CONTROL_PARAMFILE:?missing CONTROL_PARAMFILE}"
readonly OBSERVATION_FILE="${OBSERVATION_FILE:?missing OBSERVATION_FILE}"
readonly INPUT_MANIFEST="${INPUT_MANIFEST:?missing INPUT_MANIFEST}"

test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${VALIDATOR}" | awk '{print $1}')" = "${VALIDATOR_SHA256:?missing VALIDATOR_SHA256}"
test "$(sha256sum "${ENV_FILE}" | awk '{print $1}')" = "${ENV_FILE_SHA256:?missing ENV_FILE_SHA256}"
test "$(sha256sum "${OBSERVATION_FILE}" | awk '{print $1}')" = "${OBSERVATION_FILE_SHA256:?missing OBSERVATION_FILE_SHA256}"
test "$(sha256sum "${INPUT_MANIFEST}" | awk '{print $1}')" = "${INPUT_MANIFEST_SHA256:?missing INPUT_MANIFEST_SHA256}"
test ! -e "${OUTPUT_DIR}"
test ! -e "${STAGING_DIR}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${TOOL}" \
  --site ABBY \
  --pickle-dir "${PICKLE_DIR}" \
  --parameter-pickle cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl \
  --config-file "cn_s1:${CONFIG_DIR}/ABBY_cn_s1.cfg" \
  --config-file "cn_s2:${CONFIG_DIR}/ABBY_cn_s2.cfg" \
  --config-file "cn_s3:${CONFIG_DIR}/ABBY_cn_s3.cfg" \
  --config-file "cn_s4:${CONFIG_DIR}/ABBY_cn_s4.cfg" \
  --parameter-file "cn_s1:${PARAMETER_DIR}/cn_s1_paramfile" \
  --parameter-file "cn_s2:${PARAMETER_DIR}/cn_s2_paramfile" \
  --parameter-file "cn_s3:${PARAMETER_DIR}/cn_s3_paramfile" \
  --parameter-file "cn_s4:${PARAMETER_DIR}/cn_s4_paramfile" \
  --control-paramfile "${CONTROL_PARAMFILE}" \
  --observation "SR:${OBSERVATION_FILE}" \
  --output "${STAGING_DIR}" \
  --manifest "${INPUT_MANIFEST}"
micromamba run -n OLMT_puma python "${VALIDATOR}" \
  --input-manifest "${INPUT_MANIFEST}" \
  --results "${STAGING_DIR}"
mv "${STAGING_DIR}" "${OUTPUT_DIR}"
echo "ITER009_ATOMIC_PUBLICATION_PASS output=${OUTPUT_DIR}"
