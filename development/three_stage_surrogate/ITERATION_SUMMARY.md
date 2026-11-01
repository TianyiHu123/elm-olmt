# Three-Stage Surrogate Iteration Summary

## iter001 - ABBY/JERC data initialization

- Closed: `2026-10-27T05:39:17-07:00`
- Status/work type: `completed` / `data_initialization`
- Objective: initialize and validate reusable ABBY/JERC surrogate input data without training.
- Bounded scope: exact declared parameter design, ABBY/JERC transferred transient pickles and
  spinup targets, 2018--2024 forcing, site surface data, named-variable NetCDF preparation,
  deterministic 819/205 global member split, independent validation, and catalog-last publication.
- Acceptance result: `pass`.
- Decision: publish immutable snapshot `r0001` for ABBY/JERC and proceed only to the planning-only
  Iter002 direct three-stage prototype proposal. No training or fixed-test use occurred.
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`.
- Headline evidence: ABBY and JERC each contain 1,024 members and 61,320 aligned no-leap hours;
  18 named parameter variables; development/fixed-test counts 819/205; validation result
  `VALIDATE_SURROGATE_INPUT_OK`; catalog references snapshot `r0001`.
- Accounting: preflight `24430059`, preparation `24430075`, and validation `24430091` completed
  `0:0`; two rejected preflight submissions were cancelled before execution and terminally
  accounted.
- Summary evidence: `development/three_stage_surrogate/summaries/iter001/`.
- Limitations: two sites only; no models trained; published `/xdisk` data are temporary storage;
  later additions require immutable new artifacts plus a new snapshot revision.
- Campaign-plan amendment recommendation: `none`.
- Next iteration: planning-only Iter002 two-site prototype using development members exclusively;
  fresh consolidated kickoff approval is required.

## iter002 - ABBY/JERC spinup baseline

- Closed: `2026-10-29T05:40:50-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: implement and validate a development-only pooled spinup C/N baseline; `pass`.
- Final baseline: fixed 25-feature schema, separate natural-log-target `(32,)` MLPs, 655/164
  development split, positive physical predictions, and non-release artifact
  `4c42e818e124a2f72ed54635ae02979afeb7ec10518c15be187b8775e6947064`.
- Performance: pooled validation R2 C/N is `0.6704/0.6696` physical and `0.6880/0.6857` log;
  JERC log R2 is `0.5914/0.5901`, with negative pooled physical bias.
- Validation/accounting: flexible 1/7/20/164 prediction, fresh reload, identity, positivity,
  package, fixed-test-exclusion, and corrected-test gates passed. Jobs `24450843`, `24450974`,
  `24451007`, `24453838`, and `24453852` completed `0:0`; failed smoke `24450877` is preserved.
- Decision: `optimization_recommended`; no all-819 fit/prediction, release, GPP/SR work, fixed-test
  use, or push occurred.
- Evidence: `development/three_stage_surrogate/summaries/iter002/`.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter003 bounded spinup-configuration experiment; fresh consolidated
  kickoff approval is required.

## iter003 - ABBY/JERC spinup MLP configuration experiment

- Closed: `2026-10-30T15:15:56-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: select and freeze a spinup MLP configuration from 96 candidates using 20
  shared 655/164 development-only splits; `pass`.
- Decision: freeze candidate 74—`(64,32)`, `tanh`, alpha `10`, L-BFGS, `max_iter=800`, seed
  `42`—for an all-819 development refit and artifact handoff.
- Performance: winner median mean pooled validation log R2 is `0.8910`, versus `0.8015` for the
  Iter002 baseline; paired mean improvement is `+0.07655`; all four site/target median deltas are
  positive. Its 27 convergence warnings are nonfatal but remain explicit release evidence.
- Validation/accounting: all 96 production leaves, preflight `24472427`, smoke `24472428`,
  aggregation `24475235`, and independent validation `24475275` completed `0:0`; both aggregation
  and validation selected candidate 74; no retries occurred.
- Boundary/evidence: no fixed-test access, all-819 fit, or model artifact; compact evidence is in
  `development/three_stage_surrogate/summaries/iter003/` and full ranking/logs remain under the
  external run root.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter004 frozen all-819 development refit, artifact publication, and
  predicted-C/N handoff; fresh consolidated kickoff approval is required.

## iter004 - ABBY/JERC spinup robustness and release

- Closed: `2026-10-31T04:59:22-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: characterize frozen candidate 74 on fresh development-only splits, publish its
  surrogate-error component, refit on all 819 development members, and release its artifact plus
  predicted-C/N GPP handoff; `pass`.
- Robustness: 20 synchronized 655/164 splits; 6,560 paired observations; 168 metric rows; 22/40
  nonfatal convergence warnings. Cross-repetition log R2 is ABBY C/N `0.8931/0.8899` and JERC C/N
  `0.8053/0.8011`; full distributions and quantiles are retained.
- Uncertainty: member-balanced `1/k`, normalized, population-`ddof=0` site-specific paired log-error
  products passed finite/symmetry/PSD gates. C/N correlations are `0.9775` for ABBY and `0.9883`
  for JERC; minimum covariance eigenvalues are `0.00298/0.00287`.
