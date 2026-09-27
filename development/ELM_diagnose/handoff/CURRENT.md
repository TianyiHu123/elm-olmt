# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter008`
- Proposed iteration: `iter009` (`not_initialized`)
- Status: `pre_kickoff`
- Phase: planning only; no Iter009 runtime authority
- Active job scope: none; Iter008 jobs `24015245` and `24015300` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none; retained sessions `47630` and `24507` handed off to complete job-scoped accounting.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-26T18:05:09-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter008`
- Work type: `implementation`
- Objective: Characterize how separate perturbations of `cn_s1`--`cn_s4` affect realized decomposition, microbial N/P demand satisfaction, plant N/P demand satisfaction, ecosystem carbon fluxes, and mineral nutrient cycling in the ABBY vertical-soil-carbon configuration.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 27 direct raw metrics; four accumulated satisfaction ratios; 58 response endpoints; 27,555 CSV rows; 11 figures; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted the validated baseline-conditioned ABBY C:N OAT package. Increasing pool C:N reduces potential microbial nutrient demand and improves microbial demand satisfaction, especially for `cn_s3` and `cn_s4`, but does not broadly relieve plant demand or guarantee higher realized decomposition.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter008.md`.
- Compact result: `development/ELM_diagnose/summaries/iter008/ITER008_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter008_abby_ctrlvertc_cn_oat/results`.
- Input manifest SHA-256: `2c90f754d843eba1b2610be2574862f17471689ba3a98d6140155986c1f7dc19`.
- Validation receipt SHA-256: `56fb4d944afb1cfd7e5bbd74b009fd88427a7488d02c49250c21c5238dfe257a`.
- Output manifest SHA-256: `9d5c8b07e560c1fa186a28d77f7ac35cd31d8009060e6f942714120f618ab49b`.
- Execution: preflight `24015245` and diagnostic `24015300` completed `0:0` on attempt one; no retry was consumed. The diagnostic has empty stderr and generator, artifact-validator, and atomic-publication pass markers.
- Package: 4 parameter rows, 31 metric definitions, 400 member rows, 25,520 response rows, 1,600 ratio-support rows, 27,555 total CSV data rows, and exactly 11 PNGs. All ratios are supported.
- Review: initial preparation review blocked four defects that were corrected before submission; focused preparation re-review, diagnostic launch review, final artifact/calculation review, and visual review all passed.
- Scientific result: low-to-high sampled C:N changes microbial N satisfaction by `+2.3%`, `+25.4%`, `+108.4%`, and `+118.6%` for `cn_s1`--`cn_s4`; plant N/P satisfaction changes only about `+0.6%`, `-3.6%`, `+1.4%`, and `+4.3%`; direct HR changes `+1.0%`, `-5.4%`, `-0.7%`, and `+4.6%`.

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. They establish neither interactions nor causal, global-sensitivity, optimization, parameter-recommendation, cross-site/configuration, or whole-ecosystem limitation conclusions.
- `cn_s1` has a reproducible upper-range discontinuity across several outputs; it is descriptive behavior, not an inferred threshold.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unavailable to non-PI users.
- Next state: the planning-only Iter009 proposal below is approved for documentation. Iter009 remains uninitialized; implementation and execution require a fresh consolidated kickoff package and explicit authority.

## Proposed Next-Iteration Plan (Planning Only)

### Identity, objective, and hypothesis

- Sequential ID: `iter009`.
- Work type: `implementation`.
- Proposed run slug: `elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context`.
- Site and configuration: standalone ABBY vertical-soil-carbon; no site or configuration comparison.
- Objective: amend the Iter008 N/P-stress diagnostic so mean and temporal variability are separated for HR and mineral N/P-cycle figures, observed SR context is restored, and pool-size and realized pool-respiration-per-pool-C responses are added.
- Hypothesis: pool-resolved C stocks and realized HR per unit pool C will distinguish stock responses from realized decomposition responses across the separate `cn_s1`--`cn_s4` OAT ensembles. Technical acceptance is independent of whether this hypothesis is supported.

### Diagnostic inputs, dependencies, and trust boundary

