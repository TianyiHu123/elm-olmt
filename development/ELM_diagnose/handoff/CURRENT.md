# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter012`
- Proposed iteration: `iter013`
- Status: `not_initialized`
- Phase: `ready_for_kickoff_approval`
- Active job scope: none; jobs `24137742`, `24137829`, `24137929`, `24149109`, and `24149371` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none; all retained monitor outcomes and terminal handoffs are recorded in `iterations/iter012.md`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-10T02:11:14-07:00`

## Iter013 Runtime Authority

- Kickoff package: not approved.
- Runtime, repository-Python/script, output-directory, reviewer, scheduler, retry, cancellation, runtime-closeout-commit, and push authority: none.
- Planning-record commit authority: exactly one local scoped commit containing the Iter013 proposal in this handoff and the Iter012 report; exhausted by the commit containing this record; no push.
- Closeout branch: unresolved until the consolidated kickoff package is approved.

## Iter012 Closeout Snapshot

- Objective: extend the Iter011 ABBY transient/spinup OAT package with six respiration-fraction ensembles while preserving the same baseline-conditioned descriptive methods and interpretation boundary.
- Scope: exactly 27 pickles/configs/parameter files/restart cases, 2,700 members, five transient means, three final-spinup totals, three constructed pathways, 103,114 primary CSV rows, and 11 figures.
- Acceptance: `pass`; all immutable input, calculation, artifact, visual, publication, review, accounting, resource, and record gates pass.
- Inputs: passing input manifest `2d041f0d3e952bc9c22bb757ca0533ded4baecd80d8b56daa998e9a0b3ae6977`; exact six additions `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, and `rf_s3s4`, each sampled over `0.1--0.9`.
- Outputs: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter012_abby_ctrlvertc_oat_spinup/results`; output manifest `a24daac2c93c868182ed347e400938252f28a815645cb7cba41d7d61e01ec0ae`; exactly 103,114 rows and 11 PNGs.
- Execution: four preflights and one diagnostic completed `0:0`. Independent GNU-time measurement resolved allocation-pegged Slurm MaxRSS and supported right-sizing from 20 CPUs/100 GB to four CPUs/20 GB. Diagnostic process peak was `6408012K`, with no swaps.
- Review: `/root/iter012_review` passed final numerical, artifact, provenance, and visual review. It reproduced every score, rank, response bin, pathway row/curve, row count, and artifact hash; all 11 figures passed visual review.
- Result: `rf_s2s3` leads mean SR, HR, and LITFALL response spreads and ranks third for GPP and final-spinup decomposer C. `k_s4`, `k_s3`, and `k_s2` remain the leading stock-response parameters.
- Pathways: mean N-limited/potential and P-limited/potential ratios are `0.305316` and `0.401703`. P exceeds N in `2693/2700` cases; the seven exceptions are low-range `rf_s2s3` samples and are reported as sampled-range nonlinearity, not a threshold.
- Decision: accept only as baseline-conditioned, sampled-range descriptive OAT evidence. Constructed pathways remain distinct from direct model `HR`; no PAWN/Sobol/global-sensitivity, interaction, causal nutrient-limitation, tuning, threshold, recommendation, or cross-site/configuration conclusion is supported.
- Storage risk: `/xdisk` is temporary and unbacked; all attempts, logs, manifests, and published outputs are retained without overwrite or automatic backup.

## Records and Closeout

- Detailed report: `development/ELM_diagnose/iterations/iter012.md`
- Compact result: `development/ELM_diagnose/summaries/iter012/ITER012_RESULT.md`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Registry: one fixed-schema `iter012` row in `development/ELM_diagnose/registry.csv`
- Final validator: `development/ELM_diagnose/slurm/iter012/validate_iter012_closeout.sh`, SHA-256 `64c92e1053512de88626ca59a47b2216580309a94b4bb787b6149def0c47555a`; pass marker `ITER012_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=103114 transient_scores=135 spinup_scores=81 terminal_jobs=5 next_state=workflow_complete`.
- Iter012 closeout branch (historical and satisfied): exactly one scoped commit with no push.

## Next State

Iter013 is proposed but not initialized. Present one complete consolidated kickoff package and obtain fresh explicit approval before creating its report/scaffold, implementing changes, running repository Python/scripts, creating output paths, launching review, operating the scheduler, or committing.

## Next Iteration Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Sequential ID and work type: `iter013`, implementation.
- Proposed run slug: `elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs`.
- Site and configuration: standalone ABBY with vertical soil carbon active; no site or configuration comparison.
- Objective: extend the closed Iter012 standard package without changing its 27-parameter OAT inventory, transient model endpoints, decomposition pathways, or scoring framework by (1) adding the two NEON GPP partitioning products as contextual references and (2) adding final-spinup eight-pool C:N and C:P mass-ratio response endpoints, with contextual observed soil C, soil N, and C:N references.
- Hypothesis: the new final-spinup ratios may rank parameters differently from their component C/N/P stocks, while the two independently supported NEON GPP products provide observational context for the existing full-window model GPP responses. Technical acceptance is independent of response direction, ranking, or agreement with observations.
- Interpretation boundary: retain baseline-conditioned, sampled-range descriptive OAT language. Observations are contextual horizontal references only and never enter model statistics, scores, ranks, acceptance, calibration, or tuning. Results are not PAWN, Sobol, joint/global sensitivity, interaction, causal limitation, validation of boundary-mismatched stocks, optimization, parameter recommendations, exact thresholds, or cross-site/configuration evidence.

### Exact diagnostic inputs, dependencies, and trust assumptions

- Reuse exactly the ordered 27 Iter012 `parameter:pickle`, config, parameter-file, and restart-case mappings and their roots; the ordered parameter inventory remains `act25`, `br_mr`, `cn_s1`, `cn_s2`, `cn_s3`, `cn_s4`, `decomp_depth_efolding`, `frootcn`, `grperc`, `k_l1`, `k_l2`, `k_l3`, `k_s1`, `k_s2`, `k_s3`, `k_s4`, `leafcn`, `leaf_long`, `lflitcn`, `livewdcn`, `q10_mr`, `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, and `rf_s3s4`. The exact basenames are those enumerated in the immutable Iter012 finalized plan. Reject globs, discovery, reordering, missing/extra top-level pickles, substitutions, or inferred shared-directory membership.
- Preserve 100 members per parameter, the exact 2018--2024 no-leap model time axis with 61,320 hourly samples/member, the final `0201-01-01` restart mapping, the control-parameter NetCDF, and all Iter012 provenance checks. Recompute every source hash at kickoff and preflight rather than treating historical hashes as current identity.
- Retain the contextual SR source exactly as `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc`. Read-only planning inspection found source coverage 2019--2021; after no-leap conversion Iter012 retained 26,264 valid hours. The SR line remains a partial-coverage contextual mean against full-window model member means, not a timestamp-collocated comparison.
- Add `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/statistics/ABBY_neon_eval_hourly.nc`, planning-time SHA-256 `abf1d62a02791c36258330206da4c142527ba1ea5a8b1922122ac3e2cb155503`. It is a 61,368-hour Gregorian 2018--2024 NetCDF with `GPP_DT`, `GPP_NT`, `ER_DT`, `ER_NT`, and `NEE` in `gC/m^2/s`. Iter013 consumes only `GPP_DT` and `GPP_NT`. Both have 15,778 finite source values before no-leap conversion; `GPP_NT` has 4,372 finite negative source values that must be rejected under the approved nonnegative-GPP policy. Preflight records exact post-calendar raw, retained, negative-rejected, missing, and coverage counts and converted units.
- Add `/xdisk/chopinsong/tianyihu/NEON_surfdata/neon_surffiles/NEON_soilC_N_CN.csv`, planning-time SHA-256 `1869761ef73ac9b7c7789d29c516523cfd0895d6c0c53031e6bf4a147ac22afa`. Require one unique `siteID=ABBY` row with `totalSoilC_gC_m2=32303.95305411877`, `totalSoilN_gN_m2=2317.321904789272`, `CN_ratio=13.940209595980305`, and `effectiveDepth_m=2.0`, subject to exact revalidation at kickoff. Record the derivation script and ABBY surface-data identities as provenance. The CSV has no P stock or C:P observation.
- Trust the two new sources only after preflight validates exact paths/hashes, schemas, units, time/calendar handling, site uniqueness, finite values, and declared coverage. Do not repair, interpolate, extrapolate, or silently substitute either input.

