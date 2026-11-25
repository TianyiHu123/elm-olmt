# iter003 - Complete Four-Observable Posterior Adapter and Validation

## Status

- Iteration ID: `iter003`
- Work type: `implementation | integration | numerical validation | bounded benchmark`
- Run slug: `iter003_four_observable_posterior`
- Status: `completed`
- Phase: `closeout`
- HPC profile: `development/hpc/puma_mcmc_worktree.md`, inheriting `development/hpc/puma.md`
- Started: `2026-11-24T23:17:39-07:00`
- Closed: `2026-11-25T03:24:53-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Locked plan SHA-256: `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`
- Applicable campaign phase: complete four-observable posterior adapter and validation before
  candidate search or MCMC pilots
- Alignment: `aligned`
- Approved deviation: `none`

## Consolidated Kickoff Approval and Runtime Contract

- User direction: `MCMC Optimization — Iter003 Kickoff`, received `2026-11-24`.
- Primary consolidated package presented after Section 4A recovery and dependency verification.
- User approval: `I approved this complete package with one addition: give you 4 shared
  unchanged-scope retry budget. Now kickoff.`, received `2026-11-24`.
- The four shared unchanged-scope retries replace the proposed single shared retry. The absolute
  submission ceiling is ten: five planned submissions, at most one reviewed preflight-correction
  rerun, and four shared unchanged-scope retries.
- Goal: implement and validate a reusable ABBY/JERC PPE1 posterior combining the exact 18-D prior,
  frozen target-free three-stage surrogate, immutable Iter002 observations/fixed uncertainty,
  independently selectable GPP/SR resolutions, and fixed joint C/N likelihood. Stop at Iter003
  closeout without starting candidate search, MCMC, PPE2 science, or Iter004.
- Work units: general release/observation loading; pure likelihood kernels; integrated posterior;
  independent validation and bounded benchmark.
- Runtime root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter003_four_observable_posterior`.
- Storage cap: 5 GiB of new Iter003 runtime evidence. Retain submitted copies, immutable config,
  manifests, logs, JSON/CSV evidence, and accounting. No cleanup, deletion, or published overwrite.
- Puma: account `chopinsong`, partition `standard`, CPU-only `OLMT_puma`, one node/task, one-thread
  numerical libraries.
- Planned jobs: preflight 2 CPU/~10 GB/30 min; component 2 CPU/~10 GB/1 h; integrated validation
  4 CPU/~20 GB/2 h; bounded benchmark 4 CPU/~20 GB/2 h; final verification 2 CPU/~10 GB/30 min.
- Retry budgets: one reviewed preflight-only wrapper/import/path/submitted-copy/manifest correction
  and rerun; four shared unchanged-scope retries for proven scheduler/node/preemption/transport
  failures. Zero automatic application, code, schema, data, dependency, scientific, numerical,
  OOM, timeout, or performance retries.
- Fresh correction authority: user authorized one component application correction on
  `2026-11-25`, with the requirement to retain the missing `pytest` dependency as an unresolved
  issue and remind later iterations to install `pytest` or use a supported alternative test
  package/framework.
- Gate 5 correction authority: user authorized the narrow six-case independent C/N reference and
  validator correction, refreshed independent review, and one integrated evidence rerun on
  `2026-11-25`.
- Monitoring: job-scoped `squeue` while active and terminal `sacct` for every attempt; `seff` where
  useful. Empty queue state is not terminal accounting.
- Cancellation: exact recorded Iter003 jobs only for duplicate submission, identity/config drift,
  wrong scope, target leakage, fixed-test misuse, output collision, release-write risk, storage-cap
  threat, or explicit user direction; account afterward. Cancellation grants no retry.
- Outside-sandbox authority: locked `sbatch`, job-scoped read-only monitoring/accounting, and
  bounded `scancel` under the listed conditions.
- Closeout branch: at most one scoped local no-push commit with expected parent
  `67ffd6a1cd35e4aab0678e30829fa8e2743f6ff5` and subject
  `Complete MCMC optimization Iter003 posterior adapter`. No push or merge.

## Section 4A Recovery and Dependency Evidence

- Repository `git@github.com:TianyiHu123/elm-olmt`; worktree
  `/xdisk/chopinsong/tianyihu/elm-olmt-mcmc`; branch `feature/mcmc-optimization`; clean starting
  HEAD `67ffd6a1cd35e4aab0678e30829fa8e2743f6ff5`.
