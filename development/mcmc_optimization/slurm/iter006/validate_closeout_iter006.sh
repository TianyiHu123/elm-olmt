#!/usr/bin/env bash
# Static/text reconciliation after Stage F has terminal accounting.
set -euo pipefail
readonly REPO=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly BASE=${REPO}/development/mcmc_optimization
readonly ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics
readonly PLAN_SHA=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0
readonly DECISION=iter006_validation_failed
cd "${REPO}"
test "$(git branch --show-current)" = feature/mcmc-optimization
test "$(git rev-parse HEAD)" = b99bd8be53265e37df171c430495a5258f6f57e3
test "$(sha256sum "${BASE}/MCMC_OPTIMIZATION_PLAN.md" | cut -d ' ' -f 1)" = "${PLAN_SHA}"
sha256sum -c "${ROOT}/submitted/f/attempt_001/f_source.sha256" >/dev/null
sha256sum -c "${ROOT}/submitted/f/attempt_001/f_package.sha256" >/dev/null
test ! -e "${ROOT}/validation/final_available_evidence.json"
rg -Fq 'RuntimeError: pilot backend exists after blocked gate' "${ROOT}/logs/f_24840903.err"
rg -Fq 'stage_f job=24840903' "${ROOT}/logs/f_24840903.out"
test "$(jq -r '.classification' "${ROOT}/replay/fatal_attribution.json")" = exact_replay_reproduced
test "$(jq -r '.result' "${ROOT}/validation/numerical_validation.json")" = pass
test "$(rg -c '^iter006,' "${BASE}/registry.csv")" = 1
test "$(head -n 1 "${BASE}/registry.csv")" = "$(git show HEAD:development/mcmc_optimization/registry.csv | head -n 1)"
for job in 24840516 24840555 24840587 24840823 24840903; do
  rg -q "^${job}[|]" "${ROOT}/accounting/final_iter006_jobs.psv"
done
test "$(rg -c '^[0-9]+[|]' "${ROOT}/accounting/final_iter006_jobs.psv")" = 5
test "$(rg -c '^[0-9]+[|].*[|]FAILED[|]1:0[|]' "${ROOT}/accounting/final_iter006_jobs.psv")" = 5
test -z "$(find "${ROOT}/chains" -type f -name '*.h5' -print -quit)"
for record in \
  "${BASE}/iterations/iter006.md" \
  "${BASE}/registry.csv" \
  "${BASE}/ITERATION_SUMMARY.md" \
  "${BASE}/handoff/CURRENT.md"; do
  for token in "${DECISION}" "${PLAN_SHA}" "${ROOT}"; do
    rg -Fq "${token}" "${record}"
  done
done
for record in "${BASE}/iterations/iter006.md" "${BASE}/summaries/iter006/summary.md" "${BASE}/handoff/CURRENT.md"; do
  for token in 24840516 24840555 24840587 24840823 24840903; do
    rg -Fq "${token}" "${record}"
  done
  rg -iq 'no convergence|convergence.*unassessed' "${record}"
done
rg -Fq 'status `completed`' "${BASE}/iterations/iter006.md"
rg -Fq 'Current status: `closed`' "${BASE}/handoff/CURRENT.md"
rg -Fq 'Active Iter006 job: none' "${BASE}/handoff/CURRENT.md"
test "$(du -sb "${ROOT}" | cut -f 1)" -le 2147483648
git diff --check
echo ITER006_FOUR_RECORD_VALIDATE_PASS
