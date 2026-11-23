# iter001 - Dual-Prior Contract and Coupled Inference Preflight

## Status

- Iteration ID: `iter001`
- Work type: `implementation | validation | benchmark`
- Run slug: `mcmc_optimization_iter001_dual_prior_coupled_preflight`
- Status: `completed`
- Phase: `closeout`
- HPC profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Started: `2026-11-22T04:10:45-07:00`
- Closed: `2026-11-23T00:56:47-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Locked plan SHA-256: `46775c71d8fa333024be592673b1b3dcbfe4c7577c5656289ff4ad6465eaafc6`
- Applicable campaign phase: progression items 2--3
- Alignment: `aligned`
- Approved deviation: `none`

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approve the complete Iter001 kickoff package and runtime contract`; `2026-11-22T04:10:45-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Implement and validate the dual-prior contract, validate PPE1 coupled inference, and benchmark bounded throughput in exactly three work units; stop at Iter001 closeout or on identity, leakage, compatibility, immutable-gate, storage, source, or authority failure. |
| Campaign plan identity and alignment | path and SHA-256 above; aligned; no amendment or deviation. |
| Confirmed HPC system and profile | UA Puma login `junonia.hpc.arizona.edu`; `chopinsong/standard`; CPU-only `OLMT_puma`; MCMC worktree overlay. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight`; exact run/results/manifests layout; 5 GiB cap; no cleanup or deletion. |
| Locked scientific dependencies and scope | Exact PPE1/PPE2 sources and hashes; PPE1 coupled ABBY/JERC `release_0001`; snapshot r0001; Iter015 uncertainty identities; three work units below; no likelihood, chain, training, optimization, PPE2 science, or fixed-test use. |
| Immutable gates and decision rule | Seven user-approved gates; all pass and no measured blocker -> A; all pass with concrete blocker -> B; any gate failure -> classified Iter001 failure. No numerical performance threshold. |
| Lifecycle authority | Initialization, focused implementation/tests, execution package, independent read-only package/result reviews, five bounded submissions, monitoring/accounting, evaluation, records, and closeout. |
| Resources and retry boundaries | preflight 2 CPU/10 GB/30 min; prior 2/10/1 h; interface 4/20/2 h; benchmark 4/20/2 h; final 2/10/1 h. One reviewed wrapper/import/path/manifest preflight correction and rerun; one unchanged retry per job for proven scheduler/node/transport/preemption only; zero application, numerical, data, OOM, timeout, or scientific retry. |
| Cancellation scope | Exact recorded Iter001 IDs only for duplicate/out-of-contract identity, proven common defect, fixed-test/target-free violation, or storage threat. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` under stated conditions. |
| Closeout branch | At most one scoped local no-push commit: `Complete MCMC optimization Iter001 preflight`. |

## Locked Inputs

| Dependency | Identity |
| --- | --- |
| Repository base | `feature/mcmc-optimization`; `547cc22b170b3262e8ead20e948372e9d59fbc98` |
| PPE1 parameter/generator/matrix/names/metadata | `5dac81e5...3718`; `c3b64ebd...cf2`; `d73737cb...7000`; `82853201...abe6`; `80a6ed84...e0a` |
| PPE2 parameter/note/generator/matrix/unit/names/metadata | `77faf939...87bf`; `8e3b20ab...edde`; `5cd75435...f8c`; `fc552490...5b23`; `18587ea3...ddc`; `82853201...abe6`; `b4f15580...36db` |
| Coupled release manifest/catalog | `4bdc91e2...543a`; `89a636b9...85da` |
| Snapshot/global split | `39b05495...187a`; `99467dea...fce` |
| Coupled source | `model_ELM/three_stage_coupled_release.py`; `9483e27e...5fc2` |
| Iter015 uncertainty handoff/products/validation | `c9282bba...436`; `293277a8...7e9`; `fed360f8...e2b6` |

## Frozen Work Units

1. Reusable `prior_id=ppe1|ppe2` physical density, inverse map, sampling transformation/Jacobian,
   support, conditional C:N, normalized PPE2 conditional `k_s4`, and independent numerical tests.
2. Fail-closed PPE1 coupled-release loader and ABBY/JERC target-free sequential inference tests,
   including exact hard-zero GPP, no SR clipping, deterministic replay, and incompatibility rejection.
3. Cold/load and warm benchmark on ABBY/JERC, batches 1/4/16, windows 48/720/8760 hours, five
   warm repeats, one-thread numeric libraries, peak memory, deterministic checks, and projections.

## Acceptance Gates and Decision Rule

1. Both priors pass support, density, normalization, inverse-map, transform, and Jacobian tests.
2. PPE1 coupled inference passes identity, schema, target-free, numerical, and replay tests.
3. PPE2 with PPE1 release is rejected before prediction without clipping or truncation.
4. Complete reproducible benchmark report; no arbitrary performance threshold.
5. No protected fixed-test use for fitting, tuning, priors, uncertainty, or validation.
6. Campaign plan, published artifacts, and historical records remain unchanged.
7. All work/jobs are accounted, independently reviewed, and reproducibly documented.

All gates pass and no concrete infrastructure blocker -> recommendation A and decision
`continue_existing_inference_path`. All gates pass with a concrete measured blocker -> recommendation
B and a planning-only infrastructure proposal. Any failed gate yields a classified failed decision.

## Provenance and Work-Unit Ledger

| Work unit | Canonical material | Job scope | State | Notes |
| --- | --- | --- | --- | --- |
| preflight | `slurm/iter001/preflight_iter001.slurm` | `24759169`; `24759238` | attempt 1 FAILED `1:0`; attempt 2 COMPLETED `0:0` | approved unittest recovery; attempt 2 26 s, 2 CPU/10 GB, MaxRSS 276580K; import/syntax/hash PASS |
| prior | `slurm/iter001/prior_validation_iter001.slurm` | `24773888`; `24773997` | attempt 1 FAILED `1:0`; tolerance recovery COMPLETED `0:0` | Work Unit 1; recovery 22 s, TotalCPU 7.501 s, MaxRSS 270528K; all 6 tests pass; report `29bd1e2f...5c3b` |
| interface | `slurm/iter001/coupled_interface_iter001.slurm` | `24773889` | COMPLETED `0:0` | Work Unit 2; 27 s; MaxRSS 1061956K; 2 tests and interface report pass |
| benchmark | `slurm/iter001/benchmark_iter001.slurm` | `24774027` | COMPLETED `0:0` | Work Unit 3; 28 s; TotalCPU 12.308 s; batch MaxRSS 1112544K; 18/18 cells and all repeats complete; report `f7f15068...2176` |
| final | `slurm/iter001/final_validation_iter001.slurm` | `24774088` | COMPLETED `0:0` | 9 s; TotalCPU 0.214 s; batch MaxRSS 26500K; final report `4526f8b5...4e93`; decision A bound to all three report hashes |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter001_package_review`
- First reviewed identity: execution manifest `c5b2de30...0002`; checksum manifest
  `1f8d13ff...57ff`; base `547cc22b...bc98`
