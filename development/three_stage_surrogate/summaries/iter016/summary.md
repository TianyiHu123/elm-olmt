# Iter016 compact summary

- Closed: `2026-11-20T15:31:57-07:00`; status `completed`; work type `release`.
- Plan SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`;
  alignment `aligned`; approved deviation `none`; amendment recommendation `none`.
- Result: `pass`; decision `coupled_release_published`.
- Fit: frozen direct-sequential spinup -> predicted C/N -> GPP -> physical-unit `hard_zero_v1`
  -> SR chain fitted once on all 819 development members. Exactly zero fixed-test members or
  targets entered fitting, scaling, feature selection, configuration selection, or uncertainty.
- Recovery: refit job `24725445` completed all models and predictions but failed its bounded replay
  on a full-axis/prefix interface mismatch. Approved validation-only job `24729103` applied the
  prefix correction, preserved attempt 1 byte-for-byte, and accepted the artifacts without refit.
- Fixed test: job `24729214` performed target-free inference for exact ABBY/JERC, 205-member split
  order, and 61,320 hours, then joined ELM targets separately. Pooled physical TOTSOMC/TOTSOMN R2
  is `0.841217/0.846365`; natural-log R2 is `0.857511/0.857951`.
- Flux performance: pooled GPP hourly/daily R2 `0.925137/0.887714`, RMSE
  `3.752852/2.141947`, MAE `1.582358/1.001186`, bias `0.189651/0.189651`; pooled SR R2
  `0.831429/0.837068`, RMSE `0.855186/0.825501`, MAE `0.423618/0.387435`, bias
  `0.031435/0.031435`. No performance threshold was applied.
- GPP gate: pooled hourly raw -> gated R2 `0.923012 -> 0.925137` and RMSE
  `3.805745 -> 3.752852`; 835,227 raw hourly values were negative. The frozen release policy
  remains `hard_zero_v1`.
- Limitation: 128,246 of 25,141,200 fixed-test SR predictions (`0.5101%`) are negative, minimum
  `-2.2393017 gC/m^2/day`. The approved contract has no SR gate; this is disclosed without
  post-hoc alteration or tuning.
- Release: candidate job `24729323` and final job `24740188` passed independent review. Stable
  `three_stage_abby_jerc/release_0001` has 26 hash-inventoried payloads; validated manifest
  `4bdc91e2...543a`; catalog `89a636b9...85da`; staging and stable trees are byte-identical and
  the catalog was written last. Historical spinup/GPP/SR releases and catalogs remain unchanged.
- Uncertainty: exact Iter015 handoff/product/validation identities are linked with their original
  development-only provenance and limitations; no fixed-test uncertainty refit occurred.
- Accounting: Unit1 `24725402`, recovery `24729103`, fixed test `24729214`, candidate release
  `24729323`, and final `24740188` completed `0:0`; refit `24725445` failed `1:0` and is fully
  classified. No job is active or unaccounted; no cancellation or scheduler retry was used.
- Evidence: exact fixed-test metric tables, fixed-test/final reports, published manifest, and
  catalog are retained in this directory. Repository CSV copies use normalized LF line endings;
  authoritative external hashes remain in `fixed_test_report.json`. External run root is 2.0 GiB;
  stable release is 215 MiB.
- Boundary: ABBY/JERC only; no hyperparameter tuning, cross-fitting, ablation, robustness rerun,
  nine-site expansion, MCMC work, plan amendment, push, or merge.
- Iter016 is terminal. Any scientific response to negative SR or expansion requires separate
  approval; this frozen fixed-test evaluation must not be redefined.