- Iter002 is closed with decision `observation_release_0001_published`; Iter001 and Iter002 jobs
  were reconciled through terminal `sacct`, with no active or unaccounted job.
- Observation catalog/manifest/validation SHA-256:
  `cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8`,
  `460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2`, and
  `19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef`.
- Every one of 18 observation-manifest files matches its recorded hash and byte size.
- Coupled release manifest/catalog SHA-256:
  `4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a` and
  `89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da`; all manifested payloads
  match.
- Forcing snapshot SHA-256 `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a`;
  all seven snapshot artifacts match; member split
  `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce`.
- Iter015 handoff/manifest/validation SHA-256:
  `c9282bbad9abc2d6519329018ca9be026171f071e6e689a44fb2af102784f436`,
  `293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9`, and
  `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
- All PPE1 and PPE2 prior inputs match the identities locked in `model_ELM/mcmc_prior.py`.
- Current account limits have ample headroom; `/xdisk/chopinsong` reports 8.1/19.5 TiB used.
  The `xdisk` allocation-query service returned HTTP 500 during kickoff, so expiration metadata
  must be retried and recorded during preparation; failure does not permit silent storage changes.

## User-Directed Refinements to the Historical Iter002 Proposal

The historical Iter002 record remains unchanged. This Iter003 contract records the later
user-directed refinements:

1. Support all four independent hourly/daily GPP/SR combinations.
2. Use `daily/daily` as the initial baseline, not the only supported configuration.
3. Use three-stage-specific module names.
4. Introduce a general public three-stage release loader without encoding PPE1 in its public name.
5. Keep the validated PPE1-specific loader as a temporary internal compatibility layer.
6. Separate pure numerical likelihood kernels from loading and posterior orchestration.
7. Defer removal of the PPE1-specific loader until the full MCMC pipeline is finalized and a
   separate cleanup is authorized.

These refinements authorize neither PPE2 inference nor a campaign-plan change.

## Frozen Work Units and Architecture

### Work Unit 1 - General release loading and immutable observation contexts

- Add `model_ELM/mcmc_three_stage_release.py` with a versioned immutable
  `ThreeStageReleaseConfig` and general `load_three_stage_release(prior, config)` public interface.
- The only Iter003 implementation may delegate internally to
  `model_ELM.mcmc_coupled_adapter.load_ppe1_coupled_release()`; unknown configurations and all
  incompatible prior, trained-support, release, site, schema, snapshot, source, and uncertainty
  identities fail closed.
- Preserve `mcmc_coupled_adapter.py`, its PPE1 loader, and all Iter001 regression coverage.
- Add `model_ELM/mcmc_three_stage_observations.py` with frozen site contexts and read-only arrays.
- Resolve published daily source-hour indices into their variable-specific hourly arrays, reapply
  the corresponding published validity masks, map retained timestamps to exact forcing hours,
  reproduce counts/means/RMS sigmas, and aggregate predictions over the same forcing hours.

### Work Unit 2 - Pure numerical likelihood kernels

- Add `model_ELM/mcmc_three_stage_likelihood.py` with no filesystem, release, forcing, surrogate,
  or prior loading.
- Implement normalized Gaussian GPP/SR likelihoods with fixed variance
  `obs_sigma**2 + surrogate_rmse**2`, no fitted sigma, no extra square-root reduction, and no
  second GPP gate.
- Implement normalized joint bivariate-lognormal C/N likelihood with fixed depth fractions,
  residual `log(obs) - log(depth_adjusted_prediction) + total_bias_correction`, the published
  total covariance, Cholesky factorization, triangular solves, and no explicit inverse.
- Reject nonpositive/nonfinite soil predictions and invalid covariance rather than clipping.

### Work Unit 3 - Integrated posterior

- Add `model_ELM/mcmc_three_stage_posterior.py` with compact scalar/batch APIs.
- Evaluate the exact 18-D PPE1 prior and reject unsupported parameters before surrogate work.
- Run the frozen target-free surrogate once per scalar or batch and reuse predictions across
  independently configured flux operators and C/N.
- Return site, prior, resolutions, CV, include-C/N flag, component values, total, counts,
  evaluation validity, and complete provenance. Disabled C/N is exactly `0.0`.
- Preserve raw GPP only as a diagnostic; likelihood uses released hard-zero GPP. SR is unclipped.
- Provide a separately tested sampling-coordinate wrapper that adds the Jacobian; the authoritative
  physical-space posterior never includes it.

### Work Unit 4 - Independent numerical validation and bounded benchmark

- Add focused `tests/test_mcmc_three_stage_*.py` coverage and canonical material under
  `development/mcmc_optimization/slurm/iter003/`.
- Produce `posterior_validation.json`, `resolution_parity_summary.csv`,
  `likelihood_reference_tests.json`, and `posterior_benchmark.json`.
- One scalar full-release evaluation per site is authorized for integration validation, reusing
  each site's prediction across all four resolution combinations. No full-window batch sweep.

## Frozen Scientific and Numerical Configuration

- Prior: `prior_id=ppe1`; exact 18-parameter physical order/support/density from `mcmc_prior.py`.
- PPE2 implementation and tests remain; PPE2 scientific posterior requests against the PPE1
  surrogate must fail before prediction.
- Sites: ABBY and JERC, independent contexts and posteriors.
- Surrogate: frozen coupled three-stage PPE1 `release_0001`; target-free sequence
  parameters -> full-profile C/N -> hourly hard-zero GPP -> hourly unclipped SR.
- Forcing: snapshot r0001; no-leap; 61,320 hours/site; 720-hour history.
- Observation release: immutable Iter002 `release_0001`; no raw-source regeneration.
- Resolution combinations: `daily/daily` default plus `hourly/hourly`, `daily/hourly`, and
  `hourly/daily`.
- Daily thresholds: GPP at least 18 paired valid hours; SR at least 22 valid hours. Masks and
  windows remain independent; no simultaneous-observation requirement.
- Full-release counts: ABBY GPP 15,437 hourly/514 daily, SR 26,264 hourly/1,095 daily; JERC GPP
  19,844 hourly/699 daily, SR 51,162 hourly/2,114 daily.
- Fixed flux uncertainty: release observation sigma plus matching Iter015 hourly/daily RMSE in
  quadrature. Flux bias remains report-only.
- C/N: CV 0.20, 0.30 baseline, and 0.50; fixed depth operator; fixed surrogate+depth bias sign;
  paired total covariance. `include_cn=True` is primary and `False` is the controlled comparison.
- Fixed-test policy: no use of the 205 fixed-test members for surrogate fitting, tuning, selection,
  robustness, uncertainty, or validation. Complete 1,024-member use remains limited to the frozen
  PPE1 depth operator, with no independent combined-operator validation claim.
- Retained approximation: Iter015 daily errors use complete model days while some observation
  daily means contain 18--23 valid hours.

## Exact Validation Tolerances and Gates

- Hashes, schema, site, units, timestamps, masks, counts, indices, and ordering: exact equality.
- Reconstructed daily values and RMS sigmas: `rtol=0`, `atol=1e-12`.
- Independent Gaussian and C/N references: `rtol=1e-12`, `atol=1e-10`.
- Posterior component sum: `rtol=0`, `atol=1e-10`.
- Scalar/batch and physical/sampler equivalence: `rtol=1e-12`, `atol=1e-10`.
- Repeated surrogate predictions: exact array equality and identical checksums.
- Historical serialization-aware prior fixture alone retains `rtol=1e-10`, `atol=1e-12`; no new
  likelihood or posterior tolerance is relaxed.
- Independent references must not call production likelihood kernels: Gaussian references use
  scalar accumulation; C/N uses an independently coded closed-form 2x2 determinant/quadratic.

Immutable gates:

1. Dependency integrity.
2. Observation alignment.
3. All four resolution combinations for both sites.
4. Gaussian likelihood correctness.
5. Joint C/N correctness for all three CVs.
6. Prior/posterior correctness and physical/sampler Jacobian handling.
7. Determinism, scalar/batch equivalence, site independence, ordering, and target-free inference.
8. Failure handling and prior/coupled/legacy SR-only backward compatibility.
9. Complete reproducible performance/resource evidence.
10. Independent package/result review, terminal accounting, provenance, records, and closeout.

Decision rule:

- All gates pass and no material performance blocker -> `four_observable_posterior_validated`.
- All correctness/review gates pass but a declared performance criterion triggers ->
  `four_observable_posterior_validated_performance_blocker`; propose later infrastructure work only.
- Any scientific, identity, numerical, compatibility, leakage, or record gate fails ->
  `iter003_validation_failed`.
- Incomplete evidence due to missing authority or unresolved external state -> `blocked` without
  gate reinterpretation.

A material performance blocker is annual warm scalar median above 5 seconds, projected 1,024
annual evaluations above 2 hours/site, batch-16 per-candidate time not improving over scalar, or
peak RSS above 16 GiB. These criteria do not authorize an inference-engine rewrite.

## Locked Benchmark Windows

Every target interval carries its required 720-hour prefix.

| Site | Start no-leap day/hour | Window | GPP hourly/daily | SR hourly/daily |
| --- | ---: | ---: | ---: | ---: |
| ABBY | 1017 / 24408 | 48 h | 36 / 1 | 48 / 2 |
| ABBY | 1017 / 24408 | 720 h | 409 / 11 | 718 / 30 |
| ABBY | 1017 / 24408 | 8760 h | 5,124 / 179 | 8,756 / 365 |
| JERC | 116 / 2784 | 48 h | 42 / 2 | 48 / 2 |
| JERC | 116 / 2784 | 720 h | 294 / 10 | 720 / 30 |
| JERC | 116 / 2784 | 8760 h | 573 / 19 | 8,711 / 362 |

Each site/window/resolution combination receives one cold measurement, five warm repeats,
deterministic scalar and batch-4/batch-16 measurements, and component timing. Fixtures are fixed
synthetic in-support points, not PPE members or candidate-search output. Full-window future
candidate/MCMC projections are estimates only.

## Authorized Source, Execution, Evidence, and Record Paths

Authorized new or modified implementation paths:

- `model_ELM/mcmc_three_stage_release.py`
- `model_ELM/mcmc_three_stage_observations.py`
- `model_ELM/mcmc_three_stage_likelihood.py`
- `model_ELM/mcmc_three_stage_posterior.py`
- focused `tests/test_mcmc_three_stage_*.py`

Existing `mcmc_prior.py`, `mcmc_coupled_adapter.py`, coupled engine sources, legacy SR-only code,
campaign plan, historical records, and published products are read-only dependencies. A needed
change outside the authorized paths stops for fresh authority.

Authorized records and canonical material:

- `development/mcmc_optimization/iterations/iter003.md`
- `development/mcmc_optimization/slurm/iter003/`
- `development/mcmc_optimization/summaries/iter003/`
- `development/mcmc_optimization/registry.csv`
- `development/mcmc_optimization/ITERATION_SUMMARY.md`
- `development/mcmc_optimization/handoff/CURRENT.md`

External layout: `config/`, `manifests/`, `runs/<job>/attempt_<n>/`, `results/`, and `logs/` under
the approved runtime root. Submitted copies and immutable config/manifest hashes must match
canonical material before every job.

## Independent Read-Only Review

- Package review occurs after controlled preparation and before preflight. A different reviewer
  makes no edits and performs no scheduler action; it checks the contract, paths, source/submitted
  hashes, scientific compatibility, leakage boundary, independent tests, tolerances, resources,
  storage, and fail-closed behavior. `block` requires correction and passing re-review.
- Result review occurs after jobs 1--4 are terminal and before final verification. It independently
  checks product identities, reference arithmetic, all gates, performance criteria, accounting,
  and conclusions. Reviewer execution, if any, remains read-only and cannot alter evidence.

## Deferred Technical Debt

### Remove PPE-Specific Three-Stage Surrogate Loader After Full MCMC Pipeline Finalization

- Status: `Deferred`.
- Current temporary implementation: the general `load_three_stage_release()` may delegate to the
  validated `load_ppe1_coupled_release()` implementation.
- Long-term objective: one general, configuration-driven three-stage surrogate loader rather than
  PPE1/PPE2-specific loader functions.
- Future cleanup requirements:
  1. Make prior/PPE identity, release paths, schema, source identity, snapshot, and compatible
     uncertainty metadata explicit validated inputs.
  2. Remove hardcoded PPE1 release/source identities from the generic implementation while
     preserving strict compatibility checks.
  3. Migrate all MCMC consumers to the general loader.
  4. Establish numerical equivalence and regression coverage for the validated PPE1 pipeline.
  5. Deprecate/remove `load_ppe1_coupled_release()` only after the complete MCMC pipeline is
     finalized, validated, and separately authorized.
- Iter003 boundary: record and carry this debt into `handoff/CURRENT.md`; do not remove or
  substantially redesign the PPE1 loader. Preserve historical loader and immutable artifacts.

## Explicit Exclusions and Stop Conditions

No Sobol candidate search, walker initialization, local optimization, `emcee`, chain, calibrated
posterior interpretation, surrogate retraining/modification, Iter015 uncertainty recalibration,
Iter002 release/QC modification, raw preprocessing, ELM spinup work, protected fixed-test use,
PPE2 science, legacy SR-only refactor/removal, PPE1-loader removal, file deletion, published
overwrite, push, merge, or Iter004 initialization.

Stop on identity drift, dependency incompatibility, target leakage, unauthorized path need,
application/data/schema/scientific/numerical failure, unapproved resource change, exhausted retry
budget, storage threat, immutable-gate failure, unaccounted scheduler state, or closeout validation
failure. Continue otherwise through terminal accounting, independent review, record validation,
and the authorized local no-push closeout commit.

## Provenance and Work-Unit Ledger

| Work unit | Canonical material | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| preflight | `slurm/iter003/preflight_iter003.slurm` | package/import/dependency/static validation | attempt 2 job `24811617` passed | attempt 1 `24811598` classified identity-transcription failure; sole preflight correction rerun consumed |
| component | `slurm/iter003/component_iter003.slurm` | unit and compatibility tests | attempt 2 job `24811705` passed | attempt 1 application/test-package failure corrected under fresh user authority |
| integrated | `slurm/iter003/integrated_iter003.slurm` | integrated posterior validation | attempt 2 job `24812674` passed | attempt 1 `24811719` produced incomplete Gate 5 reference coverage; corrected under fresh user authority |
| benchmark | `slurm/iter003/benchmark_iter003.slurm` | bounded cold/warm benchmark | attempt 1 job `24811738` passed | no performance blockers; shared retries unused |
| final | `slurm/iter003/final_iter003.slurm` | evidence verification | attempt 1 job `24812698` passed | decision `four_observable_posterior_validated` |

## Validation, Results, and Closeout

- Static validation: canonical checksums, submitted-copy comparisons, shell syntax, JSON parsing,
  and `git diff --check` passed before preflight.
- Package review: initial independent read-only review returned `block` for incomplete benchmark
  decomposition, insufficient evidence enforcement in final validation, mutable context mappings,
  incomplete uncertainty provenance, and missing failure/isolation/backward-compatibility tests.
  The package was corrected within scope. Independent read-only re-review returned `pass` with no
  blockers. Reviewed config SHA-256
  `11e72e7c75524918ab1f929978d5d333a9bf71450331eba26b45acea3d040c35`, execution-manifest
  SHA-256 `91ffd70ffbeeae47e1eb65eeee8a59fe269680b83da31f98c622c56b74701c06`, and checksum-manifest
  SHA-256 `948e3ee75473bb2abbf3fda3f8919cbd4f13025846e097a0a0d431f3a5cd08c0`.
  After the authorized component correction, a further independent read-only review returned
  `pass`: config `fd24d847ab4b711ff7d8583eb7e1d5e54295bdf1a55d917d5f20e6d90a89cb0c`, execution manifest
  `e74bfc121d42da7890b7320d046f38fd859c649708bbe1a525677ef8176302b1`, and checksum manifest
  `5b14076b3522bea3a6f6c0b831bc0c0518d661c16414fd54f1af1086463d9e57`.
- Jobs/accounting: preflight attempt 1 job `24811598` reached terminal `FAILED (1:0)` after
  `00:00:07` on `r7u13n1` with 2 CPUs and 10 GB requested. The submitted config identity passed,
  then the initial verifier checksum failed because the `sbatch` export transcribed
  `ITER003_VERIFY_SHA=5f836582eb0c...` instead of the canonical/submitted/manifest value
  `5f8365828c35fd5c72d48be7f7ca3ffdb497e5a8ab1a968ad2b1ce763a07e0f2`. Repository Python did
  not start. This is a preflight submitted-copy/manifest identity invocation correction, not an
  application, data, schema, scientific, or numerical failure. Independent correction review is
  `pass`; the sole preflight correction rerun was consumed. Preflight attempt 2 job `24811617`
  reached terminal `COMPLETED (0:0)` after `00:00:27` on `r7u09n2`; batch MaxRSS was 247604 KiB.
  All execution identities, imports, pure likelihood smoke tests, and the storage check passed.
- Component attempt 1 job `24811658` reached terminal `FAILED (1:0)` after `00:01:00` on
  `r7u15n1`; batch MaxRSS was 1264144 KiB. The 10 Iter003 tests, 6 Iter001 prior tests, and 2
  Iter001 coupled-interface tests all passed. The next command failed while importing historical
  `tests/test_mcmc_iter009_geometry.py` because it imports `pytest`, which is absent from the locked
  `OLMT_puma` Python. The command used `unittest discover`, which would not execute that file's
  function-style pytest tests even if import succeeded. This is an application/test-package
  failure, not scheduler/node/preemption/transport; no shared retry was consumed and no automatic
  application retry is authorized.
- Authorized correction: add explicit `unittest` coverage for the legacy coordinate-transform,
  invalid-coordinate, finite-difference Jacobian, and `MCMC_forcing` sampler-target contracts;
  remove the ineffective pytest-file-through-`unittest discover` command; refresh and review all
  affected identities; then rerun the unchanged-scope component work unit once.
- Component attempt 2 job `24811705` reached terminal `COMPLETED (0:0)` after `00:01:02` on
  `r4u03n1`; batch MaxRSS was 1354348 KiB. All 11 Iter003, 6 Iter001 prior, and 2 Iter001 coupled-
  interface tests passed, followed by component release/observation validation.
- Integrated attempt 1 job `24811719` reached terminal `COMPLETED (0:0)` after `00:00:29` on
  `r7u17n2`; batch MaxRSS was 1128748 KiB. All two-site/four-resolution, alignment, component-
  isolation, replay, prior/posterior, batching, failure, and target-free checks passed.
- Benchmark attempt 1 job `24811738` reached terminal `COMPLETED (0:0)` after `00:02:36` on
  `r7u17n2`; batch MaxRSS was 1055832 KiB. All 72 warm cells, 24 cold measurements, and five warm
  repetitions completed with no material performance blocker; benchmark peak RSS was 504888 KiB.
- Independent result review returned `block`: the retained independent likelihood package has
  eight flux references and C/N references for ABBY/JERC at CV 0.30 only. Production values exist
  for CV 0.20/0.30/0.50, but Gate 5 requires independently implemented numerical references for
  both sites at every CV. The final validator currently checks only key presence and must also
  enforce all six site/CV reference cases. This is an application/evidence correction requiring
  fresh authority. The user authorized the exact correction; integrated attempt 2 job `24812674`
  passed with all 14 independent reference cases, including both sites at CV 0.20/0.30/0.50.
- Final independent result review: `pass`. All eight resolution rows are present; posterior
  component-sum maximum absolute error is zero; exact replay, scalar/batch parity, component
  isolation, sampling-coordinate Jacobian, invalid-input handling, PPE2 rejection, legacy
  compatibility, and no-target-leakage evidence pass.
- Likelihood arithmetic: eight independent flux references and six independently coded joint-C/N
  references pass `rtol=1e-12`, `atol=1e-10`; maximum normalized tolerance usage is `0.000194`.
  Baseline full-window daily/daily component values are ABBY prior/GPP/SR/CN
  `24.323430/-3151.364059/-4591.367822/-2.957532` and JERC
  `24.323430/-3381.363805/-19704.520779/-14.475787`.
- Four-resolution support: both sites validated `daily/daily`, `hourly/hourly`, `daily/hourly`,
  and `hourly/daily`, with variable-specific full-window counts and no cross-resolution component
  contamination. `include_cn=False` yields an explicit zero C/N component.
- Benchmark: 72 warm cells, 24 cold measurements, and five repeats per cell pass. Annual scalar
  medians span 0.0711--0.2950 seconds; annual daily/daily medians are 0.0785 seconds ABBY and
  0.0711 seconds JERC. Batch-16 improves per-candidate time in all eight annual configurations.
  Maximum 1,024-evaluation projection is 302.06 seconds; measured benchmark peak is 504888 KiB;
  no material performance blocker applies. Projections are estimates, not execution budgets.
- Final verification job `24812698` reached terminal `COMPLETED (0:0)` after `00:00:17`; batch
  MaxRSS was 274852 KiB. It returned `pass` and decision candidate
  `four_observable_posterior_validated`. All eight attempts are terminal and classified; zero
  shared scheduler retries were consumed and four remain unused.
- Results/gates/decision: all ten gates `pass`; decision
  `four_observable_posterior_validated`.
- Final package identities: config SHA-256
  `0038e424d5c65f8a6ddcec78a79af2c164fa63e0776d44a7ff8badc6e5c68bcc`; execution checksum
  manifest `492ad4fb4380e8c3d85b23073be574b2c5b23a232c7a49bfcc271851fb46032d`; execution manifest
  `0b5f651336e30098a2b1c58d60e1d617f38ddfc2efa587d12bc7c68ba3882ba4`; final validation
  `four_observable_posterior_validated` with posterior evidence
  `cc21836e92bb8eaf5aa960ece2a02b9ad67f764d85e58b5eda5945c45a15e6ca` and references
  `deb2a5e05d0dee69786175393f54c74ec796ab0be726a706c33fe78d971e41e4`.
- Campaign-plan amendment recommendation: none.
- Closeout mode: one local no-push commit with expected parent
  `67ffd6a1cd35e4aab0678e30829fa8e2743f6ff5` and subject
  `Complete MCMC optimization Iter003 posterior adapter`.
- Four-record validation: `ITER003_FOUR_RECORD_VALIDATE_PASS`; validator
  `validate_closeout_iter003.sh` SHA-256
  `15496e584fff9c9dd11ca20f7011ba5d0de533a032885a7546c292210251711b`; final accounting
  SHA-256 `c076920cdd27ddb28ac1248b030c90e986ffb454ff56aa545d2c28056f7dfa36`.

## Unresolved Issues

- **Missing `pytest` in locked `OLMT_puma` environment.** Status: unresolved environment/test-
  tooling debt. `tests/test_mcmc_iter009_geometry.py` is pytest-style, but the selected Python
  cannot import `pytest`. Iter003 uses explicit standard-library `unittest` regression coverage
  instead and does not change the environment. A later authorized environment-maintenance or
  campaign iteration must either install and lock a compatible `pytest` package or adopt another
  supported test package/framework and migrate the affected tests. Carry this reminder in
  `handoff/CURRENT.md` until resolved.

## Proposed Next-Iteration Plan (Planning Only)

**Title:** Initial Candidate Search and MCMC Pilot Planning.

- Objective: design, but do not yet execute, a bounded PPE1 ABBY/JERC candidate-search and initial
  MCMC pilot that consumes the validated four-observable posterior. Use site-independent posterior
  contexts and `daily/daily`, `include_cn=True`, CV 0.30 as the initial scientific baseline while
  retaining the validated alternative resolution and flux-only comparison interfaces.
- Locked dependencies: Iter003 decision `four_observable_posterior_validated`; final config
  `0038e424...8bcc`; PPE1 18-D prior; coupled `release_0001`; forcing snapshot r0001; Iter002
  observation release; fixed Iter015/depth uncertainties; exact parameter/sampling-coordinate,
  hard-zero GPP, unclipped SR, target-free, fixed-test, and provenance contracts.
- Proposed work units: choose deterministic candidate generation and ranking; define bounded local
  refinement and diversified walker initialization without changing the posterior; project and
  justify compute/storage from measured Iter003 scalar/batch performance; specify checkpoint,
  restart, convergence, failure, independent-review, and scientific non-interpretation gates; and
  present one consolidated kickoff package before initialization.
- Required planning decisions: candidate count and seed, batch size, site separation, walker count
  and geometry, pilot length/checkpoint cadence, move configuration, acceptance/ESS/autocorrelation
  evidence, exact CPU/memory/walltime/submission/storage limits, retry budgets, and stop rule.
- Exclusions until fresh approval: no candidate generation, optimization, walker initialization,
  `emcee`, chain, posterior interpretation, PPE2 science, uncertainty changes, artifact rewrites,
  loader cleanup, or Iter004 scaffold. The unresolved missing-`pytest` tooling issue must be handled
  by a separately locked install or supported alternative before relying on pytest-style tests.
- Approval boundary: this proposal is planning-only. Recover the closed Iter003 state under
  Section 4A and obtain a new consolidated user approval before creating Iter004 records, running
  repository Python, creating runtime directories, submitting jobs, or committing Iter004 work.

## Closeout Checklist

- [x] Final report and compact evidence complete
- [x] Registry, cumulative summary, and handoff reconciled
- [x] All jobs terminal and failures classified
- [x] Independent package and result reviews pass
- [x] Four-record validator identity/output preserved
- [x] Deferred loader debt carried into the handoff
- [x] At most one authorized local no-push commit created
