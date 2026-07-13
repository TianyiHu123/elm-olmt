---
name: spinup-surrogate-handoff
description: Create a compact, reproducible handoff package for spinup surrogate development so a new session can continue immediately.
disable-model-invocation: true
---

# Spinup Surrogate Handoff

## Use When

- Session context is getting high and a handoff is needed
- Finishing a run batch and capturing the next action
- User asks for a concise current status

## Source of Truth

Always keep this file current:

- `development/spinup_surrogate/handoff/CURRENT.md`

## Required Sections in `CURRENT.md`

1. Current objective
2. Best variant so far
3. Evidence (key metrics)
4. What changed in latest iteration
5. Open risks / unknowns
6. Next iteration plan
7. Exact commands to run next
8. Artifact paths (repo summaries + `/pscratch/.../UQ_output/...`)
9. Files modified in repo

## Quality Rules

- Keep handoff concise and action-oriented.
- Prefer concrete numbers over qualitative claims.
- Include split mode and seed range used in comparisons.
- Include clear stop/go criteria for the next iteration.
- Include the iteration ID (for example `iter002`) in the handoff title/summary text.

## Commit Checkpoint Before Handoff

- If meaningful workflow artifacts are uncommitted, create one checkpoint commit before finalizing handoff.
- Use a commit message that includes the iteration ID (`iterXXX`) for traceability.
- Prefer one coherent commit per iteration milestone, not one commit per run.

## Guardrails

- Do not paste large raw logs into handoff.
- Do not rely on terminal history as the only record.
- Verify referenced paths/files exist before finalizing handoff.
- Do not commit large raw `UQ_output` files unless explicitly requested.
