# iter013 - ABBY/JERC SR robustness and release

## Status

- Iteration ID: `iter013`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter013_abby_jerc_sr_release`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-16T00:28:12-07:00`
- Closed: `2026-11-16T08:18:45-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6 completion, frozen two-site SR stage and release
- Alignment: `aligned`; this stage-only iteration does not claim item 7 full-chain robustness
- Approved deviation: `none`

## Finalized Plan

- Objective: characterize frozen Iter012 arm B through 20 fresh fixed-upstream SR repetitions,
  publish descriptive uncertainty, fit SR on all 819 development members, and publish validated
  `sr_abby_jerc/release_0001` catalog last.
- Frozen model: 44 features with published predicted same-hour GPP; `(96,48)`, tanh, alpha `0.01`,
  and the exact Iter012 Adam controls. Published C/N and GPP releases remain fixed and unexecuted.
- Design: seed `20261116`; 20 synchronized unique 655/164 splits, distinct from Iter009--012;
  exactly 20 robustness fits and one all-development release fit. The 205 fixed-test members are
  prohibited.
- Work units: Unit1 identity/preflight/splits/cache/tests/smoke; one `0-19%20` array; aggregate and
  uncertainty validation; all-819 release fit; independent release validation and catalog-last
  publication.
- Interpretation: `fixed_upstream_sr_stage`, not end-to-end held-out uncertainty. Robustness is
  descriptive with `performance_gate_applied=false`; technical invalidity blocks publication.
- Exclusions: upstream execution/refit, full-chain robustness, hyperparameter search, ablation,
  cross-fitting, fixed test, nine-site expansion, coupled inference, MCMC, plan edit, and push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Approve the complete Iter013 kickoff package and runtime contract`; `2026-11-16T00:28:12-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Five normal submissions: Unit1, 20-leaf robustness array, aggregate, release, final. Stop immediately after robustness submission and identity confirmation until user ping; then resume through accounting, validation, publication, records, and closeout. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6 completion; aligned; no deviation. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; CPU-only `OLMT_puma`. |
| Approved output and storage policy | Create `<root>/runs/{unit1,robustness,aggregate,release,final}/attempt_N`; stable `NEON_ppe_vertc/surrogate_products/sr_abby_jerc/release_0001`; about 10--15 GiB retained and 400 GiB transient cap; validated successful scratch only may be removed; `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; frozen Iter012 arm B; seed-20261116 design; zero fixed-test access; descriptive robustness without performance gate; technically valid evidence permits the preselected configuration to proceed to release. |
| Lifecycle authority | Initialization; focused implementation/tests/scripts/config/manifests/validators; exact directories; independent read-only review before every submission and for results; five submissions and bounded retries; job-scoped monitoring/accounting; evaluation/publication; concise records; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 6 CPU/30 GB/6 h, cap 8/40/8; leaves 12/60/16 `%20`, cap 16/80/20; aggregate 8/40/4, cap 12/60/6; release 12/60/20, cap 16/80/24; final 8/40/6, cap 12/60/8. Initial plus at most three same-scope scheduler/node/transport/launch/resource retries per unit; sparse array retries. One reviewed minimal preflight/packaging correction before substantive work. |
| Cancellation scope | Recorded Iter013 IDs only if duplicate, outside contract, invalidated by a proven common defect, unsafe, or threatening storage integrity. Pending or slow alone is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` above. |
| Closeout branch | At most one scoped local no-push commit, proposed subject `Release SR surrogate artifact`. |

`<root>` is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release`.

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | truth, forcing, parameters, boundary | `39b05495...187a`; split `99467dea...0fce` |
| Spinup release/handoff | fixed predicted C/N | manifest `69f840f7...f2dc`; handoff `9e2d5be...fdb5` |
| GPP release/handoff | fixed predicted same-hour GPP | manifest `57cc18b0...70d1`; handoff `c905fc60...98bb` |
| Iter009 raw cache | 44-feature SR design and truth | layout `172c2f4b...b0b6`; X `c648952a...35cf`; y `35697d26...e477`; time `8f2efdef...a52e` |
| Frozen arm B | configuration and feature mode | Iter012 arm manifest `3d94f110...04d6`; decision `deployable_arm_B_selected` |
| Prior split manifests | exact-match exclusions | Iter009 `7644ed38...ace0`; Iter010 `34a33000...ae43`; Iter011 `b9e6a4e8...8a8a`; Iter012 `e1ef748c...174e` |
| Repository source | preparation base | `b247a206d686c501893024147e8f38488a2d0982` |

