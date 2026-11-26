#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
readonly CAMPAIGN=${REPO_ROOT}/development/mcmc_optimization
readonly REPORT=${CAMPAIGN}/iterations/iter004.md
readonly SUMMARY=${CAMPAIGN}/summaries/iter004/summary.md
readonly CUMULATIVE=${CAMPAIGN}/ITERATION_SUMMARY.md
readonly REGISTRY=${CAMPAIGN}/registry.csv
readonly HANDOFF=${CAMPAIGN}/handoff/CURRENT.md
readonly RUNTIME=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter004_candidate_search_mcmc_pilot
readonly PLAN_SHA=5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0

cd "${REPO_ROOT}"
git diff --check
git diff --exit-code -- development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md >/dev/null
test "$(sha256sum development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md | cut -d' ' -f1)" = "${PLAN_SHA}"
sha256sum --check development/mcmc_optimization/slurm/iter004/execution_files.sha256 >/dev/null

for file in "${REPORT}" "${SUMMARY}" "${CUMULATIVE}" "${REGISTRY}" "${HANDOFF}"; do
  test -s "${file}"
done

readonly DECISION="$(jq -r '.decision_candidate' "${RUNTIME}/results/final_validation.json")"
[[ "${DECISION}" == mcmc_pilot_validated ||
   "${DECISION}" == mcmc_pilot_validated_with_limitations ||
   "${DECISION}" == iter004_validation_failed ]]
grep -Fq -- '- Status: `completed`' "${REPORT}"
grep -Fq -- '- Phase: `closeout`' "${REPORT}"
grep -Fq -- "\`${DECISION}\`" "${REPORT}"
grep -Fq -- 'exploratory engineering pilot' "${REPORT}"
grep -Fq -- 'Missing `pytest`' "${REPORT}"
grep -Fq -- 'load_ppe1_coupled_release()' "${REPORT}"

grep -Fq -- "\`${DECISION}\`" "${SUMMARY}"
grep -Fq -- 'no posterior convergence' "${SUMMARY}"
grep -Fq -- '## iter004 - Initial Candidate Search and Four-Observable MCMC Pilot' "${CUMULATIVE}"
grep -Fq -- "\`${DECISION}\`" "${CUMULATIVE}"

readonly REGISTRY_ROW="$(tail -n 1 "${REGISTRY}")"
test "$(awk 'BEGIN{q=0;n=1} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="\""){if(q && substr($0,i+1,1)=="\""){i++}else{q=!q}}else if(c=="," && !q){n++}}} END{print n}' <<<"${REGISTRY_ROW}")" = 14
[[ "${REGISTRY_ROW}" == iter004,*,completed,* ]]
grep -Fq "${DECISION}" <<<"${REGISTRY_ROW}"
grep -Fq 'validator=validate_closeout_iter004.sh' <<<"${REGISTRY_ROW}"

grep -Fq -- '- Current status: `closed`.' "${HANDOFF}"
grep -Fq -- '- Current phase: `closed`.' "${HANDOFF}"
grep -Fq -- '- Last completed iteration: `iter004`.' "${HANDOFF}"
grep -Fq -- '- Active iteration: none.' "${HANDOFF}"
grep -Fq -- '- Active jobs: none;' "${HANDOFF}"
grep -Fq -- "Decision: \`${DECISION}\`" "${HANDOFF}"
grep -Fq -- 'Missing `pytest`' "${HANDOFF}"
grep -Fq -- 'load_ppe1_coupled_release()' "${HANDOFF}"

test "$(jq -r '.result' "${RUNTIME}/results/final_validation.json")" = pass
test "$(jq -r '.result' "${RUNTIME}/results/diagnostics_validation.json")" = pass
if [[ "${DECISION}" == iter004_validation_failed ]]; then
  for site in ABBY JERC; do
    test "$(jq -r '.schema' "${RUNTIME}/sites/${site}/pilot_validation_failure.json")" = mcmc-iter004-site-pilot-failure-v1
    test "$(jq -r '.result' "${RUNTIME}/sites/${site}/pilot_validation_failure.json")" = iter004_validation_failed
    test "$(jq -r '.continuation_gate.iteration' "${RUNTIME}/sites/${site}/pilot_validation_failure.json")" = 128
    test "$(jq '.continuation_gate.fatal_reasons | length > 0' "${RUNTIME}/sites/${site}/pilot_validation_failure.json")" = true
    test ! -e "${RUNTIME}/sites/${site}/pilot/COMPLETED.json"
  done
