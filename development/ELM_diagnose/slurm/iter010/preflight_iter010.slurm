#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=02:00:00
#SBATCH --job-name=elm-diag-i010-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOOL=${REPO_ROOT}/development/ELM_diagnose/tools/oat_carbon_balance.py
readonly CONFIG_FILE=${SUBMISSION_CONFIG:?SUBMISSION_CONFIG required}
source "${CONFIG_FILE}"
test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256}"
test "$(sha256sum conda_envs/OLMT_puma.yml | awk '{print $1}')" = "${ENV_FILE_SHA256}"
test "$(sha256sum "${CONTROL_PARAMFILE}" | awk '{print $1}')" = "3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9"
test "$(sha256sum "${CORE_RESULTS}/output_manifest.json" | awk '{print $1}')" = "afa885d5642b7cd886e5dfc05afd2575c803e91250c040604d23333fa5b95aae"
test "$(sha256sum "${CORE_INPUT_MANIFEST}" | awk '{print $1}')" = "bb2836591c0857fb45a560cc1d7fdfb2d85053571394a85633f10855f982bf62"
readonly CONFIG_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/config
readonly PARAMETER_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/params
readonly -a CONFIG_HASHES=(84063fe731ab64d3eb543bd13ff1986c498f163b8e4b70037c75de990dbb1f40 520536aa2d2a6943b1e7b268518a8b9aca9d30d0a63b61f79da92d6bbab73a0c e70d675327c231bb9f43da5deb1d3868694cda12e75398a90e8b4c77eddf7749 68e0b8af0098f16ec99961d88114e90f35574f7300f3ac13d6ce72126bd45d21)
readonly -a PARAM_HASHES=(51f5c11b913cc2f95c8afaf82bdf68de1a8f8a4a30baeceb417ecba84b11a39f a3ae8e8213e959f4f1f4a0a6b1f0937cbd6ead2f6e9af2941b6c2cf4b6f01107 9f7949a5730c0ab6f4ccdfaa1ace8a6e0f48087251c9ab541a2aace195c2a9e9 834b9073d9e53c921b5f8e389e96430749856ab02b5a2c08a8976ef7a7f74157)
for i in 1 2 3 4; do j=$((i-1)); cfg="${CONFIG_DIR}/ABBY_cn_s${i}.cfg"; par="${PARAMETER_DIR}/cn_s${i}_paramfile"; test "$(sha256sum "${cfg}"|awk '{print $1}')" = "${CONFIG_HASHES[j]}"; test "$(sha256sum "${par}"|awk '{print $1}')" = "${PARAM_HASHES[j]}"; grep -Eq '^use_nofire[[:space:]]*=[[:space:]]*\.true\.' "${cfg}"; grep -Eq '^use_vertsoilc[[:space:]]*=[[:space:]]*\.true\.' "${cfg}"; done
test ! -e "${OUTPUT_DIR}"
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
  --output "${OUTPUT_DIR}" \
  --validate-only
