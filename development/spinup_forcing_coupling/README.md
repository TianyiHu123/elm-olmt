# Spinup-Forcing Coupling Development

This directory contains the durable workflow and iteration records for constructing and validating
the spinup-forcing surrogate coupling framework.

The framework-development workflow establishes correctness, interfaces, provenance, baseline
performance, and release evidence. Model-performance improvement and optimization are intentionally
out of scope and will use a separate workflow if pursued.

Start with `handoff/CURRENT.md`, then follow `WORKFLOW.md`.

## Structure

- `WORKFLOW.md`: canonical lifecycle, authority, evidence, and closeout policy.
- `handoff/CURRENT.md`: live state and next action.
- `iterations/iterXXX.md`: append-only evidence for initialized iterations.
- `registry.csv`: strict one-row index of closed iterations.
- `ITERATION_SUMMARY.md`: cumulative closeout summary.
- `summaries/iterXXX/`: compact decision evidence.
- `slurm/iterXXX/`: canonical iteration-specific execution material.
- `tools/`: reusable validation and analysis utilities.
- `templates/`: iteration and handoff scaffolds.

## Record Conventions

- Timestamps use ISO 8601 with a timezone.
- Tracked paths are repository-relative; external paths are absolute.
- Use `none` when a registry field does not apply. Quote CSV fields by standard CSV rules.
- In `registry.csv`, `closeout_mode` is `committed` or `validated_uncommitted`;
  `closeout_identity` is the observed commit SHA or the bounded diff/source-manifest identity.
- Do not change a shared schema for one iteration without updating the workflow, templates,
  validators, and consumers together.

## General Kickoff Prompt

Use the following prompt to start or resume this workflow. For `iter001`, include the plan with
the prompt or provide it when asked. For later iterations, the planning-only proposal comes from
the preceding closed report and `handoff/CURRENT.md`.

```text
/goal Start or resume the next spinup-forcing coupling iteration by following
development/spinup_forcing_coupling/WORKFLOW.md. Begin at Section 4A and continue until the
workflow-defined stop condition is reached.
```

The `/goal` statement names the lifecycle objective and stop boundary. It does not itself grant
initialization, execution, scheduler, cancellation, or commit authority; those come only from the
user-approved consolidated kickoff package.