## Acceptance Gates and Decision Rule

- Unit1: exact identities, 20 unique 655/164 splits, validation appearances 815 times four and
  four times five, zero fixed-test overlap, no exact prior match, full cache hashes/source
  reconstruction, 44-feature schema, focused tests, and bounded smoke.
- Every leaf: exact identity/coverage, finite unclipped predictions, zero convergence warnings,
  serialization replay at `rtol=atol=1e-6`, scratch cleanup, and prohibited-scope flags false.
- Preserve 240 train/validation by ABBY/JERC/pooled by hourly/daily rows containing predictive R2,
  RMSE, MAE, signed prediction-minus-ELM bias, residual SD, and linear q01/q025/q05/q25/q50/q75/
  q95/q975/q99. Summarize mean, median, sample SD, q10, q25, q75, q90 and locked degradation gaps.
- Daily values are complete paired 24-hour means. Site uncertainty is per-repetition plus
  member-balanced bias, RMSE, total and centered variance/SD with full provenance.
- `performance_gate_applied=false`; technical validity, not metric thresholds, controls release.
- Release must prove exact all-819 fit, 44-feature artifact/scalers/schema, all `100442160` finite
  predictions, complete stored/scaled/raw standalone replay with float32-compatible scaler
  arithmetic, both upstream identities, exact hashes, byte-identical trees, and catalog last.
- Scientific, data, schema, interface, numerical, or scope changes after substantive work require
  fresh approval.

## Provenance and Job Ledger