### Reusable engine and locked calculations

- Extend `development/ELM_diagnose/tools/oat_sensitivity.py` input-driven and backward-compatibly; add no ABBY-, Iter013-, or inventory-specific defaults. Preserve the Iter012 results when its original arguments are supplied.
- Generalize transient observations from the legacy `TARGET:PATH` form to an explicit target/source/series/path contract while retaining legacy compatibility. Iter013 binds model target `SR` to source `SR`, model target `GPP` to source `GPP_DT`, and model target `GPP` to source `GPP_NT`. Multiple uniquely labelled series may target the same model endpoint; duplicate series identities remain invalid.
- Preserve full-window arithmetic model means across all 61,320 hours. For each observation product independently, convert the source calendar to no-leap, floor its timestamps consistently, restrict to 2018--2024, convert `gC/m^2/s` to `gC m-2 day-1`, apply product-specific validity, and calculate its mean over retained observations. Do not resample model members to observation-valid timestamps and do not create observation-conditioned model curves.
- Keep nonnegative GPP semantics: retain finite zero and positive `GPP_DT`/`GPP_NT`; mask negative values as invalid, including the declared negative `GPP_NT` values. `GPP_DT` and `GPP_NT` use their independent valid supports. Record raw/source, post-calendar, retained, negative-rejected, and missing counts and percentage denominators. Do not plot a synthetic uncertainty band; the source contains no uncertainty variables applicable to these lines.
- Preserve the five Iter012 transient endpoints and formulas unchanged: direct `SR`, direct `HR`, direct `GPP`, direct `LITFALL`, and eight-pool `DECOMP_C_TOTAL`. Preserve the three constructed potential/N/P-limited pathways unchanged and distinct from direct model `HR`. Keep compensation, litter-ratio, and temporal-standard-deviation families omitted.
- Preserve final-spinup `DECOMP_C_TOTAL`, `DECOMP_N_TOTAL`, and `DECOMP_P_TOTAL` as masked-array-aware sums of every stored vertical element in the exact eight corresponding lowercase `_vr` decomposer pools: `cwd`, `litr1`--`litr3`, and `soil1`--`soil4`. Introduce no layer weighting, depth truncation, vegetation pools, or alternative stock boundary.
- Add memberwise `DECOMP_CN_RATIO = DECOMP_C_TOTAL / DECOMP_N_TOTAL` in `gC gN-1` and `DECOMP_CP_RATIO = DECOMP_C_TOTAL / DECOMP_P_TOTAL` in `gC gP-1`. These are ratios of the eight-pool sums, never sums or means of component/layer ratios and never ratio-of-ensemble-means. Require finite positive denominators. Preserve an undefined ratio as an explicit gap with a rejection reason, never zero; any incomplete member support makes that endpoint's score unsupported and fails the proposed strict all-100-member acceptance gate below.
- Apply the existing score `100 * (P95 - P05) / abs(ensemble median)` independently to each of the five final-spinup endpoints and rank parameters within each endpoint. A nonfinite/zero score denominator or incomplete required member support remains explicitly unsupported.

