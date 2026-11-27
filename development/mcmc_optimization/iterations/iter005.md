# iter005 - Prior-Aware Bounded Sampler Reconstruction and Corrected Four-Observable Pilot

## Status and authority

- ID: `iter005`; work type: `implementation | integration | numerical validation | sampling pilot`.
- Status: `completed`; started `2026-11-26T23:32:41-07:00`; closed `2026-11-27T01:41:00-07:00`.
- Acceptance result: `fail`; decision: `iter005_validation_failed`.
- User approved the complete consolidated kickoff package in the message `Full package approved.`
- The same message conditionally authorized relaxing a demonstrably too-strict floating-point tolerance after diagnosis establishes correct implementation. Such a correction/rerun consumes **one of the four shared retry opportunities**, leaving at most three unchanged-scope infrastructure retries if used; the ten-submission ceiling remains. Preserve the failed attempt, numerical diagnosis, revised value, source/manifest identities, and independent re-review before rerun. This does not authorize changing prior support, scientific inputs, required identities, Jacobian correctness, or mixing criteria.
- Primary agent is the sole writer and scheduler operator. Independent reviewers are read-only.
- Stop after Iter005 four-record closeout. Iter006 is planning-only. No push or merge.

## Recovery and campaign alignment

- Repository `TianyiHu123/elm-olmt`, Puma worktree `/xdisk/chopinsong/tianyihu/elm-olmt-mcmc`, branch `feature/mcmc-optimization`, starting HEAD `205cd410f612bd7c751728d722c599b09aca6b86`, clean at kickoff.
- Plan `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md` SHA-256 `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`; aligned, approved deviation `none`.
- Workflow `development/mcmc_optimization/WORKFLOW.md`; profile `development/hpc/puma_mcmc_worktree.md` inheriting `puma.md`; active host `junonia.hpc.arizona.edu`.
- Iter004 closed with `iter004_validation_failed`. ABBY/JERC out-of-support proposal rates were `7079/8192` and `7350/8192`. All 16 prior Slurm submissions were verified terminal by live job-scoped `sacct`; scoped `squeue` was empty. Final accounting SHA-256 `20fe9fe77f2a81f25f07e566c3c1e5f7da9d5677f195420c15f236300d6184e8` and final validation SHA-256 `c344218bd58f460f73217c0b0e75c89cf842c618dc7ac80f27710063bdf76763` match stored files.
- User-directed refinement replaces the historical Iter004 next proposal's broad geometry audit with direct prior-unit/logit reconstruction and bounded diagnostics; the Iter004 report is immutable.

## Frozen science and dependencies

