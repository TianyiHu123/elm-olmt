#!/usr/bin/env bash
# Static/text closeout reconciliation after the continuation F job is terminal.
set -euo pipefail
readonly REPO=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly BASE=${REPO}/development/mcmc_optimization
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics
readonly PLAN_SHA=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0
readonly POINTER_SHA=b991f8ce81903270a5dadf7b987e982e3886f316facd8eadecbf8d776514f7ee
readonly F_JOB=${1:?pass the recorded continuation F job ID}
[[ "${F_JOB}" =~ ^[0-9]+$ ]]
cd "${REPO}"
test "$(git branch --show-current)" = feature/mcmc-optimization
test "$(git rev-parse HEAD)" = 9f81aa9d2065339c59d86f5933231b89b7b9df2a
test "$(sha256sum "${BASE}/MCMC_OPTIMIZATION_PLAN.md" | cut -d ' ' -f1)" = "${PLAN_SHA}"
test "$(sha256sum "${ROOT}/validation/approved_c_gate.json" | cut -d ' ' -f1)" = "${POINTER_SHA}"
sha256sum -c "${ROOT}/submitted/f/attempt_002/source.sha256" >/dev/null
sha256sum -c "${ROOT}/submitted/f/attempt_002/package.sha256" >/dev/null

readonly F_RESULT=${ROOT}/diagnostics/attempt_002/final_validation.json
readonly ALL_ACCOUNT=${ROOT}/accounting/final_all_iter006_jobs.psv
test "$(jq -r '.result' "${F_RESULT}")" = pass
test "$(jq -r '.pre_f_hard_gates_passed' "${F_RESULT}")" = true
test "$(jq -r '.terminal_f_and_four_record_gates_pending' "${F_RESULT}")" = true
test "$(jq -r '.approved_c_gate_sha256' "${F_RESULT}")" = "${POINTER_SHA}"
readonly DECISION=$(jq -r '.decision_candidate' "${F_RESULT}")
case "${DECISION}" in
  bounded_sampler_pilot_validated|bounded_sampler_pilot_validated_with_mixing_limitations) ;;
  *) echo "invalid final decision candidate: ${DECISION}" >&2; exit 1 ;;
esac

for job in 24840516 24840555 24840587 24840823 24840903 24841160 24847546; do
  rg -q "^${job}[|].*[|]FAILED[|]1:0[|]" "${ALL_ACCOUNT}"
  rg -q "^${job}[.]batch[|].*[|]FAILED[|]1:0[|]" "${ALL_ACCOUNT}"
  rg -q "^${job}[.]extern[|].*[|]COMPLETED[|]0:0[|]" "${ALL_ACCOUNT}"
done
for job in 24841071 24847731 24847977 24847981 "${F_JOB}"; do
  for suffix in '' .batch .extern; do
    rg -q "^${job}${suffix//./[.]}[|].*[|]COMPLETED[|]0:0[|]" "${ALL_ACCOUNT}"
  done
done
test "$(rg -c '^[0-9]+[|]' "${ALL_ACCOUNT}")" = 12
gawk -F'|' -v allowed="24840516,24840555,24840587,24840823,24840903,24841071,24841160,24847546,24847731,24847977,24847981,${F_JOB}" '
  BEGIN {
    n=split(allowed, ids, ","); for (i=1; i<=n; i++) known[ids[i]]=1
    split("24840516,24840555,24840587,24840823,24840903,24841160,24847546", failed, ",")
    for (i in failed) expected_failed[failed[i]]=1
  }
  {
    split($1, parts, /[.]/); base=parts[1]
    if (!(base in known) || NF < 5 || seen[$1]++) bad=1
    if ($3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL)$/) bad=1
    if (!(base in expected_failed) && ($3 != "COMPLETED" || $4 != "0:0")) bad=1
    if (base in expected_failed && parts[2] !~ /^(|batch|extern)$/ &&
        $3 !~ /^(COMPLETED|FAILED)$/) bad=1
  }
  END { if (NR < 36 || bad) exit 1 }
' "${ALL_ACCOUNT}"
readonly F_ACCOUNT=${ROOT}/accounting/f_attempt_002_${F_JOB}.psv
test -s "${F_ACCOUNT}"
for suffix in '' .batch .extern; do
  rg -q "^${F_JOB}${suffix//./[.]}[|].*[|]COMPLETED[|]0:0[|]" "${F_ACCOUNT}"
done
while IFS= read -r line; do
  test -n "${line}" || continue
  rg -Fqx -- "${line}" "${ALL_ACCOUNT}"
