# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none; proposed `iter008` is not initialized
- Most recent closed iteration: `iter007`
- Status: `not_initialized`
- Phase: `ready_for_kickoff_approval`
- Active job scope: none. Preflight jobs `23882414`, `23882462`, and `23882524`, and diagnostic job `23882574`, are terminally accounted.
- Active monitoring: none; all retained monitor handles ended and job-scoped accounting is complete.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-25T20:00:23-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter007`
- Work type: `implementation`
- Objective: Apply the complete Iter005/Iter006 extended OAT diagnostic to 13 ABBY vertical-soil-carbon one-parameter ensembles with explicit dynamic parameter mapping.
- Bounded scope: 13 exact ABBY vertical-soil-carbon pickles; 1,300 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated standalone ABBY vertical-soil-carbon range-conditional descriptive OAT and pathway/stoichiometry package; no PAWN/Sobol/global sensitivity, interaction, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site claim.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter007.md`.
- Compact result: `development/ELM_diagnose/summaries/iter007/ITER007_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/results`.
- Input manifest SHA-256: `bf459adab7ce1ed4400ba14a4b217381ecad812510c94164992d54bfe887fd49`.
- Output manifest SHA-256: `61a85ab5395a10865996faea1ad425229a594439e53d210941798b45688935ce`.
- Passing work: preflight `23882524 COMPLETED 0:0`; diagnostic `23882574 COMPLETED 0:0`; hardened validator passed 3,268,682 rows and 44 figures before atomic publication.
- Classified failures: preflight `23882414` and `23882462` failed before Python on the mistyped pinned postprocessing digest. Attempt two also corrected a latent newline-sensitive parameter reader. After explicit authorization, the corrected final retry passed.
- Review: independent read-only `/root/iter007_review`; preparation, retry, launch, artifacts, calculations, and corrected pathway metrics passed final review.
- Mean fluxes in gC m-2 day-1: potential, P-limited, N-limited, model SR, observed SR, and actual model HR_TOTAL are `11.782900`, `3.834530`, `2.865373`, `1.342808`, `7.501337`, and `0.785350`. The first three and observed SR differ from model SR by `+777.48%`, `+185.56%`, `+113.39%`, and `+458.63%`; N limitation reduces potential HR by `75.68%`.
- Observation coverage is 26,264/61,320 hours (`42.83%`). All four litter ratios retain 1,300 supported and zero rejected members.
- `decomp_depth_efolding` has `0.30%`--`0.57%` flux-summary response spreads and ranks 8th--11th for aggregated soil-C summaries over its sampled range.

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. Observation context does not enter screening scores and is not exactly time matched. Constructed HR pathways are not actual model HR.
- Heatmap annotation contrast is weak in low-valued cells. Axis-offset notation magnifies machine-scale scatter in effectively constant litter-ratio panels; numerical tables are authoritative.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the query is PI-only.
- Next state: the finalized planning-only Iter008 proposal is recorded below. Iter008 remains uninitialized and requires one fresh consolidated kickoff/runtime package and explicit approval before any implementation or execution.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter007.md`, its compact result, and the Iter007 registry row.
3. Treat Iter007 execution material, reports, manifests, results, and registry evidence as immutable closed provenance.
4. Use the identical finalized Iter008 proposal below to prepare one consolidated kickoff/runtime package; obtain fresh explicit approval before initialization or execution.

## Proposed Next-Iteration Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Proposed sequential ID and work type: `iter008`, implementation.
- Proposed run slug: `elm_diagnose_iter008_abby_ctrlvertc_cn_oat`.
- Objective: characterize how separate perturbations of `cn_s1`--`cn_s4` affect realized decomposition, microbial N/P demand satisfaction, plant N/P demand satisfaction, ecosystem carbon fluxes, and mineral nutrient cycling in the ABBY vertical-soil-carbon configuration.
- Hypothesis: changing soil-pool C:N ratios alters microbial nutrient demand and may relieve N or P limitation of decomposition; any released mineral nutrients may also improve plant nutrient-demand satisfaction and GPP.
- Interpretation boundary: results are baseline-conditioned, range-dependent descriptive OAT responses. They are not PAWN, Sobol, joint/global sensitivity, parameter interaction, causal mediation, optimization, calibrated parameter values, tuning recommendations, or proof that the whole ecosystem is N limited.
- Technical acceptance does not depend on whether the hypothesis is supported. The diagnostic may support, contradict, or leave it unresolved.

### Explicit inputs, dependencies, and trust assumptions

- Use exactly four explicit mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`:
  - `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`
  - `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`
  - `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`
  - `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl`
