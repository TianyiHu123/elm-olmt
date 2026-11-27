#!/usr/bin/env bash
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot
readonly EXPECTED_CONFIG=${RUNTIME_ROOT}/submitted/iter005_config.json
readonly CHECKSUM_MANIFEST=${RUNTIME_ROOT}/manifests/execution_files.sha256
readonly EXPECTED_BRANCH=feature/mcmc-optimization
readonly EXPECTED_HEAD=205cd410f612bd7c751728d722c599b09aca6b86
readonly EXPECTED_PLAN=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0

if [[ $# -ne 2 ]]; then
  echo "usage: verify_iter005_package.sh CONFIG SUBMITTED_SLURM" >&2
  exit 2
fi
config=$1
script_name=$2
[[ "${config}" == "${EXPECTED_CONFIG}" ]] || { echo "unexpected config path" >&2; exit 2; }
case "${script_name}" in
  preflight_iter005.slurm|density_iter005.slurm|pilot_abby_iter005.slurm|pilot_jerc_iter005.slurm|diagnostics_iter005.slurm) ;;
  *) echo "unexpected submitted script" >&2; exit 2 ;;
esac
[[ "$(hostname)" == *.hpc.arizona.edu ]] || { echo "not on UA HPC" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && pwd -P)" == "${REPO_ROOT}" ]] || { echo "repository physical path mismatch" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git branch --show-current)" == "${EXPECTED_BRANCH}" ]] || { echo "branch mismatch" >&2; exit 2; }
[[ "$(cd "${REPO_ROOT}" && git rev-parse HEAD)" == "${EXPECTED_HEAD}" ]] || { echo "HEAD mismatch" >&2; exit 2; }
[[ "$(sha256sum "${REPO_ROOT}/development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" == "${EXPECTED_PLAN}" ]] || { echo "plan mismatch" >&2; exit 2; }
cd "${REPO_ROOT}"
sha256sum -c "${CHECKSUM_MANIFEST}"
canonical=${REPO_ROOT}/development/mcmc_optimization/slurm/iter005
for name in preflight_iter005.slurm density_iter005.slurm pilot_abby_iter005.slurm pilot_jerc_iter005.slurm diagnostics_iter005.slurm run_iter005.py run_iter005_tests.py verify_iter005_package.sh validate_closeout_iter005.sh validate_accounting_iter005.jq iter005_config.json execution_manifest.json; do
  cmp "${RUNTIME_ROOT}/submitted/${name}" "${canonical}/${name}"
done
[[ "$(jq -r '.execution_checksum_manifest_sha256' "${RUNTIME_ROOT}/submitted/execution_manifest.json")" == "$(sha256sum "${CHECKSUM_MANIFEST}" | awk '{print $1}')" ]] || { echo "checksum manifest identity mismatch" >&2; exit 2; }
[[ "$(jq -r '.config_sha256' "${RUNTIME_ROOT}/submitted/execution_manifest.json")" == "$(sha256sum "${EXPECTED_CONFIG}" | awk '{print $1}')" ]] || { echo "config manifest identity mismatch" >&2; exit 2; }
[[ "$(jq -r '.driver_sha256' "${RUNTIME_ROOT}/submitted/execution_manifest.json")" == "$(sha256sum "${RUNTIME_ROOT}/submitted/run_iter005.py" | awk '{print $1}')" ]] || { echo "driver manifest identity mismatch" >&2; exit 2; }
[[ "$(jq -r '.verify_sha256' "${RUNTIME_ROOT}/submitted/execution_manifest.json")" == "$(sha256sum "${RUNTIME_ROOT}/submitted/verify_iter005_package.sh" | awk '{print $1}')" ]] || { echo "verifier manifest identity mismatch" >&2; exit 2; }
[[ "$(jq -r '.result' "${RUNTIME_ROOT}/reviews/package_review.json")" == "pass" ]] || { echo "independent package review missing or blocked" >&2; exit 2; }
echo "MCMC_ITER005_EXECUTION_IDENTITY_PASS script=${script_name}"
