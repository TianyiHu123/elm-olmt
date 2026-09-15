# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter006`
- Proposed iteration: `iter007` (`not_initialized`)
- Status: `not_initialized`
- Phase: `ready_for_kickoff_approval`
- Active job scope: none. Preflight jobs `23856493`, `23856561`, and `23856771`, and diagnostic job `23861155`, are terminally accounted.
- Active monitoring: none. Detector sessions `12372` and `65404` are retired; the attempt-three preflight detector was not started before a recorded platform interruption.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-15T13:57:21-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter006`
- Work type: `implementation`
- Objective: Apply the complete Iter005 extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles with explicit site-generalized tooling.
- Bounded scope: 14 exact JERC pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated JERC range-conditional descriptive OAT and pathway/stoichiometry package under the approved explicit-gap support contract; no global sensitivity, interaction, causal, optimization, tuning, parameter-value, or cross-site claim.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter006.md`.
- Compact result: `development/ELM_diagnose/summaries/iter006/ITER006_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter006_jerc_oat_extended/results`.
- Input manifest SHA-256: `b10901c14c8d5689f1a704038860f51d79d9fa3ca663bfdef510555c9f5941f0`.
- Output manifest SHA-256: `256cc1e1318aaa3e2a2ceaa123fdb06f2fd9e7ff224f4950caea659e4571ec31`.
- Passing work: revised preflight `23856771 COMPLETED 0:0`; diagnostic `23861155 COMPLETED 0:0`; artifact validator passed 3,520,119 rows and 44 figures before atomic publication.
- Classified failures: preflight `23856493 FAILED 1:0` on abbreviated/full commit-SHA mismatch; preflight `23856561 FAILED 1:0` on the original all-members litter-denominator gate. The latter led to the user-approved explicit-gap contract; neither was a scheduler/resource failure.
- Review: independent read-only `/root/iter006_review`; corrected preparation material passed, and final results passed with only retained visual-quality concerns.
- Mean fluxes in gC m-2 day-1: potential/P-limited HR `3.961651`, N-limited HR `3.560783`, model SR `2.930035`, observed SR `1.326166`. Relative to model SR: `+35.21%`, `+35.21%`, `+21.53%`, and `-54.74%`; N limitation reduces potential HR by `10.12%`.
- Litter support: 1,363 supported and 37 rejected members per ratio; all rejections are `nonpositive_nutrient_total`. Observation coverage is 51,882/61,320 hours (`84.61%`).

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. Observation context does not enter screening scores, incomplete observation support is not time-matched, and unsupported ratios are gaps rather than zeros.
- Heatmap annotation contrast is weak in some cells. Axis-offset notation magnifies machine-scale numerical scatter in effectively constant litter-ratio panels; do not interpret that display noise as sensitivity.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the query is PI-only.
- Next state: the Iter007 ABBY vertical-soil-carbon extended OAT plan is planning-only and awaits a fresh consolidated kickoff package and explicit runtime approval.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter006.md`, its compact summary, and the Iter006 registry row.
3. Treat Iter006 code, Slurm material, outputs, summary, and registry evidence as immutable closed provenance.
4. Confirm the complete Iter007 plan below still matches current inputs and constraints.
5. Present one consolidated kickoff package and obtain fresh explicit approval before initialization, implementation, Python, review, external output creation, scheduler action, retry, cancellation, or commit.

## Proposed Next-Iteration Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Proposed sequential ID and work type: `iter007`, implementation.
- Proposed run slug: `elm_diagnose_iter007_abby_ctrlvertc_oat_extended`.
- Objective: apply the complete Iter005/Iter006 extended OAT diagnostic package to the new ABBY one-parameter ensembles produced with vertical soil carbon enabled, using the same calculations, interfaces, artifact schemas, and descriptive interpretation.
- Hypothesis: the new ABBY vertical-soil-carbon ensembles, including `decomp_depth_efolding`, will produce parameter-conditional response curves, decomposition pathways, and litter-flux stoichiometry that can be characterized without inferring interactions or transferring conclusions from the earlier ABBY or JERC ensembles.
- Interpretation boundary: results remain baseline-conditioned and range-dependent OAT diagnostics. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal effects, optimization, tuning, parameter-value recommendations, or configuration-comparison evidence.
- Cross-configuration and cross-site comparisons are excluded. Iter007 produces a standalone ABBY vertical-soil-carbon package and does not statistically compare or rank it against Iter005 ABBY or Iter006 JERC.

### Proposed inputs, dependencies, and trust assumptions

- Use exactly the following 13 explicit mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles`; reject discovery, globs, path components in mappings, duplicates, missing/extra parameters, and unlisted top-level pickle files:
  - `act25:ABBY_ctrlvertcact25_I20TRCNPRDCTCBC.pkl`
  - `br_mr:ABBY_ctrlvertcbrmr_I20TRCNPRDCTCBC.pkl`
  - `decomp_depth_efolding:ABBY_ctrlvertcdepthefold_I20TRCNPRDCTCBC.pkl`
  - `grperc:ABBY_ctrlvertcgrperc_I20TRCNPRDCTCBC.pkl`
  - `k_l1:ABBY_ctrlvertckl1_I20TRCNPRDCTCBC.pkl`
  - `k_l2:ABBY_ctrlvertckl2_I20TRCNPRDCTCBC.pkl`
  - `k_l3:ABBY_ctrlvertckl3_I20TRCNPRDCTCBC.pkl`
  - `k_s1:ABBY_ctrlvertcks1_I20TRCNPRDCTCBC.pkl`
  - `k_s2:ABBY_ctrlvertcks2_I20TRCNPRDCTCBC.pkl`
  - `k_s3:ABBY_ctrlvertcks3_I20TRCNPRDCTCBC.pkl`
  - `k_s4:ABBY_ctrlvertcks4_I20TRCNPRDCTCBC.pkl`
  - `leaf_long:ABBY_ctrlvertcleaflong_I20TRCNPRDCTCBC.pkl`
  - `q10_mr:ABBY_ctrlvertcq10mr_I20TRCNPRDCTCBC.pkl`
