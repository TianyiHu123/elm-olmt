# iter007 - ABBY/JERC pooled GPP MLP configuration experiment

## Status

- Iteration ID: `iter007`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter007_abby_jerc_gpp_config`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-01T15:54:23-07:00`
- Closed: `2026-11-02T22:28:22-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 5, two-site GPP development
- Alignment: `aligned_with_scoped_deviation`
- Approved deviation: use the published all-819 predicted-C/N handoff on both sides of every
  GPP split. Evidence is `fixed_upstream_gpp_stage`, not end-to-end held out.

## Finalized Plan

- Objective: select the best pooled ABBY/JERC GPP MLP configuration from a locked 24-candidate
  matrix using development-only evidence, while recording a best candidate even if the pooled
  selection gate fails.
- Inputs: immutable snapshot `r0001`; exact 819-development/205-fixed-test boundary; published
  spinup release and predicted-C/N handoff; exact Iter006 43-feature, physical-GPP, cache, and
  inference contracts; and the exact Iter006 20 balanced 655/164 splits.
- Candidate matrix: hidden layers `(32,)`, `(64,)`, `(128,)`, `(64,32)` crossed with `relu` and
  `tanh` and alpha `1e-4`, `10`, and `100`. Candidate 0 is the exact Iter006
  `(128,)`/ReLU/`1e-4` baseline. Adam and all other optimizer controls remain frozen.
- Staging: all 24 candidates run screening splits `1,3,7,10,12,13,14,16`; the top six eligible
  configurations run the other 12 splits, so six finalists each have 20 newly fitted repetitions.
- Metrics: only pooled ABBY+JERC hourly and complete-day metrics enter tables, gates, and ranking.
  Site identity remains provenance metadata. Bias is prediction minus ELM in `gC/m^2/day`.
- Decision: always record the best technically eligible finalist. Close as
  `configuration_selected_gate_pass` if it passes every pooled gate, otherwise
  `search_insufficient_best_candidate_recorded`. A failed-gate best candidate is not release
  qualified.
- Work units: no-training preflight; bounded smoke; 192-leaf screening array; screen
  aggregation/validation and finalist freeze; 72-leaf finalist array; combined final
  aggregation/fresh-process validation; concise closeout; one no-push commit.
- Exclusions: fixed-test access; spinup execution/refit; feature, target, upstream-mode, optimizer,
  or split changes; all-819 GPP fit; artifact/uncertainty/SR handoff/publication; observations;
  MCMC; campaign-plan edit; deletion; or push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User first approved the seven-task package with the revision `combine final aggregation and validation to one task`; after the complete six-task package was presented, user responded `Yes, approved.` at `2026-11-01T15:54:23-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Six normal submissions: preflight, smoke, 192-leaf screen, screen aggregate/validate, 72-leaf finalists, and combined final aggregate/validate. Continue through authoritative terminal accounting, independently reproduced best candidate/gate, concise closeout, four-record validation, and one no-push commit. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb6865...9128`; progression item 5; `aligned_with_scoped_deviation`; fixed all-819 predicted C/N on both sides. |
| Confirmed HPC system and site profile | UA Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter007_abby_jerc_gpp_config` with `runs/{preflight,smoke,screen,screen_aggregate,finalists,final}`. Reuse the hash-locked Iter006 raw cache read-only. Keep all runtime/XDG caches on temporary unbacked `/xdisk`; preserve outputs; no cleanup. Retain about 21–25 GB of validation predictions plus up to about 3.8 TB of per-fit scaled-training scratch required by sklearn fitting; this remains within the observed 11.5 TB free allocation. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities, 24 candidates, eight screen splits, six finalists, 20-fit finalist evidence, pooled-only metrics/gates/ranking, fixed-test prohibition, and always-recorded best-candidate rule in this report. |
| Lifecycle authority | Iter007 report/handoff, bounded implementation/tests/scripts/config/manifests/validators, exact directories, independent read-only reviews, six normal submissions, contract-authorized retries, monitoring/accounting/evaluation, concise records, and one no-push closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preflight 5 derived CPUs/25 GB/4 h; smoke 4 CPUs/20 GB/2 h; screen/finalist leaf 12 derived CPUs/60 GB/16 h, arrays capped at 20; screen aggregate 4 CPUs/20 GB/2 h; final combined task 8 CPUs/40 GB/4 h. Up to five additional submissions: at most one non-scientific preflight plumbing correction after re-review, otherwise unchanged same-resource scheduler/node/transport retries for failed work only. Material changes require fresh approval. Use supported waits and job-scoped monitoring through terminal `sacct`. |
| Cancellation scope | Recorded Iter007 jobs only when duplicated, outside contract, invalidated upstream, unsafe, threatening storage integrity, or affected by a proven common defect. Pending or slow state is not sufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the stated conditions. |
| Closeout branch | One controlled no-push Iter007 closeout commit. |