- Consume only those mappings. Perform no discovery or glob expansion; reject duplicate mappings, path components, missing mapped files, parameter mismatches, and substituted basenames. Unrelated files in the shared directory are not Iter008 inputs and are ignored rather than copied or linked into a separate input directory.
- Planning-time shell inspection records 100 members per ensemble; declared linear ranges are `9`--`18` for `cn_s1` and `cn_s2`, and `7`--`16` for `cn_s3` and `cn_s4`. Each pickle is `4,121,205,317` bytes. Refresh sizes and hashes at kickoff and preflight.
- All four transferred configs declare site `ABBY`, `use_vertsoilc = .true.`, CNP biogeochemistry with RD nutrient competition, and hourly 2018--2024 output. Configs and parameter files are provenance cross-checks, not runtime dependencies; stale embedded Perlmutter paths are never dereferenced.
- Use `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` only for native-value markers. No observation input is included.
- Pickle metadata is authoritative for case identity, parameter, selector, bounds, samples, site, member count, years, variables, and time axis. Safe deserialization, exact content, units, signs, finiteness, and dimensionality remain unverified until an authorized Puma compute-node preflight.
- Preflight must require site `ABBY`, one declared varied parameter and 100 finite in-range samples per pickle, embedded bounds matching the declared ranges, exactly 61,320 no-leap hourly samples for 2018--2024, and every required array normalizing unambiguously to `61,320 x 100` time by member.

### Locked calculations and response-curve contract

- For every raw hourly variable and member, calculate the arithmetic temporal mean and temporal population standard deviation (`ddof=0`) over 61,320 hours. Temporal standard deviation is variability, not uncertainty. Do not accumulate hourly fluxes for these mean and standard-deviation curves.
- Calculate member-level microbial satisfaction from separately integrated numerator and denominator:
  - N: `sum(ACTUAL_IMMOB * dt) / sum(POTENTIAL_IMMOB * dt)`.
  - P: `sum(ACTUAL_IMMOB_P * dt) / sum(POTENTIAL_IMMOB_P * dt)`.
- Calculate member-level plant satisfaction in the same way:
  - N: `sum(SMINN_TO_PLANT * dt) / sum(PLANT_NDEMAND_COL * dt)`.
  - P: `sum(SMINP_TO_PLANT * dt) / sum(PLANT_PDEMAND_COL * dt)`.
- Validate exact numerator/denominator units and sign conventions before applying these ratios. Require a finite positive accumulated denominator. Preserve unsupported members as explicit gaps with reasons; never replace them with zero or clip ratios to `[0,1]` or 100%. Values above one remain visible and require interpretation rather than alteration.
- Require finite raw arrays where the declared metric requires them, nonnegative immobilization/demand/uptake arrays under the locked ratio semantics, and finite `FPI` and `FPI_P` in `[0,1]`. Signed `NET_NMIN` and `NET_PMIN` remain permitted.
- For each endpoint retain all 100 member points and ten deterministic equal-count bins, plot bin medians over member points, and record actual and normalized parameter coordinates plus bin support. Show a native marker only when one finite native value resolves within the sampled range.
- Produce no response-spread score, ranking, or heatmap.

### Locked figure package

Publish exactly 11 ABBY-labelled PNG figures:

