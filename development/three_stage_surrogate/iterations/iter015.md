# iter015 - ABBY/JERC full-chain robustness with hard-zero GPP

## Status

- Iteration ID: `iter015`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter015_abby_jerc_full_chain_robustness`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-18T00:42:51-07:00`
- Closed: `2026-11-19T03:42:13-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`
- Applicable campaign phase: progression item 7, ABBY/JERC full-chain robustness
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Sequential ID and work type: Iter015 experiment.
- Objective: characterize twenty synchronized fold-specific ABBY/JERC spinup -> GPP -> SR chains
  with `gpp_output_policy="hard_zero_v1"` and produce development-only robustness and downstream
  uncertainty evidence.
- Inputs: snapshot r0001, the immutable 819/205 boundary, the Iter013 seed-20261116 twenty-split
  design, frozen spinup/GPP/SR configurations, and hash-locked ABBY/JERC depth preprocessing.
- Work units: Unit1 implementation/preflight/smoke; complete pilot split 0; uncapped production
  array splits 1--19; aggregate/evaluation; independent final validation and closeout.
- Exclusions: fixed test, all-819 refit, tuning, cross-fitting, feature ablation, alternative GPP
  gate, nine-site expansion, MCMC changes, existing release mutation, plan amendment, push, merge,
  or figures beyond the three approved diagnostics.
- Decision: all immutable technical, provenance, leakage, completeness, numerical, scientific-
  product, accounting, review, and closeout gates pass -> `full_chain_robustness_characterized`;
  otherwise preserve a precisely classified failed or blocked state. Metric values have no
  performance threshold.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Approve the complete revised Iter015 kickoff package and runtime contract.`; `2026-11-18T00:42:51-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Five sequential submissions and 23 compute work units: Unit1; pilot split 0; uncapped production array splits 1--19; aggregate; final. Stop on identity/leakage/policy mismatch, fixed-test access, failed immutable gate, pilot resource failure, unapproved correction, storage threat, or unaccounted work. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `6fe37606...214d`; item 7; aligned; no deviation or plan edit. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; CPU-only `OLMT_puma`. |
| Approved output and storage policy | Create `<root>/runs/{unit1,pilot,production,aggregate,final}/attempt_N`, `<root>/products`, and `<root>/handoff`; 600 GiB transient cap and 100 GiB successful closeout retention cap; `/xdisk` temporary and unbacked; remove only validated reproducible successful scratch and preserve failed attempts. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; frozen 25/43/44 feature contracts and model configurations; twenty synchronized 655/164 chains; train-only scalers; physical-unit `maximum(gpp_raw,0)` supplied to SR; full-chain held-out evidence; technical completeness without performance threshold; explicit exclusions above. |
| Lifecycle authority | Initialization; focused implementation/tests/scripts/config/manifests/validators; exact directories; independent read-only package/result review; five submissions and bounded retries; monitoring/accounting; evaluation/products/handoff; normal records; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 8 CPU/40 GB/6 h; pilot 16/80/24; production leaves 16/80/24 array `1-19` with no concurrency throttle; aggregate 12/60/8; final 8/40/4. One unchanged scheduler/node/transport/preemption retry per unit, sparse one-per-leaf production retries, and one reviewed Unit1 wrapper/manifest/import-only correction consuming its retry. OOM, timeout, storage breach, or substantive failure stops for fresh authority. Monitor Unit1 and pilot through review; after pilot pass submit production, verify identity, record checkpoint, stop monitoring, and wait for user ping. |
| Cancellation scope | Recorded Iter015 IDs only if duplicate, outside contract, invalidated by a proven common defect, unsafe, or threatening storage integrity; pending or slow is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the stated conditions. |
| Closeout branch | Exactly one scoped local no-push commit after independent validation; subject `Complete full-chain surrogate robustness`. |

