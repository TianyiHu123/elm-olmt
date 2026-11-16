# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current and active locked SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable phase: progression item 6 completion, frozen two-site SR stage and release
- Alignment: `aligned`; approved deviation: `none`
- Campaign-plan amendment recommendation: `none`

## Live State

- Last closed iteration: `iter013`
- Status: `completed`
- Phase: `closed`
- Acceptance result: `pass`
- Decision: `sr_release_published`
- Active job scope: none; no job is active or unaccounted
- Active monitoring: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-16T08:18:45-07:00`

## Result and Evidence

- Frozen release model: 44 features including published predicted same-hour GPP; `(96,48)`, tanh,
  alpha `0.01`, and unchanged Iter012 Adam controls.
- Fresh robustness: 20 seed-20261116 synchronized 655/164 development splits; all 20 leaves
  `COMPLETED 0:0`; 240 metric rows, 168 summaries, 30 gaps, and 84 uncertainty rows validated.
- Interpretation: descriptive `fixed_upstream_sr_stage`, not end-to-end uncertainty;
  `performance_gate_applied=false`; fixed-test access false.
- Stable release:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/sr_abby_jerc/release_0001`.
- Published identities: artifact `8dd06c29...3fb2`, 819-member handoff `3704cab6...d3a1`, validated
  17-file release manifest `3a3d3faf...ed4c`, catalog `3b12ec20...a056`.
- Validation: all `100442160` finite predictions passed stored/scaled/raw standalone replay;
  staging and stable trees are byte-identical; catalog was written last. Published spinup manifest
  `69f840f7...f2dc` and C/N handoff `9e2d5be4...fdb5`, and GPP manifest `57cc18b0...70d1` and
  GPP handoff `c905fc60...98bb`, are explicit. Upstream models were not retrained.
- Jobs: Unit1 `24666357`; robustness parent `24666388`; aggregate `24667839`; release fit
  `24667881`; final `24668984`. Every scope is terminal `COMPLETED 0:0`; no retry or cancellation.
- Independent review: initial Unit1 package block was corrected before execution; every corrected
  package and result review, including final publication, passed with no concerns.

## Limitations and Boundaries

- Two sites; overlapping repeated validation sets; fixed in-sample upstream predictions;
  all-development release predictions are in-sample; temporary unbacked `/xdisk` storage.
- No fixed-test access, upstream retraining, full-chain robustness, coupled inference engine,
  hyperparameter search, feature ablation, cross-fitting, nine-site expansion, MCMC change, plan
  edit, or push occurred.

## Next Action

None. Explicit terminal declaration: no next iteration is proposed or authorized. Iter014 coupled
inference remains deferred and requires a separate consolidated kickoff approval.

## Artifact References

- Report: `development/three_stage_surrogate/iterations/iter013.md`
- Compact evidence: `development/three_stage_surrogate/summaries/iter013/`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter013/`
- External run root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter013_abby_jerc_sr_release`