- Release: artifact `9abb342d...a809`; 819-member predicted-C/N handoff `9e2d5be4...fdb5`;
  independently validated 14-file manifest `69f840f7...f2dc`; fixed-test access false.
- Publication: stable catalog-last `release_0001` under
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc`.
  Run and release copies are distinct but share temporary unbacked `/xdisk` and are not backups.
- Accounting: preflight `24479223`, successful robustness `24480121`, uncertainty `24480153`,
  release fit `24480174`, and validation `24480199` completed `0:0`. Failed robustness attempt
  `24479279` stopped before fitting; its non-scientific indexing correction and exact provenance
  passed independent re-review.
- Boundary/evidence: no fixed-test, GPP/SR fitting, full-chain robustness, observation, likelihood,
  MCMC, or push. Compact evidence is in `development/three_stage_surrogate/summaries/iter004/`.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter005 GPP input/inference-interface materialization, stopping
  before GPP fitting; fresh consolidated kickoff approval is required.

## iter005 - ABBY/JERC fixed-upstream GPP baseline

- Closed: `2026-10-31T22:17:39-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: implement, fit, and independently validate one hourly-trained ABBY/JERC GPP
  baseline using the first 655 development members for fitting and the remaining 164 for
  validation; `pass` under the user-approved batch-aware reload contract.
- Model/scope: fixed 43-feature `(128,)` ReLU/Adam MLP, physical-target standardization, 29
  iterations, zero convergence warnings, 100,442,160 total rows, zero fixed-test access, and zero
  spinup execution. Validation is `fixed_upstream_gpp_stage` because published predicted C/N is
  in-sample upstream input for all 819 development members.
- Validation performance: pooled hourly R2/RMSE/MAE/bias is
  `0.911104/4.025672/2.151374/0.087570`; pooled daily is
  `0.860052/2.366163/1.393406/0.087570`. ABBY/JERC hourly validation R2 is
  `0.918870/0.904396`; daily is `0.886994/0.819122`. Full train/validation hourly/daily metrics are
  recorded in `development/three_stage_surrogate/summaries/iter005/summary.md`.
- Artifact/evidence: artifact `09820737...c31b`, predictions `74b2b133...4024`, metrics
  `5b7a40bf...172d`; revised validation `24488737` replayed three original chunks within unchanged
  `1e-6`, verified finite exact same-batch repeatability for 1/7/1,000 rows, and independently
  matched all 12 metric rows.
- Accounting: preparation `24485863`, smoke `24485909`, baseline `24485952`, and revised validation
  `24488737` completed `0:0`. Failed validation jobs `24488350`, `24488401`, `24488434`, and
  `24488468` are preserved and classified; they exposed float32 cross-batch sensitivity, leading to
  the user-approved batch-aware replay contract.
- Decision: `freeze_baseline`; perform fixed-configuration robustness next and reconsider
  optimization only if robustness evidence is poor.
- Limitations: two sites, one split, fixed in-sample upstream C/N, temporary unbacked storage, and
  no fixed-test, repeated robustness, all-819 GPP release, SR, full-chain, observational,
  likelihood, or posterior evidence.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter006 20-repeat fixed-upstream GPP robustness; fresh consolidated
  kickoff approval is required.

## iter006 - ABBY/JERC fixed-upstream GPP robustness

- Closed: `2026-11-01T04:58:32-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: test the frozen Iter005 GPP configuration on 20 balanced 655/164
  development-member splits and conditionally release only on immutable gate pass; `fail`.
- Robustness: all 20 fits and reload validators passed with zero convergence warnings, complete
  coverage, and no fixed-test access, but R2 q10 and RMSE q90 failed for ABBY/JERC at both hourly
  and daily resolution. Bias ceilings passed.
- Gate evidence: ABBY hourly/daily R2 q10 is `0.7084/0.1937` and RMSE q90 is `7.0410/6.0718`;
  JERC hourly/daily R2 q10 is `0.7560/0.0288` and RMSE q90 is `7.2607/5.9397`.
- Uncertainty: independently validated 240-row metric table, 84-row uncertainty table, and compact
  four-field `gpp_uncertainty.nc`; member-balanced hourly RMSE is `5.3187` ABBY and `5.8212` JERC.
- Decision: `optimization_required`. Preserve diagnostic products only; no all-819 GPP fit,
  artifact, predicted-GPP SR handoff, stable release, catalog, or push occurred.
- Accounting: prepare `24489883`, smoke `24489912`, all 20 robustness leaves under `24489937`,
  and final aggregate validation `24491301` completed `0:0`. Failed validator attempts `24491172`
  and `24491252` are preserved; two user-approved numerical-validation corrections were
  independently re-reviewed.
- Boundary/evidence: fixed published C/N is in-sample upstream, so claims are GPP-stage
  conditional. Compact evidence is in `development/three_stage_surrogate/summaries/iter006/` and
  full diagnostic products remain under the external Iter006 run root.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration; any GPP configuration-optimization iteration requires
  a separate planning discussion and consolidated kickoff approval.
