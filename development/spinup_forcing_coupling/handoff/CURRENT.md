# Spinup-Forcing Coupling - Current Handoff

Iteration ID `iter017`; Status `completed`; Work type `implementation`; Objective `consolidate and end-to-end regress the coupled optimization pipeline before the separate nine-site operational campaign`; Bounded scope `1 preflight; 4 initialization/rebuild jobs; 12 optimization leaves; 4 reporting jobs; 1 handoff validation`; Overall acceptance result `pass`; Decision `technical_pipeline_regression_passed; all four reports insufficient_retained; no posterior promotion; Iter018 planning proposal recorded; kickoff approval pending`.

## Closed State

- Last closed iteration: `iter017`
- Phase: `closed`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression`
- Site profile: `development/hpc/puma.md`
- Closed at: `2026-08-20T22:48:21-07:00`

## Validated Evidence

- Preflight `23608785`, all four initialization/rebuild paths, all 12 optimization leaves, all four independent reports, and final handoff `23610344` are terminal `COMPLETED 0:0`.
- The final validator `validate_iter017_handoff.py` emitted `ITER017_HANDOFF_PASS paths=4`.
- ABBY daily/0.50, JERC hourly/0.75, joint daily/0.50, and joint hourly/0.75 each retain the required standardized report outputs but have `insufficient_retained` status with zero Tier-A seeds. This prevents posterior promotion and is the expected result for the short regression.
- Production provenance: source lock `70506cc0221a147b945fa5fc3a03ed767d69d6dd`; source manifest `f2d9ea2d51cdc9180e357172e4bdfcf5cacb9fc3cc695d0f113528a02a490756`; dependency manifest `a636037c452618d4588e3de3a758ef922c6ce4dd43e950ad5d51ef441f7ecefe`.

## Next Action

No job is active. The complete Iter018 planning-only proposal below must be approved as one
consolidated kickoff package before any new implementation, directory creation, scheduler
submission, monitoring, cancellation, or commit.

<!-- ITER018_PLAN_BEGIN -->
## Proposed Iter018 plan — final nine-site operational coupled-optimization release

### Objective, basis, and boundary

- Sequential ID and work type: `iter018`; `implementation`.
- Objective: execute the finalized coupled three-stage optimization pipeline separately at all
  nine supported NEON sites, publish site-local operational MAP-candidate products and a
  cross-site evidence package, then close the spinup-forcing coupling-development line with a
  merge-readiness assessment.
- Evidence basis: Iter017 closed with a technical pipeline-regression pass; the reusable
  interfaces are source-locked in `70506cc`, documented at repository root, and have supported
  manual examples in `examples/optimization/`. Its 2,000-step paths were intentionally
  non-promoting and do not substitute for this operational run. Iter015/016 demonstrate that
  64-walker, 8,000-step leaves fit the established Puma 16-CPU/4-hour envelope.
- Hypothesis: the finalized, site-local pipeline can reproducibly materialize immutable pools,
  complete nine independent 8,000-step leaves per site, and provide a complete, auditable
  operational evidence package without changing the scientific target or reusable pipeline.
- Work is single-site only. It is neither a joint calibration nor a new performance-improvement,
  retraining, feature-selection, likelihood, prior, or sampler-design experiment.

### Locked scientific and campaign scope

All campaigns use `SR`, one site and one case per YAML, the coupled released forcing artifact and
`drop21_corr080` spinup artifact, the ordered physical-parameter schema, fitted site-local
`sigma_SR`, transformed coordinates, and the standard 80% `DEMove` / 20% `DESnookerMove`
mixture. Preparation must lock the exact artifact, case-pickle, observation, environment, source,
and manifest hashes; no mutable ledger or prior output is an input.

| Sites | Likelihood resolution | `DEMove` scale | Initialization | Leaf settings |
| --- | --- | --- | --- | --- |
| ABBY, SOAP, YELL, WREF | daily | `0.50` | fresh `hybrid_high_l_maximin`, `high_l_quantile=0.90`, pool size 640, search seed 17017 | 64 walkers, 8,000 steps, 2,000-step checkpoints, 16 processes |
| JERC, OSBS, RMNP, TALL, TEAK | hourly | `0.75` | fresh `hybrid_high_l_maximin`, `high_l_quantile=0.90`, pool size 640, search seed 17017 | 64 walkers, 8,000 steps, 2,000-step checkpoints, 16 processes |

- Every site uses the same nine MCMC seeds, owned only by its copied Slurm array:
  `9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017`.
- The reporting contract remains `tier_a_acceptance_range: [0.20, 0.50]` and
  `copy_leaf_products: true`. Tier-A status is descriptive and never changes an integrity
  result. A retained seed is an operational MAP candidate, not a validated posterior,
  cross-site ranking, or universal recommendation.
- Exclusions: joint/site-weighted runs; candidate-pool reuse or rebuild from older ledgers;
  TIM starts; more/other seeds; any new optimization or MCMC API; artifact/environment repair;
  promotion of a posterior; push, pull request, merge, or deletion of user-owned outputs.

### Bounded work units, layout, and expected evidence

The nominal scope is 102 compute work units: one bounded preflight; nine fresh
initializations; nine nine-leaf arrays (81 leaves); nine independent site reports; one
cross-site closeout analysis; and one final handoff validator. This is 21 scheduler submissions
when each array is counted once. The hard execution cap is 205 units only because the retry
rules below permit at most one unchanged scheduler/resource retry for a failed nominal unit plus
one preflight-only correction/rerun; it is not authority to expand scope.

- Proposed external root, subject to kickoff approval:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site/`.
  It may contain only `preflight/`, one site directory per campaign with
  `initialization/`, `optimization/seed_<seed>/`, and `reports/`, `aggregate/`, and `handoff/`.
  `/xdisk` remains temporary and unbacked; raw chains, plots, NetCDF, logs, and other large
  products remain outside Git.
