# iter002 compact closeout summary

- Closed: `2026-11-24T04:26:44-07:00`; status `completed`; work type
  `audit | implementation | integration | validation | release`.
- Objective: publish one immutable, MCMC-ready ABBY/JERC observation and fixed-uncertainty release
  for GPP, SR, TOTSOMC, and TOTSOMN. All nine acceptance gates pass; decision
  `observation_release_0001_published`.
- Plan: `MCMC_OPTIMIZATION_PLAN.md` SHA-256
  `b302ee65fe8938abd6a5e1bf4d0931c43a298b336acc4c4e1afd120fa2f175ab`; aligned. Historical
  Iter001 remains locked to its original plan identity.
- Release root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/observation_products/release_0001`.
  Catalog SHA-256 `cefc9666c4d958a78ec96826157968883a012bb8bc91c6f9826f52a6f9446bd8`;
  manifest `460c01d957b8e159007b08f6b0c33f43d120d77611a4eaaae7444752f5490fe2`;
  validation report `19effdb0f67daa26c8a1e2f429e2aedd2263eac11b6d5887d1c44c4716f88fef`.
- Coverage after the 720-hour history gate: ABBY/JERC GPP 514/699 days at at least 18 paired hours;
  SR 1,095/2,114 days at at least 22 valid hours. Separate masks and exact daily source-hour
  indices are published. JERC SR uses the documented 10% relative plus 0.05 absolute-floor
  fallback; ABBY retains measured `SR_err` where valid.
- GPP zero gate: raw negatives remain published; hourly gate-after-DT/NT-averaging changed
  4,043/15,771 ABBY hours (25.635660%) and 5,223/20,278 JERC hours (25.756978%). Across eligible
  days, mean gated-minus-raw impact is 0.255241 ABBY and 0.398856 JERC `gC/m^2/day`; maxima are
  1.681819 and 2.523385. Hourly-gate versus gate-after-daily comparisons are retained.
- Soil observations at 2.0 m: ABBY C/N stocks 32303.953054 `gC/m^2` and 2317.321905 `gN/m^2`;
  JERC 4944.396067 and 405.459294. Full 1,024-member PPE1 depth fractions are ABBY
  C/N 0.7092963304/0.7077317530 and JERC 0.7576875377/0.7566024347. Paired depth covariances,
  biases, Iter015 development-only surrogate covariance, and CV 0.20/0.30/0.50 total covariances
  are published and positive definite.
- Flux surrogate RMSE is reused unchanged from Iter015. Daily observation sigma is RMS over the
  retained hours with no `sqrt(n)` or `sqrt(24)` reduction. GPP/SR absolute floors are both
  0.05 `gC/m^2/day`.
- Diagnostic figures:
  `diagnostics/flux_coverage_alignment.png`, `diagnostics/gpp_zero_gate_impact.png`, and
  `diagnostics/uncertainty_components.png` under the release root; underlying tables are retained.
- Final validation reloaded 18 products; combined runtime/publication storage is 12,243,802 bytes.
  Independent pre-publication and post-publication reviews both passed. Fixed-test access for
  surrogate uncertainty is false.
- Jobs: preflight `24794462`/`24794655` failed and `24794902` passed; source audit
  `24794997`/`24795247` failed and `24795589` passed; flux `24795706` passed; uncertainty
  `24795812` passed; publication `24795941`/`24796001` failed pre-write validation and `24797797`
  passed after explicit correction authority; final validation `24797845` passed. All attempts are
  terminal and classified.
- Limitations: transferred Perlmutter processing logs are unavailable on Puma although products and
  scripts are hash-locked; Iter015 daily flux surrogate errors use full 24-hour model days while
  observed products may average 18--23 hours; the 205 fixed-test members are not independent
  evaluation data for the combined surrogate-plus-depth operator.
- Next direction: planning-only Iter003, **Complete Four-Observable Posterior Adapter and
  Validation**. It may implement and validate the PPE1 prior plus GPP/SR/TOTSOMC/TOTSOMN posterior
  adapter, but no initialization, execution, optimization, MCMC chain, or commit is authorized
  without a fresh consolidated kickoff approval.
