# iter018 - final nine-site operational coupled-optimization release

## Status

- Iteration ID: `iter018`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter018_operational_nine_site`
- Status: `planned`
- Phase: `review`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-21T19:17:05-07:00`
- Closed: `pending`

## Finalized Plan

The complete `ITER018_PLAN_BEGIN/END` proposal in `iterations/iter017.md`, recorded by commit
`e670efb`, was byte-identical to the handoff plan at approval. User response `approved full
kickoff package` at `2026-08-21T19:17:05-07:00` approves that package unchanged.

- Objective: execute the finalized three-stage pipeline separately at nine NEON sites, publish
  site-local MAP-candidate products and cross-site evidence, then complete terminal
  coupling-development closeout and merge-readiness assessment.
- Daily/`0.50`: ABBY, SOAP, YELL, WREF. Hourly/`0.75`: JERC, OSBS, RMNP, TALL, TEAK. All are
  single-site SR campaigns with a fresh `hybrid_high_l_maximin` pool (`q=0.90`, size 640, search
  seed 17017), 64 walkers, 8,000 steps, checkpoints every 2,000, transformed coordinates, the
  standard DE mixture, fitted site-local `sigma_SR`, and 16 processes.
- Each copied array owns exactly seeds `9009` through `9017`. Reporting has Tier-A acceptance
  range `[0.20, 0.50]` and copies leaf products; Tier-A is descriptive only.
- Nominal scope: 1 preflight, 9 initializations, 9 arrays/81 leaves, 9 reports, 1 aggregate, and
  1 handoff validator (102 compute work units/21 submissions). The only approved expansion is a
  hard cap of 205 work-unit executions through one reviewed preflight correction/rerun and one
  unchanged scheduler/resource retry per job or leaf.
- Exclusions: joint runs, historical-ledger reuse, TIM, alternate seeds, retraining, scientific
  control changes, environment/artifact repair, posterior promotion, push, PR, merge, and deletion.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approved full kickoff package`; `2026-08-21T19:17:05-07:00` |
| Goal and stop condition | Complete the approved final nine-site operational run through accounting, evaluation, four-record validation, comprehensive closeout, and merge-readiness declaration; no merge. |
| HPC site | UArizona Puma; `chopinsong` / `standard`; `OLMT_puma`; `development/hpc/puma.md`. |
| Output root and storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site/`; only approved stage directories; `/xdisk` is temporary/unbacked. |
| Dependencies | Released forcing SR and `drop21_corr080` spinup artifacts; nine approved case/observation pairs; environment and source/dependency manifests locked in preparation. |
| Resources and concurrency | Preflight 4 CPU/30m; init 8 CPU/4h; leaf 16 CPU/4h; report/aggregate 4 CPU/2h; handoff 2 CPU/30m; arrays `%2`, at most two arrays (four leaves/64 CPU/320 GB). |
| Authority | Prepare, review, preflight, staged submission/monitoring/accounting, evaluation, records, validation, and closeout; `sbatch`, job-scoped accounting/monitoring, and bounded `scancel` are approved. |
| Commit authority | One scoped preparation/source-lock commit before preflight and at most one scoped closeout commit; no push, PR, or merge. |

## Upstream Dependencies and Source Lock

- Bootstrap verified both released artifacts, `conda_envs/OLMT_puma.yml`, all nine expected case
  pickles and NEON v4 observations, and optimization/report entry points. Preparation must lock
  exact hashes and source snapshots before preflight.
- Repository parent at initialization: `34d70393ae2fddaaf0f16d522a1fd2f3fac6bcfc`; clean tree.

## Acceptance Gates and Decision Rule

- Integrity requires terminal accounting, immutable package identities/pools, 81 complete
  finite/bounded leaves, nine standard nine-export reports, aggregate evidence, and final
  agreement across this report, summary, registry, handoff, and artifacts.
- Decision `operational_release_ready` requires every integrity gate. Per-site status is
  `all_tier_a`, `partial_tier_a`, or `insufficient_retained`; it is descriptive, never posterior
  promotion or a universal recommendation.
- Application/code/interface/schema/data/dependency/numerical/gate failures outside the one
  preflight exception stop pending fresh approval.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| initialization records | none | complete | approved contract recorded; no compute or external root action |
| preparation/source lock | `a3542f3`, corrections through `eeec519` | materialized root and manifests | complete | source/package corrections preserved as diagnostic siblings |

## Independent Read-Only Review

- Reviewer: `/root/iter018_review`; read-only.
- Outcome: initial review and two re-reviews blocked package integrity; final re-review after
  `eeec519` resolved all execution-material findings but required this record reconciliation.
- Findings: source locking, submitted-copy guards, exact seed membership, Puma context guards,
  and durable state evidence were corrected without altering science, seeds, resources, or scope.

## Execution and Diagnostics

- Static validation: `git diff --check` and `bash -n` passed through `eeec519`; final
  materialization completed at the approved output root.
- Preflight, submissions, accounting, and diagnostics: pending record reconciliation and
  authorized preflight.

## Validation, Evaluation, and Decision

- Overall acceptance result: pending.
- Overall decision and closeout conclusion: pending.
- Next action: submit the approved, reviewed preflight from its materialized copy.

## Proposed Next-Iteration Plan (Planning Only)

Terminal declaration planned: coupling-framework development ends after Iter018 closeout. No next
iteration is proposed; any merge is a separate user decision.

## Closeout Checklist

- [ ] Iteration report, summary, registry, and handoff finalized and cross-validated
- [ ] Required external products and accounting verified
- [ ] Authorized closeout commit verified
