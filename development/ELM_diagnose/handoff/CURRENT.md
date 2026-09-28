# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter010`
- Proposed iteration: none
- Status: `workflow_complete`
- Phase: `closed`
- Active job scope: none; Iter010 jobs `24025653` and `24025871` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-27T19:45:24-07:00`

## Iter010 Closeout Snapshot

- Objective: evaluate direct-`HR` carbon balance using cumulative `LITFALL`, direct `HR`, and eight-pool storage change across four ABBY C:N OAT ensembles.
- Acceptance: `pass`; output manifest `80afe70badeb0a0f7cd2e3bda3be4ca1ec5fceef8543891b47a39036590b5c3c`; 39,542 CSV rows and 21 PNGs.
- Result: median absolute closure errors are 8.79%--9.07%; zero of 400 members are within 5%. HR tracks 87.4%--101.2% of input contrasts, with storage accounting for 1.3%--11.5%.
- Decision: accept the technically valid partial-boundary diagnostic, but do not claim carbon-input constraint or equilibrium because `HR + delta_C` systematically exceeds declared `LITFALL` by about 151 gC m-2.
- Records: `iterations/iter010.md`, `summaries/iter010/ITER010_RESULT.md`, `ITERATION_SUMMARY.md`, and the Iter010 registry row.

## Closed Iteration Identity and Decision

- Iteration ID: `iter009`
- Work type: `implementation`
- Objective: Amend the Iter008 N/P-stress diagnostic by separating mean and temporal-variability figures, restoring observed SR context, and adding pool-C and realized pool-HR-per-C responses.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 47 metrics; 74 response endpoints per parameter; 37,812 CSV rows; 17 figures; baseline-conditioned descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted the validated amendment. Pool stocks and realized respiration per pool C can respond differently to the separate C:N perturbations; especially, the `cn_s1` sampled-parameter-bin contrast increases SOIL1C by `53.01%` while SOIL1 HR is nearly unchanged and SOIL1 HR/C falls `34.99%`.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter009.md`.
- Compact result: `development/ELM_diagnose/summaries/iter009/ITER009_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context/results`.
- Input manifest SHA-256: `bb2836591c0857fb45a560cc1d7fdfb2d85053571394a85633f10855f982bf62`.
- Validation receipt SHA-256: `04bb75cefee96589f4b3d4b452633865dc6de92352b7dc6f9e9a7d08c58fe0bd`.
- Output manifest SHA-256: `afa885d5642b7cd886e5dfc05afd2575c803e91250c040604d23333fa5b95aae`.
- Execution: preflight `24019322` and diagnostic `24019366` completed `0:0` on attempt one; no retry or cancellation was used. Diagnostic stderr is empty and generator, artifact-validator, and atomic-publication markers pass.
- Package: 4 parameter rows, 47 metric definitions, 400 member rows, 32,560 response rows, 4,800 supported-ratio rows, one observation row, 37,812 total CSV data rows, and exactly 17 PNGs.
- Review: initial preparation review blocked unit/validator/fixture/record defects that were corrected before submission; focused preparation re-review, diagnostic launch review, final calculation/artifact review, and all-figure visual review passed.
- Scientific result: lowest-to-highest sampled-parameter-bin matched soil-pool C/HR/HR-C changes are `+53.01%`/`-0.53%`/`-34.99%`, `-3.90%`/`-4.76%`/`-0.89%`, `-0.47%`/`-0.66%`/`-0.18%`, and `+3.56%`/`+4.64%`/`+1.04%` for `cn_s1`--`cn_s4`.

## Risks and Next State

- Results are conditional on declared ranges and separate baseline-conditioned OAT ensembles. They establish neither interactions nor causal, global-sensitivity, prescribed-rate, optimization, parameter-recommendation, threshold, cross-site/configuration, or whole-ecosystem limitation conclusions.
- The observation is contextual and covers 26,264/61,320 hours (`42.83%`). `/xdisk` is temporary and unbacked; allocation expiration remains unavailable to non-PI users.
- Next state: the planning-only Iter010 proposal below is approved for documentation. Iter010 remains uninitialized; implementation and execution require a fresh consolidated kickoff package and explicit authority.

## Approved Iter010 Plan (Historical)

### Identity, objective, and hypothesis

