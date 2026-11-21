# iter009 - ABBY/JERC SR implementation and configuration selection

## Status

- Iteration ID: `iter009`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter009_abby_jerc_sr_config`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-04T02:47:16-07:00`
- Closed: `2026-11-06T02:35:17-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: implement the pooled ABBY/JERC hourly SR stage from published predicted C/N and
  same-hour predicted GPP, validate the deterministic three-stage interface, screen 24 locked MLP
  candidates, and freeze the best technically eligible configuration using development-only data.
- Scope: 44 ordered features; physical SR; 819 development members; exact 20 balanced 655/164
  selection splits; 24 candidates on eight screen splits; candidate 0 plus five non-control
  finalists on all 20; pooled hourly and complete-day selection metrics.
- Interpretation: `fixed_upstream_sr_stage`, not end-to-end held out. Both published upstream
  products were fitted on all 819 development members.
- Exclusions: 205 fixed-test members; spinup/GPP refitting; lagged GPP alternatives; site category;
  all-819 SR fit/release; uncertainty; observations; optimization/MCMC; plan edits; push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Full finalized Iter009 package approved.`; `2026-11-04T02:47:16-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Four normal submissions: combined Unit1 preflight/cache/smoke, 192-leaf screen, 72-leaf finalists, combined final aggregation/validation. Continue through terminal accounting, selection, records, four-record validation, and one no-push commit. Stop only at completed closeout or a workflow-defined fresh-authority condition. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6; aligned; no deviation. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config/runs/{unit1,screen,finalists,final}` with immutable attempts. Preserve raw cache, decision evidence, predictions, models, logs, failures; remove only validated successful per-fit scaled scratch/runtime caches. `/xdisk` temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Snapshot `39b05495...187a`; split `99467dea...0fce`; C/N `9e2d5be...fdb5`; GPP handoff `c905fc60...98bb`; selection splits `7644ed38...ace0`; exact model/metrics/ranking contract below; zero fixed-test access; no release. |