- First outcome: `block`; no Python, scheduler action, or edit by reviewer.
- Findings: enforce every locked PPE input identity; validate consumed interface and uncertainty
  payloads; validate/report units; apply root/branch/HEAD/plan checks to every job; separate
  snapshot/artifact/context benchmark loading; derive A/B from evidence; strengthen final report
  validation; and broaden invalid-input tests.
- Primary response: all seven findings corrected in the canonical package; hashes and submitted
  copies were refreshed. First re-review remained `block`: remove duplicate benchmark-engine
  retention, defer A/B until result evaluation, bind units to locked source contracts, and make
  the final validator require consistent projections/release identity/reviewed decision evidence.
  Those remaining findings are corrected; passing refreshed re-review is required before preflight.
- Final package re-review: `pass` at `2026-11-22T04:41:50-07:00`; execution manifest
  `3567d7a2...e309f`, checksum manifest `e9643348...c237`; no concern blocks compute preflight.

## Validation, Reproducibility, and Results

- Static validation: canonical checksum manifest, submitted-copy comparisons, shell syntax, JSON
  parsing, and `git diff --check` passed before execution; final four-record validation is recorded
  below.
- Compute-node preflight: attempt 1 failed after all source checks because `OLMT_puma` lacks
  `pytest`; application/environment test-harness failure, not OOM/timeout/scientific rejection.
  Logs: `runs/preflight/attempt_1/slurm_24759169.{out,err}`; hashes `84a4a766...f44` and
  `c87267d7...2dcf`. Fresh approval is required before harness correction or resubmission.
