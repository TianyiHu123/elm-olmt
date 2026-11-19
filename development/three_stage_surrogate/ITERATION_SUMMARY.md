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

## iter007 - ABBY/JERC pooled GPP MLP configuration experiment

- Closed: `2026-11-02T22:28:22-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: select the best pooled ABBY/JERC GPP MLP configuration from a locked
  24-candidate matrix using development-only evidence; `pass`.
- Decision: `configuration_selected_gate_pass`. Freeze candidate 21—`(64,32)`, `tanh`, alpha
  `1e-4`, otherwise frozen Adam controls—for separately approved fresh robustness.
- Evidence: 24 candidates completed eight screening fits; finalists `[18,21,19,2,8,13]` completed
  all 20 fits; 120 selected leaves and 480 pooled metric rows passed independent validation and
  review. Final order is `21,18,19,2,8,13`; candidate 18 also passed but lost the worst-margin
  tie-break.
- Gate: candidate 21 hourly R2 q10/RMSE q90/median absolute bias is
  `0.904205/4.260999/0.135299`; daily is `0.829424/2.675357/0.135299`; every pooled threshold
  passes.
- Accounting: jobs `24494841`, `24494873`, all 192 leaves under `24494900`, `24506893`, all 72
  leaves under `24507062`, and `24512103` completed `0:0`. One redundant dependency submission
  was rejected before a job ID and retried unchanged; no workload failure or cancellation.
- Boundary/evidence: no fixed-test use, all-819 GPP fit, artifact, uncertainty/SR handoff, stable
  release, catalog, or push. Compact evidence is in
  `development/three_stage_surrogate/summaries/iter007/`; evidence remains fixed-upstream-stage.
- Limitations: two sites, pooled masking, fixed in-sample upstream C/N, reused selection splits,
  finite matrix, temporary unbacked storage, and no fresh-split release-qualified robustness.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter008 fresh robustness of candidate 21 on 20 new balanced splits;
  fresh consolidated kickoff approval is required and no runtime authority is granted.

## iter008 - ABBY/JERC GPP robustness and release

- Closed: `2026-11-04T01:12:26-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: characterize candidate 21 on 20 fresh balanced development splits, publish
  descriptive uncertainty, fit all 819 development members, and release the GPP artifact plus
  predicted-GPP downstream handoff; `pass`.
- Decision: `gpp_release_published`. Stable catalog-last `release_0001` contains artifact
  `67214897...8ec9`, handoff `c905fc60...98bb`, and release manifest `57cc18b0...70d1`.
- Evidence: all 20 robustness fits/reloads passed with zero warnings and fixed-test access false;
  240 metric rows and 84 uncertainty rows passed independent aggregation. Descriptive ABBY/JERC
  hourly R2 q10 is `0.908730/0.909111`; daily is `0.873134/0.811444`.
- Correction: failed final `24523438` exposed scaler replay dtype order. Reviewed diagnostics
  localized the interface defect; the correction mirrors scikit-learn float32 statistic casting.
  Corrected final `24523529` passed all 100,442,160 predictions without changing science content.
- Accounting: `24512852`, all leaves under `24513943`, `24520151`, `24523514`, and `24523529`
  completed `0:0`; failed jobs `24523438` and `24523491` are preserved and classified.
- Boundary/evidence: no fixed-test or SR fitting; upstream C/N and all-819 release predictions are
  in-sample; metrics are repeated-split descriptive rather than a release gate. Compact evidence
  is in `development/three_stage_surrogate/summaries/iter008/`.
- Limitations: two sites, fixed in-sample upstream C/N, temporary unbacked `/xdisk`, and no
  full-chain uncertainty, observations, likelihood, MCMC, or push.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; downstream SR or
  later work requires a separate planning discussion and consolidated kickoff approval.

## iter009 - ABBY/JERC SR implementation and configuration selection

