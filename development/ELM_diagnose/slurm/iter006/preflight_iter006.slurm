#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --job-name=elm-diag-i006-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
readonly ITERATION_FILE="${REPO_ROOT}/development/ELM_diagnose/iterations/iter006.md"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/oat_sensitivity.py"
readonly FIXTURE="${REPO_ROOT}/development/ELM_diagnose/slurm/iter006/test_oat_extended.py"
readonly ENV_FILE="${REPO_ROOT}/conda_envs/OLMT_puma.yml"
readonly CONFIG_FILE="${SUBMISSION_CONFIG:?SUBMISSION_CONFIG is required}"

test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${ITERATION_FILE}"
test -f "${TOOL}"
test -f "${FIXTURE}"
test -f "${ENV_FILE}"
test -f "${CONFIG_FILE}"

source "${CONFIG_FILE}"

readonly RUN_DIR="${RUN_DIR:?missing RUN_DIR}"
readonly OUTPUT_DIR="${OUTPUT_DIR:?missing OUTPUT_DIR}"
readonly PICKLE_DIR="${PICKLE_DIR:?missing PICKLE_DIR}"
readonly CONTROL_PARAMFILE="${CONTROL_PARAMFILE:?missing CONTROL_PARAMFILE}"
readonly OBSERVATION_FILE="${OBSERVATION_FILE:?missing OBSERVATION_FILE}"

test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${FIXTURE}" | awk '{print $1}')" = "${FIXTURE_SHA256:?missing FIXTURE_SHA256}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${FIXTURE}"
micromamba run -n OLMT_puma python "${TOOL}" \
  --site JERC \
  --pickle-dir "${PICKLE_DIR}" \
  --parameter-pickle act25:JERC_ctrlact25_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle br_mr:JERC_ctrlbrmr_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle grperc:JERC_ctrlgrperc_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle grpnow:JERC_ctrlgrpnow_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l1:JERC_ctrlkl1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l2:JERC_ctrlkl2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l3:JERC_ctrlkl3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s1:JERC_ctrlks1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s2:JERC_ctrlks2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s3:JERC_ctrlks3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s4:JERC_ctrlks4_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle kmax:JERC_ctrlkmax_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle leaf_long:JERC_ctrlleaflong_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle q10_mr:JERC_ctrlq10mr_I20TRCNPRDCTCBC.pkl \
  --log-parameters k_l1,k_l2,k_l3,k_s1,k_s2,k_s3,k_s4 \
  --control-paramfile "${CONTROL_PARAMFILE}" \
  --target GPP --target ER --target SR --target HR_TOTAL --target LITFALL \
  --target LITTER_SOIL_C_TOTAL --target LITR1C --target LITR2C --target LITR3C \
  --target SOIL1C --target SOIL2C --target SOIL3C --target SOIL4C \
  --observation "SR:${OBSERVATION_FILE}" \
  --compensation k_l1:LITR1C:K_LITR1:LITR1_HR \
  --compensation k_l2:LITR2C:K_LITR2:LITR2_HR \
  --compensation k_l3:LITR3C:K_LITR3:LITR3_HR \
  --compensation k_s1:SOIL1C:K_SOIL1:SOIL1_HR \
  --compensation k_s2:SOIL2C:K_SOIL2:SOIL2_HR \
  --compensation k_s3:SOIL3C:K_SOIL3:SOIL3_HR \
  --compensation k_s4:SOIL4C:K_SOIL4:SOIL4_HR \
  --hr-pool CWDC:K_CWD --hr-pool LITR1C:K_LITR1 --hr-pool LITR2C:K_LITR2 \
  --hr-pool LITR3C:K_LITR3 --hr-pool SOIL1C:K_SOIL1 --hr-pool SOIL2C:K_SOIL2 \
  --hr-pool SOIL3C:K_SOIL3 --hr-pool SOIL4C:K_SOIL4 \
  --hr-n-limiter FPI --hr-p-limiter FPI_P \
  --litter-ratio leaf_cn:LEAFC_TO_LITTER:LEAFN_TO_LITTER \
  --litter-ratio leaf_cp:LEAFC_TO_LITTER:LEAFP_TO_LITTER \
  --litter-ratio froot_cn:FROOTC_TO_LITTER:FROOTN_TO_LITTER \
  --litter-ratio froot_cp:FROOTC_TO_LITTER:FROOTP_TO_LITTER \
  --output "${OUTPUT_DIR}" \
  --validate-only
