# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Latest iteration locked plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Applicable campaign phase: Iter001 data initialization completed; Iter002 progression item 3 proposed
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
- Last updated: `2026-10-27T05:39:17-07:00`

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

Await user review and fresh consolidated approval of the planning-only Iter002 proposal.

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
- Summary evidence: `development/three_stage_surrogate/summaries/iter001/`.

## Current Risks or Blockers

- No active blocker. `/xdisk` is temporary and not archival storage; only ABBY/JERC are currently
  initialized. Iter002 has no authority until the user approves a complete kickoff package.

## Next Action

1. Review and revise or approve the Iter002 planning-only proposal below.
2. On approval, begin Section 4A recovery and create Iter002 records/scaffold; do not infer approval
   from this handoff.

## Next Iteration Plan (Planning Only)

- Proposed sequential ID: `iter002`.
- Work type: `implementation`.
- Campaign-plan identity, applicable phase, alignment, and proposed deviation:
  `development/three_stage_surrogate/PLAN.md`, SHA-256
  `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`, progression item 3
  (two-site prototype), `aligned`, deviation `none`.
- Evidence-derived objective and optional hypothesis: implement a deterministic ABBY/JERC direct
  `in_sample` spinup -> GPP -> SR prototype that enforces the global development-member boundary,
  uses predicted upstream C/N and same-hour predicted GPP, and proves one reusable end-to-end
  inference path. Hypothesis: existing surrogate/scaler components can be composed behind shared
  data and feature-schema interfaces without redesigning the three stages.
- Proposed inputs, upstream dependencies, identities, and trust assumptions: consume only catalog
  snapshot `r0001`, its immutable source manifests, named NetCDFs, and split manifest from the
  Iter001 output root; preserve parameter/site/member/time identities and treat the 205 fixed-test
  IDs as forbidden at loader boundaries. Reuse compatible code in `model_ELM/` and root training
  entry points only after source-contract inspection; do not reuse an artifact whose training
  membership is unproven.
- Bounded scope, work units, and exclusions: inspect and reuse existing model interfaces; implement
  shared snapshot/split loading, feature ordering, actual-timestamp no-leap `sin_doy`/`cos_doy`,
  explicit site identity, direct predicted-upstream feature generation, deterministic three-stage
  fit/predict orchestration, bundle provenance, and focused tests. Run one fixed smoke prototype on
  the first 64 ranked development members for fit and the next 16 ranked development members for
  smoke validation, using the 2018 hourly window and fixed non-tuned model settings. Exclude all
  fixed-test access, hyperparameter/feature selection, robustness repetitions, release claims,
  other sites, observations, optimization, MCMC, and scientific performance thresholds.
- Tentative acceptance gates and decision rule: exact snapshot and split identity; zero fixed-test
  reads; synchronized member/site/time grouping; fitted scalers see fit members only; GPP consumes
  predicted C/N and SR consumes predicted C/N plus predicted same-hour GPP; one deterministic
  end-to-end inference round trip; artifact reload reproduces predictions within declared numeric
  tolerance; finite outputs and complete provenance; unit/integration tests and independent
  validator pass. Accept the prototype if interface and leakage gates pass; record smoke metrics as
  descriptive evidence only and do not select or reject architecture from them.
- Proposed site, output root, resources, preflight, review, monitoring, retry, cancellation, and stop boundaries:
  Puma `chopinsong/standard`; proposed output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/three_stage_surrogate/iter002_abby_jerc_prototype`;
  preflight one task/4 CPUs/20 GB/1 hour, prototype one task/16 CPUs/80 GB/8 hours, validation one
  task/8 CPUs/40 GB/2 hours; independent read-only reviews before preflight and operational work;
  proposed three bounded correction/retry cycles separately for preflight and operational work;
  job-scoped monitoring through terminal accounting; cancellation only for recorded scope/resource
  violations, runaway behavior, threatened inputs/outputs, or user request. Stop after validation,
  records, the approved closeout branch, and a planning-only Iter003 proposal.
- Expected evidence, artifacts, and record updates: locked config/source manifest, global-member
  exclusion evidence, feature schema, fixed smoke member lists, stage/bundle artifacts, predicted
  upstream audit, deterministic reload/inference report, descriptive smoke metrics, tests,
  submitted scripts and accounting, Iter002 report/summary/registry/handoff, and four-record
  validation.
- Authorization boundary: fresh approval of one complete kickoff package is required; do not
  create the next report or iteration-specific scaffold automatically.

## Next Session Start Protocol

1. Read `PLAN.md`, this handoff, and `WORKFLOW.md`.
2. Read `iterations/iter001.md`, its registry row, and `summaries/iter001/`.
3. Read `development/hpc/puma.md` and inspect current Git, scheduler, catalog, and snapshot state.
4. Resolve any Iter002 proposal revisions and seek fresh approval of one consolidated package.
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
