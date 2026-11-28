#!/usr/bin/env bash
set -euo pipefail

readonly REPO=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly CAMPAIGN=${REPO}/development/mcmc_optimization
readonly RUNTIME=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter007_observation_release_0002
readonly RELEASE=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0002
readonly OLD=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001
readonly DECISION=observation_release_0002_published_and_dual_loader_validated
readonly PLAN_SHA=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0
readonly CATALOG_SHA=19bdc16534942d74595dfd1545fb20deff135005abc1a5287ab9e64bc1349027
readonly MANIFEST_SHA=46db205dffea320333666e9e5b237ae4ec8ed948077f55284f6931335191796e
readonly VALIDATION_SHA=d07c1fafaa366710940d4caf851f1ff07ca93f34ede06fad4d6010432ea69004
readonly INTEGRATION_SHA=193b469c1406777662f084d1163453f17a36f0ecdd77bbdffddf921515e1fde5
readonly ACCOUNTING_SHA=a3063e3b987cb4c5a565e981dfb57398f8910e7c8569084779db2114d8207e68

cd "${REPO}"
test "$(git branch --show-current)" = feature/mcmc-optimization
test "$(git rev-parse HEAD)" = 19bf509d6cb23c53c8cc58fb25682c89f3825597
git diff --check
git diff --exit-code -- development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md >/dev/null
test "$(sha256sum development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md | cut -d' ' -f1)" = "${PLAN_SHA}"
sha256sum -c "${RUNTIME}/manifests/source_files.sha256" >/dev/null

readonly REPORT=${CAMPAIGN}/iterations/iter007.md
readonly SUMMARY=${CAMPAIGN}/summaries/iter007/summary.md
readonly CUMULATIVE=${CAMPAIGN}/ITERATION_SUMMARY.md
readonly REGISTRY=${CAMPAIGN}/registry.csv
readonly HANDOFF=${CAMPAIGN}/handoff/CURRENT.md
for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done
grep -Fq 'status `completed`; phase `closeout`' "${REPORT}"
grep -Fq 'Closed `2026-11-28T02:00:39-07:00`' "${REPORT}"
grep -Fq "Decision: \`${DECISION}\`" "${REPORT}"
grep -Fq '## One planning-only next proposal' "${REPORT}"
grep -Fq 'Status `completed`' "${SUMMARY}"
grep -Fq "decision \`${DECISION}\`" "${SUMMARY}"
grep -Fq 'Planning-only next proposal:' "${SUMMARY}"
grep -Fq '## iter007 - observation release_0002 and configurable loading completed' "${CUMULATIVE}"
grep -Fq "decision \`${DECISION}\`" "${CUMULATIVE}"
grep -Fq 'Planning-only next proposal:' "${CUMULATIVE}"
grep -Fq -- '- Current status: `closed`.' "${HANDOFF}"
grep -Fq -- '- Current phase: `closed`.' "${HANDOFF}"
grep -Fq -- '- Last completed iteration: `iter007`' "${HANDOFF}"
grep -Fq -- '- Active iteration: none.' "${HANDOFF}"
grep -Fq -- '- Active Iter007 job: none.' "${HANDOFF}"
grep -Fq "${DECISION}" "${HANDOFF}"
grep -Fq 'Planning-only next proposal:' "${HANDOFF}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = 14
[[ "${REGISTRY_ROW}" == iter007,2026-11-28T02:00:39-07:00,completed,* ]]
grep -Fq "${DECISION}" <<<"${REGISTRY_ROW}"
grep -Fq 'development/mcmc_optimization/summaries/iter007/summary.md' <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter007.sh' <<<"${REGISTRY_ROW}"

