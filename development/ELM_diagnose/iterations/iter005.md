# iter005 - ABBY extended OAT pathway and stoichiometry diagnostic

## Status

- Iteration ID: `iter005`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter005_abby_oat_extended`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-08T20:19:07-07:00`
- Closed: `2026-09-09T12:37:48-07:00`
- Objective: Extend the reusable ABBY OAT diagnostic with explicit targets, SR observation context, decomposition pathways, and litter-flux stoichiometry.
- Bounded scope: 14 exact historical pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated range-conditional descriptive OAT and pathway/stoichiometry package; no global sensitivity, interaction, causal, optimization, tuning, or parameter-value claim.

## Finalized Plan

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

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Full package for iter005 approved.`; `2026-09-08T20:19:07-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Initialize, implement, execute, evaluate, and close two work units: one preflight and one diagnostic. Stop at validated closeout with no active or unaccounted job, or earlier only for exhausted authority, immutable rejection without an in-contract correction, or a fresh material decision outside the package. |
| Confirmed HPC system and site profile | Puma login host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `standard/chopinsong`; compute environment `OLMT_puma` with `micromamba/2.0.2-2`. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter005_abby_oat_extended` with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results`; creation and retention authorized; no automatic deletion or backup; xdisk is temporary and unbacked. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | The finalized plan above is immutable. Exact 14 ABBY pickles, control NetCDF, SR observation, Iter004 commit/manifests, interfaces, formulas, targets, mappings, output counts, exclusions, and pass rule are locked. |
| Lifecycle authority | Iteration initialization, preparation, tracked implementation/documentation, external-directory creation, submitted copies, independent read-only review, compute-node preflight and diagnostic, submission, agent-owned monitoring, accounting, in-contract retry, evaluation, records, validation, and closeout. |
| Resources, monitoring and wait mechanism, and retry boundaries | Initial preflight: 1 node/task, 8 CPUs/40 GB, 2 hours. Initial diagnostic: 1 node/task, 8 CPUs/40 GB, 4 hours. Two retries after the initial attempt for each work unit; retry maximum 12 CPUs/60 GB and 6 hours. Use one retained terminal-session state-change detector at 300-second cadence, suppress unchanged output, retain its handle, and reconcile terminal state with job-scoped `sacct`. |
| Cancellation scope | Initially none; after submission, only recorded Iter005 job IDs, only on explicit user direction or a proven universal pre-execution defect covered by this contract, followed by terminal reconciliation. |
| Outside-sandbox authority | `sbatch` for locked initial submissions and in-contract resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only within the recorded cancellation scope. |
| Closeout branch | One tightly scoped Iter005 closeout commit is authorized; generated outputs remain outside Git. |

## Declared Diagnostic Inputs and Bootstrap Evidence

- All and only the 14 exact ABBY pickle basenames are present beneath the locked pickle root; each is approximately 2.208 GB.
- Control parameter NetCDF SHA-256: `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9`.
- SR observation SHA-256: `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`.
- Iter004 provenance commit `1e03fdc342cc3017b175fd2680eebc9e33ad4521`; current clean bootstrap HEAD `03d03b2f6f785b1a893c90bd3799a673b7d408d9`.
- The proposed output root was absent at bootstrap.
- Capacity at bootstrap: group `210/3290` CPUs and `1.03/16.998 TB` memory in use; xdisk `17.4/19.5 TB`; home `41.4/50 GB`. Xdisk expiration is unverified because the query is PI-only.
- The isolated agent login wrapper did not expose the `module` function. Iter004 validated `micromamba/2.0.2-2` and `OLMT_puma` on compute nodes the same day; Iter005 preflight must revalidate them before substantive work.

## Acceptance Gates and Decision Rule

