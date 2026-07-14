---
name: spinup-surrogate-handoff
description: Create a compact, reproducible handoff package for spinup surrogate development so a new session can continue immediately.
disable-model-invocation: true
---

# Spinup Surrogate Handoff

## Use When

- Iteration closeout is complete and a handoff is needed
- Session context is getting high after iteration work is documented
- User asks for a concise current status

## Source of Truth

Always keep this file current:

- `development/spinup_surrogate/handoff/CURRENT.md`

## Workflow Sequence

Use handoff only after the current iteration is documented:

1. Finish iteration tracking artifacts (`iterations/iterXXX.md`, summaries, registry updates).
2. Save current session context into `development/spinup_surrogate/handoff/CURRENT.md`.
3. Apply commit policy (default one checkpoint commit for finished iteration; split only if needed for clarity).
4. End current session.
5. Start a new session for the next iteration and run the New Session Bootstrap steps.

If the iteration ended in `failed` status, handoff becomes a debug handoff:

- clearly mark iteration as failed
- include blocked variant and failure bundle pointer from `iterations/iterXXX.md`
- set next session objective to debug and unblock before any new iteration runs

## New Session Bootstrap (Required)

At the start of the next session:

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load the last three iteration reports from `development/spinup_surrogate/iterations/iterXXX.md` (if fewer than three exist, load all available).
3. Read the latest iteration report in full.
4. From the previous one or two reports, at minimum extract: objective, variant matrix, key metrics, winner/blocked status, and decision rationale.
5. Use this combined context to plan the next iteration before any execution.

## Required Sections in `CURRENT.md`

1. Current objective
2. Best variant so far
3. Evidence (key metrics)
4. What changed in latest iteration
5. Open risks / unknowns
6. Next iteration plan
7. Next session start protocol (what to read/check first)
8. Ready/blocked status for next iteration
9. Required user decisions before execution (if any)
10. Artifact paths (repo summaries + `/pscratch/.../UQ_output/...`)
11. Files modified in repo
12. Failure debug bundle reference (required when latest iteration status is `failed`)

## Quality Rules

- Keep handoff concise and action-oriented.
- Prefer concrete numbers over qualitative claims.
- Include split mode and seed range used in comparisons.
- Include clear stop/go criteria for the next iteration.
- Include the iteration ID (for example `iter002`) in the handoff title/summary text.
- Do not require runnable commands in handoff; commands belong in iteration artifacts or Slurm execution workflow.
- In `Next session start protocol`, list the exact iteration report files to load.
- If latest iteration is `failed`, next session plan must start with debug/unblock steps, not a new variant sweep.

## Commit Policy During Handoff

- Default: create one checkpoint commit per finished iteration after `CURRENT.md` is updated.
- Optional: split into two commits only when it improves review clarity (for example code changes vs tracking/docs updates).
- If an iteration is aborted without meaningful tracked updates, skip creating a checkpoint commit.
- Use a commit message that includes the iteration ID (`iterXXX`) for traceability.

## Guardrails

- Do not paste large raw logs into handoff.
- Do not rely on terminal history as the only record.
- Verify referenced paths/files exist before finalizing handoff.
- Do not commit large raw `UQ_output` files unless explicitly requested.
