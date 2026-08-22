# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter018`
- Status: `planned`
- Phase: `initializing`
- Active job IDs: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-21T19:17:05-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved`
- User response and approval timestamp: `approved full kickoff package`;
  `2026-08-21T19:17:05-07:00`.
- Goal and stop boundary: complete final nine-site operational release through accounting,
  evaluation, four-record validation, comprehensive coupling-development closeout, and a
  merge-readiness declaration; no merge.
- Site and output authority: UArizona Puma `chopinsong` / `standard`, `OLMT_puma`, and only
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site/` plus its approved stage layout; `/xdisk` is unbacked.
- Locked scope: nine independent SR sites: daily/0.50 ABBY, SOAP, YELL, WREF; hourly/0.75 JERC,
  OSBS, RMNP, TALL, TEAK; fresh q=0.90 hybrid pools, 64x8000 leaves, seeds 9009--9017, 102 work
  units, and the exact gates/exclusions in `iterations/iter018.md`.
- Lifecycle authority: preparation, source lock, independent review, preflight, staged
  submission, monitoring/accounting, evaluation, records, validation, and closeout.
- Outside-sandbox authority: `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`,
  `job-history`, and `job-limits`; `scancel` only for recorded Iter018 IDs under the approved
  universal-pre-execution-defect or user-emergency condition.
- Resources/retries: preflight 4 CPU/30m; initialization 8 CPU/4h; leaf 16 CPU/4h;
  report/aggregate 4 CPU/2h; handoff 2 CPU/30m; at most two `%2` arrays. One reviewed preflight
  correction/rerun and one unchanged scheduler/resource retry per job or leaf; all other failures
  need fresh approval.
- Closeout branch: one preparation/source-lock commit and at most one closeout commit; no push,
  PR, or merge.

## Current Objective

Create and source-lock the thin Iter018 adapters/configurations and materialization package, then
obtain the required independent read-only review before preflight.

## Best Evidence So Far

- Iter017 validator job `23610344` is terminal `COMPLETED 0:0`; no Iter018 root or job exists.
- All nine case/observation pairs, released artifacts, environment, and entry points were present
  at bootstrap; Puma capacity supports the approved resource cap.
- The complete planning block was synchronized before approval and is preserved in the Iter017
  closure; approved contract restatement is in `iterations/iter018.md`.

## Current Risks or Blockers

- `none`; preparation has not yet created source-locked execution material.

## Next Action

1. Create canonical Iter018 stage adapters, configurations, aggregate, and validator; statically
   validate them and make the approved source-lock commit before independent review.

## Next Iteration Plan (Planning Only)

Terminal declaration: after validated Iter018 evidence and comprehensive closeout, the
spinup-forcing coupling-development line ends. Any merge is a separate user decision.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter018.md`, then Iter017 closure.
2. Reconcile Git, current artifacts, and job-scoped scheduler evidence before acting.
3. Continue from the recorded phase while this approved package remains unchanged and unexhausted.

## Artifact References

- Current report: `development/spinup_forcing_coupling/iterations/iter018.md`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter018/` (pending)
- Submitted package and scratch output: approved Iter018 root (not yet created)
- Cumulative records: `ITERATION_SUMMARY.md`, `registry.csv`, `summaries/iter018/` (pending)
