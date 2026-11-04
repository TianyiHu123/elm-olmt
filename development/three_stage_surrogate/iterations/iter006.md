# iter006 - ABBY/JERC fixed-upstream GPP robustness and conditional release

## Status

- Iteration ID: `iter006`
- Work type: `implementation`
- Run slug: `three_stage_surrogate_iter006_abby_jerc_gpp_release`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-01T00:28:58-07:00`
- Closed: `2026-11-01T04:58:32-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256:
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 5, two-site GPP development and release
- Alignment: `aligned_with_scoped_deviation`
- Approved deviation: use the published all-819 predicted-C/N handoff for both GPP training and
  validation. Evidence is `fixed_upstream_gpp_stage`, not end-to-end held out.

## Finalized Plan

- Objective: characterize the frozen Iter005 43-feature hourly GPP configuration on the exact
  Iter004 20-split balanced 655/164 development design, publish a compact member-balanced GPP
  uncertainty component, and conditionally fit and release the all-819 GPP artifact plus its
  predicted-GPP SR handoff.
- Inputs: immutable snapshot `r0001` (`39b05495...187a`); 819/205 global split
  (`99467dea...0fce`); spinup release manifest `69f840f7...f2dc`; predicted-C/N handoff
  `9e2d5be4...fdb5`; Iter004 repeated-split file `7644ed38...ace0`, seed `20261031`, design
  `0b343378...6ecb`; and validated Iter005 GPP interfaces. The Iter005 prepared cache is
  split-standardized and is provenance evidence only, not arbitrary-split training input.
- Frozen science: physical GPP in `gC/m^2/day`; exact 43-feature order/history semantics; fit-only
  standardization; no target transform or clipping; `(128,)` ReLU/Adam, alpha `1e-4`, adaptive
  learning rate `0.001`, `max_iter=500`, early stopping, internal fraction `0.1`,
  `n_iter_no_change=10`, tolerance `1e-4`, batch `auto`, shuffle, seed `42`; batch-aware public
  inference; hourly predictions and complete-day means from the same artifact.
- Development boundary: every repetition fits scalers, optimizer state, and model using only its
  655 members; 164 members are inference-only at both sites. All 205 fixed-test members are
  forbidden from fitting, metrics, uncertainty, gates, release decisions, and products.
- Work units: combined preflight/preparation; smoke; unthrottled 20-leaf robustness array;
  combined aggregation/independent validation; conditional all-819 release fit/staging; conditional
  independent release validation; catalog-last publication; concise records; one no-push commit.
- Robustness products: comprehensive `metric_distribution.csv`; `convergence.json`; exact split
  manifest; compact per-member moments sufficient to reproduce member-balanced estimates without
  retaining full hourly residual arrays.
- Uncertainty products: comprehensive `uncertainty_estimates.csv`, compact
  `gpp_uncertainty.nc`, and `uncertainty_report.json`. The NetCDF dimensions are site, resolution,
  and repetition and its only data variables are `GPP_error_bias`, `GPP_error_rmse`,
  `GPP_per_repetition_error_bias`, and `GPP_per_repetition_error_rmse`.
- Conditional release: after gate pass only, fit all 819 development members; stage a hash-verified
  pickle plus manifest; create `gpp_predicted_for_sr.nc` containing site/member/time and physical
  predicted GPP but no ELM truth, fixed-test data, parameters, forcing, or duplicated C/N; validate
  in a fresh process; promote immutable `release_0001`; write catalog last.
- Exclusions: spinup execution/refit; fixed-test access; feature/model search; SR fitting;
  full-chain robustness; temporal/autocorrelation/target-conditioned residual analysis;
  observations; likelihood/MCMC; campaign-plan edit; backup; deletion; or push.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `Full revised package approved`; recorded `2026-11-01T00:28:58-07:00` after revising to combined preparation, unthrottled robustness, combined aggregation/validation, five additional submissions, and comprehensive robustness/uncertainty tables. |
