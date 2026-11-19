# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current and Iter015 locked SHA-256:
  `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`
- Applicable phase: progression item 7, ABBY/JERC full-chain robustness
- Alignment: `aligned`; approved deviation: `none`
- GPP policy: `hard_zero_v1`; existing releases and historical iterations remain unchanged
- Campaign-plan amendment recommendation: `none`

## Closed State

- Last closed iteration: `iter015`
- Status: `completed`
- Phase: `closed`
- Work type: `experiment`
- Acceptance result: `pass`
- Decision: `full_chain_robustness_characterized`
- Closed: `2026-11-19T03:42:13-07:00`
- Active iteration: none
- Active job scope: none; no job is active or unaccounted
- Active monitoring: none
- Site profile: `development/hpc/puma.md`

## Result

Twenty synchronized ABBY/JERC fold-specific chains passed all immutable technical, provenance,
leakage, numerical, scientific-product, accounting, and independent review gates. Every split used
655 development training and 164 held-out validation members, train-only scalers, predicted C/N,
and physical-unit `maximum(gpp_raw, 0)` before GPP entered SR. No performance threshold applied.

- Pooled held-out mean GPP hourly/daily R2: `0.929685/0.897078`; RMSE:
  `3.668057/2.063302`.
- Pooled held-out mean SR hourly/daily R2: `0.802874/0.808664`; RMSE:
  `0.919953/0.887979`.
- Mean pooled hourly/daily gated-minus-raw GPP R2: `+0.004582/+0.011979`; mean
  raw-minus-gated RMSE: `+0.115088/+0.111132`. Some daily split effects are slightly negative.
- Equal-member pooled C/N--GPP, C/N--SR, and GPP--SR error correlations:
  `0.468836/0.530589/0.769234`.

## Accounting and Validation

- Unit1 `24700507`, pilot `24700675`, all 19 production leaves under `24711922`, aggregate
  `24717714`, and final `24717815` completed `0:0`; no retry, rejection, cancellation, or
  unaccounted work remains.
- Peak production batch MaxRSS was `38478540K` of 80 GB. The retained external root is 26 GiB,
  below the approved 100-GiB closeout cap.
- Twenty-three spinup L-BFGS max-iteration warnings across 14 production leaves are retained as
  non-failing diagnostic provenance under the frozen Iter004 rule; GPP and SR warnings are zero.
- Independent read-only result review passes scientific and technical acceptance. Its final
  records-only concern was resolved by synchronizing the production/final ledger wording.
- Final validation report SHA-256:
  `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
- Products manifest SHA-256:
  `293277a89bfa55bed100bf2e00476d26c39614e22dfb1a81eb3953c823df77e9`.
- Products contain exactly 28 hashed aggregate products plus the manifest, including exactly
  `error_propagation.png`, `gpp_gate_comparison.png`, and `gpp_sr_joint.png`; handoff has three
  files. The six joint-density panels are 200x200 unit-mass grids.

## Scope Boundary and Limitations

- Evidence is development-only for ABBY/JERC, with overlapping repeated validation membership
  and direct sequential downstream training.
- No fixed-test access, all-development fit, hyperparameter search, cross-fitting, extra feature
  or gate experiment, nine-site expansion, release modification, MCMC change, plan amendment,
  push, or merge occurred.
- This characterizes held-out full-chain robustness and error propagation; it does not publish a
  final all-development artifact or make fixed-test/general nine-site claims.
- External `/xdisk` storage is temporary and unbacked.

## Artifact References

- Report: `development/three_stage_surrogate/iterations/iter015.md`
- Compact evidence: `development/three_stage_surrogate/summaries/iter015/`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter015/`
- External root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter015_abby_jerc_full_chain_robustness`
- Products: `<external root>/products`
- Downstream uncertainty handoff: `<external root>/handoff`

## Next Action

None within Iter015. Iter015 is terminal. No next iteration is proposed or authorized. Any
fixed-test evaluation, all-development refit, release, expansion, or downstream inference requires
a new user-directed planning proposal and explicit approval.
