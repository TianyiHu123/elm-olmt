# iter011 - Focused SR capacity versus regularization experiment

## Status

- Iteration ID: `iter011`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter011_abby_jerc_sr_capacity_regularization`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-11T02:35:29-07:00`
- Closed: `2026-11-11T18:37:48-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: compare exactly five tanh SR MLP configurations on 20 new matched development-only
  splits to isolate evidence for capacity, weaker L2 regularization, or both.
- Inputs: snapshot r0001; exact 819/205 boundary; published predicted C/N and same-hour GPP;
  validated Iter009 44-feature physical-SR raw cache. Upstream models remain fixed.
- Matrix: A `(96,48)`/alpha `1.0`; B `(96,48)`/`0.01`; C `(128,64)`/`1.0`;
  D `(128,64)`/`0.01`; E `(128,64)`/`0.1`; tanh and frozen Iter010 Adam controls throughout.
- Design: seed `20261111`; 20 unique balanced 655/164 splits shared by all candidates; exactly
  100 production fits and no screening stage.
- Selection: lowest mean pooled daily validation RMSE, then pooled hourly RMSE, mean absolute
  daily validation bias, and parameter count. Site/tail/stability flags are diagnostic only.
- Exclusions: fixed test; upstream execution/refit; feature or optimizer changes; ablations;
  cross-fitting; all-819 SR fit; release; uncertainty; MCMC; plan edit; push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Approved the complete package.` plus production-monitoring checkpoint instruction; `2026-11-11T02:35:29-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Three normal submissions: Unit1 identity/preflight/splits/cache/tests/smoke; one 100-leaf production array; final aggregation/independent validation. Continue through closeout except checkpoint after confirmed production submission until user wake. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6; aligned; no deviation. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; CPU only. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter011_abby_jerc_sr_capacity_regularization/runs/{unit1,production,final}` with immutable attempts. Reuse Iter009 raw cache read-only. Retain at most about 12 GiB; transient scratch at most about 320 GiB; remove only validated successful per-fit scaled/runtime scratch. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; A--E only; seed-20261111 20-split design; exact 100 production fits; pooled daily RMSE primary rule and locked tie-breakers; zero fixed-test access; no release. |
| Lifecycle authority | Initialization; focused code/tests/scripts/config/manifests/validators; exact directories; independent read-only review before each submission; three normal submissions and bounded retries; job-scoped monitoring/accounting; evaluation; concise records; validation; limited cleanup; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 6 CPU/30 GB/6 h, cap 8/40/8; production leaves 12 CPU/60 GB/16 h `%20`, cap 16/80/20; final 8 CPU/40 GB/4 h, cap 12/60/6. At most three additional submissions per logical unit for scheduler/node/transport/launch/resource failures; sparse array retries only. One reviewed minimal preflight-only correction per unit. Application/code/interface/schema/data/dependency/numerical/science/gate changes stop. After production identity check, record checkpoint and await user wake without active monitoring. |
| Cancellation scope | Recorded Iter011 jobs only if duplicate, outside contract, invalidated by proven common defect, unsafe, or threatening storage; pending/slow alone is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` above. |
| Closeout branch | At most one scoped local no-push commit, proposed subject `Complete SR capacity regularization experiment`. |

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | SR truth, forcing, parameters, surfaces | `39b05495...187a` |
| Global split | 819/205 boundary | `99467dea...0fce` |
| Spinup release/handoff | predicted C/N | manifest `69f840f7...f2dc`; handoff `9e2d5be...fdb5` |
| GPP release/handoff | predicted same-hour GPP | manifest `57cc18b0...70d1`; handoff `c905fc60...98bb` |
| Iter009 raw cache | fixed 44-feature physical-SR design | layout `172c2f4b...b0b6`; X `c648952a...5cf`; y `35697d26...477`; time `8f2efdef...52e` |
| Prior SR splits | exact-match exclusions | Iter009 `7644ed38...ace0`; Iter010 `34a33000...ae43` |
| Repository source | preparation base | `d67845c371678db632b3844a25e344b268389199` |

## Acceptance Gates and Decision Rule

- Unit1 must produce 20 unique seed-`20261111` splits, each 655/164, each development member in
  validation four or five times, no exact validation-set match to Iter009 or Iter010, and no fixed
  test overlap. It must verify full raw/dependency hashes and pass focused tests and bounded smoke.
- Task `0-99` maps `task_id // 20` to A--E and `task_id % 20` to split `0-19`.
- All 100 production fits must pass exact identity/coverage, finite unclipped predictions,
  serialization replay at `rtol=atol=1e-6`, zero production convergence warnings, scratch cleanup,
  and prohibited-scope flags false.
