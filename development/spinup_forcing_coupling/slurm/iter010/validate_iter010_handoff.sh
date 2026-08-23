#!/usr/bin/env bash
set -euo pipefail

phase=""
expected_parent=""
expected_subject=""
active_job_count=""

while (( $# )); do
  case "$1" in
    --phase) phase="$2"; shift 2 ;;
    --expected-parent) expected_parent="$2"; shift 2 ;;
    --expected-subject) expected_subject="$2"; shift 2 ;;
    --active-job-count) active_job_count="$2"; shift 2 ;;
    *) printf 'VALIDATE_BLOCK: unknown argument %s\n' "$1" >&2; exit 2 ;;
  esac
done

if [[ "$phase" != "precommit" && "$phase" != "postcommit" ]]; then
  printf 'VALIDATE_BLOCK: --phase must be precommit or postcommit\n' >&2
  exit 2
fi
if [[ -z "$expected_parent" || -z "$expected_subject" || "$active_job_count" != "0" ]]; then
  printf 'VALIDATE_BLOCK: expected parent/subject and active-job-count=0 are required\n' >&2
  exit 2
fi

repo_root=$(git rev-parse --show-toplevel)
wf="$repo_root/development/spinup_forcing_coupling"
iteration="$wf/iterations/iter010.md"
current="$wf/handoff/CURRENT.md"
summary="$wf/ITERATION_SUMMARY.md"
registry="$wf/registry.csv"
report="$wf/summaries/iter010/ITER010_REPORT.md"
compact="$wf/summaries/iter010"
external="$repo_root/../E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_topology"

fail() {
  printf 'VALIDATE_BLOCK: %s\n' "$1" >&2
  exit 1
}

require_line() {
  local file=$1
  local line=$2
  grep -Fqx -- "$line" "$file" || fail "missing exact line in ${file#"$repo_root/"}: $line"
}

for file in "$iteration" "$current" "$summary" "$registry" "$report"; do
  [[ -s "$file" ]] || fail "missing or empty ${file#"$repo_root/"}"
done

id='iter010'
status='completed'
work_type='implementation'
objective='TIM terminal-partition topology diagnosis'
scope='Six immutable TIM chains; ABBY/JERC; seeds 9009-9011; terminal/rolling topology diagnostics; conditional prediction skip'
acceptance='pass'
decision='ABBY and JERC two_basin_declined; forced terminal screen declined as evidence for two physical basins; replace the screen, reassess TIM/JERC, and route to ABBY proposal-scale Experiment 5'
output_root='/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling'
summary_path='development/spinup_forcing_coupling/summaries/iter010'
next_state='Iter011 is not_initialized; its complete planning-only ABBY target-equivalent DE proposal-scale pilot is recorded in iterations/iter010.md and CURRENT.md, and execution requires a fresh consolidated kickoff package with explicit approval.'

for file in "$iteration" "$summary" "$report"; do
  require_line "$file" "- Iteration ID: \`$id\`"
done
require_line "$current" "- Active iteration: \`$id\`"
for file in "$iteration" "$current" "$summary" "$report"; do
  require_line "$file" "- Status: \`$status\`"
  require_line "$file" "- Work type: \`$work_type\`"
  require_line "$file" "- Objective: \`$objective\`"
  require_line "$file" "- Bounded scope: \`$scope\`"
  require_line "$file" "- Overall acceptance result: \`$acceptance\`"
  require_line "$file" "- Decision: \`$decision\`"
  require_line "$file" "- Output root: \`$output_root\`"
  require_line "$file" "- Summary path: \`$summary_path\`"
done
require_line "$iteration" "- Phase: \`closed\`"
require_line "$current" "- Phase: \`closed\`"

grep -Fq -- "$next_state" "$iteration" || fail 'iteration record next state differs'
grep -Fq -- "$next_state" "$current" || fail 'CURRENT next state differs'
grep -Fq -- "$next_state" "$summary" || fail 'cumulative summary next state differs'
grep -Fq -- "$next_state" "$report" || fail 'comprehensive report next state differs'

registry_prefix="iter010,2026-08-12T20:05:00-07:00,$status,$work_type,$objective,$scope,$acceptance,$decision,"
grep -Fq -- "$registry_prefix" "$registry" || fail 'registry identity/scope/gate/decision differs'
grep -Fq -- ",$output_root,$summary_path,committed,expected_parent=$expected_parent;expected_subject=$expected_subject;validator=validate_iter010_handoff.sh," "$registry" || fail 'registry paths or non-circular closeout identity differ'

for job in 23554607 23554935 23555136 23555187; do
  grep -Fq -- "$job" "$iteration" || fail "iteration record missing job $job"
  grep -Fq -- "$job" "$compact/iter010_accounting.csv" || fail "accounting missing job $job"
done
[[ $(grep -c ',COMPLETED,0:0,' "$compact/iter010_accounting.csv") -eq 4 ]] || fail 'terminal accounting is incomplete'

