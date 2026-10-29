# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current plan SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Latest iteration locked plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Applicable campaign phase: Iter001 closed under its locked plan; revised Iter002 progression
  item 3 spinup baseline proposed
- Alignment status: `aligned`
- Approved deviation: `none`

## Live State

- Latest iteration: `iter001`
- Active iteration: `none`
- Status: `completed`
- Phase: `closed`
- Active job scope: none
- Active monitoring: none; all five recorded jobs have authoritative terminal accounting
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-29T01:23:58-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `closed`
- Kickoff goal and stop boundary: Iter001 initialized and validated the no-training ABBY/JERC data
  package through publication, terminal accounting, durable records, four-record validation, and
  the authorized closeout branch.
- User response and approval timestamp: approved with independent reviews before preflight and
  operational runs and three correction/retry cycles per phase; `2026-10-27T00:40:17-07:00`.
- Confirmed HPC system and profile: UA Puma; `development/hpc/puma.md`; `chopinsong/standard`;
  absolute `OLMT_puma` interpreter.
- Approved output root, layout, creation authority, and retention policy:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`;
  immutable components, appendable snapshot catalog, sources and failure evidence preserved.
- Locked inputs, dependencies, scope, exclusions, gates, and decision rule: completed contract in
  `iterations/iter001.md`; exact 18-parameter/1,024-member ABBY/JERC package, 61,320 no-leap hours,
  deterministic 819/205 split, all gates passed, no training or fixed-test use.
- Lifecycle and outside-sandbox authority: Iter001 authority exhausted and closed; no Iter002
  runtime, scheduler, directory, retry, or commit authority exists.
- Resources, monitoring/wait mechanism, retry boundaries, and cancellation scope: historical
  Iter001 contract and complete accounting are preserved in the report; no active scope remains.
- Closeout branch: one scoped no-push commit satisfied and externally verified with expected parent
  `174a7f6c33acbf111ef67533d6ef69ea33c91565` and subject
  `Initialize ABBY JERC surrogate input data`.

## Current Objective

Await fresh consolidated approval of the revised planning-only Iter002 spinup-baseline proposal.

## Best Evidence So Far

- Work type and bounded scope: Iter001 `data_initialization`; exact declared ABBY/JERC sources,
  named-variable NetCDF preparation, deterministic global split, independent reconstruction and
  catalog-last publication; no training.
- Declared input and upstream-dependency identities: source manifests under published snapshot
  `r0001`; original ABBY/JERC transient pickle hashes `65fac5b7...d1d82` and
  `cb808465...d3c5`; plan SHA-256 `347646ad...dda0c`.
- Headline evidence: ABBY and JERC each have 1,024 members and 61,320 aligned no-leap hours; 18
  named parameter variables; split counts 819 development and 205 fixed test; catalog snapshot
  hash `39b05495...187a`.
- Scheduler evidence: rejected preflights `24428809` and `24428935` were cancelled before
  execution and terminally accounted; preflight `24430059`, preparation `24430075`, and validation
  `24430091` completed `0:0`.
- Acceptance-gate result and decision: `pass`; `VALIDATE_SURROGATE_INPUT_OK`; immutable snapshot
  `r0001` published and ready for development-only prototype use.
- Campaign amendment: the current plan now develops spinup, GPP, and SR sequentially and represents
  site context through approved surface/climatology inputs while retaining site labels as metadata.
- Summary evidence: `development/three_stage_surrogate/summaries/iter001/`.

## Current Risks or Blockers

- No active blocker. `/xdisk` is temporary and not archival storage; only ABBY/JERC are currently
  initialized. Iter002 has no authority until the user approves a complete kickoff package.

## Next Action

1. Present the complete Iter002 kickoff/runtime package based on the proposal below and seek fresh
   approval.
2. Only on that approval, begin Section 4A recovery and create Iter002 records/scaffold; do not
   infer runtime authority from the campaign-plan amendment or its commit.

## Next Iteration Plan (Planning Only)

- Proposed sequential ID: `iter002`.
- Work type: `implementation`.
- Campaign-plan identity, applicable phase, alignment, and proposed deviation:
  `development/three_stage_surrogate/PLAN.md`, SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`, progression item 3
  (two-site spinup baseline), `aligned`, deviation `none`.
- Evidence-derived objective and optional hypothesis: implement and validate a deterministic pooled
  ABBY/JERC spinup C/N baseline with exact development-member control, flexible member prediction,
  physical/log evaluation, versioned development artifacts, and resource evidence. Hypothesis:
  the prior compact spinup feature/model configuration can provide a technically sound baseline
  against the new 18-parameter prepared data without adding categorical site identity.
- Proposed inputs, upstream dependencies, identities, and trust assumptions: consume only catalog
  snapshot `r0001`, its immutable source manifests, named NetCDFs, and split manifest from the
  Iter001 output root; preserve parameter/site/member/time identities and treat the 205 fixed-test
  IDs as forbidden at loader boundaries. Reuse compatible scaler, MLP, metric, plotting, and strict
  artifact-validation concepts only after source-contract inspection; do not reuse a model whose
  training membership or target definition is unproven.