- Per fit retain train/validation x hourly/daily x ABBY/JERC/pooled R2, RMSE, MAE, signed bias.
  Across splits report mean, median, SD, q10, q25, q75, q90. Daily means require complete 24-hour
  days. Positive degradation gaps are train-minus-validation R2, validation-minus-train RMSE/MAE,
  and absolute-validation-minus-absolute-train bias.
- Paired improvement is candidate-minus-comparator for R2 and comparator-minus-candidate for
  RMSE/MAE/absolute bias. Report B/A, D/C, C/A, D/B, E/C, D/E, and selected/A,D.
- A site-cost flag requires pooled mean daily validation RMSE improvement plus at least 5% worse
  mean daily RMSE at either site and at least 14/20 site-level paired losses. Poor stability means
  pooled daily validation RMSE SD at least 1.5 times the median candidate SD. Flags do not rank.
- A contrast is supported when pooled-daily RMSE mean and median improvement are positive, wins
  at least 14/20 splits, and has no site-cost flag. Both matched contrasts are required to support
  capacity or weaker regularization; otherwise describe mixed/unsupported evidence.
- Select by full-precision lowest mean pooled daily validation RMSE, then lowest mean pooled hourly
  RMSE, lowest mean split absolute pooled daily bias, then fewer parameters. An exact remaining tie
  yields `sr_capacity_regularization_selection_unresolved`; otherwise record
  `sr_capacity_regularization_configuration_selected`. No absolute performance gate applies.
- Final validation must independently recompute all 600 validation metric rows from retained
  physical predictions and raw truth and reproduce summaries, paired comparisons, flags, selection,
  hashes, fixed-test exclusion, and no-release state.

## Provenance and Job Ledger

| Work unit | Canonical/submitted material | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- |
| Unit1 | attempt-1 manifest `e95fecbc...2a45`; corrected manifest `0c92c2f2...a350`; corrected config `e8f01cb5...a211`; exact submitted copies | `<root>/runs/unit1`; `unit1_246076{09,28}.{out,err}` | jobs `24607609`, `24607628` | attempt 1 `FAILED 1:0`; attempt 2 `COMPLETED 0:0`, eligible; retry submission 1 consumed |
| production | manifest `0c92c2f2...a350`; resolved config `984aac6f...7d29`; script `13f21fb5...216f`; exact submitted copies | `<root>/runs/production`; `production_24607646_*.{out,err}` | array `24607646_0-99%20` | all 100 tasks `COMPLETED 0:0`; independent completion review pass |
| final | attempt-1 manifest `0c92c2f2...a350`; corrected manifest `7e05b072...7b47`; config `984aac6f...7d29`; script `6df517d1...4b5`; exact submitted copies | `<root>/runs/final`; `final_24617{562,685}.{out,err}` | jobs `24617562`, `24617685` | attempt 1 `FAILED 1:0`; attempt 2 `COMPLETED 0:0`; retry submission 1 consumed |

