#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=02:00:00
#SBATCH --job-name=elm-diag-i004-preflight
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err

set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/development/ELM_diagnose/WORKFLOW.md"
readonly ITERATION_FILE="${REPO_ROOT}/development/ELM_diagnose/iterations/iter004.md"
readonly TOOL="${REPO_ROOT}/development/ELM_diagnose/tools/oat_sensitivity.py"
readonly FIXTURE="${REPO_ROOT}/development/ELM_diagnose/slurm/iter004/test_oat_sensitivity.py"
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

test "$(pwd -P)" = "${RUN_DIR}"
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${REPOSITORY_COMMIT:?missing REPOSITORY_COMMIT}"
test "$(sha256sum "${TOOL}" | awk '{print $1}')" = "${TOOL_SHA256:?missing TOOL_SHA256}"
test "$(sha256sum "${FIXTURE}" | awk '{print $1}')" = "${FIXTURE_SHA256:?missing FIXTURE_SHA256}"

module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${FIXTURE}"
micromamba run -n OLMT_puma python "${TOOL}" \
  --pickle-dir "${PICKLE_DIR}" \
  --parameter-pickle act25:ABBY_ctrlact25_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle br_mr:ABBY_ctrlbrmr_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle grperc:ABBY_ctrlgrperc_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle grpnow:ABBY_ctrlgrpnow_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l1:ABBY_ctrlkl1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l2:ABBY_ctrlkl2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_l3:ABBY_ctrlkl3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s1:ABBY_ctrlks1_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s2:ABBY_ctrlks2_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s3:ABBY_ctrlks3_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle k_s4:ABBY_ctrlks4_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle kmax:ABBY_ctrlkmax_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle leaf_long:ABBY_ctrlleaflong_I20TRCNPRDCTCBC.pkl \
  --parameter-pickle q10_mr:ABBY_ctrlq10mr_I20TRCNPRDCTCBC.pkl \
  --log-parameters k_l1,k_l2,k_l3,k_s1,k_s2,k_s3,k_s4 \
  --control-paramfile "${CONTROL_PARAMFILE}" \
  --output "${OUTPUT_DIR}" \
  --validate-only