- Each materialized site package must include its campaign YAML, copied submitted scripts,
  submission configuration, package/source/dependency manifests, locked observations/case/artifact
  identities, frozen pool hash, stage receipts, and terminal accounting ledger.
- Every leaf must retain its standard chain/checkpoint/production metadata and finite/bounded
  products. Every site report must retain per-seed diagnostics and likelihood/collocation/residual
  tables, physical corner products, combined CSV/TXT MAP parameter rows, and exactly one
  `clm_params_seed_*.nc` export per seed.
- The aggregate package must include a machine-readable 9-site/81-leaf completeness table and
  a human-readable comparison with configuration, Tier-A status, acceptance and sampler-health
  context, and R2, KGE, RMSE, and correlation diagnostics. Selection/retention indicators must
  be visibly separated from descriptive skill metrics.

### Proposed Puma runtime contract

- Confirm Puma `chopinsong` / `standard` and `development/hpc/puma.md` at kickoff; use
  `OLMT_puma` only inside Slurm compute jobs. No repository Python runs on a login node.
- Proposed resource envelope: preflight 4 CPUs/30 minutes; each initialization 8 CPUs/4 hours;
  each optimization leaf 16 CPUs/4 hours; each site report and aggregate analysis 4 CPUs/2
  hours; final validator 2 CPUs/30 minutes. Array concurrency is `%2`, with at most two active
  arrays, for a hard cap of four concurrent leaves (64 CPUs and derived 320 GB).
- Materialize, byte-check, and independently review all canonical and submitted packages before
  preflight. Preflight validates all nine YAML/configuration and dependency identities plus
  bounded compute-node interface/target construction checks; it must not begin substantive
  initialization, MCMC, data generation, or evaluation.
- After a passing preflight, submit and immediately identity-check an initialization before the
  next independent submission. Submit a site's array only after its immutable pool and receipt
  pass. Submit its report only after all nine leaves have terminal accounting and pass leaf
  completeness. Submit aggregate analysis only after all nine reports pass; submit handoff
  validation only after aggregate evidence is complete.
- An independent agent performs read-only review before preflight and after every authorized
  correction. The primary agent is the sole writer and scheduler operator.

### Gates, decision rule, failure handling, and closeout

- Integrity acceptance requires: all work units terminally accounted; exact source/dependency and
  submitted-copy identity; valid immutable pools; 81 complete finite/bounded leaf products;
  nine standard reports with nine exact CLM NetCDF exports each; aggregate evidence; and a final
  validator that agrees across `iterations/iter018.md`, `ITERATION_SUMMARY.md`, `registry.csv`,
  `handoff/CURRENT.md`, and current artifacts. Tier-A counts, sampler diagnostics, predictive
  skill, and cross-site differences are reported evidence, not integrity vetoes.
- Overall decision: `operational_release_ready` only when every integrity gate passes. The
  report separately assigns each site `all_tier_a`, `partial_tier_a`, or
  `insufficient_retained`; no site with `insufficient_retained` receives a promoted posterior or
  representative recommendation. Any integrity failure produces a classified non-ready
  conclusion rather than post-result gate revision.
- Permit one minimal preflight-only code correction and rerun, with repeated static checks and
  review. Permit one unchanged scheduler/resource retry per recorded job or individual array
  leaf. Any application, code, interface, schema, data, dependency, numerical, or gate failure
  outside that preflight exception preserves diagnostics and requires a revised consolidated
  package and fresh user approval before a change or retry.
- `scancel` is limited to recorded Iter018 IDs and only for a demonstrated universal
  pre-execution defect or a user-directed emergency. Query/transport failure leaves state
  unknown and authorizes neither retry nor completion claim.
- Closeout will produce a comprehensive Iter001--Iter018 development narrative; released
  architecture/interface and example inventory; site and cross-site operational evidence;
  reproducibility identities; limitations and storage-retention risk; and a merge-readiness
  declaration. It ends this development line with an explicit terminal declaration rather than
  an unspecified next iteration. No merge, push, or PR is in scope.
- Proposed repository branch: one scoped preparation/source-lock commit before preflight for
  Iter018 adapters, configurations, validators, and records only, then at most one scoped
  closeout commit after final validation. Reusable pipeline changes require separate fresh
  approval.

### Fresh authorization boundary

This is a complete planning-only proposal. It does not authorize initialization, directory
creation, repository Python, compute-node work, scheduler submission, monitoring, cancellation,
commits, or merge activity. Before any such action, obtain one explicit approval of the full
runtime contract, including the output root, lifecycle/closeout authority, two proposed local
commits, and outside-sandbox authority for `sbatch`, job-scoped `squeue`, `scontrol show job`,
`sacct`, `seff`, `job-history`, and `job-limits`, plus the bounded `scancel` conditions above.
<!-- ITER018_PLAN_END -->
