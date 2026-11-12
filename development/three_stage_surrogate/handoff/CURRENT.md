# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current locked SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable phase: progression item 6, SR development and configuration selection
- Alignment: `aligned`; approved deviation: `none`

## Last Closed Iteration

- Last closed iteration: `iter011`
- Status: `completed`
- Phase: `closed`
- Work type: `experiment`
- Run slug: `three_stage_surrogate_iter011_abby_jerc_sr_capacity_regularization`
- Closed: `2026-11-11T18:37:48-07:00`
- Site profile: `development/hpc/puma.md`
- Active job scope: none; no job is active or unaccounted

## Completed Objective and Decision

- Completed objective: compare exactly five locked SR capacity/regularization configurations on
  20 new matched development splits using the fixed 44-feature, fixed-upstream interface.
- Acceptance result: `pass`.
- Decision: `sr_capacity_regularization_configuration_selected`.
- Selected development candidate: B, `(96,48)`, `tanh`, alpha `0.01`, with the frozen Iter010 Adam
  controls. It won mean pooled daily validation RMSE at `0.769154`; no tie-breaker was needed.
- Interpretation: weaker regularization is supported in both matched capacity contrasts; increased
  capacity is not supported. The alpha-0.1 result is non-monotonic.
- Historical boundary: Iter010's candidate-19 decision remains unchanged. B is a development
  candidate for later fresh robustness, not a released production model.

## Evidence and Limitations

- Unit1 job `24607609` failed pre-substantively; corrected `24607628` completed `0:0`.
- Production array `24607646_0-99` contains exactly 100 task records, all `COMPLETED 0:0`, and all
  leaf identity, replay, coverage, warning, cleanup, and prohibited-scope gates pass.
- Final `24617562` failed only at the incompatible plotting keyword after CSV aggregation. Under
  fresh approval, the exact keyword correction was independently reviewed; corrected final
  `24617685` completed `0:0` and independently recomputed all 600 validation rows.
- B versus A/D improves mean daily RMSE by 11.1%/3.4%. Mean site RMSE improves at ABBY and JERC,
  but B versus D wins only 11/20 ABBY and 12/20 JERC site-split pairs.
- B's pooled daily train-validation RMSE gap is `0.452906` and RMSE SD is `0.128813`; it does not
  cross the locked instability flag but is less stable than A/C.
- Evidence is fixed-upstream, two-site, finite-matrix, and development-only. No fixed-test access,
  all-819 SR fit, uncertainty, release, catalog, likelihood/MCMC, or push occurred.
- Campaign-plan amendment recommendation: `none`.

## Terminal Direction

No next iteration is authorized. Recommended next step, only after a separate planning discussion
and consolidated kickoff approval, is fresh SR robustness validation of B with explicit attention to
split stability, train-validation gaps, and both-site consistency before any release decision.

## Next Session Start Protocol

1. Read `PLAN.md`, `WORKFLOW.md`, this handoff, and `iterations/iter011.md`.
2. Treat all Iter011 jobs as terminal and preserve both classified failures and corrected attempts.
3. Require a new consolidated kickoff approval before scheduler, retry, directory, or commit action.

## Artifact References

- Report: `development/three_stage_surrogate/iterations/iter011.md`
- Canonical material: `development/three_stage_surrogate/slurm/iter011/`
- Compact evidence: `development/three_stage_surrogate/summaries/iter011/`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter011_abby_jerc_sr_capacity_regularization`
