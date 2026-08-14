# iter010 - TIM terminal-partition topology diagnosis

## Closeout identity

- Iteration ID: `iter010`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `TIM terminal-partition topology diagnosis`
- Bounded scope: `Six immutable TIM chains; ABBY/JERC; seeds 9009-9011; terminal/rolling topology diagnostics; conditional prediction skip`
- Overall acceptance result: `pass`
- Decision: `ABBY and JERC two_basin_declined; forced terminal screen declined as evidence for two physical basins; replace the screen, reassess TIM/JERC, and route to ABBY proposal-scale Experiment 5`
- Started: `2026-08-12T19:06:17-07:00`
- Closed: `2026-08-12T20:05:00-07:00`

## Finalized scope and authority

The approved objective was to determine whether the forced terminal two-means partitions in the
six Iter009 TIM chains represent reproducible physical basins, a connected ridge, a broad/unimodal
screen artifact, or inconclusive topology. ABBY and JERC were evaluated separately across seeds
9009--9011. The scope included terminal and rolling-window diagnostics, five figures per chain,
one three-seed synthesis per site, and representative-state prediction only for a site classified
`two_basin_supported`. It excluded new MCMC, chain continuation, posterior changes, proposal
tuning, and a convergence-length study.

The exact user response `approved the full package` authorized bounded Puma preparation,
submission, monitoring, accounting, evaluation, durable records, and one local closeout commit.
That package is exhausted. On 2026-08-13 the user separately authorized this corrective closeout
and follow-up commit. Neither authority carries forward to Iter011.

## Dependencies and output contract

- Source lock: six Iter009 TIM `raw_chain.npz` archives plus matching HDF, metadata, checkpoint,
  and selection-ledger evidence in `iter010_source_manifest.json`.
- Fixed scientific target: Iter002 forcing, Iter012 `drop21_corr080`, ABBY/JERC observations,
  cases, physical bounds, parameter order, and posterior convention inherited unchanged.