`<root>` is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness`.

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Repository source | implementation base | commit `1338f8aa11afb5cedbf51797d965ee928890702b`; clean at bootstrap |
| Snapshot r0001 | parameters, forcing, surfaces, truth, population | `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a` |
| Global split | immutable development/fixed-test boundary | `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce`; 819/205 |
| Iter013 repetitions | synchronized split design | manifest `c6ab41f1a9dbb7f49bc24a3654b2798dcd0ee6886aa5cc1d169aaa9045c754c4`; design `6e35eae529c80a4611880fe4840bf206b85f6d9a0cb204fff6df5f1a944064f5`; seed 20261116 |
| Spinup configuration | frozen 25-feature C/N models | `(64,32)` tanh, alpha 10, L-BFGS, max_iter 800, seed 42 |
| GPP configuration | frozen 43-feature model | file `0250047da2fd3909a5efaf9a1c0e1972d47185e5a4a72241e1706ab50407f62e` |
| SR configuration | frozen 44-feature model | file `821348eae89a798975e8a8418b6a7cf3abaaf0e017d7bba16502ff9d37ff2613` |
| Depth preprocessing | paired same-member diagnostic | ABBY `822611984a2f2a3bfdfc6c8b9f9b421a6bed809d938351faf122ed954dbab358`; JERC `c6fa8500db6bf21387dfc5d875c997e70112db2fe5ddadd09c3760a679f9df61` |
| Iter014 engine | reusable inference base | `model_ELM/three_stage_inference.py` SHA-256 `73fb88a81cbc5759ce93b39583ff959aef384368b67c057283b835cb0145becf` |
| Existing releases | historical compatibility regression only | spinup/GPP/SR `release_0001`; prohibited as fold training inputs and unchanged |

## Acceptance Gates and Decision Rule

- Every split contains exactly 655 training and 164 validation members over the same 819-member
  development population, synchronized across sites and stages, with zero fixed-test overlap.
- Every model and data-dependent scaler identifies only its split's training members. Training
  uses direct sequential in-sample predicted C/N, then physical raw and gated GPP, then gated-GPP
  SR; validation uses a completely unseen full chain.
- The new fold path records `hard_zero_v1`, returns raw and gated GPP, proves gated GPP equals
  `np.maximum(gpp_raw, 0.0)`, and proves the identical gated values enter SR. Published all-819
  upstream predictions never enter fold training.
- Preserve canonical 18 parameters, conditional C:N support, site descriptors, no-leap time,
  seven forcing variables, 720-hour history, and exact 25/43/44 schemas. Preserve the historical
  frozen-release interface and replay behavior.
- Fold artifacts reload; direct and streamed/memmap inference agree at `rtol=atol=1e-6`; compact
  serialized evidence reloads exactly; all required values are finite and positive where required.
- Pilot must pass the complete scientific/numerical/provenance path within 16 CPU, derived 80 GB,
  24 hours, and the storage contract without indicating production needs larger limits.
- Retain train/validation ABBY/JERC/pooled C/N physical/log and GPP/SR hourly/daily predictive R2,
  RMSE, MAE, prediction-minus-ELM bias, residual SD, and linear q01/q025/q05/q25/q50/q75/q95/
  q975/q99. Daily values are complete paired 24-hour means.
- Preserve paired held-out C/N values and site-specific 2x2 log-error covariance; member-balanced
  cross-repetition uncertainty; training-validation gaps; per-member propagation evidence; and
  same-member surrogate/depth within- and cross-element covariance/correlation.
- `gpp_gate_comparison` contains exactly 120 split/site/resolution rows using identical held-out
  targets, with raw/gated R2 and RMSE and paired differences.
- Produce exactly `error_propagation.png`, `gpp_gate_comparison.png`, and `gpp_sr_joint.png` under
  the approved definitions. Split-0 joint evidence uses pooled/ABBY/JERC 200x200 common grids,
  matched axes, unit-mass normalization, and 50/75/90/99 percent enclosed-mass contours; preserve
  Pearson summaries across all twenty repetitions.
- Final validation independently recomputes identities, split membership, leakage exclusions,
  gate arithmetic, required inventories, representative and aggregate metrics, covariance,
  density normalization, correlations, hashes, and prohibited-scope flags.
- No performance threshold applies. Complete technically valid evidence passes regardless of
  metric direction; technical, provenance, leakage, numerical, or completeness failure blocks.
- Application/code/interface/schema/data/dependency/numerical/scientific changes after substantive
  work begins require fresh approval.

## Provenance and Job Ledger

| Work unit | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| Unit1 | `<root>/runs/unit1` | job `24700507` | `COMPLETED 0:0` | attempt 1; 37 s; 8 CPUs/40 GB; batch MaxRSS `1144448K`; primary and independent result validation pass |
| pilot split 0 | `<root>/runs/pilot` | job `24700675` | `COMPLETED 0:0` | attempt 1; `04:21:52`; 16 CPUs/80 GB; batch MaxRSS `38462568K`; primary and independent result validation pass |
| production splits 1--19 | `<root>/runs/production` | parent `24711922`, array `1-19` | all 19 leaves/batch/extern `COMPLETED 0:0` | attempt 1; no retry; walltimes `03:51:31`--`06:56:13`; peak batch MaxRSS `38478540K`; primary and independent result validation pass with non-failing warning provenance |
| aggregate | `<root>/runs/aggregate` | job `24717714` | `COMPLETED 0:0` | attempt 1; `00:02:22`; 12 CPUs/60 GB; batch MaxRSS `28039984K`; primary and independent result validation pass |
| final | `<root>/runs/final` | job `24717815` | `COMPLETED 0:0` | attempt 1; `00:02:40`; 8 CPUs/40 GB; batch MaxRSS `19535548K`; primary and independent result validation pass |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter015_unit1_review`.
- Reviewed source hash: execution manifest
  `1aecdcb3f6cee5b9f116cde4c31e5c859a4faa443a74f17c15547dd50efdaad3`.
