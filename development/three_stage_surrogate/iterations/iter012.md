# iter012 - SR surrogate GPP-input ablation

## Status

- Iteration ID: `iter012`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter012_abby_jerc_sr_gpp_ablation`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-11T19:21:53-07:00`
- Closed: `2026-11-12T15:37:51-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6, SR development and configuration selection
- Alignment: `aligned`; the user-directed ablation supersedes Iter011's planning-only robustness
  recommendation but remains a development-only input-dependence experiment.
- Approved deviation: `none`

## Finalized Plan

- Objective: determine whether published same-hour predicted GPP improves SR relative to omitting
  GPP and whether replacing predicted GPP with authoritative same-hour ELM GPP improves SR.
- Arms: A has 43 features and no GPP; B has the established 44 features with predicted GPP; C has
  the same 43 base features plus true GPP and is a non-deployable diagnostic.
- Frozen model: `(96,48)`, `tanh`, alpha `0.01`, with Iter011 Adam controls unchanged.
- Design: ABBY/JERC, 819 development members, seed `20261112`, 20 fresh balanced 655/164 splits
  shared by all arms, and exactly 60 production fits. The fixed 205-member test is excluded.
- Work units: Unit1 identity/preflight/splits/alignment/smoke; one 60-task production array; final
  aggregation, independent validation, decision, and closeout.
- Interpretation: fixed-upstream SR-stage validation, not full-chain held-out performance. No
  upstream retraining, hyperparameter search, cross-fitting, all-819 fit, release, MCMC, plan edit,
  automatic architecture change, push, or fixed-test access.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approve the complete Iter012 kickoff package and runtime contract. Besides, for this iteration, standby after you submit the production array job and wait for me to ping you.`; `2026-11-11T19:21:53-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Three normal submissions: Unit1; production `0-59%20`; final. After production submission and identity confirmation, record a voluntary checkpoint and stop active monitoring until the user pings. Then resume through terminal accounting, evaluation, validation, records, and closeout. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6; aligned; no deviation. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; CPU only; `OLMT_puma`. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter012_abby_jerc_sr_gpp_ablation/runs/{unit1,production,final}` with immutable attempts. Reuse Iter009 raw cache read-only; retain about 7 GiB maximum; transient scratch about 320 GiB; remove only validated successful scaled/runtime scratch. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Snapshot `39b05495...187a`; split `99467dea...0fce`; C/N `9e2d5be...fdb5`; GPP `c905fc60...98bb`; raw cache identities below; arms A/B/C only; seed-20261112 20-split design; exact 60 fits; locked daily-RMSE/site-consistency rule; zero fixed-test access; no release. |