- Every gate and the decision rule in the finalized plan is immutable.
- Changes to inputs, formulas, targets, mappings, interpretation, gates, output root, resource caps, retry budget, or cancellation scope require fresh authorization.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight attempt 1 | wrapper `785e2bc1`; tool `d366a0d9`; fixture `e3e009e6`; archived canonical config `preflight_submission_config_attempt1.env` `31b1569f` | byte-identical submitted wrapper/config | `.../preflight/attempt_1`; `slurm_23834279.out/err` | locked inputs and `OLMT_puma` | bootstrap HEAD `03d03b2`; hash-pinned dirty source | `23834279` | `FAILED 1:0`; 00:00:24; 00:03.269 CPU; 424.41 MB/40 GB | no monitor needed after immediate terminal identity; outcome `finished`; fixture expected-value defect; retries remaining: 2 |
| preflight attempt 2 | wrapper `785e2bc1`; tool `0c7a5173`; fixture `e3e009e6`; archived canonical config `preflight_submission_config_attempt2.env` `bdfcd7d2` | byte-identical submitted wrapper/config | `.../preflight/attempt_2`; `slurm_23834351.out/err` | locked inputs and `OLMT_puma` | bootstrap HEAD `03d03b2`; hash-pinned dirty source | `23834351` | `FAILED 1:0`; 00:00:19; 00:03.291 CPU; 419.11 MB/40 GB | immediate terminal identity; outcome `finished`; second fixture expected-value defect; retries remaining: 1 |
| preflight attempt 3 | wrapper `785e2bc1`; tool `880f5f87`; fixture `e3e009e6`; current canonical config `2ab33c58` | byte-identical submitted wrapper/config | `.../preflight/attempt_3`; `slurm_23834413.out/err` | locked inputs and `OLMT_puma` | bootstrap HEAD `03d03b2`; hash-pinned dirty source | `23834413` | `COMPLETED 0:0`; 00:02:42; 02:11.583 CPU; 31.90/40 GB | detector session `27428`, outcome `finished` at queue-to-accounting handoff; receipt/manifest pass; retries remaining: 0 |
| diagnostic attempt 1 | wrapper `d5f76b4d`; tool `880f5f87`; validator `e48a817e`; config `1f326bcc` | byte-identical submitted wrapper/config | `.../diagnostic/attempt_1`; `slurm_23834468.out/err` | passing manifest `7581cafa`; Iter004 regression results | bootstrap HEAD `03d03b2`; hash-pinned dirty source | `23834468` | `COMPLETED 0:0`; 00:03:17; 02:41.786 CPU; 32.85/40 GB | detector session `93091`, outcome `handoff` after expected completed-job `squeue` invalid-ID response; `sacct` reconciled; artifact validator and atomic publication pass; retries remaining: 2 |

## Independent Read-Only Review

- Reviewer: independent read-only `/root/iter005_review`
- Initial reviewed tool hash: `bf3c9fec3c5d74b7150360842c942ab1678a4d2c470353ffb60da8e4ff53dc9d`.
- Initial outcome: `block`.
- Findings: optional families were coupled to fixed production counts; the external artifact validator ran after publication; the fixture did not explicitly prove the exact eight-pool total; and `CURRENT.md` retained stale pre-kickoff resume instructions.
- Primary-agent response: made optional-family tables/counts/figures dynamic and regression checking optional; added empty-family interface/count fixtures and exact eight-pool integration evidence; changed the diagnostic wrapper to validate a hidden staging directory before atomic rename; replaced the stale resume protocol; refreshed hashes and submitted configuration.
- Re-review outcome: `pass_with_concerns`. All four blocks are resolved. The sole concern was stale ledger hash prefixes; the ledger now records tool `d366a0d9`, wrapper `785e2bc1`, and canonical/submitted config `31b1569f`. No code re-review is required while these identities remain unchanged.
- Focused retry review: the arithmetic-only correction passed. After preserving the attempt-one canonical config separately and making the current canonical config byte-identical to attempt two, final focused re-review returned `pass` with no concerns; tool `0c7a5173`, wrapper `785e2bc1`, attempt-two config `bdfcd7d2`.
- Final-retry review: `pass_with_concerns`; arithmetic `(2, 3)`, tool `880f5f87`, wrapper `785e2bc1`, and attempt-three config `2ab33c58` pass with no code, formula, scope, interface, or gate concern. The record-only concern about the attempt-two config label is resolved above.
- Focused diagnostic launch review: execution material passed at tool `880f5f87`, wrapper `d5f76b4d`, validator `e48a817e`, config `1f326bcc`, and manifest `7581cafa`; initial outcome `block` only because two preflight record lines retained stale retry/next-action wording. Those record inconsistencies are corrected below, with execution identities unchanged.

## Execution and Diagnostics

