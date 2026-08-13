# Spinup-Forcing Coupling - Current Handoff

## Live state

- Active iteration: `iter010`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `TIM terminal-partition topology diagnosis`
- Bounded scope: `Six immutable TIM chains; ABBY/JERC; seeds 9009-9011; terminal/rolling topology diagnostics; conditional prediction skip`
- Overall acceptance result: `pass`
- Decision: `ABBY and JERC two_basin_declined; forced terminal screen declined as evidence for two physical basins; replace the screen, reassess TIM/JERC, and route to ABBY proposal-scale Experiment 5`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-13`

## Authority and stop boundary

The Iter010 consolidated package is exhausted. Its bounded lifecycle reached terminal accounting,
evaluation, aggregation, durable records, handoff validation, and closeout. The user's 2026-08-13
instruction separately authorized correction of the incomplete closeout and one follow-up commit.
No current authority exists to initialize Iter011, run repository Python, create external campaign
directories, submit or cancel jobs, retry work, or make another closeout commit.

## Best evidence

- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter010`
- Dependencies: six immutable Iter009 TIM chain bundles; fixed Iter002 forcing, Iter012
  `drop21_corr080`, ABBY/JERC observations and cases, physical bounds/order, and posterior target.
- Accounting: preflight `23554607`, topology `23554935`, conditional prediction `23555136`, and
  finalize `23555187` are all terminal `COMPLETED 0:0`; no Iter010 job is active or unaccounted.
- Integrity: source identity/hash/schema/shape/finiteness and posterior provenance passed. The
  compact package contains 32 PNG figures, six metric archives, decisions/tables, source manifest,
  validated conditional skip, accounting, and comprehensive report.
- Topology: ABBY and JERC are separately `two_basin_declined`; scalar, multivariate, and temporal
  requirements oppose in all three seeds at both sites, while corresponding occupied locations
  reproduce across seeds.
- Secondary interpretation: JERC is
  `convergence_supported_under_revised_iter009_diagnostics` as a screening conclusion; ABBY is
  `convergence_not_established_abby_acceptance_and_saturation`; no general TIM convergence claim.
- Conditional branch: `skipped`, zero evaluations; equifinality
  `not_applicable_no_supported_basins`.

## Risks and limitations

- Declining the forced partition does not prove global unimodality, connectedness, stationarity,
  walker exchange, or independent posterior samples.
- PCA and corner projections can miss nonlinear high-dimensional separation; interacting-walker
  assignment counts are diagnostic rather than independent evidence.
- ABBY's low acceptance and transformed-coordinate saturation remain unresolved.
- `/xdisk` products are temporary and unbacked.

## Next action

`Iter011 is not_initialized; its complete planning-only ABBY target-equivalent DE proposal-scale pilot is recorded in iterations/iter010.md and CURRENT.md, and execution requires a fresh consolidated kickoff package with explicit approval.`

<!-- ITER011_PLAN_BEGIN -->
## Planning-only Iter011 proposal

- Sequential ID: `iter011`
- Status: `not_initialized`
- Work type: `implementation`
- Objective: `ABBY target-equivalent DE proposal-scale pilot`
- Evidence basis: Iter010 declined ABBY's forced terminal partition, but all three ABBY TIM chains
  retain mean acceptance near 0.146--0.148 and marked transformed-coordinate saturation. The next
  falsifiable question is whether overly aggressive differential-evolution proposals cause the
  rejection/saturation while the physical posterior target is held exactly fixed.
- Hypothesis: reducing only the DEMove scale will lower transformed-bound rejection and saturation,
  move mean acceptance toward 0.20--0.50, and preserve the occupied physical posterior. Persistent
  low acceptance or materially shifted physical summaries would route instead to likelihood/model
  structure or a non-equivalent proposal defect.
