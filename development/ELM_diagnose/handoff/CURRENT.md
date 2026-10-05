# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter010`
- Proposed iteration: `iter011`
- Status: `pre_kickoff`
- Phase: `planning`
- Active job scope: none; Iter010 jobs `24025653` and `24025871` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-04T22:13:11-07:00`

## Iter010 Closeout Snapshot

- Objective: evaluate direct-`HR` carbon balance using cumulative `LITFALL`, direct `HR`, and eight-pool storage change across four ABBY C:N OAT ensembles.
- Acceptance: `pass`; output manifest `80afe70badeb0a0f7cd2e3bda3be4ca1ec5fceef8543891b47a39036590b5c3c`; 39,542 CSV rows and 21 PNGs.
- Result: median absolute closure errors are 8.79%--9.07%; zero of 400 members are within 5%. HR tracks 87.4%--101.2% of input contrasts, with storage accounting for 1.3%--11.5%.
- Decision: accept the technically valid partial-boundary diagnostic, but do not claim carbon-input constraint or equilibrium because `HR + delta_C` systematically exceeds declared `LITFALL` by about 151 gC m-2.
- Records: `iterations/iter010.md`, `summaries/iter010/ITER010_RESULT.md`, `ITERATION_SUMMARY.md`, and the Iter010 registry row.

## Planning Authority and Next Action

- The user approved the finalized Iter011 planning-only proposal, the exact output root, three retries after the initial attempt for each of preflight and diagnostic, and one scoped closeout commit with no push.
- Current authority is limited to recording this plan and making the scoped planning commit. It does not authorize Iter011 initialization, implementation, repository Python, output creation, review launch, scheduler operations, retries, cancellation, publication, runtime closeout, or another commit.
- Next action: present one complete consolidated Iter011 kickoff package and runtime contract, including the exact outside-sandbox authority question required by `WORKFLOW.md`, then await fresh explicit approval.

## Proposed Iter011 Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Sequential ID and work type: `iter011`, implementation.
- Proposed run slug: `elm_diagnose_iter011_abby_ctrlvertc_oat_spinup`.
- Site and configuration: standalone ABBY with vertical soil carbon active; no site or configuration comparison.
- Objective: rank the baseline-conditioned responses of transient carbon fluxes and decomposer carbon storage, final spinup decomposer C/N/P states, and idealized potential/N/P-limited decomposition pathways across 21 separate ABBY one-parameter OAT ensembles.
- Hypothesis: the expanded 21-parameter inventory will show distinct range-conditional controls on transient flux means and final spinup pool states, while the constructed pathway responses will distinguish potential decomposition from N- and P-limited realizations. Technical acceptance is independent of the hypothesis direction.
- Interpretation boundary: results are range-dependent descriptive OAT responses conditioned on the baseline configuration and each declared one-parameter range. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal limitation, optimization, tuning, parameter recommendations, exact thresholds, or evidence for cross-site/configuration differences.

### Exact diagnostic inputs, dependencies, and trust assumptions

- Consume exactly the following ordered mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`; reject globs, discovery, duplicate parameters or basenames, path components in basenames, missing/extra top-level pickles, or substitutions:
  - `act25:ABBY_ctrlvertcact25_I20TRCNPRDCTCBC.pkl`
  - `br_mr:ABBY_ctrlvertcbrmr_I20TRCNPRDCTCBC.pkl`
  - `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`
  - `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`
  - `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`
  - `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl`
  - `decomp_depth_efolding:ABBY_ctrlvertcdepthefold_I20TRCNPRDCTCBC.pkl`
  - `frootcn:ABBY_ctrlvertcfrootcn_I20TRCNPRDCTCBC.pkl`
  - `grperc:ABBY_ctrlvertcgrperc_I20TRCNPRDCTCBC.pkl`
  - `k_l1:ABBY_ctrlvertckl1_I20TRCNPRDCTCBC.pkl`
  - `k_l2:ABBY_ctrlvertckl2_I20TRCNPRDCTCBC.pkl`
  - `k_l3:ABBY_ctrlvertckl3_I20TRCNPRDCTCBC.pkl`
  - `k_s1:ABBY_ctrlvertcks1_I20TRCNPRDCTCBC.pkl`
  - `k_s2:ABBY_ctrlvertcks2_I20TRCNPRDCTCBC.pkl`
  - `k_s3:ABBY_ctrlvertcks3_I20TRCNPRDCTCBC.pkl`
  - `k_s4:ABBY_ctrlvertcks4_I20TRCNPRDCTCBC.pkl`
  - `leafcn:ABBY_ctrlvertcleafcn_I20TRCNPRDCTCBC.pkl`
  - `leaf_long:ABBY_ctrlvertcleaflong_I20TRCNPRDCTCBC.pkl`
  - `lflitcn:ABBY_ctrlvertclflitcn_I20TRCNPRDCTCBC.pkl`
  - `livewdcn:ABBY_ctrlvertclivewdcn_I20TRCNPRDCTCBC.pkl`
  - `q10_mr:ABBY_ctrlvertcq10mr_I20TRCNPRDCTCBC.pkl`