- Sequential ID: `iter010`.
- Work type: `implementation`.
- Proposed run slug: `elm_diagnose_iter010_abby_ctrlvertc_cn_carbon_balance`.
- Site and configuration: standalone ABBY vertical-soil-carbon; no site or configuration comparison.
- Objective: determine whether the weak historical HR responses to the separate `cn_s1`--`cn_s4` perturbations are associated with limited carbon input to the decomposition subsystem or with changing carbon storage in that subsystem.
- Hypothesis: over 2018--2024, cumulative litterfall carbon input is balanced primarily by direct model HR, with a smaller contribution from the change in total decomposer-pool carbon. Technical acceptance is independent of whether this hypothesis is supported.

### Diagnostic inputs, dependencies, and trust boundary

- Consume exactly the four ordered explicit mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`: `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`, `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`, `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`, and `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl`. Do not discover or consume unrelated files.
- Preserve the Iter009 linear ranges, 100 members per parameter, exact 61,320-hour 2018--2024 no-leap support, site/configuration provenance, four explicit config files, four explicit parameter files, control parameter NetCDF for native markers, and baseline-conditioned descriptive OAT interpretation. Recompute all identities and hashes at kickoff and preflight rather than trusting historical receipts.
- Create a new reusable engine at `development/ELM_diagnose/tools/oat_carbon_balance.py`. Do not extend `oat_nutrient_diagnostics.py`: Iter010 is a carbon-balance analysis, not an N/P-stress analysis. Iter009 tools, scripts, manifests, results, and hashes remain immutable closed provenance.
- Required raw outputs are direct `LITFALL`, direct `HR`, and the exact eight carbon pools `CWDC`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`, `SOIL3C`, and `SOIL4C`. Direct `HR` is the sole HR term; do not replace it with or cross-sum the pool-specific HR outputs.
- Preflight must verify from declared model/configuration provenance that `LITFALL` is the intended external carbon-input variable for the eight-pool boundary and identify whether fire, harvest, leaching, or another external carbon transfer crosses that boundary. If the declared outputs cannot establish a complete boundary, retain technical reporting but label the result a partial balance and withhold the intended carbon-input-constraint conclusion.

### Calculations and figure contract

- For each member, integrate daily-equivalent hourly fluxes over the full common window as `input_C = sum_t(LITFALL_t / 24)` and `HR_C = sum_t(HR_t / 24)`, both in `gC m-2`.
- At each hour define total decomposer-pool carbon as `CWDC + LITR1C + LITR2C + LITR3C + SOIL1C + SOIL2C + SOIL3C + SOIL4C`. Define `delta_C = total_pool_C_end - total_pool_C_begin` in `gC m-2`, using the exact first and last common state samples and recording their timestamps.
- Define `rhs_C = HR_C + delta_C`, signed closure residual `residual_C = input_C - rhs_C`, and absolute relative closure error `abs(residual_C) / abs(input_C)` only where input is finite and nonzero. Preserve unsupported values as explicit gaps with reasons; never coerce them to zero.
- Use the established 100 member points, ten equal-count parameter bins, bin medians, and native-value markers for the three parameter-response products. Publish exactly four new figures: `ABBY_cumulative_litter_input_response.png`, `ABBY_cumulative_total_hr_response.png`, `ABBY_decomposer_pool_delta_c_response.png`, and `ABBY_carbon_balance_closure.png`.
- The closure figure has separate `cn_s1`--`cn_s4` panels of `input_C` against `rhs_C`, an equal-aspect 1:1 line, and labeled 1% and 5% relative-error bands. Do not pool the four separate OAT ensembles into one fitted sensitivity relationship.
- Preserve and regression-check the 37,812 Iter009 core CSV data rows and 17 prior figures. Add exactly 6 `carbon_balance_metric_definitions.csv` rows, 400 `carbon_balance_members.csv` rows, 1,320 `carbon_balance_response_curves.csv` rows (`4 parameters x 3 metrics x 110 member/bin rows`), and 4 `carbon_balance_parameter_summary.csv` rows. The complete proposed package is exactly 39,542 CSV data rows and 21 PNGs, plus versioned input, validation, and output manifests.
- The parameter summary records finite support, counts and percentages within 1% and 5% closure error, median and P95 absolute relative error, descriptive absolute-scale slope/intercept/R-squared, and lowest-to-highest-bin contrasts for `input_C`, `HR_C`, `delta_C`, and their balance residual.

### Scientific decision rule and exclusions

