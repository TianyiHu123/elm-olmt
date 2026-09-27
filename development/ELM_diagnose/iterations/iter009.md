# iter009 - ABBY C:N pool-context nutrient-stress diagnostic

## Status

- Iteration ID: `iter009`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-26T18:18:32-07:00`
- Closed: `2026-09-26T19:01:08-07:00`
- Objective: Amend the Iter008 N/P-stress diagnostic by separating mean and temporal-variability figures, restoring observed SR context, and adding pool-C and realized pool-HR-per-C responses.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 47 metrics; 74 response endpoints per parameter; 37,812 CSV rows; 17 figures; baseline-conditioned descriptive OAT only.

## Finalized Plan

- Sequential ID and work type: `iter009`, implementation.
- Objective: amend the Iter008 N/P-stress diagnostic so mean and temporal variability are separated for HR and mineral N/P-cycle figures, observed SR context is restored, and pool-size and realized pool-respiration-per-pool-C responses are added.
- Hypothesis: pool-resolved C stocks and realized HR per unit pool C will distinguish stock responses from realized decomposition responses across the separate `cn_s1`--`cn_s4` OAT ensembles. Technical acceptance is independent of the hypothesis outcome.
- Inputs: exactly the ordered mappings `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`, `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`, `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`, and `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl`; their four configs and parameter files; the control parameter NetCDF; and contextual `SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc`. No discovery or unrelated input is permitted.
- Preserve Iter008 linear ranges, 100 members per parameter, exact 61,320-hour 2018--2024 no-leap support, arithmetic means, population temporal standard deviations (`ddof=0`), accumulated satisfaction ratios, equal-count response bins, native markers, explicit gaps, and descriptive baseline-conditioned OAT interpretation.
- Add exact pool/HR pairs `CWDC:CWDC_HR`, `LITR1C:LITR1_HR`, `LITR2C:LITR2_HR`, `LITR3C:LITR3_HR`, and `SOIL1C:SOIL1_HR` through `SOIL4C:SOIL4_HR`. Pool responses are temporal means in `gC m-2`. Realized pool respiration per unit pool C is `sum_t(pool_HR) / sum_t(pool_C)` in `day-1`; it requires a finite numerator and finite positive denominator, retains supported zero HR as zero, and preserves unsupported members as explicit gaps. Neither new family has a temporal-SD endpoint.
- The SR observation uses established unit/time handling, unique timestamps, and finite valid 2018--2024 overlap. Record coverage numerator and model-window denominator, minimum, maximum, arithmetic mean, and population temporal SD. Plot observed mean and SD only on their corresponding SR rows; observations do not alter model responses.
- Retain seven figures: FPI, microbial N/P, plant N/P, GPP, and SR. Replace the four mixed HR/N/P figures with eight separate mean/temporal-SD files. Add one eight-pool mean-C figure and one eight-pool realized-HR-per-C figure. Exactly 17 PNGs are required; the four superseded mixed files must be absent.
- Artifacts are exactly 4 parameter rows, 47 metric-definition rows, 400 member rows, 32,560 response rows, 4,800 support rows, one observation row, 37,812 CSV data rows total, 17 PNGs, and versioned input/validation/output manifests.
- Work units: one bounded compute-node preflight and one diagnostic after preflight passes. Generate in attempt-local staging and atomically publish only a complete `results/` directory.
- Exclusions: reconstructed `poolC * K`, potential/N/P-limited HR, new heatmaps, time-series plots, interactions, PAWN/Sobol/global sensitivity, optimization, tuning, parameter recommendations, causal claims, cross-site/configuration comparisons, and whole-ecosystem limitation claims.
- Acceptance requires exact input/provenance, calculation, support, artifact, visual, publication, independent-review, terminal-accounting, and record gates. Technical acceptance is independent of response direction.
- Site/resources: Puma `standard/chopinsong`, `OLMT_puma`, one node/task, 12 CPUs with standard-derived 60 GB, two hours for preflight and four hours for diagnostic. Use a retained 300-second state-change monitor and job-scoped terminal `sacct`.
- Retry/cancellation/stop boundary: one minimal preflight-only correction/rerun; one same-scope scheduler/resource retry per work unit; no application/code/interface/schema/data/dependency/numerical retry without revised approval; cancellation only for recorded Iter009 jobs under the approved conditions; stop for a material decision, identity mismatch, failed immutable gate, exhausted authority, unavailable monitoring, explicit user stop, or validated closeout.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `Complete package approved`; `2026-09-26T18:18:32-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Complete initialization through validated closeout for exactly two compute work units; stop under the finalized-plan conditions above. |
| Confirmed HPC system and site profile | Puma login host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; `standard/chopinsong`; `OLMT_puma`; module pin `micromamba/2.0.2-2` to validate in preflight. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context`; `preflight/attempt_N`, `diagnostic/attempt_N`, atomic `results`; create exact layout, retain failed attempts, never overwrite/delete/auto-backup. `/xdisk` is temporary and unbacked. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | Finalized plan above; exact four mappings and dependencies; `sum(HR)/sum(pool_C)`; 37,812 rows; 17 PNGs; descriptive OAT only. |
| Lifecycle authority | Primary agent may initialize records; implement engine and Iter009 material; create approved external paths; launch/wait for read-only reviewers; submit, monitor, account, evaluate, update records, validate, and close out. |
| Resources, monitoring and wait mechanism, and retry boundaries | 12 CPUs/derived 60 GB; 2 h preflight, 4 h diagnostic; retained 300-second state-change monitor on one handle, one materially different detached `tmux` fallback if lost; one minimal preflight correction/rerun and one scheduler/resource retry per work unit. |
| Cancellation scope | Recorded Iter009 job IDs only for identity mismatch, universal pre-execution defect, writes outside scope, contract overrun, or explicit user instruction; cancellation grants no fix/retry. |
| Outside-sandbox authority | Approved locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under stated conditions. |
| Closeout branch | Exactly one scoped closeout commit authorized; no push. |

## Declared Diagnostic Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| `cn_s1` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl` | Iter008-validated ELMcase | 4,121,205,317 bytes; SHA `fca486c1...f9fcc1f` | Exact current hash reproduced during preparation; preflight recheck pending |
| `cn_s2` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl` | Iter008-validated ELMcase | 4,121,205,317 bytes; SHA `40589f8c...c2297` | Exact current hash reproduced during preparation; preflight recheck pending |
| `cn_s3` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl` | Iter008-validated ELMcase | 4,121,205,317 bytes; SHA `b3d5d2aa...525f1` | Exact current hash reproduced during preparation; preflight recheck pending |
| `cn_s4` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl` | Iter008-validated ELMcase | 4,121,205,317 bytes; SHA `c68eaafb...ff6` | Exact current hash reproduced during preparation; preflight recheck pending |
| Four configs/parameter files | provenance | declared external config/parameter roots | explicit ordered mappings | current small-file hashes match Iter008 | All four configs declare vertical soil C and eight pool/HR variables |
| Control parameter NetCDF | native markers | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` | NetCDF | SHA `3876806b...1042e9` | Present and matches Iter008 |
| ABBY observation | contextual SR | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` | NEON v4 NetCDF | SHA `e5f7b679...a1fdb2` | Present and current planning hash verified |
| Repository/environment | source/runtime | repository root; `conda_envs/OLMT_puma.yml` | branch `feature/ELM_diagnostics`; kickoff `53cd94f` | environment SHA `02283ec1...878bb` | Clean at kickoff; implementation pinned by file hashes |

- Capacity evidence at kickoff: group standard 132/3290 CPUs and 660/16,998 GB; `/xdisk` 17.5/19.5 TB; group 473.5/500 GB; home 39.2/50 GB. Allocation expiration is unavailable to non-PI users.

## Acceptance Gates and Decision Rule

- Required completeness: exact four inputs/400 members/61,320 hours, eight pool/HR pairs, one SR observation, exact schemas, 37,812 CSV rows, 17 figures, manifests, reviews, and terminal accounting.
- Calculation gate: existing Iter008 calculations plus mean pool C, exact `sum(HR)/sum(pool_C)`, finite-positive denominator support, contextual observation mean/SD, and deterministic fixtures.
- Artifact/visual gate: separated HR/N/P mean and SD figures; correct SR references; all eight pools in both new figures; superseded files absent; legible units, markers, legends, and panels.
- Decision rule: pass only if every immutable technical gate passes; scientific direction does not determine acceptance.
- Changes requiring fresh authorization: inputs, formula, variables, figures, counts, output root, gates, interpretation, maximum resources, retry count, cancellation scope, or closeout branch.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter009.slurm` / `657526ee` | submitted script byte-identical `657526ee`; config byte-identical `76fd1aec` | `.../preflight/attempt_1`; logs `slurm_%j.out/.err` | tool `7fe6caa0`; exact inputs/configs/parameters/control/observation/environment | kickoff `53cd94f`; dirty source pinned by hashes | `24019322` | `COMPLETED 0:0`; elapsed 00:01:12; batch MaxRSS 20,682,404 K | identity matched; monitor session `89631` outcome `handoff`; terminal `sacct` complete; no retry |
| diagnostic | `diagnostic_iter009.slurm` / `efb7f9fb` | submitted script byte-identical `efb7f9fb`; manifest-pinned config byte-identical `5cbc71fc` | `.../diagnostic/attempt_1` | validator `20ed5174`; tool `7fe6caa0`; input manifest `bb283659` | kickoff `53cd94f`; dirty source pinned by hashes | `24019366` | `COMPLETED 0:0`; elapsed 00:01:17; batch MaxRSS 20,683,104 K | identity matched; retained corrected 300-second monitor session `45108` outcome `finished`; terminal `sacct` complete; no retry |

