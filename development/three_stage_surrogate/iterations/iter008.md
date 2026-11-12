# iter008 - ABBY/JERC GPP robustness characterization and release

## Status

- Iteration ID: `iter008`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter008_abby_jerc_gpp_release`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-02T23:29:39-07:00`
- Closed: `2026-11-04T01:12:26-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 5, two-site GPP development and release.
- Alignment: `aligned_with_scoped_deviation`.
- Approved deviation: the published all-819 predicted-C/N handoff is fixed upstream input for
  both robustness partitions and the release fit; evidence is `fixed_upstream_gpp_stage`, not
  end-to-end held out.

## Finalized Plan

- Objective: freeze Iter007 candidate 21, characterize it on 20 fresh synchronized balanced
  655/164 development-only splits, retain descriptive metrics and the Iter006-format uncertainty
  product, fit candidate 21 on all 819 development members, and publish the Iter006-format GPP
  artifact and `gpp_predicted_for_sr.nc` handoff after independent technical validation.
- Release basis: `iter007_best_configuration`; `performance_gate_applied=false`. Robustness
  performance is evidence, not a release gate. Technical validity remains mandatory.
- Frozen model: 43 features; physical GPP in `gC/m^2/day`; fit-only standardization; no transform
  or clipping; `(64,32)` tanh MLP, alpha `1e-4`; Adam/adaptive `0.001`; `max_iter=500`; early
  stopping fraction `0.1`; `n_iter_no_change=10`; tolerance `1e-4`; batch `auto`; shuffle; seed 42.
- Population: 819 development members only. Every robustness leaf fits 655 and evaluates 164 at
  ABBY and JERC. All 205 fixed-test members are prohibited from fitting, metrics, uncertainty,
  validation, release decisions, and products.
- Fresh design: seed `20261102`; 20 synchronized balanced splits; preflight must prove complete
  819-member coverage, 655/164 disjointness, 815 members appearing four times and four appearing
  five times, zero fixed-test membership, and no validation-set identity with any Iter006/Iter007
  selection split.
- Four normal submissions: combined preflight/preparation; uncapped `1-20` robustness array;
  all-819 release-core fit and GPP handoff; combined aggregation, independent validation,
  staging promotion, and catalog-last publication.
- Products and stable layout are the exact Iter006 contract under
  `NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/release_0001`.
- Exclusions: spinup execution/refit; fixed-test use; further configuration search; a performance
  release gate; SR fitting; full-chain uncertainty; observations; likelihood/MCMC; campaign-plan
  edit; backup; cleanup; deletion; or push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `Full finalized Iter008 package approved`; recorded `2026-11-02T23:29:39-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Execute four normal submissions and continue through authoritative terminal accounting, technical validation, descriptive aggregation, all-819 release, publication, concise records, four-record validation, and one no-push commit. Stop only at completed closeout or a workflow-classified condition requiring fresh authority. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; SHA-256 `9bbb6865...9128`; progression item 5; `aligned_with_scoped_deviation`; fixed all-819 predicted C/N on both sides. |