| Work unit | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| Unit1 | `<root>/runs/unit1` | job `24666357` | `COMPLETED 0:0`, eligible | review pass; attempt 1; resolved config `a9e4a4ef...4549`; split `c6ab41f1...754c4` |
| robustness | `<root>/runs/robustness` | array `24666388_0-19%20` | all 20 `COMPLETED 0:0`; eligible | max batch MaxRSS `51835932K`/60 GB; primary and independent audit pass; no retry |
| aggregate | `<root>/runs/aggregate` | job `24667839` | `COMPLETED 0:0`, eligible | 8 CPU/40 GB; `00:05:23`; batch MaxRSS `20867916K`; primary and independent validation pass |
| release | `<root>/runs/release` | job `24667881` | `COMPLETED 0:0`, eligible | `02:44:20`; 12 CPU/60 GB; batch MaxRSS `42041936K`; no retry |
| final | `<root>/runs/final` | job `24668984` | `COMPLETED 0:0`, pass | `00:03:01`; 8 CPU/40 GB; batch MaxRSS `1606660K`; catalog-last publication pass |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter013_unit1_review`
- Reviewed source hash: manifest `a241214075bc5adfe350969587d18a62167bf84f37ae456074943f79ce0bda0c`
- Outcome: initial `block`; every corrected package/result review, including final publication,
  subsequently `pass` with no concerns
- Findings and primary-agent response: locked transitive spinup helper imports; moved every
  config-derived Slurm assignment after identity/source checks; normalized convergence and release-
  basis metadata; refreshed exact manifest/submitted copy. The reviewer independently reproduced
  the split design, all 240 robustness rows, 84 uncertainty rows, all-819 artifact/handoff
  identities, full replay evidence, 17/17 publication hashes, staging/stable identity, and catalog-
  last order. The final review found no scientific, technical, scope, or publication blocker.

## Execution and Diagnostics

- Initialization: approved package recorded; repository and external run scaffold created.
- Static validation: JSON and shell syntax, source-manifest verification, submitted-copy material,
  `git diff --check`, and resource/scope inspection pass; compute-node tests remain pending Unit1.
- Unit1 job `24666357` matched the locked identity and completed `0:0` in `00:01:09` on 6 CPUs;
  batch MaxRSS was `18725128K` against derived 30 GB. Unit1 reports 20 fresh split sets, zero prior
  exact matches, complete raw hashes, 44 features, passing tests/smoke, and prohibited scope false.
- No retry or cancellation occurred. Production package review is pending.
- Independent production review passed with no concerns. It reproduced all 20 mappings, exact
  655/164 membership and 815/4 appearance balance, zero fixed-test and prior-set overlap, exact
  submitted copies, frozen model, resources, and scope gates.
- Production submission from the reviewed run-directory copy returned parent `24666388` at
  `2026-11-16T00:51:14-07:00`. Immediate identity validation passed exact array `0-19%20`, throttle
  20, `chopinsong/standard`, 12 CPUs and Puma-derived 60 GB per leaf, 16-hour limit, exact command,
  workdir, logs, stdin `/dev/null`, and attempt/config/manifest exports. All 20 tasks were initially
  `PENDING`; no result or terminal accounting was inspected.
- Mandatory checkpoint entered at `2026-11-16T00:51:30-07:00`; active monitoring is stopped without
  changing the array. Resume only after user ping with job-scoped `squeue --job=24666388 -r` and
  complete parent `sacct --jobs=24666388` using array-form `JobID`, then reconcile all 20 tasks.
- After the user's explicit ping, job-scoped `squeue` was empty and authoritative parent `sacct`
  contained exactly array-form task records `24666388_0` through `_19`, each `COMPLETED 0:0`.
  Maximum batch MaxRSS was `51835932K`, below 60 GB; no retry was used. Primary validation then
  passed all 20 split reports, reload results, exact artifact hashes, 12-row metric tables,
  prohibited-scope flags, scratch cleanup, and success sentinels. Retained attempt size is 15 GiB.
- Independent robustness/result and exact aggregate-package review passed with no blockers.
  Aggregate job `24667839` passed exact identity and completed `0:0` in `00:05:23`; batch MaxRSS
  was `20867916K` against 40 GB. Primary and independent checks passed 240 reconstructed metric
  rows, 168 summaries, 30 positive-degradation gap rows, 84 descriptive uncertainty rows, all
  file hashes, fixed-test exclusion, and `performance_gate_applied=false`.
- Independent aggregate/result and exact release-package review passed with no blockers. Release
  job `24667881` passed exact identity at 12 CPUs, Puma-derived 60 GB, and 20 hours and is running.
- Release job `24667881` completed `0:0` in `02:44:20`; authoritative batch MaxRSS was
  `42041936K` against 60 GB. The frozen model converged in 27 iterations with zero warnings; the
  all-819 artifact, 44-feature schema, embedded scalers, 100,442,160 finite prediction handoff,
  complete persisted-scaled replay, both upstream identities, and scratch cleanup passed primary
  and independent validation.
- Final job `24668984` passed exact identity at 8 CPUs, Puma-derived 40 GB, and 6 hours and
  completed `0:0` in `00:03:01`; authoritative batch MaxRSS was `1606660K`. It replayed all
  `100442160` predictions through the standalone raw-input interface, validated the release tree,
  and published staging then stable release before catalog. No retry or cancellation occurred in
  Iter013. All five job scopes are terminal and accounted.
- Stable `sr_abby_jerc/release_0001` contains artifact `8dd06c29...3fb2`, handoff
  `3704cab6...d3a1`, and validated 17-file manifest `3a3d3faf...ed4c`; catalog
  `3b12ec20...a056` points to that exact manifest. Staging and stable trees are byte-identical.
- Four-record closeout command
  `bash development/three_stage_surrogate/slurm/iter013/validate_closeout_iter013.sh --active-job-count 0`
  returned `ITER013_FOUR_RECORD_VALIDATE_PASS`; the validator identity and output are preserved in
  `summaries/iter013/four_record_validation.txt`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `sr_release_published`; publish the preselected
  Iter012 arm-B SR model as catalog-last `release_0001`. The robustness and uncertainty evidence
  is descriptive `fixed_upstream_sr_stage`, not end-to-end uncertainty; no performance gate was
  applied.
- Limitations: fixed upstream, two sites, overlapping repeated validation sets, all-development
  release predictions in-sample, and temporary unbacked storage.
- Campaign-plan amendment recommendation: `none`
- Next action: none; iteration is terminal and no later iteration is proposed or authorized.

## Explicit Terminal Declaration

Iter013 is closed. No next iteration is proposed or authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter013/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] One authorized local no-push closeout commit created and verified