test "$(sha256sum "${RELEASE}/catalog.json" | cut -d' ' -f1)" = "${CATALOG_SHA}"
test "$(sha256sum "${RELEASE}/release_manifest.json" | cut -d' ' -f1)" = "${MANIFEST_SHA}"
test "$(sha256sum "${RELEASE}/validation_report.json" | cut -d' ' -f1)" = "${VALIDATION_SHA}"
test "$(sha256sum "${OLD}/catalog.json" | cut -d' ' -f1)" = cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8
test "$(sha256sum "${OLD}/release_manifest.json" | cut -d' ' -f1)" = 460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2
test "$(sha256sum "${OLD}/validation_report.json" | cut -d' ' -f1)" = 19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef
test "$(jq -r '.release_manifest_sha256' "${RELEASE}/catalog.json")" = "${MANIFEST_SHA}"
test "$(jq -r '.decision' "${RELEASE}/catalog.json")" = observation_release_0002_published
test "$(jq -r '.files | length' "${RELEASE}/release_manifest.json")" = 27
test "$(jq -r '.catalog_last' "${RELEASE}/release_manifest.json")" = true
test "$(jq -r '.iter015_fixed_test_access' "${RELEASE}/release_manifest.json")" = false
while IFS=$'\t' read -r relative digest size; do
  test -f "${RELEASE}/${relative}"
  test "$(stat -c %s "${RELEASE}/${relative}")" = "${size}"
  test "$(sha256sum "${RELEASE}/${relative}" | cut -d' ' -f1)" = "${digest}"
done < <(jq -r '.files[] | [.path,.sha256,.size_bytes] | @tsv' "${RELEASE}/release_manifest.json")

test "$(jq -r '.result' "${RUNTIME}/results/staged_validation.json")" = pass
test "$(jq -r '.outcome' "${RUNTIME}/reviews/staged_review.json")" = pass
test "$(jq -r '.outcome' "${RUNTIME}/reviews/staged_review_attempt_001.json")" = block
test "$(jq -r '.result' "${RUNTIME}/results/publication.json")" = pass
test "$(jq -r '.result' "${RUNTIME}/results/final_reload.json")" = pass
test "$(jq -r '.outcome' "${RUNTIME}/reviews/integration_package_review.json")" = pass
test "$(jq -r '.outcome' "${RUNTIME}/reviews/integration_result_review.json")" = pass
test "$(sha256sum "${RUNTIME}/results/dual_release_integration.json" | cut -d' ' -f1)" = "${INTEGRATION_SHA}"
jq -e '(.result == "pass") and
  (.selections.release_0001.ABBY.GPP == 514) and (.selections.release_0001.ABBY.SR == 1095) and
  (.selections.release_0001.JERC.GPP == 699) and (.selections.release_0001.JERC.SR == 2114) and
  (.selections.release_0002.ABBY.GPP == 333) and (.selections.release_0002.ABBY.SR == 1083) and
  (.selections.release_0002.JERC.GPP == 463) and (.selections.release_0002.JERC.SR == 2046) and
  ((.rejections | length) == 8) and (([.rejections[] | select(. != "rejected")] | length) == 0)' \
  "${RUNTIME}/results/dual_release_integration.json" >/dev/null

readonly ACCOUNTING=${RUNTIME}/accounting/all_iter007_jobs.psv
test "$(sha256sum "${ACCOUNTING}" | cut -d' ' -f1)" = "${ACCOUNTING_SHA}"
test "$(wc -l < "${ACCOUNTING}")" = 33
for job in 24850270 24850330 24851156 24851282 24851366 24851404 24851454 24851497 24851532; do
  for suffix in '' '.batch' '.extern'; do
    awk -F'|' -v id="${job}${suffix}" '$1==id && $3=="COMPLETED" && $4=="0:0" {n++} END{exit n==1?0:1}' "${ACCOUNTING}"
  done
done
for job in 24850386 24851190; do
  for suffix in '' '.batch'; do
    awk -F'|' -v id="${job}${suffix}" '$1==id && $3=="FAILED" && $4=="1:0" {n++} END{exit n==1?0:1}' "${ACCOUNTING}"
  done
  awk -F'|' -v id="${job}.extern" '$1==id && $3=="COMPLETED" && $4=="0:0" {n++} END{exit n==1?0:1}' "${ACCOUNTING}"
done
test "$(du -sb "${RUNTIME}" | cut -f1)" -lt 2147483648
test "$(du -sb "${RELEASE}" | cut -f1)" -lt 104857600

echo "ITER007_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=${DECISION} jobs=11 terminal_rows=33 active_jobs=0"
