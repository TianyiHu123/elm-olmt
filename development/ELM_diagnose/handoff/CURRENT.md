# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter011`
- Proposed iteration: `iter012`
- Status: `pre_kickoff`
- Phase: `planning`
- Active job scope: none; Iter011 jobs `24101686`, `24102996`, `24103048`, and `24103109` are terminally accounted.
- Active monitoring: none.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-07T02:06:23-07:00`

## Iter011 Closeout Snapshot

- Objective: rank baseline-conditioned transient carbon responses, final-spinup decomposer C/N/P states, and idealized decomposition pathways across 21 separate ABBY vertical-soil-carbon OAT ensembles.
- Acceptance: `pass`; exactly 80,200 primary CSV rows and 11 PNGs; input manifest `7f528763...`; output manifest `0e13dfa6168c0df852f0f19aa5a2c7db8549e43e17345a579014ffb5224e577a`.
- Execution: preflight `24101686` failed a launch-import defect; authorized corrected preflight `24102996` passed. Diagnostic `24103048` generated the complete package but failed an overbroad validator assertion. Under fresh user authority, validator-only job `24103109` passed and atomically published the unchanged staging package. All four jobs are terminally accounted and no monitor is active.
- Result: `act25` leads mean SR/HR/LITFALL response spreads and `leaf_long` leads GPP. `k_s4`, `k_s3`, and `k_s2` lead transient decomposer-C and final-spinup C/N/P spreads. Across all 2,100 members, mean N- and P-limited/potential pathway ratios are 0.294 and 0.388, with P-limited greater than N-limited for every member.
- Decision: accept the technically and independently validated package only as baseline-conditioned, sampled-range descriptive OAT evidence. Constructed potential/N/P-limited pathways are distinct from direct model `HR`; no global-sensitivity, interaction, causal, tuning, threshold, recommendation, or cross-site/configuration conclusion is supported.
- Records: `iterations/iter011.md`, `summaries/iter011/ITER011_RESULT.md`, `ITERATION_SUMMARY.md`, and the Iter011 registry row.

## Planning Authority and Next Action

- The user authorized the finalized Iter012 planning-only proposal, the two authoritative planning-record updates, and one scoped planning commit with no push.
- Current authority does not include Iter012 initialization, implementation, repository Python, output-directory creation, review launch, scheduler operation, retry, cancellation, publication, runtime closeout, or another commit.
- Next action: present one complete consolidated Iter012 kickoff package and runtime contract, including the exact outside-sandbox authority question required by `WORKFLOW.md`, then await fresh explicit approval.

## Proposed Iter012 Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Sequential ID and work type: `iter012`, implementation.
- Proposed run slug: `elm_diagnose_iter012_abby_ctrlvertc_oat_spinup`.
- Site and configuration: standalone ABBY with vertical soil carbon active; no site or configuration comparison.
- Objective: extend the complete Iter011 diagnostic unchanged from 21 to 27 separate ABBY one-parameter OAT ensembles, ranking baseline-conditioned transient carbon responses, final-spinup decomposer C/N/P states, and idealized potential/N/P-limited decomposition pathways after adding six respiration-fraction parameters.
- Hypothesis: the six transfer-fraction ensembles may show distinct range-conditional controls on transient fluxes, decomposer stocks, and constructed decomposition pathways relative to the original 21-parameter inventory. Technical acceptance is independent of the direction or magnitude of those responses.
- Interpretation boundary: results are range-dependent descriptive OAT responses conditioned on the baseline configuration and each declared one-parameter range. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal limitation, optimization, tuning, parameter recommendations, exact thresholds, or evidence for cross-site/configuration differences.

### Exact diagnostic inputs, dependencies, and trust assumptions

- Consume exactly these ordered `parameter:pickle` mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`; reject globs, discovery, duplicate parameters or basenames, path components in basenames, missing/extra top-level pickles, or substitutions:
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
  - `rf_l1s1:ABBY_ctrlvertcrfl1s1_I20TRCNPRDCTCBC.pkl`
  - `rf_l2s2:ABBY_ctrlvertcrfl2s2_I20TRCNPRDCTCBC.pkl`
  - `rf_l3s3:ABBY_ctrlvertcrfl3s3_I20TRCNPRDCTCBC.pkl`
  - `rf_s1s2:ABBY_ctrlvertcrfs1s2_I20TRCNPRDCTCBC.pkl`
  - `rf_s2s3:ABBY_ctrlvertcrfs2s3_I20TRCNPRDCTCBC.pkl`
  - `rf_s3s4:ABBY_ctrlvertcrfs3s4_I20TRCNPRDCTCBC.pkl`