### Figures, observation presentation, artifacts, and report

- Publish exactly 13 ABBY-labelled PNGs: the existing five transient-mean response atlases; five final-spinup response atlases for C, N, P, C:N, and C:P; one transient score/rank heatmap; one five-column final-spinup score/rank heatmap; and one accumulated pathway atlas.
- In the GPP atlas, draw `GPP_DT` and `GPP_NT` as different colored horizontal lines, proposed `tab:orange` and `tab:purple`, with an unambiguous figure-level legend rather than repeated panel legends. Keep model member points blue, bin medians black, and native markers red. Labels must identify them as NEON daytime-partitioning and nighttime-partitioning GPP products, not daylight-hour and nighttime-hour subsets.
- Keep the SR reference presentation scientifically unchanged while permitting the generalized plotting machinery. Every transient observation row and report statement must disclose its actual retained support and its percentage denominator relative to the 61,320-hour model window.
- Plot the ABBY CSV values as contextual horizontal references in the `DECOMP_C_TOTAL`, `DECOMP_N_TOTAL`, and `DECOMP_CN_RATIO` final-spinup atlases. Label them as NEON soil-profile observations integrated to 2.0 m. State on the figures/tables/report that the model endpoint is the eight-pool CWD+litter+soil total across all stored vertical elements, whereas the observation is a measured soil profile; this is an intentionally accepted boundary mismatch and not a like-for-like validation. Plot no observation in the P or C:P atlas and no observations in either heatmap.
- Publish exactly 109,113 primary CSV data rows excluding headers: 27 parameter metadata; 2,700 transient member metrics; 135 transient scores; 14,850 transient response-curve rows; three transient observation summaries (`SR`, `GPP_DT`, `GPP_NT`); 2,700 final-spinup member rows with five endpoints; 135 final-spinup scores; 14,850 final-spinup response-curve rows; three scalar spinup observation summaries (soil C, soil N, C:N); 72,900 pathway pool/member rows; and 810 pathway total-curve rows.
- Keep transient time-series observation summaries separate from scalar final-spinup observation summaries. Tables and manifests must retain model target, source variable/column, series label, source path/hash, units, aggregation, raw/retained/rejected support, actual temporal or depth coverage, percentage denominator, endpoint definition, stock-boundary warning, and whether the reference enters scoring (`false`).
- Produce a compact result report with inputs, formulas, units, model/observation coverage, ratio support, range-conditional rankings and nonlinearities, contextual observation comparisons, pathways, limitations, and unsupported quantities. Do not describe visual proximity to an observation line as fit, validation, bias, or performance.

