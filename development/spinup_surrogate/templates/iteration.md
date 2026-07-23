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

| Variant | Canonical script and SHA-256 | Variant-local submitted copy/config and SHA-256 | Variant-local log paths | Commit | Dirty diff/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path/hash>` | `<script path/hash>; <config path/hash>` | `<stdout>; <stderr>` | `<hash>` | `<path/hash or clean>` | `<IDs>` | `<state>` | `<notes>` |

## Execution and Diagnostics

- Exact submission commands:
- Variant-local submission-copy/configuration and log-path evidence:
- Queue/accounting evidence:
- Resource diagnostics:
- Failure or rejection evidence:

## Results and Decision

| Variant | Eligible | Key metrics | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `<name>` | `<yes/no>` | `<metrics>` | `<pass/fail/rejected>` | `<rationale>` |

- Selected baseline or no-promotion decision:
- Next action:

## Proposed Next-Iteration Plan (Planning Only)

- Proposed sequential ID and retained baseline:
- Evidence-derived hypothesis:
- Tentative fixed controls and candidate matrix:
- Tentative acceptance gates and ranking rule:
- Proposed site/resources, preflight, reviewer, and retry boundaries:
- Expected artifacts and decision record:
- Authorization boundary: `<A new runtime contract is required; do not scaffold, submit, or execute this proposal automatically.>`

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Summary/stability artifacts copied to `summaries/iterXXX/`
- [ ] `ITERATION_SUMMARY.md` updated with objective, settings, evidence, and conclusion
- [ ] `registry.csv` updated
- [ ] `handoff/CURRENT.md` updated
- [ ] Optional one closeout commit created, if authorized