Live Section 4A evidence at kickoff: Git was clean at
`eab261a62f4ffcfb82436aa6afd179d0171654e3`; Iter006 had no active jobs and final job `24491301`
remained `COMPLETED 0:0`; declared input hashes matched; `/xdisk/chopinsong` used `8.0/19.5 TB`;
home used `41.9/50 GB` and group home `473.5/500 GB`; allocation expiration was unavailable to a
non-PI query.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction and invariants | `development/three_stage_surrogate/PLAN.md` | approved plan | `9bbb6865...9128` | Iter006 alignment and live hash confirmed. |
| Workflow | Lifecycle authority | `development/three_stage_surrogate/WORKFLOW.md` | current | `f23f040e...dc4` | Governing lifecycle policy. |
| Puma profile | Site mechanics | `development/hpc/puma.md` | current | `12d05836...2851` | Host, quota, account, and resource semantics checked. |
| Snapshot manifest | Immutable ABBY/JERC inputs | `<snapshot>/manifests/dataset_snapshot_r0001.json` | snapshot v1 | `39b05495...187a` | Live hash matched. |
| Global member split | Development/fixed-test boundary | `<snapshot>/splits/member_split_1024_v1.json` | 819/205 | `99467dea...0fce` | Live hash matched; fixed-test access forbidden. |
| Spinup release | Fixed upstream package | `<products>/spinup_abby_jerc/release_0001/release_manifest.json` | release v1 | `69f840f7...f2dc` | Live hash matched. |
| Predicted C/N | Fixed GPP input | `<products>/spinup_abby_jerc/release_0001/handoff/spinup_predicted_cn.nc` | 819 development members | `9e2d5be4...fdb5` | Live hash matched; in-sample upstream limitation retained. |
| Repeated splits | Paired candidate evidence | `<products>/spinup_abby_jerc/release_0001/uncertainty/repeated_split_manifest.json` | 20 balanced splits | `7644ed38...ace0` | Live hash matched; exact Iter006 design. |
| Raw GPP cache | Read-only training/evaluation design | `<iter006>/runs/prepare/attempt_1/raw` | 100,442,160 rows, 43 features | X `7cd98417...281`; y `89297f4f...219`; layout `02414677...161` | Iter006 full-hash/source reconstruction validator passed; full hashes must pass again in compute-node preflight. |
| Iter006 pooled baseline metrics | Paired candidate-0 comparison | `<iter006>/runs/aggregate/attempt_3/metric_distribution.csv` | 20 pooled validation repetitions | `0c5f13f2...a366` | Independently validated Iter006 product; live hash must match before use. |

