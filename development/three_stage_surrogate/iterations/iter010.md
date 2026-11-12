# iter010 - ABBY/JERC SR configuration refinement

## Status

- Iteration ID: `iter010`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter010_abby_jerc_sr_refinement`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-07T23:48:12-07:00`
- Closed: `2026-11-10T01:04:21-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: refine the Iter009 SR configuration around candidate 21 using fresh development-only
  splits and select a replacement only when a challenger passes the locked matched-control gate.
- Inputs: snapshot r0001; exact 819/205 boundary; published predicted C/N and same-hour predicted
  GPP; the validated Iter009 44-feature physical-SR raw cache; deterministic seed `20261107`.
- Matrix: 33 exact candidates. Candidate 0 is the Iter009 `(64,32)` tanh/alpha `1e-4`
  incumbent; candidates 1--31 vary nearby tanh width, depth, and alpha; candidate 32 is the
  Iter009 `(128,)` ReLU/alpha `10` runner-up reference. Adam and all other controls remain frozen.
- Staging: all 33 candidates on eight screen splits; mandatory control 0 plus five eligible
  challengers on the other 12 splits, yielding 20 fits for each finalist.
- Exclusions: fixed-test access, upstream refitting or execution, all-819 SR fit, robustness,
  uncertainty, release, observations, likelihood/MCMC, plan edit, deletion of prior evidence,
  and push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Complete package and runtime contract approved`; `2026-11-07T23:48:12-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Four normal submissions: Unit1 combined no-training preflight/fresh splits/cache validation/smoke; 264-leaf screen; 72-leaf finalists; final aggregation/fresh validation. Continue through authoritative accounting, replacement decision, records, four-record validation, and one no-push commit. Stop only at completed closeout or a workflow-defined fresh-authority condition. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6; aligned; no deviation. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; CPU only. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter010_abby_jerc_sr_refinement/runs/{unit1,screen,finalists,final}` with immutable attempts. Reuse Iter009 raw cache read-only. Preserve decision evidence; remove only successful validated per-fit scaled/runtime scratch. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; 33 candidates; 20 fresh balanced 655/164 splits; pooled hourly/daily ranking; matched-control replacement gate; zero fixed-test access; no release. |
