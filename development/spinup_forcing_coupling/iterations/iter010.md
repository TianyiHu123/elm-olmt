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

## Closeout checklist

- [x] Terminal accounting complete; no active or unaccounted Iter010 jobs
- [x] Integrity, topology, conditional-skip, and limitations evidence classified
- [x] Comprehensive report and required figure captions complete
- [x] `ITERATION_SUMMARY.md`, `registry.csv`, and `handoff/CURRENT.md` aligned
- [x] Exactly one complete next proposal recorded with no execution authority
- [x] Corrective pre-commit validator passed
- [x] Authorized follow-up commit selected for external post-commit verification