| Lifecycle authority | Initialization; focused code/tests/scripts/config/manifests/validators; exact directories; independent read-only review before each submission and for results/closeout; three submissions and bounded retries; job-scoped monitoring/accounting; evaluation; records; validation; limited cleanup; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 6 CPU/30 GB/6 h, cap 8/40/8; production leaves 12 CPU/60 GB/16 h `%20`, cap 16/80/20; final 8 CPU/40 GB/4 h, cap 12/60/6. At most three additional same-scope submissions per logical unit for scheduler/node/transport/launch/resource failures; sparse array retries only. One reviewed minimal Unit1 preflight/packaging correction. Application/code/interface/schema/data/dependency/numerical/science failures after substantive work stop for fresh authority. |
| Cancellation scope | Recorded Iter012 jobs only if duplicate, outside contract, invalidated by a proven common defect, unsafe, or threatening storage; pending or slow alone is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` above. |
| Closeout branch | At most one scoped local no-push commit, proposed subject `Complete SR GPP input ablation`. |

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | SR/GPP truth, forcing, parameters, surfaces | `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a`; ABBY input `85f52690...c9c1`; JERC `a846c731...c0cb6` |
| Global split | 819/205 boundary | `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce` |
| Spinup release/handoff | fixed predicted C/N | manifest `69f840f7...f2dc`; handoff `9e2d5be...fdb5` |
| GPP release/handoff | fixed predicted same-hour GPP | manifest `57cc18b0...70d1`; handoff `c905fc60...98bb` |
| Iter009 raw cache | 44-feature SR design and truth | layout `172c2f4b...b0b6`; X `c648952a...5cf`; y `35697d26...477`; time `8f2efdef...52e` |
| Prior SR splits | exact-match exclusions | Iter009 `7644ed38...ace0`; Iter010 `34a33000...ae43`; Iter011 `b9e6a4e8...8a8a` |
| Repository source | preparation base | `70cd248c07b0bea9d49bfe25c55870237a5939a6` |

## Acceptance Gates and Decision Rule

- Unit1 must produce 20 unique seed-`20261112` splits, each 655/164, with validation appearance
  counts four or five, no fixed-test overlap, and no exact validation-set match to Iter009--011.
- A uses exactly the first 43 cache columns and a 43-input scaler; B uses the exact 44-column cache;
  C uses the first 43 plus aligned true ELM GPP for both training and validation. Each arm has a
  separate ordered feature schema and hash. No complete feature-matrix copy is allowed.
- All 60 fits must pass identity, coverage, finite unclipped prediction, serialization replay at
  `rtol=atol=1e-6`, zero convergence warnings, scratch cleanup, and prohibited-scope gates.
- Retain train/validation by hourly/daily by ABBY/JERC/pooled R2, RMSE, MAE, and signed bias.
  Across splits report mean, median, sample SD, q10, q90, and training-validation gaps. Daily
  values require complete 24-hour means.
- Paired RMSE improvement is comparator minus candidate. Report mean, median, and wins for A/B,
  B/C, and A/C. A consistent practical improvement requires positive mean and median pooled daily
  RMSE improvement, at least 14/20 wins, at least 2% relative mean improvement, and no meaningful
  site deterioration. Meaningful site deterioration is at least 5% worse site-mean daily RMSE plus
  at least 14/20 site losses.
- Select B only if B passes against A; select A only if the reverse passes. Otherwise record
  `deployable_architecture_preference_inconclusive` and leave B as the historical baseline. C is
  never deployable. C is substantially more informative than B only if it passes the consistency
  rule and improves mean pooled daily RMSE by at least 5%. C is not a mathematical upper bound.
- Final validation independently recomputes all 360 validation metric rows and reproduces tables,
  paired decisions, identities, hashes, fixed-test exclusion, and no-release state.

## Provenance and Job Ledger

| Work unit | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| Unit1 | `<root>/runs/unit1`; `unit1_{24618587,24621652,24623717}.{out,err}` | jobs `24618587`, `24621652`, `24623717` | attempts 1-2 `FAILED 1:0`; attempt 3 `COMPLETED 0:0` | Unit1 validation pass; 54 s, 6 CPUs, batch MaxRSS `2368556K`, 30 GB requested; manifest `e1b9f152...32eeb` |
| production | `<root>/runs/production` | parent `24623755`, `0-59%20` | all 60 tasks `COMPLETED 0:0` | 60 leaf reports and success markers; no retry; longest `05:24:23`; maximum batch RSS `48180492K` of 60 GB |
| final | `<root>/runs/final`; `final_24630916.{out,err}` | job `24630916` | attempt 1 `COMPLETED 0:0` | 65 s; batch MaxRSS `5920960K` of 40 GB; aggregation, independent validator, and result review pass |

`<root>` is the approved output root above.

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter012_unit1_review`
- Reviewed source hash: execution manifest `7cf572f75c20008e8359d8b73574f175661ea0da0466c567db87309d77eba387`
- Outcome: `pass` with no concerns at `2026-11-11T19:32:01-07:00`
- Findings and primary-agent response: exact canonical/submitted copies, identities, A/B/C feature
  construction, training-only scalers, true-GPP alignment and compact extraction, split freshness,
  fixed-test exclusion, task mapping, resources, prohibited scope, and checkpoint wording pass.
  Reviewer performed no edits, repository Python, directory creation, or scheduler action.
  Mandatory correction re-review passed with no concerns at `2026-11-11T23:10:44-07:00`:
  only the test's expected exception changed, all corrected hashes and current submitted copies
  pass, attempt-1 identities/logs remain preserved, and attempt-2 output is absent.
  At that checkpoint, a further launch-only correction required mandatory re-review: attempts 1-2 and their exact
  packages remain preserved; both Slurm entry points now use repository-root module launches; no
  model, data, feature, split, resource, or scientific contract changed.
  Mandatory attempt-3 re-review passed with no concerns at `2026-11-12T04:26:01-07:00`:
  the preserved attempt-2 package and logs match recorded hashes, exactly the Unit1 and production
  launch lines changed, current canonical/submitted candidate copies match, manifest
  `e1b9f152...32eeb` verifies, static shell syntax and `git diff --check` pass, and the correction
  remains within the approved same-scope launch-failure retry boundary. The reviewer made no
  edits, repository-Python calls, directory changes, or scheduler calls.
  Independent Unit1 completion and production-package review passed with no concerns at
  `2026-11-12T04:35:17-07:00`: terminal success and the eligible-only inventory passed; hashes
  were recomputed; all 20 splits independently satisfy 655/164 disjoint partitions over the same
  819 development members, validation appearances 4-5, zero fixed-test overlap, and zero exact
  validation-set matches to Iter009-Iter011; A/B/C schemas and true-GPP provenance passed; the
  exact production package, `0-59%20` mapping, 12 CPU/60 GB/16 h resources, prohibitions, and
  post-submission stop boundary passed. The reviewer made no mutations or scheduler calls.
  Production-completion evidence passed independent review at `2026-11-12T15:23:34-07:00`, but
  the first final-package review rejected submission because the final script did not assert locked
  production attempt `1` and the independent validator checked only two of five prohibited leaf
  scope flags. The rejected exact candidate is preserved under `runs/final/reviewed_candidate_1`.
  The minimal correction adds the attempt assertion; independently enforces fixed-test, spinup,
  GPP, all-development-fit, and release flags; and verifies/records fixed-upstream, non-upper-bound,
  and no-performance-gate interpretation flags. No aggregation math, data, training output,
  resource request, or scientific rule changed. Mandatory re-review was required before submission.
  Mandatory correction re-review passed with no concerns at `2026-11-12T15:26:22-07:00`:
  exactly the validator and final script hashes changed, all manifest entries verify, production
  attempt `1` and all five prohibited-scope flags are independently enforced, interpretation flags
  are verified and recorded, exact submitted copies match, and the prior rejected package remains
  intact. The reviewer made no mutations or scheduler calls.
  Independent result review passed with no concerns after final completion: the reviewer
  independently checked the primary pooled-daily ranking, all three paired comparisons, both-site
  deterioration rules, all required output inventories and hashes, the 360-row recomputation,
  fixed-test and prohibited-scope flags, and the diagnostic-only interpretation of C. The result
  is `deployable_arm_B_selected`; no scientific or closeout correction was required.
  Final four-record closeout review passed with no concerns: the report, summary, registry, and
  handoff agree; every compact hash and required row count verifies; the validator is sound; the
  worktree is restricted to the approved Iter012 paths; and the proposed parent/subject are exact.
  The reviewer made no mutations, repository-Python calls, directory changes, or scheduler calls.