| Lifecycle authority | Initialization; focused code/tests/scripts/config/manifests/validators; exact directories; independent read-only review before every submission; four normal submissions and bounded retries; monitoring/accounting; evaluation; concise records; validation; cleanup limited above; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 6 CPU/30 GB/6 h, cap 8/40/8; leaves 12 CPU/60 GB/16 h `%20`, cap 16/80/20; final 8 CPU/40 GB/4 h, cap 12/60/6. Unit1 and final each allow three additional submissions; screen/finalists share three. One reviewed validation-only correction per logical unit; otherwise scheduler/node/transport/launch/resource failures only. Application/code/interface/schema/data/dependency/numerical/science changes stop. Supported waits and job-scoped monitoring continue through terminal `sacct`. |
| Cancellation scope | Recorded Iter010 jobs only if duplicate, outside contract, invalidated by a proven common defect, unsafe, or threatening storage integrity. Pending or slow alone is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` above. |
| Closeout branch | One scoped local no-push commit authorized. |

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | SR truth, forcing, parameters, surfaces | `39b05495...187a` |
| Global split | 819/205 boundary | `99467dea...0fce` |
| Spinup release/handoff | predicted C/N | manifest `69f840f7...f2dc`; handoff `9e2d5be...fdb5` |
| GPP release/handoff | predicted same-hour GPP | manifest `57cc18b0...70d1`; handoff `c905fc60...98bb` |
| Iter009 raw cache | fixed 44-feature physical-SR design | layout `172c2f4b...b0b6`; X `c648952a...5cf`; y `35697d26...477`; time `8f2efdef...52e` |
| Iter009 selection splits | reference design prohibited from exact reuse | `7644ed38...ace0` |
| Candidate manifest | exact 33-candidate inventory | `1e2c8234...a0f5` |

## Acceptance Gates and Decision Rule

- Unit1 must produce 20 unique balanced `655/164` splits from seed `20261107`, with zero exact
  validation-set match to the Iter009 reference design, then pass full raw hashes, source
  reconstruction, contract checks, and bounded smoke.
- Technical eligibility requires complete expected fits, exact identities and coverage, finite
  unclipped predictions, successful serialization replay at `rtol=atol=1e-6`, zero production
  convergence warnings, successful scaled-scratch cleanup, and all prohibited-scope flags false.
- Rank pooled hourly and complete-day R2 q10, RMSE q90, and median absolute split bias by best
  worst ordinal score, mean score, lower composite variability, fewer parameters, then ID.
- Always report the best eligible finalist. Replace control 0 only if a challenger ranks first,
  strictly improves at least four of six selection statistics, and neither resolution has both
  worse R2 q10 and worse RMSE q90. Record `sr_refined_configuration_selected` on pass; otherwise
  retain control 0 and record `sr_refinement_insufficient_control_retained`.
- No absolute publication gate and no release. Any material contract change requires fresh approval.

## Provenance and Job Ledger

| Work unit | Canonical/submitted material | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- |
| Unit1 | manifests attempt 1 `e4bc138e...a003`, attempt 2 `be4830d6...1457`; config `6b0733f3...c16c`; exact submitted copy | `<root>/runs/unit1`; `unit1_24578833.*`, `unit1_24578853.*` | jobs `24578833`, `24578853` | attempt 1 `FAILED 1:0`; attempt 2 `COMPLETED 0:0`, eligible | approved minimal correction; retry submission 1 consumed |
| screen | manifest `3870eecb...2f66`; config `72e0a671...8718`; script `f5b872e8...5356`; exact submitted copies | `<root>/runs/screen`; `screen_24579541_*.{out,err}` | array `24579541_0-263%20` | all 264 tasks `COMPLETED 0:0`; evidence eligible | independent completion review pass; attempt 1 |
| finalists | manifest `3870eecb...2f66`; config `72e0a671...8718`; script `b7354cdb...e64ed`; exact submitted copies | `<root>/runs/finalists` | array `24590678_0-71%20` | all 72 tasks `COMPLETED 0:0`; evidence eligible | independent completion review pass; attempt 1 |
| final | manifest `3870eecb...2f66`; config `72e0a671...8718`; script `7d3a3e7c...72652`; exact submitted copies | `<root>/runs/final` | job `24595272` | `COMPLETED 0:0`; evidence eligible | independent package/result review pass; attempt 1 |

`<root>` is the approved output root above.

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter010_unit1_review`
- Reviewed source hash: initial `20868a68...3dee`; corrected `e4bc138e...a003`
- Outcome: initial `pass_with_concerns`; corrected-package re-review `pass`
- Findings and primary-agent response: no blocker. The reviewer verified the complete matrix,
  fresh-split contract, cache provenance, exact submitted copies, resources, and boundaries. It
  recommended direct redundant checks for three prohibited candidate-manifest flags. Those checks
  were added before submission; re-review verified every hash and exact submitted copy and passed
  with no remaining concern.
- Subsequent reviewer: independent read-only agent `/root/iter010_screen_rereview`. Screen
  completion/finalist package, finalist completion/final package, final result, and closeout-record
  reviews all passed with no remaining concern. The reviewer performed no edits or scheduler action.

## Execution and Diagnostics

- Section 4A recovery: Puma confirmed; Git clean at `414faa23`; Iter009 jobs terminal and queue
  empty; declared dependency hashes matched; `/xdisk` had about 7.6 TB available; current group
  limits accommodate the approved throttle.
- Initialization: package approved and goal created; preparing locked sources and submitted copies.
- Static validation: shell syntax, JSON syntax, source-manifest verification, submitted-copy and
  configuration equality, and `git diff --check` passed on the initial package; corrected package
  validation passed on corrected manifest `e4bc138e...a003`; independent re-review passed.
- Preflight and production accounting: complete; every expected task is terminal, the single
  pre-substantive Unit1 failure is classified, and all corrected/production work completed `0:0`.
- Unit1 submission: exact command used `sbatch --parsable` from the approved run directory with
  attempt `1`, config `6b0733f3...c16c`, manifest `e4bc138e...a003`, and stdin `/dev/null`;
  returned job `24578833` at `2026-11-08T00:01:41-07:00`. Immediate identity check follows.
- Unit1 immediate identity passed: `chopinsong/standard`, 6 CPUs with derived 30 GB, six-hour
  limit, exact command/workdir/logs, stdin `/dev/null`, and locked attempt/config/manifest exports;
  initial state `PENDING (Priority)`.