- Static validation: `bash -n`, canonical/submitted `cmp`, pinned SHA-256 checks, and `git diff --check` pass; repository Python is deferred to compute-node preflight.
- Preflight: attempts one and two failed only their fixture expectations; final attempt three `23834413` passed all immutable gates with input manifest `7581cafa262c112e3881ecf30ef4c0f0425058e195b02de8b37002832a5592cc` and receipt `84f17f9f42b6a3d3166ae2aad51c2ff1fb738b5853810803ed16531ccd779eda`.
- Exact submission commands: all preflight attempts used `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=<attempt_N>/submission_config.env ./submit_preflight_iter005.slurm </dev/null` from the recorded run directory and returned `23834279`, `23834351`, and `23834413`.
- Diagnostic attempt one used `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=.../diagnostic/attempt_1/submission_config.env ./submit_diagnostic_iter005.slurm </dev/null` and returned job `23834468`.
- Job identity checks: all jobs matched their exact names, standard/chopinsong, approved resources, scripts, work directories, and log paths. Preflight detector session `27428` and diagnostic detector session `93091` retained their job scopes through accounting handoff.
- Queue and terminal accounting: job-scoped accounting records `23834279 FAILED 1:0`, `23834351 FAILED 1:0`, `23834413 COMPLETED 0:0`, and `23834468 COMPLETED 0:0`.
- Resource diagnostics: passing preflight used 31.90/40 GB in 00:02:42; diagnostic used 32.85/40 GB in 00:03:17 with 02:41.786 CPU.
- Diagnostic publication: generation passed with 1,400 member rows, 364 scores, and 44 figures; artifact validation passed `3,520,119` data rows and 44 figures before atomic rename to `results/`. Output manifest SHA-256 is `99d3f377f9242d85eac3c29d94ec88fc66a8b415a07d31cf6a8491306267e339`.
- Failure, rejection, retry, or cancellation evidence: both are application fixture failures caused by incorrect hand-calculated expected vectors. Attempt one exposed N/P expectations and attempt two exposed the second member's flux-weighted ratio expectation (`3`, not `2`). Each correction restored only the locked fixture math; no input, formula, target, mapping, gate, or scientific scope changed. The final authorized preflight retry passed; no preflight retry remains.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Work-unit results: preflight `pass` on authorized attempt three after two classified fixture-expectation corrections; diagnostic `pass` on attempt one; publication, review, terminal-accounting, artifact, regression, and record gates pass.
- Completeness and provenance: the published package contains exactly 14 parameter rows, 1,400 member rows, 364 sensitivity-score rows, 40,040 response-curve rows, one observation row, 37,800 HR-pathway rows, 420 HR-curve rows, 5,600 litter member-ratio rows, 3,433,920 litter time-series rows, 560 litter-curve rows, and 44 PNGs. The output manifest is `99d3f377f9242d85eac3c29d94ec88fc66a8b415a07d31cf6a8491306267e339`; the four core table hashes reproduce Iter004 exactly.
- Observation context: 26,264 valid observed SR hours give mean `7.501337` and population temporal SD `2.627639` gC m-2 day-1. Across the 1,400 model members, SR means span `0.622847`--`3.076300` and temporal SDs span `0.134623`--`0.586511`, so neither observed summary is bracketed. The observation remains contextual and does not enter the OAT score.
- Pathway result: accumulated total potential HR spans `1,912.427`--`13,685.020` gC m-2 and N-limited HR spans `1,710.962`--`11,512.151` gC m-2. P-limited totals equal potential totals for all 1,400 parameter/member pairs, consistent with the plotted overlap; no actual-HR claim is made.
- Stoichiometry result: all four hourly ratios retain complete 100-member support at all 858,480 parameter/hour rows per ratio. Flux-weighted ratios are constant across all 1,400 parameter/member cases for each ratio: leaf C:N `70`, leaf C:P `1050`, fine-root C:N `42`, and fine-root C:P `1000`; these outputs therefore show fixed stoichiometry rather than a parameter response in the declared ensembles.
- Standard OAT regression: rank-one results remain identical to Iter004. `leaf_long` leads GPP and ER for both statistics and mean SR/HR_TOTAL/LITFALL; `act25` leads temporal variability for SR/HR_TOTAL/LITFALL; matched decomposition rates lead the corresponding mean pools except total litter-plus-soil C is led by `k_s4`.
- Representative visual checks: `ABBY_SR_mean_response_atlas.png`, `ABBY_accumulated_hr_pathways.png`, and `ABBY_leaf_cn_hourly_ratio_atlas.png` have complete 14-panel layouts, readable axes/legends, expected observation/pathway/support content, and no missing or malformed panels. Scientific-offset notation in the near-constant ratio panels is retained and interpretable.
- Overall decision and closeout conclusion: Accepted validated range-conditional descriptive OAT and pathway/stoichiometry package; no global sensitivity, interaction, causal, optimization, tuning, or parameter-value claim.
- Limitations: conclusions are conditional on the declared parameter ranges and separate OAT ensembles. The SR mismatch is a contextual diagnostic, the P-limited/potential identity reflects these inputs, and constant litter ratios do not establish insensitivity outside the declared flux construction or ranges. `/xdisk` is temporary and unbacked, and allocation expiration remains unverified because the query is PI-only.
- Next state: workflow intentionally stopped after Iter005 closeout; no next iteration is proposed automatically.

### Final closeout validator

- Identity: inline bounded shell validator using `set -eu`, fixed-string cross-record checks, registry-row uniqueness, artifact counts and hashes, `bash -n`, submitted-copy equality, and `git diff --check`; executed from the repository root at `2026-09-09T12:37:48-07:00`.
- Command scope: `iterations/iter005.md`, `summaries/iter005/ITER005_RESULT.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, Iter005 canonical/submitted execution material, and the published external result directory.
- Result: `ITER005_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=44 data_rows=3520119 terminal_jobs=4 next_state=intentionally_stopped`.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed automatically.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter005/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout commit selected; verification follows the atomic commit