## Execution and Diagnostics

- Static validation: execution-manifest verification, JSON and shell syntax, Python AST parsing,
  `git diff --check`, and exact submitted-copy comparisons passed before review.
- Preflight: Unit1 attempt 1 passed all execution-manifest identities, then the focused test suite
  stopped before data access because `test_invalid_arm_rejected` expected `RuntimeError` while the
  repository `require()` contract raised `ValueError`.
- Unit1 attempt 2 passed the corrected manifest and all four focused tests, then stopped before
  data access because the absolute-path script launch did not place the repository root on
  `sys.path` (`ModuleNotFoundError: development`). The launch-only correction invokes both Unit1
  and production entry points with `python -m` from the already locked repository root.
- Exact submission commands: Unit1 attempt 1 used locked exports, stdin `/dev/null`, and
  `sbatch --parsable ./submit_unit1_iter012.slurm`; returned `24618587` at
  `2026-11-11T19:32:23-07:00`. Corrected attempt 2 used unchanged config/script, corrected manifest,
  and returned `24621652` at `2026-11-11T23:11:06-07:00`. Launch-corrected attempt 3 used config
  `664f86a9...5a96`, manifest `e1b9f152...32eeb`, attempt token 3, stdin `/dev/null`, and returned
  `24623717` at `2026-11-12T04:26:31-07:00`.
