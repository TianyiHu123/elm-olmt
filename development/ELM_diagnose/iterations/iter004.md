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
- Next action: Iter004 remains terminal; the planning-only Iter005 proposal below requires a fresh consolidated kickoff package and approval.

### Final closeout validator

- Identity: inline bounded shell validator using `set -eu`, fixed-string cross-record checks, registry-row uniqueness, `find`/`wc` artifact counts, `sha256sum`, `bash -n`, and `git diff --check`; executed from repository root at `2026-09-08T13:57:00-07:00`.
- Command scope: `iterations/iter004.md`, `summaries/iter004/ITER004_RESULT.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, the two canonical Slurm wrappers, and the published external result directory.
- Result: `ITER004_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=35 csv_rows=41818 terminal_jobs=2 next_plan=none`.
- Hash output: output manifest `9d4308d0`, member metrics `9c3a9eed`, parameter metadata `c96eabc8`, response curves `33d06c62`, and sensitivity scores `cbdb7d62`; all full hashes agree with the manifest and recorded evidence.

## Proposed Next-Iteration Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Proposed sequential ID and work type: iter005, implementation.
- Objective: extend the reusable ABBY OAT diagnostic with explicit target selection, observation references, independently selected compensation analysis, accumulated potential/N/P-limited heterotrophic-respiration pathways, and leaf/fine-root litter-flux stoichiometry.
- Hypothesis: observation context will show whether the separately perturbed ensembles bracket observed SR summary behavior; accumulated pathway diagnostics will expose how parameter perturbations alter potential decomposition and separate N/P scaling; flux-weighted litter C:N and C:P will reveal stoichiometric responses without unstable averaging of hourly ratios.
- Interpretation boundary: retain the baseline-conditioned, range-dependent OAT interpretation. Do not call results PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal effects, optimization, or parameter-value recommendations. Observation lines are contextual and do not enter the OAT score.

### Proposed inputs, dependencies, and trust assumptions

- Reuse exactly the 14 ABBY historical sensitivity pickles validated by Iter004 beneath /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/ABBY/pklfiles, with the same one-parameter, 100-member mapping:
  - act25:ABBY_ctrlact25_I20TRCNPRDCTCBC.pkl
  - br_mr:ABBY_ctrlbrmr_I20TRCNPRDCTCBC.pkl
  - grperc:ABBY_ctrlgrperc_I20TRCNPRDCTCBC.pkl
  - grpnow:ABBY_ctrlgrpnow_I20TRCNPRDCTCBC.pkl
  - k_l1:ABBY_ctrlkl1_I20TRCNPRDCTCBC.pkl
  - k_l2:ABBY_ctrlkl2_I20TRCNPRDCTCBC.pkl
  - k_l3:ABBY_ctrlkl3_I20TRCNPRDCTCBC.pkl
  - k_s1:ABBY_ctrlks1_I20TRCNPRDCTCBC.pkl
  - k_s2:ABBY_ctrlks2_I20TRCNPRDCTCBC.pkl
  - k_s3:ABBY_ctrlks3_I20TRCNPRDCTCBC.pkl
  - k_s4:ABBY_ctrlks4_I20TRCNPRDCTCBC.pkl
  - kmax:ABBY_ctrlkmax_I20TRCNPRDCTCBC.pkl
  - leaf_long:ABBY_ctrlleaflong_I20TRCNPRDCTCBC.pkl
  - q10_mr:ABBY_ctrlq10mr_I20TRCNPRDCTCBC.pkl
- Reuse control parameter NetCDF /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc for native markers.
- Add the explicit observation mapping SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc. The observed file hash seen during planning is e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2 and must be recomputed at kickoff/preflight.
- Iter004 commit 1e03fdc342cc3017b175fd2680eebc9e33ad4521 and its passing input/output manifests are provenance and regression references, not substitutes for a new Iter005 preflight.
- Pickle metadata remains authoritative for parameter identity, bounds, samples, site, member count, years, variables, and time axes. Transferred configs are provenance cross-checks only; stale embedded runtime paths are never dereferenced.
- User-confirmed units and process meaning: K_CWD, K_LITR1--K_LITR3, and K_SOIL1--K_SOIL4 are s-1 and already incorporate temperature, water, and oxygen scalars, so pool C times K is potential decomposition flux in gC m-2 s-1. Litter C/N/P flux outputs have already been converted to per-day units.

### Independent command-line analysis interfaces

- Standard targets are selected only by repeated --target VARIABLE arguments. Iter005 passes GPP, ER, SR, HR_TOTAL, LITFALL, LITTER_SOIL_C_TOTAL, LITR1C, LITR2C, LITR3C, SOIL1C, SOIL2C, SOIL3C, and SOIL4C. These arguments alone control standard response atlases and heatmap columns.
- Observations are selected by repeated --observation VARIABLE:ABSOLUTE_NETCDF arguments. An observation variable must be a selected target. Iter005 supplies only SR; its mean and population temporal standard deviation appear as horizontal references only in the corresponding two SR atlases.
- Compensation figures are selected independently by repeated --compensation PARAMETER:POOL_C:K_RATE:POOL_HR mappings:
  - k_l1:LITR1C:K_LITR1:LITR1_HR
  - k_l2:LITR2C:K_LITR2:LITR2_HR
  - k_l3:LITR3C:K_LITR3:LITR3_HR
  - k_s1:SOIL1C:K_SOIL1:SOIL1_HR
  - k_s2:SOIL2C:K_SOIL2:SOIL2_HR
  - k_s3:SOIL3C:K_SOIL3:SOIL3_HR
  - k_s4:SOIL4C:K_SOIL4:SOIL4_HR
- The accumulated HR analysis is selected independently by repeated --hr-pool POOL_C:K_RATE mappings plus exactly one --hr-n-limiter FPI and --hr-p-limiter FPI_P. Iter005 supplies CWDC:K_CWD, LITR1C:K_LITR1, LITR2C:K_LITR2, LITR3C:K_LITR3, SOIL1C:K_SOIL1, SOIL2C:K_SOIL2, SOIL3C:K_SOIL3, and SOIL4C:K_SOIL4.
- Litter stoichiometry is selected independently by repeated --litter-ratio LABEL:C_FLUX:N_OR_P_FLUX mappings:
  - leaf_cn:LEAFC_TO_LITTER:LEAFN_TO_LITTER
  - leaf_cp:LEAFC_TO_LITTER:LEAFP_TO_LITTER
  - froot_cn:FROOTC_TO_LITTER:FROOTN_TO_LITTER
  - froot_cp:FROOTC_TO_LITTER:FROOTP_TO_LITTER
- Omitting an interface family disables only that family. Reject duplicate labels/mappings, unknown targets, incomplete interface families, observation mappings outside the selected targets, path components where exact basenames are required, and any production arguments that differ from the passing manifest.
- Derived target formulas remain named code-side definitions; command-line arguments select them but may not supply arbitrary expressions. Preflight derives the required raw-variable union from every requested family.

### Locked proposed calculations and plots

- Preserve Iter004 standard statistics and score: arithmetic mean and population temporal standard deviation over exactly 61,320 no-leap hourly samples from 2018--2024; score 100 * (P95 - P05) / abs(ensemble median); descending ranks by target/statistic; linear/log parameter coordinates and ten equal-count bin medians unchanged.
- For SR observation references, convert with the existing observation unit logic, align unique hourly timestamps to the model's 2018--2024 no-leap window, reject invalid/negative SR consistently with the existing loader, and calculate mean and population standard deviation over finite overlapping observations. Record coverage and values in observation_summary.csv. Do not use SR_err or modify model statistics/scores.
- For each hour and member, calculate potential_pool = poolC * K_pool in gC m-2 s-1; N_limited_pool = FPI * potential_pool; and P_limited_pool = FPI_P * potential_pool. Require finite FPI and FPI_P in [0,1]. Sum the eight pools and accumulate each pathway as sum(hourly flux * 3600 s) in gC m-2 over 2018--2024.
- Produce one 14-panel accumulated-HR atlas. Each parameter panel shows all 100 member values lightly and three ten-bin median lines for potential, N-limited, and P-limited accumulated HR on a raw gC m-2 y-axis. Do not plot actual total HR; under the declared process relationship it is the hourly minimum of the three pathways.
- For hourly litter ratios, calculate member-wise C-flux/N-or-P-flux only where numerator and denominator are finite and the denominator is positive. Ratios are mass ratios (gC/gN or gC/gP); the common per-day time unit cancels. Plot ensemble mean plus/minus population standard deviation, leave unsupported hours as gaps, record valid-member support, and do not interpolate or replace denominators.
- For each member's parameter-response litter ratio, first convert each daily-equivalent elemental flux to hourly mass by dividing by 24, sum across all 61,320 hours, and calculate total C / total N or total P. Require a finite positive accumulated denominator for every member. Plot member points and ten-bin medians across each parameter range.
- Produce four 14-panel hourly litter-ratio atlases and four 14-panel flux-weighted parameter-response atlases.
- Core Iter004 response tables must remain byte-identical when regenerated from the same inputs and ordered 13-target list. Observation references change only the two SR figure renderings; specialized families do not enter or redefine the core 13-target sensitivity rankings.

### Bounded scope, work units, and exclusions

- Extend development/ELM_diagnose/tools/oat_sensitivity.py and its documentation; create only Iter005-specific wrappers, configs, fixtures, and validators under development/ELM_diagnose/slurm/iter005 after kickoff approval. Leave all Iter004 code, Slurm material, summaries, registry evidence, and external outputs unchanged.
- Work unit one is a compute-node preflight: validate the four interfaces, exact input membership and hashes, observation schema/time/unit support, every required time-by-member variable, FPI bounds, formulas, unit conversions, ratio support, deterministic fixtures, dynamic artifact expectations, and core-table regression contract. It publishes only a fresh receipt and immutable Iter005 input manifest.
- Work unit two is the diagnostic: consume only the passing Iter005 manifest, load one pickle at a time, retain bounded summaries, generate tables/figures in hidden staging, run the artifact validator, and atomically publish only a complete results directory.
- No ELM run, postprocessing, input repair, member/time dropping, surrogate, PAWN/Sobol analysis, interaction inference, optimization, tuning, or parameter-value recommendation is in scope. Iter004 results are never overwritten.

### Tentative acceptance gates and decision rule

- Input gate: all exact 14 pickles, control NetCDF, and explicit SR observation exist, are readable, and match newly recorded hashes; the pickle directory has no missing or extra top-level pickle; every case remains ABBY, single-parameter, 100-member, bounded, finite, and exactly 2018--2024 hourly.
- Interface gate: the passing manifest pins the ordered 13 targets, one observation, seven compensation mappings, eight HR-pool mappings and two limiters, and four litter-ratio mappings. Each family independently controls only its declared outputs and required variables.
- Observation gate: SR has unique hourly timestamps, finite valid overlap in 2018--2024, recognized/convertible units, and recorded count/range/mean/population SD. Invalid supplied observations reject preflight; absent unrequested observations create no line.
- HR gate: every pool C, K, FPI, and FPI_P array is finite and unambiguous time by member; K is treated as s-1; limiters remain in [0,1]; fixtures prove multiplication before pool/time summation, 3600-second integration, exact eight-pool totals, and N/P pathway calculations.
- Stoichiometry gate: all six distinct litter C/N/P flux arrays are shape-compatible and use their postprocessed daily-equivalent units; fixtures prove divide-by-24 accumulation, member-wise hourly masking, population spread, flux-weighted total ratios, support accounting, and ten-bin response curves. Every member has a finite positive accumulated N/P denominator.
- Regression gate: parameter_metadata.csv (14 rows), member_metrics.csv (1,400 rows), sensitivity_scores.csv (364 rows), and response_curves.csv (40,040 rows) reproduce the four Iter004 artifact hashes exactly.
- New table gate: observation_summary.csv has one SR row; hr_pathway_metrics.csv has 37,800 parameter/member/pathway/pool-or-total rows; hr_pathway_curves.csv has 420 total-pathway bin rows; litter_ratio_member_metrics.csv has 5,600 rows; litter_ratio_timeseries.csv has 3,433,920 parameter/ratio/hour rows with explicit valid-member counts; and litter_ratio_curves.csv has 560 bin rows.
- Figure gate: exactly 44 PNGs exist: 26 standard response atlases, two heatmaps, seven compensation figures, one accumulated-HR atlas, four hourly litter-ratio atlases, and four flux-weighted litter-ratio response atlases.
- Publication/review/accounting/record gate: manifests are hash-complete and internally consistent; no partial result is published; independent review passes or concerns are resolved; every job is terminally reconciled with job-scoped accounting; and iteration report, summary, registry, and handoff agree.
- Pass decision: accept only as a validated, range-conditional descriptive OAT and pathway/stoichiometry package. Any failed immutable gate rejects the affected work unit and prevents partial publication or scientific interpretation.

### Proposed site, resources, retry, cancellation, and stop boundaries

- Proposed site: Puma using development/hpc/puma.md, standard/chopinsong, and OLMT_puma on compute nodes. Reconfirm host, account/partition access, capacity, storage, and dependency availability during kickoff bootstrap.
- Proposed output root: /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter005_abby_oat_extended, with preflight/attempt_N, diagnostic/attempt_N, hidden staging, and atomic results. Creation and retention require kickoff approval; xdisk remains temporary and unbacked, with no automatic deletion or backup.
- Proposed initial resources: one node/task and eight CPUs (40 GB) for each work unit; two hours for preflight and four hours for diagnostic. The higher memory floor reflects Iter004's approximately 30 GB peak plus the added raw-variable and ratio summaries.
- Proposed retry budget: two retries after the initial attempt for each work unit. Autonomous retry is limited to classified scheduler/resource failure or a minimal correction that restores the locked interfaces, publication behavior, or calculation gates without changing inputs, formulas, targets, mappings, interpretation, or acceptance thresholds. Material changes receive static checks and independent re-review. Retry resources may rise only to 12 CPUs (60 GB) and six hours. Genuine input/data/schema/scientific gate rejection, exhausted budget, or any scope/method change requires fresh approval.
- Proposed monitoring: immediate job-identity validation followed by one retained, runtime-supported state-change monitor at a 300-second cadence, with unchanged-state output suppressed; queue handoff must be reconciled through job-scoped sacct. Query or transport failure means unknown state, not completion or retry authority.
- Proposed cancellation: only recorded Iter005 job IDs, and only for explicit user direction or a proven universal pre-execution defect covered by the approved contract; verify terminal accounting afterward.
- Stop boundary: continue through preflight, diagnostic, evaluation, four-record validation, and the kickoff-selected closeout branch. Stop earlier only for exhausted authority, an immutable gate rejection with no in-contract correction, or a decision outside the approved scope. No next iteration is proposed automatically.

### Expected evidence, artifacts, records, and authorization boundary

- Expected evidence includes exact source/config/submitted hashes and byte identity, input and output manifests, validation receipt, observation coverage, fixture output, core regression hashes, table/figure counts, representative visual checks, job IDs/logs/terminal accounting/resources, reviewer identity/findings, and a compact interpretation that retains the OAT boundary.
- After kickoff approval, create iterations/iter005.md, development/ELM_diagnose/slurm/iter005, the approved external work-unit directories, and later summaries/iter005 plus registry, cumulative-summary, and handoff closeout updates. Generated data and figures remain outside Git.
- This proposal grants no Iter005 initialization, implementation, Python execution, directory creation, independent-review launch, scheduler operation, retry, cancellation, or commit authority. Before any such action, perform read-only bootstrap and present one complete consolidated kickoff package containing this plan unchanged, confirmed current inputs/site/storage, exact runtime authority, monitoring mechanism, retry/cancellation terms, stop conditions, outside-sandbox request, and closeout commit choice; obtain one fresh explicit approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter004/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout commit selected; verification follows the atomic commit
