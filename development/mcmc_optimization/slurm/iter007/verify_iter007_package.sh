#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter007_observation_release_0002
readonly CONFIG=${RUNTIME_ROOT}/submitted/iter007_config.json
readonly SOURCE_MANIFEST=${RUNTIME_ROOT}/manifests/source_files.sha256
readonly EXPECTED_HEAD=19bf509d6cb23c53c8cc58fb25682c89f3825597
readonly EXPECTED_PLAN=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0

[[ $# -eq 1 ]] || { echo 'usage: verify_iter007_package.sh submitted-script-basename' >&2; exit 2; }
readonly SCRIPT_NAME=$1
[[ ${SCRIPT_NAME} == *_iter007.slurm ]] || { echo 'wrong script name' >&2; exit 2; }
[[ -f ${RUNTIME_ROOT}/submitted/${SCRIPT_NAME} ]] || { echo 'missing submitted script' >&2; exit 2; }
[[ $(hostname) == *.hpc.arizona.edu ]] || { echo 'not on Puma' >&2; exit 2; }
[[ $(cd "${REPO_ROOT}" && git branch --show-current) == feature/mcmc-optimization ]] || { echo 'branch mismatch' >&2; exit 2; }
[[ $(cd "${REPO_ROOT}" && git rev-parse HEAD) == "${EXPECTED_HEAD}" ]] || { echo 'HEAD mismatch' >&2; exit 2; }
[[ $(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | cut -d' ' -f1) == "${EXPECTED_PLAN}" ]] || { echo 'plan mismatch' >&2; exit 2; }
[[ $(sha256sum "${SOURCE_MANIFEST}" | cut -d' ' -f1) == "${ITER007_MANIFEST_SHA:?manifest hash required}" ]] || { echo 'source manifest mismatch' >&2; exit 2; }
cd "${REPO_ROOT}"
sha256sum -c "${SOURCE_MANIFEST}" >/dev/null
cmp "${CONFIG}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter007/iter007_config.json"
cmp "${RUNTIME_ROOT}/submitted/${SCRIPT_NAME}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter007/${SCRIPT_NAME}"
cmp "${RUNTIME_ROOT}/submitted/run_iter007.py" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter007/run_iter007.py"
cmp "${RUNTIME_ROOT}/submitted/integrate_iter007.py" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter007/integrate_iter007.py"
echo "MCMC_ITER007_EXECUTION_IDENTITY_PASS script=${SCRIPT_NAME}"