| Kickoff goal, finite work-unit count, and stop conditions | Six normal submissions on the pass branch and four on a failed-gate branch. Continue through authoritative terminal accounting, immutable gate application, correct conditional publication, concise records, four-record validation, and one no-push commit. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `9bbb6865...9128`; progression item 5; `aligned_with_scoped_deviation`; fixed published all-819 C/N inputs on both sides. |
| Confirmed HPC system and site profile | UA Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create exact run root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter006_abby_jerc_gpp_release` and its approved run/staging layout. Preserve outputs; no cleanup. On pass only, publish under `NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/release_0001` and write catalog last. `/xdisk` is temporary/unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities and frozen science above; exact 20 splits; no fixed test; immutable numeric and technical gates below; all-or-nothing release branch. |
| Lifecycle authority | Bounded GPP implementation, focused tests, Iter006 scripts/config/manifests/validators, exact directories, independent read-only review, six normal submissions, up to five additional submissions, monitoring/accounting, conditional publication, records, and one no-push closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preparation 25 GB/derived 5 CPUs/4 h; smoke 4 CPUs/20 GB/2 h; array `1-20` unthrottled, 50 GB/derived 10 CPUs/16 h per leaf; aggregation/validation 4 CPUs/20 GB/4 h; release 50 GB/derived 10 CPUs/16 h; release validation 8 CPUs/40 GB/4 h. Up to five additional submissions total under the locked retry rules. Use supported waits and job-scoped monitoring through terminal `sacct`. |
| Cancellation scope | Recorded Iter006 jobs only when duplicated, outside contract, invalidated upstream, threatening integrity/storage, or an array has a demonstrated common failure. Pending/slow state is not a cancellation condition. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` under the conditions above. |
| Closeout branch | One controlled Iter006 no-push closeout commit authorized after validation. |

