#!/usr/bin/env bash
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly RUNTIME_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot
readonly RECORD_ROOT=${REPO_ROOT}/development/mcmc_optimization
readonly PACKAGE=${RECORD_ROOT}/slurm/iter005
readonly REPORT=${RECORD_ROOT}/iterations/iter005.md
readonly SUMMARY=${RECORD_ROOT}/summaries/iter005/summary.md
readonly REGISTRY=${RECORD_ROOT}/registry.csv
readonly CUMULATIVE=${RECORD_ROOT}/ITERATION_SUMMARY.md
readonly HANDOFF=${RECORD_ROOT}/handoff/CURRENT.md
readonly DIAGNOSTICS=${RUNTIME_ROOT}/results/diagnostics_validation.json
readonly ACCOUNTING=${RUNTIME_ROOT}/manifests/final_job_accounting.json
readonly PACKAGE_REVIEW=${RUNTIME_ROOT}/reviews/package_review.json
readonly RESULT_REVIEW=${RUNTIME_ROOT}/reviews/result_review.json
readonly PLAN_SHA=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0
readonly START_HEAD=205cd410f612bd7c751728d722c599b09aca6b86

cd "${REPO_ROOT}"
[[ "$(git branch --show-current)" == feature/mcmc-optimization ]] || { echo branch_mismatch >&2; exit 2; }
[[ "$(git rev-parse HEAD)" == "${START_HEAD}" ]] || { echo parent_commit_mismatch >&2; exit 2; }
[[ "$(sha256sum "${RECORD_ROOT}/MCMC_OPTIMIZATION_PLAN.md" | awk '{print $1}')" == "${PLAN_SHA}" ]] || { echo plan_mismatch >&2; exit 2; }
sha256sum -c "${PACKAGE}/execution_files.sha256" >/dev/null
cmp "${RUNTIME_ROOT}/manifests/execution_files.sha256" "${PACKAGE}/execution_files.sha256"
for name in preflight_iter005.slurm density_iter005.slurm pilot_abby_iter005.slurm pilot_jerc_iter005.slurm diagnostics_iter005.slurm run_iter005.py run_iter005_tests.py verify_iter005_package.sh validate_closeout_iter005.sh validate_accounting_iter005.jq iter005_config.json execution_manifest.json; do
  cmp "${RUNTIME_ROOT}/submitted/${name}" "${PACKAGE}/${name}"
done
[[ "$(jq -r '.result' "${PACKAGE_REVIEW}")" == pass ]] || { echo package_review_missing >&2; exit 2; }
[[ "$(jq -r '.result' "${DIAGNOSTICS}")" == pass ]] || { echo diagnostics_not_complete >&2; exit 2; }
decision=$(jq -r '.decision_candidate' "${DIAGNOSTICS}")
case "${decision}" in
  bounded_sampler_pilot_validated|bounded_sampler_pilot_validated_with_mixing_limitations|iter005_validation_failed) ;;
  *) echo invalid_closeout_decision >&2; exit 2 ;;
esac
[[ "$(jq -r '.result' "${RESULT_REVIEW}")" == pass ]] || { echo result_review_missing >&2; exit 2; }
diagnostics_sha=$(sha256sum "${DIAGNOSTICS}" | awk '{print $1}')
[[ "$(jq -r '.reviewed_diagnostics_sha256' "${RESULT_REVIEW}")" == "${diagnostics_sha}" ]] || { echo result_review_identity_mismatch >&2; exit 2; }
[[ "$(jq -r '.reviewer_id' "${RESULT_REVIEW}")" != '' ]] || { echo reviewer_identity_missing >&2; exit 2; }
[[ "$(jq -r '.reviewer_id' "${RESULT_REVIEW}")" != null ]] || { echo reviewer_identity_missing >&2; exit 2; }
[[ "$(jq -r '.reviewer_id' "${RESULT_REVIEW}")" != primary ]] || { echo reviewer_not_independent >&2; exit 2; }
jq -e --arg decision "${decision}" -f "${PACKAGE}/validate_accounting_iter005.jq" "${ACCOUNTING}" >/dev/null || { echo iter005_accounting_semantic_failure >&2; exit 2; }
config_sha=$(sha256sum "${PACKAGE}/iter005_config.json" | awk '{print $1}')
checksum_sha=$(sha256sum "${PACKAGE}/execution_files.sha256" | awk '{print $1}')
execution_sha=$(sha256sum "${PACKAGE}/execution_manifest.json" | awk '{print $1}')
accounting_sha=$(sha256sum "${ACCOUNTING}" | awk '{print $1}')
review_sha=$(sha256sum "${RESULT_REVIEW}" | awk '{print $1}')
[[ "$(jq -r '.config_sha256' "${PACKAGE}/execution_manifest.json")" == "${config_sha}" ]] || { echo config_manifest_mismatch >&2; exit 2; }
[[ "$(jq -r '.execution_checksum_manifest_sha256' "${PACKAGE}/execution_manifest.json")" == "${checksum_sha}" ]] || { echo checksum_manifest_mismatch >&2; exit 2; }
[[ "$(rg -c '^iter005,' "${REGISTRY}")" == 1 ]] || { echo registry_row_count_mismatch >&2; exit 2; }
for path in "${REPORT}" "${SUMMARY}" "${REGISTRY}" "${CUMULATIVE}" "${HANDOFF}"; do
  for token in "${decision}" "${PLAN_SHA}" "${RUNTIME_ROOT}"; do
    rg -Fq "${token}" "${path}" || { echo "record mismatch: ${path}: ${token}" >&2; exit 2; }
  done
done
for path in "${REPORT}" "${SUMMARY}" "${HANDOFF}"; do
  for token in "${config_sha}" "${checksum_sha}" "${execution_sha}" "${diagnostics_sha}" "${accounting_sha}" "${review_sha}"; do
    rg -Fq "${token}" "${path}" || { echo "evidence mismatch: ${path}: ${token}" >&2; exit 2; }
  done
done
rg -Fq 'Status: `completed`' "${REPORT}" || { echo report_status_mismatch >&2; exit 2; }
rg -Fq 'Current status: `closed`' "${HANDOFF}" || { echo handoff_status_mismatch >&2; exit 2; }
rg -Fq 'Active jobs: none' "${HANDOFF}" || { echo active_jobs_record_mismatch >&2; exit 2; }
git diff --check
echo ITER005_FOUR_RECORD_VALIDATE_PASS