- Job identity checks: Unit1 matches `chopinsong/standard`, 6 CPUs with Puma-derived 30 GB,
  six-hour limit, exact command, workdir, logs, stdin, and locked exports for both attempts;
  attempt 2 initial state priority.
- Queue and terminal accounting: Unit1 job `24618587` is terminal `FAILED 1:0`, elapsed `00:00:15`,
  6 CPUs, batch MaxRSS `193664K`, requested memory 30 GB. Job `24621652` is terminal `FAILED 1:0`,
  elapsed `00:00:21`, 6 CPUs, batch MaxRSS `193704K`, requested memory 30 GB, node `r7u12n1`.
- Resource diagnostics: attempts 1-2 failed before substantive resource or data use.
- Failure, rejection, retry, or cancellation evidence: classified as the approved one-time minimal
  Unit1 preflight/test correction. Change only the expected exception from `RuntimeError` to
  `ValueError`, refresh the manifest, preserve attempt-1 identities, require independent re-review,
  and submit attempt 2. Retry submission 1 will be consumed.
- Attempt 2 is classified as an approved same-scope launch failure. Preserve the exact attempt-2
  package and logs, change only both Python entry points to repository-root module launches,
  refresh the manifest to `e1b9f1529766b18bca8c250df6e841a4c40771ad1fdaeb76d3f53c54a0a32eeb`,
  require independent re-review, and submit attempt 3. Retry submission 2 is consumed.
- Attempt 3 completed `0:0` in `00:00:54` on 6 CPUs with batch MaxRSS `2368556K` against 30 GB.
  Stdout contains `ITER012_UNIT1_OK arms=3 splits=20 production_fits=60 fixed_test=false`; all four
  focused tests passed. Static artifact validation confirms the eligible marker only, all required
  JSON and compact true-GPP files, exact resolved/split/schema/true-GPP hashes, 20 fresh 655/164
  splits with validation appearances 4-5 and zero prior exact matches, A/B/C feature counts
  43/44/44, C non-deployable, fixed-test/upstream-execution/release flags false, full raw and
  true-GPP hashes, and finite reloadable smoke fits for all arms.
- Locked production package materialized with resolved config `13a20f47...d188`, execution manifest
  `e1b9f152...32eeb`, and production script `155d55de...a29`; exact canonical/submitted comparisons,
  shell syntax, absent attempt-1 output, and `git diff --check` pass. Independent review passes.
- Production submission used locked exports, stdin `/dev/null`, and
  `sbatch --parsable ./submit_production_iter012.slurm`; returned parent `24623755` at
  `2026-11-12T04:35:42-07:00`. Immediate identity validation passes exact array `0-59%20` with
  throttle 20, `chopinsong/standard`, 12 CPUs and Puma-derived 60 GB per leaf, 16-hour limit,
  exact command/workdir/logs/stdin, and attempt/config/manifest exports. Initial parent state was
  `PENDING` at submission; no production task result had yet been inspected.
- User-requested standby checkpoint entered immediately after identity confirmation. Active
  monitoring is stopped. Resume only after user ping with job-scoped
  `squeue --job=24623755 -r -o "%i|%T|%j|%M|%R"` and complete parent accounting via
  `sacct --jobs=24623755 --parsable2 --noheader --format=JobID,JobIDRaw,ArrayTaskID,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,ReqMem,NodeList`.