| Confirmed HPC system and site profile | UA Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter008_abby_jerc_gpp_release` with four run roots and staging. Publish immutable `gpp_abby_jerc/release_0001` and catalog last. Preserve outputs; no cleanup; `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities and science above; candidate 21; fresh seed-20261102 splits; no fixed test; no performance gate. Release proceeds after complete technically valid robustness evidence. Technical invalidity stops publication. |
| Lifecycle authority | Iter008 records; bounded shared-code generalization; focused tests; scripts/config/manifests/validators; approved directories; independent read-only review; four normal submissions and bounded retries; monitoring/accounting; validation/publication; records; one no-push closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preflight 5 derived CPUs/25 GB/4 h; uncapped array leaves 12 CPUs/60 GB/16 h; release 12 CPUs/60 GB/20 h; final 8 CPUs/40 GB/4 h. At most one reviewed preflight-plumbing correction, one unchanged scheduler/node/transport retry for failed work only, and one same-source validation-only retry. Use supported waits and job-scoped monitoring through terminal `sacct`. |
| Cancellation scope | Recorded Iter008 jobs only when duplicated, outside contract, invalidated upstream, unsafe, threatening storage integrity, or affected by a demonstrated common defect. Pending or slow state is not sufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only for recorded Iter008 jobs under the approved conditions. |
| Closeout branch | One controlled local no-push closeout commit authorized after validation. |

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction | `development/three_stage_surrogate/PLAN.md` | approved | `9bbb6865...9128` | Live hash matched at bootstrap. |
| Workflow | Lifecycle authority | `development/three_stage_surrogate/WORKFLOW.md` | current | `f23f040e...dc4` | Governing lifecycle policy. |
| Puma profile | Site mechanics | `development/hpc/puma.md` | current | `12d05836...2851` | Host and current limits reconciled. |
| Snapshot r0001 | Forcing, GPP truth, parameters, split boundary | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data` | immutable snapshot | `39b05495...187a` | Iter001-published input. |
| Global split | Development/fixed-test boundary | snapshot manifest | 819/205 | `99467dea...0fce` | Fixed-test boundary is immutable. |
| Spinup release | Fixed upstream package | `<products>/spinup_abby_jerc/release_0001/release_manifest.json` | release v1 | `69f840f7...f2dc` | Live hash matched. |
| Predicted C/N | Fixed GPP input | `<products>/spinup_abby_jerc/release_0001/handoff/spinup_predicted_cn.nc` | 819 development members | `9e2d5be4...fdb5` | Live hash matched. |
| Iter007 selection | Release-basis evidence | `development/three_stage_surrogate/summaries/iter007/selection_report.json` | selected candidate 21 | `d90cf503...e745` | Decision is `configuration_selected_gate_pass`. |
| Iter006 raw cache | Hash-locked reusable 43-feature data | `<iter006>/runs/prepare/attempt_1/raw` | 819 development members | hashes locked in Iter007 config | Reuse read-only after independent validation. |

## Acceptance Gates and Decision Rule

- Required completeness: exact identities; four normal work units; all 20 array leaves terminal
  and technically valid; exact split coverage; finite predictions; coverage `1.0`; successful
  artifact reload; complete uncertainty and handoff schemas; zero fixed-test access; all files and
  hashes independently reproduced; no active or unaccounted jobs.
- Performance gate: none. R2, RMSE, MAE, bias, residual distribution, and convergence evidence are
  retained descriptively and do not determine publication.
- Decision: publish candidate 21 after technical validity passes. Any technical failure blocks
  publication until classified under the approved retry or fresh-authority boundary.
- Changes to science, model configuration, seed/design, products, resources, fixed-test boundary,
  release interpretation, or numerical contract require fresh authorization.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter008.slurm` / `0396a896...54a5` | exact submitted copy; base config `7de16aec...9dd4`; manifest `b3595398...7a9f`; resolved config `e05767cd...0c19` | `<root>/runs/preflight`; `preflight_%j.{out,err}` | declared inputs | base `6bbbb779`; source manifest `b3595398...7a9f` | job `24512852` | `COMPLETED 0:0`, `00:00:54` | identity matched; split `c3aa7c4b...c904`, design `67d00b10...f4cb`; reviewer follow-up passed |