- Outcome: `pass`; no blocker or concern.
- Findings and primary-agent response: initial review identified two concern-level omissions before
  submission: artifact reload was declared but not exercised, and the fold constructor did not
  explicitly enforce conditional C:N metadata/counts. The primary added hash-verified reload of
  all three artifacts before coupled inference plus exact 25/43/44, development-only, and C:N
  metadata checks, refreshed the manifest/submitted copy, and obtained passing re-review. The
  reviewer verified every manifest entry and exact submitted-copy equality and made no mutation,
  Python call, or scheduler call.
- Unit1 result review: `pass`; the reviewer independently reconciled job `24700507`, all five
  tests, smoke inventories, retained hashes, artifact reload, exact schemas, hard-zero routing,
  prohibited-scope flags, and scratch cleanup. No concern remains.
- Pilot package review: execution manifest
  `82e656cad9c0ef7c74948d1cb4ab36b7022ed8311c9a35cb9dc024c710c02fe8`;
  `pass_with_concerns`. The execution package is ready and exact: split 0 only, 16 CPUs with
  Puma-derived 80 GB, 24 h, pinned Unit1 prerequisites, non-overwrite guard, and exact submitted
  copies. The sole concern was stale durable-record state; this records-only correction resolves
  it and the reviewer stated no execution-package change or re-review was required.
- Pilot result review: `pass`; no concern. The reviewer independently verified terminal
  accounting, split/member identity and fixed-test exclusion, all report/artifact/file hashes,
  exact row inventories, finite evidence, raw/gated paired comparisons, hard-zero equality and SR
  routing, reload/convergence/prohibited-scope flags, scratch cleanup, storage, and production
  resource eligibility.
- Production package review: execution manifest
  `f04babdaa9ce204ed2f75dcabe4fabc7dacefe986ffb502ade94496693c312d6`;
  `pass_with_concerns`. The package is technically ready: exact submitted copies, pilot report
  prerequisite, array `1-19` with no `%` throttle, 16 CPUs/80 GB/24 h per leaf, isolated paths,
  non-overwrite and prohibited-scope controls, and absent attempt 1 all pass. The sole concern was
  stale pilot-review record state; this records-only correction resolves it, and no package
  re-review is required.
- Production result review: `pass_with_concerns`; aggregate eligible after a records-only
  correction. All 19 leaves, split/member identities, fixed-test exclusion, hashes, inventories,
  finiteness, hard-zero/reload/prohibited/scratch gates, resources, and storage pass. The reviewer
  found 23 retained diagnostic spinup L-BFGS `max_iter` warnings across 14 leaves (TOTSOMC in 12,
  TOTSOMN in 11); GPP and SR have zero warnings. Iter004's frozen spinup gate explicitly treats
  convergence warnings as diagnostic and non-failing, so no retry or model change is warranted.