- Map those parameters in the same order to these exact restart case basenames beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/restart`: `ABBY_ctrlvertcact25_I1850CNPRDCTCBC`, `ABBY_ctrlvertcbrmr_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns1_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns2_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns3_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns4_I1850CNPRDCTCBC`, `ABBY_ctrlvertcdepthefold_I1850CNPRDCTCBC`, `ABBY_ctrlvertcfrootcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertcgrperc_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl1_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl2_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl3_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks1_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks2_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks3_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks4_I1850CNPRDCTCBC`, `ABBY_ctrlvertcleafcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertcleaflong_I1850CNPRDCTCBC`, `ABBY_ctrlvertclflitcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertclivewdcn_I1850CNPRDCTCBC`, and `ABBY_ctrlvertcq10mr_I1850CNPRDCTCBC`. Each must contain exactly `g00001`--`g00100/<case_basename>.elm.r.0201-01-01-00000.nc`. Do not infer or substitute cases from the shared root.
- Require the matching 21 configs under `.../ABBY/config` and 21 parameter files under `.../NEON_ctrlvertc_sensi/params` as provenance cross-checks. The four added files declare `leafcn 30--40`, `frootcn 30--50`, `livewdcn 35--65`, and `lflitcn 50--90`. Pickle metadata remains authoritative for parameter identity, selector, bounds, samples, site, member count, years, output variables, and time axes; stale embedded Perlmutter paths are never dereferenced.
- Use `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` for native parameter markers and `SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` for the contextual observed mean-SR line. Recompute all hashes at kickoff and preflight.
- Planning-time read-only inspection found 21 pickles totaling 76,930,326,400 bytes, 21 restart case directories with 100 files each, and the same 24 lowercase vertical-pool variables in member one of every case family. Full content, hashes, dimensions, units, masks, finiteness, deserialization compatibility, and all-member parity remain compute-node preflight gates.

### Reusable engine and locked calculations

- Extend `development/ELM_diagnose/tools/oat_sensitivity.py` backward-compatibly. Add no ABBY-, Iter011-, or inventory-specific defaults. Preserve historical interfaces and formulas when their prior arguments are supplied.
- Replace the 16-parameter/fixed-4-by-4 plotting limit with a deterministic dynamic layout that accommodates 21 panels, expected to be 5 by 5. Apply it to every multi-parameter atlas used by Iter011.
- Preserve 100 members per parameter, exactly 61,320 no-leap hourly samples for 2018--2024, log10 parameter coordinates only for `k_l1`--`k_l3` and `k_s1`--`k_s4`, linear coordinates for the other 14 parameters, ten deterministic equal-count parameter bins, member points, bin medians, and native markers where one finite native value resolves inside the sampled range.
- Transient analysis uses arithmetic temporal means only; produce no temporal-standard-deviation rows, scores, heatmaps, or response figures. The five endpoints are direct `SR`, direct `HR`, direct `GPP`, direct `LITFALL`, and `DECOMP_C_TOTAL = CWDC + LITR1C + LITR2C + LITR3C + SOIL1C + SOIL2C + SOIL3C + SOIL4C`. Direct `HR` must be `case.output["HR"]`; never replace it with or cross-sum pool-specific HR outputs. The observed SR mean is a contextual horizontal line in the SR response atlas and never enters model statistics or scores.
- Add an explicit restart interface binding every parameter to its exact restart case basename. For each member calculate final-spinup `DECOMP_C_TOTAL`, `DECOMP_N_TOTAL`, and `DECOMP_P_TOTAL` as the sum of the eight corresponding lowercase vertical arrays: `cwd{c,n,p}_vr`, `litr1{c,n,p}_vr`--`litr3{c,n,p}_vr`, and `soil1{c,n,p}_vr`--`soil4{c,n,p}_vr`.
- Follow the repository spinup-surrogate scalar convention of summing restart components with masked-array-aware `numpy.nansum`, but harden support validation: require every exact lowercase component, expected dimensions/shapes and compatible units, at least one valid value per component, no unmasked NaN/Inf, exact member/file identity, and recorded masked/valid counts. Sum the stored layer pools directly; introduce no layer-thickness weighting or vegetation pools. A dimensional or unit contradiction stops rather than silently changing the formula.
- For transient and spinup endpoints, retain the existing range-conditional screening score `100 * (P95 - P05) / abs(ensemble median)` and descending within-endpoint parameter rank. A nonfinite or zero denominator is an explicit unsupported score with reason, never zero. Produce exactly one transient-mean score/rank heatmap and one final-spinup score/rank heatmap.
- Enable only the Iter005 decomposition-pathway family with eight mappings: `CWDC:K_CWD`, `LITR1C:K_LITR1`, `LITR2C:K_LITR2`, `LITR3C:K_LITR3`, `SOIL1C:K_SOIL1`, `SOIL2C:K_SOIL2`, `SOIL3C:K_SOIL3`, and `SOIL4C:K_SOIL4`; use `FPI` and `FPI_P` as the N and P limiters. Calculate potential pool decomposition as `pool_C * K_pool`, N-limited as `FPI * potential`, P-limited as `FPI_P * potential`, multiply hourly flux by 3600 seconds, then sum over pools and time. Require finite limiters in `[0,1]`.
- Compensation and litter-ratio interfaces are omitted. Add regression coverage proving that absent compensation arguments produce no compensation plots or tables and do not affect other families. Constructed potential/N/P-limited pathways remain distinct from direct model `HR`.

### Figures, machine-readable artifacts, and report

- Publish exactly 11 ABBY-labelled PNGs: five 21-panel transient-mean response atlases, three 21-panel final-spinup response atlases, one transient-mean sensitivity heatmap, one final-spinup sensitivity heatmap, and one 21-panel accumulated potential/N-limited/P-limited pathway atlas.
- Publish the following primary CSV data rows: 21 parameter metadata; 2,100 transient member metrics; 105 transient sensitivity scores; 11,550 transient response-curve rows; one SR observation row; 2,100 spinup member metrics; 63 spinup sensitivity scores; 6,930 spinup response-curve rows; 56,700 pathway pool/member rows; and 630 pathway total-curve rows. The primary total is exactly 80,200 data rows excluding headers.
- Tables must state endpoint definitions, units, parameter/member identity, model or observation coverage, score denominator/support, rank scope, restart component support, and explicit rejection reasons. Manifests record every mapped absolute source, hash, generated artifact, size, row count, and SHA-256.
- Produce a compact result report covering inputs, methods, units, model and observation coverage, range-conditional rankings, response directions and nonlinearities, pathway comparisons, limitations, and unsupported quantities. Repository closeout records are `iterations/iter011.md`, `summaries/iter011/ITER011_RESULT.md`, one `ITERATION_SUMMARY.md` append, one `registry.csv` row, rebuilt `handoff/CURRENT.md`, and Iter011 execution material.

### Bounded scope, work units, exclusions, and output policy

- Work unit one is a bounded compute-node preflight. It validates exact inventories and hashes, safe pickle deserialization, config/parameter provenance, time/member axes, direct targets, observation coverage, restart file/member mapping, all 24 restart variables, masks/dimensions/units/support, score behavior, pathway formulas, optional-interface behavior, dynamic layouts, deterministic fixtures, and exact artifact expectations. It publishes only an immutable input manifest and validation receipt in its attempt directory.
- Work unit two is one diagnostic operation after preflight passes. It consumes only the passing manifest, loads inputs sequentially, creates outputs in hidden attempt-local staging, runs the exact artifact validator, and atomically publishes only a complete `results/` directory.
- Approved proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup`, with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`. Do not create it before consolidated kickoff approval; never overwrite, delete, or automatically back up existing material. `/xdisk` is temporary and unbacked.
- Exclude ELM simulation, postprocessing, input mutation or repair, member/time dropping, interpolation, alternative pool definitions, layer weighting, vegetation pools, compensation plots, litter ratios, temporal-standard-deviation products, cross-site/configuration comparison, prior-result regeneration, surrogate modeling, PAWN/Sobol/global sensitivity, interactions, causal limitation, optimization, tuning, thresholds, and parameter recommendations.

### Tentative gates, decision rule, resources, retries, and authority boundary

- Input/provenance gate: exactly 21 mapped pickles, configs, parameter files, and restart cases with 2,100 uniquely mapped members match the locked identities; every pickle has the exact ABBY/100-member/2018--2024 contract; every restart member has the exact final timestamp and required component schema; control and observation dependencies match newly recorded hashes.
- Calculation gate: direct-HR use, five transient means, three restart totals, observation separation, masks/support, units, parameter coordinates, equal-count bins, conditional scores/ranks, and potential/N/P-limited pathway multiplication and summation order pass fixtures and independent reproduction.
- Artifact/visual gate: exactly 80,200 primary CSV rows and 11 PNGs with correct membership, units, labels, support, native markers, observed SR line, ranks, and legibility; no standard-deviation, compensation, or litter artifacts exist.
- Publication/review/accounting/record gate: manifests cover the full payload, hidden staging validates before atomic publication, a different read-only reviewer passes preparation and final calculation/artifact/visual checks, every job receives job-scoped terminal `sacct` evidence, and the iteration report, compact result, cumulative summary, registry, and handoff agree under the final validator.
- Decision rule: technical acceptance depends only on the immutable gates, not on ranking magnitude or hypothesis direction. Report only baseline-conditioned, sampled-range descriptive OAT evidence.
- Proposed Puma envelope: `development/hpc/puma.md`, `standard/chopinsong`, one node/task, 16 CPUs with standard-derived 80 GB; two hours for preflight and four hours for diagnostic under `OLMT_puma`. Recheck host, account, limits, environment, capacity, and storage at kickoff.
- Retry budget for each work unit is one initial attempt plus at most three retries, for at most four preflight attempts and four diagnostic attempts. Preflight retries may include at most one minimal correction that restores the locked validation/interface contract without changing inputs, calculations, artifacts, interpretation, or gates; other retries are limited to classified same-scope scheduler/resource failures. Diagnostic retries are limited to classified same-scope scheduler/resource failures. Application, code, interface, schema, data, dependency, numerical, scientific, publication, or gate failures require classification, preserved evidence, a revised package, and fresh user authority before change or rerun. Retry resources may not exceed 16 CPUs/80 GB and six hours.
- Proposed monitoring requires immediate identity checks, one retained runtime-supported state-change monitor with bounded backoff and unchanged-output suppression, and job-scoped terminal accounting for every attempt. Empty `squeue` is not completion; query/transport failure means unknown state.
- Proposed cancellation is limited to recorded Iter011 job IDs under the future runtime contract for identity mismatch, a proven universal pre-execution defect, out-of-root writes, resource-contract overrun, or explicit user instruction, followed by terminal accounting.
- Expected evidence includes the approved contract; repository/source/config/submitted identities and hashes; exact input/dependency manifests; fixture and preflight receipts; dimensions, units, masks, support and coverage; table/figure counts; independent numerical reproductions and visual review; job IDs, logs, terminal accounting and resources; output manifest; scientific report; and cross-record validator output.
- The user authorized these planning-record updates and one scoped planning commit with no push. This planning-only approval grants no Iter011 initialization, implementation, repository Python, output-directory creation, review launch, scheduler operation, retry, cancellation, diagnostic publication, runtime closeout, or additional commit authority. Before any runtime work, present the complete consolidated kickoff package required by `WORKFLOW.md`, including exact lifecycle authority, outside-sandbox submission/monitoring/accounting/cancellation authority, and the already selected one-commit/no-push closeout branch, then obtain fresh explicit approval.
