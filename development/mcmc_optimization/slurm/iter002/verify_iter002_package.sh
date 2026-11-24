#!/usr/bin/env bash
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation
readonly EXPECTED_CONFIG=${RUNTIME_ROOT}/submitted/iter002_config.json
readonly CHECKSUM_MANIFEST=${RUNTIME_ROOT}/manifests/execution_files.sha256
readonly EXPECTED_BRANCH=feature/mcmc-optimization
readonly EXPECTED_HEAD=f649e43cfa3c08a0cd02e02a92adf66d59fe2ded
readonly EXPECTED_PLAN=b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab

if [[ $# -ne 2 ]]; then
  echo "usage: verify_iter002_package.sh CONFIG SUBMITTED_SLURM" >&2
  exit 2
fi
config=$1
script_name=$2
[[ "${config}" == "${EXPECTED_CONFIG}" ]] || { echo "unexpected config path: ${config}" >&2; exit 2; }
[[ "${script_name}" == *_iter002.slurm ]] || { echo "unexpected submitted script name: ${script_name}" >&2; exit 2; }
submitted_slurm=${RUNTIME_ROOT}/submitted/${script_name}
[[ -f "${submitted_slurm}" ]] || { echo "submitted Slurm file missing: ${submitted_slurm}" >&2; exit 2; }
[[ "$(hostname)" == *.hpc.arizona.edu ]] || { echo "not on UA HPC" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git branch --show-current)" == "${EXPECTED_BRANCH}" ]] || { echo "branch mismatch" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git rev-parse HEAD)" == "${EXPECTED_HEAD}" ]] || { echo "HEAD mismatch" >&2; exit 2; }
[[ "$(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" == "${EXPECTED_PLAN}" ]] || { echo "plan mismatch" >&2; exit 2; }
expected_manifest=$(jq -r '.execution_checksum_manifest_sha256' "${config}")
[[ "${expected_manifest}" != "PENDING_REFRESH" ]] || { echo "config manifest identity not finalized" >&2; exit 2; }
[[ "$(sha256sum "${CHECKSUM_MANIFEST}" | awk '{print $1}')" == "${expected_manifest}" ]] || { echo "checksum manifest mismatch" >&2; exit 2; }
cd "${REPO_ROOT}"
sha256sum -c "${CHECKSUM_MANIFEST}"
cmp "${submitted_slurm}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter002/${script_name}"
cmp "${config}" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter002/iter002_config.json"
cmp "${RUNTIME_ROOT}/submitted/run_iter002.py" "${REPO_ROOT}/development/mcmc_optimization/slurm/iter002/run_iter002.py"
echo "MCMC_ITER002_EXECUTION_IDENTITY_PASS script=${script_name}"