- PPE1, exactly 18 physical ELM parameters in canonical order; independent ABBY/JERC targets; daily GPP and daily SR; `include_cn=True`; C/N observation CV `0.30`; forcing indices `[720,61320)`.
- Frozen target-free PPE1 coupled surrogate `release_0001` with hard-zero GPP and unclipped SR; immutable observation `release_0001`; fixed Iter015 development-only surrogate errors, full-ensemble PPE1 depth operator, C/N covariance and bias.
- Protected fixed-test members remain outside surrogate fitting, selection and uncertainty. PPE2 scientific requests with the PPE1 release fail closed. No likelihood kernel or scientific input changes.
- PPE1 parameter/generator/metadata SHA-256: `5dac81e5a00088e9d8e94b88f4805bc16076a51f1895cf2e5f78a6382e243718` / `c3b64ebdd4116ff7aff6c3c4ecc2ac2351f2b275c58cc84be9074ffcdcf88cf2` / `80a6ed8403df389b746d33aef389dde3f89754d94df9f74953acce98dd400e0a`.
- Snapshot/split: `39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a` / `99467dea4d34834c4ea4aaea9e416620cd9bc16310f567f7b7fc1735abe74fce`.
- Surrogate manifest/catalog/constraints: `4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a` / `89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da` / `29af5ac158761baea828868d1a259f1f295e279c6178b2dd93650c0c2864a6b6`.
- Iter015 handoff/manifest/validation: `c9282bbad9abc2d6519329018ca9be026171f071e6e689a44fb2af102784f436` / `293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9` / `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
- Observation catalog/manifest/validation: `cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8` / `460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2` / `19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef`.
- Iter003 posterior/reference validation: `cc21836e92bb8eaf5aa960ece2a02b9ad67f764d85e58b5eda5945c45a15e6ca` / `deb2a5e05d0dee69786175393f54c74ec796ab0be726a706c33fe78d971e41e4`.

## Approved work and numerical contract

1. Add focused prior-unit/logit geometry `u=sigmoid(z)`, `theta=Prior18.inverse_unit(u)`; strict inverse from validated physical support and interior unit values. Stable log-Jacobian; no clipping, reflection or uncorrected resampling.
2. Independently validate the analytical full Jacobian and `log p_z=log p_theta+log|det dtheta/dz|=sum(log u+log(1-u))+sum(flux/CN likelihoods)+const`. Preserve full Jacobian in blobs. Compare all 18 prior/surrogate snapshot bounds and conditional C:N metadata only in a compact development-validation artifact; operational release, schema, prior and support checks remain.
3. Integrate into existing audited `emcee 3.1.6` sampler. Preserve 64 walkers/site, 0.80 `DEMove(sigma=1e-5,gamma0=None)` plus 0.20 `DESnookerMove(gammas=1.7)`, append-only proposal ledger, structured blobs, HDF checkpoints, non-overwriting outputs and exact restart. Reuse only Iter004 physical walkers after hash, source, support and physical-target replay. No new Sobol search, no old-backend resume. Mint versioned coordinate and sampler identities. New 16 versus 8+8 restart must match positions, log probabilities, blobs, acceptance, random state, checkpoint iteration and all identities exactly.
4. Run independent ABBY/JERC 128-step pilots with 64-step checkpoints; no automatic continuation, optimization, tuning, or production sampling. Report numerical, support, surrogate, ordinary rejection, acceptance, movement, boundary, resource and convergence diagnostics.

Strict references: `rtol=1e-12`, `atol=1e-10`; component sum `rtol=0`, `atol=1e-10`. Scalar/batch parity alone: `rtol=1e-7`, `atol=1e-8`. Interior physical round-trip `rtol=1e-12`, `atol=0`; unit absolute error `<=1e-12` on declared interior fixtures. Independent analytical Jacobian `rtol=1e-12`, `atol=1e-10`; two density expressions absolute difference `<=1e-9`.

Per site, 8,192 proposals: zero ordinary mapped-proposal support violations, unexpected mapping errors, unexplained exceptions and parameter-dependent surrogate numerical failures. Extreme coordinate saturation gets a distinct reason and may occur at most 8/site and 2/walker. Movement criteria, nonfatal if correctness passes: acceptance fraction `[0.05,0.80]`, at most 16 zero-move walkers, 64 distinct final states, rank 18, condition `<=1e12`, median walker net prior-unit displacement `>=0.01`. Report per-parameter occupancy within `0.01` of unit boundaries. No convergence claim.

Ten immutable gates: (1) plan/source/release identity; (2) development-only bounds/schema; (3) mapping and support; (4) Jacobian and density; (5) scalar/batch, failure and regression; (6) physical walker reuse and new identity; (7) restart/backend protection; (8) bounded site pilots; (9) resources, provenance, storage, retries, accounting; (10) independent reviews and closeout. Gates 2–7 pass before pilots. Decisions: `bounded_sampler_pilot_validated`, `bounded_sampler_pilot_validated_with_mixing_limitations`, `iter005_validation_failed`, or `blocked`. Mapping, Jacobian, support, release, checkpoint and identity failures are fatal, not mixing limitations.

## Approved resources, output and retry boundary

- Account `chopinsong`, partition `standard`, environment `OLMT_puma`, CPU-only, one node/task, one-thread numerical libraries. Puma derives 5 GB/CPU; omit both memory directives.
- External root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot`; `config/`, `manifests/`, `submitted/`, `logs/`, `reviews/`, `results/`, and independent site walker/restart/pilot/checkpoint/diagnostic subdirectories. New storage cap 2 GiB. Preserve bulk artifacts, logs and failures externally, compact decision evidence in Git. Verify project expiration for Iter005 before first submission.
- Five planned jobs: preflight/tests 2 CPU/1 h; density/integration/restart 2 CPU/1 h; ABBY pilot 4 CPU/2 h; JERC pilot 4 CPU/2 h; diagnostics/evidence 2 CPU/1 h. Maximum two site pilots concurrently; no shared writers. After jobs terminal, read-only result review, then static final verification.
- Five additional opportunities total: one reviewed narrow preflight correction/rerun and four initially shared unchanged-scope infrastructure retries. The user's diagnosed-too-strict floating-point tolerance exception may reallocate one of those four, never create a sixth opportunity. Absolute ceiling ten submissions. No automatic application, scientific, data, schema, dependency, OOM, timeout or performance retry. Material fixes require fresh user approval and re-review, except that specific conditional tolerance correction.
- Outside-sandbox `sbatch`, scoped `squeue`/`sacct`, and bounded `scancel` are authorized for exact Iter005 scope. Cancel only for duplicate submission, identity/scope drift, target leakage, collision, published-release write risk, storage threat, or explicit user direction; reconcile terminal state afterward.
- Before submission, independently review scientific equivalence, numerical geometry, development-only check placement, leakage, source identities, test quality, resource limits and canonical/submitted equality. After substantive jobs terminal, independently review results before final verification.
- Authorized implementation: new `model_ELM/mcmc_three_stage_sampler_geometry.py`, focused edits to `mcmc_three_stage_sampler.py`, required coordinate interface in `mcmc_three_stage_posterior.py`, necessary `mcmc_three_stage_initialization.py`, `mcmc_three_stage_diagnostics.py`, `mcmc_three_stage_artifacts.py`; focused `tests/test_mcmc_three_stage_iter005_*.py`; canonical `development/mcmc_optimization/slurm/iter005/`; this report, `summaries/iter005/`, fixed-schema registry, cumulative summary and handoff. Other paths require fresh authority. Missing pytest and PPE1-specific loader cleanup remain deferred.
- Closeout: at most one scoped local no-push commit with expected parent `205cd410f612bd7c751728d722c599b09aca6b86`, proposed subject `Complete MCMC optimization Iter005 prior-unit sampler pilot`. Four-record validation, then planning-only Iter006 proposal. No push, merge or Iter006 initialization.