### Bounded work units, exclusions, output policy, and tentative gates

- Work unit one is a bounded compute-node preflight. It validates the unchanged exact 27-way transient/restart/provenance inventory; both new observation sources; aliases and duplicate-target series; calendar/unit conversions; negative-GPP rejection; scalar CSV selection; all restart C/N/P components; eight-pool totals and ratio-of-sums formulas; gap/support semantics; plotting legends/layouts; backward compatibility; deterministic fixtures; and exact artifact expectations. It performs no substantive diagnostic evaluation and publishes only an immutable input manifest and validation receipt.
- Work unit two is one diagnostic after preflight passes. It consumes only the passing manifest, loads inputs sequentially, writes hidden attempt-local staging, runs the exact artifact validator, and atomically publishes only a complete `results/` directory.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs`, with immutable `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`. Do not create it before consolidated kickoff approval; never overwrite, delete, or automatically back up existing material. `/xdisk` remains temporary and unbacked.
- Exclude ELM simulation, postprocessing, source-data mutation/repair, member or model-time dropping, interpolation, observation-conditioned/collocated model curves, ER/NEE response analysis, alternative or depth-matched stock boundaries, layer weighting, vegetation pools, observed P/C:P, uncertainty bands, calibration, compensation plots, litter ratios, temporal-standard-deviation products, cross-site/configuration comparison, prior-result regeneration, surrogate modeling, PAWN/Sobol/global sensitivity, interactions, causal limitation, optimization, tuning, thresholds, and parameter recommendations.
- Input/provenance gate: all unchanged Iter012 identities and all new observation identities/schemas/hashes pass; exact 27 parameters and 2,700 transient/restart members remain complete; no inferred inputs are admitted.
- Calculation/support gate: full-window model means remain unchanged; SR/GPP references use independently valid observation support only; negative GPP is rejected; all 2,700 C:N and C:P ratios equal independently reproduced ratios of eight-pool sums with finite positive denominators. The proposed strict gate requires 100/100 supported ratio members for every parameter and all 135 final-spinup endpoint scores supported; otherwise stop for classification rather than silently ranking partial ensembles.
- Artifact/visual gate: exactly 109,113 primary rows and 13 PNGs; both GPP lines have distinct colors and one correct legend; soil C/N/C:N references appear only in their intended atlases with coverage/boundary warnings; the five-column spinup heatmap and all units, ranks, native markers, disabled empty panels, and labels are legible; no excluded output family exists.
- Publication/review/accounting/record gate: complete manifests, hidden-stage validation before atomic publication, independent preparation and final numerical/artifact/visual review by a different read-only agent, job-scoped terminal accounting, and agreement among the iteration report, compact result, cumulative summary, registry, and handoff.
- Decision rule: technical acceptance depends only on the immutable gates, not scientific ranking or observation agreement. Report only baseline-conditioned, sampled-range descriptive OAT evidence and contextual, coverage-qualified observations.

### Proposed resources, retry boundaries, evidence, and authorization boundary

- Proposed site/resource envelope: Puma using `development/hpc/puma.md`, account/partition `chopinsong/standard`, `OLMT_puma`, one node/task, four CPUs and scheduler-derived 20 GB; two hours for preflight and four hours for diagnostic. Revalidate host, account, limits, environment, quotas/capacity, and storage at kickoff. This reuses the successful Iter012 right-sized shape, whose diagnostic GNU-time peak was approximately 6.41 GB; historical measurements are planning evidence, not current runtime proof.
- Proposed retry boundary: one initial attempt plus at most three retries per work unit; at most one minimal preflight-only correction that restores the locked interface/validation contract; all other automatic retries are classified same-scope scheduler/resource failures only. Application, code, interface, schema, data, dependency, numerical, scientific, publication, immutable-gate, or resource-cap failures require preserved evidence, classification, a revised complete package, and fresh user authorization before change or rerun.
- Proposed monitoring/cancellation: immediate post-submission identity checks, one retained supported state-change monitor with bounded backoff and unchanged-output suppression, and authoritative job-scoped terminal accounting for every attempt. Cancellation is limited to recorded Iter013 job IDs for identity mismatch, a proven universal pre-execution defect, out-of-root writes, resource-contract overrun, or explicit user instruction, followed by terminal accounting.
- Expected evidence: approved kickoff/runtime contract; repository and source identity; exact input/dependency and submitted-copy hashes; preflight fixture/receipt; observation schema, conversion, rejection, support and coverage records; independently reproduced eight-pool totals/ratios, scores, ranks, bins, row counts and hashes; visual review of all 13 figures; job IDs/logs/accounting/resources; atomic output manifest; scientific report; and cross-record validator output.
- The user's initial `2026-10-10` request authorized finalizing this planning-only proposal in the Iter012 report and current handoff plus static text/diff validation. The subsequent explicit request `commit the finalized plan` authorizes exactly one scoped local planning-record commit containing only those two records, with no push. It grants no Iter013 initialization, new report/scaffold, implementation, repository Python/script execution, output-directory creation, reviewer launch, scheduler operation, retry, cancellation, diagnostic publication, runtime closeout, additional commit, or push authority. Before any runtime work, present one complete consolidated kickoff package under `development/ELM_diagnose/WORKFLOW.md`, including the unchanged plan, finite goal/work units, confirmed Puma context, exact lifecycle and outside-sandbox authorities, resources/retries/cancellation, and an explicit closeout commit-or-uncommitted branch, then obtain fresh approval.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter012.md`, its compact result, registry row, and `development/hpc/puma.md`.
3. Treat all Iter012 execution material, attempts, manifests, outputs, and closeout records as immutable provenance.
4. Do not resubmit any Iter012 job. Treat the Iter013 plan above as planning-only until one complete kickoff package receives fresh approval.