- Closed: `2026-11-06T02:35:17-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: implement the fixed-upstream pooled hourly SR stage and select a configuration
  from the locked 24-candidate development-only design; `pass`.
- Decision: `sr_configuration_selected`. Freeze candidate 21: `(64,32)`, `tanh`, alpha `1e-4`,
  with the frozen Adam controls; no all-819 fit or release is authorized.
- Evidence: Unit1 passed the 44-feature physical-SR interface and raw-cache gates; all 192 screen
  and 72 finalist leaves completed `0:0` with zero production warnings and no fixed-test access.
  Fresh final validation recomputed 240 rows and reproduced candidate 21.
- Ranking: candidate 21 achieved worst/mean ordinal scores `1.0/1.0`; hourly R2 q10/RMSE q90/
  median absolute bias was `0.736201/1.119896/0.027569`, and daily was
  `0.737210/1.098576/0.027569`. No absolute performance gate was applied.
- Accounting: `24524508`, array `24524587`, array `24536618`, and `24548424` completed `0:0`;
  no retry submission was consumed. Pre-submission review blocks were corrected before execution.
- Boundary/evidence: fixed upstream C/N and GPP are in-sample; no fixed-test, all-819 SR fit,
  uncertainty, release, catalog, likelihood/MCMC, or push. Compact evidence is in
  `development/three_stage_surrogate/summaries/iter009/`.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; later SR robustness,
  release, fixed-test evaluation, or downstream work requires separate planning and approval.

## iter010 - ABBY/JERC SR configuration refinement

- Closed: `2026-11-10T01:04:21-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: refine the Iter009 SR configuration using a locked 33-candidate matrix and 20
  fresh development-only splits; `pass`.
- Decision: `sr_refined_configuration_selected`. Freeze candidate 19—`(96,48)`, `tanh`, alpha
  `1.0`, otherwise frozen Adam controls—for separately approved later work.
- Evidence: 264 screen and 72 finalist leaves passed technical and scope gates; finalists
  `[0,23,19,26,11,15]` ranked `19,23,15,26,11,0`. Fresh validation recomputed 240 rows and
  reproduced candidate 19.
- Gate: candidate 19 improved all 6/6 components over control, with no both-worse resolution.
  Hourly R2 q10/RMSE q90/median absolute bias is `0.773460/1.025263/0.035658`; daily is
  `0.790604/0.967047/0.035658`.
- Accounting: Unit1 `24578833` failed before substantive work; corrected Unit1 `24578853`, screen
  array `24579541`, finalist array `24590678`, and final `24595272` completed `0:0`.
- Boundary/evidence: fixed upstream C/N and GPP are in-sample; no fixed-test, all-819 SR fit,
  uncertainty, release, catalog, likelihood/MCMC, or push. Compact evidence is in
  `development/three_stage_surrogate/summaries/iter010/`.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; later SR robustness,
  release, fixed-test evaluation, or downstream work requires separate planning and approval.

## iter011 - Focused SR capacity versus regularization experiment

- Closed: `2026-11-11T18:37:48-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: compare five locked SR capacity/regularization configurations on 20 new matched
  development-only splits; `pass`.
- Decision: `sr_capacity_regularization_configuration_selected`. Select B—`(96,48)`, `tanh`,
  alpha `0.01`, otherwise frozen Iter010 Adam controls—as a development candidate for separately
  approved fresh robustness; no release is authorized.
- Evidence: all 100 production fits passed. Mean pooled daily validation RMSE ranks B, D, C, A, E
  at `0.7692`, `0.7961`, `0.8640`, `0.8657`, `0.8895`; fresh validation recomputed 600 rows.
- Effects: weaker regularization is supported by B/A (18/20 RMSE wins) and D/C (16/20); capacity
  is not supported because C/A is nearly neutral and D loses to B. Alpha `0.1` is non-monotonic.
- Diagnostics: B improves mean daily RMSE at both ABBY and JERC versus A and D, with no site-cost
  flag, but has larger train-validation gaps and greater split variability than A/C.
- Accounting: Unit1 `24607609` failed pre-substantively and corrected `24607628` completed `0:0`;
  array `24607646_0-99` completed `0:0`; final `24617562` failed at a Matplotlib keyword and the
  exactly corrected final `24617685` completed `0:0`. Both corrections had independent re-review.
- Boundary/evidence: fixed predicted upstream C/N and GPP, two sites, and development-only splits;
  no fixed-test, all-819 SR fit, uncertainty, release, catalog, likelihood/MCMC, or push.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; fresh B robustness
  requires a separate planning discussion and consolidated kickoff approval.

## iter012 - SR surrogate GPP-input ablation

- Closed: `2026-11-12T15:37:51-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: test SR dependence on same-hour GPP using no-GPP A, published predicted-GPP B,
  and true-ELM-GPP diagnostic C with the frozen `(96,48)` tanh alpha `0.01` model; `pass`.
