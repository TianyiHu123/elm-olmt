# iterXXX - <short objective>

## Status

- Iteration ID: `iterXXX`
- Run slug: `spinup_surrogate_iterXXX`
- Status: `planned`
- Phase: `planning`
- Site profile: `development/hpc/<site>.md`
- Started: `<UTC timestamp>`
- Closed: `<UTC timestamp or pending>`

## Runtime Contract

| Field | Value |
| --- | --- |
| Run mode and stop conditions | `<N rounds or run-until-stopped>` |
| HPC confirmed | `<yes/no>` |
| Submission/monitoring authority | `<scope>` |
| Resource policy and caps | `<explicit values or calibrated caps>` |
| Closeout commit authority | `<yes/no>` |

## Context and Objective

- Prior baseline and evidence:
- Hypothesis:
- Objective:

## Fixed Controls and Variant Matrix

- Cases:
- Split mode:
- Train fraction:
- Targets:
- Seed range:
- Other fixed controls:

| Variant | Change from control | Expected output path |
| --- | --- | --- |
| `<name>` | `<description>` | `<path>` |

## Decision and Retry Rules

- Required seeds and eligible variant states:
- Target-combination and ranking rule:
- Acceptance gates:
- Tie-breaker:
- Scientific-rejection rule:
- Retryable failure classes, maximum retries, and fail-fast behavior:
- Changes that require fresh user authorization:

## Provenance and Job Ledger

| Variant | Canonical script and SHA-256 | Submitted script and SHA-256 | Commit | Dirty diff/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path/hash>` | `<path/hash>` | `<hash>` | `<path/hash or clean>` | `<IDs>` | `<state>` | `<notes>` |

## Execution and Diagnostics

- Exact submission commands:
- Queue/accounting evidence:
- Resource diagnostics:
- Failure or rejection evidence:

## Results and Decision

| Variant | Eligible | Key metrics | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `<name>` | `<yes/no>` | `<metrics>` | `<pass/fail/rejected>` | `<rationale>` |

- Selected baseline or no-promotion decision:
- Next action:

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Summary/stability artifacts copied to `summaries/iterXXX/`
- [ ] `registry.csv` updated
- [ ] `handoff/CURRENT.md` updated
- [ ] Optional one closeout commit created, if authorized