- Map those parameters in the same order to the exact restart case basenames beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/restart`: `ABBY_ctrlvertcact25_I1850CNPRDCTCBC`, `ABBY_ctrlvertcbrmr_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns1_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns2_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns3_I1850CNPRDCTCBC`, `ABBY_ctrlvertccns4_I1850CNPRDCTCBC`, `ABBY_ctrlvertcdepthefold_I1850CNPRDCTCBC`, `ABBY_ctrlvertcfrootcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertcgrperc_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl1_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl2_I1850CNPRDCTCBC`, `ABBY_ctrlvertckl3_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks1_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks2_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks3_I1850CNPRDCTCBC`, `ABBY_ctrlvertcks4_I1850CNPRDCTCBC`, `ABBY_ctrlvertcleafcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertcleaflong_I1850CNPRDCTCBC`, `ABBY_ctrlvertclflitcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertclivewdcn_I1850CNPRDCTCBC`, `ABBY_ctrlvertcq10mr_I1850CNPRDCTCBC`, `ABBY_ctrlvertcrfl1s1_I1850CNPRDCTCBC`, `ABBY_ctrlvertcrfl2s2_I1850CNPRDCTCBC`, `ABBY_ctrlvertcrfl3s3_I1850CNPRDCTCBC`, `ABBY_ctrlvertcrfs1s2_I1850CNPRDCTCBC`, `ABBY_ctrlvertcrfs2s3_I1850CNPRDCTCBC`, and `ABBY_ctrlvertcrfs3s4_I1850CNPRDCTCBC`. Each must contain exactly `g00001`--`g00100/<case_basename>.elm.r.0201-01-01-00000.nc`; do not infer or substitute cases from the shared root.
- Require the corresponding 27 configs beneath `.../ABBY/config` and 27 parameter files beneath `.../NEON_ctrlvertc_sensi/params` as provenance cross-checks. The six additions are exactly `ABBY_rf_l1s1.cfg`/`rf_l1s1_paramfile`, `ABBY_rf_l2s2.cfg`/`rf_l2s2_paramfile`, `ABBY_rf_l3s3.cfg`/`rf_l3s3_paramfile`, `ABBY_rf_s1s2.cfg`/`rf_s1s2_paramfile`, `ABBY_rf_s2s3.cfg`/`rf_s2s3_paramfile`, and `ABBY_rf_s3s4.cfg`/`rf_s3s4_paramfile`; each parameter file declares a linear `0.1--0.9` range. Pickle metadata remains authoritative for identity, selector, bounds, samples, site, member count, years, output variables, and time axes; stale embedded Perlmutter paths are never dereferenced.
- Preserve the Iter011 control-parameter and contextual SR-observation dependencies and recompute every source hash at kickoff and preflight.
- Planning-time read-only inspection on Puma found exactly 27 pickles totaling 106,366,940,620 bytes, 27 configs, 27 parameter files, and 27 restart cases with exact `g00001`--`g00100` final files, for 2,700 restart files totaling 1,112,112,400 bytes. The proposed output root is absent. Full pickle content, hashes, dimensions, units, masks, finiteness, deserialization compatibility, and all-member transient/restart parity remain compute-node preflight gates.

### Reusable engine and locked calculations

- Reuse `development/ELM_diagnose/tools/oat_sensitivity.py` and the complete Iter011 scientific interface without changing formulas or adding ABBY-, Iter012-, or inventory-specific defaults. Only general fixture/validation support needed to lock the 27-parameter inventory and its deterministic `6 x 5` atlas layout may be added.
- Preserve 100 members per parameter, exactly 61,320 no-leap hourly samples for 2018--2024, log10 coordinates only for `k_l1`--`k_l3` and `k_s1`--`k_s4`, linear coordinates for the other 20 parameters, ten deterministic equal-count bins, member points, bin medians, and supported native markers.
- Preserve the five transient arithmetic-mean endpoints: direct `SR`, direct `HR`, direct `GPP`, direct `LITFALL`, and `DECOMP_C_TOTAL = CWDC + LITR1C + LITR2C + LITR3C + SOIL1C + SOIL2C + SOIL3C + SOIL4C`. Direct `HR` must remain `case.output["HR"]`; the contextual observed SR line never enters model statistics or scores.
- Preserve final-spinup `DECOMP_C_TOTAL`, `DECOMP_N_TOTAL`, and `DECOMP_P_TOTAL` as masked-array-aware sums of the exact eight corresponding lowercase vertical restart arrays. Require exact member/file identity, component names, shapes, compatible units, finite unmasked values, and recorded valid/masked support; introduce no layer weighting or vegetation pools.
- Retain the range-conditional score `100 * (P95 - P05) / abs(ensemble median)` and descending within-endpoint rank. A nonfinite or zero denominator remains explicitly unsupported with a reason, never zero.
- Preserve the eight Iter011 pool/rate mappings and `FPI`/`FPI_P` limiters. Calculate potential pool decomposition as `pool_C * K_pool`, N-limited as `FPI * potential`, and P-limited as `FPI_P * potential`, multiply hourly flux by 3,600 seconds, then sum over pools and time. Constructed pathways remain distinct from direct model `HR`.
- Keep compensation and litter-ratio interfaces omitted. Produce no temporal-standard-deviation products. Regression checks must prove that the original Iter011 formulas, schemas, optional-family exclusions, and ordering remain unchanged apart from the enlarged declared inventory.

### Figures, machine-readable artifacts, and report

- Publish exactly 11 ABBY-labelled PNGs: five 27-panel transient-mean response atlases, three 27-panel final-spinup response atlases, one transient-mean score/rank heatmap, one final-spinup score/rank heatmap, and one 27-panel accumulated potential/N-limited/P-limited pathway atlas. Each atlas uses the engine's deterministic `6 x 5` layout with unused panels disabled.
- Publish exactly 103,114 primary CSV data rows excluding headers: 27 parameter metadata; 2,700 transient member metrics; 135 transient scores; 14,850 transient response-curve rows; one SR observation; 2,700 spinup member metrics; 81 spinup scores; 8,910 spinup response-curve rows; 72,900 pathway pool/member rows; and 810 pathway total-curve rows.
- Tables retain Iter011 definitions, units, identities, coverage, score denominator/support, rank scope, restart support, and explicit rejection reasons. Manifests record every mapped absolute source, hash, artifact, size, row count, and SHA-256.
- Produce the same compact report structure as Iter011, covering inputs, methods, units, model and observation coverage, range-conditional rankings, directions/nonlinearities, pathway comparisons, limitations, and unsupported quantities. Closeout records would be `iterations/iter012.md`, `summaries/iter012/ITER012_RESULT.md`, one cumulative-summary append, one registry row, rebuilt handoff, and Iter012 execution material.

### Bounded scope, work units, exclusions, and output policy

- Work unit one is a bounded compute-node preflight. It validates exact 27-way inventories and hashes, safe deserialization, config/parameter provenance, time/member axes, direct targets, observation coverage, all 2,700 restart mappings and 24 restart variables, masks/dimensions/units/support, score behavior, pathway formulas, optional-interface exclusions, the `6 x 5` layouts, deterministic fixtures, and exact artifact expectations. It publishes only an immutable input manifest and validation receipt in its attempt directory.
- Work unit two is one diagnostic operation after preflight passes. It consumes only the passing manifest, loads inputs sequentially, creates outputs in hidden attempt-local staging, runs the exact artifact validator, and atomically publishes only a complete `results/` directory.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter012_abby_ctrlvertc_oat_spinup`, with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`. Do not create it before consolidated kickoff approval; never overwrite, delete, or automatically back up existing material. `/xdisk` is temporary and unbacked.
- Exclude ELM simulation, postprocessing, input mutation or repair, member/time dropping, interpolation, alternative pool definitions, layer weighting, vegetation pools, compensation plots, litter ratios, temporal-standard-deviation products, cross-site/configuration comparison, prior-result regeneration, surrogate modeling, PAWN/Sobol/global sensitivity, interactions, causal limitation, optimization, tuning, thresholds, and parameter recommendations.

### Tentative gates, decision rule, resources, retries, and authority boundary

- Input/provenance gate: exactly 27 mapped pickles, configs, parameter files, and restart cases with 2,700 uniquely mapped members match the locked identities; every pickle has the exact ABBY/100-member/2018--2024 contract; every restart member has the exact final timestamp and required component schema; control and observation dependencies match newly recorded hashes.
- Calculation gate: direct-HR use, five transient means, three restart totals, observation separation, masks/support, units, coordinates, equal-count bins, conditional scores/ranks, and pathway multiplication/summation order pass fixtures and independent reproduction.
- Artifact/visual gate: exactly 103,114 primary CSV rows and 11 PNGs with correct membership, units, labels, support, native markers, observed SR line, ranks, disabled empty panels, and legibility; no standard-deviation, compensation, or litter artifacts exist.
- Publication/review/accounting/record gate: manifests cover the full payload, hidden staging validates before atomic publication, a different read-only reviewer passes preparation and final calculation/artifact/visual checks, every job receives job-scoped terminal `sacct` evidence, and all durable records agree under the final validator.
- Decision rule: technical acceptance depends only on the immutable gates, not on ranking magnitude or hypothesis direction. Report only baseline-conditioned, sampled-range descriptive OAT evidence.
- Proposed Puma envelope: `development/hpc/puma.md`, `standard/chopinsong`, one node/task, 16 CPUs and 80 GB; two hours for preflight and four hours for diagnostic under `OLMT_puma`. Recheck host, account, limits, environment, capacity, storage, and the 80 GB headroom at kickoff because Iter011 reached approximately 77.2 GB MaxRSS.
- Proposed retry budget matches Iter011: one initial attempt plus at most three retries per work unit; at most one minimal preflight-only correction; all other automatic retries are classified same-scope scheduler/resource failures only. Application, code, interface, schema, data, dependency, numerical, scientific, publication, or gate failures require classification, preserved evidence, a revised package, and fresh user authority. Retry resources may not exceed 16 CPUs/80 GB and six hours.
- Proposed monitoring requires an immediate identity check, one retained runtime-supported state-change monitor with bounded backoff and unchanged-output suppression, and job-scoped terminal accounting for every attempt. Empty `squeue` is not completion; query/transport failure means unknown state.
- Proposed cancellation is limited to recorded Iter012 job IDs under a future runtime contract for identity mismatch, a proven universal pre-execution defect, out-of-root writes, resource-contract overrun, or explicit user instruction, followed by terminal accounting.
- Expected evidence includes the approved contract; repository/source/config/submitted identities and hashes; exact manifests; fixture/preflight receipts; dimensions, units, masks, support and coverage; row/figure counts; independent numerical reproduction and visual review; job IDs, logs, terminal accounting and resources; output manifest; scientific report; and cross-record validator output.
- The user's `2026-10-07` request authorized finalizing this planning-only proposal, updating the two authoritative planning records, and one scoped planning commit with no push. It grants no Iter012 initialization, implementation, repository Python, output-directory creation, review launch, scheduler operation, retry, cancellation, diagnostic publication, runtime closeout, or additional commit authority. Before runtime work, present the complete consolidated kickoff package required by `WORKFLOW.md`, including exact lifecycle authority, outside-sandbox submission/monitoring/accounting/cancellation authority, and the proposed closeout branch, then obtain fresh explicit approval.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter011.md`, its compact result, the Iter011 registry row, and `development/hpc/puma.md`.
3. Treat Iter011 execution material, records, manifests, and results as immutable closed provenance.
4. Verify the exact 27-way input inventory and current repository/HPC state, then present the complete Iter012 kickoff package; Iter012 remains uninitialized until fresh approval.