1. `FPI` and `FPI_P` responses.
2. Microbial N: `POTENTIAL_IMMOB`, `ACTUAL_IMMOB`, and accumulated actual/potential ratio.
3. Microbial P: `POTENTIAL_IMMOB_P`, `ACTUAL_IMMOB_P`, and accumulated actual/potential ratio.
4. Plant N: `PLANT_NDEMAND_COL`, `SMINN_TO_PLANT`, and accumulated uptake/demand ratio.
5. Plant P: `PLANT_PDEMAND_COL`, `SMINP_TO_PLANT`, and accumulated uptake/demand ratio.
6. `GPP` response.
7. `SR` response.
8. Direct model `HR` response.
9. Actual pool-HR atlas containing `CWDC_HR`, `LITR1_HR`, `LITR2_HR`, `LITR3_HR`, `SOIL1_HR`, `SOIL2_HR`, `SOIL3_HR`, and `SOIL4_HR`.
10. N-cycle context: `SMINN`, `GROSS_NMIN`, and `NET_NMIN`.
11. P-cycle context: `SOLUTIONP`, `GROSS_PMIN`, and `NET_PMIN`.

- Figures 1--8 and 10--11 contain all four `cn_s*` responses. Raw hourly variables distinguish temporal mean from population standard deviation. Composite figures keep quantities with incompatible units on separate axes or panels.
- Figure 9 contains all eight direct pool-HR outputs and must preserve pool-specific scales where needed for legibility.
- Figure 8 uses `case.output["HR"]` directly. Do not derive total HR by summing pool HR. Do not calculate `poolC * K`, potential HR, N-limited HR, P-limited HR, matched soil-stock/pathway figures, seasonal/full time-series figures, or a response-spread heatmap.

### Machine-readable artifacts

- Publish `parameter_metadata.csv` with exactly 4 rows.
- Publish `metric_definitions.csv` with exactly 31 rows: 27 raw variables and four accumulated ratios.
- Publish `member_metrics.csv` with exactly 400 rows, one per parameter/member, including coverage and ratio-support fields.
- Publish `response_curves.csv` with exactly 25,520 rows: 27 raw variables times two statistics plus four integrated ratios gives 58 endpoints; each endpoint has 100 member rows and ten bin rows for each of four parameters (`58 * 110 * 4`).
- Publish `ratio_support.csv` with exactly 1,600 rows: four ratios for 400 parameter-members, including supported status and explicit rejection reason.
- The five CSVs contain exactly 27,555 data rows excluding headers. Every table states units, statistic definitions, model-hour coverage, ratio denominator, and support where applicable.
- Publish `input_manifest.json`, `validation_receipt.json`, and `output_manifest.json`; manifests record every mapped absolute source path and every published artifact with size and SHA-256.

### Bounded implementation scope and work units