- Recovery authority: user response `approved.` at `2026-11-22T04:50:59-07:00`; replace only the
  unavailable `pytest` harness with standard-library `unittest`, preserve all assertions and
  tolerances, refresh hashes/copies, obtain independent re-review, and submit one same-resource
  preflight attempt 2. No environment installation or other correction is authorized.
- Independent recovery-package review: `pass`; execution manifest `e45518d8...fd76`, checksum
  manifest `40515c57...a462`; exact unittest-only correction; attempt 2 review-eligible.
- Compute-node preflight attempt 2: job `24759238` COMPLETED `0:0`; 26 s; TotalCPU 4.690 s;
  batch MaxRSS 276580K; success tokens `MCMC_ITER001_PREFLIGHT_IMPORT_PASS`,
  `MCMC_ITER001_PREFLIGHT_TEST_SYNTAX_PASS`, and `MCMC_ITER001_PREFLIGHT_PASS`.
- Prior result: five of six tests pass. Both PPE1/PPE2 persisted inverse-map subtests fail because
  the test maps the already `%.12g`-serialized unit matrix and compares to the independently
  `%.12g`-serialized physical matrix at `rtol=1e-12`; maximum absolute/relative differences are
  `5.40012479e-11` / `5.95362337e-12`. Conditional normalization, density ratios/support,
  PPE2 width normalization, Jacobian/roundtrip, and incompatibility rejection pass.
- Interface result: pass; exact release/catalog/unit provenance; ABBY/JERC `(2,48)` outputs;
  target-free flags false, hard-zero exact, direct/chunk equivalence, deterministic replay,
  invalid-input and PPE2 incompatibility rejection. Report SHA-256 `7fc10ed5...e253`.
- Tolerance recovery authority: user directed `You can relax the tolerence threshold and rerun the
  work units, I feel 1e-12 is too strict.` The persisted inverse-map comparison is changed to
  serialization-aware `rtol=1e-10`, `atol=1e-12`; all density, normalization, support,
  transformation, Jacobian, and incompatibility tolerances remain unchanged. Work Unit 1 receives
  one reviewed same-resource rerun; the passing Work Unit 2 evidence is retained if independent
  review confirms its source/provenance are unaffected.
- Tolerance-recovery package review: independent read-only `pass`; execution manifest
  `c53a7ed8...046b`, checksum manifest `61dcd07d...5631`. The reviewer confirmed the only
  scientific-test relaxation is persisted inverse-map `rtol=1e-10`, `atol=1e-12`; driver and
  final validation use the identical rule, every other gate is unchanged, Work Unit 2 evidence
  remains applicable, and all attempt-3 submitted copies match their canonical files.
- Prior tolerance-recovery result: job `24773997` COMPLETED `0:0`; 22 s; TotalCPU 7.501 s;
  batch MaxRSS 270528K. All six tests pass and the report records both PPE1 and PPE2 support,
  finite density, source identity, and inverse-map acceptance. Report SHA-256
  `29bd1e2fc24839c09a6b76b0255ab4971f8e60d507e37875149ad05c4a8c5c3b`.
