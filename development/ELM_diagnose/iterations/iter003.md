# iter003 - Generalized carbon-flux diagnostic tool and nine-site SR package

## Status

- Iteration ID: `iter003`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter003_nine_site_sr`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-29T18:53:48-07:00`
- Closed: `2026-08-30T14:18:14-07:00`

## Finalized Plan and Runtime Contract

- User approved the complete Iter003 package at `2026-08-29T18:53:48-07:00`, including preparation through closeout, one Puma job, job-scoped accounting, bounded cancellation, and one scoped closeout commit.
- Goal: implement the readable direct-YAML carbon-flux diagnostic tool and produce one descriptive nine-site `SR` package, stopping only at validated closeout.
- Inputs: `configs/iter003_sr.yml` lists nine absolute observation paths, nine `ctrl` control paths, and 60 seed-labeled optimized paths; no glob or generated receipt is an input. `SR_err` is conditional: missing or invalid values suppress only its band and are recorded.
- Scope: member collections may mix single-run and ensemble pickles; plots preserve `NaN` gaps; each site receives hourly, daily, monthly, UTC-diurnal, and distribution `SR` figures plus series/member metrics. No ranking, selection, pooling, scientific conclusion, model execution, or automatic retry.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter003/`; authorized creation and retention, with no automated backup/deletion.
- Resources: Puma standard, one node/task, six CPUs (30 GB), one hour, `OLMT_puma`; 300-second monitoring cadence except immediate identity and terminal checks. One job validates all direct inputs before output; no separate config-generating preflight.
- Gates: exact 9/9/60 input membership, compatible `taxis`, nonempty paired support and complete UTC day/site, 45 variable-named figures, two metrics CSVs, manifest/receipt, review, terminal accounting, and four-record agreement.

### Approved retry revision

- `2026-08-30`: job `23725468` reached `TIMEOUT 0:0` at 01:00:18 (7.55 GB/30 GB; no application output). The user approved one retry with the same six CPUs/30 GB and a two-hour cap in `diagnostic_retry1`.
- The retry loads/hashes each input once and writes sequential artifacts only to hidden staging. A late failure may leave staging artifacts, but it never publishes `results_retry1`; receipt, manifest, tables, and figures are atomically published only after every site succeeds. This narrowly replaces the original no-artifact-before-all-validation rule for retry one.
- After retry one, preserve terminal evidence and ask the user before any additional retry or closeout.

### Approved retry-two revision

- `2026-08-30`: the user cancelled retry one (`23728964`, 15:34 elapsed) and approved retry two. Replace per-member repeated daily scans with one vectorized `time × members` complete-day aggregation per series/site; add flushed per-site progress messages. Retain six CPUs/30 GB/two hours and use distinct `diagnostic_retry2`/`results_retry2` paths.
- Preserve all inputs, gates, staging publication, and scope. Ask the user before any later retry or closeout.

## Provenance and Job Ledger

| Work unit | Canonical material | Run directory | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- |
| diagnostic | submitted original material | `.../elm_diagnose_iter003/diagnostic` | `23725468` | `TIMEOUT 0:0`, 01:00:18; 7.55 GB/30 GB | no automatic retry |
| diagnostic retry one | submitted script/config byte-identical to canonical | `.../elm_diagnose_iter003/diagnostic_retry1` | `23728964` | `CANCELLED by 49065 0:0`, 00:15:34; 4.44 GB/30 GB | user-authorized cancellation for efficiency revision |
| diagnostic retry two | reviewed vectorized material | `.../elm_diagnose_iter003/diagnostic_retry2` | `23729042` | `COMPLETED 0:0`, 02:29; 21.6 GB/30 GB | no further retry |

## Independent Read-Only Review

- Reviewer: independent read-only `/root/iter003_review`.
- Outcome: initial pass after correction/re-review; focused retry-one identity review passed for canonical/submitted script `fd04cb…`, config `327852…`, current tool/YAML hashes, reconciled timeout ledger, `bash -n`, and `git diff --check`.

## Execution and Diagnostics

- Static validation: `bash -n`, membership counts 9 sites/9 controls/60 optimized, and `git diff --check` passed before review.
- Exact submission: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=.../elm_diagnose_iter003/diagnostic/submission_config.env ./submit_diagnostic_iter003.slurm </dev/null`.
- Immediate identity: job `23725468` RUNNING on `r4u06n2`, standard/chopinsong, six CPUs, 30 GB, one hour, and the recorded work directory.

### Monitoring-environment evidence

- During terminal monitoring of `23725468`, the documented Puma foreground loop with `POLL_SECONDS=300` was launched directly through the Codex agent terminal. The wrapper ended that foreground command after its first `squeue` snapshot, before the next 300-second sleep/poll cycle. Re-launches had the same behavior.
- This was not a Slurm cancellation or HPC-admin action: the workload remained `RUNNING` in subsequent job-scoped `squeue`/`sacct` checks. A detached tmux monitor also could write a snapshot log, but cannot cause Codex to proactively re-enter this chat after a polling interval.
- Consequence: this agent session cannot supply persistent loop-driven chat updates. Use discrete 300-second agent checks while a turn is active; for future workflows, evaluate Slurm `END,FAIL,TIME_LIMIT` notifications or an explicitly approved external monitoring/notification service. Preserve this evidence for a later workflow improvement; it does not authorize a workflow change in Iter003.

### Agent-continuity failure to diagnose later

- During Iter003 retry preparation, the agent repeatedly returned a final status while an approved workflow action remained pending (independent-review retrieval, submitted-copy materialization, or the next authorized monitoring action). This caused user-required manual `continue` prompts despite an active iteration and explicit continuity authority.
- This is separate from the foreground-terminal wrapper limitation: it is an agent control-flow failure to remain active through the next bounded workflow action. Future workflow improvement must diagnose and prevent premature final responses while an iteration is `in_progress`, except when a user decision or external-state change is genuinely required.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Evidence: retry two `23729042` completed `0:0` in 02:29 with 02:01 CPU and 21.6 GB peak memory. `results_retry2` contains 45 PNGs, 69 series rows, 960 member rows, passing input receipt, and a nine-site manifest.
- Decision: accepted descriptive SR diagnostic package; no ranking, parameter selection, or scientific conclusion.
- Next action: closed by user authorization; future workflow-improvement work must separately address recorded monitoring and agent-continuity evidence.