## Work-unit ledger

Prepared canonical package `development/mcmc_optimization/slurm/iter005/` and byte-identical
submitted copies under the approved external root. Configuration SHA-256
`4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021`;
execution checksum-manifest SHA-256
`8a38d9c3f6efa241f0a113f4f498e71d0902cca1494a2437550cc7a531196837`;
execution manifest SHA-256
`cd6213004c10edbe97e0587e0c8ab8cb1ddcd0a89bf3c836bc779d98975a13f4`.
Static checksum, JSON, shell syntax, submitted-copy, and `git diff --check` checks pass.
Independent reviewer `iter005_package_review` initially blocked source-identity, strict
reference, snapshot metadata, numerical classification, test, and accounting gaps. All were
corrected and re-reviewed; final result `pass`. Review artifact SHA-256
`64d25e57130f9665dd904eb81aba4ff061a7ccd16ff5a7286fc2137710bc067f`.
This read-only review does not substitute for compute-node tests. Personal `xdisk -c query`
shows no allocation and the project-identity query returns `403 Forbidden`; the user confirmed
on `2026-11-27` that `/xdisk/chopinsong` will remain valid and directed continuation. The
storage-expiration gate is therefore cleared for this Iter005 window. Puma account limits and
12 TiB free capacity were rechecked before submission.