`<snapshot>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`;
`<products>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products`; and
`<iter006>` is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release`.

## Acceptance Gates and Decision Rule

- Screening candidates require all eight assigned fits; finalists require all 20. All assigned
  work must be terminal and every failure classified.
- Technical eligibility requires exact identities, full coverage, fit-only scalers/stopping state,
  finite unclipped predictions, complete diagnostics, and zero prohibited access/output.
- Pool ABBY and JERC hourly rows before scoring. Construct complete site/member/day means first,
  then pool daily rows. Site-specific metrics are not produced.
- Across 20 repetitions, pooled validation gates are: hourly R2 q10 `>=0.85`, RMSE q90 `<=5.0`,
  median absolute bias `<=0.35`; daily R2 q10 `>=0.75`, RMSE q90 `<=3.0`, median absolute bias
  `<=0.35`. Quantiles use NumPy `linear`.
- Normalized margins are `(value-floor)/floor` for R2 and `(ceiling-value)/ceiling` for RMSE/bias.
  Rank by overall gate pass, largest worst margin, largest mean margin, largest median paired
  composite improvement over candidate 0, lower cross-split variability, lower parameter count,
  then candidate ID.
- Always record the best eligible finalist. Gate pass yields
  `configuration_selected_gate_pass`; gate failure yields
  `search_insufficient_best_candidate_recorded` without release qualification.
- Final validation must independently recompute selection-driving pooled metrics from locked truth
  and saved held-out predictions, then independently reproduce eligibility, ranking, margins, gate,
  and best candidate in a fresh process inside the combined final task.
- Any input, candidate, feature, target, optimizer, split, metric, pooling, gate, ranking, resource,
  fixed-test, release, or scientific-interpretation change requires fresh approval.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `427ebc95...231d` | exact copy; config `ef4cb61f...85d2`; manifest `3327dd9a...1aff` | `<root>/runs/preflight`; `preflight_24494841.*` | locked inputs/cache | source manifest `3327dd9a...1aff` | job `24494841` | `COMPLETED 0:0`, `00:00:50`, batch MaxRSS `17801912K` | full hashes, source reconstruction, candidate/split contracts passed |
| smoke | `fed06e86...7657` | exact copy; same config/manifest | `<root>/runs/smoke`; `smoke_24494873.*` | preflight pass | source manifest `3327dd9a...1aff` | job `24494873` | `COMPLETED 0:0`, `00:00:26`, batch MaxRSS `720104K` | candidates 0/17/23 finite with exact pickle round trips; bounded convergence warnings expected at two iterations |
| screen | `45e8bdfc...4ab3` | exact copy; same config/manifest | `<root>/runs/screen` | smoke/review pass | source manifest `3327dd9a...1aff` | array job `24494900`, `0-191%20` | 192/192 `COMPLETED 0:0` | exact 24 x 8 coverage; all reports pass; no failed terminal state; elapsed `00:27:00` to `04:19:01`; batch MaxRSS below 60 GB |
| screen aggregate/validate | `a76a74d5...76f0` | exact copy; same config/manifest | `<root>/runs/screen_aggregate` | eligible screen evidence | source manifest `3327dd9a...1aff` | job `24506893` | `COMPLETED 0:0`, `00:01:55` | validation pass; finalists `[18,21,19,2,8,13]`; manifest `f0a97d89...24ad` |
| finalists | `fc567520...3429` | exact copy; same config/manifest | `<root>/runs/finalists` | finalist manifest/review pass | source manifest `3327dd9a...1aff` | array job `24507062`, `0-71%20` | 72/72 `COMPLETED 0:0` | exact 6 x 12 coverage; all reports pass; elapsed `00:27:18` to `04:43:31`; peak batch MaxRSS `45724988K` |
| final aggregate/validate | `c5f35e6d...df12` | exact copy; same config/manifest | `<root>/runs/final` | complete finalist evidence | source manifest `3327dd9a...1aff` | job `24512103` | `COMPLETED 0:0`, `00:01:32` | aggregation and fresh-process validation agree: best 21, gate pass |

`<root>` is the approved Iter007 output root above.

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter007_review`
- Reviewed source hash: first review `969d211f...c1ca`; corrected package `3327dd9a...1aff`.
- Outcome: first review `block`; corrected-package re-review upgraded to `pass` after its sole
  concern was withdrawn; production-stage screen/finalist reviews passed with no blocker or
  concern; final decision review was `pass_with_concerns` with no scientific blocker, and both
  closeout concerns were resolved before validation.
- Findings and primary-agent response: first review found partial-leaf retries could not feed one
  aggregation root, the Iter006 baseline metric file was not hash-locked, and the finalist manifest
  was not re-verified downstream. The primary agent added explicit multi-attempt leaf resolution
  requiring exactly one passing leaf, locked baseline hash `0c5f13f2...a366` in preflight and both
  ranking implementations, and enforced the finalist-manifest hash in downstream Slurm,
  aggregation, and independent validation. Validation-only predictions are retained, and the
  approximately 3.8 TB maximum scaled-training scratch footprint is recorded. Re-review confirmed
  all blockers resolved and every submitted copy/hash/static check passing. Its only concern read
  the Bash flag/path argument-array length as an attempt count; each root contributes two tokens,
  so the `>=2` check correctly requires one or more roots and clean attempt list `1` is valid.

