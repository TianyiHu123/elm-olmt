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
- Last updated: `2026-08-14T15:05:00-07:00`

## Authority and stop boundary

The user response `the kickoff package and outside sandbox authority is approved` at
`2026-08-13T20:15:40-07:00` approves the complete Iter011 package copied below. It authorizes the
primary agent to prepare, obtain independent read-only review, create the approved external layout,
submit and monitor the locked preflight and staged campaign, apply the recorded bounded retry and
cancellation rules, evaluate, update durable records, validate the handoff, and make one local
closeout commit. It also authorizes outside-sandbox `sbatch`, job-scoped `squeue`, `scontrol show
job`, `sacct`, `seff`, `job-history`, and `job-limits`, plus `scancel` only for recorded Iter011 IDs
under the contract's cancellation conditions. No scope, code, dependency, numerical, or gate change
outside this contract is authorized.

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
  an unresolved material trade-off and no selected configuration.
- `/xdisk` products are temporary and unbacked.

## Next action

Closed. Preserve the complete Iter011 package and its failed-attempt provenance. A future ABBY
site-specific production proposal or a JERC diagnostic must be defined and explicitly approved as a
new iteration; no scheduler action is currently authorized or required.

<!-- ITER011_PLAN_BEGIN -->
## Approved Iter011 plan and runtime contract

- Sequential ID: `iter011`
- Status: `planned`
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
- The approved package authorizes only this Iter011 lifecycle. A later proposal still requires a
  fresh complete consolidated kickoff package and explicit approval.
<!-- ITER011_PLAN_END -->

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