- Unit1 attempt 1 job `24578833` failed `1:0` after eight seconds; batch MaxRSS `15788K`. All
  source hashes passed, then unittest import stopped on a `SyntaxError` in the newly written
  candidate-inventory construction. No split generation, raw-cache access, smoke, or substantive
  training occurred. This is classified under the approved single minimal preflight-only
  correction: replace invalid starred generator syntax with equivalent explicit `extend` calls,
  refresh the manifest and submitted package, and require independent re-review before retry.
- Corrected manifest `be4830d6...1457` passed AST/shell/JSON/hash/copy checks and mandatory
  independent retry re-review with no concern. Retry submission 1 is authorized as Unit1 attempt 2.
- Unit1 attempt 2 used the exact run-directory copy with attempt `2`, unchanged config
  `6b0733f3...c16c`, corrected manifest `be4830d6...1457`, and stdin `/dev/null`; `sbatch --parsable`
  returned job `24578853` at `2026-11-08T00:06:40-07:00`.
- Attempt 2 identity matched `chopinsong/standard`, 6 CPUs/30 GB, six hours, exact command,
  workdir, logs, stdin, and attempt/config/manifest exports; initial state `PENDING (Priority)`.
- Attempt 2 job `24578853` completed `0:0` in `00:01:08`, TotalCPU `00:47.942`, 6 CPUs,
  batch MaxRSS `1971408K`, node `r7u08n1`. Unit1 report `868f9890...8017`, resolved config
  `72e0a671...8718`, and split manifest `34a33000...ae43` pass. The split design is
  `938c9c1b...51ff`, with 815 members appearing four times and four appearing five times in
  validation, zero reference matches, 33 candidates, 264 screen fits, 72 finalist fits, full raw
  hashes/source reconstruction, and bounded smoke success. Expected smoke-only two-iteration
  convergence warnings are non-production.
- Initial screen review blocked before submission because finalist selection verified only a subset
  of the approved leaf technical contract. No scheduler state changed. The selector is being
  strengthened to require exact report/candidate/split/member identities, all prohibited flags,
  prediction/artifact/metric/scaler/serialization hashes, serialization result/identity, complete
  metric rows, finite/reload flags, warning count, coverage, and successful scratch cleanup.
- First corrected-package re-review found one remaining exact-identity gap: mutually consistent
  candidate evidence was not compared directly to the approved candidate manifest. No scheduler
  action occurred. The selector now requires both candidate files to equal the hash-locked manifest
  candidate before ranking and requires another passing re-review.
- Corrected screen package passed independent read-only re-review with no concern on selector
  `d95eaa98...9455`, script `f5b872e8...5356`, execution manifest `3870eecb...2f66`, resolved
  config `72e0a671...8718`, and candidate manifest `1e2c8234...a0f5`. The reviewer independently
  reproduced all 264 unique mappings and every approved technical and scope gate.
- Screen submission used `sbatch --parsable` from the approved run directory with attempt `1`,
  resolved config `72e0a671...8718`, manifest `3870eecb...2f66`, and stdin `/dev/null`; returned
  array job `24579541` at `2026-11-08T04:20:24-07:00`. Immediate identity check follows.
- Screen immediate identity matched `chopinsong/standard`, array `0-263%20`, 12 CPUs with
  Puma-derived 60 GB, 16-hour limit, exact command/workdir/logs, stdin `/dev/null`, and locked
  attempt/config/manifest exports; initial state `PENDING (Priority)`.
- At the user's explicit request, the attached read-only monitor was stopped at
  `2026-11-08T04:22:07-07:00` without changing scheduler state. Final checkpoint: all 264 tasks
  remain `PENDING`, with no instantiated terminal accounting record and no failure. Exact resume:
  query job-scoped `squeue` and full parent `sacct` for `24579541`, reconcile all 264 task records,
  and resume monitoring only when the user reports completion or failure.
- The user reported completion and requested resumption. Fresh reconciliation at
  `2026-11-09T15:38:55-07:00` found an empty job-scoped queue and exactly 264 unique task records
  for `24579541_0-263`: every task is `COMPLETED 0:0`, allocated 12 CPUs with requested memory
  `60G`, with elapsed times from `00:36:37` to `05:21:30`. No task is missing or duplicated.
  Independent leaf-evidence and ranking review is now required before finalist submission.