## Execution and Diagnostics

- Initialization: approved at `2026-11-01T15:54:23-07:00`; report, exact external layout, six
  submitted copies, configuration, candidate manifest, and complete source manifest initialized.
- Static validation: shell syntax, JSON syntax, source-manifest verification, submitted-copy and
  configuration equality, and `git diff --check` pass. The first review blocked three
  provenance/retry gaps; corrected source manifest
  `3327dd9a11b306d3b3c04ddb4ca2d922ea889a73dcbfe72786d78c4b6aea1aff`
  passed independent re-review with the nonblocking argument-array rationale above.
- Preflight: attempt 1 job `24494841` passed full hashes, 18 source-row reconstructions, exact
  24-candidate/20-split/stage-fit counts, 43 features, and fixed-test/spinup prohibitions.
- Exact submission commands: preserved in scheduler `SubmitLine` and the preflight run directory.
- Job identity checks: job `24494841` matched the locked script, work directory, account,
  partition, 5 derived CPUs/25 GB, four-hour limit, and required hash exports.
- Queue and terminal accounting: preflight `24494841` completed `0:0` in 50 seconds with batch
  MaxRSS `17801912K`; smoke `24494873` completed `0:0` in 26 seconds with batch MaxRSS `720104K`.
- Smoke diagnostics: the structured report passed for candidate IDs 0, 17, and 23 on split 1,
  with 80 training members, 20 validation members, 1,440 hours, finite predictions, exact pickle
  round trips, zero fixed-test access, and zero spinup execution. Three two-iteration convergence
  warnings are expected and nonfatal for this bounded plumbing test.
- Resource diagnostics: smoke used well below its 20 GB allocation; production leaf evidence is
  pending.
- Production-stage review: the independent reviewer returned `PASS` with no blocker or concern,
  reverified smoke accounting and reports, source/config/submitted-copy hashes, exact 192-leaf
  mapping, resources, dependency, output isolation, and prohibited-output guards, and withdrew
  the earlier attempt-root argument concern in full.
- Screening submission: attempt 1 array `24494900` was submitted with dependency
  `afterok:24494873`; initial identity matched the exact script, work directory, account,
  partition, array `0-191%20`, throttle 20, 12 derived CPUs, 60 GB, 16-hour limit, and locked
  exports. It was pending for scheduler priority at the identity check.
- Monitoring mechanism: a persistent 45-second `squeue`/`sacct` monitor was started. Its first
  accounting parser used `JobIDRaw`, which Puma represents as separate instantiated IDs rather
  than array labels, so it counted zero tasks and could never satisfy its exit condition. It was
  stopped cleanly; direct task queries confirmed `JobID` carries `24494900_<task>`. Monitoring was
  replaced with the same job scope and wake interval using the correct `JobID` field; the workload
  was unaffected.
- User-requested monitoring checkpoint: after a platform usage-limit interruption, the corrected
  persistent handle was recovered with uninterrupted history and the full 192-leaf scope. At
  `2026-11-01T21:45:21-07:00`, authoritative accounting showed 78 `COMPLETED`, 20 `RUNNING`, 94
  `PENDING`, and no failed terminal state. At the user's explicit request to pause, the local
  read-only monitor was stopped cleanly; screening array `24494900` remains active and unchanged.
  Exact resume action is a fresh job-scoped `squeue` plus per-task `sacct` reconciliation, followed
  by one persistent monitor if any task is nonterminal.
- Screening completion: on `2026-11-02`, the user reported completion and authoritative `sacct`
  independently confirmed all 192 task allocations `COMPLETED 0:0`; queue lookup returned the
  expected post-exit invalid-job response. Elapsed times ranged from `00:27:00` to `04:19:01`, and
  observed batch MaxRSS remained below the 60 GB request. Static leaf reconciliation found 192
  unique candidate/split pairs, eight per candidate, 24 per locked split, zero bad structured
  reports, zero convergence warnings, exact 655/164 membership counts, 20,112,960 validation rows
  per leaf, complete artifact hashes, and no fixed-test, spinup, all-development-fit, or release
  flag. Attempt 1 retained about 2.5 TB including required scaled-training scratch.