`<root>` is the approved output root above.

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter011_unit1_review`
- Reviewed source hash: execution manifest `e95fecbc3df8c022357df228bc8cf9507dc14f9157cb757e8e6bcb3650982a45`
- Outcome: `pass` with no concerns at `2026-11-11T02:48:25-07:00`
- Findings and primary-agent response: exact canonical/submitted copies, identities, A--E matrix,
  split exclusions, identity-first ordering, resources, non-production smoke, and scope flags pass.
  Reviewer performed no edits, repository Python, or scheduler action. Mandatory retry re-review
  passed corrected manifest `0c92c2f2...a350`; it verified the only contract change is the locked
  Iter009 raw-source split hash, attempt-1 identities are preserved, and attempt 2 is absent.
  Unit1 completion and production-package review passed with no concerns: all 100 task mappings,
  split identities, full raw hashes, exact copies, resources, technical gates, and exclusions pass.
  Production-completion/final-package review passed accounting `059f0bf8...fe31`, all 100 leaf
  packages, 1,200 metric rows, final selection/validator logic, exact copies, and resources.
  Mandatory plotting-correction retry review passed corrected selection `1566e5f2...5e6f` and
  manifest `7e05b072...7b47`; attempt-1 identities are preserved and no other source changed.
  Independent final-result review passed: it reproduced the B,D,C,A,E ranking, matched
  regularization/capacity contrasts, both-site mean improvements, stability diagnostics, scope
  exclusions, final job accounting, and all compact artifact hashes without edits or
  scheduler-state changes.

## Execution and Diagnostics

- Static validation: canonical shell/JSON syntax, execution-manifest verification, and
  `git diff --check` passed at `2026-11-11T02:44:28-07:00`; compute-node tests were pending at that
  checkpoint and later passed in corrected Unit1.
- Preflight: corrected Unit1 passed focused tests, 20 fresh balanced splits, prior-split exclusion,
  full raw/dependency hashes, contract checks, and five-candidate non-production smoke. Resolved
  config `984aac6f...7d29`; split manifest `b9e6a4e8...8a8a`; design `523809a0...ea0`.
- Exact submission commands: Unit1 used `sbatch --parsable` from the approved run directory with
  attempt `1`, config `1811eab4...51f`, manifest `e95fecbc...2a45`, and stdin `/dev/null`; returned
  job `24607609` at `2026-11-11T02:48:47-07:00`. Corrected attempt 2 used config
  `e8f01cb5...a211`, manifest `0c92c2f2...a350`, and returned `24607628` at
  `2026-11-11T02:55:46-07:00`. Production attempt 1 used resolved config
  `984aac6f...7d29`, manifest `0c92c2f2...a350`, and returned array `24607646` at
  `2026-11-11T03:01:09-07:00`. Final attempt 1 used production attempt 1, the same config/manifest,
  and returned job `24617562` at `2026-11-11T18:19:20-07:00`.
  Corrected final attempt 2 used manifest `7e05b072...7b47`, unchanged config/production attempt,
  and returned job `24617685` at `2026-11-11T18:27:56-07:00`.
- Job identity checks: Unit1 matches `chopinsong/standard`, 6 CPUs with Puma-derived 30 GB,
  six-hour limit, exact command/workdir/logs/stdin and locked exports for both attempts; attempt 2
  initial state priority. Production matches `0-99%20`, `chopinsong/standard`, 12 CPUs with
  Puma-derived 60 GB per leaf, 16-hour limit, exact command/workdir/stdin and locked exports. Final
  matches 8 CPUs/40 GB, four hours, exact command/workdir/logs/stdin and locked exports.
- Queue and terminal accounting: Unit1 attempt 1 job `24607609` is terminal `FAILED 1:0`, elapsed
  `00:00:25`, 6 CPUs, batch MaxRSS `1390312K`, requested memory 30 GB. Corrected job `24607628`
  completed `0:0` in `00:00:34`, 6 CPUs, batch MaxRSS `1115620K`, requested memory 30 GB.
- Resource diagnostics: corrected Unit1 used batch MaxRSS `1115620K` of 30 GB; production leaves
  completed within 12 CPUs/60 GB and the 16-hour limit; corrected final used `8280952K` of 40 GB.
  Final `seff` reported 19.74% memory efficiency and 10.15% CPU efficiency for its short aggregate.
- Failure, rejection, retry, or cancellation evidence: tests passed, then Unit1 stopped before raw
  hashing, smoke, or production training because the new config omitted the Iter009 raw cache's
  separate `raw_source_split_manifest_sha256`. Classified as the approved one-time minimal
  preflight-only correction: add the already locked Iter009 split hash, refresh identities and
  submitted copies, and require independent re-review before retry.
- Monitoring checkpoint: at `2026-11-11T03:01:21-07:00`, production array `24607646_0-99%20`
  passed immediate identity validation and all 100 tasks were `PENDING (Priority)` with no terminal
  task records. Per the user's explicit instruction, active monitoring stops here without changing
  scheduler state. Exact resume: query job-scoped `squeue --job=24607646 -r` and full parent
  `sacct --jobs=24607646`, reconcile all 100 array-form `JobID` task records, classify any failure,
  and proceed to independent completion review only after authoritative accounting.
- Resume reconciliation at `2026-11-11T18:05:37-07:00` found the expected invalid completed-parent
  queue lookup and exactly 100 unique array-form accounting records: all `COMPLETED 0:0`, 12 CPUs,
  60 GB, with elapsed times `00:57:44`--`05:11:08`. All 100 leaf packages, internal hashes,
  12-row metric files, zero-warning/coverage/scope/cleanup gates, stdout success markers, and logs
  passed static checks. Retained production evidence is about 7.7 GiB.
- Final job `24617562` is terminal `FAILED 1:0`, elapsed `00:00:34`, 8 CPUs, batch MaxRSS
  `7553564K`, requested memory 40 GB. It verified sources and all 100 leaves, wrote the metric,
  comparison, site, paired, and gap CSVs, then stopped before plots, selection report, or independent
  validation because this Matplotlib version rejects `Axes.boxplot(labels=...)` and requires the
  current tick-label keyword. Production evidence and scientific computations were unchanged.
- Classification: application/code compatibility failure after substantive final aggregation.
  The approved package limits automatic correction to preflight-only failures, so no code change or
  retry is authorized. Proposed bounded correction, subject to fresh approval: replace only the two
  plotting calls' `labels=` keyword with `tick_labels=`, refresh hashes/submitted attempt-2 package,
  require independent re-review, and resubmit the same final work against unchanged production.
- Fresh authority: user responded `approved` after the failure checkpoint. Authority is limited to
  that exact plotting-keyword correction, attempt-1 preservation, identity refresh, mandatory
  independent re-review, and otherwise unchanged final attempt-2 submission and lifecycle continuation.
- Corrected final job `24617685` completed `0:0` in `00:01:37` on 8 CPUs/40 GB; batch MaxRSS was
  `8280952K`. No Iter011 job remains active or unaccounted. Selection and independent validation
  both passed; all 600 validation rows, ranking, paired contrasts, flags, and compact hashes were
  reproduced from retained physical predictions.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Overall decision: `sr_capacity_regularization_configuration_selected`; select B `(96,48)`,
  `tanh`, alpha `0.01`, with all other Iter010 Adam controls frozen, as a development candidate for
  separately approved fresh robustness. No release or all-819 fit is authorized.
- Pooled validation means rank B, D, C, A, E by daily RMSE: `0.769154`, `0.796148`, `0.864014`,
  `0.865663`, `0.889526`. B's hourly RMSE/R2 and daily R2 are `0.803085`, `0.849326`, and
  `0.855806`; its mean daily signed bias is `0.038569`.
- Weaker regularization is supported by matched contrasts: B versus A improves pooled daily RMSE
  on 18/20 splits (mean/median `0.096509/0.080284`), and D versus C improves it on 16/20
  (`0.067866/0.058810`), with no site-cost flag. Increased capacity is not supported: C versus A
  is nearly neutral (12/20; `0.001649`), while D loses to B (6/20; `-0.026994`). Alpha `0.1` E
  is worse than C and D, so no monotonic intermediate-regularization effect is established.
- Selected B improves mean daily RMSE over A/Iter010 candidate 19 by 11.1% and over D/Iter010
  candidate 26 by 3.4% on the new Iter011 splits. Mean daily RMSE improves at both ABBY and JERC
  versus both references, but B versus D wins only 11/20 ABBY and 12/20 JERC site-split pairs.
- Tail/stability diagnostics: B daily R2 q10/RMSE q90 are `0.805184/0.913074`; no candidate meets
  the locked poor-stability flag. B nevertheless has pooled daily RMSE SD `0.128813` and a daily
  train-validation RMSE gap `0.452906`, versus A's `0.064820` and `0.197976`.
- Limitations: fixed in-sample upstream C/N and GPP, two sites, finite candidate matrix, 20
  development-only splits, larger weak-L2 train-validation gaps, temporary unbacked storage, and no
  fixed-test, release, absolute performance gate, or full-chain robustness. Effects are matched
  descriptive evidence for this design, not global causal separation.
- Campaign-plan amendment recommendation: `none`.
- Closeout conclusion: preserve Iter010's historical decision; carry B only as the preferred
  development candidate into a separately planned fresh robustness iteration. No next iteration is
  authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter011/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] One authorized local no-push closeout commit created and verified