- Aggregate package review: initial outcome `block`. The reviewer found a 120x120 rather than
  approved 200x200 joint grid, missing member-balanced cross-repetition products, and incomplete
  C/N target provenance. The primary changed no scientific gate: it corrected the grid to 201
  edges with explicit 200x200/unit-mass checks; added first-stage site/member aggregation over the
  exact 4/5 appearances followed by equal-member summaries/covariance/correlations; and recorded
  soil1--soil4, units, active nlevdecomp mask, DZSOI source, ZISOI[10] depth, and exclusions.
  Refreshed manifest `33bb7e06f290e1607f160c4a8b3f10aec29e31d321147fdad3bba6db5d770527`
  received `pass` re-review with no concerns; submitted copies are exact and attempt 1 is absent.
- Aggregate result review: `pass`; no concern. The reviewer independently verified accounting,
  all 27 output hashes and exact inventories, member balancing/covariance, finite evidence, paired
  gating, all-repetition correlations, 200x200 unit-mass panels, visual figure legibility,
  provenance/handoff limitations, exclusions, and final-validation eligibility.
- Final package review: initial `pass_with_concerns`; scientific and execution logic passed. The
  primary recorded the aggregate result pass and added explicit post-copy SHA-256 checks for the
  product manifest plus both uncertainty-handoff copies, refreshed execution manifest
  `ff075e65031b8cd2cb4fc19558799c35b989e1d00711aa0096f368762a525b9b`,
  and requested re-review before submission.
- Final result review: `pass_with_concerns`; scientific and technical acceptance pass. The
  reviewer independently verified terminal accounting, all recomputation counts and hashes, exact
  product/handoff inventories, the 26-GiB retained footprint, and all scope exclusions. Its sole
  concern was the stale production/final ledger wording corrected above; no scientific artifact,
  execution package, or result changed. Closeout is eligible.

## Execution and Diagnostics

- Initialization: approved revised package recorded; canonical repository scaffold and exact
  external `runs/{unit1,pilot,production,aggregate,final}`, `products`, and `handoff` paths created.
- Static validation: Unit1 and pilot shell syntax, JSON syntax, full execution-manifest
  verification, canonical/submitted equality, scope/resource inspection, and `git diff --check`
  pass. Repository Python ran only in completed Unit1 job `24700507`.
- Preflight: Unit1 attempt 1 submitted as job `24700507` at `2026-11-18T01:02:16-07:00`.
- Exact submission command: from `<root>/runs/unit1`, `sbatch --parsable` with attempt `1`, config
  SHA-256 `34abb606...99eb3`, execution-manifest SHA-256 `1aecdcb3...daad3`, and stdin `/dev/null`.
- Job identity checks: job `24700507` matches `3stage_i015_unit1`, `chopinsong/standard`, one
  node/task, 8 CPUs, Puma-derived 40 GB, six-hour limit, exact command/exports/workdir/logs, and
  stdin `/dev/null`; initial state `PENDING (Priority)`.
- Queue and terminal accounting: authoritative `sacct` records parent `24700507`, batch, and
  extern as `COMPLETED 0:0`; elapsed `00:00:37`; 8 allocated CPUs; parent TotalCPU `00:10.017`;
  batch MaxRSS `1144448K`; requested memory 40 GB; node `r4u28n1`.
- Resource diagnostics: `seff 24700507` confirms 1.09 GB memory (2.73% of 40 GB) and 37-second
  walltime. Historical GPP/SR peaks support the approved pilot 16 CPU/80 GB shape; production
  concurrency is explicitly uncapped by user revision.
- Failure, rejection, retry, or cancellation evidence: none.

- Unit1 result: all five focused tests passed; `ITER015_UNIT1_OK` emitted. Preflight locked 20
  splits with 815/four and 4/five validation appearances and `hard_zero_v1`. Smoke retained 48
  metric, six gate-comparison, four propagation, and 32 depth-dependence rows; every recorded
  artifact/file hash verifies; reloaded artifacts and prohibited-scope flags pass; scaled scratch
  is absent; retained attempt size is 904 KiB.
