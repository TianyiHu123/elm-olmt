# Iter015 compact summary

- Closed: `2026-11-19T03:42:13-07:00`; status `completed`; work type `experiment`.
- Plan SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`;
  alignment `aligned`; approved deviation `none`; amendment recommendation `none`.
- Result: `pass`; decision `full_chain_robustness_characterized`.
- Scope: 20 synchronized ABBY/JERC fold-specific spinup -> GPP -> SR chains, each with 655
  development training and 164 held-out validation members, train-only scalers, and
  `hard_zero_v1` in physical units before every SR input.
- Validation: pooled held-out mean GPP hourly/daily R2 `0.929685/0.897078` and RMSE
  `3.668057/2.063302`; SR hourly/daily R2 `0.802874/0.808664` and RMSE
  `0.919953/0.887979`.
- Gate: mean pooled hourly/daily gated-minus-raw R2 `+0.004582/+0.011979`; mean
  raw-minus-gated RMSE `+0.115088/+0.111132`. Some daily split differences are slightly negative.
- Uncertainty: member-balanced pooled C/N--GPP, C/N--SR, and GPP--SR error correlations are
  `0.468836`, `0.530589`, and `0.769234`; ABBY/JERC C--N log-error correlations are
  `0.990145/0.994552`.
- Accounting: jobs `24700507`, `24700675`, all 19 leaves under `24711922`, `24717714`, and
  `24717815` completed `0:0` without retry or cancellation. Peak production MaxRSS was
  `38478540K`; retained root is 26 GiB.
- Review: independent read-only review passes scientific and technical acceptance. Twenty-three
  spinup L-BFGS max-iteration warnings across 14 production leaves remain diagnostic and
  non-failing under the frozen gate; GPP/SR warnings are zero.
- Evidence: 29 product files (28 hashed products plus manifest), three handoff files, exactly
  three approved figures, and final report SHA-256
  `fed360f89b181dfb70166cdf05b18b91deb167737d022a9f6369cc0641dee2b6`.
- Boundary: development-only, two sites, overlapping validation sets, no fixed-test access,
  all-development fit, release modification, cross-fitting, tuning, plan edit, push, or merge.
- Iter015 is terminal. No next iteration is proposed or authorized.