- Screen aggregation submission: attempt 1 job `24506893` was submitted from the exact locked copy
  with screen attempt list `1`; initial identity matched account, standard partition, four CPUs,
  20 GB, two-hour limit, work directory, command, and locked exports while pending for priority.
- Screen aggregation result: job `24506893` completed `0:0` in `00:01:55`; both
  `ITER007_SCREEN_AGGREGATE_OK` and `ITER007_SCREEN_VALIDATE_OK` were emitted. It independently
  reproduced 192 leaves and froze finalists `[18,21,19,2,8,13]` with remaining split IDs
  `[0,2,4,5,6,8,9,11,15,17,18,19]`. Finalist manifest SHA-256 is
  `f0a97d89040c1b9f2d0f82c31b7989b7796cda3fba0ff59272f2ba74b7dc24ad`; fixed-test access is
  false. Screen ranks 1 and 2 (candidates 18 and 21) passed the provisional eight-split gate, but
  only complete 20-fit finalist evidence may determine the final gate and selection.
- Finalist-stage review: the independent reviewer returned `PASS` with no blocker or concern after
  reproducing the screen coverage, aggregate hashes/ranking, frozen finalist identity, exact
  72-pair mapping, resources, submitted-copy equality, and prohibited-output guards.
- Finalist submission rejection: the first `sbatch` call requested redundant
  `afterok:24506893` after the aggregation job was already terminal; Puma rejected it before
  assigning a job ID with `Batch job submission failed: Job dependency problem`. No workload was
  created. This is classified as a scheduler submission failure; the approved retry uses the same
  locked material, resources, attempt, and exports without the unnecessary terminal dependency.
- Finalist submission retry: the unchanged submission without the redundant terminal dependency
  succeeded as array `24507062`. Initial identity matched the exact script/work directory, account,
  standard partition, array `0-71%20`, throttle 20, 12 derived CPUs, 60 GB, 16-hour limit, and
  locked exports; it was pending at the identity check.
- User-requested finalist monitoring checkpoint: a corrected full-array monitor saw all 72 task
  accounting rows. At `2026-11-02T15:32:29-07:00`, 10 were `RUNNING`, 62 `PENDING`, and none
  terminal. At the user's explicit request, the local read-only monitor was stopped cleanly;
  finalist array `24507062` remains active and unchanged. Exact resume action is a fresh job-scoped
  `squeue` plus per-task `sacct` reconciliation, followed by one persistent monitor if any task is
  nonterminal.
- Finalist completion: authoritative `sacct` independently confirmed all 72 task allocations
  `COMPLETED 0:0`; queue lookup returned the expected post-exit invalid-job response. Elapsed times
  ranged from `00:27:18` to `04:43:31`, and peak observed batch MaxRSS was `45724988K`, below the
  60 GB request. Static leaf reconciliation found exactly 72 unique pairs, 12 new fits per frozen
  finalist, six per remaining split, zero bad reports, zero convergence warnings, exact 655/164
  membership counts, 20,112,960 validation rows per leaf, complete artifact hashes, and no
  prohibited flag. Attempt 1 retained about 954 GB including scaled-training scratch.
- Combined final submission: attempt 1 job `24512103` was submitted from the exact locked copy with
  screen/finalist attempt lists `1` and screen aggregate attempt `1`; initial identity matched
  account, standard partition, eight CPUs, 40 GB, four-hour limit, work directory, command, and
  locked exports while pending for priority.
- Combined final result: job `24512103` completed `0:0` in `00:01:32`; both
  `ITER007_FINAL_AGGREGATE_OK` and `ITER007_FINAL_VALIDATE_OK` were emitted. Aggregation and the
  fresh-process validator agree on best candidate 21, selection gate `pass`, and decision
  `configuration_selected_gate_pass`; final validation independently recomputed all 120 finalist
  leaves and records fixed-test access false and release authorization false.
