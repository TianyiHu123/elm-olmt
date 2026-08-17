# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`

## Live state

- Active iteration: `iter012`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`
- Bounded scope: `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`
- Overall acceptance result: `pass`
- Decision: `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`
- Active job IDs: none; handoff validation `23575977` completed `0:0` with
  `ITER012_HANDOFF_VALIDATE_PASS`; canonical evaluations ABBY/JERC `23575950`/`23575951` completed `0:0`
  with `fixed_length_inconclusive`; legacy-audit evaluations ABBY/JERC `23575952`/`23575953`
  completed `0:0` with `legacy_misconfigured_sampler`; production ABBY seeds 9009/9010/9011
  `23574707`/`23574706`/`23574708` and JERC seeds 9009/9010/9011
  `23574709`/`23574710`/`23574711`, all completed `0:0` with `FIXED_PRODUCTION_PASS`;
  pool validation `23574678` completed `0:0` with
  `POOL_VALIDATION_PASS`; Revision1 initialization ABBY `23574453` and JERC `23574454` completed
  `0:0` with `INITIALIZE_PASS`;
  Revision1 preflight `23574395` completed `0:0` with `PREFLIGHT_PASS`;
  Package v2 preflights `23574254` and `23574301` both terminal `OUT_OF_MEMORY 0:125`; Package v1 jobs
  `23570407--23570412` are reconciled `COMPLETED 0:0`
- Site profile: `development/hpc/puma.md`
- Canonical Package v2 root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2`
- Active Revision1 root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1`
- Legacy Package v1 root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012`
- Last updated: `2026-08-17T12:47:17-07:00`

## Authority and stop boundary

The original Package v1 authority remains historical provenance. On `2026-08-16`, the user confirmed
that this session is on UArizona Puma, selected the canonical/legacy and cleanup boundaries, and
responded `agreed. Are you ready to resume the iteration with the new package now?` after reviewing
the complete revised contract and record-amendment plan. This approves Package v2 preparation,
repository scripts/tests, the new external layout, locked Slurm submissions, job-scoped monitoring
and accounting, bounded retries and cancellation, evaluation, durable records, relocation of the
misplaced Package v1 logs, removal of superseded Iter012 Python adapters after external preservation,
and one local closeout commit. No push is authorized.

Package v2 has 16 nominal work units. After both approved 10 GB preflight attempts ended
`OUT_OF_MEMORY 0:125`, the user approved Revision1: exactly one 4 CPU/20 GB, 30-minute preflight
attempt with no retry, unchanged source behavior/dependencies/gates/downstream resources, and a
revised ceiling of 32 total scheduler tasks. Every downstream eligible leaf retains at most one
unchanged scheduler/resource retry. Any application, code, interface, schema, dependency,
numerical, target, scientific-gate, or scope failure stops for another revised package.

## Best evidence

- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012`
- Dependencies: Iter002 forcing, Iter012 `drop21_corr080`, ABBY/JERC case pickles, observations,
  source closure, and Puma environment were hash-verified by revised preflight `23569607`.
- Revised Iter012 preflight `23569607` completed `0:0` with `PREFLIGHT_PASS`; corrected generalized-package preflight `23569843` completed `0:0` with `PREFLIGHT_PASS`; ABBY retry
  `23569633` failed `1:0` after 35:07 on `r6u01n1` during JSON serialization of initialization
  metadata/report (`numpy.int64` not serializable). Its artifacts and prior manifests are preserved.
- The approved retry now uses reusable `model_ELM/coupling_pipeline.py` target and initialization
  interfaces with thin Iter012 adapters; the retry package is materialized under
  `initialization/abby_retry_23569633` and has passed independent review.
- ABBY retry `23569844` completed `FAILED 1:0` after `03:02:13` on `r7u05n1` with 16 CPUs/80 GB;
  terminal traceback reports `pool gate failed: 12106 robust strata exceed pool size 640`.
  `seff` reports 8.65 GB memory use, so this is an application/pool-gate failure, not a
  scheduler/resource failure. No initialization gate is met and no retry is authorized.
- Material design finding: Iter012 also introduced iteration-specific production/optimization
  surfaces even though reusable root-level optimization code already exists. This does not match
  the pipeline objective. Preserve the active ABBY job, audit the boundary after terminal
  accounting, and do not advance to pool validation or production until a revised package makes
  Iter012 files thin adapters and places reusable behavior in root-level engines/interfaces.
- Revised package approval: user approved the revised package on `2026-08-15T19:41:27-07:00`.
  The corrected pool contract uses marginal parameter-bin strata (`15` parameters x `4` bins,
  at most `60` required representatives) while retaining the `640` pool, exact-unique,
  full-rank, condition-number, and nonzero-spread gates. Reusable walker selection and fixed
  production execution are now in `model_ELM/coupling_pipeline.py`; Iter012 production is a
  configuration adapter. The preserved failed attempts remain immutable; the revised ABBY
  initialization will use `initialization/abby_retry_23569844_revised`.
- Historical Iter011 closeout remains provenance context only; it is not current Iter012 evidence.
- Package v1 terminal accounting is complete. Its six production leaves completed `0:0`, but raw
  metadata proves they used `move_configuration=stretch` instead of the locked `de_mixture`.
  Misplaced logs were hash-verified into their matching leaves, and superseded Python adapters were
  preserved under Package v1 provenance before repository removal.

## Risks and limitations

- Canonical Package v2 conclusions are `fixed_length_inconclusive` at both sites. JERC additionally
  shows severe cross-seed nonconvergence (max split R-hat `2.22410`, Wasserstein `0.54843`).
  Neither posterior is promoted.
- Package v1 is comparison-only `legacy_misconfigured_sampler` evidence (`stretch` instead of
  `de_mixture`).
- Production stderr accumulated large empirical-range warning streams; they did not change terminal
  status and remain a pipeline usability finding.
- `/xdisk` products are temporary and unbacked.

## Package v2 invariants

- Package v2 is canonical. Package v1 is retained and evaluated only as legacy corroboration.
- Scientific targets, dependencies, settings, seeds, fixed 32,000-step length, and diagnostic
  qualification gates are unchanged.
- Reusable behavior lives in `model_ELM/coupling_pipeline.py`; `initialize_pipeline.py` and
  `optimize_surrogate_forcing.py` are the public initialization and production entry points.
- Iteration-specific Python adapters are removed only after their executed copies and hashes are
  verified under the Package v1 external tree. Iteration-specific Slurm files remain thin,
  auditable orchestration and provenance.
- Slurm logs use explicit work-unit-local paths. The twelve Package v1 root logs are relocated to
  their matching external production leaves with before/after hash verification.
- ABBY and JERC remain separate invocations because they use different likelihood resolutions.
  The reusable interface may support multiple sites only under one common resolution.

## Next action

No next iteration is proposed. This workflow is intentionally stopped because both canonical
fixed-length outcomes are inconclusive. Start the next session by reading this file, `WORKFLOW.md`,
the Iter012 record/report, and `development/hpc/puma.md`. Any continuation requires a fresh planning
package and explicit approval.

<!-- ITER012_PLAN_BEGIN -->
## Historical Package v1 plan - superseded operationally by approved Package v2

- Sequential ID: `iter012`
- Status: `not_initialized`
- Work type: `implementation`
- Objective: implement a reusable initialization-to-production MCMC pipeline, then run fixed
  independent production inference for ABBY at `daily/0.75` and JERC at `hourly/0.75`.
- Evidence basis: Iter011 uniquely supported ABBY `daily/0.75`. JERC `hourly/0.75` is the user's
  selected production configuration from Iter011's two non-dominated hourly choices; Iter011 itself
  remained `inconclusive_metric_tradeoff` for JERC. Conclusions and posterior products remain
  site-specific.

### Fixed targets and dependencies

- Run two isolated targets only: ABBY and JERC. Do not run joint ABBY+JERC production.
- Re-lock the Iter002 forcing surrogate, Iter012 `drop21_corr080` spinup surrogate, matching cases
  and NEON v4 observations, physical parameter names/order, priors, bounds, transformations,
  analytic Jacobian, software environment, source, and Puma profile.
- Preserve 14 shared physical parameters plus fitted `sigma_SR`, transformed sampler coordinates,
  the physical-posterior target, and the 80% `DEMove` / 20% `DESnookerMove` mixture.
- ABBY uses the existing complete-day `daily` likelihood with fitted `sigma_SR` directly and no
  `sqrt(24)` adjustment. JERC uses the existing `hourly` likelihood. Both retain hourly
  collocation, predictions, and performance evaluation.
- Use DEMove multiplier `0.75` and production seeds `9009`, `9010`, and `9011` at both sites.

### Reusable target and pipeline interface

- Factor one shared target builder used by both initialization and production so cases,
  observations, collocation, daily maps, artifacts, parameter schema, fitted-error bounds, and
  target fingerprints cannot drift between stages.
- `--cases` is the sole authority for target membership. Observation/artifact mappings configure
  selected cases but cannot add cases. Canonicalize case order and reject missing, extra,
  duplicated, or mismatched case configuration.
- Support multiple selected cases in the reusable code: apply the prior once, sum every selected
  case likelihood once, produce one shared physical parameter vector, and fit one shared
  `sigma_<variable>` from all valid collocated observations across those cases.
- Permit only one global likelihood resolution per invocation. Reject mixed-resolution targets,
  manifests, pools, and continuations. Iter012 exercises only the two single-case targets above;
  deterministic fixtures test multi-case behavior.
- Implement a separate initialization command backed by a reusable initialization engine. Extend
  `optimize_surrogate_forcing.py` with a candidate-pool interface; do not make the optimizer
  generate or overwrite a pool implicitly.

### Candidate-pool initialization

- Generate one pool for ABBY's exact daily target and one for JERC's exact hourly target. Do not
  generate seed-specific initialization bundles.
- Exclude Iter008/Iter009/Iter011 chains and all transferred states. Generate candidates only from
  the new search under the current site target.
- Use `sobol_multistart_local_v1`: 8,192 scrambled Sobol states in normalized physical-prior
  coordinates, with deterministic expansion to 16,384, 32,768, and at most 65,536 states only when
  the pool gate remains unmet.
- Select 32 dispersed high-physical-posterior anchors and run bounded L-BFGS-B with at most 512
  posterior evaluations per anchor. Retain all evaluated states, not only endpoints, and rank only
  by physical log posterior.
- Filter finite, strictly in-bound, exact-unique states; preserve diversity strata without treating
  clusters as posterior modes. Require at least 640 selected states, nonzero spread in every
  parameter, full normalized-space rank, normalized condition number at most `1e6`, and
  representation of every robust retained stratum.
- Freeze `search_contract.json`, the complete candidate ledger and metadata, the high-posterior
  pool and manifest, diversity diagnostics, the initialization report, and all hashes before
  production. Pool failure stops production without threshold changes or fallback states.

### Pool-to-production checkpoint

- For each new production leaf, reconstruct the target and require exact equality of cases,
  resolution, case/observation/artifact/collocation identities, daily-map identity where applicable,
  parameter schema, priors, bounds, fitted-error configuration, source, pool manifest, and hashes.
- Derive pool-selection randomness separately from sampler randomness using the production seed and
  pool hash. Allocate across all retained robust strata, then select 64 unique states by seeded
  maximin selection.
- Verify strict bounds, finiteness, full normalized-space rank, condition number, and nonzero
  spread. Re-evaluate the 64 selected states under the production physical posterior and compare
  their stored likelihood/prior/posterior components before opening the HDF backend.
- Record the realized pool indices, selected physical states, derived selection seed, production
  seed, validation results, and hashes in each production leaf. A continuation must reproduce and
  verify this ledger and must never select walkers again.

### Fixed production runs

- Run six independent chains: ABBY/JERC x seeds `9009--9011`.
- Each chain uses 64 walkers x exactly 32,000 steps, 16 workers, incremental HDF persistence,
  checkpoints every 8,000 steps, and complete unthinned sampler- and physical-coordinate raw-chain
  packages.
- Do not perform diagnostic-driven extension, early stopping, configuration comparison, or
  follow-up sampling. A compatible scheduler/resource recovery may resume the same locked
  32,000-step target but cannot extend it.

### Concise final evaluation

- Evaluate once after all three seeds for a site finish. Use
  `discard=max(ceil(0.20*32000), ceil(5*tau_max))`; record unavailable or unstable tau rather than
  substituting a favorable discard.
- Report mean and walker acceptance, tau and its retrospective stability, post-burn steps per tau,
  rank-normalized split R-hat, bulk/tail ESS, prior-width-normalized cross-seed Wasserstein distance,
  transformed saturation, and physical prior-edge occupancy.
- Report hourly-prediction RMSE, R2, KGE, bias, fitted `sigma_SR`, and valid observation count for
  posterior-median parameters, MAP parameters as a descriptive point, and a bounded deterministic
  posterior-predictive sample. Metrics are descriptive and cannot override MCMC diagnostics.
- Retain compact parameter/physical-log-posterior traces, a physical-coordinate corner plot, and
  observed plus posterior-predicted hourly time series. Do not produce an observed-versus-predicted
  scatter plot, topology package, configuration ranking, or non-domination analysis.
- Label each site `diagnostically_qualified` only when tau is stable to 20%, every parameter has at
  least 50 post-burn tau, rank-normalized split R-hat is at most `1.05`, bulk and tail ESS are each
  at least 400, and maximum cross-seed normalized Wasserstein distance is at most `0.05`.
  Otherwise label it `fixed_length_inconclusive`; either outcome ends sampling.

### Integrity, work units, outputs, and exclusions

- Hard gates are exact identity/provenance, target and pool agreement, complete valid initialization
  artifacts, finite in-bound 32,000-step HDF/raw chains, synchronized checkpoints/metadata,
  terminal accounting, complete concise evaluation artifacts, and durable-record agreement.
  Scientific diagnostic outcomes are not iteration-integrity failures.
- Proposed scheduler work is one technical preflight, two initialization leaves, one pool
  validation, six production leaves, two site evaluations, and one aggregate/handoff validation:
  13 nominal tasks across six staged submissions.
- Proposed Puma resources are 2 CPUs/10 GB/30 min for preflight; 16 CPUs/80 GB/4 h per
  initialization leaf; 4 CPUs/20 GB/1 h for pool validation; 16 CPUs/80 GB/8 h per production
  leaf; and 4 CPUs/20 GB/2 h per evaluation or aggregate task.
- Proposed retry ceiling is one minimal preflight correction/rerun, one unchanged
  scheduler/resource retry per initialization leaf, one compatible scheduler/resource recovery per
  production leaf, one unchanged retry per evaluation leaf, and one unchanged aggregate retry: at
  most 25 scheduler tasks. Application/code/schema/dependency/numerical/target/pool/scientific/scope
  failures stop for a revised package.
- Proposed external layout is
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012/`
  with `preflight/`, `initialization/{abby,jerc}/`,
  `production/{abby,jerc}/seed_{9009,9010,9011}/`, `evaluation/{abby,jerc}/`, and `aggregate/`.
  Large pools, ledgers, HDF/raw chains, and full predictions remain outside Git; `/xdisk` is
  temporary and unbacked.
