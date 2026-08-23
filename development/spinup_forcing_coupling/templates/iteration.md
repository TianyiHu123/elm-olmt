# iterXXX - <short objective>

## Status

- Iteration ID: `iterXXX`
- Work type: `<audit | implementation | validation | integration | release>`
- Run slug: `spinup_forcing_coupling_iterXXX_<work_unit>`
- Status: `planned`
- Phase: `initializing`
- Site profile: `development/hpc/<site>.md`
- Started: `<timestamp and timezone>`
- Closed: `<timestamp and timezone or pending>`

## Finalized Plan

- Sequential ID and work type:
- Evidence-derived objective and optional hypothesis:
- Proposed upstream dependencies and trust assumptions:
- Bounded scope, work units, and exclusions:
- Tentative acceptance gates and decision rule:
- Proposed site and resource envelope, preflight, review, retry, cancellation, and stop boundaries:
- Expected evidence, artifacts, and record updates:
- Fresh consolidated kickoff-approval boundary:

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `<exact response; timestamp and timezone>` |
| Kickoff goal, finite work-unit count, and stop conditions | `<goal; count; conditions>` |
| Confirmed HPC system and site profile | `<system; development/hpc/<site>.md>` |
| Approved output and storage policy | `<exact root; work-unit layout; creation authority; retention/backup assumptions>` |
| Locked dependencies, scope, exclusions, gates, and decision rule | `<identities and immutable terms>` |
| Lifecycle authority | `<preparation through records and closeout>` |
| Resources and retry boundaries | `<exact resources; separate preflight and scheduler/resource retry limits>` |
| Cancellation scope | `<conditions; exact current-iteration job scope>` |
| Outside-sandbox authority | `<locked sbatch; job-scoped read-only monitoring/accounting; bounded scancel>` |
| Closeout branch | `<one commit authorized | validated_uncommitted>` |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `<role>` | `<path>` | `<identity>` | `<size/hash>` | `<evidence>` |

- Repository commit:
- Clean tree or bounded diff/source manifest:
- Environment identity:

## Acceptance Gates and Decision Rule

- Required completeness:
- Acceptance gates:
- Decision rule:
- Conditional comparative metrics, aggregation, ranking, or tie-breaker:
- Changes requiring fresh authorization:

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path/hash>` | `<paths/hashes>` | `<paths>` | `<identities>` | `<identity>` | `<IDs>` | `<state>` | `<notes>` |

## Independent Read-Only Review

- Reviewer:
- Reviewed source hash:
- Outcome:
- Findings and primary-agent response:

## Execution and Diagnostics

- Static validation:
- Preflight:
- Exact submission commands:
- Job identity checks:
- Queue and terminal accounting:
- Resource diagnostics:
- Failure, rejection, retry, or cancellation evidence:

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `<name>` | `<yes/no>` | `<paths and findings>` | `<pass/fail/rejected>` | `<rationale>` |

- Overall acceptance result:
- Overall decision and closeout conclusion:
- Limitations:
- Next action:

## Proposed Next-Iteration Plan (Planning Only)

Use this section for exactly one complete next-iteration proposal, or replace it with an explicit
terminal declaration that no next iteration is proposed.

- Proposed sequential ID:
- Work type:
- Evidence-derived objective and hypothesis:
- Proposed upstream dependencies and trust assumptions:
- Bounded scope, work units, and exclusions:
- Tentative acceptance gates and decision rule:
- Proposed site and resource envelope, preflight, review, retry, cancellation, and stop
  boundaries:
- Expected evidence, artifacts, and record updates:
- Authorization boundary: fresh approval of one complete consolidated kickoff package is
  required; do not create the next report or iteration-specific scaffold automatically.

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Required evidence copied to `summaries/iterXXX/`
- [ ] `ITERATION_SUMMARY.md` updated
- [ ] `registry.csv` updated without schema changes
- [ ] `handoff/CURRENT.md` rebuilt
- [ ] Four-record validator identity, command, output, and passing result recorded
- [ ] No job is active or unaccounted and every failure is classified
- [ ] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