| robustness | `robustness_iter008.slurm` / `74e5d3e4...9b89` | exact submitted copy; resolved config `e05767cd...0c19`; manifest `b3595398...7a9f` | `<root>/runs/robustness`; `robustness_%A_%a.{out,err}` | preflight `24512852`; eligible marker; split `c3aa7c4b...c904` | base `6bbbb779`; source manifest `b3595398...7a9f` | array `24513943`, `1-20`, uncapped | all 20 `COMPLETED 0:0`; elapsed `01:57:45`-`04:29:53` | resumed accounting complete; all split/reload reports and hashes pass; zero warnings; fixed-test false |
| release | `release_iter008.slurm` / `c53e81b2...2335` | exact submitted copy; resolved config `e05767cd...0c19`; manifest `b3595398...7a9f` | `<root>/runs/release`; `release_%j.{out,err}` | 20 technically valid robustness leaves | base `6bbbb779`; source manifest `b3595398...7a9f` | job `24520151` | `COMPLETED 0:0`, `02:27:52` | artifact `67214897...8ec9`; handoff `c905fc60...98bb`; 819 members; zero warnings; fixed-test false |
| final | `final_iter008.slurm` / `75c7a890...efeb` | exact submitted copy; resolved config `e05767cd...0c19`; manifest `b3595398...7a9f` | `<root>/runs/final`; `final_%j.{out,err}` | release core and all robustness leaves | base `6bbbb779`; source manifest `b3595398...7a9f` | job `24523438` | `FAILED 1:0`, `00:03:41` | aggregate passed; release replay raised `ValueError: handoff prediction mismatch`; no publication; fresh authority required |
| diagnostic | `diagnose_handoff_replay_iter008.slurm` / `c01d8130...e2e` | exact submitted copy; config `e05767cd...0c19`; diagnostic manifest `a2951b1c...8e20` | `<root>/runs/diagnostic`; `diagnostic_%j.{out,err}` | preserved release attempt 1 and failed final evidence | reviewed Python `0d2bd4cf...c2b` | job `24523491` | `FAILED 1:0`, `00:00:25` | reporter `TypeError` on 2-D flat-argmax indexing; no diagnostic report; no resubmission; fresh approval required |
| diagnostic retry 1/3 | `diagnose_handoff_replay_iter008.slurm` / `d85cbf90...208e` | exact attempt-2 submitted copy; config `e05767cd...0c19`; diagnostic manifest `79a2bd4d...b288` | `<root>/runs/diagnostic`; `diagnostic_%j.{out,err}`; output `attempt_2` | preserved release attempt 1 and failed diagnostic attempt 1 | reviewed Python `02d8b6c6...22e0` | job `24523514` | `COMPLETED 0:0`, `00:00:16` | handoff equals stored; scaled replay passes; raw replay fails; retry unit 1 consumed; 2 remain |
| final retry 2/3 | `final_iter008.slurm` / `75c7a890...efeb` | exact attempt-2 submitted copy; config `e05767cd...0c19`; corrected manifest `91a25126...3345` | `<root>/runs/final`; `final_%j.{out,err}`; output `attempt_2` | robustness/release attempt 1; diagnostic attempt 2 | corrected `three_stage_gpp.py` `e2c22e55...a818` | job `24523529` | `COMPLETED 0:0`, `00:03:44` | validation and catalog-last publication passed; retry unit 2 consumed; 1 unused |

