# iterXXX - <short objective>

## Status

- Iteration ID: `iterXXX`
- Work type: `<audit | data_initialization | implementation | validation | integration | robustness | release>`
- Run slug: `<campaign>_iterXXX_<work_unit>`
- Status: `planned`
- Phase: `initializing`
- Site profile: `development/hpc/<site>.md`
- Started: `<timestamp and timezone>`
- Closed: `<timestamp and timezone or pending>`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
- Applicable campaign phase:
- Alignment:
- Approved deviation: `none`

## Finalized Plan

- Sequential ID and work type:
- Evidence-derived objective and optional hypothesis:
- Proposed inputs, upstream dependencies, identities, and trust assumptions:
- Bounded scope, work units, and exclusions:
- Tentative acceptance gates and decision rule:
- Proposed site, output root, resources, preflight, review, monitoring, retry, cancellation, and stop boundaries:
- Expected evidence, artifacts, and record updates:
- Fresh consolidated kickoff-approval boundary:

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `<exact response; timestamp and timezone>` |
| Kickoff goal, finite work-unit count, and stop conditions | `<goal; count; conditions>` |
| Campaign plan identity and alignment | `<path; SHA-256; phase; alignment; approved deviation or none>` |
| Confirmed HPC system and site profile | `<system; development/hpc/<site>.md>` |
| Approved output and storage policy | `<exact root; layout; creation authority; retention assumptions>` |
| Locked dependencies, scope, exclusions, gates, and decision rule | `<identities and immutable terms>` |
| Lifecycle authority | `<preparation through records and closeout>` |
| Resources, monitoring/wait mechanism, and retry boundaries | `<exact resources and limits>` |
| Cancellation scope | `<conditions; exact current-iteration job scope>` |
| Outside-sandbox authority | `<locked sbatch; job-scoped monitoring/accounting; bounded scancel>` |
| Closeout branch | `<one commit authorized | validated_uncommitted>` |

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `<role>` | `<path>` | `<identity>` | `<size/hash>` | `<evidence>` |

## Acceptance Gates and Decision Rule

- Required completeness:
- Acceptance gates:
- Decision rule:
- Conditional metrics, aggregation, ranking, or tie-breaker:
- Changes requiring fresh authorization:

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path/hash>` | `<paths/hashes>` | `<paths>` | `<identities>` | `<identity>` | `<scope>` | `<state>` | `<mechanism; handle; outcome; reason>` |

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
- Campaign-plan amendment recommendation: `<none or advisory recommendation for user decision>`
- Next action:

## Proposed Next-Iteration Plan (Planning Only)

Use this section for exactly one complete proposal or replace it with an explicit terminal
declaration. A proposed campaign-plan amendment is not a next iteration and requires separate user
authorization outside this workflow.

- Proposed sequential ID:
- Work type:
- Campaign-plan identity, applicable phase, alignment, and proposed deviation:
- Evidence-derived objective and optional hypothesis:
- Proposed inputs, upstream dependencies, identities, and trust assumptions:
- Bounded scope, work units, and exclusions:
- Tentative acceptance gates and decision rule:
- Proposed site, output root, resources, preflight, review, monitoring, retry, cancellation, and stop boundaries:
- Expected evidence, artifacts, and record updates:
- Authorization boundary: fresh approval of one complete kickoff package is required; do not
  create the next report or iteration-specific scaffold automatically.

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Required evidence copied to `summaries/iterXXX/`
- [ ] `ITERATION_SUMMARY.md` updated
- [ ] `registry.csv` updated without schema changes
- [ ] `handoff/CURRENT.md` rebuilt
- [ ] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [ ] Four-record validator identity, command, output, and passing result recorded
- [ ] No job is active or unaccounted and every failure is classified
- [ ] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