- Pilot submission: attempt 1 submitted as job `24700675` at
  `2026-11-18T01:13:07-07:00`. Immediate identity verification matches the locked script and
  exports, `chopinsong/standard`, one node/task, 16 CPUs with Puma-derived 80 GB, 24 h, exact
  workdir/logs, and stdin `/dev/null`; initial state `PENDING (Priority)`.
- Pilot standby checkpoint: at the user's explicit request, the monitoring process was stopped and
  Slurm job `24700675` was left running. Last job-scoped check at
  `2026-11-18T01:32:56-07:00` showed parent, batch, and extern `RUNNING` on `r4u32n2`, elapsed
  `00:15:12`. On the user's ping, resume with `squeue --job=24700675 -r`, authoritative `sacct`
  for parent/batch/extern, and `seff 24700675`; do not infer completion from queue departure.
- Pilot terminal accounting: after the user's resume ping, `sacct` reconciled parent, batch, and
  extern as `COMPLETED 0:0`, start `2026-11-18T01:17:41-07:00`, end
  `2026-11-18T05:39:33-07:00`, elapsed `04:21:52`, 16 allocated CPUs, parent TotalCPU
  `04:18:54`, batch MaxRSS `38462568K`, requested memory 80 GB, node `r4u32n2`. `seff` reports
  36.68 GB (45.85% of 80 GB); no retry, failure, rejection, or cancellation occurred.
- Pilot primary validation: success token `ITER015_SPLIT_OK split=0 metrics=48 gate_rows=6`
  emitted. Report SHA-256 `95d5de65...9476a` verifies full split 0 with 655 training and 164
  validation members, 61,320 hours, artifact reload, `hard_zero_v1`, 48 metric rows, six paired
  gate rows, 328 member propagation rows, and 32 depth rows. Every recorded artifact/file hash,
  finite CSV check, exact identity, prohibited-scope flag, and scaled-scratch cleanup passes;
  retained attempt size is 1.3 GB. Spinup, GPP, and SR report no convergence warnings.
- Production submission: uncapped attempt 1 array `1-19` submitted as parent `24711922` at
  `2026-11-18T15:35:59-07:00`. Immediate `squeue` listed exactly 19 leaves, all `PENDING`; no `%`
  throttle is present. `scontrol` matches `3stage_i015_prod`, `chopinsong/standard`, one node/task,
  16 CPUs and Puma-derived 80 GB per leaf, 24 h, locked exports/command, exact workdir/log pattern,
  and stdin `/dev/null`.
- Mandatory production checkpoint: monitoring stopped at `2026-11-18T15:36:09-07:00` after
  identity verification; jobs remain under Slurm control. On the user's ping, resume with
  job-scoped `squeue --job=24711922 -r`, parent-array `sacct` using the `JobID` field, and
  leaf-scoped `seff`; reconcile all elements `1-19` plus batch/extern before validation or aggregate.
- Production terminal accounting: after the user's resume ping, job-scoped `sacct` reconciled all
  19 leaves and every batch/extern step as `COMPLETED 0:0`; no retry, failure, rejection, or
  cancellation occurred. Walltimes span `03:51:31`--`06:56:13`, all leaves allocated 16 CPUs and
  80 GB, and peak batch MaxRSS is `38478540K` (36.70 GB). Leaf-scoped `seff` independently reports
  36.44--36.70 GB and completion for every element.
- Production primary validation: all split IDs 1--19 emit the exact success token and pass exact
  655/164 membership counts, 61,320 hours, artifact reload, `hard_zero_v1`, 48 metric rows, six
  paired gate rows, 328 member propagation rows, and 32 depth rows. Every report identity,
  artifact/file SHA-256, CSV finiteness check, prohibited-scope flag, and scaled-scratch check
  passes. Spinup retains 23 diagnostic L-BFGS `max_iter` warnings in 14 leaves (C in 12, N in 11),
  while GPP and SR have none; these are non-failing under the immutable frozen spinup gate.
  Retained production attempt size is 25 GB.
- Aggregate submission: reviewed attempt 1 submitted as job `24717714` at
  `2026-11-19T03:11:08-07:00`. Immediate identity verification matches `3stage_i015_aggr`,
  `chopinsong/standard`, one node/task, 12 CPUs with Puma-derived 60 GB, 8 h, exact locked
  exports/command/workdir/logs, and stdin `/dev/null`; initial state `PENDING (Priority)`.