- Decision: `deployable_arm_B_selected`. Retain B and its predicted-GPP dependency; C remains
  non-deployable and is not a mathematical upper bound.
- Primary evidence: mean pooled daily validation RMSE is A/B/C
  `0.835770/0.771187/0.751254`. B versus A improves by `7.727%`, median absolute improvement
  `0.052538`, with `19/20` wins and no meaningful site deterioration.
- Diagnostic evidence: C versus B improves only `2.585%`, median `0.017654`, with `12/20`
  wins, failing the frozen 5%/14-win threshold. C versus A improves `10.112%` with `19/20`
  wins, so GPP carries useful information but remaining GPP error is not a substantial limiter.
- Sites: daily RMSE A/B/C is `0.607712/0.562874/0.558255` at ABBY and
  `1.010602/0.931282/0.901905` at JERC. B loses to A on only `5/20` and `2/20` site splits.
- Accounting: Unit1 `24618587` and `24621652` failed pre-substantively; corrected Unit1
  `24623717`, all 60 leaves under `24623755`, and final `24630916` completed `0:0`.
  Independent validation reproduced all 360 validation rows and the decision.
- Boundary/evidence: fixed-upstream, two-site, development-only validation; no fixed-test,
  upstream retraining, cross-fitting, all-819 SR fit, release, architecture change, performance
  gate, MCMC change, or push. Compact evidence is in
  `development/three_stage_surrogate/summaries/iter012/`.
- Campaign-plan amendment recommendation: `none`.
- Next state: explicit terminal declaration. No next iteration is authorized; separately approved
  fresh SR robustness is recommended instead of another GPP-input or architecture experiment.

## iter013 - ABBY/JERC SR robustness and release

- Closed: `2026-11-16T08:18:45-07:00`.
- Status/work type: `completed` / `implementation`.
- Objective/result: characterize frozen Iter012 arm B on 20 fresh fixed-upstream development
  splits, publish descriptive uncertainty, fit all 819 development members, and publish validated
  SR `release_0001`; `pass`.
- Decision: `sr_release_published`; artifact `8dd06c29...3fb2`, 819-member handoff
  `3704cab6...d3a1`, and 17-file release manifest `3a3d3faf...ed4c` passed complete scaled/raw
  replay and catalog-last publication.
- Robustness: pooled validation hourly/daily mean R2 `0.839425/0.845276`, mean RMSE
  `0.832632/0.800984`, and mean bias `0.024049/0.024049`. The release retains all ABBY, JERC,
  pooled, hourly/daily metrics, residual quantiles, gaps, and 84 uncertainty rows.
- Boundary: `fixed_upstream_sr_stage`, not end-to-end uncertainty; no performance gate, fixed-test
  access, upstream retraining, full-chain robustness, coupled inference, MCMC, or push.
- Publication: stable catalog-last `sr_abby_jerc/release_0001`; exact published spinup and GPP
  release/handoff identities; 100,442,160 finite all-development predictions.
- Accounting: `24666357`, all 20 tasks under `24666388`, `24667839`, `24667881`, and `24668984`
  completed `0:0`; no retry or cancellation occurred.
- Evidence: `development/three_stage_surrogate/summaries/iter013/`.
- Limitations: two sites, overlapping repeated validation sets, fixed in-sample upstream features,
  in-sample release predictions, and temporary unbacked `/xdisk` storage.
