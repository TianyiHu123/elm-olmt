#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="/xdisk/chopinsong/tianyihu/elm-olmt"
readonly REPORT="${REPO_ROOT}/development/three_stage_surrogate/iterations/iter016.md"
readonly SUMMARY="${REPO_ROOT}/development/three_stage_surrogate/summaries/iter016/summary.md"
readonly CUMULATIVE="${REPO_ROOT}/development/three_stage_surrogate/ITERATION_SUMMARY.md"
readonly REGISTRY="${REPO_ROOT}/development/three_stage_surrogate/registry.csv"
readonly HANDOFF="${REPO_ROOT}/development/three_stage_surrogate/handoff/CURRENT.md"
readonly EVIDENCE="${REPO_ROOT}/development/three_stage_surrogate/summaries/iter016"
readonly OUTPUT_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter016_abby_jerc_frozen_release_fixed_test"
readonly STAGING="${OUTPUT_ROOT}/staging/three_stage_abby_jerc/release_0001"
readonly STABLE_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc"
readonly STABLE="${STABLE_ROOT}/release_0001"

cd "${REPO_ROOT}"
git diff --check
git diff --exit-code -- development/three_stage_surrogate/PLAN.md >/dev/null

for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done

grep -Fq -- '- Status: `completed`' "${REPORT}"
grep -Fq -- '- Phase: `closeout`' "${REPORT}"
grep -Fq -- '- Closed: `2026-11-20T15:31:57-07:00`' "${REPORT}"
grep -Fq -- '- Overall acceptance result: `pass`' "${REPORT}"
grep -Fq -- '`coupled_release_published`' "${REPORT}"
grep -Fq -- 'Iter016 is terminal. No later iteration is proposed or authorized.' "${REPORT}"
grep -Fq -- '128,246 negative fixed-test values out of 25,141,200' "${REPORT}"
for job in 24725402 24725445 24729103 24729214 24729323 24740188; do
  grep -Fq "${job}" "${REPORT}"
done

grep -Fq -- '- Result: `pass`; decision `coupled_release_published`.' "${SUMMARY}"
grep -Fq -- '`4bdc91e2...543a`; catalog `89a636b9...85da`' "${SUMMARY}"
grep -Fq -- 'Iter016 is terminal.' "${SUMMARY}"
grep -Fq -- '## iter016 - frozen all-development coupled release and fixed test' "${CUMULATIVE}"
grep -Fq -- 'Decision: `coupled_release_published`' "${CUMULATIVE}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = "14"
[[ "${REGISTRY_ROW}" == iter016,2026-11-20T15:31:57-07:00,completed,release,* ]]
grep -Fq 'coupled_release_published' <<<"${REGISTRY_ROW}"
grep -Fq 'expected_parent=f2361316185979af41c6758100d98ee78d5157dd' <<<"${REGISTRY_ROW}"
grep -Fq 'expected_subject=Publish coupled three-stage surrogate release' <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter016.sh' <<<"${REGISTRY_ROW}"

grep -Fq -- '- Active iteration: none; latest closed iteration is `iter016`' "${HANDOFF}"
grep -Fq -- '- Status: `completed`' "${HANDOFF}"
grep -Fq -- '- Decision: `coupled_release_published`' "${HANDOFF}"
grep -Fq -- '- Active job scope: none' "${HANDOFF}"
grep -Fq -- '- Active monitoring: none' "${HANDOFF}"
grep -Fq -- 'No next iteration is proposed or authorized.' "${HANDOFF}"

sha256sum -c <<'EOF'
2f12645c54997ba9bcd40fdfd75bbab46b2dc4b2451287a184c4a4cf32abc1ba  development/three_stage_surrogate/summaries/iter016/cn_metrics.csv
18a05fa01878d6b34f13e13e87ddbdd507d86f5fa252111b092b9981468497f8  development/three_stage_surrogate/summaries/iter016/final_publication_report.json
abb6dd67e19dc5a68691131f839cbf753781596459a5548d01b70fd7c0f850d4  development/three_stage_surrogate/summaries/iter016/fixed_test_report.json
8d2857ab42bb60be0853e80d19ac709f8936e87ef9eebe1b80700cd90d3cf15e  development/three_stage_surrogate/summaries/iter016/flux_metrics.csv
b1bcf8c8514e30fae585aba60fb32942b2a789569a201539b3d4839b9a52255a  development/three_stage_surrogate/summaries/iter016/gpp_gate_diagnostics.csv
99a2c75e299c56ffc02451e575cbe4759adc7ff2a6856c65cf3f6cbcfb9651f8  development/three_stage_surrogate/summaries/iter016/gpp_sr_correlations.csv
89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da  development/three_stage_surrogate/summaries/iter016/published_catalog.json
4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a  development/three_stage_surrogate/summaries/iter016/published_release_manifest.json
EOF

test "$(sha256sum "${STABLE}/release_manifest.json" | cut -d' ' -f1)" = "4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a"
test "$(sha256sum "${STABLE_ROOT}/catalog.json" | cut -d' ' -f1)" = "89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da"
test "$(jq -r '.result' "${STABLE}/release_manifest.json")" = "validated"
test "$(jq -r '.files | length' "${STABLE}/release_manifest.json")" = "26"
test "$(jq -r '.current_manifest_sha256' "${STABLE_ROOT}/catalog.json")" = "4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a"
diff -qr "${STAGING}" "${STABLE}" >/dev/null
while IFS=$'\t' read -r relative expected size; do
  test "$(sha256sum "${STABLE}/${relative}" | cut -d' ' -f1)" = "${expected}"
  test "$(stat -c %s "${STABLE}/${relative}")" = "${size}"
done < <(jq -r '.files[] | [.path,.sha256,(.size_bytes|tostring)] | @tsv' "${STABLE}/release_manifest.json")

test "$(sha256sum /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc/release_0001/release_manifest.json | cut -d' ' -f1)" = "69f840f7972d640e91b1693c2fcf71b984dae2e20fee9a07f05434af0591f2dc"
test "$(sha256sum /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/release_0001/release_manifest.json | cut -d' ' -f1)" = "57cc18b063ab46a4cd07a3bd4e03ab1bfd05fb81894b097277d3c667135370d1"
test "$(sha256sum /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/sr_abby_jerc/release_0001/release_manifest.json | cut -d' ' -f1)" = "3a3d3faf8ffd1aba5af1c842732e26a25470cfa320742e0b38ff7daf5f1aed4c"

test -z "$(/usr/bin/squeue --jobs=24725402,24725445,24729103,24729214,24729323,24740188 -h -o '%i')"
readonly ACCOUNTING="$(/usr/bin/sacct --jobs=24725402,24725445,24729103,24729214,24729323,24740188 --starttime=2026-11-19T00:00:00 --parsable2 --noheader --format=JobIDRaw,State,ExitCode)"
for job in 24725402 24729103 24729214 24729323 24740188; do
  grep -Eq "^${job}\|COMPLETED\|0:0\|?$" <<<"${ACCOUNTING}"
done
grep -Eq '^24725445\|FAILED\|1:0\|?$' <<<"${ACCOUNTING}"

echo "ITER016_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=coupled_release_published active_jobs=0 release=release_0001 files=26"