`<root>` is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter008_abby_jerc_gpp_release`.

## Independent Read-Only Review

- Reviewer: different read-only agent `/root/iter008_review`.
- Reviewed source hash: final `b3595398...7a9f`.
- Outcome: initial `block`; corrected final re-review `pass`.
- Findings and primary-agent response: reviewer found that reused raw-cache validation still
  compared its historical Iter006 source-split hash to the fresh Iter008 active-split hash. The
  primary agent added an explicit `raw_source_split_manifest_sha256` identity with a backward-
  compatible fallback, refreshed submitted config/source manifest, and obtained a passing
  re-review. The reviewer also suggested an earlier catalog-absence precondition; this was moved
  before stable copy/move and re-reviewed as fail-closed. The reviewer requires the planned
  read-only check of Unit1's generated split and resolved-config identities before Unit2. No
  Python or scheduler action occurred before the final pass.
- Post-preflight follow-up: `pass`; independently verified resolved config `e05767cd...0c19`, split
  manifest `c3aa7c4b...c904`, canonical design `67d00b10...f4cb`, exact 655/164 coverage and 815/4
  balance, zero prior-design matches, raw-source identity separation, candidate 21, no-gate flags,
  and fixed-test/spinup prohibitions. No concerns.
- Failure-correction authority: user explicitly approved `correction and retry` after final job
  `24523438` failed. A different read-only agent initially blocked the diagnostic material for
  missing fail-closed identity, boundary, manifest, coordinate, and localization checks. After
  correction, re-review passed for Python `0d2bd4cf...c2b` and Slurm `c01d8130...e2e`; no reviewer
  edits or scheduler actions occurred.
- Additional retry authority: after diagnostic job `24523491` failed, the user approved the
  reporter fix and three further retry units without intermediate permission stops. Diagnostic
  attempt 2 consumed retry unit 1; final attempt 2 consumed unit 2; unit 3 remained unused.
- Production correction review: `pass`. The reviewer independently confirmed that casting the
  stored scaler statistics to the `float32` design dtype exactly matches the installed
  `StandardScaler.transform` arithmetic, preserves artifact compatibility, and changes no model,
  science, data, gate, or fixed-test scope. Corrected `three_stage_gpp.py` is `e2c22e55...a818`;
  corrected execution manifest is `91a25126...3345`. Final-attempt and catalog-last publication
  guards passed review before job `24523529` was submitted.

## Execution and Diagnostics

- Static validation: `bash -n`, JSON parsing, submitted-copy equality, source-manifest verification,
  fixed-root/path checks, uncapped array assertion, and `git diff --check` pass. Repository Python
  remains unexecuted on the login node.
- Preflight: job `24512852` completed `0:0`; `ITER008_PREFLIGHT_OK`; no training; seed `20261102`;
  20 fresh splits; 815/4 member appearance balance; zero reference-set matches; full raw-cache
  hashes and 18 source reconstructions passed; resolved config `e05767cd...0c19`.
- Exact submission commands: preflight command recorded above; from `<root>/runs/robustness`,
  `/usr/bin/sbatch --parsable --export=ALL,ITER008_ATTEMPT=1,ITER008_PREFLIGHT_ATTEMPT=1,ITER008_CONFIG_SHA256=e05767cd...0c19,ITER008_EXECUTION_MANIFEST_SHA256=b3595398...7a9f ./submit_robustness_iter008.slurm </dev/null`.
- Job identity checks: preflight name, account/partition, 25 GB/derived 5 CPUs, 4 h limit,
  workdir, script, exports, logs, and `/dev/null` stdin matched the locked submission.
- Queue and terminal accounting: preflight `squeue` was invalid after exit; authoritative `sacct`
  records parent/batch `COMPLETED 0:0`, elapsed `00:00:54`. Robustness identity matched all 20
  uncapped leaves, 12 CPUs/60 GB/16 h, workdir/script/exports/logs. At the explicit user stop
  checkpoint `2026-11-03T03:41:30-07:00`, all 20 leaves were `RUNNING`; leaves 1-10 had elapsed
  `00:21:40`, leaves 11-20 `00:16:37`; no terminal failure existed. Persistent monitoring was
  interrupted without cancelling or changing the jobs.
- Resource diagnostics: batch MaxRSS `17,813,920K`; `/usr/bin/time` Python MaxRSS `419,664K`;
  preflight full-hash filesystem reads dominate the batch accounting. Robustness batch MaxRSS
  ranged about `35,016,348K`-`52,574,612K`, within 60 GB; elapsed ranged `01:57:45`-`04:29:53`.
- Earlier failure, rejection, retry, or cancellation evidence: none. User explicitly requested monitoring
  stop while jobs continue; exact resume action is fresh job-scoped `squeue -r` plus complete-parent
  `sacct` for array `24513943` before any other lifecycle action. That reconciliation later passed.
  User separately requested monitoring stop for release job `24520151` while it was `PENDING`
  `(Priority)` at `2026-11-03T15:26:47-07:00`; monitor stopped without job mutation. Exact resume
  action is fresh job-scoped `squeue` and `sacct` for `24520151` before output validation.
  Resumed accounting found release job `24520151` `COMPLETED 0:0`; no retry or failure.
- Final job `24523438` reached authoritative `FAILED 1:0` after `00:03:41`; batch MaxRSS
  `20,867,548K`. Aggregation and aggregate validation completed first, producing exactly `240`
  metric rows and `84` uncertainty rows. Release validation then raised
  `ValueError: handoff prediction mismatch` at the artifact-replay comparison using locked
  `reload_rtol=1e-6` and `reload_atol=1e-6`. This is classified as an
  application/code/interface/numerical failure under Workflow Section 4E. No retry, correction,
  promotion, catalog write, or commit was attempted. Stable `release_0001` and `catalog.json`
  were confirmed absent at `2026-11-04T00:37:23-07:00`.
- After fresh correction-and-retry approval and passing read-only review, diagnostic job `24523491`
  reached `FAILED 1:0` after `00:00:25`; batch MaxRSS `1,465,052K`. It failed while formatting the
  first chunk's 2-D `manual_vs_original_scaled` result: `np.argmax` returned a flat index but
  `delta[worst]` indexed only axis 0, raising `TypeError: only length-1 arrays can be converted to
  Python scalars`. No `diagnostic_report.json` was written. This is a new application/code failure;
  no correction or retry was attempted without fresh approval.
- Diagnostic retry job `24523514` completed `0:0` after `00:00:16`; batch MaxRSS `1,382,392K`.
  Across first, middle, and last production chunks, NetCDF handoff values equal persisted release
  predictions exactly and artifact replay from the persisted scaled design passes the locked
  tolerance. Raw-interface replay fails by up to `7.518004284033e-4`; reconstructed scaled features
  differ from the persisted design by up to `3.814697265625e-6`. Installed scikit-learn casts
  scaler statistics to the input dtype before in-place arithmetic; the released interface did not.
  The minimal correction casts `x_mean` and `x_scale` to `float32` before subtract/divide, with no
  model, artifact, handoff, data, science, gate, or fixed-test change.
- Corrected final job `24523529` completed `0:0` after `00:03:44`; batch MaxRSS `20,858,492K`.
  Independent validation passed all `100,442,160` handoff predictions, the 819-member coordinates,
  artifact replay, exact product hashes, and fixed-test exclusion. Catalog-last publication then
  completed. All 13 release-manifest files independently match size and SHA-256; validated,
  staging, and stable trees match exactly.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | job `24512852`; identity report and eligible marker | technical pass | fresh split/config and raw cache eligible; reviewer follow-up passed before Unit2 |
| robustness | yes | all 20 allocations `COMPLETED 0:0`; 20 split/reload passes; hashes match; zero warnings | performance not applicable | technically eligible descriptive evidence; proceed to release |
| release | yes | job `24520151`; artifact/handoff reports and hashes match | technical pass | all-819 candidate-21 release core eligible for final validation |
| final | yes | corrected job `24523529`; `ITER008_FINAL_VALIDATE_OK`; 13-file manifest and catalog independently reproduced | technical pass; performance gate not applicable | publish candidate-21 release and downstream GPP handoff |

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: `gpp_release_published`; publish candidate-21
  robustness uncertainty, all-819 artifact, and predicted-GPP downstream handoff as
  `gpp_abby_jerc/release_0001`.
- Limitations: two sites; fixed in-sample upstream C/N; all-819 release predictions are in-sample;
  metrics are descriptive and no robustness performance threshold is applied; `/xdisk` is
  temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next action: explicit terminal declaration. Iter008 is complete; any SR surrogate fitting,
  full-chain uncertainty, likelihood/MCMC work, or later release requires a separately planned and
  approved iteration. No job is active or unaccounted.

## Explicit Terminal Declaration

No next iteration proposal is authorized. The GPP artifact, descriptive robustness uncertainty,
and `gpp_predicted_for_sr.nc` handoff are published for downstream handoff. SR fitting and all
later campaign work require a separate planning discussion and consolidated kickoff approval.

## Closeout Validation and Commit Branch

- Validator: `development/three_stage_surrogate/slurm/iter008/validate_closeout_iter008.sh`;
  SHA-256 `73c84595ac45ab08260f88fcefea2cc9126080789ae595f762e52baf62d23b9a`.
- Command: `bash development/three_stage_surrogate/slurm/iter008/validate_closeout_iter008.sh --active-job-count 0`.
- Result: `ITER008_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=gpp_release_published active_jobs=0 release=release_0001 files=13`.
- Commit branch: expected parent `6bbbb779b6700da9e3dd0c010f1fe5c338829f89`; expected subject
  `Release GPP surrogate artifact`; one local commit and no push.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter008/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified local no-push commit