- Independent final review: independently reconciled 120 unique selected leaves, every leaf
  artifact hash, 480 pooled-only metric rows, linear quantiles, medians, six normalized margins,
  paired baseline improvement, population variability, and the complete rank key. It reproduced
  order `21,18,19,2,8,13`, found candidates 21 and 18 gate-passing, and confirmed candidate 21 wins
  on the larger worst normalized margin. It found no scientific blocker. Its two closeout concerns
  were resolved by correcting the rejection/retry record and obtaining fresh scheduler evidence.
- Fresh terminal reconciliation: successful job-scoped `squeue` returned no active Iter007 jobs;
  successful `sacct` reported 268 allocations `COMPLETED 0:0`—192 screen leaves, 72 finalist
  leaves, and preflight, smoke, screen aggregation, and final jobs. All expected work is terminal.
- Failure, rejection, retry, or cancellation evidence: one finalist `sbatch` call with redundant
  `afterok:24506893` was rejected before job-ID assignment with
  `Batch job submission failed: Job dependency problem`; unchanged locked material/resources were
  resubmitted without the unnecessary terminal dependency as array `24507062`. There was no
  workload failure, scientific retry, or cancellation.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight/smoke | yes | jobs `24494841`/`24494873`; structured reports pass | pass | Eligible for production. |
| screening | yes | 192 leaves; exact 24 x 8 coverage; zero bad reports | pass | Eligible for finalist freeze. |
| screen aggregate/validate | yes | job `24506893`; 768 metric rows; independent validation pass | pass | Freeze `[18,21,19,2,8,13]`. |
| finalists | yes | 72 new leaves; six candidates x 12 remaining splits | pass | Each finalist has 20 fits. |
| final aggregate/validate | yes | 120 leaves; 480 pooled metric rows; validator and reviewer agree | selection gate `pass` | Select candidate 21. |
| release/publication | no | no fit, artifact, handoff, stable package, or catalog | prohibited | Selection does not authorize release. |

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: `configuration_selected_gate_pass`. Freeze candidate
  21—`(64,32)`, `tanh`, alpha `1e-4`, otherwise frozen Adam controls—for separately approved fresh
  robustness. Hourly R2 q10/RMSE q90/median absolute bias are
  `0.904205/4.260999/0.135299`; daily values are `0.829424/2.675357/0.135299`; all pooled gates
  pass. Candidate 18 also passes, but candidate 21 has the larger worst normalized margin
  (`0.063771` versus `0.056001`).
- Limitations: two sites; fixed in-sample upstream C/N; finite MLP matrix; repeated development
  splits reused from Iter006 for selection; pooled metrics can mask site-specific behavior;
  temporary unbacked storage; no fixed test, all-819 fit, release, SR, observation, or MCMC evidence.
- Campaign-plan amendment recommendation: `none`; fresh robustness is the appropriate next
  evidence stage within the current campaign direction.
- Next action: present the planning-only Iter008 proposal below for separate kickoff discussion.

## Proposed Next-Iteration Plan (Planning Only)

Freeze candidate 21 and test it on 20 newly generated balanced 655/164 development-member splits
that are distinct from the Iter006/Iter007 selection splits. Preserve the exact fixed-upstream
43-feature, physical-GPP, Adam, pooled hourly/daily metric, and immutable gate contracts. Retain
compact repeated-fit diagnostics and independently validate coverage, predictions, metrics, and
the gate. A pass may support a later separately planned all-819 release iteration; a failure must
stop with diagnostic evidence. Fixed-test use, release fitting/publication, SR handoff, and MCMC
remain out of scope. This proposal grants no runtime authority.

## Four-Record Closeout Validation

- Validator: `development/three_stage_surrogate/slurm/iter007/validate_closeout_iter007.sh`
- Command: `bash development/three_stage_surrogate/slurm/iter007/validate_closeout_iter007.sh --active-job-count 0`
- Result: `pass`
- Output: `ITER007_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=configuration_selected_gate_pass best=21 active_jobs=0 release=absent`
- Scope: report/summary/registry/handoff agreement; plan identity/alignment; terminal/no-active
  state; classified submission rejection; external and compact evidence hashes; 120-leaf/480-row
  coverage; candidate-21 identity, pooled gate, decision, and absence of release authorization.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter007/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified no-push commit
