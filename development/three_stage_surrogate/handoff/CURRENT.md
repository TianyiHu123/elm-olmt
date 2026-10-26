# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Active iteration locked plan SHA-256: `none`
- Applicable campaign phase: project scaffold and pre-kickoff planning
- Alignment status: `aligned`
- Approved deviation: `none`

## Live State

- Active iteration: `none`
- Status: `not_initialized`
- Phase: `pre_kickoff`
- Active job scope: `none`
- Active monitoring: `none`
- Site profile: `not selected`
- Last updated: `2026-10-26T03:08:36-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `not approved`
- Kickoff goal and stop boundary: `none`
- User response and approval timestamp: `none`
- Confirmed HPC system and profile: `none`
- Approved output root, layout, creation authority, and retention policy: `none`
- Locked inputs, dependencies, scope, exclusions, gates, and decision rule: `none`
- Lifecycle and outside-sandbox authority: `none`
- Resources, monitoring/wait mechanism, retry boundaries, and cancellation scope: `none`
- Closeout branch: `none`

## Current Objective

Prepare a complete planning-only proposal for the first bounded campaign iteration; no iteration or
runtime work is initialized.

## Best Evidence So Far

- The campaign direction and initial development progression are recorded in `PLAN.md`.
- The spinup design is settled at exactly two soil-only, full-profile outputs reconstructed from
  `soil1`-`soil4` over the 10 active decomposition layers with ELM layer-thickness weighting.
- ABBY and JERC spinup-preprocessing NetCDF files for all 1,024 members per site have been
  transferred under the declared Puma `spinup_preprocessing/` root; their identities, schemas,
  units, member coverage, and recorded reconstruction evidence remain subject to Iter001 input
  validation.
- The plan defines paired held-out C/N error outputs and the diagnostic-only surrogate/depth-error
  dependence check required by the downstream MCMC project. The MCMC project owns the fixed
  site-specific NEON-depth observation operator and likelihood construction.
- No iteration-specific inputs, runtime contract, outputs, jobs, or results exist.

## Current Risks or Blockers

- The exact authoritative ABBY/JERC PPE parameter/member mapping, forcing, GPP, and SR inputs and
  their schemas and coverage must still be declared or confirmed before the first
  data-initialization proposal can be finalized.
- Preprocessed spinup inputs for the remaining seven sites are pending, but they do not block the
  planned ABBY/JERC initialization.

## Next Action

1. Discuss and finalize the complete `iter001` data-initialization proposal.
2. Present one consolidated kickoff package for user approval before creating any
   iteration-specific record, script, summary, or external output directory.

## Next Iteration Plan (Planning Only)

The campaign plan proposes a first data-initialization iteration, but its complete planning-only
proposal has not yet been finalized or approved.

## Next Session Start Protocol

1. Read `PLAN.md`, this handoff, and `WORKFLOW.md`.
2. Confirm Git state and the current campaign-plan identity.
3. Do not expect an iteration report, registry row, summary, script, or job for pre-kickoff
   `iter001`.
4. Confirm the remaining ABBY/JERC input paths and resolve every missing proposal field.
5. Seek one approval of the complete kickoff package before initialization or runtime action.

## Artifact References

- Current/latest report: `none`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Summaries: `none`
- Canonical scripts: `none`
- Submitted scripts/configurations: `none`
- Scratch output: `none`