- `grpnow` and `kmax` are intentionally absent. The user-facing shorthand `depth_efold` maps to the model parameter name `decomp_depth_efolding`, as declared by `depth_efold_paramfile.txt`; the exact model name is used in the diagnostic mapping and manifests.
- Reuse control parameter NetCDF `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` for native markers. Planning-time shell inspection confirms that its header contains `decomp_depth_efolding`; its planning-time SHA-256 is `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9` and must be recomputed at kickoff and preflight.
- Use explicit observation mapping `SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc`. Its planning-time SHA-256 is `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` and must be recomputed at kickoff and preflight.
- Iter005 and Iter006 code, fixtures, manifests, results, and closeout evidence are provenance and regression-design references, not substitutes for a new preflight and not data dependencies.
- Pickle metadata is authoritative for parameter identity, bounds, samples, site, member count, years, variables, and time axes. The 13 transferred configuration files and parameter files are provenance cross-checks only; stale embedded Perlmutter runtime paths are never dereferenced.
- Planning-time shell inspection found exactly 13 expected configs, 13 top-level parameter files, and 13 expected pickles totaling approximately 39 GB. Each pickle is approximately 3.140 GB, every config declares `use_vertsoilc = .true.`, all 13 postprocessing sections are identical, and they request hourly 2018--2024 output with the full Iter005/006 required-variable union plus additional variables. Pickle content, deserialization compatibility, array shape, units, finiteness, and completeness remain unverified until an approved Puma compute-node preflight.

### Locked analysis parity and interfaces