- Site profile: `development/hpc/puma.md`; environment: `OLMT_puma`.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter010`

## Terminal accounting

| Work unit | Job ID | Terminal state | Evidence |
| --- | ---: | --- | --- |
| preflight | 23554607 | `COMPLETED 0:0` | `PREFLIGHT_PASS`; 13 s |
| topology | 23554935 | `COMPLETED 0:0` | `TOPOLOGY_PASS`; 1:12 |
| conditional prediction | 23555136 | `COMPLETED 0:0` | `PREDICTION_SKIPPED`; 8 s |
| finalize | 23555187 | `COMPLETED 0:0` | `FINALIZE_PASS`; 9 s |

All four jobs were rechecked in authoritative Slurm accounting on 2026-08-13. No Iter010 job is
active or unaccounted, and no retry or cancellation was used.

## Evidence, decision, and limitations

Preflight verified source identities, hashes, schemas, shapes, finiteness, site/seed fields,
parameter order, bounds, and physical-log-posterior convention. The terminal package contains 32
PNG figures, six metric archives, the topology decision/table, source manifest, conditional skip,
accounting, and comprehensive report.

ABBY and JERC are both `two_basin_declined`: scalar, multivariate, and temporal requirements oppose
in every seed, while corresponding occupied locations reproduce across seeds. The forced screen is
therefore declined as evidence for two physical basins. JERC receives the secondary screening label
`convergence_supported_under_revised_iter009_diagnostics`; ABBY receives
`convergence_not_established_abby_acceptance_and_saturation`. No general TIM convergence claim is
made. Conditional prediction was correctly skipped with zero evaluations, and equifinality is
`not_applicable_no_supported_basins`.

This result does not prove global unimodality, connectedness, stationarity, or independent posterior
draws. PCA/corner projections can miss nonlinear separation; interacting walkers are not
independent samples; ABBY's low acceptance and transformed-coordinate saturation remain unresolved;
and `/xdisk` products are temporary and unbacked.

## Independent review and closeout verification

Independent read-only review corrected source/provenance enforcement, aggregation initialization,
label ordering, and required trajectory/rolling evidence before execution. The final submitted
copies matched reviewed repository sources. The comprehensive report now supplies the required
per-figure construction, reading guide, observed result, implication, and limitation.

The corrective closeout validator is
`development/spinup_forcing_coupling/slurm/iter010/validate_iter010_handoff.sh`. It verifies exact
cross-record identity, scope, gate, decision, dependencies, paths, artifacts, accounting, report
content, next action, and the identical next proposal. The follow-up commit must have parent
`ed42024d513f879d7dd88c998944b80f79b02ebe`, subject `Correct Iter010 closeout records`, exactly the
controlled paths enforced by the validator, and a clean post-commit tree. Its own hash is
intentionally not embedded in the commit it validates.

## Next state

`Iter011 is not_initialized; its complete planning-only two-site TIM DE-scale and likelihood-resolution pilot is recorded in iterations/iter010.md and CURRENT.md, and execution requires a fresh consolidated kickoff package with explicit approval.`

<!-- ITER011_PLAN_BEGIN -->
## Planning-only Iter011 proposal

- Sequential ID: `iter011`
- Status: `not_initialized`
- Work type: `implementation`
- Objective: `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`
- Evidence basis: Iter010 declined the forced terminal partition at both sites. JERC retains the
  healthy remaining TIM screens, while ABBY retains mean acceptance near 0.146--0.148 and marked
  transformed-coordinate saturation. Iter008 also showed residual lag-1 correlation above 0.99
  and ABBY `sigma_SR` saturation, motivating a bounded daily-information-reduction comparison.
- Hypotheses: reduced DEMove scale may improve ABBY proposal movement and transformed saturation;
  JERC may benefit, remain neutral, or be harmed; and a complete-day mean likelihood may reduce
  redundant hourly information. Conclusions must remain site-specific. A preferred configuration
  requires material improvement without a material regression in another locked metric.

### Dependencies and unchanged TIM contract

- Re-lock the Iter002 forcing surrogate, Iter012 `drop21_corr080` spinup surrogate, ABBY/JERC cases
  and NEON v4 observations, 14 physical parameters plus fitted `sigma_SR`, bounds, priors, order,
  transformed coordinates, analytic Jacobian, software environment, repository source, and Puma
  profile. Preserve the 80% DEMove / 20% DESnookerMove mixture and IID Gaussian form.
- Reuse the exact Iter009 TIM site/seed initialization bundles: seed 9009 uses its seed-9009 bundle,
  9010 uses seed-9010, and 9011 uses seed-9011. The same bundle is reused across all six
  scale/resolution configurations for that site and seed. These states are non-inferential
  initialization evidence, not posterior draws.

### Fixed matrix and chain contract

- Sites: ABBY and JERC, analyzed separately.
- Likelihood resolutions: `hourly` and `daily`.
- DEMove scale multipliers: `0.50`, `0.75`, and `1.00`; the multiplier changes only DEMove, while
  DESnookerMove remains unchanged. Record the resolved numerical scale and prove that `1.00`
  matches default `DEMove()` behavior.
- Seeds: `9009`, `9010`, and `9011`.
- Total: 36 independent 64-walker x 8,000-step chains, checkpointed at 2,000-step intervals, with
  incremental HDF persistence and immutable sampler- and physical-coordinate raw-chain packages.

### Likelihood-only daily aggregation

- Preserve hourly observation loading, exact hourly collocation, hourly coupled-surrogate
  prediction, baseline output, plots, skill calculations, and residual diagnostics.
- Precompute a hashed daily index map from collocated model-calendar timestamps. Retain only dates
  with exactly 24 valid paired hourly SR/error entries and use the arithmetic mean of the same 24
  indices for observation and prediction.
- Each retained daily mean contributes one IID Gaussian likelihood term using fitted `sigma_SR`
  directly, with no `sqrt(24)` adjustment. Preserve the existing `sigma_SR` prior and upper bound.
- Record included/excluded dates, hourly/daily counts, aggregation rules, and map identity. Hourly
  is the backward-compatible default. Target equivalence applies across DE scales within a
  resolution; hourly and daily are intentionally different targets.

### Preflight and staged submission

- Preflight must verify dependency/bundle identity, complete-day behavior on a deterministic
  fixture, manual daily-likelihood equality, exact fixed-vector equivalence of the old and explicit
  hourly paths, `1.00` DEMove equivalence, finite evaluation of every reused bundle under both
  targets, and HDF/checkpoint/raw-chain wiring.
- Submit the six hourly/`1.00` leaves first. Release the remaining five unthrottled six-leaf arrays
  only when all six baseline leaves are `COMPLETED 0:0` with campaign-pass markers, their
  site/seed/bundle/resolution/scale identities are correct, and preflight hourly equivalence passed.
  No intermediate scientific comparison or detailed artifact audit is required.
- After that checkpoint submit hourly/`0.50`, hourly/`0.75`, daily/`0.50`, daily/`0.75`, and
  daily/`1.00` as five unthrottled six-leaf arrays, subject to Puma scheduling.

### Slim metric package and immutable material thresholds

- Mean acceptance: `0.20--0.50` is healthy; an absolute change of at least 0.03 toward or away from
  that interval is material; values already within the interval are equivalent for ranking.
- Worst transformed-coordinate saturation fraction: at most 0.05 is healthy; an absolute change
  of at least 0.10 is material; configurations both at or below 0.05 are equivalent.
- Minimum steps per tau: below 20 is insufficient, 20--50 is pilot-adequate, and at least 50 is
  strong; a tier crossing or at least 20% change within a tier is material. Tau must first satisfy
  the existing at-most-20% stability screen, which is interpretability evidence, not another rank.
- Maximum prior-width-normalized cross-seed Wasserstein distance: values at or below 0.05 are
  equivalent; crossing 0.05 is material.
- Absolute hourly posterior-predictive residual correlation at lag 24 hours: an absolute change of
  at least 0.05 is material; lower is better, including for daily-likelihood chains.
- `sigma_SR` upper-edge occupancy: define the edge as the top 5% of its unchanged prior; at most
  0.10 is healthy, at least 0.50 is saturated, and an absolute change of at least 0.20 is material.
- ESS, split R-hat, minimum walker acceptance, RMSE, R2, KGE, best likelihood, MAP, and the retired
  terminal two-means screen do not select a configuration.

### Site-specific decision rule

- Use paired matching-seed comparisons. Require all three seeds to point in the same direction,
  the median paired difference to reach the material threshold, and no materially opposite seed.
- A site supports a configuration only if it passes integrity/interpretability requirements,
  materially improves at least one core metric, materially worsens none, and is the unique
  non-dominated configuration among the six tested combinations.
- Allowed independent outcomes for each site are `preferred_configuration_supported`,
  `default_configuration_retained`, `inconclusive_metric_tradeoff`,
  `inconclusive_seed_instability`, `inconclusive_no_unique_preference`, and
  `no_eligible_configuration`. Neither site may veto, rescue, or determine the other.

### Plots, gates, and exclusions

- Retain the standard per-chain hourly SR prediction time series, one-dimensional physical PDFs,
  physical-coordinate corner plot, parameter and physical-log-posterior traces, and walker
  acceptance overview. Daily-likelihood chains still show hourly predictions and residuals.
  Use steps 4001--8000 with deterministic display-only subsampling and fixed within-site axes/bins.
- Hard gates are exact identity/provenance, complete finite HDF/raw chains, physical bounds/order,
  transform/Jacobian/target convention, synchronized checkpoints/metadata, daily-map provenance,
  terminal accounting, complete metric/plot/decision packages, and durable-record agreement.
  Sampler quality and site decisions are diagnostic outcomes, not iteration-integrity failures.
- Exclude new initialization search, production inference, automatic extension, transform redesign,
  boundary-aware replacement proposals, prior/bound/Jacobian/observation/case/surrogate/site-window
  changes, AR(1)/robust/weighted likelihoods, joint or pooled site inference, adaptive tuning,
  fit-based selection, and automatic follow-up execution.

### Puma resources, retries, outputs, and stop

- Puma `standard` / `chopinsong` / `OLMT_puma`: preflight 2 CPUs/10 GB/30 min; each chain leaf
  16 CPUs/80 GB/4 h/16 workers; aggregate/report/validation 4 CPUs/20 GB/2 h.
- Submission shape: preflight, six six-leaf arrays, and aggregate/validation = 38 nominal scheduler
  tasks across eight submissions. Stage A is at most 96 CPUs/480 GB; Stage B is at most
  480 CPUs/2,400 GB, subject to Puma scheduling.
- Retry rule: one minimal preflight-only correction/rerun; at most six campaign-leaf recoveries
  total and at most one per leaf; one unchanged aggregate/validation scheduler/resource retry;
  hard cap 46 tasks. A leaf recovery requires verified compatible HDF/checkpoint state and cannot
  change scientific or sampler terms. Application/code/schema/dependency/numerical/scientific/
  threshold/scope failures stop for fresh approval.
- Cancellation is limited to recorded Iter011 IDs: a proven universal pre-execution defect may
  cancel all affected pending leaves, while a configuration-specific defect may cancel only its
  array. Cancellation grants no correction or resubmission authority.
- External root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with
  one preflight directory, six configuration parents containing six immutable leaves each, and one
  aggregate/validation directory. Large raw/HDF/prediction/full-plot products remain outside Git;
  `/xdisk` is temporary and unbacked.
- Compact `summaries/iter011` evidence must include a comprehensive report, six-configuration table
  per site, separate ABBY/JERC machine-readable decisions, selected comparison figures, aggregation
  provenance, and terminal accounting, plus cumulative summary, registry, handoff, and validator.
- Stop only after terminal accounting, integrity evaluation, independent site decisions, complete
  reports/plots, durable-record agreement, final validation, and a valid handoff.

### Next-production and authority boundary

- A later site-specific production proposal may use a supported configuration only after the full
  reproducible non-inferential initialization search, frozen fresh bundles, and independent burn-in
  described in the Iter009 report. Inconclusive sites require narrower follow-up, not forced choice.
- This proposal creates no directory, file, job, retry, cancellation, commit, initialization, or
  execution authority. Iter011 requires one fresh consolidated kickoff package and explicit user
  approval before any runtime or iteration-specific work.
<!-- ITER011_PLAN_END -->

## Closeout checklist

- [x] Terminal accounting complete; no active or unaccounted Iter010 jobs
- [x] Integrity, topology, conditional-skip, and limitations evidence classified
- [x] Comprehensive report and required figure captions complete
- [x] `ITERATION_SUMMARY.md`, `registry.csv`, and `handoff/CURRENT.md` aligned
- [x] Exactly one complete next proposal recorded with no execution authority
- [x] Corrective pre-commit validator passed
- [x] Authorized follow-up commit selected for external post-commit verification