- Aggregate terminal accounting: parent, batch, and extern are `COMPLETED 0:0`; elapsed
  `00:02:22`, TotalCPU `01:43.027`, 12 allocated CPUs, batch MaxRSS `28039984K` (26.74 GB of
  60 GB), node `r7u07n1`. No failure, retry, rejection, or cancellation occurred.
- Aggregate primary validation: exact success token emitted; report SHA-256
  `c06454a70020e0b5ad141baade9dcf7e6242c08cc8af99540f59b0e113610744`.
  All output hashes, finite CSVs, exact 960/120/6,560/640 core inventories, 6,560 C/N rows and
  160 repetition covariance cells, 1,638 equal-member C/N and propagation rows with 1,630/four
  and 8/five site-member appearances, balanced summaries/covariance/correlations, 120 GPP--SR
  correlations, six 200x200 common unit-mass panels, explicit provenance/handoff exclusions, and
  exactly three PNGs pass. Primary visually inspected all figures; retained aggregate is 3.7 MB.
- Final submission: independently reviewed attempt 1 submitted as job `24717815` at
  `2026-11-19T03:33:03-07:00`. Immediate identity verification matches `3stage_i015_final`,
  `chopinsong/standard`, one node/task, 8 CPUs with Puma-derived 40 GB, 4 h, exact locked
  exports/command/workdir/logs, and stdin `/dev/null`; initial state `PENDING (Priority)`.
- Final terminal accounting: parent, batch, and extern are `COMPLETED 0:0`; elapsed `00:02:40`,
  TotalCPU `01:48.611`, 8 allocated CPUs, batch MaxRSS `19535548K` (18.63 GB of 40 GB), node
  `r7u06n1`. No failure, retry, rejection, or cancellation occurred.
- Final primary validation: success token emitted; report SHA-256
  `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
  Independent recomputation passes all 20 split/leakage identities, aggregate concatenation/hashes,
  full binary hard-zero equality, six gate metrics, 24 representative metrics, 160+8 C/N
  covariance cells, 180+9 propagation correlations, 120 GPP--SR correlations, and six 200x200
  density panels. Twenty-eight aggregate files plus product manifest are hash-verified under
  `products/`; the uncertainty handoff, manifest, and final report are exact under `handoff/`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: `full_chain_robustness_characterized`. Twenty
  synchronized fold-specific chains and the complete development-only uncertainty handoff pass
  all immutable technical, provenance, leakage, numerical, product, accounting, and independent
  review gates. No performance threshold was applied and no release refit is authorized.
- Pooled held-out GPP hourly/daily mean R2 is `0.929685/0.897078` and mean RMSE is
  `3.668057/2.063302`; pooled held-out SR hourly/daily mean R2 is `0.802874/0.808664` and mean
  RMSE is `0.919953/0.887979`.
- The hard-zero gate has mean pooled hourly/daily gated-minus-raw R2 of
  `+0.004582/+0.011979` and raw-minus-gated RMSE of `+0.115088/+0.111132`. A few daily split
  comparisons are slightly negative, so this is a paired distributional result, not universal
  split-level improvement.
- Equal-member held-out propagation correlations (C/N RMS log error versus GPP RMSE, C/N versus
  SR RMSE, and GPP versus SR RMSE) are `0.468836`, `0.530589`, and `0.769234` pooled. ABBY and
  JERC member-balanced C/N C--N error correlations are `0.990145` and `0.994552`.
- Limitations: ABBY/JERC only; overlapping repeated validation sets; direct sequential downstream
  training; temporary unbacked storage; no fixed-test or final all-development artifact claim.
- Campaign-plan amendment recommendation: `none`.
- Next action: none within Iter015. Any fixed-test evaluation, all-development refit, release,
  expansion, or downstream inference requires separately approved work.

## Explicit Terminal Declaration

Iter015 is terminal. No next iteration is proposed or authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter015/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] Exactly one authorized local no-push closeout commit created and verified under the recorded
  expected parent and subject metadata
