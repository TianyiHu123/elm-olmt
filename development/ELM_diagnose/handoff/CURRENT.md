# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `none`
- Status: `not_initialized`
- Phase: `pre_kickoff`
- Active job IDs: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-27T00:00:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `not approved`
- Kickoff goal and stop boundary: none
- User response and approval timestamp: none
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`
- Approved output root, layout, creation authority, and retention policy: none
- Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule: none
- Lifecycle and outside-sandbox authority: none
- Resources, monitoring cadence, retry boundaries, and cancellation scope: none
- Closeout branch: `none`

## Current Objective

Initialize a general ELM diagnostic-development workflow. No diagnostic iteration, input set, site selection, or cross-site comparison has been proposed or approved.

## Best Evidence So Far

- Workload scaffold and general workflow engine are present.
- The intended diagnostic inputs will be transferred to Puma later; no input files are currently declared or available to this workflow.

## Current Risks or Blockers

- No Iter001 diagnostic plan or consolidated kickoff package has been approved.
- ELM output and `.pkl` input locations on Puma are not yet available.

## Next Action

1. When diagnostic inputs are available, obtain the user-defined Iter001 scope, including the selected site/model outputs and whether a cross-site comparison is requested.
2. Present one complete consolidated kickoff package before creating `iter001` material or executing repository code.

## Next Iteration Plan (Planning Only)

No Iter001 proposal has been supplied. The user will determine diagnostic inputs, site selection, and any cross-site comparison at kickoff.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Confirm the selected diagnostic inputs are available and obtain the Iter001 plan.
3. Read `development/hpc/puma.md` before site-dependent planning or execution.
4. Inspect Git state.
5. Seek approval of one complete consolidated kickoff package before initializing an iteration.

## Artifact References

- Current/latest report: none
- Registry: `development/ELM_diagnose/registry.csv`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Summaries: `development/ELM_diagnose/summaries/`
- Canonical scripts: none
- Submitted scripts/configurations: none
- Scratch output: none
