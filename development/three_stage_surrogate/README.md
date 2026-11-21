# Three-Stage Surrogate Development

This directory contains the campaign plan, reusable workflow, handoff, and iteration records for
developing the three-stage ELM surrogate system. Core reusable implementation belongs in the
repository's normal source and test locations, not in this directory.

Start with `PLAN.md`, then read `handoff/CURRENT.md` and follow `WORKFLOW.md`.

## Structure

- `PLAN.md`: user-approved campaign direction, architecture, scope, and development progression.
- `WORKFLOW.md`: context-independent iteration lifecycle, authority, evidence, and closeout procedure.
- `handoff/CURRENT.md`: live state, campaign-plan identity, authority, and next action.
- `iterations/iterXXX.md`: exact approved plan, runtime contract, evidence, and decision for an initialized iteration.
- `registry.csv`: fixed-schema index of closed iterations.
- `ITERATION_SUMMARY.md`: cumulative closeout evidence and decisions.
- `summaries/iterXXX/`: compact decision evidence required by an iteration plan.
- `slurm/iterXXX/`: canonical iteration-specific execution material when required.
- `tools/`: reusable campaign-specific validation and analysis utilities.
- `templates/`: iteration and handoff scaffolds.

## Record Conventions

- Timestamps use ISO 8601 with a timezone.
- Tracked paths are repository-relative; external paths are absolute.
- Use `none` when a registry field does not apply. Quote CSV fields using standard CSV rules.
- In `registry.csv`, `closeout_mode` is `committed` or `validated_uncommitted`; `closeout_identity`
  is the observed commit SHA or the bounded diff/source-manifest identity.
- Do not change a shared schema for one iteration without updating the workflow, templates,
  validators, and consumers together.

## General Kickoff Prompt

For `iter001`, provide or finalize its planning-only proposal before requesting kickoff. For later
iterations, recover the proposal from the preceding closed report and `handoff/CURRENT.md`.

```text
/goal Start or resume the active or next three-stage-surrogate iteration by following
development/three_stage_surrogate/WORKFLOW.md. Begin at Section 4A and continue until the
workflow-defined stop condition is reached. Apply the monitoring-continuity gate before any
turn-ending response.
```

The goal names the lifecycle objective and stop boundary. It does not grant initialization,
execution, scheduler, cancellation, directory-creation, or commit authority; those come only from
the user-approved consolidated kickoff package.