- Make only reusable, explicit-interface changes needed for paired absolute responses, accumulated ratios, direct `HR`, direct pool-HR atlases, and nutrient-cycle context. Keep the exact Iter008 inventory and figure selection in iteration-specific configuration; add no ABBY-, Iter008-, or `cn_s*`-specific defaults to reusable code.
- Load one pickle at a time, retain bounded summaries, generate under the current diagnostic attempt, validate before publication, and atomically publish only a complete `results/` directory.
- Work unit one is a bounded compute-node preflight. It validates exact input/config/parameter-file identity, hashes, safe deserialization, provenance, parameter samples and ranges, time axes, required variables, units, signs, shapes, ratio support, formulas, fixtures, and exact artifact expectations. It publishes only a passing receipt and immutable input manifest under its attempt directory.
- Work unit two is the diagnostic. It consumes only the passing manifest, generates tables and figures into staging within `diagnostic/attempt_N/`, validates the complete package, and atomically publishes it as `results/`.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter008_abby_ctrlvertc_cn_oat`, containing only top-level `preflight/attempt_N/`, `diagnostic/attempt_N/`, and published `results/`. Retain failed attempts; do not automatically delete, overwrite, or back up existing material.
- No ELM simulation, postprocessing, pickle repair, input mutation, member/time dropping, interpolation, depth aggregation, surrogate, PAWN/Sobol analysis, optimization, parameter recommendation, observation comparison, prior-result regeneration, or cross-configuration/site comparison is in scope.

### Tentative acceptance gates and decision rule

- Input gate: exactly four explicit mappings and 400 members satisfy the locked identities, ranges, provenance, variables, units, signs, time axis, dimensions, and newly recorded hashes. Unrelated shared-directory files are ignored and never consumed.
- Calculation gate: direct means, `ddof=0` standard deviations, and all four separately integrated ratio formulas reproduce deterministic fixtures; no undefined ratio is coerced or clipped; `FPI`/`FPI_P` remain in `[0,1]`.
- Artifact gate: exact counts are 4 parameter rows, 31 metric-definition rows, 400 member rows, 25,520 response rows, 1,600 ratio-support rows, 27,555 total CSV data rows, and 11 PNGs. Figure 8 uses direct `HR`; Figure 9 contains all eight direct pool-HR variables; removed reconstructed-HR and heatmap products are absent.
- Publication/review/accounting gate: hidden attempt-local staging passes validation before atomic publication; representative figures pass visual inspection for labels, units, legends, support, completeness, and legibility; an independent read-only reviewer passes preparation and final results; all jobs receive job-scoped terminal `sacct` accounting.
- A technical pass depends on contract and artifact correctness, not whether stress relief occurs. Report direction, range, support, nonlinearities, and microbial--plant trade-offs descriptively. Undefined ratios or flat responses are results, not evidence created by coercion. Decomposition N limitation alone does not establish whole-ecosystem N limitation.

### Proposed site, resources, retries, cancellation, evidence, and authority boundary

- Proposed system is Puma using `standard/chopinsong`, `micromamba/2.0.2-2`, and `OLMT_puma`. Refresh site access, account limits, storage, environment identity, output-root state, and module version before kickoff.
- Proposed initial resources: preflight uses one node/task, 12 CPUs (60 GB), and two hours; diagnostic uses one node/task, 12 CPUs (60 GB), and four hours. The envelope reflects the 4.12 GB pickles and Iter007's approximately 43 GB diagnostic peak.
- Retry budget per work unit is one initial attempt plus at most three retries, for at most four preflight attempts and four diagnostic attempts. Scheduler/resource failures may retry within a maximum of 16 CPUs (80 GB) and six hours. One minimal preflight-only correction may restore the locked interface or validation contract without changing inputs, calculations, figures, interpretation, output root, or gates. Diagnostic application/code/data/schema/unit/sign/dimensionality/dependency/numerical failures require a revised package and fresh approval rather than automatic retry.
- Proposed cancellation is limited to recorded Iter008 job IDs under the future runtime contract for identity mismatch, dangerous output behavior, resource escalation beyond contract, or explicit user instruction. Stop for undeclared/substituted inputs, incompatible units, unresolved semantics, corrupt pickles, material scope changes, exhausted retries, or missing authority.
- Expected evidence includes source/config/parameter identities and hashes; environment and repository identity; immutable input, validation, and output manifests; fixture, shape, unit, sign, support, and coverage evidence; exact table/figure counts; representative visual checks; reviewer identity/findings; submitted-copy equality; job IDs, logs, terminal accounting, and resource use; compact scientific interpretation; and cross-record validation.
- After a future kickoff approval, required records are `iterations/iter008.md`, `handoff/CURRENT.md`, `slurm/iter008/`, `summaries/iter008/ITER008_RESULT.md`, one closeout row in `registry.csv`, and one closeout entry in `ITERATION_SUMMARY.md`.
- This planning-only proposal grants no Iter008 initialization, Python execution, implementation, directory creation, review launch, scheduler operation, retry, cancellation, publication, or runtime-closeout authority. Before any such action, present one consolidated kickoff package containing this plan unchanged, refreshed evidence, exact lifecycle and outside-sandbox authority, monitoring and terminal-accounting mechanics, retry/cancellation terms, stop conditions, output authority, and the closeout commit/no-commit choice, then obtain fresh explicit approval.
