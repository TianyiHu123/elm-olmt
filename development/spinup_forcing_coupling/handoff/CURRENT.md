# Spinup-Forcing Coupling - Current Handoff

## Live state

- Active iteration: `iter011`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`
- Bounded scope: `ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains`
- Overall acceptance result: `pass`
- Decision: `ABBY preferred_configuration_supported: daily_0.75; JERC inconclusive_metric_tradeoff: no selected configuration`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-14T19:08:12-07:00`

## Authority and stop boundary

The user response `the kickoff package and outside sandbox authority is approved` at
`2026-08-13T20:15:40-07:00` approves the complete Iter011 package copied below. It authorizes the
primary agent to prepare, obtain independent read-only review, create the approved external layout,
submit and monitor the locked preflight and staged campaign, apply the recorded bounded retry and
cancellation rules, evaluate, update durable records, validate the handoff, and make one local
closeout commit. It also authorizes outside-sandbox `sbatch`, job-scoped `squeue`, `scontrol show
job`, `sacct`, `seff`, `job-history`, and `job-limits`, plus `scancel` only for recorded Iter011 IDs
under the contract's cancellation conditions. No scope, code, dependency, numerical, or gate change
outside this contract is authorized. That authority is exhausted and does not authorize any
Iter012 action.

## Best evidence

- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter011`
- Dependencies: Iter002 forcing, Iter012 `drop21_corr080`, matching-site/seed Iter009 TIM bundles,
  and ABBY/JERC observations/cases were identity-verified by the completed preflight and v5 aggregate.
- Terminal evidence: preflight `23561067`, all 36 campaign leaves, and aggregate `23565465` completed
  `0:0`; aggregate emitted `AGGREGATE_PASS leaves=36` and `AGGREGATE_PASS`.

## Risks and limitations

- Aggregate v1--v4 application/launcher failures are classified in `iterations/iter011.md`; their
  material and v3/v4 partial outputs are preserved. The bounded v5 correction was independently
  reviewed and passed before submission.
- ABBY's preferred `daily_0.75` is only future-proposal evidence. JERC's hourly configurations have
  an unresolved material trade-off; `hourly_0.75` is a user-selected future production choice, not
  an Iter011-supported unique preference.
- `/xdisk` products are temporary and unbacked.

## Next action

Closed. Preserve the complete Iter011 package and its failed-attempt provenance. The identical
planning-only Iter012 proposal below is ready for a fresh consolidated kickoff package. Iter012 is
not initialized, and no implementation or scheduler action is authorized.

<!-- ITER012_PLAN_BEGIN -->
## Proposed Iter012 plan - standard initialization and fixed production MCMC

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

- Closeout identity: Iteration ID `iter011`; Status `completed`; Work type `implementation`;
  Objective `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`;
  Bounded scope `ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains`;
  Overall acceptance result `pass`; Decision `ABBY preferred_configuration_supported daily_0.75; JERC inconclusive_metric_tradeoff with no selected configuration`.
- Iteration record: `development/spinup_forcing_coupling/iterations/iter011.md`
- Comprehensive report: `development/spinup_forcing_coupling/summaries/iter011/ITER011_REPORT.md`
- Decisions: `development/spinup_forcing_coupling/summaries/iter011/abby_decision.json` and
  `development/spinup_forcing_coupling/summaries/iter011/jerc_decision.json`
- Accounting/evidence: aggregate `23565465`; external result
  `spinup_forcing_coupling_iter011_aggregate/result/aggregate_result.json`
- Validator: `development/spinup_forcing_coupling/slurm/iter011/validate_iter011_handoff.py`

Start the next session by reading this file, `WORKFLOW.md`, the Iter011 record/report, and
`development/hpc/puma.md`. Reconcile any claimed live state against scheduler accounting before
requesting a new consolidated package.