- Reuse `development/ELM_diagnose/tools/oat_sensitivity.py` with explicit `--site ABBY`. Make only the minimal generalized changes needed for the 13-parameter inventory and the new exact parameter name; do not add ABBY, vertical-soil-carbon, or work-specific defaults to reusable code.
- Preserve 100 members per parameter; log10 coordinates for `k_l1`--`k_l3` and `k_s1`--`k_s4`; linear coordinates for `act25`, `br_mr`, `decomp_depth_efolding`, `grperc`, `leaf_long`, and `q10_mr`; and exactly 61,320 no-leap hourly samples spanning 2018--2024.
- Preserve arithmetic temporal mean and population standard deviation (`ddof=0`) and the conditional screening score `100 * (P95 - P05) / abs(ensemble median)`.
- Pass the same 13 standard targets through repeated `--target`: `GPP`, `ER`, `SR`, `HR_TOTAL`, `LITFALL`, `LITTER_SOIL_C_TOTAL`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`, `SOIL3C`, and `SOIL4C`.
- Pass only the explicit ABBY SR observation through `--observation`; its mean and population temporal standard deviation are contextual horizontal references and do not alter model statistics or OAT scores.
- Preserve the seven independent compensation mappings: `k_l1:LITR1C:K_LITR1:LITR1_HR`, `k_l2:LITR2C:K_LITR2:LITR2_HR`, `k_l3:LITR3C:K_LITR3:LITR3_HR`, `k_s1:SOIL1C:K_SOIL1:SOIL1_HR`, `k_s2:SOIL2C:K_SOIL2:SOIL2_HR`, `k_s3:SOIL3C:K_SOIL3:SOIL3_HR`, and `k_s4:SOIL4C:K_SOIL4:SOIL4_HR`.
- Preserve eight HR pools: `CWDC:K_CWD`, `LITR1C:K_LITR1`, `LITR2C:K_LITR2`, `LITR3C:K_LITR3`, `SOIL1C:K_SOIL1`, `SOIL2C:K_SOIL2`, `SOIL3C:K_SOIL3`, and `SOIL4C:K_SOIL4`, with `FPI` as the N limiter and `FPI_P` as the P limiter.
- Preserve four litter ratios: `leaf_cn:LEAFC_TO_LITTER:LEAFN_TO_LITTER`, `leaf_cp:LEAFC_TO_LITTER:LEAFP_TO_LITTER`, `froot_cn:FROOTC_TO_LITTER:FROOTN_TO_LITTER`, and `froot_cp:FROOTC_TO_LITTER:FROOTP_TO_LITTER`.
- Preserve Iter005/006 formulas and units: potential pool HR is `poolC * K_pool` in `gC m-2 s-1`; accumulated potential, N-limited, and P-limited HR uses `sum(hourly_flux * 3600)`; actual HR remains intentionally unplotted. Hourly litter ratios use finite positive denominators, while parameter-response ratios use accumulated elemental mass before division and retain unsupported members as explicit gaps with reasons.
- Analyze required variables exactly as stored in each pickle and require every required array to normalize unambiguously to `61,320 x 100` time by member. The additional postprocessed vegetation, nutrient, soil-state, and scalar variables are out of scope. Iter007 does not introduce depth-resolved aggregation, layer weighting, or new targets; any need for those changes is a new scientific-method decision requiring a revised plan.
- Preserve independent interface families: standard targets do not implicitly enable compensation, HR, litter, or observation outputs, and specialized mappings do not modify standard rankings.

### Bounded scope, work units, and exclusions

- Create only Iter007-specific wrappers, configurations, fixtures, and validators under `development/ELM_diagnose/slurm/iter007/` after kickoff approval. Preserve Iter004--Iter006 tools at their recorded commits, execution material, outputs, summaries, registry evidence, and published artifacts as closed provenance.
- Work unit one is a bounded compute-node preflight. It validates exact input identity and hashes, safe deserialization, site and `use_vertsoilc` provenance, one varied parameter and 100 finite in-range samples per pickle, exact time axes, the full required-variable union and unambiguous time-by-member arrays, observation support, limiter bounds, formulas, unit conversions, deterministic fixtures, dynamic 13-parameter artifact expectations, and absence of hidden `grpnow`/`kmax` inputs.
- Work unit two is the ABBY vertical-soil-carbon diagnostic. It consumes only the passing manifest, loads one pickle at a time, retains bounded summaries, generates into hidden staging, validates before publication, and atomically publishes only a complete results directory.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended`, with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`.
- No ELM simulation, postprocessing, input repair, member/time dropping, depth-profile reconstruction, analysis of extra output variables, Iter005/006 regeneration, cross-site or cross-configuration comparison, surrogate, PAWN/Sobol analysis, interaction inference, optimization, tuning, or parameter-value recommendation is in scope.

### Tentative acceptance gates and decision rule

- Input gate: exactly the declared 13 pickles, shared control NetCDF, and ABBY SR observation exist, are readable, and match newly recorded hashes; every pickle reports site `ABBY`, one declared varied parameter, 100 finite bounded samples, the expected required variables, and an exact 2018--2024 hourly axis. No undeclared top-level pickle is permitted.
- Configuration/provenance gate: exactly 13 configs and 13 parameter files agree with the mapping, all configs declare `use_vertsoilc = .true.`, their postprocessing contracts are identical, and `grpnow`/`kmax` are absent. Configuration paths are evidence only and are not runtime dependencies.
- Interface and parity gate: `--site ABBY`, the ordered 13-parameter mapping, log-parameter set, ordered targets, and all specialized mappings match this plan; deterministic fixtures prove unchanged Iter006 calculations with a 13-parameter inventory and `decomp_depth_efolding`; no work-specific default enters reusable code.
- Observation gate: ABBY SR has unique hourly timestamps, recognized/convertible units, and finite valid overlap in the model window; count, coverage, range, mean, and population standard deviation are recorded. Observation context never enters an OAT score.
- Calculation and shape gate: every required model array is finite where required and normalizes unambiguously to `61,320 x 100`; target derivations, population statistics, conditional score, HR multiplication/limiting/integration order, and litter ratios reproduce the Iter006 explicit-gap contract. FPI/FPI_P must be finite in `[0,1]`; unsupported litter ratios remain gaps with recorded support and rejection reason.
- Artifact gate: publish exactly 13 parameter rows, 1,300 member rows, 338 sensitivity-score rows, 37,180 response-curve rows, one observation row, 35,100 HR-pathway rows, 390 HR-curve rows, 5,200 litter member-ratio rows, 3,188,640 litter time-series rows, 520 litter-curve rows, and 44 ABBY-labelled PNGs, totaling 3,268,682 data rows. Manifests must cover exact membership and hashes.
- Publication/review/accounting/record gate: validation passes on hidden staging before atomic publication; representative figures pass visual inspection; independent read-only review passes or all concerns are resolved; all jobs are terminally reconciled; and iteration report, summary, registry, and handoff agree.
- Iter005/006 table hashes are not regression oracles for the new model configuration. Exact-analysis parity is established by locked interfaces/formulas, deterministic fixtures, schemas, dynamic counts, input/output manifests, and review.
- Decision rule: if every gate passes, accept a validated ABBY vertical-soil-carbon range-conditional descriptive OAT/pathway/stoichiometry package. A genuine input, schema, dimensionality, dependency, numerical, or scientific gate failure stops for classification and a fresh decision; it is not silently repaired or reframed as a scientific conclusion.

### Proposed site, resources, retries, cancellation, evidence, and authority boundary

- Proposed HPC site/profile: Puma using `development/hpc/puma.md`, account `chopinsong`, partition `standard`, and environment `OLMT_puma`; revalidate host, account/partition access, current limits, storage, module, and environment availability at kickoff/preflight.
- Proposed initial resources: preflight uses one node/task and eight CPUs (40 GB) for two hours; diagnostic uses one node/task and 12 CPUs (60 GB) for four hours. The larger diagnostic allocation reflects approximately 3.140 GB per new pickle versus approximately 2.208 GB in Iter005/006 and the Iter006 diagnostic peak of 32.87 GB.
- Proposed retry budget: two retries after the initial attempt for each work unit. Autonomous retry is limited to classified scheduler/resource failure or one minimal preflight-only correction restoring the locked interface, validation, or publication contract without changing inputs, formulas, targets, mappings, interpretation, or gates. Retry resources may rise only to 16 CPUs (80 GB) and six hours. Diagnostic application/code/interface/schema/data/dependency/numerical failures and material changes require a revised package and fresh approval.
- Proposed monitoring: immediate job-identity validation followed by one retained runtime-supported state-change monitor with bounded backoff and unchanged-state output suppressed; reconcile every expected job through job-scoped `sacct`. Query or transport failure means unknown state, not completion or retry authority. Exact cadence and mechanism must be locked in the kickoff package.
- Proposed cancellation: only recorded Iter007 job IDs, only on explicit user direction or a proven universal pre-execution defect covered by the eventual runtime contract, followed by terminal accounting.
- Expected evidence: source/config/submitted hashes and byte identity; exact input inventory and hashes; immutable input, validation, and output manifests; fixture and observation receipts; dimensionality and support evidence; table/figure counts; representative visual checks; reviewer identity/findings; job IDs, logs, accounting, and resources; compact ABBY vertical-soil-carbon interpretation; and cross-record validation.
- Expected Git records after eligible results: `iterations/iter007.md`, `summaries/iter007/`, an `ITERATION_SUMMARY.md` append, one `registry.csv` row, rebuilt `handoff/CURRENT.md`, and Iter007 execution material. Large outputs remain outside Git.
- Stop at validated closeout with no active or unaccounted jobs, or earlier for exhausted authority, immutable rejection without an in-contract correction, or a fresh material decision outside the approved package.
- This planning-only proposal grants no Iter007 initialization, Python execution, implementation, directory creation, review launch, scheduler operation, retry, cancellation, output publication, or commit authority. Before any such action, present one consolidated kickoff package containing this plan unchanged, refreshed bootstrap evidence, exact lifecycle and outside-sandbox authority, resources, monitoring, retry/cancellation terms, stop conditions, and the closeout-commit choice, then obtain fresh explicit approval.
