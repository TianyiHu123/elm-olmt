# iter016 - ABBY/JERC frozen coupled release and fixed test

## Status

- Iteration ID: `iter016`
- Work type: `release`
- Run slug: `three_stage_surrogate_iter016_abby_jerc_frozen_release_fixed_test`
- Status: `completed`
- Phase: `closeout`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-19T17:24:49-07:00`
- Closed: `2026-11-20T15:31:57-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`
- Applicable campaign phase: progression item 8, ABBY/JERC all-development refit and fixed test
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Sequential ID and work type: Iter016 release.
- Objective: refit the frozen direct-sequential ABBY/JERC three-stage chain on all 819 development
  members, evaluate it once on all 205 fixed-test members, and publish a versioned coupled release.
- Inputs: snapshot r0001, immutable 819/205 global split, frozen spinup/GPP/SR configurations,
  Iter015 gated full-chain implementation and uncertainty handoff, and Iter014 inference concepts.
- Work units: Unit1 implementation/review/preflight; all-819 refit; fixed-test inference/evaluation;
  coupled release and closeout, with five sequential Slurm submissions because release and final
  validation are separate submissions.
- Exclusions: tuning, cross-fitting, ablation, robustness repetitions, nine-site expansion, MCMC,
  unrelated refactoring, historical release changes, plan amendment, intermediate commit, push,
  or merge.
- Decision: all immutable artifact, leakage, inference, gate, fixed-test, release, accounting,
  review, and closeout gates pass -> `coupled_release_published`; metric magnitude has no
  performance threshold and any scientific concern is recorded for a separate decision.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Approve the complete Iter016 kickoff package and runtime contract as stated.`; `2026-11-19T17:24:49-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Four logical work units and five sequential submissions: Unit1; refit; fixed test; release; final. Stop at the mandatory post-refit-submission checkpoint, identity/leakage/policy mismatch, premature fixed-test access, failed immutable gate, storage threat, unapproved correction, or unaccounted job. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `6fe37606...214d`; item 8; aligned; no deviation or plan edit. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; CPU-only `OLMT_puma`. |
| Approved output and storage policy | Create `<root>/runs/{unit1,refit,fixed_test,release,final}/attempt_N`, `<root>/staging/three_stage_abby_jerc/release_0001`, `<root>/products/fixed_test`, `<root>/manifests`, and the job ledger; publish catalog-last under `surrogate_products/three_stage_abby_jerc/release_0001`. Transient cap 80 GiB; successful retained cap 10 GiB under the run root plus 2 GiB stable. Remove only validated reproducible successful scratch; preserve failed attempts and stop if retention limits are threatened. `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; all models/scalers fit only 819 development members; fixed-test inference excludes ELM targets and evaluation joins them separately; frozen 25/43/44 schemas/configurations; physical-unit `hard_zero_v1`; exact provenance distinction among training, fixed test, and historical artifacts; no performance threshold; explicit exclusions above. |
| Lifecycle authority | Initialization; focused implementation/tests/scripts/config/manifests/validators; exact directories; independent read-only package/result reviews; five locked submissions and bounded retries; monitoring/accounting; fixed-test evaluation; new coupled release publication; normal records; one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Unit1 4 CPU/20 GB/2 h; refit 16/80/12 h; fixed test 8/40/6 h; release 4/20/2 h; final 8/40/4 h. One reviewed wrapper/import/manifest/test-harness-only preflight correction and rerun; one unchanged same-scope scheduler/node/transport/preemption/launch retry per submission. OOM, timeout, storage breach, or substantive failure stops for fresh authority. Immediately after refit submission and identity recording, stop monitoring and end the turn until user ping. |
| Cancellation scope | Recorded Iter016 IDs only if duplicate, outside contract, invalidated by a proven common defect, unsafe, or threatening storage integrity; pending, slow, or checkpoint status is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the stated conditions. |
| Closeout branch | Exactly one scoped local no-push commit after independent validation; proposed subject `Publish coupled three-stage surrogate release`. |