jq -e '.prediction_required == false and .sites.ABBY.topology == "two_basin_declined" and .sites.JERC.topology == "two_basin_declined" and (.sources | length == 6)' "$compact/topology_decision.json" >/dev/null || fail 'topology decision is invalid'
jq -e '.status == "skipped" and .evaluations == 0' "$compact/conditional_prediction.json" >/dev/null || fail 'conditional prediction skip is invalid'
for artifact in iter010_source_manifest.json topology_table.csv iter010_accounting.csv abby_three_seed_comparison.png jerc_three_seed_comparison.png; do
  [[ -s "$compact/$artifact" ]] || fail "missing compact artifact $artifact"
done
[[ -d "$external" ]] || fail 'external topology directory missing'
[[ $(find "$external" -maxdepth 1 -type f -name '*.png' | wc -l) -eq 32 ]] || fail 'expected 32 external PNG figures'
[[ $(find "$external" -maxdepth 1 -type f -name '*_metrics.npz' | wc -l) -eq 6 ]] || fail 'expected six external metric archives'

for site in abby jerc; do
  for seed in 9009 9010 9011; do
    for suffix in 01_traces 02_terminal 03_corner 04_pca 05_rolling; do
      grep -Fq -- "${site}_seed${seed}_${suffix}.png" "$report" || fail "report missing caption for ${site}_seed${seed}_${suffix}.png"
    done
  done
  grep -Fq -- "${site}_three_seed_comparison.png" "$report" || fail "report missing site synthesis caption for $site"
done
for label in convergence_supported_under_revised_iter009_diagnostics convergence_not_established_abby_acceptance_and_saturation not_applicable_no_supported_basins; do
  grep -Fq -- "$label" "$report" || fail "report missing interpretation $label"
done

plan_a=$(mktemp)
plan_b=$(mktemp)
paths_actual=$(mktemp)
paths_expected=$(mktemp)
trap 'rm -f "$plan_a" "$plan_b" "$paths_actual" "$paths_expected"' EXIT
sed -n '/<!-- ITER011_PLAN_BEGIN -->/,/<!-- ITER011_PLAN_END -->/p' "$iteration" > "$plan_a"
sed -n '/<!-- ITER011_PLAN_BEGIN -->/,/<!-- ITER011_PLAN_END -->/p' "$current" > "$plan_b"
[[ -s "$plan_a" && -s "$plan_b" ]] || fail 'complete Iter011 proposal markers missing'
cmp -s "$plan_a" "$plan_b" || fail 'Iter011 proposal differs between iteration record and CURRENT'
for heading in 'Sequential ID' 'Status' 'Work type' 'Objective' 'Evidence basis' 'Hypothesis' 'Dependencies' 'Bounded matrix' 'Exclusions' 'Integrity gates' 'Diagnostic evidence, not scientific hard gates' 'Decision rule' 'Proposed outputs' 'Proposed Puma resources' 'Monitoring and closeout' 'Authority boundary'; do
  grep -Fq -- "- $heading:" "$plan_a" || fail "Iter011 proposal missing $heading"
done

if grep -Fq -- 'Planning-Only Proposed Iter010' "$current" || grep -Fq -- 'Submit and monitor the reviewed Iter010 preflight' "$current"; then
  fail 'CURRENT retains stale Iter010 planning or submission instructions'
fi
grep -Fq -- 'No current authority exists to initialize Iter011' "$current" || fail 'CURRENT authority boundary missing'

cat > "$paths_expected" <<'EOF'
development/spinup_forcing_coupling/ITERATION_SUMMARY.md
development/spinup_forcing_coupling/handoff/CURRENT.md
development/spinup_forcing_coupling/iterations/iter010.md
development/spinup_forcing_coupling/registry.csv
development/spinup_forcing_coupling/slurm/iter010/validate_iter010_handoff.py
development/spinup_forcing_coupling/slurm/iter010/validate_iter010_handoff.sh
development/spinup_forcing_coupling/summaries/iter010/ITER010_REPORT.md
EOF

if [[ "$phase" == "precommit" ]]; then
  [[ $(git rev-parse HEAD) == "$expected_parent" ]] || fail 'precommit HEAD is not expected parent'
  git diff --cached --name-only | sort > "$paths_actual"
else
  [[ $(git rev-parse HEAD^) == "$expected_parent" ]] || fail 'postcommit parent differs'
  [[ $(git log -1 --format=%s) == "$expected_subject" ]] || fail 'postcommit subject differs'
  git diff-tree --no-commit-id --name-only -r HEAD | sort > "$paths_actual"
  [[ -z $(git status --short) ]] || fail 'postcommit worktree is not clean'
fi
cmp -s "$paths_expected" "$paths_actual" || {
  diff -u "$paths_expected" "$paths_actual" >&2 || true
  fail 'controlled path set differs'
}

git diff --check "$expected_parent" -- || fail 'diff check failed'
printf 'ITER010_HANDOFF_VALIDATE_PASS phase=%s active_job_count=0\n' "$phase"