- Consume exactly the four ordered explicit mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`: `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`, `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`, `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`, and `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl`. Do not discover or consume unrelated files.
- Preserve the Iter008 linear ranges, 100 members per parameter, exact 61,320-hour 2018--2024 no-leap support, site/configuration provenance, four explicit config files, four explicit parameter files, and control parameter NetCDF used for native markers. Recompute all identities and hashes at kickoff and preflight rather than trusting historical receipts.
- Add the explicit contextual mapping `SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc`. Its planning-time SHA-256 is `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`; recompute it at kickoff and preflight.
- Modify the specialized engine `development/ELM_diagnose/tools/oat_nutrient_diagnostics.py`. Iter008 scripts, manifests, results, and hashes remain immutable closed provenance; Iter009 receives new wrappers, configuration, validator, manifests, output root, and schemas.
- Add the exact pool/HR pairs `CWDC:CWDC_HR`, `LITR1C:LITR1_HR`, `LITR2C:LITR2_HR`, `LITR3C:LITR3_HR`, `SOIL1C:SOIL1_HR`, `SOIL2C:SOIL2_HR`, `SOIL3C:SOIL3_HR`, and `SOIL4C:SOIL4_HR`.

### Calculations and figure contract

- Preserve Iter008 arithmetic temporal means, population temporal standard deviations (`ddof=0`), separately accumulated microbial/plant satisfaction ratios, equal-count response bins, native markers, explicit-gap behavior, and baseline-conditioned descriptive OAT interpretation.
- For each pool and member, publish the mean pool size in `gC m-2`; no pool-size temporal standard deviation is required.
- Define realized pool respiration per unit pool C as `sum_t(pool_HR) / sum_t(pool_C)`, equivalently the ratio of temporal means on their common support, with units `day-1`. Require a finite numerator and finite positive pool-C denominator; preserve unsupported members as explicit gaps with reasons, preserve supported zero-HR values as zero, and do not clip or coerce values. Label this as a realized respiration-to-pool ratio, not the prescribed decomposition rate or a causal turnover constant. No temporal standard deviation is required for this ratio.
- Load the SR observation through the established observation-unit/time logic, require unique timestamps and finite valid 2018--2024 overlap, and record path, hash, units, coverage numerator and model-window denominator, minimum, maximum, arithmetic mean, and population temporal standard deviation. Plot the observed mean on the SR mean row and observed temporal standard deviation on the SR temporal-SD row. Observation values are contextual only and do not modify model statistics, bins, or scores.
- Retain seven files: `ABBY_fpi_response.png`, `ABBY_microbial_n_response.png`, `ABBY_microbial_p_response.png`, `ABBY_plant_n_response.png`, `ABBY_plant_p_response.png`, `ABBY_gpp_response.png`, and `ABBY_sr_response.png`.
- Replace the four mixed files with eight separated files: `ABBY_hr_mean_response.png`, `ABBY_hr_temporal_std_response.png`, `ABBY_pool_hr_mean_response.png`, `ABBY_pool_hr_temporal_std_response.png`, `ABBY_n_cycle_mean_response.png`, `ABBY_n_cycle_temporal_std_response.png`, `ABBY_p_cycle_mean_response.png`, and `ABBY_p_cycle_temporal_std_response.png`.
- Add `ABBY_pool_c_mean_response.png` and `ABBY_pool_hr_per_c_response.png`, each with the exact eight ordered pool rows. The superseded `ABBY_hr_response.png`, `ABBY_pool_hr_response.png`, `ABBY_n_cycle_response.png`, and `ABBY_p_cycle_response.png` must be absent. The complete contract is exactly 17 PNGs.

### Bounded scope, artifacts, and exclusions

- Expected machine-readable artifacts are exactly 4 `parameter_metadata.csv` rows, 47 `metric_definitions.csv` rows, 400 `member_metrics.csv` rows, 32,560 `response_curves.csv` rows, 4,800 `ratio_support.csv` rows, and one `observation_summary.csv` row: 37,812 CSV data rows total. The response table contains 74 endpoints per parameter: the existing 58, eight pool means, and eight realized HR/pool-C ratios. The support table covers the four accumulated satisfaction ratios plus the eight HR/pool-C ratios.
- Publish versioned input, validation, and output manifests with exact membership, hashes, schemas, row counts, figure names, byte sizes, and artifact hashes. Generate only in attempt-local staging and atomically publish a complete new `results/` directory.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context`. Do not create it before consolidated kickoff approval; never overwrite, delete, or automatically back up existing material.
- Exclude reconstructed `poolC * K`, potential/N/P-limited HR, new heatmaps, time-series plots, parameter interactions, PAWN/Sobol/global sensitivity, optimization, tuning, parameter recommendations, causal claims, cross-site/configuration comparisons, and whole-ecosystem limitation claims.