- A near-1:1 absolute balance demonstrates closure of the selected accounting boundary; it does not alone demonstrate that HR is carbon-input limited because `input_C = HR_C + delta_C` is the balance identity.
- Historical HR tracking of carbon input is supported only where closure errors are small, the response contrast in `HR_C` follows the response contrast in `input_C`, and the response contrast in `delta_C` is small relative to the input response. If storage change is material, report partitioning between respiration and accumulation or depletion instead.
- Describe only the 2018--2024 historical window. A small net storage change may be described as approximate balance over that window, not proof of equilibrium or a spinup-convergence result.
- Exclude pool-HR reconstruction, potential/N/P-limited HR, N/P-stress figures, observations, parameter interactions, PAWN/Sobol/global sensitivity, causal limitation, optimization, tuning, parameter recommendations, exact thresholds, and cross-site/configuration comparisons.

### Work units, tentative resources, review, and boundaries

- Work unit one is a bounded compute-node preflight. It validates exact identities and provenance, safe deserialization, shapes/time axes, units, nonnegative pool stocks, direct-`HR` use, full-window integration, endpoint timestamps, boundary semantics, explicit-gap behavior, deterministic balance fixtures, schemas, counts, figure membership, and Iter009 regression evidence.
- Work unit two is one diagnostic execution after preflight passes, followed by exact artifact validation and atomic publication. Proposed Puma envelope for each unit is `standard/chopinsong`, one node/task, 12 CPUs, 60 GB, with 2 hours for preflight and 4 hours for diagnostic under `OLMT_puma`; recheck account, capacity, environment, storage, and current site policy at kickoff.
- A different read-only reviewer must pass the prepared package before preflight, verify passing preflight evidence before diagnostic launch, and perform final independent calculation, artifact, and visual review.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter010_abby_ctrlvertc_cn_carbon_balance`. Do not create it before consolidated kickoff approval; generate only in attempt-local staging and atomically publish a complete new `results/` directory; never overwrite, delete, or automatically back up existing material.
- Tentative retry boundary: at most one minimal preflight-only correction/rerun and one same-scope scheduler/resource retry per work unit. Application, code, interface, schema, data, dependency, numerical, scope, or gate failures require a revised package and fresh authority. Cancellation is limited to recorded Iter010 job IDs under verified contract conditions.
- Stop for a missing material decision, identity mismatch, failed immutable gate, unapproved defect, exhausted retry, unavailable authoritative monitoring, explicit user stop, or validated closeout. Empty `squeue` is not completion; every submitted job requires job-scoped terminal `sacct` evidence.

### Tentative gates, evidence, records, and approval boundary

- Input/provenance gate: the exact four mapped pickles and declared dependencies match the approved identities and contracts; only direct `LITFALL`, direct `HR`, and the eight declared pools enter the balance; no undeclared input is consumed.
- Calculation gate: full-window flux integration, eight-pool endpoint storage change, right-hand side, signed and relative residuals, support rules, equal-count bins, endpoint-bin contrasts, and independent reproductions pass deterministic checks.
- Artifact/visual gate: exact 39,542 CSV rows and 21 PNGs; four carbon-balance figures have correct quantities, units, panels, member support, bin summaries, native markers, 1:1 reference, and error bands; the preserved Iter009 core passes regression checks.
- Publication/review/accounting/record gates: manifests cover the full payload, staging is atomically published, independent reviews pass, every job is terminally accounted, and the iteration report, compact result, cumulative summary, registry, and handoff agree under a final cross-record validator.
- Decision rule: technical acceptance depends only on immutable gates, not on closure or hypothesis direction. Report closure denominators and response partitioning without exceeding the descriptive OAT boundary.
- Expected evidence includes the approved contract; source/config/submitted hashes and byte identity; exact input/dependency identities; boundary audit; fixture and preflight receipts; table/figure counts; support denominators; independent calculation reproductions; visual checks; reviewer findings; job IDs, logs, terminal accounting, resources; output manifest; compact interpretation; and final record-validation output.
- Planning approval and documentation/commit authority were granted by the user's response agreeing with the plan while requiring direct `HR` and a new carbon-balance engine. This authorizes only these two planning-record updates and one scoped planning commit. Iter010 remains uninitialized. Before implementation, repository Python, output creation, review launch, scheduler activity, or runtime work, present the complete consolidated kickoff package required by `development/ELM_diagnose/WORKFLOW.md` and obtain fresh explicit approval, including outside-sandbox scheduler and cancellation authority and the closeout branch.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter009.md`, its compact result, and the Iter009 registry row.
3. Treat Iter009 execution material, records, manifests, and results as immutable closed provenance.
4. Treat Iter010 as immutable closed provenance. Any further diagnostic requires a new complete plan and kickoff approval.