Current Puma evidence at kickoff: user/group standard limit 3,290 CPUs and 16,998 GB, current use
2 CPUs/10 GB; the unthrottled array requests at most 200 CPUs/1,000 GB. `/xdisk/chopinsong` uses
approximately 7.7/19.5 TB; estimated Iter006 retention is approximately 0.4 TB. Expiration is not
available to a non-PI query. Home uses 41.9/50 GB, so runtime caches and temporary files belong
under the approved run root.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | Direction | `development/three_stage_surrogate/PLAN.md` | approved | `9bbb6865...9128` | Iter006 alignment reviewed at kickoff. |
| Snapshot | GPP/forcing/parameter/surface inputs | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data` | `r0001` | `39b05495...187a` | Iter001 and Iter005 validation passed. |
| Global split | Development/fixed test | `<snapshot>/splits/member_split_1024_v1.json` | 819/205 | `99467dea...0fce` | Fixed-test access false in prior stages. |
| Spinup release | Fixed C/N upstream | `NEON_ppe_vertc/surrogate_products/spinup_abby_jerc/release_0001` | release v1 | manifest `69f840f7...f2dc`; handoff `9e2d5be4...fdb5` | Iter004 independent validation and catalog-last publication passed. |
| Repeated splits | Robustness partitions | `<spinup release>/uncertainty/repeated_split_manifest.json` | 20 balanced splits | file `7644ed38...ace0`; design `0b343378...6ecb` | Exact 655/164 partitions; every development member appears 4 or 5 times. |
| Iter005 interface | Frozen feature/model/inference contract | `model_ELM/three_stage_gpp.py` and Iter005 records | baseline v1 | source `e5ae810c...6ba3`; prepared manifest `acd9a7bb...416b` | Baseline and revised batch-aware validation passed. |

`<snapshot>` is the declared snapshot root above. Only recorded identities are trusted; preparation
must fail closed on mismatch.

## Acceptance Gates and Decision Rule

- Exactly 20 complete split results; exact 655/164 synchronized membership; all-and-only 819
  development identities; no fixed-test access; finite predictions; no identity drift or
  unexplained gaps; coverage exactly `1.0` for every repetition/site/resolution.
- For each site using NumPy linear quantiles across validation repetitions: hourly R2 q10 at least
  `0.85`; daily R2 q10 at least `0.75`; hourly RMSE q90 at most `5.0`; daily RMSE q90 at most
  `3.0`; median absolute per-repetition bias at most `0.35 gC/m^2/day` at both resolutions.
- Convergence warnings are nonfatal only when outputs are finite and every performance, identity,
  and reload gate passes; preserve all warnings.
- Batch-aware validation: original 250,000-row chunk replay under `rtol=atol=1e-6`; public batches
  1/7/1,000 finite and exactly repeatable for the same batch; characterize cross-batch differences.
- Aggregation validator independently recomputes comprehensive tables and all four NetCDF fields,
  checks schemas/units/provenance/hashes, and applies the gate before release submission.
- If the gate fails, preserve diagnostic products, decide `optimization_required`, publish no
  release/handoff/catalog, and close after records/validation/commit. If it passes, submit the
  conditional release work and publish only after fresh-process independent release validation.
- Changes to science, feature/model configuration, upstream mode, split design, gates, products,
  resources, fixed-test boundary, or interpretation require fresh approval.

## Retry and Cancellation Rules

- At most five additional submissions total. A failed-index array resubmission counts as one.
- One minimal preflight correction may repair import/path/manifest/launch defects without changing
  science or runtime terms. Transient scheduler/node/preemption failures may retry identical
  material and resources.
- OOM, timeout, resource increase, application/code/interface/schema/data/dependency/numerical
  failure, or gate reinterpretation requires fresh approval before correction or retry.
- Cancellation follows the bounded conditions in the approved package and still requires terminal
  accounting.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prepare | `58e2076a...85d9` | exact copy; config `de54faa0...5688`; manifest `0ff9b492...2eb0` | `<root>/runs/prepare`; `prepare_24489883.*` | locked inputs | HEAD `9340b060`; manifest `0ff9b492...2eb0` | job `24489883` | `COMPLETED 0:0`, `00:02:13`, batch MaxRSS `18197176K` | Preflight, 100,442,160-row cache, 18-row source reconstruction, and full hashes passed. |
| smoke | `8eb40926...5542` | exact copy; config `de54faa0...5688`; manifest `0ff9b492...2eb0` | `<root>/runs/smoke`; `smoke_24489912.*` | prepare pass | HEAD `9340b060`; manifest `0ff9b492...2eb0` | job `24489912` | `COMPLETED 0:0`, `00:00:29`, batch MaxRSS `660304K` | Bounded 80/20-member fit/inference passed. |
| robustness | `ae5d8b41...03a1` | exact copy; config `de54faa0...5688`; manifest `0ff9b492...2eb0` | `<root>/runs/robustness`; `robustness_24489937_*.*` | smoke pass | HEAD `9340b060`; manifest `0ff9b492...2eb0` | array `24489937_[1-20]` | all 20 `COMPLETED 0:0`; elapsed `01:38:12` to `03:19:21`; batch MaxRSS `36133900K` to `52428384K` | All split and reload reports pass; zero convergence warnings. Post-exit `squeue` returned invalid job ID, then complete `sacct` reconciled all leaves. |
| aggregate/validate | `ee2e1f00...a16b7` | attempts 1/2/3 manifests `0ff9b492...2eb0` / `84d6d5db...bd007` / `073ca1fb...6741`; config `de54faa0...5688`; exact script copy | `<root>/runs/aggregate`; `aggregate_24491172.*`, `aggregate_24491252.*`, `aggregate_24491301.*` | all 20 eligible | HEAD `9340b060`; final manifest `073ca1fb...6741` | jobs `24491172`, `24491252`, `24491301` | attempts 1/2 `FAILED 1:0`; attempt 3 `COMPLETED 0:0`, `00:03:28`, MaxRSS `15350176K` | All aggregations returned the same immutable gate `fail`. Approved numerical-validation corrections were independently re-reviewed; attempt 3 independently validated all products and the gate. Two additional submissions consumed. |
| release | `1a6676a1...e1d` | not submitted | `<root>/runs/release` | immutable gate pass | final manifest `073ca1fb...6741` | none | prohibited | Gate failed; no all-819 fit or staging. |
| release validation | `be167820...06` | not submitted | `<root>/runs/release_validation` | release pass | final manifest `073ca1fb...6741` | none | not applicable | No release package existed to validate. |

`<root>` is the approved Iter006 run root.

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter006_review`
- Reviewed source hash: execution manifest
  `0ff9b492f641b685d240f98aeb094f56c2656e1e55cfbabbdd4c6a9665512eb0`
- Outcome: `pass` with no remaining blockers or concerns at `2026-11-01T00:40:26-07:00`
- Findings and primary-agent response: the initial review blocked missing direct dependency locking,
  insufficient raw-source reconstruction, aggregate-table/NetCDF independence, and release-package
  coverage. The primary agent locked `three_stage_data.py`, added source reconstruction, independently
  recalculated every leaf metric/member-balanced field/NetCDF field, validated all coordinates,
  units, definitions, provenance and hashes, expanded full release/handoff replay, refreshed all six
  exact submitted copies, and obtained a pass on the final material.
- Retry review: after aggregate attempt 1, the user approved the bounded correction and one retry.
  Reviewer passed manifest `84d6d5dbc89767278fdb7661741d0c20896fa37c07a9a3f4908e88a4cedbd007`
  at `2026-11-01T04:38:02-07:00` with no concerns: direct metrics remain at `1e-12`, only
  compounded gap/ratio comparisons use `1e-10`, and science/gate/resources are unchanged.