| Work unit | State | Evidence |
| --- | --- | --- |
| Initialization | complete | approval and this locked report |
| Preparation | complete | canonical/submitted package and hashes above |
| Independent package review | pass | `reviews/package_review.json` at hash above |
| Compute-node preflight | pass | job `24838315` terminal `FAILED 1:0`; corrected job `24838440` terminal `COMPLETED 0:0`, 41/41 tests and development-only bounds gate passed |
| Density, reuse and restart | fatal mapping failure | job `24838469` terminal `FAILED 1:0` at validation tolerance; reviewed retry `24838627` terminal `FAILED 1:0` at ABBY proposal mapping during restart |
| ABBY/JERC pilots | not submitted | fatal density/restart gate blocks pilots |
| Diagnostics and result review | pass for failed decision | job `24838734` terminal `COMPLETED 0:0`; independent result review confirms fatal mapping and no pilot |
| Final verification and closeout | complete | five terminal submissions, failure-compatible four-record validation; local no-push closeout |

Preflight submission command, to be executed from the approved external run root after exact
package verification:

```bash
sbatch --parsable --export=ALL,ITER005_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot/submitted/iter005_config.json,ITER005_CONFIG_SHA=4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021,ITER005_VERIFY_SHA=3bd19938d142a84b11fa6a812fd0b18f982dfb7c1e18fc689f5866d6cc22c12c,ITER005_MANIFEST_SHA=8a38d9c3f6efa241f0a113f4f498e71d0902cca1494a2437550cc7a531196837,ITER005_EXECUTION_MANIFEST_SHA=cd6213004c10edbe97e0587e0c8ab8cb1ddcd0a89bf3c836bc779d98975a13f4 ./submitted/preflight_iter005.slurm
```

Submitted as job `24838315`; immutable submission manifest SHA-256
`4dd72fce5c1091141eab2c01a17d49e85a170625e4e0d9e48a08be496e1ee3c9`.
Monitor only `squeue --job=24838315 -r` while active; reconcile terminal state with
`sacct --jobs=24838315 --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,AllocTRES`.

Preflight job `24838315` reached terminal `FAILED 1:0` after `00:01:01`, `2` CPUs,
`10G` allocation, `1206284K` batch MaxRSS, and `00:28.629` TotalCPU. Its
`41` tests had zero skips, zero assertion failures, and two errors in the new
Iter005 test fixture. The boundary test wrongly expected `CoordinateSaturation`
for an exact physical PPE1 endpoint, which `Prior18.support_mask` correctly
rejects as outside the open prior support. The scalar/batch density fixture
implemented `evaluate_batch` but omitted `evaluate`, causing `AttributeError`
only on its scalar test path. These errors did not diagnose a geometry, posterior,
or tolerance failure. Logs remain immutable; terminal accounting is
`manifests/terminal_001_24838315.psv` SHA-256
`df8226b67982492fead1683bbb45ef43f0843a01ffa3ae570c66f892b6afa00d`.
The original submitted package, checksum manifest, and package review were
archived under `archive/attempt_001/` before correction. The approved one
narrow preflight correction/rerun opportunity is allocated to a test-only fix:
the exact physical endpoint now expects outside-support `ValueError`, and the
fixture's scalar `evaluate` delegates to its batch implementation. No science,
implementation, numerical tolerance, or resource value changed. Corrected test
SHA-256 `318a092d1ba2958774eed0b6affca3df3f246fcf3ddae659a009121d98c8bc2e`,
checksum manifest `355fce52e0fab597dcbc4386d733abb4d7b2870aac03b6979adc4b6c03aad1ce`,
and execution manifest `ea99f5070a3e1937e50f3efa2f5c5b4f8733ace8b7b88ee7d0dffff733eaf61c`.
Independent read-only re-review passed; refreshed review artifact
`reviews/package_review_002.json` SHA-256
`bc84539a89be24813d2b6649172be738c09e2757116682ee016f890a1eae59ec`.
Static execution identity validation passed on the corrected package. The one
approved narrow preflight rerun was submitted as job `24838440`, sequence 2/10;
immutable submission manifest `manifests/submission_002_24838440.json` SHA-256
`5389dc55ecf0d17fa5afc79b6cbeb75c6573c2f3619c1a4d2fa5ef2978579869`.
No dependent job was submitted before the corrected preflight completed; its
terminal state was reconciled with job-scoped `sacct`.