- Benchmark result: job `24774027` COMPLETED `0:0`; 28 s; TotalCPU 12.308 s; batch MaxRSS
  1112544K. All 18 ABBY/JERC x 48/720/8760-hour x batch 1/4/16 cells and five repeats per
  cell completed deterministically. Artifact/engine/forcing/prior/snapshot loading components,
  single and batched warm times, thread settings, environment, peak process RSS 329336 KiB, and
  release identity are reported. Linear projections are 232.509 s for 1,024 and 22,705.939 s for
  100,000 two-site 61,320-parameter-hour evaluations; these are measurements, not production
  budgets. Report SHA-256 `f7f150687c0352c09c12043526c640789937f542ca8b6d62a11746d44f072176`.
- Independent result review: `pass`; reports independently matched their locked hashes, Gates
  1--6 pass, and Gate 7 is satisfied through the three work units and benchmark accounting.
- Benchmark recommendation: `A`; decision `continue_existing_inference_path`. The bounded
  measurements show deterministic execution, useful batching efficiency, low memory use, and no
  concrete infrastructure blocker. Projections remain feasibility evidence rather than approved
  production budgets; posterior-call throughput must be rebenchmarked after a likelihood adapter
  exists. Decision artifact: `summaries/iter001/benchmark_decision.json`.
- Final validation: job `24774088` COMPLETED `0:0`; 9 s; TotalCPU 0.214 s; batch MaxRSS 26500K.
  It emitted `MCMC_ITER001_FINAL_PASS decision=continue_existing_inference_path` and bound report
  hashes `29bd1e2f...5c3b`, `7fc10ed5...e253`, and `f7f15068...2176` plus decision hash
  `705fe383...53fe`. Final report SHA-256 `4526f8b51cce31a58318e598c1eeb8f0255c183c03116490e92e58cc8c7c4e93`.
- Terminal accounting: preflight `24759169` FAILED `1:0`, recovery `24759238` COMPLETED `0:0`;
  prior `24773888` FAILED `1:0`, tolerance recovery `24773997` COMPLETED `0:0`; interface
  `24773889` COMPLETED `0:0`; benchmark `24774027` COMPLETED `0:0`; final validation `24774088`
  COMPLETED `0:0`. No job is active or unaccounted.
- Overall acceptance and decision: all seven gates `pass`; recommendation `A`; decision
  `continue_existing_inference_path`.
- Scientific and infrastructure limitations: PPE2 remains implementation/testing only and is
  incompatible with the PPE1 release; no observational likelihood or posterior was evaluated;
  surrogate-only linear projections are not approved production budgets; complete posterior-call
  throughput must be rebenchmarked after a likelihood adapter exists.
- Campaign-plan amendment recommendation: `none`.
- Closeout validation: `ITER001_FOUR_RECORD_VALIDATE_PASS` using
  `slurm/iter001/validate_closeout_iter001.sh`; exact command, validator hash, and output are
  preserved in `summaries/iter001/four_record_validation.txt`.
- Closeout branch: one scoped local no-push commit with expected parent
  `547cc22b170b3262e8ead20e948372e9d59fbc98` and subject
  `Complete MCMC optimization Iter001 preflight`; no push or merge.

## Explicit Terminal Direction

Iter001 is terminal at closeout. No next iteration is proposed or authorized. Iter002, likelihood
work, candidate search, posterior sampling, performance optimization, PPE2 scientific inference,
cleanup, push, and merge require fresh user direction and, where applicable, a new consolidated
kickoff approval.

## Closeout Checklist

- [x] Report finalized with exact prior, surrogate, uncertainty, site, and plan identities
- [x] Compact evidence copied to `summaries/iter001/`
- [x] `ITERATION_SUMMARY.md` and `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt with no active work
- [x] Campaign alignment and no-amendment decision are consistent
- [x] Cross-record validator identity, command, output, and pass recorded
- [x] No job is active/unaccounted and both failures are classified with authorized recoveries
- [x] Authorized closeout branch prepared for one verified local no-push commit
