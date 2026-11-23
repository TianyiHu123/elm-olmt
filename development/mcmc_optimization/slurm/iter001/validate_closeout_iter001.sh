#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly CAMPAIGN="${REPO_ROOT}/development/mcmc_optimization"
readonly REPORT="${CAMPAIGN}/iterations/iter001.md"
readonly SUMMARY="${CAMPAIGN}/summaries/iter001/summary.md"
readonly CUMULATIVE="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly EXTERNAL=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight
readonly JOBS=24759169,24759238,24773888,24773889,24773997,24774027,24774088

cd "${REPO_ROOT}"
git diff --check
git diff --exit-code -- development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md >/dev/null
test "$(sha256sum development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md | cut -d' ' -f1)" = "46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6"
sha256sum --check development/mcmc_optimization/slurm/iter001/execution_files.sha256 >/dev/null

for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done

grep -Fq -- '- Status: `completed`' "${REPORT}"
grep -Fq -- '- Phase: `closeout`' "${REPORT}"
grep -Fq -- '- Closed: `2026-11-23T00:56:47-07:00`' "${REPORT}"
grep -Fq -- 'all seven gates `pass`' "${REPORT}"
grep -Fq -- '`continue_existing_inference_path`' "${REPORT}"
grep -Fq -- 'No next iteration is proposed or authorized.' "${REPORT}"

grep -Fq -- 'all seven acceptance gates pass' "${SUMMARY}"
grep -Fq -- '`continue_existing_inference_path`' "${SUMMARY}"
grep -Fq -- 'No next iteration is proposed or authorized.' "${SUMMARY}"
grep -Fq -- '## iter001 - Dual-Prior Contract and Coupled Inference Preflight' "${CUMULATIVE}"
grep -Fq -- '`continue_existing_inference_path`' "${CUMULATIVE}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = 14
[[ "${REGISTRY_ROW}" == iter001,2026-11-23T00:56:47-07:00,completed,* ]]
grep -Fq 'continue_existing_inference_path' <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter001.sh' <<<"${REGISTRY_ROW}"

grep -Fq -- '- Current status: `completed`' "${HANDOFF}"
grep -Fq -- '- Current phase: `closed`' "${HANDOFF}"
grep -Fq -- '- Active iteration: none; latest closed iteration is `iter001`' "${HANDOFF}"
grep -Fq -- '- Active jobs: none' "${HANDOFF}"
grep -Fq -- 'decision `continue_existing_inference_path`' "${HANDOFF}"
grep -Fq -- 'No next iteration is proposed or authorized.' "${HANDOFF}"

test "$(sha256sum development/mcmc_optimization/summaries/iter001/benchmark_decision.json | cut -d' ' -f1)" = "705fe383a5f341074fbbe278c442fe18a363331e8011c0a9e5b3277176cd53fe"
test "$(sha256sum development/mcmc_optimization/summaries/iter001/final_report.json | cut -d' ' -f1)" = "4526f8b51cce31a58318e598c1eeb8f0255c183c03116490e92e58cc8c7c4e93"
cmp development/mcmc_optimization/summaries/iter001/benchmark_decision.json "${EXTERNAL}/results/benchmark/decision.json"
cmp development/mcmc_optimization/summaries/iter001/final_report.json "${EXTERNAL}/results/final_report.json"
test "$(sha256sum "${EXTERNAL}/results/prior/prior_report.json" | cut -d' ' -f1)" = "29bd1e2fc24839c09a6b76b0255ab4971f8e60d507e37875149ad05c4a8c5c3b"
test "$(sha256sum "${EXTERNAL}/results/interface/interface_report.json" | cut -d' ' -f1)" = "7fc10ed58aadf99230e0def97e35d29279099f8b5bf9b0afa5e0846cf39fe253"
test "$(sha256sum "${EXTERNAL}/results/benchmark/benchmark_report.json" | cut -d' ' -f1)" = "f7f150687c0352c09c12043526c640789937f542ca8b6d62a11746d44f072176"

test -z "$(/usr/bin/squeue --jobs="${JOBS}" -h -o '%i')"
readonly ACCOUNTING="$(/usr/bin/sacct --jobs="${JOBS}" --starttime=2026-11-21T00:00:00 --parsable2 --noheader --format=JobIDRaw,State,ExitCode)"
for job in 24759238 24773889 24773997 24774027 24774088; do
  grep -Eq "^${job}\|COMPLETED\|0:0\|?$" <<<"${ACCOUNTING}"
done
for job in 24759169 24773888; do
  grep -Eq "^${job}\|FAILED\|1:0\|?$" <<<"${ACCOUNTING}"
done

echo "ITER001_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=continue_existing_inference_path recommendation=A active_jobs=0"
