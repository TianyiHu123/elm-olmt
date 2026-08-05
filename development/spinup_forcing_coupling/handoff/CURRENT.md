# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter002`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-05T11:31:02-0700`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted` (Iter002 closed)
- Kickoff goal and stop boundary: publish identity-locked, inference-validated
  `forcing-surrogate-v1`; stop after terminal accounting, immutable gates, durable
  records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response `approved, yes and yes.`; accepted
  `2026-08-03T18:38:23-07:00`. Release-retry amendment accepted `2026-08-04T16:48:00-07:00`.
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`.
- Approved output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` with Iter002 run dirs only.
- Locked dependencies/gates/decision: amended package (full-data refit; 100-seed aggregate
  baseline characterization only; inference + ABBY operational validate).
- Outside-sandbox and closeout authorities: exhausted with Iter002 closeout.

## Current Objective

Identity-locked forcing-surrogate-v1 full-data release with inference validation

## Best Evidence So Far

- Work type: `implementation`
- Bounded scope: Nine sites; SR; full-data forcing-surrogate-v1; 8-repeat full-data importance; inference validation; ABBY operational predict; no live coupling
- Upstream dependency identities: source-manifest `ea7ec3f35b452c78b21ac710079004dcd083867c95d4262342c6bc4a8bf46ab2`; memmap
  `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`; artifact `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; inference summary
  `44e493d65b770aedec83ef2d75978c2ff7857f49fe0c79550df848c87af3c20e`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter002`
- Preflight `23491474` pass; historical release `23497577` fail (reproduction); amended
  release `23501708` pass; authoritative validate `23507103` pass
- Acceptance result: `pass`
- Decision: Standalone forcing-surrogate-v1 artifact identity-locked and inference-validated; full-data importance characterized; live coupling readiness not established

## Current Risks or Blockers

- `/xdisk` retention is temporary and unbacked.
- Accidental validate multi-submit is classified and closed (pending duplicates cancelled).

## Next Action

1. Idle until a consolidated kickoff package for proposed `iter003` is approved.

## Next Iteration Plan (Planning Only)

## Proposed Next-Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter003`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter003`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter003_preflight`,
  `spinup_forcing_coupling_iter003_bridge`, and
  `spinup_forcing_coupling_iter003_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: couple the closed Iter002 `forcing-surrogate-v1` artifact with an existing
locked spinup-surrogate artifact to produce and validate real forcing-target (`SR`)
predictions through the forcing bridge, replacing design-matrix-only bridge checks.

Evidence basis: Iter002 closed `pass` with identity-locked full-data artifact
SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` and
inference/`ABBY` operational validation; spinup handoff still records forcing-bridge
checks as column-order/shape/dtype only, awaiting a real forcing artifact.

Optional hypothesis: loading both versioned artifacts and exercising the bridge on a
bounded site/member fixture is sufficient to establish an executable coupling path
without MCMC, PPE sweeps, or accuracy thresholds.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Closed Iter002 artifact/manifest/validation/importance | Forcing surrogate | Immutable read-only; lock artifact SHA-256 `8d139b32...` |
| Closed Iter001 memmap/layout (if still needed for fixtures) | Optional fixture support | Read-only; reuse locked hashes only if required |
| Locked spinup-surrogate release named at kickoff | Spinup state surrogate | Immutable; exact path/hash chosen in kickoff package |
| `forcing_surrogate_artifact` / spinup loader APIs | Public load/predict | Repository commit and source manifest locked at preparation |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime/site | Puma; `chopinsong` / `standard` |

### 4. Bounded scope, work units, and exclusions

In scope: wire real forcing-surrogate predictions into the forcing bridge; bounded
preflight; one bridge execution work unit on a declared site/member/fixture; positive
and negative gates for schema/version/load failures; durable records and closeout.

Exclusions: MCMC/PPE campaigns; accuracy or coupling-readiness numeric thresholds beyond
functional/inference integrity; retraining either surrogate; feature selection; expanding
beyond the kickoff-declared fixture set.

Nominal scheduler tasks: 3. Provisional hard cap: 5.

### 5. Tentative acceptance gates and decision rule

Pass only if terminal accounting exists; both artifacts load under their versioned APIs;
bridge returns finite `SR` for the declared fixture; negative gates fail closed; durable
records agree after handoff validation. Pass means an executable forcing–spinup coupling
path is demonstrated on the fixture; it does not claim production MCMC readiness.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter003_{preflight,bridge,validate}/` |
| Preflight / bridge / validate | finalize exact CPU/mem/time at kickoff from fixture size |
| Review | independent read-only agent before substantive submission |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed bridge/validate; no automatic application/numerical retry |
| Cancellation | recorded Iter003 job IDs only under proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

### 7. Expected evidence, artifacts, and record updates

Bridge prediction/report JSON under the approved Iter003 run dirs; compact
`summaries/iter003/`; finalized `iterations/iter003.md`; `ITERATION_SUMMARY.md` append;
`registry.csv` row; rebuilt `handoff/CURRENT.md`; handoff validator result.

### 8. Fresh consolidated kickoff-approval boundary

Present one complete consolidated kickoff package that includes this plan unchanged and
states runtime contract, exact output-root authority, lifecycle authorities, resources,
retry/cancellation, outside-sandbox `sbatch`/monitoring/`scancel`, and closeout-commit
authorization. Obtain one explicit user approval before any Iter003 initialization.


## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Read `iterations/iter002.md` in full and up to two preceding reports.
3. Read registry/summary evidence and the proposed plan above.
4. Inspect Git state and reconcile scheduler/artifact state before any new kickoff.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter002.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter002/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter002/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
