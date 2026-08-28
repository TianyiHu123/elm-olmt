# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `iterXXX` or `none`
- Status: `planned | in_progress | completed | failed | blocked | not_initialized`
- Phase: `pre_kickoff | ready_for_kickoff_approval | initializing | preparing | review | preflight | execution | evaluation | closeout | closed`
- Active job IDs: `<IDs or none>`
- Site profile: `development/hpc/<site>.md` or `not selected`
- Last updated: `<timestamp and timezone>`

## Active Kickoff Package and Runtime Authority

- Package state: `<not approved | approved | exhausted | closed>`
- Kickoff goal and stop boundary:
- User response and approval timestamp:
- Confirmed HPC system and profile:
- Approved output root, layout, creation authority, and retention policy:
- Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule:
- Lifecycle and outside-sandbox authority:
- Resources, retry boundaries, and cancellation scope:
- Closeout branch: `<one commit authorized | validated_uncommitted | none>`

## Current Objective

<One concise statement.>

## Best Evidence So Far

- Work type and bounded scope:
- Declared diagnostic-input and upstream-dependency identities:
- Headline evidence:
- Acceptance-gate result and decision:

## Current Risks or Blockers

- <Risk, blocker, or `none`>

## Next Action

1. <Concrete next workflow action>

## Next Iteration Plan (Planning Only)

<Copy the complete planning-only proposal from the latest closed iteration report unchanged, or record an explicit terminal declaration. For pre-kickoff Iter001, record the user-supplied plan or state that none has been supplied.>

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. If an active or closed iteration exists, read its `iterations/iterXXX.md` report in full and up to two preceding reports. No report is expected for pre-kickoff `iter001`.
3. Read relevant registry rows and summaries.
4. Read the proposed or approved HPC profile when one exists; otherwise leave site selection unresolved.
5. Inspect Git state and reconcile scheduler and artifact state relevant to any recorded iteration.
6. For a new iteration, resolve missing decisions and seek one approval of the complete consolidated kickoff package. For an initialized iteration, verify and reuse its recorded, unexhausted package without asking again.

## Artifact References

- Current/latest report:
- Registry:
- Cumulative summary:
- Summaries:
- Canonical scripts:
- Submitted scripts/configurations:
- Scratch output:
