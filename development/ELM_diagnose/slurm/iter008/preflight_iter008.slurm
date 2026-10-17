#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=02:00:00
#SBATCH --job-name=elm-diag-i008-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
readonly ITERATION_FILE="${REPO_ROOT}/development/ELM_diagnose/iterations/iter008.md"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/oat_nutrient_diagnostics.py"
readonly ENV_FILE="${REPO_ROOT}/conda_envs/OLMT_puma.yml"
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"

test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${ITERATION_FILE}"
test -f "${TOOL}"
test -f "${ENV_FILE}"
test -f "${CONFIG_FILE}"
source "${CONFIG_FILE}"

readonly RUN_DIR="${RUN_DIR:?missing RUN_DIR}"
readonly OUTPUT_DIR="${OUTPUT_DIR:?missing OUTPUT_DIR}"
readonly PICKLE_DIR="${PICKLE_DIR:?missing PICKLE_DIR}"
readonly CONFIG_DIR="${CONFIG_DIR:?missing CONFIG_DIR}"
readonly PARAMETER_DIR="${PARAMETER_DIR:?missing PARAMETER_DIR}"
readonly CONTROL_PARAMFILE="${CONTROL_PARAMFILE:?missing CONTROL_PARAMFILE}"

test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${ENV_FILE}" | awk '{print $1}')" = "${ENV_FILE_SHA256:?missing ENV_FILE_SHA256}"
test "$(sha256sum "${CONTROL_PARAMFILE}" | awk '{print $1}')" = "${CONTROL_PARAMFILE_SHA256:?missing CONTROL_PARAMFILE_SHA256}"
test ! -e "${OUTPUT_DIR}"

readonly -a PARAMETERS=(cn_s1 cn_s2 cn_s3 cn_s4)
readonly -a CONFIG_NAMES=(ABBY_cn_s1.cfg ABBY_cn_s2.cfg ABBY_cn_s3.cfg ABBY_cn_s4.cfg)
readonly -a PARAMETER_FILES=(cn_s1_paramfile cn_s2_paramfile cn_s3_paramfile cn_s4_paramfile)
readonly -a PICKLE_NAMES=(
  ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl
  ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl
  ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl
  ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl
)
readonly -a PICKLE_HASHES=(
  fca486c11cf2a7c087195a7608b49d9b26c87c7369cd5a9418d6e44f4d9fcc1f
  40589f8c95da4d12940dc99f1acfbe118721399e826283365fd628c3642c2297
  b3d5d2aa40c48211551a16cd8db8ffca56430dc13f323087aeeffaf87ee525f1
  c68eaafb6b0dbe54c5aa7eb604842ee36673228cb0357ecdd4b973ff35954ff6
)
readonly -a CONFIG_HASHES=(
  84063fe731ab64d3eb543bd13ff1986c498f163b8e4b70037c75de990dbb1f40
  520536aa2d2a6943b1e7b268518a8b9aca9d30d0a63b61f79da92d6bbab73a0c
  e70d675327c231bb9f43da5deb1d3868694cda12e75398a90e8b4c77eddf7749
  68e0b8af0098f16ec99961d88114e90f35574f7300f3ac13d6ce72126bd45d21
)
readonly -a PARAMETER_HASHES=(
  51f5c11b913cc2f95c8afaf82bdf68de1a8f8a4a30baeceb417ecba84b11a39f
  a3ae8e8213e959f4f1f4a0a6b1f0937cbd6ead2f6e9af2941b6c2cf4b6f01107
  9f7949a5730c0ab6f4ccdfaa1ace8a6e0f48087251c9ab541a2aace195c2a9e9
  834b9073d9e53c921b5f8e389e96430749856ab02b5a2c08a8976ef7a7f74157
)

for index in "${!PARAMETERS[@]}"; do
  config_path="${CONFIG_DIR}/${CONFIG_NAMES[index]}"
  parameter_path="${PARAMETER_DIR}/${PARAMETER_FILES[index]}"
  test "$(sha256sum "${config_path}" | awk '{print $1}')" = "${CONFIG_HASHES[index]}"
  test "$(sha256sum "${parameter_path}" | awk '{print $1}')" = "${PARAMETER_HASHES[index]}"
  test "$(sha256sum "${PICKLE_DIR}/${PICKLE_NAMES[index]}" | awk '{print $1}')" = "${PICKLE_HASHES[index]}"
  grep -Eq '^use_vertsoilc[[:space:]]*=[[:space:]]*\.true\.[[:space:]]*$' "${config_path}"
  grep -F "${PARAMETER_FILES[index]}" "${config_path}" >/dev/null
  test "$(awk 'NR == 1 {print $1; exit}' "${parameter_path}")" = "${PARAMETERS[index]}"
  test "$(sed -n '/^\[postprocessing\]/,/^frequency/p' "${config_path}" | sha256sum | awk '{print $1}')" = "${POSTPROCESSING_SHA256:?missing POSTPROCESSING_SHA256}"
done

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
  --output "${OUTPUT_DIR}" \
  --validate-only
