#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly CAMPAIGN=${REPO_ROOT}/development/mcmc_optimization
readonly REPORT=${CAMPAIGN}/iterations/iter003.md
readonly SUMMARY=${CAMPAIGN}/summaries/iter003/summary.md
readonly CUMULATIVE=${CAMPAIGN}/ITERATION_SUMMARY.md
readonly REGISTRY=${CAMPAIGN}/registry.csv
readonly HANDOFF=${CAMPAIGN}/handoff/CURRENT.md
readonly RUNTIME=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior
readonly JOBS=24811598,24811617,24811658,24811705,24811719,24811738,24812674,24812698
readonly PLAN_SHA=b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab
readonly CONFIG_SHA=0038e424d5c65f8a6ddcec78a79af2c164fa63e0776d44a7ff8badc6e5c68bcc
readonly CHECKSUM_SHA=492ad4fb4380e8c3d85b23073be574b2c5b23a232c7a49bfcc271851fb46032d
readonly EXECUTION_SHA=0b5f651336e30098a2b1c58d60e1d617f38ddfc2efa587d12bc7c68ba3882ba4

cd "${REPO_ROOT}"
git diff --check
git diff --exit-code -- development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md >/dev/null
test "$(sha256sum development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md | cut -d' ' -f1)" = "${PLAN_SHA}"
sha256sum --check development/mcmc_optimization/slurm/iter003/execution_files.sha256 >/dev/null
test "$(sha256sum development/mcmc_optimization/slurm/iter003/iter003_config.json | cut -d' ' -f1)" = "${CONFIG_SHA}"
test "$(sha256sum development/mcmc_optimization/slurm/iter003/execution_files.sha256 | cut -d' ' -f1)" = "${CHECKSUM_SHA}"
test "$(sha256sum development/mcmc_optimization/slurm/iter003/execution_manifest.json | cut -d' ' -f1)" = "${EXECUTION_SHA}"

for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done

grep -Fq -- '- Status: `completed`' "${REPORT}"
grep -Fq -- '- Phase: `closeout`' "${REPORT}"
grep -Fq -- '- Closed: `2026-11-25T03:24:53-07:00`' "${REPORT}"
grep -Fq -- 'all ten gates `pass`' "${REPORT}"
grep -Fq -- '`four_observable_posterior_validated`' "${REPORT}"
grep -Fq -- 'Initial Candidate Search and MCMC Pilot Planning' "${REPORT}"
grep -Fq -- 'Missing `pytest`' "${REPORT}"
grep -Fq -- 'Remove PPE-Specific Three-Stage Surrogate Loader' "${REPORT}"

grep -Fq -- 'all ten gates pass' "${SUMMARY}"
grep -Fq -- '`four_observable_posterior_validated`' "${SUMMARY}"
grep -Fq -- 'Initial Candidate Search and MCMC Pilot Planning' "${SUMMARY}"
grep -Fq -- '## iter003 - Complete Four-Observable Posterior Adapter and Validation' "${CUMULATIVE}"
grep -Fq -- '`four_observable_posterior_validated`' "${CUMULATIVE}"
grep -Fq -- 'Initial Candidate Search and MCMC Pilot Planning' "${CUMULATIVE}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = 14
[[ "${REGISTRY_ROW}" == iter003,2026-11-25T03:24:53-07:00,completed,* ]]
grep -Fq 'four_observable_posterior_validated' <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter003.sh' <<<"${REGISTRY_ROW}"

grep -Fq -- '- Current status: `closed`.' "${HANDOFF}"
grep -Fq -- '- Current phase: `closed`.' "${HANDOFF}"
grep -Fq -- '- Last completed iteration: `iter003`.' "${HANDOFF}"
grep -Fq -- '- Active iteration: none.' "${HANDOFF}"
grep -Fq -- '- Active jobs: none;' "${HANDOFF}"
grep -Fq -- 'Decision: `four_observable_posterior_validated`' "${HANDOFF}"
grep -Fq -- 'Initial Candidate Search and MCMC Pilot Planning' "${HANDOFF}"
grep -Fq -- 'Missing `pytest`' "${HANDOFF}"
grep -Fq -- 'Remove PPE-Specific Three-Stage Surrogate Loader' "${HANDOFF}"

test "$(jq -r '.result' "${RUNTIME}/results/final_validation.json")" = pass
test "$(jq -r '.decision_candidate' "${RUNTIME}/results/final_validation.json")" = four_observable_posterior_validated
test "$(jq -r '.gates_1_through_9_pass' "${RUNTIME}/results/final_validation.json")" = true
test "$(jq -r '.reference_case_count' "${RUNTIME}/results/posterior_validation.json")" = 14
test "$(jq -r '.cases | length' "${RUNTIME}/results/likelihood_reference_tests.json")" = 14
test "$(jq '[.cases[] | select(.kind == "joint_cn")] | length' "${RUNTIME}/results/likelihood_reference_tests.json")" = 6
test "$(jq -r '.outcome' "${RUNTIME}/reviews/package_review.json")" = pass
test "$(jq -r '.outcome' "${RUNTIME}/reviews/result_review.json")" = pass
test "$(jq -r '.active_or_unaccounted' "${RUNTIME}/manifests/final_job_accounting.json")" = 0
test "$(jq -r '.attempts | length' "${RUNTIME}/manifests/final_job_accounting.json")" = 8
test "$(jq -r '.shared_retries_consumed' "${RUNTIME}/manifests/final_job_accounting.json")" = 0

test -z "$(/usr/bin/squeue --jobs="${JOBS}" -h -o '%i')"
readonly ACCOUNTING="$(/usr/bin/sacct --jobs="${JOBS}" --starttime=2026-11-24T00:00:00 --parsable2 --noheader --format=JobIDRaw,State,ExitCode)"
for job in 24811617 24811705 24811719 24811738 24812674 24812698; do
  grep -Eq "^${job}\|COMPLETED\|0:0\|?$" <<<"${ACCOUNTING}"
done
for job in 24811598 24811658; do
  grep -Eq "^${job}\|FAILED\|1:0\|?$" <<<"${ACCOUNTING}"
done

echo "ITER003_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=four_observable_posterior_validated active_jobs=0"
