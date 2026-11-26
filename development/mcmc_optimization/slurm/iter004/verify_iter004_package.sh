#!/usr/bin/env bash
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot
readonly EXPECTED_CONFIG=${RUNTIME_ROOT}/submitted/iter004_config.json
readonly CHECKSUM_MANIFEST=${RUNTIME_ROOT}/manifests/execution_files.sha256
readonly EXPECTED_BRANCH=feature/mcmc-optimization
readonly EXPECTED_HEAD=4ed771d270559cf4cb5fc2c8f54b5d099d51ecb8
readonly EXPECTED_PLAN=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0

if [[ $# -ne 2 ]]; then
  echo "usage: verify_iter004_package.sh CONFIG SUBMITTED_SLURM" >&2
  exit 2
fi
config=$1
script_name=$2
[[ "${config}" == "${EXPECTED_CONFIG}" ]] || { echo "unexpected config path" >&2; exit 2; }
[[ "${script_name}" == *_iter004.slurm ]] || { echo "unexpected submitted script name" >&2; exit 2; }
submitted_slurm=${RUNTIME_ROOT}/submitted/${script_name}
[[ -f "${submitted_slurm}" ]] || { echo "submitted Slurm file missing" >&2; exit 2; }
[[ "$(hostname)" == *.hpc.arizona.edu ]] || { echo "not on UA HPC" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git branch --show-current)" == "${EXPECTED_BRANCH}" ]] || { echo "branch mismatch" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git rev-parse HEAD)" == "${EXPECTED_HEAD}" ]] || { echo "HEAD mismatch" >&2; exit 2; }
[[ "$(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" == "${EXPECTED_PLAN}" ]] || { echo "plan mismatch" >&2; exit 2; }
cd "${REPO_ROOT}"
sha256sum -c "${CHECKSUM_MANIFEST}"
cmp "${submitted_slurm}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter004/${script_name}"
cmp "${config}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter004/iter004_config.json"
for name in run_iter004.py run_iter004_tests.py verify_iter004_package.sh; do
  cmp "${RUNTIME_ROOT}/submitted/${name}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter004/${name}"
done
cmp "${RUNTIME_ROOT}/submitted/execution_manifest.json" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter004/execution_manifest.json"
[[ "$(jq -r '.execution_checksum_manifest_sha256' "${RUNTIME_ROOT}/submitted/execution_manifest.json")" == "$(sha256sum "${CHECKSUM_MANIFEST}" | awk '{print $1}')" ]] || { echo "execution manifest checksum identity mismatch" >&2; exit 2; }
echo "MCMC_ITER004_EXECUTION_IDENTITY_PASS script=${script_name}"