- Retry review 2: after attempt 2 exposed the `np.dot` versus `np.sum` denominator accumulation
  mismatch, the user approved production-equivalent `np.sum` accumulation and one further retry.
  Reviewer passed manifest `073ca1fbd311eb22748979154d387728a6f04c0ef26f312e74e448f823436741`
  at `2026-11-01T04:51:24-07:00` with no concerns; tolerances, science, gates, and resources are
  unchanged, and attempt 3 is clear.

## Execution and Diagnostics

- Initialization: package approved; scaffold, exact run directories, configs, manifests, and scripts
  prepared.
- Static validation: manifest `sha256sum -c`, shell syntax, JSON parsing, submitted-copy comparison,
  `git diff --check`, and independent read-only review all pass.
- Preflight and execution: prepare, smoke, and all 20 robustness leaves completed successfully.
  Aggregate attempt 1 job `24491172` generated the complete diagnostic products and gate result,
  then its fresh-process validator failed on `independent leaf r2_train_validation_gap mismatch`.
  The independent direct R2 values passed at `1e-12`; the derived subtraction comparison used the
  same `1e-12` tolerance even though its separately accumulated inputs have compounded rounding.
  The user then approved a derived-only `1e-10` tolerance, manifest refresh/re-review, and one
  aggregate retry. Re-review passed. Attempt 2 job `24491252` failed validation at a later direct R2
  comparison: the independent implementation reduces the denominator with `np.dot`, while the
  production implementation reduces the same tens of millions of squared values with `np.sum`.
  Their accumulation-order difference exceeded `1e-12`. The user approved matching the reduction;
  attempt 3 completed and technical validation passed. No release work was submitted.
- Submission, identity, accounting, resources, failures/retries/cancellation: all jobs are
  terminally accounted. Prepare `24489883`, smoke `24489912`, all array tasks `24489937_[1-20]`,
  and final aggregate `24491301` completed `0:0`. Aggregate attempts `24491172` and `24491252`
  failed validation and are preserved/classified. Two of five additional submissions were used;
  no cancellation occurred.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| prepare | yes | preflight/cache/raw validator pass; report `3b118f38...5d93` | pass | Eligible for smoke. |
| smoke | yes | report `ebd12bb...c4e3` | pass | Eligible for robustness. |
| robustness | yes | 20 split/reload reports; all terminal `0:0` | pass | Eligible for aggregation. |
| aggregate/validate | yes | 240 metrics, 84 uncertainty rows, NetCDF and independent validation `f95fccbf...5d07` | science gate `fail`; technical validation pass | Preserve diagnostic products; optimization required. |
| release | no | no submission or artifact | prohibited | Immutable gate failed. |
| release validation/publication | no | no release, handoff, stable package, or catalog | not applicable | Correct failed-gate branch. |

- Overall acceptance result: `fail`; technical product validation passed, but every site/resolution
  failed its immutable R2 and RMSE publication thresholds.
- Overall decision and closeout conclusion: `optimization_required`. Preserve diagnostic
  robustness/uncertainty products only; no release artifact, SR handoff, stable package, or catalog.
- Limitations: two sites; fixed upstream C/N is in-sample for all 819 development members;
  overlapping robustness validation sets; uncertainty comes from 655-member fits and no final
  819-member GPP fit exists; temporary unbacked storage; no fixed-test, SR, full-chain,
  observation, likelihood, or posterior evidence.
- Campaign-plan amendment recommendation: `none`; configuration optimization is already the
  declared failed-gate branch and needs a separately approved iteration.
- Next action: explicit terminal declaration. Discuss and approve any future planning-only GPP
  configuration-optimization iteration separately.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration proposal is authorized or implied. Iter006 terminates with
`optimization_required`; future optimization first requires a planning discussion.

## Four-Record Closeout Validation

- Validator: `development/three_stage_surrogate/slurm/iter006/validate_closeout_iter006.sh`
- Command: `bash development/three_stage_surrogate/slurm/iter006/validate_closeout_iter006.sh --active-job-count 0`
- Result: `pass`
- Output: `ITER006_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=fail decision=optimization_required active_jobs=0 release=absent`
- Scope: report/summary/registry/handoff agreement; plan identity; terminal jobs; 20 split/reload
  reports; aggregate product hashes; 240/84 table counts; independent gate validation; and absence
  of the conditional stable release.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter006/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified no-push commit
