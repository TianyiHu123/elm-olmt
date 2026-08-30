# ELM Diagnostic Iteration Summary

## Iter001 — failed input-interface preflight

- Objective: nine-site seed-resolved optimized `SR` diagnostic against `ppe6` control ensembles and coupling observations.
- Evidence: Puma preflight `23718019` failed `1:0` after 28 seconds; its receipt found `ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl` missing `case.output['SR']`.
- Resources: 2.41 GB/20 GB and 7.925 CPU seconds; this was not a resource failure.
- Gate result: `fail`; no substantive diagnostic, figures, metrics, or scientific conclusion.
- Decision: close failed; require a fresh package with compatible optimized historical outputs or authorized output generation.

## Iter002 — completed nine-site SR diagnostic

- Objective: the recovered nine-site, seed-resolved optimized `SR` diagnostic against the same `ppe6` control ensembles and coupling observations.
- Input gate: preflight `23723017` passed for all 60 updated `ctrlopt` pickles, nine controls, and nine SR observations using the locked receipt.
- Execution: first substantive attempt `23723072` failed only at the ABBY boxplot due to a Matplotlib `labels` API incompatibility. After user-directed minimal revision and independent re-review, retry `23723308` completed `0:0` in 2:51 (22.94/30 GB).
- Outputs: 45 PNGs (hourly, complete-day daily, monthly, UTC diurnal, and hourly distribution for every site), plus 69 hourly descriptive metric rows (60 seed-level optimized and nine control means) in the external results directory.
- Decision: accepted as a descriptive diagnostic package; no cross-site ranking, score threshold, or scientific selection conclusion was made.
