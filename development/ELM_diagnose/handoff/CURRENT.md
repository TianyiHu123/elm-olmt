# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `none`
- Most recent closed iteration: `iter004`
- Status: `completed`
- Phase: `closed`
- Active job scope: none; preflight `23830156` and diagnostic `23830259` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none; detector sessions `89518` and `43613` both reached queue-to-accounting handoff with outcome `finished`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-08T13:55:00-07:00`

## Closed Iteration Identity

- Iteration ID: `iter004`
- Work type: `implementation`
- Objective: Rank ABBY range-wide OAT responses for 13 carbon targets across 14 separately perturbed parameters.
- Bounded scope: 14 exact historical pickles; 1,400 members; 2018-2024 hourly means and population standard deviations; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted range-conditional descriptive OAT package; no global sensitivity, interaction, causal, tuning, or parameter-value claim.

## Evidence and Artifacts

- Preflight `23830156`: `COMPLETED 0:0`, 00:02:00, 30.00/30 GB; receipt and input manifest passed.
- Diagnostic `23830259`: `COMPLETED 0:0`, 00:02:11, 31,456,380 K peak RSS; application and artifact validator passed.
- Published result: 14 parameter rows, 1,400 member rows, 364 score rows, 40,040 response-curve rows, and 35 PNGs.
- Input manifest: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter004_abby_oat/preflight/attempt_1/artifacts/input_manifest.json`; SHA-256 `7c92ea9e0cd94b6657ea0926611ebbac6f4fe879947ee16826f1f0563d9b2082`.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter004_abby_oat/results`.
- Output manifest SHA-256: `9d4308d04b68e49a816ebb23e6162703165a3dca9d810e4cc958f714ea86eca2`.
- Detailed report: `development/ELM_diagnose/iterations/iter004.md`.
- Compact summary: `development/ELM_diagnose/summaries/iter004/ITER004_RESULT.md`.

## Risks and Limitations

- Results are conditional on the declared parameter ranges and separate OAT ensembles; they do not identify interactions, global importance, causality, optima, or tuning values.
- `grpnow` and `kmax` varied across their samples but produced zero score in all 26 groups.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the non-PI query is unavailable.

## Next Action and Next-Plan State

The Iter004 workflow is terminal and complete. No next iteration is proposed and no runtime authority remains active.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Treat Iter004 as immutable closed provenance.
3. Require a new complete planning-only package and explicit approval before initializing another iteration or taking runtime action.
