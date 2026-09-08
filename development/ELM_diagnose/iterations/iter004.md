# iter004 - ABBY OAT sensitivity diagnostic

## Status

- Iteration ID: `iter004`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter004_abby_oat`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-08T12:54:35-07:00`
- Closed: `2026-09-08T13:55:00-07:00`

## Finalized Plan

- Sequential ID and work type: `iter004`; reusable OAT diagnostic implementation plus one ABBY application.
- Objective and hypothesis: rank the range-wide response of 13 ELM carbon-flux and pool targets to 14 separately perturbed parameters using each member's 2018--2024 hourly mean and population standard deviation. Robust response spread over each user-selected range may identify a compact set for later tuning work.
- Method boundary: descriptive baseline-conditioned OAT response screening only. Do not label results PAWN, Sobol, joint/global sensitivity, interaction, mediation, or causal effects. Do not recommend parameter values or run ELM, postprocessing, optimization, tuning, or a surrogate.
- Inputs: exactly 14 explicitly mapped ABBY historical pickles beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/ABBY/pklfiles` and control parameter file `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc`. Pickle metadata is authoritative; transferred configs/range files are provenance cross-checks only; stale Perlmutter paths are never dereferenced.
- Scope: one preflight work unit and one diagnostic work unit. Process one pickle at a time, lock hashes in an immutable manifest, retain compact summaries, and atomically publish only a complete result.
- Outputs: 26 response atlases, two sensitivity heatmaps, seven compensation figures, `parameter_metadata.csv` (14 rows), `member_metrics.csv` (1,400 rows), `sensitivity_scores.csv` (364 rows), `response_curves.csv`, validation receipt, input manifest, and output manifest.
- Decision: pass only when every immutable input, time/output, calculation, artifact, review, accounting, and four-record gate passes. A failed gate rejects the work unit and prevents partial publication or scientific interpretation.

### Exact parameter mapping

| Parameter | Exact pickle basename | Coordinate |
| --- | --- | --- |
| `act25` | `ABBY_ctrlact25_I20TRCNPRDCTCBC.pkl` | linear |
| `br_mr` | `ABBY_ctrlbrmr_I20TRCNPRDCTCBC.pkl` | linear |
| `grperc` | `ABBY_ctrlgrperc_I20TRCNPRDCTCBC.pkl` | linear |
| `grpnow` | `ABBY_ctrlgrpnow_I20TRCNPRDCTCBC.pkl` | linear |
| `k_l1` | `ABBY_ctrlkl1_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_l2` | `ABBY_ctrlkl2_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_l3` | `ABBY_ctrlkl3_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s1` | `ABBY_ctrlks1_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s2` | `ABBY_ctrlks2_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s3` | `ABBY_ctrlks3_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s4` | `ABBY_ctrlks4_I20TRCNPRDCTCBC.pkl` | log10 |
| `kmax` | `ABBY_ctrlkmax_I20TRCNPRDCTCBC.pkl` | linear |
| `leaf_long` | `ABBY_ctrlleaflong_I20TRCNPRDCTCBC.pkl` | linear |
| `q10_mr` | `ABBY_ctrlq10mr_I20TRCNPRDCTCBC.pkl` | linear |

### Diagnostic contract

- Targets: `GPP`, `ER`, `SR`, `HR_TOTAL`, `LITFALL`, `LITTER_SOIL_C_TOTAL`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`, `SOIL3C`, and `SOIL4C`.
- `HR_TOTAL` is the hourly sum of `CWDC_HR`, `LITR1_HR`--`LITR3_HR`, and `SOIL1_HR`--`SOIL4_HR` before temporal aggregation.
- `LITTER_SOIL_C_TOTAL` is the hourly sum of `LITR1C`--`LITR3C` and `SOIL1C`--`SOIL4C`, excludes `CWDC`, and is labeled `Total SOC`.
- For every member and target, calculate the arithmetic mean and population standard deviation (`ddof=0`) over exactly 61,320 no-leap hourly samples from 2018--2024. Fluxes remain sampled daily-equivalent rates and are not accumulated.
- Score: `100 * (P95 - P05) / abs(ensemble median)` with a finite nonzero median. Rank descending separately by target and statistic. Spearman correlation is secondary direction evidence only.
- Normalize parameter coordinates from embedded bounds, using log10 only for `k_l1`--`k_l3` and `k_s1`--`k_s4`. Plot all members and connect ten equal-count bin medians; never fit or extrapolate a response surface.
- Compensation mappings are `k_l1`/`LITR1`, `k_l2`/`LITR2`, `k_l3`/`LITR3`, and `k_s1`--`k_s4`/`SOIL1`--`SOIL4`, using corresponding pool C, actual regulated `K_*`, and pool HR.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User responses and approval | Initial package: `I approved this complete package. In addition, I'll give you two retry budgets for preflight and diagnostic run respectively, no need for user approval for before consuming all retry budegts.` Clarification: `Yes.` Revised-package approval: `Revised package approved, out of sandbox execution approved.` Recorded at `2026-09-08T12:54:35-07:00`. |
| Goal and stop | Implement and close the two-work-unit ABBY OAT package. Continue through terminal accounting, immutable-gate evaluation, four-record validation, and the authorized closeout commit; checkpoint only for exhausted authority or an out-of-contract decision. |
| HPC system | Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; account/partition `chopinsong`/`standard`; compute environment `OLMT_puma`. |
| Output/storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter004_abby_oat/`, containing `preflight/`, `diagnostic/`, hidden result staging, and atomically published `results/`. Creation is authorized. Retain without automatic deletion or backup; `/xdisk` is temporary/unbacked and expiration is unverified because the non-PI query is unavailable. |
| Lifecycle authority | Initialization, preparation, tracked implementation and documentation, external-directory creation, independent read-only review, compute-node preflight and diagnostic, submission, monitoring, accounting, evaluation, records, validation, and closeout. |
| Initial resources | Each work unit: one node/task, six CPUs, implied 30 GB, two hours. |
| Retry budgets | Two retries after the initial attempt for each work unit; maximum three preflight and three diagnostic submissions. Autonomous retry requires classified terminal evidence and rationale. Corrections may restore locked wrapper/import/receipt/manifest/interface/calculation behavior or address scheduler/resource failure, but may not change inputs, method, targets, score, interpretation, or gates. Changed material receives static checks and independent re-review. Retry resources may rise only to eight CPUs, implied 40 GB, and four hours. Query failures and reconciled no-job submissions do not consume attempts. Genuine input/data/schema gate rejection or any change outside the contract requires fresh approval. This supersedes the earlier after-every-retry checkpoint; ask only after the applicable budget is exhausted or no in-contract retry exists. |
| Monitoring | Immediate identity check, then one persistent state-change detector at 300-second cadence using the same runtime session handle and suppressing unchanged output. If that exact mechanism demonstrably fails, record it narrowly and use one materially different runtime-supported bounded wait strategy. Reconcile every job through job-scoped `sacct`; empty `squeue` is not completion. |
| Cancellation | Only recorded Iter004 job IDs and only for a proven universal pre-execution defect or explicit user direction. |
| Outside-sandbox authority | `sbatch` for the two initial submissions and four in-budget retries; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the recorded conditions. |
| Closeout | One tightly scoped closeout commit is authorized for Iter004 code, documentation, execution material, and records. Generated outputs remain outside Git. |

## Declared Diagnostic Inputs and Evidence

- Static bootstrap found all 14 distinct, readable protocol-4 pickle files, each approximately 2.208 GB, all 14 historical configs/range files, and the control NetCDF. Full hashes and content/schema validation are deferred to the compute-node preflight.
- Bootstrap repository identity: `6870e60a28cd1de87307e56bff915f7358c61908` on `feature/ELM_diagnostics`, clean worktree.
- Bootstrap capacity: `/xdisk/chopinsong` 17.4/19.5 TB; group standard usage 234/3290 CPUs and 1.14/16.998 TB memory. Allocation expiration remains unverified.

## Acceptance Gates and Decision Rule

- Input: exact mappings only; reject path components, glob syntax, duplicates, omissions, extras, and unlisted files. Each pickle must be ABBY, single-parameter, 100-member, bounded, finite, and consistent with its coordinate.
- Time/output: every required raw variable must be unambiguous `time x member`; all cases must have exactly equal 61,320-sample hourly `taxis`; all primary and derived values must be finite and shape-compatible. No repairs or dropped members.
- Calculation: deterministic fixture covers orientation, hourly sums before aggregation, `ddof=0`, linear/log normalization, ten-member bins, quantiles, score/rank direction, and seven compensation mappings.
- Artifacts: exact row and PNG counts stated above, complete curve provenance, and hash-complete internally consistent receipts/manifests.
- Review/accounting/records: independent review resolves blocking findings, all submitted jobs are terminally accounted, and report/summary/registry/handoff agree.
- Changes requiring fresh authorization: any input, method, target, score, interpretation, gate, output-root, cancellation-scope, resource-cap, or retry-budget expansion.

## Provenance and Job Ledger

| Work unit | Canonical material | Submitted material | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- |
| preflight | wrapper `e71e5352`; tool `d952b7dc`; fixture `69161464`; config `f7638454` | byte-identical submitted wrapper/config | `.../preflight/attempt_1`; `slurm_23830156.out/err` | `23830156` | `COMPLETED 0:0`; 00:02:00; 01:10.882 CPU; 30.00/30 GB | detector session `89518`, outcome `finished` at queue-to-accounting handoff; receipt/manifest pass; retries remaining: 2 |
| diagnostic | wrapper `8bf29c5e`; tool `d952b7dc`; validator `77b45aa`; config `24a88e97` | byte-identical submitted wrapper/config | `.../diagnostic/attempt_1`; `slurm_23830259.out/err` | `23830259` | `COMPLETED 0:0`; 00:02:11; 01:39.545 CPU; 31,456,380 K peak RSS | detector session `43613`, outcome `finished` at queue-to-accounting handoff; output manifest pass; retries remaining: 2 |

## Independent Read-Only Review

- Reviewer: independent read-only `/root/iter004_review`
- Outcome: initial `block`; corrected re-review `pass` at `2026-09-08T13:23:50-07:00`.
- Findings: implement exact top-level pickle-directory membership and prevent replacement/mixing of preflight receipt/manifest artifacts. Both corrections were made within the immutable input and publication contract before any job submission.
- Re-review evidence: tool `d952b7dc55ede7bee89459b59efec378458deecccc3714ca13b9c570d80e1451`; exact directory membership and fresh staged receipt/manifest publication verified; canonical/submitted pairs byte-identical; `bash -n` and `git diff --check` pass.
- Focused diagnostic launch review: `pass_with_concerns` at `2026-09-08T13:38:41-07:00`. Config `24a88e97`, manifest `7c92ea9e`, wrapper `8bf29c5e`, tool `d952b7dc`, validator `77b45aa`, result absence, and initial resources pass. The only concern was stale handoff template/materialization wording; corrected before submission. The preflight memory watch is retained without changing the locked initial diagnostic allocation.

## Execution and Diagnostics

- Static validation: `bash -n`, canonical/submitted `cmp`, exact refreshed hashes, and `git diff --check` passed after correction at `2026-09-08T13:21:28-07:00`. Repository Python is deferred to the compute-node preflight.
- Preflight: job `23830156` submitted at `2026-09-08T13:24:33-07:00` with the locked command from the approved attempt-one directory. Immediate identity confirmed `PENDING`/Priority, standard/chopinsong, one task, six CPUs, 30 GB, two hours, and the exact work directory.
- Preflight result: `COMPLETED 0:0` in 00:02:00 with 01:10.882 CPU and 30.00/30 GB peak memory. `validation_receipt.json` and immutable input manifest `7c92ea9e0cd94b6657ea0926611ebbac6f4fe879947ee16826f1f0563d9b2082` pass all 14-case, 1,400-member, 61,320-hour, required-variable, time-axis, native-marker, and fixture gates. No retry was consumed.
- Diagnostic: attempt-one job `23830259` submitted at `2026-09-08T13:40:32-07:00` from the approved run directory with manifest `7c92ea9e`. Immediate identity confirmed PENDING/Priority, standard/chopinsong, one task, six CPUs, 30 GB, two hours, and the exact work directory.
- Diagnostic result: job `23830259` completed `0:0` in 00:02:11 with 01:39.545 CPU and 31,456,380 K peak RSS. The application and artifact validator both passed; no retry was consumed.
- Publication: atomic `results/` contains 14 parameter rows, 1,400 member rows, 364 finite score rows, 40,040 response-curve rows, and 35 PNGs. Output manifest `9d4308d04b68e49a816ebb23e6162703165a3dca9d810e4cc958f714ea86eca2` pins all 39 payload artifacts and input manifest `7c92ea9e`.
- Accounting reconciliation at `2026-09-08T13:51:00-07:00` found both jobs absent from `squeue` and terminal in job-scoped `sacct`: preflight `23830156 COMPLETED 0:0`; diagnostic `23830259 COMPLETED 0:0`.
- A platform-forced interruption occurred after preflight closeout and before diagnostic configuration materialization. On resumption, the agent recovered from this report, `CURRENT.md`, Git state, external artifacts, and scheduler accounting; no duplicate submission or partial diagnostic config existed.

## Validation, Evaluation, and Decision

- Canonical objective: Rank ABBY range-wide OAT responses for 13 carbon targets across 14 separately perturbed parameters.
- Canonical bounded scope: 14 exact historical pickles; 1,400 members; 2018-2024 hourly means and population standard deviations; descriptive OAT only.
- Overall acceptance result: `pass`.
- Artifact validation: `ITER004_DIAGNOSTIC_PASS parameters=14 member_rows=1400 score_rows=364 figures=35` and `ITER004_ARTIFACT_VALIDATE_PASS rows=41818 figures=35`. All 26 target/statistic groups contain each rank 1--14 exactly once; all scores are finite.
- Representative visual inspection: the mean-score heatmap is populated and legible, and the `k_s4`/`SOIL4` compensation figure contains all three declared response series for both statistics.
- Top-ranked results: `leaf_long` ranks first for the mean and temporal standard deviation of GPP and ER, and for the mean of SR, HR_TOTAL, and LITFALL. `act25` ranks first for temporal variability of SR, HR_TOTAL, and LITFALL. The matched decomposition rates rank first for the mean of their corresponding litter/soil pools, except total litter-plus-soil C is led by `k_s4`; temporal-variability leaders vary by pool. The compact summary records all 26 leaders, and `sensitivity_scores.csv` is the complete 364-row ranking table.
- Limitation: scores are conditional on these separately sampled parameter ranges and ensemble medians. `grpnow` and `kmax` varied across their declared samples but produced exactly zero score for all 26 groups. This is descriptive OAT evidence only and is not a PAWN, Sobol, joint/global sensitivity, interaction, causal, tuning, or parameter-value result.
- Decision: Accepted range-conditional descriptive OAT package; no global sensitivity, interaction, causal, tuning, or parameter-value claim.
- Next action: workflow terminal; no next iteration is proposed.

### Final closeout validator

- Identity: inline bounded shell validator using `set -eu`, fixed-string cross-record checks, registry-row uniqueness, `find`/`wc` artifact counts, `sha256sum`, `bash -n`, and `git diff --check`; executed from repository root at `2026-09-08T13:57:00-07:00`.
- Command scope: `iterations/iter004.md`, `summaries/iter004/ITER004_RESULT.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, the two canonical Slurm wrappers, and the published external result directory.
- Result: `ITER004_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=35 csv_rows=41818 terminal_jobs=2 next_plan=none`.
- Hash output: output manifest `9d4308d0`, member metrics `9c3a9eed`, parameter metadata `c96eabc8`, response curves `33d06c62`, and sensitivity scores `cbdb7d62`; all full hashes agree with the manifest and recorded evidence.

## Proposed Next-Iteration Plan (Planning Only)

The ELM diagnostic workflow is complete at Iter004 closeout. No next iteration is proposed.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter004/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout commit selected; verification follows the atomic commit
