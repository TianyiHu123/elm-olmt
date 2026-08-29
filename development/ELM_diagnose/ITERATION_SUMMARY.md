# ELM Diagnostic Iteration Summary

## Iter001 — failed input-interface preflight

- Objective: nine-site seed-resolved optimized `SR` diagnostic against `ppe6` control ensembles and coupling observations.
- Evidence: Puma preflight `23718019` failed `1:0` after 28 seconds; its receipt found `ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl` missing `case.output['SR']`.
- Resources: 2.41 GB/20 GB and 7.925 CPU seconds; this was not a resource failure.
- Gate result: `fail`; no substantive diagnostic, figures, metrics, or scientific conclusion.
- Decision: close failed; require a fresh package with compatible optimized historical outputs or authorized output generation.