- Independent read-only screen completion and finalist-package review passed at
  `2026-11-09T15:49:37-07:00` with no concern. The reviewer verified 33 candidates by eight
  splits, all 1,320 recorded artifact hashes, 1,056 metric rows, exact coverage and technical
  gates, and zero prohibited-scope flags. Independently reconstructed fingerprint
  `cc0721d7...af39` and finalist candidates `[0, 23, 19, 26, 11, 15]`; all 72 mappings to splits
  `[0,2,4,5,6,8,9,11,15,17,18,19]` are exact. The finalist submitted copy is byte-identical and
  contract-exact at script `b7354cdb...e64ed`, config `72e0a671...8718`, and execution manifest
  `3870eecb...2f66`.
- Finalist attempt 1 submission from the exact reviewed run-directory copy returned array job
  `24590678` at `2026-11-09T15:50:16-07:00`. Immediate identity matched `chopinsong/standard`,
  `0-71%20`, 12 CPUs and derived 60 GB, 16 hours, exact command/workdir/logs, stdin `/dev/null`,
  and the locked attempt, screen-attempt, config, and execution-manifest exports; initial state
  `PENDING (Priority)`.
- At the user's explicit request, the attached read-only finalist monitor was stopped at
  `2026-11-09T15:54:55-07:00` without changing scheduler state. Final checkpoint: all 72 tasks
  are `PENDING (Priority)`; no task has an instantiated accounting record and no failure is
  present. Exact resume: query job-scoped `squeue` and full parent `sacct` for `24590678`,
  reconcile all 72 task records, and resume the lifecycle only when the user reports completion
  or failure.
- The user reported completion and requested resumption. Fresh reconciliation at
  `2026-11-10T00:45:00-07:00` found an empty job-scoped queue and exactly 72 unique task records
  for `24590678_0-71`: every task is `COMPLETED 0:0`, allocated 12 CPUs with requested memory
  `60G`, with elapsed times from `00:58:01` to `04:07:29`. No task is missing or duplicated.
  Independent finalist-evidence and final-package review is required before final submission.
- Independent read-only finalist completion and final-package review passed at
  `2026-11-10T00:51:23-07:00` with no concern. The reviewer verified all 72 leaves, 360 recorded
  artifact hashes, 288 metric rows, exact technical/scope gates, and 20 execution-manifest entries.
  Independent aggregation of all 120 finalist fits predicts candidate 19 as best and selected,
  with 6/6 component improvements over control and neither resolution both worse. The final
  submitted copy is byte-identical and contract-exact at script `7d3a3e7c...72652`, config
  `72e0a671...8718`, and execution manifest `3870eecb...2f66`; `attempt_1` does not exist.
- Final attempt 1 submission from the exact reviewed run-directory copy returned job `24595272`
  at `2026-11-10T00:51:51-07:00`. Immediate identity matched `chopinsong/standard`, 8 CPUs and
  derived 40 GB, four hours, exact command/workdir/logs, stdin `/dev/null`, and the locked final,
  screen, and finalist attempt plus config/manifest exports; initial state `PENDING (Priority)`.
- Final job `24595272` completed `0:0` in `00:03:36`, TotalCPU `02:56.389`, 8 CPUs, batch
  MaxRSS `27700376K`, node `r7u07n1`. The aggregation and fresh-process validation both report
  candidate 19 selected with decision `sr_refined_configuration_selected`, replacement gate pass,
  6/6 component improvements, 240 independently recomputed metric rows, zero fixed-test access,
  and no release. Independent final-result review is pending before closeout.
- Independent final-result review passed with no concern. It verified all 240 unique rows against
  their originating leaves, reproduced rank order `19,23,15,26,11,0`, all ranking tie-breaks,
  the 6/6 improvement count, both-worse guards, canonical decision, and four final hashes. Candidate
  19 is `(96,48)`, tanh, alpha `1.0`, with frozen Adam controls. Final artifact hashes are metrics
  `6e43c47f...ffbf`, ranking `948f32df...9e5c`, selection `ebd1e541...edf5`, and validation
  `4c883485...617`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: `sr_refined_configuration_selected`; freeze candidate
  19 for separately approved later work. The matched-control gate passed with 6/6 improvements and
  neither resolution both worse. No all-819 fit or release is authorized.
- Limitations: fixed-upstream, two-site, development-only configuration selection; no fixed test.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; later SR robustness,
  release, fixed-test evaluation, all-819 fitting, or downstream work requires separate planning
  and consolidated kickoff approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter010/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] One authorized local no-push closeout commit created and post-commit verified
