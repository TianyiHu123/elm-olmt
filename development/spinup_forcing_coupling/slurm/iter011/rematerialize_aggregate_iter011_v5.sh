#!/usr/bin/env bash
# Preserve v4's partial validator directories and materials before the approved per-site reference correction.
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
readonly AGGREGATE_DIR="${ROOT}/spinup_forcing_coupling_iter011_aggregate"
readonly SUMMARY_ROOT="${REPO_ROOT}/development/spinup_forcing_coupling/summaries/iter011"
test -d "${AGGREGATE_DIR}/result"; test ! -e "${AGGREGATE_DIR}/result_v4_partial"
test -d "${SUMMARY_ROOT}"; test ! -e "${SUMMARY_ROOT}_v4_partial"
mv "${AGGREGATE_DIR}/result" "${AGGREGATE_DIR}/result_v4_partial"
mv "${SUMMARY_ROOT}" "${SUMMARY_ROOT}_v4_partial"
ARCHIVE_VERSION=v4 bash -e "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011/rematerialize_aggregate_iter011_v3.sh"
echo AGGREGATE_REMATERIALIZE_V5_PASS