Corrected preflight job `24838440` completed `0:0` in `00:00:55` on 2 CPUs,
10G allocation, batch MaxRSS `1122820K`, with 41/41 tests, zero skips, and
`MCMC_ITER005_PREFLIGHT_PASS`. The development-only prior/snapshot bounds
artifact was written; preflight result SHA-256
`4b8ef1c963875cb2c985b720edfbbe73002b9481c5463d12a06e4a6ab3237bd9`,
terminal accounting SHA-256
`d8f34bd48ff237a107fabb0113837c0e25e321b6741b9a1cdfc29a56afd4113f`.
The density, walker-reuse and restart validation job `24838469` was then
submitted as sequence 3/10 with unchanged reviewed package identity;
submission manifest SHA-256
`0e252a17d0822262278086e48055da55b01d96d01b9ef5428c71b26de1b06263`.
No site pilot has been submitted pending its result.

Density/restart job `24838469` reached terminal `FAILED 1:0` after `00:00:39`
on 2 CPUs, 10G allocation, batch MaxRSS `1947552K`. It passed package identity,
strict midpoint references, physical target identity, all ABBY old walker hashes,
support, physical-to-unit replay, and stored-versus-current physical likelihood
components. It then failed at ABBY walker 63 when the absolute `1e-9` threshold
compared the full `log p_theta + log Jacobian` sum with the independent
likelihood-plus-unit-prior expression. The original check used likelihoods
evaluated at the archived physical walkers while `log p_z` used walkers after
physical-to-unit-to-logit round trip. Those are distinct floating-point
physical vectors, whose component parity was explicitly allowed the separately
predeclared `rtol=1e-7`, `atol=1e-8`; the absolute `1e-9` total-density threshold
was too strict for that cross-vector comparison. The independent read-only
reviewer confirmed the validation mismatch and found no evidence of a geometry
or posterior implementation error. The original log lacks a numerical
residual, so corrected validation must prove tight same-vector cancellation
before any pilot.
Terminal accounting SHA-256 `edea25c30e4faa01e56be9aa3d484839276055996f10d616cfb93f4cd66b13af`.
The submitted package and review were archived under `archive/attempt_003/`;
no partial site outputs were written. The original source, tolerance and
failure log remain available for review.

The user-authorized conditional numerical-tolerance correction is allocated
one of the four shared opportunities, leaving at most three unchanged-scope
infrastructure retries and a ten-submission absolute ceiling. Only the
Iter005 validation driver changed: it now requires prior-plus-full-Jacobian
versus unit-logit terms within absolute `1e-9` at the same reconstructed
physical vector; strict `rtol=1e-12`, `atol=1e-10` physical component sum and
same-vector normalized density; exact full-Jacobian sampler identity within
absolute `1e-9`; and the already locked scalar/batch `rtol=1e-7`, `atol=1e-8`
only for archived versus reconstructed physical-vector totals. It records
maximum absolute residuals and worst walker for each comparison. No geometry,
sampler, physical posterior, scientific input, configuration tolerance, or
resource value changed. Corrected driver SHA-256
`bae58c799624743dedaae66c9d1ed4ad571176f2c06dde9e76ac10867bc5a46f`,
execution checksum manifest
`2b414218813fbdbc93957f321222e3b144058595ca226a61dc40f5dd386abddc`,
execution manifest `7507fa14751efac64389655be9aea14c1cc8b4f218fea5ce2d8cfa0b2d5ea0e9`.
Independent read-only re-review passed; diagnosis artifact
`reviews/tolerance_diagnosis_003.json` SHA-256
`0b8a432bdaae19ee04789126f49e49932c470568b120c9fc92e06363e5ad5418`,
refreshed package review `reviews/package_review_004.json` SHA-256
`afd4ea6736f7b3b841995a019fae1ea57387c1d4c942a06c108682659b833522`.
No site pilot has been submitted.

