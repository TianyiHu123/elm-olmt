# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Last closed iteration locked plan SHA-256:
  `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6, SR development and configuration selection
- Alignment: `aligned`
- Approved deviation: `none`
- Campaign-plan amendment recommendation: `none`

## Live State

- Active iteration: `none`
- Last closed iteration: `iter012`
- Status: `completed`
- Phase: `closed`
- Acceptance result: `pass`
- Active job scope: none; no job is active or unaccounted
- Active monitoring: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-12T15:37:51-07:00`

## Closed Runtime Authority

- Iter012 used its approved three-unit lifecycle and the required post-production checkpoint.
- Unit1 jobs `24618587` and `24621652` failed pre-substantively and were corrected within the
  approved retry boundary. Unit1 `24623717`, all 60 production leaves under parent `24623755`,
  and final job `24630916` completed `0:0`; every job is terminally accounted.
- The final package passed aggregation, independent 360-row recomputation, independent result
  review, and four-record closeout validation. No retry remains pending.
- The one authorized local closeout commit has subject `Complete SR GPP input ablation`; no push
  is authorized or performed.

## Iter012 Decision

- Decision: `deployable_arm_B_selected`.
- Frozen model: `(96,48)`, `tanh`, alpha `0.01`, unchanged Adam controls.
- Retain arm B: the deployable 44-feature configuration with published predicted same-hour GPP.
  Mean pooled daily validation RMSE is A/B/C `0.835770/0.771187/0.751254`.
- B versus A improves pooled daily RMSE by mean `0.064583` (`7.727%`), median `0.052538`, with
  `19/20` wins and no meaningful ABBY or JERC deterioration.
- C versus B improves by mean `0.019933` (`2.585%`), median `0.017654`, with `12/20` wins.
  True GPP is not substantially more informative under the frozen 5%/14-win rule.
- C versus A improves `10.112%` with `19/20` wins, showing useful GPP explanatory power. C is
  diagnostic only, non-deployable, and not a mathematical upper bound.
- Interpretation: predicted GPP provides a consistent benefit; retain the dependency. Proceed to
  separately approved fresh SR robustness testing rather than another GPP-input or architecture
  experiment.

## Boundaries and Risks

- This is fixed-upstream SR-stage validation, not full-chain held-out performance. Published
  upstream predictions used all 819 development members.
- Evidence covers ABBY/JERC and overlapping repeated validation sets only. The fixed 205-member
  test was not accessed.
- No upstream retraining, cross-fitting, all-development SR fit, release, architecture change,
  performance gate, likelihood/MCMC change, campaign-plan edit, or push occurred.
- `/xdisk` output is temporary and unbacked; compact hashes, schemas, split identities, metrics,
  plots, and validation records are retained in the repository summary package.

## Next Action

No next iteration is authorized. If desired, prepare a new consolidated kickoff package for fresh
SR robustness testing of arm B; do not initialize or execute it without explicit approval.

## Next Session Start Protocol

1. Read `PLAN.md`, `WORKFLOW.md`, this handoff, and `iterations/iter012.md`.
2. Verify the Iter012 closeout commit and compact evidence before relying on the result.
3. Treat fresh SR robustness, release fitting, fixed-test evaluation, and publication as separate
   work requiring explicit authority.

## Artifact References

- Report: `development/three_stage_surrogate/iterations/iter012.md`
- Canonical material: `development/three_stage_surrogate/slurm/iter012/`
- Compact evidence: `development/three_stage_surrogate/summaries/iter012/`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter012_abby_jerc_sr_gpp_ablation`
