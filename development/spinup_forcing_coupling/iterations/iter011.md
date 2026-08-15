# iter011 - TIM DE-scale and likelihood-resolution pilot

## Status

- Iteration ID: `iter011`
- Work type: `implementation`
- Run slug prefix: `spinup_forcing_coupling_iter011_`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-13T20:15:40-07:00`
- Closed: `2026-08-14T15:05:00-07:00`

## Consolidated Kickoff Package and Runtime Contract

| Field | Approved value |
| --- | --- |
| User response and approval timestamp | `the kickoff package and outside sandbox authority is approved`; `2026-08-13T20:15:40-07:00` |
| Goal and stop boundary | Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC; stop only after terminal accounting, integrity evaluation, independent site decisions, complete evidence, durable-record agreement, final validation, and valid handoff. |
| HPC system and profile | UArizona Puma; `development/hpc/puma.md`; repository root confirmed on `junonia.hpc.arizona.edu`. |
| Output and storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; one preflight, six configuration parents with six leaves each, and one aggregate/validation directory; `/xdisk` is temporary and unbacked. Creation is authorized only for this layout. |
| Work units | One compute-node preflight; six unthrottled six-leaf arrays (36 chains total); one aggregate/validation work unit. Hourly/1.00 is Stage A; other arrays release only after its six valid campaign passes. |
| Locked target | Iter002 forcing, Iter012 `drop21_corr080`, ABBY/JERC cases and NEON v4 observations, 14 physical parameters plus fitted `sigma_SR`, bounds, priors, order, transforms, analytic Jacobian, IID Gaussian form, 80% DEMove/20% DESnookerMove, `OLMT_puma`, and repository source. |
| Matrix | Sites ABBY/JERC separately; resolutions hourly/daily; DEMove multipliers 0.50/0.75/1.00; seeds 9009/9010/9011; 64 walkers x 8,000 steps per chain with checkpoints every 2,000 steps and immutable sampler/physical raw-chain packages. |
| Initialization | Reuse matching site/seed Iter009 TIM bundles identically across all six configurations. Bundles are non-inferential initialization evidence, not posterior draws. |
| Daily target | Hash a complete-day map from collocated timestamps; retain exactly 24 valid paired hourly entries/date; mean the same indices for prediction and observation; use fitted `sigma_SR` directly with no sqrt(24) adjustment. |
| Hard gates | Provenance/identity, finite complete HDF/raw chains, physical bounds/order, transform/Jacobian/target convention, synchronized checkpoints/metadata, daily-map provenance, terminal accounting, complete metric/plot/decision package, and durable-record agreement. Sampler outcomes are diagnostic, not integrity failures. |
| Decision rule | Paired matching-seed comparisons; all three seeds same direction, material median difference, and no materially opposite seed. A site needs integrity/interpretability plus a unique non-dominated configuration that materially improves at least one core metric and worsens none. Sites decide independently. |
| Resources | Puma `standard` / `chopinsong` / `OLMT_puma`: preflight 2 CPUs/10 GB/30 min; each leaf 16 CPUs/80 GB/4 h/16 workers; aggregate/report/validation 4 CPUs/20 GB/2 h. Nominal total 38 scheduler tasks; hard cap 46. |
| Retry and cancellation | One minimal preflight correction/rerun; at most six leaf recoveries total and one/leaf from compatible state; one unchanged aggregate scheduler/resource retry. Application/code/schema/dependency/numerical/scientific/gate/scope failures stop. `scancel` only for recorded Iter011 IDs: universal pre-execution defects may cancel affected pending leaves, configuration defects only that array. |
| Lifecycle authority | Prepare, independent review, preflight, staged submission, monitoring, terminal accounting, evaluation, durable records, handoff validation, and one local closeout commit. |
| Outside-sandbox authority | `sbatch` for locked submissions and allowed resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only within the listed Iter011 scope. |

## Immutable Plan Details

The full approved planning proposal is retained verbatim in the active handoff between
`ITER011_PLAN_BEGIN` and `ITER011_PLAN_END`; it is the authoritative detailed contract for
acceptance metrics, thresholds, standard plots, exclusions, staging, and required artifacts. This
record and the handoff must remain consistent with it. Exclusions include new initialization search,
production inference, automatic extension, transform redesign, proposal replacement, changes to
priors/bounds/Jacobian/observations/cases/surrogates/windows, alternative likelihood families,
joint inference, adaptive tuning, fit-based selection, and automatic follow-up execution.

## Upstream Dependencies and Source Lock

| Dependency | Role | Lock status |
| --- | --- | --- |
| Iter002 forcing surrogate | coupled forcing prediction | pending hash/path/schema verification |
| Iter012 `drop21_corr080` | coupled spinup prediction | pending hash/path/schema verification |
| Iter009 TIM bundles | matching-site/seed initialization | pending six-bundle identity verification |
| ABBY/JERC cases and NEON v4 observations | fixed physical posterior target | pending hash/path/schema verification |
| `OLMT_puma` and repository source | execution environment/source | head `08cc56123daa2b6b7f83342166c28d1ae5ad5afd`; clean at initialization |

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| preparation/review | none | completed | v1-v3 source/manifests remain preserved; active v4 source manifest `954f78cce87e6fa73f414d05d92a4c9f8966e0a91ba0b8b3b255a2980a9f6f52` and dependency manifest `11e9380297500a88aa72300fe7279ae60d2121803a71919246d1a0537d922c77` passed independent read-only review. |
| preflight | `23561056` | failed | Terminal `FAILED 1:0`, 20 s, 2 CPUs/10 GB. Classified minimal launcher defect: absolute-path Python entrypoint lacked fixed repository `sys.path`; no scientific/model evaluation began. |
| preflight rerun | `23561067` | completed | `COMPLETED 0:0`, 6:15, 2 CPUs/10 GB; required fixture/equivalence/HDF checks passed and all 12 finite bundle evaluations (hourly/daily x ABBY/JERC x three seeds) emitted `FINITE_BUNDLE_PASS`, followed by `PREFLIGHT_PASS`. |
| hourly scale 1.00 | `23561095_[1-6]` (`23561105`--`23561109`, with leaf 6 accounting as `23561095`) | completed | All six leaves are `COMPLETED 0:0` and emit `CAMPAIGN_PASS`; terminal elapsed times 57:18, 1:07:48, 1:05:09, 1:17:17, 1:17:41, and 1:12:41. Every leaf has immutable raw-chain and hash artifacts. Stage A release condition passed. |
| hourly scale 0.50 | `23561349_[1-6]` | completed | All six leaves terminal `COMPLETED 0:0`; every raw/HDF/checkpoint package is complete and emits `CAMPAIGN_PASS`. |
| hourly scale 0.75 | `23561351_[1-6]` | completed | All six leaves terminal `COMPLETED 0:0`; every raw/HDF/checkpoint package is complete and emits `CAMPAIGN_PASS`. |
| daily scale 0.50 | `23561352_[1-6]` | completed | All six leaves terminal `COMPLETED 0:0`; every raw/HDF/checkpoint package is complete and emits `CAMPAIGN_PASS`. |
| daily scale 0.75 | `23561353_[1-6]` | completed | All six leaves terminal `COMPLETED 0:0`; every raw/HDF/checkpoint package is complete and emits `CAMPAIGN_PASS`. |
| daily scale 1.00 | `23561365_[1-6]` | completed | All six leaves terminal `COMPLETED 0:0`; every raw/HDF/checkpoint package is complete and emits `CAMPAIGN_PASS`. |
| aggregate/validation v1 | `23561580` | failed | Terminal `FAILED 126:0`, 9 s, before Python/validator execution. Classified materialization-config launcher defect: unquoted multi-path `CAMPAIGN_PARENTS` is executed while sourcing `submission_config.env`. All 36 campaign leaves remain valid; no scientific evaluation began. |
| aggregate/validation v2 | `23565245` | failed | Terminal `FAILED 1:0`, 18 s, 4 CPUs/20 GB; source/dependency manifests verified, then the Slurm launcher stopped before Python/validator execution because Puma's noninteractive job environment lacks `rg` at the campaign-marker check. This is a second application/launcher material defect, not scheduler/resource failure or a scientific evaluation. V1 provenance remains preserved and all 36 campaign leaves remain valid. |
| aggregate/validation v3 | `23565316` | failed | Terminal `FAILED 1:0`, 1:12, 4 CPUs/20 GB; source/dependency and all launcher checks passed, then the validator began immutable-package evaluation. It stopped at its first edge-occupancy read because `np.genfromtxt` inferred a too-short string field from early parameter names and truncates `sigma_SR`, yielding `IndexError` when the validator looks it up. This is an aggregate-validator application/schema defect; no gate decision or valid aggregate result was produced. Partial v3 result/summary directories exist and must be preserved or safely replaced only under fresh authority. |
| aggregate/validation v4 | `23565388` | failed | Terminal `FAILED 1:0`, 1:18, 4 CPUs/20 GB. The parser correction passed and validator processed into the JERC leaves, then incorrectly compared every leaf against ABBY's reference bounds. All physical parameters match, but fitted `sigma_SR` has a deliberately site-specific upper bound (ABBY `3.678561543741014`; JERC `1.2585830572660597`), so JERC correctly fails the erroneous cross-site equality check. This is an aggregate-validator contract-check defect; no gate decision or valid aggregate result was produced, and partial v4 result/summary directories now exist. |
| aggregate/validation v5 | `23565465` | completed | Terminal `COMPLETED 0:0`, 5:52, 4 CPUs/20 GB, MaxRSS 5.08 GB. `AGGREGATE_PASS leaves=36` and `AGGREGATE_PASS` emitted. The complete result/report/decision package exists: ABBY selects `daily_0.75`; JERC is integrity/interpretability pass with `inconclusive_metric_tradeoff` and no selected configuration. |

## Independent Read-Only Review

- Reviewer: `/root/iter011_review` (read-only; no files, scheduler state, or external artifacts modified).
- Reviewed source hashes: v3 `d236459c3a3bc72f0b85b15d8ce8c417c8b2876eff97ffecddaa60dc039015b0`; active v4 `954f78cce87e6fa73f414d05d92a4c9f8966e0a91ba0b8b3b255a2980a9f6f52`.
- Outcome: `pass`; v1/v2 review blocks were corrected and preserved as unsubmitted provenance. The v4 re-review approved the single authorized preflight launcher correction, which inserted the fixed repository root on `sys.path` before importing repository modules.
- Findings and response: the reviewer required actual hourly/HDF checks, exact bundle locks,
  compatible daily recovery, and daily-target smoke state; the active material verifies these checks.
- Aggregate reviewer: `/root/iter011_aggregate_review` (read-only). Final v5 review passed after
  verifying the aggregate validator's complete raw/HDF/bundle/provenance/daily-map/lag-24 checks,
  paired seed materiality, full-matrix non-domination, comprehensive site reports, and bounded
  aggregate source/materialization identity. Aggregate submission remains prohibited until all 36
  campaign leaves have terminal pass evidence.
- Aggregate v2 correction reviewer: `/root/iter011_aggregate_review` (read-only). Outcome: `pass`.
  It verified preservation of the failed-v1 artifacts, a one-line v1-to-v2 config delta, successful
  six-path sourcing, canonical/submitted byte identity, source/dependency manifest verification, and
  no evaluator/resource/runtime/dependency/scientific-contract change.
- Aggregate v3 correction reviewer: `/root/iter011_aggregate_review` (read-only). Outcome: `pass`.
  It verified v1/v2 preservation, the sole `rg`-to-`grep` submitted-script delta, all six marker
  counts, source/dependency/config identity, and no evaluator/resource/dependency/scientific change.
- Aggregate v4 correction reviewer: `/root/iter011_aggregate_review` (read-only). Outcome: `pass`.
  It verified v1-v3 artifacts and v3 partial outputs are preserved, the parser-only validator delta,
  exactly one finite in-range `sigma_SR` entry in each of 36 CSVs, and current provenance identity.
- Aggregate v5 correction reviewer: `/root/iter011_aggregate_review` (read-only). Outcome: `pass`.
  It verified v1-v4 preservation, per-site reference use, all 36 parameter/order/bounds/transform
  contracts, current identity, and no resource/dependency/scientific-contract change.

## Current Next Action

Closed. ABBY's `daily_0.75` result is bounded-pilot evidence for a future site-specific production
proposal only. JERC has no selected configuration because its eligible hourly configurations retain a
material trade-off. No follow-on execution is authorized; any new work requires a new consolidated
kickoff package.

## Final Result and Closeout

- Closeout identity: Iteration ID `iter011`; Status `completed`; Work type `implementation`;
  Objective `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`;
  Bounded scope `ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains`;
  Overall acceptance result `pass`; Decision `ABBY preferred_configuration_supported daily_0.75; JERC inconclusive_metric_tradeoff with no selected configuration`.
- Overall acceptance result: `pass`. The v5 aggregate job `23565465` reached terminal
  `COMPLETED 0:0` and emitted `AGGREGATE_PASS leaves=36` and `AGGREGATE_PASS` after validating all
  36 immutable campaign packages.
- Decision: ABBY is `preferred_configuration_supported` with selected configuration `daily_0.75`.
  JERC is `inconclusive_metric_tradeoff` with no selected configuration. This is a site-specific
  conclusion; it does not select a universal likelihood resolution or proposal scale.
- Evidence: the complete aggregate package is retained at
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter011_aggregate/result`,
  with the durable report and decision artifacts in `summaries/iter011/`. Failed aggregate v1--v4
  materials and v3/v4 partial outputs remain preserved as provenance.
- Handoff validation: identity `slurm/iter011/validate_iter011_handoff.py`; command
  `python development/spinup_forcing_coupling/slurm/iter011/validate_iter011_handoff.py --active-job-count 0`;
  output `ITER011_HANDOFF_VALIDATE_PASS leaves=36 decision=site_specific`; result `pass`.
- Limitation and next state: `/xdisk` remains temporary and unbacked. The line of work continues only
  through a fresh, explicitly approved proposal; no inference, extension, or automatic production run
  follows from this pilot.

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