Monitoring outcomes are `active`, `handoff`, `failed`, `unsupported`, or `finished`. Workload state is recorded separately.

## Independent Read-Only Review

- Reviewer: `/root/iter009_review`, read-only prepared-package review.
- Reviewed source hashes: tool `7fe6caa0`, validator `20ed5174`, preflight wrapper `657526ee`, diagnostic wrapper `efb7f9fb`, preflight config `76fd1aec`, diagnostic template `f7bbd1c3`, and submitted diagnostic config `5cbc71fc`.
- Outcome: initial `block`; focused corrected-package re-review `pass` at `2026-09-26T18:37:01-07:00`.
- Findings and primary-agent response: reviewer found that response-curve rows mislabeled eight HR/pool-C metrics as dimensionless, the validator did not enforce exact headers/units/endpoint multiplicity, fixtures omitted explicit observation `ddof=0` and derived artifact-contract assertions, and two records were stale. Primary agent corrected ratio units to `day-1`, strengthened exact-schema/unit/multiplicity validation, added observation and complete derived-contract fixtures, and reconciled records. No job was submitted.
- Diagnostic-launch review: the same reviewer returned `pass` at `2026-09-26T18:46:19-07:00` after verifying terminal preflight accounting, manifest `bb283659`, receipt `04bb75ce`, all fixtures/observation summaries, config `5cbc71fc`, script `efb7f9fb`, pinned source identities, resources, guards, validator-before-atomic-publication order, and output/staging absence.
- Final result review: the same independent read-only reviewer returned `pass` with no required correction. It independently verified terminal accounting, empty stderr, all pass markers, all 23 payload hashes/sizes, every member-level `sum(HR)/sum(pool_C)` value (maximum absolute discrepancy `3.47e-18`), all 4,800 supported ratios, 400 supported numeric-zero CWD ratios, observation coverage/mean/`ddof=0` SD, all 17 original-resolution figures, absence of superseded files, every reported endpoint-bin contrast, and the descriptive OAT boundary.

