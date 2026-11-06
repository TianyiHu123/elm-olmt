# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current and latest locked plan SHA-256:
  `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6, SR development and configuration selection
- Planning alignment status: `aligned`; approved deviation: `none`

## Live State

- Active iteration: none; latest closed iteration: `iter009`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Acceptance result: `pass`
- Decision: `sr_configuration_selected`
- Active job scope: none; no job is active or unaccounted
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-06T02:35:17-07:00`

## Completed Objective and Scope

Iter009 implemented the pooled ABBY/JERC hourly physical-SR interface from fixed published C/N and
same-hour GPP predictions, validated its 44-feature contract, screened the exact 24-candidate MLP
design, and selected the best technically eligible configuration using development-only evidence.
The 205 fixed-test members, all-819 SR fitting, uncertainty, release, observations, likelihood, and
MCMC remained outside scope.

## Best Evidence and Decision

- Unit1 job `24524508`, all 192 screen leaves under `24524587`, all 72 finalist leaves under
  `24536618`, and final job `24548424` completed `0:0`; no retry submission was consumed.
- Every production leaf passed complete coverage, finite prediction, serialization, hash,
  zero-convergence-warning, exclusion, and successful scaled-scratch cleanup gates.
- Screen finalists were `[0,21,2,8,16,13]`; the final ranking over all 20 splits selected
  candidate 21: `(64,32)`, `tanh`, alpha `1e-4`, with the frozen Adam controls.
- Candidate 21 achieved worst/mean normalized ordinal scores `1.0/1.0`. Hourly R2 q10/RMSE q90/
  median absolute bias were `0.736201/1.119896/0.027569`; daily values were
  `0.737210/1.098576/0.027569`.
- Final selection report `4c414784...931c` and fresh validation `8a0138fe...967f` agree on
  candidate 21. The validator recomputed 240 metric rows from raw physical SR truth and hashed
  predictions. No absolute performance gate was applied.
- Overall decision: `sr_configuration_selected`. Candidate 21 is frozen for separately approved
  later work; no all-819 fit or release is authorized.

## Outputs and Evidence

- Compact evidence: `development/three_stage_surrogate/summaries/iter009/`
- Iteration report: `development/three_stage_surrogate/iterations/iter009.md`
- Full run root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter009_abby_jerc_sr_config`
- Final evidence: `runs/final/attempt_1/final_metric_distribution.csv`, `final_ranking.csv`,
  `final_selection_report.json`, and `final_validation.json`
- Execution manifest SHA-256:
  `dbcd4d68eb355d6613fc7e75f042b04ec88f0bc7c6060bc192147aaad583ee15`

## Interpretation and Risks

- Evidence is `fixed_upstream_sr_stage`, not end-to-end held out: both published upstream products
  were fitted on all 819 development members.
- Results describe the approved balanced splits and finite candidate matrix, not global or causal
  sensitivity. Site identity is provenance rather than a ranking term.
- `/xdisk` is temporary and unbacked. No stable SR release or catalog exists.
- Campaign-plan amendment recommendation: `none`.

## Explicit Terminal Declaration

Iter009 is complete and no job is active or unaccounted. No next iteration proposal is authorized.
Any all-819 SR fit, robustness/uncertainty, release, fixed-test evaluation, full-chain likelihood,
MCMC, or later work requires a separate planning discussion and consolidated kickoff approval.

## Next Session Start Protocol

1. Read `PLAN.md`, this handoff, `WORKFLOW.md`, and `iterations/iter009.md`.
2. Read `summaries/iter009/summary.md` and verify external final hashes if needed.
3. Read `development/hpc/puma.md` before any scheduler work.
4. Treat later work as planning-only until a new complete package is approved.

## Closeout Identity

- Four-record validator: `development/three_stage_surrogate/slurm/iter009/validate_closeout_iter009.sh`
- Expected validator result: `ITER009_FOUR_RECORD_VALIDATE_PASS`
- Closeout mode: `committed`; expected parent `2b22a3ec11fd8935bc7b434357ead6acc8449252`;
  expected subject `Select SR surrogate configuration`; no push authorized.