- Bounded scope, work units, and exclusions: implement validated snapshot/member loading; one
  shared 25-feature train/predict schema consisting of the 18 ordered parameters, `PCT_SAND`,
  `ORGANIC`, `PRECTmms_clim_mean`, `PRECTmms_clim_std`, `FSDS_clim_mean`, `TBOT_clim_std`, and
  `RH_clim_seasonal_amp`; compute climatology from the exact first five complete forcing years
  (2018--2022, no-leap, 43,800 hours/site); retain site only as coordinate/provenance metadata.
  Implement separate training and flexible member-prediction interfaces plus versioned development
  artifacts. Use the ranked development manifest to lock one operational split: first 655 members
  for fit and remaining 164 for validation. Nest the smoke split as the first 80 operational-fit
  members and first 20 operational-validation members. Fit separate C and N MLPs with `(32,)`,
  `tanh`, `lbfgs`, alpha `40`, `max_iter=800`, estimator seed `42`, and independent X/Y scalers.
  Run preflight, 80/20 smoke, 655/164 operational baseline, and independent validation. Exclude
  fixed-test access, feature/configuration tuning, robustness repetitions, GPP/SR work, all-819
  fitting or prediction, release/publication claims, observations, optimization, and MCMC.
- Tentative acceptance gates and decision rule: exact catalog/snapshot/source/split identities;
  zero fixed-test parameter or target reads; exact member roles at both sites; exact 2018--2022
  timestamp-derived climatology and ordered 25-feature schema; fit-only scalers/models; training and
  validation results per site and pooled in both physical and natural-log space; conventional
  predictive R2, RMSE, MAE, signed `prediction - ELM` bias, residual standard deviation, counts,
  train/validation gaps, and eight-repeat validation permutation importance; physical/log scatter
  plots for both targets with training and validation panels; flexible single/subset/20/164-member
  prediction; finite strictly positive outputs with no clipping or row removal; complete provenance;
  and fresh-process artifact reload/prediction reproduction within locked tolerance. Optimizer
  convergence warnings are recorded but nonfatal; exceptions, missing artifacts, nonfinite or
  nonpositive outputs, and reload/package disagreement fail. No scientific-performance threshold
  applies. A technical pass may conclude either baseline acceptable for later release planning or
  configuration optimization recommended; both complete Iter002 successfully, but neither
  authorizes an all-819 fit or release.
- Proposed site, output root, resources, preflight, review, monitoring, retry, cancellation, and stop boundaries:
  Puma `chopinsong/standard`; proposed output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/three_stage_surrogate/iter002_abby_jerc_spinup_baseline`;
  four sequential jobs: preflight one task/2 CPUs/about 10 GB/30 minutes; smoke one task/4
  CPUs/about 20 GB/1 hour; operational one task/10 CPUs/about 50 GB/2 hours; independent validation
  one task/4 CPUs/about 20 GB/1 hour. Use fixed numerical-library threads and record wall time,
  peak memory, CPU efficiency, and convergence evidence. Require independent read-only review
  before preflight and refreshed review after passing preflight before smoke/operational work;
  corrections require refreshed review. Propose three bounded correction/retry cycles for
  preflight and three shared across smoke, operational, and validation; a fourth cycle, resource
  increase, or scientific/configuration change requires fresh approval. Use job-scoped monitoring
  through terminal accounting; cancel only recorded current-iteration jobs for scope/resource
  violations, runaway behavior, threatened inputs/outputs, or user request. Stop after validation,
  decision, records, a proposed scoped no-push closeout commit, and a planning-only Iter003
  proposal. Do not continue automatically into tuning or release.
- Expected evidence, artifacts, and record updates: locked configuration; source/execution
  manifests; exact member partitions; feature schema; fixed smoke and operational artifacts labeled
  as development evidence, not releases; flexible predictor; held-out prediction NetCDFs for 20 and
  164 members only; JSON and long-form CSV metrics; physical/log C/N scatter plots with training and
  validation panels; convergence and resource evidence; fresh-process reload report; tests and
  independent package validation; submitted scripts and terminal accounting; Iter002
  report/summary/registry/handoff; and four-record validation. No 819-member prediction file or
  published downstream C/N handoff is produced.
- Authorization boundary: fresh approval of one complete kickoff package is required; do not
  create the next report or iteration-specific scaffold automatically.

## Next Session Start Protocol

1. Read `PLAN.md`, this handoff, and `WORKFLOW.md`.
2. Read `iterations/iter001.md`, its registry row, and `summaries/iter001/`.
3. Read `development/hpc/puma.md` and inspect current Git, scheduler, catalog, and snapshot state.
4. Revalidate the revised Iter002 proposal and seek fresh approval of one consolidated package.
5. Only after approval, create Iter002 records/scaffold and follow the two mandatory review gates.

## Artifact References

- Current/latest report: `development/three_stage_surrogate/iterations/iter001.md`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Summaries: `development/three_stage_surrogate/summaries/iter001/`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter001/`
- Submitted scripts/configurations:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data/runs/iter001_abby_jerc_data_init`
- Scratch/published output:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`