## Execution and Diagnostics

- Static validation: `git diff --check`, both wrappers under `bash -n`, exact pickle rehash, declared dependency presence, output absence, and corrected canonical/submitted byte-identity checks passed. Corrected tool `7fe6caa0`; validator `20ed5174`; configs `76fd1aec`/`f7bbd1c3`.
- Preflight: job `24019322` passed on attempt one with `NUTRIENT_OAT_PREFLIGHT_PASS parameters=4 members=400 hours=61320`; input manifest `bb283659`; receipt `04bb75ce`; all locked fixture/input/observation gates pass.
- Exact submission commands: the analogous locked commands from each attempt directory returned preflight `24019322` and diagnostic `24019366`; login-shell module warnings preceded each valid parsable ID. Full diagnostic command used `SUBMISSION_CONFIG=.../diagnostic/attempt_1/submission_config.env ./submit_diagnostic_iter009.slurm </dev/null`.
- Job identity checks: preflight `24019322` and diagnostic `24019366` matched their names, `standard/chopinsong`, 12 CPUs, derived 60 GB, 2 h/4 h limits, submitted commands, workdirs, logs, and `/dev/null` stdin.
- Queue and terminal accounting: preflight parent, batch, and extern are terminal `COMPLETED 0:0`; elapsed 00:01:12, TotalCPU 00:40.856, 12 CPUs, node `r4u28n1`.
- Diagnostic accounting: parent, batch, and extern are terminal `COMPLETED 0:0`; elapsed 00:01:17, TotalCPU 00:48.687, 12 CPUs, batch MaxRSS 20,683,104 K, node `r4u04n1`. Retained monitor session `45108` finished after observing the authoritative terminal state.
- Resource diagnostics: `seff` reports 4.73% CPU efficiency and 19.72/60 GB memory (32.87%); no resource failure.
- Diagnostic resource evidence: batch peak memory was 19.72/60 GB; elapsed time was 00:01:17. This was not a resource failure.
- Failure, rejection, retry, or cancellation evidence: none.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | passing manifest/receipt, fixtures, logs, and terminal accounting | pass | every locked preflight gate passed on attempt one |
| diagnostic | yes | `NUTRIENT_OAT_DIAGNOSTIC_PASS`, `ITER009_ARTIFACT_VALIDATE_PASS`, atomic publication, output manifest `afa885d5`, 37,812 CSV rows, 17 PNGs, and independent final review | pass | every immutable execution, calculation, artifact, visual, review, and accounting gate passed |