`<root>` is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter016_abby_jerc_frozen_release_fixed_test`.

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Repository source | implementation base | commit `f2361316185979af41c6758100d98ee78d5157dd`; clean at bootstrap |
| Snapshot r0001 | parameters, forcing, surfaces, truth, population | `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a` |
| Global split | immutable development/fixed-test boundary | `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce`; seed 2026; 819/205 |
| Spinup configuration | frozen 25-feature C/N models | `(64,32)` tanh, alpha 10, L-BFGS, max_iter 800, seed 42 |
| GPP configuration | frozen 43-feature model | `0250047da2fd3909a5efaf9a1c0e1972d47185e5a4a72241e1706ab50407f62e` |
| SR configuration | frozen 44-feature model | `821348eae89a798975e8a8418b6a7cf3abaaf0e017d7bba16502ff9d37ff2613` |
| Iter015 uncertainty handoff | development-only empirical uncertainty | handoff `c9282bbad9abc2d6519329018ca9be026171f071e6e689a44fb2af102784f436`; products manifest `293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9`; validation `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6` |
| Historical releases | compatibility and immutability only | spinup `69f840f7...f2dc`; GPP `57cc18b0...70d1`; SR `3a3d3faf...ed4c`; all `release_0001` unchanged |

## Acceptance Gates and Decision Rule

- Exactly 819 development members and zero fixed-test members enter every model and scaler fit.
- Fixed-test inference contains exactly two sites, 205 members, and 61,320 hours per site/member;
  it consumes parameters, site context, and forcing but no ELM target.
- Evaluation separately joins immutable ELM targets and reports pooled/ABBY/JERC C/N physical and
  natural-log R2, RMSE, MAE, and prediction-minus-ELM bias, plus GPP/SR hourly/daily R2, RMSE, MAE,
  and bias. Daily values are paired complete 24-hour means.
- Raw-versus-gated GPP diagnostics use identical targets and report both variants without changing
  the release gate. Retain exactly three compact figures: C/N parity, flux parity, and GPP-SR joint
  density.
- Preserve canonical 18 parameters, bounds, transforms, conditional C:N support, no-leap time,
  seven forcing variables, 720-hour history, and exact 25/43/44 feature schemas.
- All artifacts reload; direct and chunked inference agree at `rtol=atol=1e-6`; serialization and
  hashes are stable; outputs are finite and positive where required.
- Gated GPP equals `maximum(gpp_raw, 0)` in physical units and the identical values enter SR.
- The coupled bundle records artifacts/scalers, configurations, feature schemas, parameter
  constraints, site/forcing requirements, GPP policy, executable inference entry point, exact
  training provenance, fixed-test evaluation provenance, and hash-locked Iter015 uncertainty
  references and limitations.
- New stable and staged release trees are byte-identical and the new catalog is written last.
  Historical individual release trees and catalogs remain unchanged.
- No performance threshold applies. Complete technically valid evidence passes regardless of
  metric direction; scientific concerns are recorded without post-hoc changes.
- Application/code/interface/schema/data/dependency/numerical/scientific changes after substantive
  work begins require fresh approval.

## Provenance and Job Ledger

| Work unit | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| Unit1 | `<root>/runs/unit1` | job `24725402` | `COMPLETED 0:0`; eligible | attempt 1; 34 s; 4 CPUs/20 GB; batch MaxRSS `1052608K`; primary pass and independent `pass_with_concerns`; sole records-state concern resolved before refit submission |
| refit | `<root>/runs/refit` | job `24725445` | `FAILED 1:0`; recovered and accepted | attempt 1; `07:14:12`; 16 CPUs/80 GB; batch MaxRSS `43654448K`; all three fits/artifacts/prediction arrays completed, then bounded replay rejected a full-axis/prefix interface mismatch; no refit retry submitted; immutable outputs accepted by reviewed validation-only attempt 2 |
| refit recovery | `<root>/runs/refit` | `24729103` | COMPLETED `0:0` | submitted `2026-11-20T01:19:17-07:00`; elapsed 25 s, TotalCPU 5.900 s, batch MaxRSS 2,256,000 K; report PASS `9469e440...e90c`; layout `f3be7c00...bfa58`; stdout/stderr `14a208cd...a5d5` / `5842eaed...f84d`; independent result review PASS; refit accepted for Unit 3 |
| fixed test | `<root>/runs/fixed_test` | `24729214` | COMPLETED `0:0` | elapsed 2m04s, TotalCPU 1m38.350s, batch MaxRSS 3,149,304 K; report PASS `abb6dd67...50d4`; prediction NetCDF `9e7463b7...25d6`; 12 C/N + 12 flux + 6 gate + 6 correlation rows and exactly 3 figures; independent result review PASS; eligible for Unit 4 |
| release | `<root>/runs/release` | `24729323` | COMPLETED `0:0` | elapsed 17 s, TotalCPU 5.872 s, batch MaxRSS 1,525,796 K; candidate report PASS `ad9baa7a...6d09`; assembled 26-file manifest `93e23bf5...4b5f`; retained 215 MB; `published=false`; independent result review PASS |
| final | `<root>/runs/final` | `24740188` | COMPLETED `0:0` | elapsed 31 s, TotalCPU 7.268 s, batch MaxRSS 1,738,836 K; final report PASS `18a05fa0...97f8`; validated manifest `4bdc91e2...543a`; catalog `89a636b9...85da`; byte-identical 215 MB staging/stable; catalog last; independent result review PASS; closeout eligible |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter016_package_review`
- Reviewed source hash: corrected execution manifest
  `b4d9d6787a29888911b8aa8bd37810aa79cd457e213a0f139aec1b82cacae0d1`
- Outcome: `pass`; no blocker or concern.
- Findings and primary-agent response: initial review blocked submission because the coupled
  loader did not fail closed on every manifest provenance field. The primary added complete
  manifest-to-snapshot/artifact validation, corruption rejection tests, and hashes for all three
  retained development prediction files; refreshed both exact submitted manifests; and obtained
  passing re-review. The reviewer made no edit, Python call, or scheduler call.

## Execution and Diagnostics

- Static validation: shell syntax, JSON syntax, full execution-manifest verification,
  canonical/submitted equality, declared resource/scope inspection, and `git diff --check` pass.
- Preflight: Unit1 attempt 1 submitted as job `24725402` at
  `2026-11-19T17:38:51-07:00`; initially `PENDING (Priority)`.
- Exact submission commands: from `<root>/runs/unit1`, `sbatch --parsable` with attempt 1,
  config `fd73f995...1282`, execution manifest `b4d9d678...ae0d1`, and stdin `/dev/null`.
- Job identity checks: `3stage_i016_unit1`; `chopinsong/standard`; one node/task; 4 CPUs with
  Puma-derived 20 GB; 2 h; exact command, exports, workdir, logs, and stdin `/dev/null` all match.
- Queue and terminal accounting: authoritative `sacct` records parent, batch, and extern
  `COMPLETED 0:0`; elapsed `00:00:34`; parent TotalCPU `00:12.167`; 4 allocated CPUs; batch
  MaxRSS `1052608K`; requested memory 20 GB; node `r7u10n1`.
- Resource diagnostics: `seff 24725402` reports 1.00 GB (5.02% of 20 GB) and 8.95% CPU
  efficiency. Unit1 retained size is 912 KiB.
- Failure, rejection, retry, or cancellation evidence: none

- Unit1 result: all seven focused tests passed. Exact success token
  `ITER016_UNIT1_OK release_interface=true smoke=pass fixed_test=false` emitted. Preflight report
  SHA-256 `c7b77df282525d4e7fef8b9cddb5b008520a553827e316dca5b40d3732add24a`
  confirms 819/205 identity, exact 25/43/44 schemas, `hard_zero_v1`, release-interface coverage,
  false fixed-test target access, false all-development fit, and unchanged historical releases.
- Independent Unit1 result review: `pass_with_concerns`; scientific and technical result passes
  and refit is eligible. Its sole concern was stale pending/active durable-record wording; the
  terminal ledger and handoff wording above resolve it before refit submission. No source or
  execution-package change or re-review is required.

- Refit submission: attempt 1 submitted as job `24725445` at
  `2026-11-19T17:43:33-07:00`. Immediate identity verification matches `3stage_i016_refit`,
  `chopinsong/standard`, one node/task, 16 CPUs with Puma-derived 80 GB, 12 h, exact submitted
  script/configuration/manifest/Unit1-report exports, workdir, log paths, and stdin `/dev/null`;
  initial state `PENDING (Priority)`.
- Mandatory human checkpoint entered at `2026-11-19T17:43:43-07:00`. Slurm job `24725445`
  remains under normal scheduler control; no fixed-test or release job is submitted. Active
  monitoring is intentionally stopped as required by the approved contract.
- Exact resume action on user ping: first run job-scoped
  `squeue --job=24725445 -r`, `scontrol show job 24725445`, and authoritative
  `sacct --jobs=24725445 --parsable2 --noheader --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,ReqMem,NodeList`;
  use `seff 24725445` after terminal accounting. Do not infer completion from queue departure.
  Then validate refit artifacts and obtain independent result review before any fixed-test work.

- Resume reconciliation at `2026-11-20T01:04:24-07:00`: `squeue` and `scontrol` report the
  expected invalid completed-job ID; authoritative `sacct` records parent and batch
  `FAILED 1:0`, extern `COMPLETED 0:0`, elapsed `07:14:12`, TotalCPU `07:10:09`, 16 allocated
  CPUs, batch MaxRSS `43654448K`, requested memory 80 GB, and node `r7u17n1`. `seff` reports
  41.63 GB (52.04%) and confirms application exit code 1, so this is not OOM or timeout.
- Failure classification: application/interface validation failure after substantive fitting.
  The replay requested `[720,768)` but supplied full 61,320-hour forcing/time arrays; the locked
  inference interface correctly requires the ordered prefix ending at `end=768` and rejected
  before prediction with `ValueError: fold time axis invalid`. The minimal correction is to pass
  `time[:768]` and every forcing variable `[:768]`; no model, data, scaler, configuration,
  scientific gate, artifact, or tolerance change is implicated.