| Lifecycle authority | Initialization; shared/iteration code and focused tests; exact directories; independent read-only review before every submission; four normal submissions and bounded retries; monitoring/accounting; evaluation; records; validation; cleanup limited as above; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 6 CPU/30 GB/6 h, cap 8/40/8; array leaves 12 CPU/60 GB/16 h `%20`, cap 16/80/20; final 8 CPU/40 GB/4 h, cap 12/60/6. Three additional submissions per logical unit; Unit2 shares three. Every initial/retry submission requires reviewer pass. Supported wait and job-scoped monitoring through terminal `sacct`. |
| Cancellation scope | Recorded Iter009 jobs only if duplicate, outside contract, invalidated by common/upstream defect, unsafe, or threatening storage. Pending/slow alone is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` above. |
| Closeout branch | One scoped local no-push commit authorized. |

The approved four-submission design specializes Workflow Section 4D by placing the bounded
no-training preflight and substantive Unit1 cache/smoke phases in one allocation. The Unit1 driver
executes them strictly in order and exits before cache generation or smoke if preflight fails. This
specialization changes submission packaging only; it does not weaken the preflight gate.

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | SR truth, forcing, parameters, surfaces | `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a` |
| Global split | 819/205 boundary | `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce` |
| Spinup handoff | predicted C/N | `9e2d5be4809ee7c9053baf70ad7574ca0b5cc2afc4a15b6006663a0fb8fafdb5` |
| GPP release/handoff | predicted same-hour GPP | manifest `57cc18b0...70d1`; handoff `c905fc60...98bb` |
| Selection splits | exact 20 balanced splits | file `7644ed38...ace0`; design `0b343378...6ecb` |
| Historical SR config | candidate-0 provenance | artifact `8d139b32...4553`; evidence `65cc3344...f50` |

## Acceptance Gates and Decision Rule

- Features: GPP's ordered 43 plus final `GPP_predicted`; target physical SR with fit-only
  standardization, inverse scaling, no log, and no clipping.
- Candidate 0 is `(128,)` ReLU/Adam alpha `1e-3`; candidates 1--23 are Iter007 IDs 1--23.
  Frozen controls: adaptive LR `0.001`, 500 iterations, early stopping 0.1, patience 10, tol
  `1e-4`, batch auto, shuffle, seed 42.
- Screen split IDs: `1,3,7,10,12,13,14,16`; remaining: `0,2,4,5,6,8,9,11,15,17,18,19`.
  Candidate 0 is mandatory; five eligible non-controls advance. Fewer than six eligible stops.
- Technical eligibility: complete expected fit; finite predictions; full coverage; exact identities;
  reload within `rtol=atol=1e-6`; zero production convergence warnings; fixed-test access false.
- Selection statistics at hourly and complete-day (`24/24`, `sum(hourly)/24`) pooled resolution:
  R2 q10 high, RMSE q90 low, median absolute split bias low. Convert each to ordinal normalized
  rank with average ties; rank by best worst score, mean score, lower split-composite variability,
  fewer parameters, candidate ID. Sitewise metrics, MAE, residual spread/quantiles are diagnostics.
- No absolute performance gate. Decision `sr_configuration_selected` only after complete eligible
  evidence and independent final reproduction; otherwise record the applicable insufficient or
  failed decision. Never publish a release.

## Provenance and Job Ledger

| Work unit | Canonical/submitted material | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- |
| Unit1 | manifest `906f283f...e6b7`; exact submitted copies | `<root>/runs/unit1`; `unit1_24524508.*` | job `24524508` | `COMPLETED 0:0` | review pass; identity matched; eligible |
| screen | manifest `96919817...ddb6`; resolved config `257cfcfb...1120`; exact submitted copies | `<root>/runs/screen`; `screen_24524587_*.{out,err}` | array `24524587_0-191%20` | 192 `COMPLETED 0:0`; eligible | identity matched; full accounting reconciled |
| finalists | manifest `dbcd4d68...ee15`; config `257cfcfb...1120`; exact submitted copies | `<root>/runs/finalists`; `finalists_24536618_*.{out,err}` | array `24536618_0-71%20` | 72 `COMPLETED 0:0`; eligible | full accounting and artifacts reconciled |
| final | manifest `dbcd4d68...ee15`; config `257cfcfb...1120`; exact submitted copies | `<root>/runs/final`; `final_24548424.{out,err}` | job `24548424` | `COMPLETED 0:0`; pass | candidate 21 selected and independently validated |

## Independent Read-Only Review

- Reviewer: independent read-only agent `iter009_unit1_review`
- Reviewed source hash: execution manifest `906f283fa0acb75635b70d7c667627ad6d7500ebcd4140eaa21e2e947d4de6b7`
- Outcome: `pass` after one blocked review and correction; no submission preceded the pass.
- Findings and primary-agent response: initial review blocked retry safety because a retried Unit1
  would retain the attempt-1 raw path. The resolved configuration now binds the actual immutable
  attempt path. The approved combined-preflight specialization is explicit and preflight remains
  the first hard gate. Re-review verified sources and submitted copies byte-identical and passed.
- Screen reviewer outcome: `block` on manifest `ae1b253c...9455` before submission because the
  script redundantly specified both 12 CPUs and 60 GB, which the Puma standard-ratio profile
  prohibits. The reviewer also recommended an exact run-directory assertion. No scheduler state
  was changed. The primary agent removed redundant memory directives from all unsubmitted scripts
  (12 CPUs derive 60 GB; 8 derive 40 GB), added exact run-directory assertions, regenerated
  manifest `96919817...ddb6`, and rematerialized the screen package for mandatory re-review.
- Screen re-review outcome: `pass` with no concerns on manifest
  `969198175068e70da97f39ad7357af1c0fe5ef1b3d909b6f93681fb3a5ccddb6`. The reviewer
  verified exact submitted-copy/config equality, 192 unique mappings, CPU-derived memory,
  immutable attempt/run paths, exclusions, and technical eligibility/cleanup gates.
- Finalist review independently reproduced all 192 screen leaf hashes/gates, ranking order,
  finalists `[0,21,2,8,16,13]`, and fingerprint `c2210049...10c2`, but blocked the unsubmitted
  package because repository selection code ran before identity checks. The primary agent moved
  all run/config/manifest/script/source gates before config parsing or Python in the finalist
  script, applied the same ordering proactively to final, regenerated manifest `dbcd4d68...ee15`,
  and rematerialized the finalist package for mandatory re-review. No job was submitted.
- Finalist re-review outcome: `pass` with no concerns on manifest
  `dbcd4d68eb355d6613fc7e75f042b04ec88f0bc7c6060bc192147aaad583ee15`; exact package
  equality, identity-first ordering, isolated caches, 72 mappings, resources, and gates passed.
- Final-job review outcome: `pass` with no concerns on manifest `dbcd4d68...ee15`. The reviewer
  independently verified all 72 finalist leaf hashes/gates, reproduced candidate 21 as the
  20-split leader, audited the approved pooled ordinal rule, and confirmed the fresh validator
  independently recomputes 240 metric rows from raw truth and physical predictions.

## Execution and Diagnostics

- Unit1 static validation, preflight, 100,442,160-row raw-cache validation, interface contract,
  focused tests, and three-candidate smoke test passed. The eligible resolved configuration SHA-256
  is `257cfcfb9e46466ec1dca47dc8734a228d09bdb9023d88c4da01e2d8cea31120`; it binds the
  immutable attempt-1 raw directory and its full layout/X/y/time hashes.
- Unit1 submission command used the locked run-directory copy and exported attempt `1`, config
  `c3c4a919...63f`, and manifest `906f283f...e6b7`; immediate job identity matched the contract.
- Screen submission command: `/usr/bin/sbatch --parsable --export=ALL,ITER009_ATTEMPT=1,` plus
  config `257cfcfb...1120` and manifest `96919817...ddb6`, then
  `./submit_screen_iter009.slurm`; returned array job `24524587`.
- Immediate scheduler identity matched `chopinsong/standard`, 12 CPUs with Puma-derived 60 GB,
  16-hour limit, `%20` throttle, exact command/workdir, and locked attempt/config/manifest exports.
- Screen terminal accounting contains exactly 192 array-task records, all `COMPLETED 0:0`.
  Exactly 192 leaf reports, metric files, and prediction files exist; all reports pass, cover all
  24 candidates on splits `1,3,7,10,12,13,14,16`, contain zero production convergence warnings,
  preserve fixed-test/release exclusions, and confirm successful scaled-scratch cleanup.
- Deterministic screen selection independently invoked from the locked source selected finalist
  IDs `[0,21,2,8,16,13]` with screen fingerprint
  `c22100491c93a3ff653720347fa2f9ac7ddd83f8ba4d46793e5488ab208910c2`.
  An initial sandbox-only read failed before evaluation because the home cache was read-only; the
  same command succeeded with task-specific `/tmp` caches and changed no run or scheduler state.
- Finalist submission command used the locked run-directory copy with attempt `1`, screen attempt
  `1`, config `257cfcfb...1120`, and manifest `dbcd4d68...ee15`; returned array job `24536618`.
- Immediate finalist identity matched `chopinsong/standard`, 12 CPUs with Puma-derived 60 GB,
  16-hour limit, `%20`, exact command/workdir, and all locked exports; initial state was priority.
- User requested stopping active monitoring at `2026-11-05T00:20:24-07:00`; the attached monitor
  was terminated without changing scheduler state. Final snapshot: tasks 0--9 running for about
  `00:02:51`, tasks 10--71 pending by priority, no terminal task records yet. Exact resume action:
  query job-scoped `squeue` and full 72-element `sacct`, then continue monitoring/reconciliation.
- On user-directed resume, finalist accounting contained exactly 72 task records, all
  `COMPLETED 0:0`. Exactly 72 logs, task maps, reports, metric files, and prediction files cover
  candidates `[0,2,8,13,16,21]` on splits `[0,2,4,5,6,8,9,11,15,17,18,19]`. All reports pass,
  contain zero convergence warnings, preserve fixed-test/release exclusions, and confirm scratch
  cleanup; every stdout has `ITER009_LEAF_OK` and every timed command has exit status zero.
- Final submission command used the locked run-directory copy with final/screen/finalist attempts
  `1/1/1`, config `257cfcfb...1120`, and manifest `dbcd4d68...ee15`; returned job `24548424`.
- Immediate final identity matched `chopinsong/standard`, 8 CPUs with Puma-derived 40 GB,
  four-hour limit, exact command/workdir, and all locked exports; initial state was priority.
- Final job `24548424` completed `0:0` in `00:01:45` with TotalCPU `01:04.466`, 8 allocated
  CPUs, requested memory 40 GB, batch MaxRSS `10810132K`, and node `r7u06n1`. Selection and fresh
  validation success markers are present; the only stderr message is an unrelated ArviZ future
  warning.
- Authoritative terminal accounting: job `24524508` `COMPLETED 0:0`, elapsed `00:02:25`,
  TotalCPU `01:26.730`, 6 allocated CPUs, requested memory 30 GB, node `r7u03n1`; batch MaxRSS
  `19773068K`. The only stderr warnings were the expected non-production two-iteration smoke-fit
  convergence warnings; the production warning gate was not exercised.
- The first screen review blocked redundant CPU-plus-memory directives under the Puma profile.
  Corrected unsubmitted scripts request 12 CPUs for array leaves (derived 60 GB) and 8 CPUs for
  final (derived 40 GB), and now assert their approved run directories. The regenerated execution-
  manifest SHA-256 is `969198175068e70da97f39ad7357af1c0fe5ef1b3d909b6f93681fb3a5ccddb6`.
  Unit1's submitted manifest remains preserved as execution provenance.
- Failure, rejection, retry, or cancellation evidence: none.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Overall decision: `sr_configuration_selected`.
- Selected candidate: `21`, hidden layers `(64,32)`, `tanh`, alpha `1e-4`, with the frozen Adam
  controls recorded above. All six finalists were eligible; final order was `21,13,8,2,16,0`.
- Candidate 21 led every normalized selection component: worst normalized score `1.0` and mean
  normalized score `1.0`. Its hourly R2 q10/RMSE q90/median absolute bias were
  `0.736201/1.119896/0.027569`; daily values were `0.737210/1.098576/0.027569`.
- Final evidence contains 240 validation metric rows. Selection report
  `4c414784...931c` and fresh validation `8a0138fe...967f` agree on candidate 21; the validator
  recomputed all 240 rows from raw physical SR truth and hashed predictions.
- No absolute performance gate was applied. The result freezes a development-only SR
  configuration; it does not authorize all-819 fitting, uncertainty, release, fixed-test use, or
  downstream likelihood/MCMC work.
- Closeout conclusion: all four approved submissions completed successfully, no retry submission
  was consumed, no job is active or unaccounted, and no release was created.
- Limitations: two sites; fixed in-sample upstream C/N/GPP; reused selection splits; finite matrix;
  temporary unbacked storage; no fixed-test/release/full-chain uncertainty.
- Campaign-plan amendment recommendation: `none`.
- Next direction: explicit terminal declaration. Any all-819 SR fit, robustness/uncertainty,
  release, fixed-test evaluation, or downstream full-chain work requires a separately planned and
  approved iteration.

## Explicit Terminal Declaration

Iter009 is complete. Unit1 `24524508`, screen array `24524587`, finalist array `24536618`, and
final job `24548424` are authoritatively terminal; no job is active or unaccounted. Candidate 21 is
selected for the SR stage using development-only fixed-upstream evidence. No next iteration
proposal is authorized.

## Closeout Validation and Identity

- Validator: `development/three_stage_surrogate/slurm/iter009/validate_closeout_iter009.sh`
- Command: `bash development/three_stage_surrogate/slurm/iter009/validate_closeout_iter009.sh --active-job-count 0`
- Result: `ITER009_FOUR_RECORD_VALIDATE_PASS`
- Closeout mode: `committed`; expected parent
  `2b22a3ec11fd8935bc7b434357ead6acc8449252`; expected subject
  `Select SR surrogate configuration`; no push authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter009/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified local no-push commit