### Work units, tentative resources, review, and boundaries

- Work unit one is a bounded compute-node preflight. It validates exact identities and provenance, safe deserialization, shapes/time axes, units/signs, FPI bounds, the eight pool/HR mappings, SR observation support, formulas, explicit gaps, deterministic fixtures, schemas, counts, figure membership, and absence of superseded outputs. Fixtures must distinguish ratio-of-sums from mean-of-hourly-ratios and prove supported zero-HR and rejected nonpositive-pool cases.
- Work unit two is one diagnostic execution after preflight passes, followed by exact artifact validation and atomic publication. Proposed Puma envelope for each unit is `standard/chopinsong`, one node/task, 12 CPUs, 60 GB, with 2 hours for preflight and 4 hours for diagnostic under `OLMT_puma`; recheck account, capacity, environment, storage, and current site policy at kickoff.
- A different read-only reviewer must pass the prepared package before preflight and verify passing preflight evidence before diagnostic launch. Final calculation, artifact, and visual review is also required.
- Tentative retry boundary: at most one minimal preflight-only correction/rerun and one same-scope scheduler/resource retry per work unit. Application, code, interface, schema, data, dependency, numerical, scope, or gate failures require a revised package and fresh authority. Cancellation is limited to recorded Iter009 job IDs under verified contract conditions.
- Stop for a missing material decision, identity mismatch, failed immutable gate, unapproved defect, exhausted retry, unavailable authoritative monitoring, explicit user stop, or validated closeout. Empty `squeue` is not completion; every submitted job requires job-scoped terminal `sacct` evidence.

### Tentative gates, evidence, records, and approval boundary

- Input/provenance gate: exact four mapped pickles and declared dependencies match the approved identities and contracts; no undeclared input is consumed.
- Calculation gate: means, `ddof=0` standard deviations, existing satisfaction ratios, pool means, `sum(HR)/sum(pool_C)`, observation summaries, units, support, and binning pass deterministic and independent checks.
- Artifact/visual gate: exact 37,812 CSV rows and 17 PNGs; separated HR/N/P mean and SD files; observation references on the correct SR rows; all eight ordered pools in both new figures; explicit gaps and denominators reported; superseded mixed figures absent; titles, units, markers, legends, and panels legible.
- Publication/review/accounting/record gates: manifests cover the full payload, staging is atomically published, independent reviews pass, every job is terminally accounted, and the iteration report, compact result, cumulative summary, registry, and handoff agree under a final cross-record validator.
- Decision rule: technical acceptance depends only on the immutable gates, not response direction. Report ranges, directions, nonlinearities, observation coverage, and stock-versus-realized-respiration contrasts without exceeding the descriptive OAT boundary.
- Expected evidence includes approved contract text; source/config/submitted hashes and byte identity; exact input/dependency/observation identities; fixture and preflight receipts; table/figure counts; support and coverage denominators; representative calculation reproductions and visual checks; reviewer identities/findings; job IDs, logs, terminal accounting, resources; output manifest; compact interpretation; and final record-validation output.
- Planning approval and documentation/commit authority were granted by the user's exact response `The plan is approved, HR/pool response should use sum divided by sum as you suggested here. Now update the plan to the relavant files and commit it.` This authorizes only the two planning-record updates and one scoped planning commit. Iter009 remains uninitialized. Before implementation, Python, output creation, review launch, scheduler activity, or runtime work, present the complete consolidated kickoff package required by `development/ELM_diagnose/WORKFLOW.md` and obtain fresh explicit approval, including outside-sandbox scheduler and cancellation authority and the closeout branch.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter008.md`, its compact result, and the Iter008 registry row.
3. Treat Iter008 execution material, reports, manifests, results, and registry evidence as immutable closed provenance.
4. Confirm the Iter009 planning block is identical in this handoff and the closed Iter008 report.
5. Build and present a fresh consolidated Iter009 kickoff package; do not initialize or execute it without explicit authority.
