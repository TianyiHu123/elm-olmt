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