fi
test "$(jq -r '.outcome' "${RUNTIME}/reviews/package_review.json")" = pass
[[ "$(jq -r '.outcome' "${RUNTIME}/reviews/result_review.json")" == pass* ]]
test "$(jq -r '.schema' "${RUNTIME}/manifests/final_job_accounting.json")" = mcmc-iter004-job-accounting-v1
test "$(jq -r '.active_or_unaccounted' "${RUNTIME}/manifests/final_job_accounting.json")" = 0
test "$(jq '.attempts | length <= 16' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "preflight_correction")] | length <= 3' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "preflight_diagnostic")] | length <= 1' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "wu3_correction")] | length <= 1' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "wu3_identity_correction")] | length <= 1' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "pilot_startup_correction")] | length <= 2' "${RUNTIME}/manifests/final_job_accounting.json")" = true
test "$(jq '[.attempts[] | select(.retry_class == "shared_infrastructure_retry")] | length == 0' "${RUNTIME}/manifests/final_job_accounting.json")" = true
jq -e '
  ([.attempts[].planned_job] | unique | sort) ==
  (["preflight_iter004.slurm","search_abby_iter004.slurm","search_jerc_iter004.slurm",
    "pool_restart_iter004.slurm","pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm",
    "diagnostics_iter004.slurm","final_iter004.slurm"] | sort)
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  .attempts as $rows |
  ([$rows[].submission_sequence] == [range(1; ($rows | length) + 1)]) and
  (([$rows[].job_id | tostring] | unique | length) == ($rows | length)) and
  ([$rows[].job_id | tostring | test("^[1-9][0-9]*$")] | all) and
  ([$rows[].retry_class | IN("planned","preflight_correction","preflight_diagnostic","wu3_correction","wu3_identity_correction","pilot_startup_correction","shared_infrastructure_retry")] | all)
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  [.attempts | group_by(.planned_job)[] | sort_by(.submission_sequence) |
   select(.[0].retry_class != "planned" or ([.[1:][]? | select(.retry_class == "planned")] | length) != 0)] |
  length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  [.attempts[] | select(
    .account != "chopinsong" or .partition != "standard" or
    (.state | IN("COMPLETED","FAILED","CANCELLED","TIMEOUT","OUT_OF_MEMORY","NODE_FAIL","PREEMPTED","BOOT_FAIL","DEADLINE","REVOKED") | not)
  )] | length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  [.attempts[] | select(
    ((.planned_job | IN("preflight_iter004.slurm","final_iter004.slurm")) and .alloc_cpus != 2) or
    ((.planned_job | IN("search_abby_iter004.slurm","search_jerc_iter004.slurm","pool_restart_iter004.slurm","pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm","diagnostics_iter004.slurm")) and .alloc_cpus != 4)
  )] | length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
if [[ "${DECISION}" == iter004_validation_failed ]]; then
  jq -e '
    [.attempts | group_by(.planned_job)[] | sort_by(.submission_sequence) | last |
     select(
       if (.planned_job | IN("pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm")) then
         (.state != "FAILED" or .exit_code != "1:0" or
          .failure_classification != "pilot_fatal_numerical_rejection")
       else
         (.state != "COMPLETED" or .exit_code != "0:0")
       end
     )] | length == 0
  ' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
else
  jq -e '
    [.attempts | group_by(.planned_job)[] | sort_by(.submission_sequence) | last |
     select(.state != "COMPLETED" or .exit_code != "0:0")] | length == 0
  ' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
fi
jq -e '
  [.attempts[] | select(
    .state == "COMPLETED" and .exit_code == "0:0" and (.failure_classification | IN(null,"none") | not)
  )] | length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  [.attempts[] | select(
    (.failure_classification | IN("pilot_precreated_directory_compatibility","pilot_fatal_numerical_rejection")) and
    (.planned_job | IN("pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm") | not)
  )] | length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null
