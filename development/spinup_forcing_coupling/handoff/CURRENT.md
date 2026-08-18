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
- Last updated: `2026-08-17T17:50:00-07:00`

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

Iter013 is recorded as a planning-only Stage A initialization-cloud comparison at ABBY and JERC.
It is `not_initialized`. Do not scaffold, submit, or run jobs until a consolidated kickoff package
is approved under `WORKFLOW.md`. Copy the plan below unchanged into that kickoff package.

<!-- ITER013_PLAN_BEGIN -->
## Proposed Iter013 plan - Stage A initialization-cloud comparison

- Sequential ID: `iter013`
- Status: `not_initialized`
- Work type: `validation`
- Objective: compare Iter009 TIM high-posterior start clouds with Iter012 production
  candidate-pool start clouds at ABBY and JERC, and test whether the Iter012 640/64 sets are
  high-posterior rank sets or diversity-dominated sets.
- Evidence basis: Iter012 JERC mixing collapsed relative to Iter011 `hourly/0.75` while MAP
  skill matched; Iter012 hypothesized initialization geometry rather than likelihood form.
  Iter011/009 TIM starts are transferred top-decile Iter008 chain states. Iter012 starts come
  from an independent Sobol plus L-BFGS-B search with marginal-quartile representation and
  maximin fill. ABBY is included as the geometry control because the same pool recipe did not
  split Iter012 ABBY seeds.
- Hypothesis: the TIM walker cloud is a compact high-posterior neighborhood, while the Iter012
  pool and walkers span near-full prior width; the Iter012 640/64 sets are not the top-k
  posterior states from the same search.

### Fixed targets and dependencies

- Re-lock the Iter012 Package v2 Revision1 site targets and the Iter009 TIM high-likelihood
  artifacts. Do not rebuild pools, replay MCMC, or change priors, bounds, transforms, surrogates,
  observations, or likelihood resolution.
- ABBY comparison uses the Iter012 daily target
  (`target_sha256=bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd`).
- JERC comparison uses the Iter012 hourly target
  (`target_sha256=26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196`).
- Forcing artifact SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`.
- Spinup `drop21_corr080` SHA-256
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`.
- Iter012 pools: ABBY `982350b16e17202acb4f2b82ab40c26e24c31dff159bb68dafbd6d8cc69a2d19`;
  JERC `32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96`.
- Iter012 candidate ledgers: ABBY
  `ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b`; JERC
  `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d`.
- TIM high-likelihood pools: ABBY
  `b19cbe90bdc746a4c2bf577fc2dc4877a32d89ee6bf77d76b6058c3f9085ad4a` (2,212 states, top-decile
  cutoff `-81162.4853383585`); JERC
  `fcd909188789ab97b222773fc21f2a60e401a730f16e95edeee1e7aac49140e8` (1,208 states, top-decile
  cutoff `-52719.034473135165`).
- TIM high-seed bundles 9009/9010/9011: ABBY
  `37f51011638e93ef1420d092d7f97bbd8e6bfa24342d205fcc09b9d5a9d8716a`,
  `49a32268e72a183414e2ba684717b1b7675c84f4ebf12b2ffd23df850c9f69cb`,
  `8c30198df99da7225f9c3235866c3020fef8d1e7a9349494149ddcfa11d14e0c`; JERC
  `394902f2c2378a6793196f226c7cf136872a2631012f559ba857c989c47bd8fe`,
  `86fa8a3a732be080454bb451ab025cf604c1c8c0a98ffbdce26ed2b46d3870d6`,
  `fa19ed47a533f540e88992c1eac6346f46478192ed85b1132222ac08599f063e`.
- Iter012 walker starts are the `selected_physical_states` in Revision1
  `production/{abby,jerc}/seed_{9009,9010,9011}/selection_ledger.json`.
- Physical parameter order remains
  `k_l1, k_l2, k_l3, k_s1, k_s2, k_s3, k_s4, k_frag, rf_l1s1, rf_l2s2, rf_l3s3, rf_s1s2, rf_s2s3, rf_s3s4, sigma_SR`.
- Use Iter012 site bounds, including site-specific `sigma_SR` upper bounds. Trust assumption:
  TIM physical states are in that same order and strictly in bounds; hash mismatch or order
  mismatch is an integrity failure, not a scientific result.

### Clouds, coordinates, and comparison methods

- Per site, compare four primary clouds: TIM high-L pool; TIM walker starts (per seed and the
  192-row union); Iter012 640-member pool; Iter012 walker starts (per seed and union).
- Add two Iter012-ledger counterfactual clouds: the unique states with the top 640 stored
  physical log posteriors, and the top 64 stored physical log posteriors.
- All geometry uses prior-normalized coordinates
  `(theta - pmin) / (pmax - pmin)` with the Iter012 site bounds. Do not compare stored TIM log
  posterior values with stored Iter012 log posterior values. TIM stored logp is Iter008 hourly
  chain posterior; Iter012 ABBY logp is daily.
- Geometry metrics, all in prior-normalized units: per-parameter mean, standard deviation, range,
  and 5–95 width; per-parameter 1D Wasserstein between each TIM cloud and each Iter012 cloud;
  centroid Euclidean distance; mean pairwise distance; mean nearest-neighbor distance;
  overlap fraction at Euclidean radius `0.05` from each TIM walker to the nearest Iter012 walker
  and to the nearest Iter012 pool member, and the reverse fractions.
