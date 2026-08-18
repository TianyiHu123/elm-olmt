# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter014`; Status `completed`; Work type `implementation`; Overall acceptance result `pass`; Decision `partial_repair`

## Live State

- Active iteration: `iter014`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `JERC high-likelihood candidate-pool reconstruction`
- Bounded scope: `pool_rule API; rebuild eligible rules from frozen ledger; hybrid-only MCMC if A geometry-fails; evaluate; aggregate; handoff validation`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014`
- Last updated: `2026-08-17T22:34:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `closed` (revised geometry-gate scientific handling executed)
- Kickoff goal and stop boundary: Executed Iter014 through aggregate; overall decision `partial_repair`
- User response and approval timestamp: original `approved the complete package` `2026-08-17T19:48:15-07:00`; revision `approved the revised package` `2026-08-17T20:18:46-07:00`
- Confirmed HPC system and profile: UArizona Puma; `development/hpc/puma.md`
- Locked dependencies: ledger `25382a57…`; control pool `32d2ba5f…`; hybrid pool `40ac807e…`; target `26e5caa0…`
- Closeout branch: one local closeout commit authorized; no push

## Current Objective

Closed. High-likelihood pool reconstruction at JERC yielded `partial_repair` for
`hybrid_high_l_maximin` and `geometry_gate_failed` for `rank_dominated`.

## Best Evidence So Far

- Work type and bounded scope: implementation; revised package completed
- Headline evidence: A condition `1.72e7` fails geometry; hybrid condition ≈359 passes;
  hybrid mean acceptance `0.1898` (control `0.1866`); cross-seed W `0.4365` (control `0.5484`)
- Acceptance-gate result and decision: integrity pass; overall `partial_repair`; no posterior promotion

## Current Risks or Blockers

- `/xdisk` products are temporary and unbacked
- Remaining W and acceptance gaps vs `repair_supported` thresholds

## Next Action

1. Complete handoff validation and authorized closeout commit (no push)
2. Do not start Iter015 until a fresh consolidated kickoff

## Next Iteration Plan (Planning Only)

Planning-only Iter015: longer and/or milder-quantile hybrid diagnostics at JERC to test
whether the remaining Wasserstein gap can clear without TIM revert or new search.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter014.md`, and `development/hpc/puma.md`.
2. Treat Iter014 as closed; initialize a successor only after a new approved package.

## Artifact References

- Current report: `development/spinup_forcing_coupling/iterations/iter014.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter014/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter014/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014`