jq -e '
  [.attempts | group_by(.planned_job)[] | sort_by(.submission_sequence) | . as $rows |
   range(1; ($rows | length)) as $i |
   select(
     ($rows[$i].retry_class == "preflight_correction" and
       ($rows[$i].planned_job != "preflight_iter004.slurm" or
        ((($rows[$i - 1].failure_classification |
             IN("preflight_packaging","preflight_application_compatibility","preflight_numerical_parity") | not)) and
          (($rows[$i - 1].retry_class != "preflight_diagnostic") or
           (($rows[$i - 1].job_id | tostring) != "24825862") or
           ($rows[$i - 1].diagnostic_outcome != "parity_fail") or
           (($rows[$i].preceding_job_id | tostring) != "24825862"))))) or
     ($rows[$i].retry_class == "preflight_diagnostic" and
       ($rows[$i].planned_job != "preflight_iter004.slurm" or
        $rows[$i - 1].failure_classification != "preflight_numerical_parity" or
        ($rows[$i - 1].job_id | tostring) != "24825557" or
        ($rows[$i].preceding_job_id | tostring) != "24825557")) or
     ($rows[$i].retry_class == "wu3_correction" and
       ($rows[$i].planned_job != "pool_restart_iter004.slurm" or
        $rows[$i - 1].failure_classification != "pool_replay_numerical_parity" or
        ($rows[$i - 1].job_id | tostring) != "24826641" or
        ($rows[$i].preceding_job_id | tostring) != "24826641")) or
     ($rows[$i].retry_class == "wu3_identity_correction" and
       ($rows[$i].planned_job != "pool_restart_iter004.slurm" or
        $rows[$i - 1].failure_classification != "wu3_target_identity_packaging" or
        ($rows[$i - 1].job_id | tostring) != "24826855" or
        ($rows[$i].preceding_job_id | tostring) != "24826855")) or
     ($rows[$i].retry_class == "pilot_startup_correction" and
       ($rows[$i - 1].failure_classification != "pilot_precreated_directory_compatibility" or
        (($rows[$i].planned_job == "pilot_abby_iter004.slurm") and
         (($rows[$i - 1].job_id | tostring) != "24827059" or ($rows[$i].preceding_job_id | tostring) != "24827059")) or
        (($rows[$i].planned_job == "pilot_jerc_iter004.slurm") and
         (($rows[$i - 1].job_id | tostring) != "24827061" or ($rows[$i].preceding_job_id | tostring) != "24827061")) or
        ($rows[$i].planned_job | IN("pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm") | not))) or
     ($rows[$i].retry_class == "shared_infrastructure_retry" and
       (($rows[$i].planned_job | IN("pilot_abby_iter004.slurm","pilot_jerc_iter004.slurm","diagnostics_iter004.slurm","final_iter004.slurm") | not) or
        ($rows[$i - 1].failure_classification | IN("scheduler","node","preemption","transport") | not)))
   )] | length == 0
' "${RUNTIME}/manifests/final_job_accounting.json" >/dev/null

readonly JOBS="$(jq -r '[.attempts[].job_id] | join(",")' "${RUNTIME}/manifests/final_job_accounting.json")"
test -z "$(/usr/bin/squeue --jobs="${JOBS}" -h -o '%i')"
readonly ACCOUNTING="$(/usr/bin/sacct --jobs="${JOBS}" --starttime=2026-11-25T00:00:00 --parsable2 --noheader --format=JobIDRaw,State,ExitCode)"
while IFS='|' read -r job state exit_code; do
  grep -Eq "^${job}\\|${state}(\\+)?\\|${exit_code}\\|?$" <<<"${ACCOUNTING}"
done < <(jq -r '.attempts[] | [.job_id, .state, .exit_code] | @tsv' "${RUNTIME}/manifests/final_job_accounting.json" | tr '\t' '|')

echo "ITER004_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=${DECISION} active_jobs=0"