- On JERC, highlight `k_s1`–`k_s4` versus `k_l1` and `rf_l3s3`. On ABBY, highlight `sigma_SR`.
- Common-target logp: reconstruct each Iter012 site target and re-evaluate TIM pool and TIM
  walker physical states under that target. Compare those values with stored Iter012 pool and
  walker physical log posteriors. Report 5/50/95 percentiles for each cloud and the median
  difference TIM walkers minus Iter012 walkers. Do not re-evaluate the full Iter012 search
  ledger except as needed to confirm stored pool/ledger logp identity.
- Rank-versus-diversity counterfactual: exact-row intersection of the Iter012 640 with the
  ledger top 640, and of each seed's 64 walkers with the ledger top 64. Report intersection
  counts, intersection fractions, and the max/mean normalized spread of actual versus top-k
  sets.
- Plots: one per-parameter overlay figure per site (violin or histogram) for the four primary
  clouds. No PCA scatter, no corner plot, and no observed-versus-predicted plot. Tables and JSON
  are the primary evidence.

### Classification and decision rule

Classify each site independently after integrity passes. Geometry classes are mutually exclusive
in this order:

1. `coincide` if the maximum per-parameter 1D Wasserstein between the TIM walker union and the
   Iter012 walker union is `<= 0.05` and at least 80% of TIM walkers have an Iter012 walker
   within Euclidean radius `0.05`.
2. `tim_nested_in_iter012_pool` if not `coincide`, at least 80% of TIM walkers have an Iter012
   pool member within radius `0.05`, and Iter012 walker mean pairwise distance is at least twice
   the TIM walker mean pairwise distance.
3. `separated` if fewer than 20% of TIM walkers have an Iter012 walker within radius `0.05` and
   the maximum per-parameter 1D Wasserstein between those walker unions is `> 0.05`.
4. `inconclusive_geometry` otherwise.

Separately classify Iter012 selection:

- `rank_dominated` if `|actual 640 ∩ top 640| / 640 >= 0.80`.
- `diversity_dominated` if that fraction is `< 0.50`.
- `mixed_rank_and_diversity` otherwise.

Also report the same intersection fractions for each seed's 64 walkers versus the ledger top 64.
These classes are descriptive. They do not promote a posterior, change the initializer, or
authorize MCMC.

### Bounded scope, work units, and exclusions

- Stage A only. No MCMC, no new candidate search, no pool regeneration, no TIM production replay,
  no DE-scale change, no likelihood or error-model change, no joint ABBY+JERC target, no
  initializer code change, and no automatic follow-up experiment.
- Proposed scheduler work: one compute-node preflight; one ABBY analysis leaf; one JERC analysis
  leaf; one aggregate/handoff validation: 4 nominal tasks.
- Preflight verifies artifact paths, hashes, parameter order, bounds, TIM-bundle membership in
  the TIM pool, Iter012 selection-ledger identity, and target fingerprints. It may run one
  midpoint posterior fixture per site. It must not re-evaluate TIM clouds or write scientific
  classifications.
- Each analysis leaf writes that site's geometry JSON, common-target logp JSON, top-k
  counterfactual JSON, overlay figure, and site classification.
- Aggregate concatenates both sites, writes the comparison table and report, and runs the
  four-record handoff validator after durable records exist.
- Exclude Iter009 uniform bundles, Iter012 Package v1 stretch-move chains, and any transferred
  chain states except the locked TIM high-L pools and high-seed bundles above.

### Proposed site, resources, retry, and stop boundary

- Proposed site: UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition
  `standard`; environment `OLMT_puma`.
- Proposed output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter013/`
  with `preflight/`, `analysis/{abby,jerc}/`, and `aggregate/`. Large arrays remain outside Git;
  `/xdisk` is temporary and unbacked.
- Proposed resources: preflight 4 CPUs / 20 GB / 30 min; each analysis leaf 16 CPUs / 80 GB / 4 h;
  aggregate/handoff 4 CPUs / 20 GB / 1 h.
- Proposed retry ceiling: one minimal preflight correction/rerun; one unchanged
  scheduler/resource retry per analysis or aggregate leaf; at most 8 scheduler tasks.
  Application, code, schema, dependency, numerical, target, hash, or scope failures stop for a
  revised package.
- Cancellation only for recorded Iter013 job IDs, and only for a proven universal pre-execution
  defect that would make remaining Iter013 work fail.
- Stop after both site analyses, aggregate/handoff validation, complete terminal accounting,
  classified failures, and durable-record agreement. Do not start MCMC or Stage B.

### Expected evidence, artifacts, and record updates

- External: hashed analysis JSON, overlay figures, `aggregate_result.json`, `accounting.csv`,
  and `ITER013_REPORT.md` under the approved output root, with compact copies in
  `development/spinup_forcing_coupling/summaries/iter013/`.
- Repository: `iterations/iter013.md`, canonical scripts under `slurm/iter013/`, registry row,
  `ITERATION_SUMMARY.md` append, and rebuilt `handoff/CURRENT.md` at closeout.
- Required completeness: both sites classified; all locked hashes verified; common-target TIM
  logp finite for every TIM pool and walker row; top-k counterfactuals present; no PCA plot.

### Fresh consolidated kickoff-approval boundary

This planning-only proposal does not authorize initialization, scaffolding, repository Python,
Slurm, retry, cancellation, or a closeout commit. It becomes executable only when included in
an approved consolidated kickoff package under `WORKFLOW.md`.
<!-- ITER013_PLAN_END -->

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

Start the next session by reading this file, `WORKFLOW.md`, the Iter012 record/report, the
Iter013 planning-only proposal in this file, and `development/hpc/puma.md`. Reconcile any claimed
live state against scheduler accounting. Iter013 remains `not_initialized` until one consolidated
kickoff package is approved.
