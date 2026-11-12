# Iter009 Closeout Summary

- Iteration/work type: `iter009` / `implementation`.
- Objective/result: implement the pooled ABBY/JERC hourly SR interface and select the best
  technically eligible MLP from the locked 24-candidate design using development-only evidence;
  `pass`.
- Decision: `sr_configuration_selected`. Freeze candidate 21: hidden layers `(64,32)`, `tanh`,
  alpha `1e-4`, and the frozen Adam controls. This authorizes no all-819 fit or release.
- Scope: 44 features (the GPP 43 plus same-hour `GPP_predicted`), physical SR, fixed published
  C/N and GPP upstream, 819 development members, 20 balanced 655/164 splits, and zero access to
  the 205 fixed-test members.
- Evidence: all 192 screen leaves and 72 finalist leaves completed `0:0`, passed serialization and
  coverage checks, produced finite predictions, had zero convergence warnings, and removed only
  successful scaled scratch. Finalists were `[0,21,2,8,16,13]`.
- Ranking: candidate 21 ranked first with worst/mean normalized ordinal scores `1.0/1.0`.
  Hourly R2 q10/RMSE q90/median absolute bias were `0.736201/1.119896/0.027569`; daily values
  were `0.737210/1.098576/0.027569`. No absolute performance gate was applied.
- Independent validation: the fresh validator reread raw physical SR truth and hashed predictions,
  recomputed 240 metric rows, reproduced candidate 21, and confirmed fixed-test/release flags
  false. Final selection report is `4c414784...931c`; validation is `8a0138fe...967f`.
- Accounting: Unit1 `24524508`, screen `24524587`, finalists `24536618`, and final `24548424`
  completed `0:0`. No retry submission was consumed. Pre-submission reviewer blocks corrected
  attempt-path safety, Puma resource directives, and identity-gate ordering before affected jobs.
- Interpretation: `fixed_upstream_sr_stage`, not end-to-end held out. Both published upstream
  products were fitted on all 819 development members; selection distributions describe the
  approved sampled splits and finite candidate matrix, not global or causal sensitivity.
- Boundary: no fixed-test use, all-819 SR fit, uncertainty, stable release, catalog, observations,
  likelihood, MCMC, or push occurred. `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; all-819 SR fitting,
  robustness/uncertainty, release, fixed-test evaluation, or downstream work requires separate
  planning and consolidated kickoff approval.
