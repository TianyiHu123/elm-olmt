# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Locked SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable phase: progression item 6, SR development and configuration selection
- Alignment: `aligned`; approved deviation: `none`

## Live State

- Active iteration: `none`
- Last closed iteration: `iter010`
- Status: `completed`
- Phase: `closed`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter010_abby_jerc_sr_refinement`
- Active job scope: none; no job is active or unaccounted
- Site profile: `development/hpc/puma.md`
- Closed: `2026-11-10T01:04:21-07:00`

## Acceptance and Decision

- Completed objective: refine the Iter009 ABBY/JERC SR surrogate configuration using the locked
  33-candidate matrix and 20 fresh development-only splits.
- Acceptance result: `pass`.
- Decision: `sr_refined_configuration_selected`.
- Selected candidate: candidate 19—hidden layers `(96,48)`, `tanh`, alpha `1.0`, and the frozen
  Adam controls.
- Replacement gate: pass; candidate 19 ranked first, improved 6/6 selection components over
  incumbent 0, and neither resolution had both worse q10 R2 and q90 RMSE.
- Finalists/order: `[0,23,19,26,11,15]`; final order `19,23,15,26,11,0`.
- Gate statistics: candidate 19 hourly R2 q10/RMSE q90/median absolute bias
  `0.773460/1.025263/0.035658`; daily `0.790604/0.967047/0.035658`.
- Fresh validation recomputed 240 rows and reproduced candidate 19, the gate, and decision.

## Evidence and Accounting

- Unit1 attempt 1 job `24578833` failed on a pre-substantive syntax error. The approved minimal
  correction passed independent re-review; attempt 2 job `24578853` completed `0:0`.
- Screen array `24579541`: all 264 tasks `COMPLETED 0:0`; independent completion review passed.
- Finalist array `24590678`: all 72 tasks `COMPLETED 0:0`; independent completion review passed.
- Final job `24595272`: `COMPLETED 0:0`; independent result review passed.
- Final hashes: metrics `6e43c47f...ffbf`, ranking `948f32df...9e5c`, selection
  `ebd1e541...edf5`, validation `4c883485...617`, execution manifest `3870eecb...2f66`.
- Four-record closeout validator: `ITER010_FOUR_RECORD_VALIDATE_PASS`.
- Closeout mode: one scoped local no-push commit was created and post-commit verified, subject
  `Refine SR surrogate configuration`.

## Scope and Boundaries

The result is fixed-upstream, two-site, development-only SR configuration evidence. Published C/N
and GPP inputs were fitted on all 819 development members, so this is not end-to-end held-out
evidence. The 205 fixed-test members were not accessed. No all-819 SR fit, uncertainty, release,
catalog, observations, likelihood, MCMC, plan edit, or push occurred. `/xdisk` is temporary and
unbacked. Campaign-plan amendment recommendation: `none`.

## Next State

Explicit terminal declaration. No next iteration is authorized. Any robustness, uncertainty,
all-819 fitting, release, fixed-test evaluation, or downstream work requires a separate planning
discussion and consolidated kickoff approval.

## Paths

- Report: `development/three_stage_surrogate/iterations/iter010.md`
- Compact evidence: `development/three_stage_surrogate/summaries/iter010/`
- Canonical material: `development/three_stage_surrogate/slurm/iter010/`
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter010_abby_jerc_sr_refinement`