- Campaign-plan amendment recommendation: `none`.
- Next direction: explicit terminal declaration; no next iteration is proposed or authorized.

## iter014 - ABBY/JERC coupled inference engine and diagnostics

- Closed: `2026-11-17T15:21:18-07:00`.
- Status/work type: `completed` / `integration`.
- Objective/result: implement and validate the frozen spinup -> GPP -> SR engine and four
  development-only scientific diagnostics without fitting any model; `pass`.
- Decision: `three_stage_inference_ready_for_robustness`; the callable engine passed exact schema,
  provenance, validation, bounded handoff replay, strict direct/chunk, and serialization gates.
- Integration: nine locked development members, ABBY/JERC, and early/middle/late 48-hour windows;
  counts C/N `18/18`, GPP/SR `2592/2592`; maximum handoff differences C `2.037268e-10`, N
  `1.818989e-11`, GPP `5.340576e-05`, SR `4.768372e-06`.
- Diagnostics: exact all-development descriptive metrics, pooled/ABBY/JERC density parity,
  GPP-SR joint density/Pearson structure, and paired locked-bin conditional summaries with separate
  night/near-zero accounting; four figures passed independent visual and numerical validation.
- Accounting: preflight `24678619`, `24678718`, `24678814` failed and `24678875` passed;
  integration `24678937`, `24680350` failed and `24680395` passed; diagnostics `24680459` and
  `24680504` and final `24691748` completed `0:0`. Every failure is classified; no cancellation.
- Boundary: no training, fixed-test access, full-819 engine chain, full-chain robustness or
  uncertainty, release edit, extra site, MCMC, plan amendment, or push.
- Evidence: `development/three_stage_surrogate/summaries/iter014/`.
- Limitations: two sites; frozen in-sample development releases; diagnostics are descriptive, not
  causal confirmation, held-out end-to-end performance, or full-chain uncertainty; temporary
  unbacked `/xdisk` storage.
- Campaign-plan amendment recommendation: `none`.
- Next direction: explicit terminal declaration; no next iteration is proposed or authorized.

## iter015 - ABBY/JERC full-chain robustness with hard-zero GPP

- Closed: `2026-11-19T03:42:13-07:00`.
- Status/work type: `completed` / `experiment`.
- Objective/result: train and evaluate 20 synchronized fold-specific ABBY/JERC spinup -> GPP ->
  SR chains with physical-unit `hard_zero_v1`; `pass`.
- Decision: `full_chain_robustness_characterized`; publish the validated development-only
  robustness and uncertainty handoff. No all-development refit or release is authorized.
- Performance: pooled held-out mean GPP hourly/daily R2 `0.929685/0.897078` and RMSE
  `3.668057/2.063302`; SR hourly/daily R2 `0.802874/0.808664` and RMSE
  `0.919953/0.887979`. No performance threshold was applied.
- Gate: mean pooled hourly/daily gated-minus-raw R2 `+0.004582/+0.011979` and
  raw-minus-gated RMSE `+0.115088/+0.111132`; some daily split comparisons are slightly negative.
- Uncertainty: equal-member pooled C/N--GPP, C/N--SR, and GPP--SR error correlations are
  `0.468836/0.530589/0.769234`; exactly three approved figures and the complete covariance,
  propagation, gate, gap, depth, and joint-density products passed final validation.
- Accounting: jobs `24700507`, `24700675`, all 19 leaves under `24711922`, `24717714`, and
  `24717815` completed `0:0` without retry or cancellation. Twenty-three non-failing spinup
  max-iteration warnings were retained; GPP/SR had none.
- Boundary/evidence: ABBY/JERC development-only repeated held-out predictions; no fixed-test,
  all-development fit, tuning, cross-fitting, release edit, MCMC change, plan amendment, or push.
  Compact evidence is in `development/three_stage_surrogate/summaries/iter015/`.
- Campaign-plan amendment recommendation: `none`.
- Next state: Iter015 is terminal. No next iteration is proposed or authorized.