- Overall acceptance result: `pass`.
- Artifact validation: output manifest `afa885d5` has status `pass` and covers exactly 4 parameter rows, 47 metric definitions, 400 member rows, 32,560 response rows, 4,800 support rows, one observation row, 37,812 CSV data rows, 17 PNGs, and 23 payload artifacts. All 4,800 ratios are supported, no supported zero was converted to a gap, all members have 61,320 model hours, and attempt-local staging is absent after atomic publication.
- Visual validation: all 17 full-resolution PNGs were inspected. The HR, pool-HR, N-cycle, and P-cycle means and temporal standard deviations are in separate legible figures; the SR observed mean and temporal standard deviation occur on their corresponding rows; both new pool figures contain all eight ordered pools with units and native markers; supported zero `CWDC_HR` remains visible; and all four superseded mixed figures are absent.
- The contextual ABBY SR observation has 26,264 valid hours of the 61,320-hour model window (`42.83%`), mean `7.501337`, and population temporal standard deviation `2.627639` gC m-2 day-1. It is plotted as context and does not enter model response calculations.
- Sampled-parameter-bin medians distinguish stock from realized pool respiration. From the lowest to highest sampled-parameter bins, `cn_s1` increases SOIL1C by `53.01%` while SOIL1 HR changes `-0.53%`, so realized SOIL1 HR/C falls `34.99%`. `cn_s2` changes SOIL2C, SOIL2 HR, and SOIL2 HR/C by `-3.90%`, `-4.76%`, and `-0.89%`; `cn_s3` changes the corresponding SOIL3 quantities by `-0.47%`, `-0.66%`, and `-0.18%`; and `cn_s4` changes the corresponding SOIL4 quantities by `+3.56%`, `+4.64%`, and `+1.04%`.
- Across the other matched pools, realized HR/C can respond more strongly even when the matched soil-pool ratio changes little: LITR1 HR/C rises `38.50%` under `cn_s2`, and LITR3 HR/C rises `32.18%` and `27.74%` under `cn_s3` and `cn_s4`. These are baseline-conditioned OAT endpoint-bin contrasts, not global sensitivity, interaction, causal, prescribed-rate, or threshold estimates.
- Overall decision and closeout conclusion: accepted the validated amendment. C:N perturbations can change pool stocks and realized respiration per pool C differently; the especially large `cn_s1` SOIL1 stock increase is accompanied by nearly unchanged SOIL1 HR and a lower realized HR/C ratio.
- Limitations: `/xdisk` is temporary and unbacked; allocation expiration is unavailable; scientific interpretation remains bounded by the approved OAT scope.
- Next action: workflow complete; no next iteration is proposed, and any new diagnostic requires a fresh planning package and approval.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed. The approved amendment objective is complete; any additional diagnostic question requires a fresh planning package and approval.

## Final Closeout Validator

- Identity: inline bounded validator using Python's CSV-aware standard-library parser plus shell identity, artifact, row-count, hash, submitted-copy, `bash -n`, and `git diff --check` checks; scope is the iteration report, compact result, cumulative summary, registry, current handoff, canonical/submitted execution material, and published result package.
- Result: `ITER009_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=17 csv_rows=37812 ratios_supported=4800 terminal_jobs=2 next_state=workflow_complete`.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter009/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit
