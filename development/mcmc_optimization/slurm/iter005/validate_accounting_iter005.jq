def terminal: IN("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "PREEMPTED");
def expected_jobs: {
  "preflight_iter005.slurm": 2,
  "density_iter005.slurm": 2,
  "pilot_abby_iter005.slurm": 4,
  "pilot_jerc_iter005.slurm": 4,
  "diagnostics_iter005.slurm": 2
};

. as $root |
expected_jobs as $expected |
($root.schema == "mcmc-iter005-job-accounting-v1")
and ($root.active_or_unaccounted == 0)
and (($root.attempts | type) == "array")
and (($root.attempts | length) >= 1 and ($root.attempts | length) <= 10)
and (([$root.attempts[].job_id] | unique | length) == ($root.attempts | length))
and (($root.attempts | map(.submission_sequence)) == [range(1; ($root.attempts | length) + 1)])
and all($root.attempts[];
  (.job_id | type == "string" and test("^[0-9]+$"))
  and (.planned_job | in($expected))
  and (.alloc_cpus == $expected[.planned_job])
  and (.account == "chopinsong" and .partition == "standard")
  and (.state | terminal)
  and (.exit_code | type == "string" and test("^[0-9]+:[0-9]+$"))
  and (.failure_classification | type == "string")
  and (.retry_class | IN("planned", "preflight_correction", "infrastructure", "tolerance_correction")))
and (([$root.attempts[] | select(.retry_class == "planned")] | length) <= 5)
and (([$root.attempts[] | select(.retry_class == "preflight_correction")] | length) <= 1)
and (([$root.attempts[] | select(.retry_class == "tolerance_correction")] | length) <= 1)
and (([$root.attempts[] | select(.retry_class == "infrastructure" or .retry_class == "tolerance_correction")] | length) <= 4)
and all(($expected | keys[]);
  . as $job |
  ([$root.attempts[] | select(.planned_job == $job and .retry_class == "planned")] | length) <= 1)
and all($root.attempts[];
  . as $row |
  if $row.retry_class == "planned" then
    $row.preceding_job_id == null
  else
    ($root.attempts | map(select(.job_id == $row.preceding_job_id)) | .[0]) as $previous |
    $previous != null
    and ($previous.submission_sequence < $row.submission_sequence)
    and ($previous.planned_job == $row.planned_job)
    and ($previous.state != "COMPLETED")
    and (if $row.retry_class == "preflight_correction"
         then $row.planned_job == "preflight_iter005.slurm"
              and $previous.failure_classification == "preflight_narrow_correction"
         elif $row.retry_class == "tolerance_correction"
         then $previous.failure_classification == "numerical_tolerance_confirmed_correct_implementation"
              and ($row.tolerance_diagnosis_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
         else ($previous.failure_classification | IN("scheduler", "node", "preemption", "transport"))
         end)
  end)
and (if $decision == "iter005_validation_failed" then
  any($root.attempts[]; .state != "COMPLETED" and .failure_classification != "none")
else
  ([$root.attempts[].planned_job] | unique | sort) == ($expected | keys | sort)
  and all(($expected | keys[]);
    . as $job |
    ($root.attempts | map(select(.planned_job == $job)) | .[-1]) as $last |
    $last.state == "COMPLETED" and $last.exit_code == "0:0")
end)
