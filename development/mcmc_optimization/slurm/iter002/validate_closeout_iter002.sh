#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly CAMPAIGN="${REPO_ROOT}/development/mcmc_optimization"
readonly REPORT="${CAMPAIGN}/iterations/iter002.md"
readonly SUMMARY="${CAMPAIGN}/summaries/iter002/summary.md"
readonly CUMULATIVE="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly RELEASE=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001
readonly RUNTIME=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter002_neon_observation_preparation
readonly JOBS=24794462,24794655,24794902,24794997,24795247,24795589,24795706,24795812,24795941,24796001,24797797,24797845
readonly PLAN_SHA=b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab
readonly CATALOG_SHA=cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8
readonly MANIFEST_SHA=460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2
readonly VALIDATION_SHA=19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef

cd "${REPO_ROOT}"
git diff --check
git diff --exit-code -- development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md >/dev/null
test "$(sha256sum development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md | cut -d' ' -f1)" = "${PLAN_SHA}"
sha256sum --check development/mcmc_optimization/slurm/iter002/execution_files.sha256 >/dev/null

for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done

grep -Fq -- '- Status: `completed`' "${REPORT}"
grep -Fq -- '- Phase: `closeout`' "${REPORT}"
grep -Fq -- '- Closed: `2026-11-24T04:26:44-07:00`' "${REPORT}"
grep -Fq -- 'all nine gates `pass`' "${REPORT}"
grep -Fq -- 'Decision: `observation_release_0001_published`' "${REPORT}"
grep -Fq -- 'Complete Four-Observable Posterior Adapter and Validation' "${REPORT}"

grep -Fq -- 'All nine acceptance gates pass' "${SUMMARY}"
grep -Fq -- '`observation_release_0001_published`' "${SUMMARY}"
grep -Fq -- 'Complete Four-Observable Posterior Adapter and' "${SUMMARY}"
grep -Fq -- '## iter002 - NEON Observation Preparation and Fixed-Uncertainty Release' "${CUMULATIVE}"
grep -Fq -- '`observation_release_0001_published`' "${CUMULATIVE}"
grep -Fq -- 'Complete Four-Observable Posterior Adapter and' "${CUMULATIVE}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = 14
[[ "${REGISTRY_ROW}" == iter002,2026-11-24T04:26:44-07:00,completed,* ]]
grep -Fq 'observation_release_0001_published' <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter002.sh' <<<"${REGISTRY_ROW}"

grep -Fq -- '- Current status: `closed`' "${HANDOFF}"
grep -Fq -- '- Current phase: `closed`' "${HANDOFF}"
grep -Fq -- '- Last completed iteration: `iter002`' "${HANDOFF}"
grep -Fq -- '- Active iteration: none' "${HANDOFF}"
grep -Fq -- '- Active jobs: none' "${HANDOFF}"
grep -Fq -- 'Decision: `observation_release_0001_published`' "${HANDOFF}"
grep -Fq -- 'Complete Four-Observable Posterior Adapter and Validation' "${HANDOFF}"

test "$(sha256sum "${RELEASE}/catalog.json" | cut -d' ' -f1)" = "${CATALOG_SHA}"
test "$(sha256sum "${RELEASE}/release_manifest.json" | cut -d' ' -f1)" = "${MANIFEST_SHA}"
test "$(sha256sum "${RELEASE}/validation_report.json" | cut -d' ' -f1)" = "${VALIDATION_SHA}"
test "$(jq -r '.release_manifest_sha256' "${RELEASE}/catalog.json")" = "${MANIFEST_SHA}"
test "$(jq -r '.decision' "${RELEASE}/catalog.json")" = observation_release_0001_published
test "$(jq -r '.files | length' "${RELEASE}/release_manifest.json")" = 18
test "$(jq -r '.source_identities | length' "${RELEASE}/release_manifest.json")" = 19
test "$(jq -r '.catalog_last' "${RELEASE}/release_manifest.json")" = true
test "$(jq -r '.iter015_fixed_test_access' "${RELEASE}/release_manifest.json")" = false
test "$(jq -r '.result' "${RUNTIME}/results/final_validation.json")" = pass
test "$(jq -r '.decision' "${RUNTIME}/results/final_validation.json")" = observation_release_0001_published
test "$(jq -r '.validated_product_count' "${RUNTIME}/results/final_validation.json")" = 18

test -z "$(/usr/bin/squeue --jobs="${JOBS}" -h -o '%i')"
readonly ACCOUNTING="$(/usr/bin/sacct --jobs="${JOBS}" --starttime=2026-11-23T00:00:00 --parsable2 --noheader --format=JobIDRaw,State,ExitCode)"
for job in 24794902 24795589 24795706 24795812 24797797 24797845; do
  grep -Eq "^${job}\|COMPLETED\|0:0\|?$" <<<"${ACCOUNTING}"
done
for job in 24794655 24794997 24795247 24795941 24796001; do
  grep -Eq "^${job}\|FAILED\|1:0\|?$" <<<"${ACCOUNTING}"
done
grep -Eq '^24794462\|FAILED\|2:0\|?$' <<<"${ACCOUNTING}"

echo "ITER002_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=observation_release_0001_published active_jobs=0"