The corrected density/restart job `24838627` was submitted as sequence 4/10
after exact static source/submitted verification; submission manifest SHA-256
`7b9f06c3181a2dafe19c1be14a51b4b9622d8b8442ffdd85d3fb669328cc788d`.
It consumes the single user-authorized tolerance-correction opportunity. The
strict decomposed same-vector guards and exact restart remain fatal gates.

Corrected density/restart job `24838627` reached terminal `FAILED 1:0` after
`00:01:29` on 2 CPUs, 10G allocation, batch MaxRSS `1948984K`. ABBY's 64
validated physical walkers passed source/target/support, physical component
parity and the corrected decomposed density checks. Maximum absolute residuals
were `5.684341886080802e-14` for prior-plus-full-Jacobian cancellation,
`1.8189894035458565e-12` for same-vector normalized density, zero for
physical component sum and full-Jacobian sampler identity, and
`1.2009706551907584e-05` for archived-versus-reconstructed density at walker
63 (within its predeclared scalar/batch tolerance). The independent density
identity is therefore supported for ABBY's initial walkers.

During the ABBY 16-step restart fixture, a proposal triggered
`RuntimeError: prior inverse unit mapping escaped PPE1 marginal bounds` in
`sampler_to_physical` before the run could finish. The partial append-only
ledger contains 128 proposal rows through step 2, including 28 distinct
numerical-saturation reason-code-5 rows and 41 accepted moves; the failing
proposal was not ledgered. This is a fatal mapping/restart failure under locked
gates, regardless of whether the specific escape is a floating-point boundary
classification defect. No JERC validation or site pilot ran, and no move
configuration was tuned. The partial ABBY backend and ledger remain external
and must not be resumed or interpreted as a validated chain. Terminal
accounting SHA-256 `ac4d1fef615d470cc4a33fe00bf0350f13f0819a9eee990f3c2c58f57f57eb5f`,
ABBY numerical residual artifact SHA-256
`eeef256479142ac5f0f4ad3ff0b4ebfa0dd9e9eec7187dcbcd39c201470ed7fc`,
partial proposal ledger SHA-256
`b1d746892b85626682005eb61af56d59d7c07bdce6f54c0800d747f626431fd9`.
At the restart failure, `du -sb` measured 1,899,831 bytes including directory
metadata. The diagnostics job's file-only tally was 1,857,767 bytes; later
final-accounting `du -sb` measured 1,908,394 bytes and the post-review check
measured 1,915,734 bytes. All are below the 2 GiB cap and reflect distinct
measurement times/methods; the accounting artifact retains its own timestamped
measurement.
Independent read-only result classification confirms `iter005_validation_failed`
and that neither site pilot may proceed. The planned diagnostics aggregation
job `24838734` was submitted as sequence 5/10; submission manifest SHA-256
`cd61c49604682487538c473606d3ee44515fb26effc5f9f6c2b393ecb15e1ee4`.
Final independent result review must bind its diagnostics hash before static
four-record verification. The material geometry correction needed for another restart
requires a separately approved runtime contract; the user's tolerance-only
exception does not authorize it.

## Proposed Iter006 direction (planning only)

**Boundary-Safe Prior-Unit Mapping and Restart Feasibility.** Use the preserved
Iter005 partial ABBY ledger/backend, exact frozen source identity, and failed
traceback to reproduce the extreme-coordinate marginal escape on a compute
node. Measure unit coordinate, physical value, parameter index, distance in
ULPs from the bound, and whether `Prior18.inverse_unit` arithmetic caused the
escape. Distinguish one-ULP numerical saturation from a larger mapping defect.
Do not clip, reflect, change the physical prior, or absorb unexpected failures.