done < "${F_ACCOUNT}"
rg -Fq 'ITER006_CONTINUATION_EVIDENCE_PASS' "${ROOT}/logs/f2_${F_JOB}.out"

test "$(jq -r '.classification' "${ROOT}/replay/fatal_attribution.json")" = exact_replay_reproduced
test "$(jq -r '.partial_step_3.generated' "${ROOT}/diagnostics/attempt_002/legacy_replay/boundary_diagnostics.json")" = 16
test "$(jq -r '.partial_step_3.failed' "${ROOT}/diagnostics/attempt_002/legacy_replay/boundary_diagnostics.json")" = 1
test "$(jq -r '.partial_step_3.unexamined' "${ROOT}/diagnostics/attempt_002/legacy_replay/boundary_diagnostics.json")" = 15
for site in ABBY JERC; do
  SITE_REPORT=${ROOT}/chains/${site}/pilot_report.json
  SITE_DIAG=${ROOT}/diagnostics/attempt_002/${site}/pilot
  test "$(jq -r '.result' "${SITE_REPORT}")" = pass
  test "$(jq -r '.iteration' "${SITE_REPORT}")" = 128
  test "$(jq -r '.nwalkers' "${SITE_REPORT}")" = 64
  test "$(jq -r '.convergence' "${SITE_REPORT}")" = unassessed
  test "$(jq -r '.overall_counts.generated' "${SITE_DIAG}/boundary_diagnostics.json")" = 8192
  test "$(jq -r '.overall_counts.completed' "${SITE_DIAG}/boundary_diagnostics.json")" = 8192
  test "$(jq -r '.overall_counts.failed' "${SITE_DIAG}/boundary_diagnostics.json")" = 0
  test "$(jq -r '.overall_counts.unexamined' "${SITE_DIAG}/boundary_diagnostics.json")" = 0
  test "$(wc -l < "${SITE_DIAG}/boundary_counts_by_step.csv")" = 130
  test "$(wc -l < "${SITE_DIAG}/boundary_counts_by_block.csv")" = 9
  test -s "${SITE_DIAG}/boundary_counts_by_group.csv"
  test -s "${SITE_DIAG}/boundary_history.png"
  for role in restart_uninterrupted restart_split; do
    test "$(wc -l < "${ROOT}/diagnostics/attempt_002/${site}/${role}/boundary_counts_by_step.csv")" = 18
  done
done

test "$(rg -c '^iter006,' "${BASE}/registry.csv")" = 1
test "$(head -n1 "${BASE}/registry.csv")" = "$(git show HEAD:development/mcmc_optimization/registry.csv | head -n1)"
gawk -v decision="${DECISION}" '
  BEGIN { FPAT = "(\"([^\"]|\"\")*\")|([^,]+)" }
  NR==1 { if (NF != 14 || $1 != "iteration_id" || $3 != "status" || $7 != "acceptance_result" || $8 != "decision") exit 1 }
  $1=="iter006" { seen++; if (NF != 14 || $3 != "completed" || $7 != "pass" || $8 != decision) exit 1 }
  END { if (seen != 1) exit 1 }
' "${BASE}/registry.csv"
for record in \
  "${BASE}/iterations/iter006.md" \
  "${BASE}/registry.csv" \
  "${BASE}/ITERATION_SUMMARY.md" \
  "${BASE}/handoff/CURRENT.md"; do
  for token in "${DECISION}" "${PLAN_SHA}" "${ROOT}"; do
    rg -Fq "${token}" "${record}"
  done
done
rg -Fq "**Final decision:** \`${DECISION}\`" "${BASE}/iterations/iter006.md"
rg -Fq "Reopened Iter006 final decision: \`${DECISION}\`; acceptance \`pass\`." "${BASE}/ITERATION_SUMMARY.md"
rg -Fq "Current final decision: \`${DECISION}\`." "${BASE}/handoff/CURRENT.md"
rg -Fq "Final decision: \`${DECISION}\`; acceptance \`pass\`." "${BASE}/summaries/iter006/summary.md"
rg -Fq 'Current status: `closed`' "${BASE}/handoff/CURRENT.md"
rg -Fq 'Active Iter006 job: none' "${BASE}/handoff/CURRENT.md"
for record in "${BASE}/iterations/iter006.md" "${BASE}/summaries/iter006/summary.md" "${BASE}/handoff/CURRENT.md"; do
  rg -iq 'convergence.*unassessed' "${record}"
done
test "$(du -sb "${ROOT}" | cut -f1)" -le 2147483648
git diff --check
echo ITER006_CONTINUATION_FOUR_RECORD_VALIDATE_PASS
