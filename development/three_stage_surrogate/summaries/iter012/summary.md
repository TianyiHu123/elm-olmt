# Iter012 - SR surrogate GPP-input ablation

- Status/work type: `completed` / `experiment`
- Acceptance result: `pass`
- Decision: `deployable_arm_B_selected`; retain arm B, the 44-feature published predicted-GPP
  configuration. Arm C remains a non-deployable diagnostic and is not a mathematical upper bound.
- Frozen design: `(96,48)`, `tanh`, alpha `0.01`, unchanged Adam controls; ABBY/JERC only; 20
  matched 655/164 development splits; exactly 60 fits; fixed 205-member test excluded.

## Primary result

| Arm | GPP input | Deployable | Mean pooled daily validation RMSE | Median | SD |
| --- | --- | --- | ---: | ---: | ---: |
| A | none | yes | 0.835770 | 0.840015 | 0.097480 |
| B | published predicted same-hour GPP | yes | 0.771187 | 0.794257 | 0.089109 |
| C | true ELM same-hour GPP | no | 0.751254 | 0.763353 | 0.075623 |

- B versus A: mean RMSE improvement `0.064583` (`7.727%`), median `0.052538`, `19/20`
  pooled split wins, with no meaningful site deterioration. B passes the frozen deployable rule.
- C versus B: mean improvement `0.019933` (`2.585%`), median `0.017654`, `12/20` wins. This
  fails the frozen 5% and 14-win diagnostic threshold, so remaining GPP prediction error is not a
  substantial limiter under this design.
- C versus A: mean improvement `0.084516` (`10.112%`), median `0.070736`, `19/20` wins. Perfect
  GPP information is useful relative to no GPP, without making C deployable or an upper bound.

## Site evidence and interpretation

- ABBY daily RMSE means are A/B/C `0.607712/0.562874/0.558255`; B loses to A on `5/20`
  splits, below the deterioration rule.
- JERC daily RMSE means are A/B/C `1.010602/0.931282/0.901905`; B loses to A on `2/20`
  splits, below the deterioration rule.
- Predicted GPP provides a consistent improvement at the pooled primary endpoint and at both
  sites. True GPP adds only a small, inconsistent increment over predicted GPP. Retain the GPP
  dependency and proceed to separately approved fresh SR robustness testing; another GPP-input
  or architecture experiment is not supported by this result.

This is fixed-upstream SR-stage validation, not full-chain held-out performance. Published upstream
predictions were generated using all 819 development members. Evidence is limited to two sites and
overlapping repeated validation sets. No fixed-test access, upstream retraining, cross-fitting,
all-development SR fit, release, architecture change, performance gate, MCMC change, or push
occurred. Campaign-plan amendment recommendation: `none`. No next iteration is authorized by this
closeout; robustness work requires its own consolidated kickoff approval.

Accounting: Unit1 jobs `24618587` and `24621652` failed pre-substantively; corrected Unit1
`24623717`, all 60 leaves under production parent `24623755`, and final `24630916` completed
`0:0`. Independent result validation reproduced all 360 validation rows and the decision.
Repository CSV copies are LF-normalized; `evidence.sha256` preserves both their repository hashes
and the authoritative external CRLF artifact hashes.
