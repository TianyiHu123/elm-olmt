#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=04:00:00
#SBATCH --job-name=elm-diag-i010-diagnostic
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOOL=${REPO_ROOT}/development/ELM_diagnose/tools/oat_carbon_balance.py
readonly VALIDATOR=${REPO_ROOT}/development/ELM_diagnose/slurm/iter010/validate_iter010_artifacts.py
readonly CONFIG_FILE=${SUBMISSION_CONFIG:?SUBMISSION_CONFIG required}
source "${CONFIG_FILE}"
test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256}"
test "$(sha256sum "${VALIDATOR}" | awk '{print $1}')" = "${VALIDATOR_SHA256}"
test "$(sha256sum "${INPUT_MANIFEST}" | awk '{print $1}')" = "${INPUT_MANIFEST_SHA256}"
test ! -e "${OUTPUT_DIR}"; test ! -e "${STAGING_DIR}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${TOOL}" \
  --pickle-dir "${PICKLE_DIR}" \
  --parameter-pickle cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl \
  --config-dir "${CONFIG_DIR}" \
  --parameter-dir "${PARAMETER_DIR}" \
  --control-paramfile "${CONTROL_PARAMFILE}" \
  --core-input-manifest "${CORE_INPUT_MANIFEST}" \
  --core-results "${CORE_RESULTS}" \
  --output "${STAGING_DIR}" \
  --manifest "${INPUT_MANIFEST}"
micromamba run -n OLMT_puma python "${VALIDATOR}" --results "${STAGING_DIR}"
mv "${STAGING_DIR}" "${OUTPUT_DIR}"
echo "ITER010_ATOMIC_PUBLICATION_PASS output=${OUTPUT_DIR}"