Propose a narrowly scoped geometry classification correction only if numerical
evidence supports it, with targeted boundary tests for log-uniform and linear
parameters and conditional C:N. Require the unchanged strict analytical
Jacobian, posterior density, physical support, release compatibility, and
source-provenance gates. Revalidate deterministic 16-step uninterrupted versus
8+8 restart for both ABBY and JERC with fresh coordinate, identity and backend
artifacts; never resume the Iter005 partial backend. Quantify extreme-coordinate
saturation by move and walker. The 28 saturation events in just 128 ABBY
restart proposals suggest the original `<=8/site` pilot threshold may be
infeasible with the unchanged move mixture, but this partial fixture is not a
pilot measurement. A new separately approved scope must predeclare its own
diagnostic limits and decide whether move geometry needs a later iteration.
No 128-step pilot or production chain is proposed automatically.

Provisional compute plan: one 2-CPU, 10-GB, 1-hour boundary diagnostic;
one 2-CPU, 10-GB, 1-hour numerical/restart validation after review; one 2-CPU,
10-GB, 1-hour evidence aggregation job. Fresh external run root, source hashes,
independent reviews, terminal accounting and storage limit would be locked in
an Iter006 kickoff package and require explicit approval. This proposal grants
no Iter006 initialization, execution, retry, scheduler, push, or merge authority.

## Final decision and closeout identities

- Decision `iter005_validation_failed`: Gate 1 plan/source/release identity passed; Gate 2
  development-only bounds/schema passed; Gate 3 initial-walker mapping passed but extreme proposal
  mapping failed fatally; Gate 4 ABBY initial-walker Jacobian/density passed, JERC not evaluated;
  Gate 5 preflight tests passed 41/41; Gate 6 ABBY physical walker reuse passed, JERC not reached;
  Gate 7 exact restart failed; Gate 8 ABBY/JERC pilots not submitted; Gate 9 all actual jobs and
  storage reconciled; Gate 10 independent reviews passed for truthful failure closeout.
- Diagnostics artifact SHA-256 `d1d1ec631f4d4620f4345e30ac0515010c5f2f7e40f71541211f4cec68e0479e`;
  final accounting SHA-256 `80cb77f33c54106521278b851c620ea34c8ab837763fd403fb3da1062762b891`;
  independent result review SHA-256 `06009889d7667c19f606bb34eb7877df86ed6fcf4275f1a1953c5a4f1fe0fcd6`;
  four-record validation `ITER005_FOUR_RECORD_VALIDATE_PASS` artifact SHA-256
  `8412993640011ecbab5f0990a271eddc56856c44bd0e09606c08b21b5666f9c6`.
- Final execution package identities: config `4cefd55f3aa8f6f348d22463740b00a882c9ca470f0d235b797932848d7c9021`,
  checksum manifest `2b414218813fbdbc93957f321222e3b144058595ca226a61dc40f5dd386abddc`,
  execution manifest `7507fa14751efac64389655be9aea14c1cc8b4f218fea5ce2d8cfa0b2d5ea0e9`.
- External evidence root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter005_prior_unit_sampler_pilot`.
  It retains immutable failure logs, prior package snapshots, proposals, partial backend,
  numerical residuals, Slurm submissions/accounting, and both independent reviews.
- All five actual submissions are terminal; active or unaccounted jobs: zero. One preflight
  correction and one conditional tolerance correction were used; no infrastructure retry or
  site pilot was submitted. No posterior convergence, calibrated parameter inference, or
  acceptable pilot movement is claimed. Missing `pytest` and PPE1-specific-loader cleanup
  remain deferred.
- Four-record closeout uses the approved single local no-push commit with expected parent
  `205cd410f612bd7c751728d722c599b09aca6b86`, subject
  `Complete MCMC optimization Iter005 prior-unit sampler pilot`. No push or merge.
