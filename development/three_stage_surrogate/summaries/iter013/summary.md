# Iter013 Closeout Summary

- Iteration/work type: `iter013` / `implementation`.
- Objective/result: characterize the frozen Iter012 arm-B SR model on 20 fresh development-only
  splits, publish descriptive uncertainty, fit all 819 development members, and publish
  `sr_abby_jerc/release_0001`; `pass`.
- Decision: `sr_release_published`. Stable catalog-last release contains artifact
  `8dd06c29...3fb2`, 819-member handoff `3704cab6...d3a1`, and validated 17-file manifest
  `3a3d3faf...ed4c`.
- Frozen design: 44 features ending in published predicted same-hour GPP; `(96,48)`, tanh,
  alpha `0.01`, unchanged Adam controls; 20 seed-20261116 synchronized 655/164 splits; zero fixed-test
  access and zero convergence warnings.
- Interpretation: evidence is descriptive `fixed_upstream_sr_stage`, not end-to-end uncertainty.
  Published C/N and GPP inputs are fixed all-development upstream predictions;
  `performance_gate_applied=false`.

## Descriptive robustness evidence

Values summarize 20 validation repetitions. Bias is SR prediction minus ELM truth.

| Site / resolution | Mean R2 | Median R2 | Mean RMSE | Median RMSE | Mean MAE | Mean bias |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ABBY hourly | 0.787659 | 0.792766 | 0.619354 | 0.624377 | 0.326321 | 0.005382 |
| ABBY daily | 0.791686 | 0.796921 | 0.601427 | 0.605701 | 0.301888 | 0.005382 |
| JERC hourly | 0.801176 | 0.797382 | 0.999404 | 1.021441 | 0.544472 | 0.042716 |
| JERC daily | 0.807085 | 0.802833 | 0.957565 | 0.981544 | 0.491562 | 0.042716 |
| pooled hourly | 0.839425 | 0.838772 | 0.832632 | 0.845475 | 0.435397 | 0.024049 |
| pooled daily | 0.845276 | 0.844111 | 0.800984 | 0.812739 | 0.396725 | 0.024049 |

- Products include 240 train/validation metric rows, 168 cross-split summaries, 30 locked
  train-validation gap summaries, and 84 site/resolution uncertainty rows. Full residual standard
  deviations, linear residual quantiles, coverage, and provenance remain in the release. Repository
  CSV copies are LF-normalized; the release manifest preserves authoritative external hashes.
- Release validation proved an exact all-819 fit, complete 44-feature artifact/scalers/schema,
  `100442160` finite predictions, complete scaled and raw standalone replay, exact spinup and GPP
  release/handoff identities, and byte-identical staging/stable trees.
- Stable publication:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/sr_abby_jerc/release_0001`.
  Catalog `3b12ec20...a056` was written last and points to manifest `3a3d3faf...ed4c`.
- Accounting: Unit1 `24666357`, all 20 robustness leaves under `24666388`, aggregate `24667839`,
  release fit `24667881`, and final validation/publication `24668984` completed `0:0`. No retry or
  cancellation occurred.
- Limitations: two sites; overlapping repeated validation sets; fixed in-sample upstream C/N and
  GPP; all-819 release predictions are in-sample; `/xdisk` is temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is proposed or authorized; the
  complete spinup to GPP to SR inference engine remains outside Iter013.