- Preserved attempt-1 evidence: the three-stage artifact package exists and its manifest records
  819 development members, zero fixed-test fit access, exact snapshot/split, 25/43/44 features,
  direct in-sample upstream mode, and `hard_zero_v1`. Artifact SHA-256 values are spinup
  `8e84721a...a79bf`, GPP `8bdeeae6...d3f05`, and SR `819bc828...b391a`; artifact manifest
  SHA-256 is `eaed33d620711fd491042e78e6988146b16585c29b9c4904170afa1855ce1c48`.
  Complete 401,768,640-byte
  raw-GPP, gated-GPP, and SR arrays have SHA-256 `f215e2f4...328e`, `cb5f561b...2662`, and
  `f575a724...c53c`. Artifact save and strict reload completed before the rejected replay.
- Contract boundary: this application/interface failure is not eligible for the unchanged
  scheduler retry. No correction, recovery submission, full refit rerun, fixed-test work, or
  release work is authorized without a fresh user-approved recovery package.
- Independent failure/recovery review: read-only agent `/root/iter016_failure_review` returns
  `pass`, conditional on fresh authority and reviewed recovery material. It confirms that no
  retraining is scientifically or technically warranted and requires immutable attempt 1, a
  validation-only attempt 2, exact artifact/array identity gates, chunked finiteness and binary
  gate checks, corrected prefix direct/chunk replay, explicit failed-job provenance, package and
  result reviews, and a stop on any mismatch.
- Recovery package preparation: the only production-source correction passes `time[:768]` and
  each forcing variable `[:768]` into the existing bounded replay. New validation-only material
  hash-locks failed job/logs, attempt-1 manifest/artifacts/arrays, scans all 100,442,160 values per
  array for finiteness and exact gating, replays artifact inference direct/chunk and against stored
  predictions, checks conditional C:N rejection and scope flags, writes only attempt-2 report and
  layout, and requests 4 CPUs/20 GB/2 h. Canonical/submitted config, manifest, and script are
  byte-identical. Initial independent review blocked because the durable report omitted failed-log
  and recovery-package identities; the report now records both log paths/hashes plus recovery
  config and execution-manifest paths/hashes. Independent refreshed exact-package re-review passed
  without blocker or concern at `2026-11-20T01:18:51-07:00`; the package is submission-eligible.
- Fresh recovery authority: user response
  `Approve the Iter016 prefix-only correction and one reviewed recovery-validation submission as stated.`
  at `2026-11-20T01:08:45-07:00`. Authorized scope is limited to the `[720,768)` forcing/time
  prefix correction, immutable read-only use of attempt 1, one independently reviewed
  validation-only attempt 2 at 4 CPUs/20 GB/2 h, one unchanged scheduler/node/transport/preemption
  retry, exact recovery gates, and independent result review. No retraining, attempt-1 mutation,
  fixed-test access, release publication, or other correction is authorized.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `coupled_release_published`; the frozen 819-member
  coupled artifact, one 205-member fixed test, development-only Iter015 uncertainty linkage, and
  catalog-last ABBY/JERC `release_0001` satisfy all technical and provenance gates. No performance
  threshold or post-hoc tuning was applied.
- Fixed-test scientific results (no performance threshold): pooled physical R2 is `0.841` for
  TOTSOMC and `0.846` for TOTSOMN; natural-log R2 is `0.858` for both; pooled GPP R2 is
  `0.925` hourly and `0.888` daily; pooled SR R2 is `0.831` hourly and `0.837` daily.
- Frozen-result limitation: SR has 128,246 negative fixed-test values out of 25,141,200
  (`0.5101%`), minimum `-2.2393 gC/m^2/day`. The approved contract has no SR gate; disclose this
  physical limitation in the release and do not alter or tune the frozen configuration.
- Limitations: ABBY/JERC only; direct sequential training; fixed test is the one campaign-defined
  two-site evaluation and will be disclosed as reused when the nine-site system is later tested;
  Iter015 uncertainty is development-only; `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`
- Next action: none within Iter016. Any response to the disclosed negative-SR behavior, nine-site
  expansion, or MCMC work requires a separately approved iteration and must not revise this frozen
  fixed-test result.
- Final validator: `bash development/three_stage_surrogate/slurm/iter016/validate_closeout_iter016.sh`
  passed with token `ITER016_FOUR_RECORD_VALIDATE_PASS`, decision
  `coupled_release_published`, `active_jobs=0`, `release=release_0001`, and `files=26`.
- Independent final result review: `pass`; published release, catalog-last evidence, payload
  inventory, provenance, uncertainty linkage, historical immutability, limitation disclosure,
  accounting, and storage caps are closeout-eligible.

## Explicit Terminal Direction

Iter016 is terminal. No later iteration is proposed or authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter016/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] Exactly one authorized local no-push closeout commit created and verified under the recorded
  expected parent and subject metadata
