# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Locked SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`
- Completed phase: progression item 8, ABBY/JERC all-development refit and fixed test
- Alignment: `aligned`; approved deviation: `none`; amendment recommendation: `none`

## Live State

- Active iteration: none; latest closed iteration is `iter016`
- Status: `completed`
- Phase: `closeout`
- Decision: `coupled_release_published`
- Active job scope: none
- Active monitoring: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-20T15:31:57-07:00`

## Published Coupled Release

- Stable root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/three_stage_abby_jerc`
- Release: `release_0001`; 26 payload files; validated manifest SHA-256
  `4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a`
- Catalog SHA-256: `89a636b98b3866d6721e663c5b7ee3a9a7698248c8355dde0d9d4fe1fd4285da`
- Publication: staging and stable trees are byte-identical; catalog written last; retained stable
  footprint 215 MiB; storage is temporary and unbacked `/xdisk`.
- Training provenance: exact 819 development members, frozen 25/43/44 schemas and configurations,
  direct sequential predicted-upstream training, `hard_zero_v1`; zero fixed-test fit/selection use.
- Inference: `model_ELM.three_stage_coupled_release.CoupledThreeStageInference`; ABBY/JERC,
  canonical 18-parameter order/constraints, seven forcing variables, no-leap calendar, 720-hour
  history, target-free direct/chunk replay validated.
- Uncertainty: exact Iter015 development-only handoff/product/validation identities retained;
  no fixed-test recalibration or refit.
- Historical spinup/GPP/SR `release_0001` manifests and catalogs remain unchanged.

## Fixed-Test Result

- Exact 205 fixed-test members, ABBY/JERC, 61,320 hours each; inference excluded ELM targets and
  evaluation joined them separately. Report SHA-256
  `abb6dd67e19dc5a68691131f839cbf753781596459a5548d01b70fd7c0f850d4`.
- Pooled physical TOTSOMC/TOTSOMN R2: `0.841217/0.846365`; natural-log R2:
  `0.857511/0.857951`.
- Pooled GPP hourly/daily R2: `0.925137/0.887714`; RMSE `3.752852/2.141947`; bias
  `0.189651/0.189651 gC/m^2/day`.
- Pooled SR hourly/daily R2: `0.831429/0.837068`; RMSE `0.855186/0.825501`; bias
  `0.031435/0.031435 gC/m^2/day`.
- GPP gate: pooled hourly raw-to-gated R2 `0.923012 -> 0.925137`, RMSE
  `3.805745 -> 3.752852`; exact physical binary gate passed.
- Scientific limitation: 128,246 of 25,141,200 SR predictions (`0.5101%`) are negative, minimum
  `-2.2393017 gC/m^2/day`. No SR gate was approved; release records disclose this without tuning.
- No performance threshold was applied and no configuration changed after viewing the result.

## Accounting and Failure Classification

- Unit1 `24725402`: `COMPLETED 0:0`; 34 s; 4 CPUs/20 GB; MaxRSS `1052608K`.
- Full refit `24725445`: `FAILED 1:0`; 7h14m12s; 16 CPUs/80 GB; MaxRSS `43654448K`.
  All fits/artifacts/predictions completed; only bounded replay failed because full forcing/time was
  passed to a prefix interface. Attempt 1 remained immutable.
- Approved recovery validation `24729103`: `COMPLETED 0:0`; 25 s; accepted attempt 1 without
  refitting after the prefix-only correction and independent review.
- Fixed test `24729214`: `COMPLETED 0:0`; 2m04s; 8 CPUs/40 GB; MaxRSS `3149304K`.
- Candidate release `24729323`: `COMPLETED 0:0`; 17 s; 4 CPUs/20 GB; `published=false`.
- Final publication `24740188`: `COMPLETED 0:0`; 31 s; 8 CPUs/40 GB; MaxRSS `1738836K`;
  final report `18a05fa0...97f8` and independent result review pass.
- No retry or cancellation was used. Every job is terminal and accounted; no job is active.

## Closeout and Next Direction

- Compact evidence: `development/three_stage_surrogate/summaries/iter016/`
- Detailed report: `development/three_stage_surrogate/iterations/iter016.md`
- Closeout branch: one authorized local no-push commit with subject
  `Publish coupled three-stage surrogate release` after final validator pass.
- Iter016 is terminal. No next iteration is proposed or authorized. Any negative-SR response,
  nine-site expansion, fixed-test reuse decision, or MCMC work requires separate approval.
