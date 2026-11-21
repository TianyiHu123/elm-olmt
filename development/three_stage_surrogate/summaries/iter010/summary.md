# Iter010 Closeout Summary

- Iteration/work type: `iter010` / `experiment`.
- Objective/result: refine the Iter009 SR configuration using a locked 33-candidate matrix and
  fresh development-only splits; `pass`.
- Decision: `sr_refined_configuration_selected`. Freeze candidate 19: hidden layers `(96,48)`,
  `tanh`, alpha `1.0`, and the frozen Adam controls. This authorizes no all-819 fit or release.
- Scope: 44 physical-SR features; fixed published predicted C/N and same-hour GPP; 819 development
  members; 20 fresh balanced 655/164 splits; zero access to the 205 fixed-test members.
- Evidence: Unit1 passed fresh-split, raw-cache, interface, contract, and smoke gates. All 264
  screen leaves and 72 finalist leaves completed `0:0`, passed serialization/coverage/hash gates,
  had zero production convergence warnings, and removed successful scaled scratch.
- Finalists/ranking: `[0,23,19,26,11,15]`; final order `19,23,15,26,11,0`. Candidate 19's
  worst/mean normalized ordinal scores are `0.6/0.833333`; the replacement gate passed with 6/6
  component improvements and neither resolution both worse than control.
- Selected gate statistics: candidate 19 hourly R2 q10/RMSE q90/median absolute bias is
  `0.773460/1.025263/0.035658`; daily is `0.790604/0.967047/0.035658`. Control 0 values are
  `0.719296/1.139500/0.061042` hourly and `0.719260/1.118734/0.061042` daily.
- Independent validation: a fresh process reread physical SR truth and hashed predictions,
  recomputed 240 metric rows, reproduced candidate 19 and the replacement decision, and confirmed
  fixed-test/release flags false. Selection report `ebd1e541...edf5`; validation
  `4c883485...617`.
- Accounting: Unit1 jobs `24578833` (failed pre-substantive syntax preflight) and `24578853`,
  screen array `24579541`, finalist array `24590678`, and final job `24595272` are fully
  accounted. Every production task and the corrected Unit1 retry completed `0:0`.
- Interpretation: `fixed_upstream_sr_stage`, not end-to-end held out. Both upstream products were
  fitted on all 819 development members. Results describe the approved splits and finite matrix,
  not global or causal sensitivity.
- Boundary: no fixed-test use, all-819 SR fit, uncertainty, release, catalog, observations,
  likelihood/MCMC, or push occurred. `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; all-819 SR fitting,
  robustness/uncertainty, release, fixed-test evaluation, or downstream work requires separate
  planning and consolidated kickoff approval.

## Finalist metric distributions

Bias is prediction minus truth. Values are across the 20 development splits using pooled ABBY/JERC
validation metrics; daily metrics aggregate the same hourly predictions over complete days.

| Candidate | Resolution | Mean R2 | Median R2 | Mean RMSE | Median RMSE | Mean signed bias | Median signed bias |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | hourly | 0.794782154 | 0.808673998 | 0.936408136 | 0.917152672 | 0.038233237 | 0.043437206 |
| 0 | daily | 0.797680211 | 0.811593045 | 0.910936127 | 0.891891129 | 0.038233237 | 0.043437206 |
| 23 | hourly | 0.803549933 | 0.809602644 | 0.923132459 | 0.909872425 | 0.012967128 | 0.007877080 |
| 23 | daily | 0.820905121 | 0.827524372 | 0.864141980 | 0.847820159 | 0.012967128 | 0.007877080 |
| 19 | hourly | 0.802100965 | 0.803757368 | 0.926387133 | 0.911468955 | 0.016204861 | -0.003935036 |
| 19 | daily | 0.819644823 | 0.823430845 | 0.867044301 | 0.852185073 | 0.016204861 | -0.003935036 |
| 26 | hourly | 0.843278022 | 0.855066693 | 0.817927333 | 0.778312890 | 0.050530160 | 0.031393559 |
| 26 | daily | 0.849459578 | 0.861587679 | 0.784806138 | 0.744500778 | 0.050530160 | 0.031393559 |
| 11 | hourly | 0.803019412 | 0.804645815 | 0.923986399 | 0.918706164 | 0.011564380 | 0.002097610 |
| 11 | daily | 0.820718881 | 0.820781736 | 0.864180064 | 0.856061789 | 0.011564380 | 0.002097610 |
| 15 | hourly | 0.800951400 | 0.803783646 | 0.929266448 | 0.917955234 | 0.018886384 | 0.003595342 |
| 15 | daily | 0.818775494 | 0.823027004 | 0.869355696 | 0.851070206 | 0.018886384 | 0.003595342 |