- User resumed the workflow after reporting completion. Job-scoped `squeue` was empty and complete
  Puma accounting using `JobID`/`JobIDRaw` (the site does not support the requested `ArrayTaskID`
  field) proves all 60 tasks `COMPLETED 0:0`. Elapsed times ranged `01:15:16`--`05:24:23`; maximum
  batch MaxRSS was `48180492K` against 60 GB. No sparse retry is required.
- Primary production validation finds exactly 60 arm/split directories, 60 leaf reports, 60
  `ITER012_LEAF_OK` markers, 12 complete metric rows per leaf, zero convergence warnings, finite
  serialized predictions, expected 43/44/44 arm identities, prohibited-scope flags false, and
  retained physical predictions/metrics/hashes for aggregation.
- Final aggregation and independent-recomputation package is materialized with resolved config
  `13a20f47...d188`, corrected manifest `bc83f399...2d9b3`, and corrected script
  `3611b6a4...0400`. Static AST/shell, manifest, exact submitted-copy, absent attempt-1, and
  `git diff --check` gates passed; mandatory correction re-review was required before submission.
- Final attempt 1 used locked exports, production attempt `1`, stdin `/dev/null`, and
  `sbatch --parsable ./submit_final_iter012.slurm`; returned job `24630916` at
  `2026-11-12T15:26:40-07:00`. Immediate identity validation passes `chopinsong/standard`, 8 CPUs
  and Puma-derived 40 GB, 4-hour limit, exact command/workdir/logs/stdin, and all locked exports;
  initial state at submission was `PENDING (Priority)`.
- Final job `24630916` completed `0:0` in `00:01:05` on 8 CPUs with batch MaxRSS `5920960K`
  against 40 GB. Stdout contains both `ITER012_AGGREGATE_OK` and
  `ITER012_FINAL_VALIDATE_OK`; the validator independently reproduced all 360 validation rows.
- Primary result: deployable arm B is selected. Mean pooled daily validation RMSE is A `0.835770`,
  B `0.771187`, C `0.751254`. B improves on A by mean `0.064583` (`7.727%`), median `0.052538`,
  and `19/20` wins without meaningful ABBY/JERC deterioration. C improves on B by mean `0.019933`
  (`2.585%`), median `0.017654`, and `12/20` wins, so it is not substantially more informative
  under the frozen 5%/14-win rule. C improves on A by `10.112%` and `19/20` wins, showing useful
  GPP explanatory power while remaining non-deployable and not a mathematical upper bound.
- Required outputs exist with validated hashes: 720-row metric distribution, complete summary and
  gap evidence, pooled overall and ABBY/JERC validation tables, 72-row paired summary, R2/RMSE
  plots, selection/validation JSON, and concise interpretation. At that checkpoint independent
  result review and repository closeout had not yet occurred; both subsequently passed.
- The user resumed after the production checkpoint and later confirmed the jobs were done;
  monitoring, terminal accounting, final validation, independent result review, and closeout then
  proceeded under the approved runtime contract.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `deployable_arm_B_selected`. Retain arm B, the
  deployable 44-feature published predicted-GPP configuration. B improves mean pooled daily
  validation RMSE over A by `0.064583` (`7.727%`), median `0.052538`, with `19/20` wins and no
  meaningful site deterioration. C improves over B by only `0.019933` (`2.585%`), median
  `0.017654`, with `12/20` wins, so true GPP is not substantially more informative under the
  frozen rule. C versus A improves `10.112%` with `19/20` wins, showing useful GPP explanatory
  power while C remains non-deployable and not an upper bound. Proceed to separately approved
  fresh SR robustness testing rather than another GPP-input or architecture experiment.
- Limitations: fixed-upstream, two-site, development-only evidence; C is non-deployable and not an
  upper bound; repeated validation sets overlap; `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`; the exploratory no-GPP arm and altered sequence
  were explicitly approved and remain within campaign-plan progression item 6.
- Next action: none within Iter012. No next iteration is authorized; fresh SR robustness requires
  a separate consolidated kickoff package and approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter012/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] One authorized local no-push closeout commit created and verified
