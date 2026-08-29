# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `iter001`
- Status: `failed`
- Phase: `closed`
- Active job IDs: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-28T20:41:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `exhausted`
- Kickoff goal and stop boundary: Implement and close one integrated nine-site `SR` diagnostic. Stop only after terminal accounting, evaluation, records validation, and one authorized closeout commit.
- User response and approval timestamp: `2026-08-28T20:24:11-07:00`; “Start the ELM diagnostic iteration 1 by following development/ELM_diagnose/WORKFLOW.md. Begin at Section 4A and continue until the workflow-defined stop condition is reached. Use this kickoff package you just showed for this iteration.”
- Confirmed HPC system and profile: Puma; `development/hpc/puma.md`
- Approved output root, layout, creation authority, and retention policy: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter001/`; authorized creation of deterministic run paths; retained unchanged after closeout; no automated backup or deletion.
- Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule: nine ensemble `ppe6` controls; all 60 current `ctrlopt` historical candidates; nine standard coupling SR NetCDF observations; scalar `SR` only; seed-resolved optimized plots and per-seed metrics; control ensemble mean plus standard-deviation spread; UTC common finite support; no ranking, pooling, or score threshold. Preparation locks a full input receipt and hashes.
- Lifecycle and outside-sandbox authority: preparation, review, preflight, submission, monitoring, terminal accounting, evaluation, records, validation, and closeout; authorized `sbatch` for the locked preflight/substantive jobs and allowed preflight rerun, job-scoped monitoring/accounting, and bounded `scancel` for recorded Iter001 jobs under the approved condition.
- Resources, monitoring cadence, retry boundaries, and cancellation scope: Puma standard, account `chopinsong`, one node/task, four CPUs (20 GB implied), 00:15:00 preflight and 01:00:00 substantive caps, 300-second cadence; one minimal re-reviewed preflight-only correction/rerun; no automatic substantive retry; cancellation only for a proven universal pre-execution defect before substantive processing.
- Closeout branch: `one scoped closeout commit authorized`

## Current Objective

Iter001 closed failed before substantive diagnostics because the first approved optimized pickle lacks `case.output['SR']`.

## Best Evidence So Far

- Bootstrap verified all nine operational `ppe6` controls, all nine observations, and 60 optimized candidates.
- Independent review passed the locked preflight source.
- Puma job `23718019` failed `1:0` after 28 seconds; `preflight_result.json` reports `ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl: missing case.output['SR']`.
- `seff` recorded 2.41 GB/20 GB, so this is not a resource failure.

## Current Risks or Blockers

- The approved optimized input family does not expose the required `SR` output interface.
- No changed-input or output-generation retry is authorized by the exhausted contract.

## Next Action

Obtain a new complete package selecting compatible optimized historical output files or authorizing their generation/postprocessing. Do not retry Iter001 unchanged.

## Next Iteration Plan (Planning Only)

No Iter002 plan is proposed. Fresh approval is required to resolve the failed optimized-output interface.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, and `iterations/iter001.md`.
2. Preserve `23718019` receipt/logs and do not infer an alternative input interface.
3. Obtain new scope and runtime authority before any retry or output generation.

## Artifact References

- Current/latest report: `development/ELM_diagnose/iterations/iter001.md`
- Registry: `development/ELM_diagnose/registry.csv`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Summaries: `development/ELM_diagnose/summaries/`
- Canonical scripts: `development/ELM_diagnose/slurm/iter001/preflight_iter001.py` and `.slurm`
- Submitted scripts/configurations: `.../elm_diagnose_iter001/preflight/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter001/`