- Exclude joint production, mixed resolutions, annealed SMC, transferred initialization states,
  automatic extension, alternate likelihoods, site weighting, changes to scientific dependencies
  or targets, pooled conclusions, and automatic follow-up execution.
- This planning-only proposal becomes executable only through a fresh consolidated kickoff under
  `WORKFLOW.md`; Iter012 remains uninitialized.
<!-- ITER012_PLAN_END -->

## Closeout references

- Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`
- Iteration record: `development/spinup_forcing_coupling/iterations/iter012.md`
- Comprehensive report: `development/spinup_forcing_coupling/summaries/iter012/ITER012_REPORT.md`
- Aggregate: `development/spinup_forcing_coupling/summaries/iter012/aggregate_result.json`
- Accounting: `development/spinup_forcing_coupling/summaries/iter012/accounting.csv`
- Canonical evaluations: `summaries/iter012/abby_evaluation_result.json` and
  `summaries/iter012/jerc_evaluation_result.json`
- Validator: `development/spinup_forcing_coupling/slurm/iter012/validate_iter012_handoff.py`
- Validator job: `23575977` `COMPLETED 0:0`; output
  `ITER012_HANDOFF_VALIDATE_PASS abby=fixed_length_inconclusive jerc=fixed_length_inconclusive`
- Canonical output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1`

Start the next session by reading this file, `WORKFLOW.md`, the Iter012 record/report, and
`development/hpc/puma.md`. Reconcile any claimed live state against scheduler accounting before
requesting a new consolidated package.