- Dependencies: the three immutable Iter009 TIM/ABBY chains and initialization bundles; the same
  Iter002 forcing surrogate, Iter012 `drop21_corr080` spinup surrogate, ABBY observations/case,
  15-parameter physical bounds and order, IID Gaussian likelihood, prior, transform, Jacobian,
  surrogate identities, software environment, and Puma profile. Preparation must re-hash all.
- Bounded matrix: ABBY only; DEMove scale multipliers `0.50`, `0.75`, `1.00`, and `1.25` relative
  to the current default; seeds `11011`, `11012`, and `11013`; 12 independent 64-walker x
  8,000-step chains. Preserve the 80% DEMove / 20% DESnookerMove mixture and every target-defining
  component. Use the frozen high-likelihood initialization strategy; do not reuse posterior draws
  as inferential output.
- Exclusions: no JERC rerun, transformed-coordinate redesign, likelihood/prior/bounds/Jacobian or
  surrogate changes, adaptive scale selection, continuation of Iter009 chains, arm promotion,
  calibrated-skill claim, or automatic production extension.
- Integrity gates: exact source and target-equivalence hashes; finite complete raw/HDF chains;
  exact shapes and seed/arm identities; synchronized metadata/checkpoints; terminal Slurm
  accounting; complete per-chain and cross-seed summaries; and exact durable-record agreement.
- Diagnostic evidence, not scientific hard gates: mean and walker-level acceptance, proposal and
  transformed-bound rejection causes, transformed saturation, tau/steps-per-tau, split R-hat,
  cross-seed prior-width-normalized distances, physical posterior summaries, and residual/sigma
  behavior. Thinning cannot create convergence.
- Decision rule: route to `proposal_scale_supported` only if at least one reduced-scale arm improves
  acceptance and saturation consistently across all three seeds without a material target-
  equivalence or physical-posterior shift; route to `proposal_scale_not_supported` if it does not;
  otherwise `inconclusive`. Any later production choice requires a new approved package.
- Proposed outputs: one preflight package, 12 immutable leaf bundles, one aggregate/decision
  package, chain and cross-seed diagnostic figures, terminal accounting, comprehensive report,
  cumulative summary, registry row, rebuilt CURRENT, and closeout validator evidence under the
  shared coupling output root and `summaries/iter011`.
- Proposed Puma resources: preflight 2 CPUs/10 GB/30 min; each unthrottled leaf 16 CPUs/80 GB/4 h;
  validation 4 CPUs/20 GB/2 h. Nominal submitted tasks: 14; proposed hard cap: 18 including at
  most one unchanged scheduler/resource retry per substantive unit and one minimal preflight
  correction. Application/scientific failures stop for review; cancellation is limited to
  recorded Iter011 IDs for a proven universal pre-execution defect.
- Monitoring and closeout: primary agent is sole writer/operator; use `sbatch --parsable`, immediate
  identity checks, job-scoped `squeue`/`sacct`/`seff`, terminal accounting, aggregation, records,
  handoff validation, and the commit/no-commit branch explicitly selected by a future kickoff.
- Authority boundary: this proposal creates no directories, files, jobs, retries, cancellations,
  commits, or execution authority. Iter011 requires one fresh consolidated kickoff package and
  explicit user approval.
<!-- ITER011_PLAN_END -->

## Closeout references

- Iteration record: `development/spinup_forcing_coupling/iterations/iter010.md`
- Comprehensive report: `development/spinup_forcing_coupling/summaries/iter010/ITER010_REPORT.md`
- Decision: `development/spinup_forcing_coupling/summaries/iter010/topology_decision.json`
- Accounting: `development/spinup_forcing_coupling/summaries/iter010/iter010_accounting.csv`
- Validator: `development/spinup_forcing_coupling/slurm/iter010/validate_iter010_handoff.sh`

Start the next session by reading this file, `WORKFLOW.md`, the Iter010 record/report, and
`development/hpc/puma.md`. Reconcile any claimed live state against scheduler accounting before
requesting a new consolidated package.
