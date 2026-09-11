# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter005`
- Proposed iteration: `iter006` (`not_initialized`)
- Status: `not_initialized`
- Phase: `ready_for_kickoff_approval`
- Active job scope: none; Iter005 jobs `23834279`, `23834351`, `23834413`, and `23834468` are terminally accounted.
- Active monitoring: none; detector sessions `27428` and `93091` are retired after terminal reconciliation.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-10T19:21:42-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter005`
- Work type: `implementation`
- Objective: Extend the reusable ABBY OAT diagnostic with explicit targets, SR observation context, decomposition pathways, and litter-flux stoichiometry.
- Bounded scope: 14 exact historical pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated range-conditional descriptive OAT and pathway/stoichiometry package; no global sensitivity, interaction, causal, optimization, tuning, or parameter-value claim.
- Closeout branch: one authorized scoped commit selected; verification follows atomic commit creation.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter005.md`.
- Compact result: `development/ELM_diagnose/summaries/iter005/ITER005_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter005_abby_oat_extended/results`.
- Input manifest SHA-256: `7581cafa262c112e3881ecf30ef4c0f0425058e195b02de8b37002832a5592cc`.
- Output manifest SHA-256: `99d3f377f9242d85eac3c29d94ec88fc66a8b415a07d31cf6a8491306267e339`.
- Passing work: preflight `23834413 COMPLETED 0:0`; diagnostic `23834468 COMPLETED 0:0`; artifact validator passed 3,520,119 rows and 44 figures before atomic publication.
- Classified failures: preflight `23834279` and `23834351` each `FAILED 1:0` only on incorrect deterministic fixture expectations; both minimal corrections stayed within the approved contract, and the final preflight exhausted its authorized retry count by passing.
- Review: independent read-only `/root/iter005_review`; all blocking findings and record-only concerns resolved before launch.
- Final record/artifact result: `ITER005_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=44 data_rows=3520119 terminal_jobs=4 next_state=intentionally_stopped`.

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. Observation lines are contextual; no interaction, global-importance, causal, optimization, tuning, or parameter-value inference is supported.
- Observed SR mean and temporal variability exceed the full model-member ranges; P limitation is inactive in these declared total-pathway outputs; litter flux-weighted ratios are fixed across all declared cases.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the query is PI-only. Home usage was `41.4/50 GB` at bootstrap; do not install or recreate the environment.
- Next state: the Iter006 JERC extended OAT plan is approved as planning-only and awaits a fresh consolidated kickoff package and explicit runtime approval.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter005.md`, the compact summary, and the Iter005 registry row.
3. Treat Iter005 code, Slurm material, outputs, summary, and registry evidence as immutable closed provenance.
4. Confirm the complete Iter006 plan below still matches current inputs and constraints.
5. Present one consolidated kickoff package and obtain fresh explicit approval before initialization, implementation, Python, review, external output creation, scheduler action, retry, cancellation, or commit.

## Proposed Next-Iteration Plan (Planning Only)

### Identity, objective, and interpretation boundary

- Proposed sequential ID and work type: `iter006`, implementation.
- Proposed run slug: `elm_diagnose_iter006_jerc_oat_extended`.
- Objective: apply the complete Iter005 ABBY extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles, using the same calculations, interfaces, artifact schemas, and descriptive interpretation.
- Hypothesis: JERC-specific response curves, SR observation context, decomposition pathways, and litter-flux stoichiometry will characterize the responses within the declared JERC parameter ranges without inferring parameter interactions or transferring ABBY conclusions.
- Interpretation boundary: results remain baseline-conditioned and range-dependent OAT diagnostics. They are not PAWN, Sobol, joint/global sensitivity, interaction, mediation, causal effects, optimization, tuning, parameter-value recommendations, or site-ranking evidence.
- Site-to-site comparison is excluded. Iter006 produces a standalone JERC package and does not statistically compare or rank JERC against ABBY.

### Proposed inputs, dependencies, and trust assumptions

- Use exactly the following 14 explicit mappings beneath `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/JERC/pklfiles`; reject discovery, globs, path components in mappings, duplicates, missing/extra parameters, and unlisted top-level pickle files:
  - `act25:JERC_ctrlact25_I20TRCNPRDCTCBC.pkl`
  - `br_mr:JERC_ctrlbrmr_I20TRCNPRDCTCBC.pkl`
  - `grperc:JERC_ctrlgrperc_I20TRCNPRDCTCBC.pkl`
  - `grpnow:JERC_ctrlgrpnow_I20TRCNPRDCTCBC.pkl`
  - `k_l1:JERC_ctrlkl1_I20TRCNPRDCTCBC.pkl`
  - `k_l2:JERC_ctrlkl2_I20TRCNPRDCTCBC.pkl`
  - `k_l3:JERC_ctrlkl3_I20TRCNPRDCTCBC.pkl`
  - `k_s1:JERC_ctrlks1_I20TRCNPRDCTCBC.pkl`
  - `k_s2:JERC_ctrlks2_I20TRCNPRDCTCBC.pkl`
  - `k_s3:JERC_ctrlks3_I20TRCNPRDCTCBC.pkl`
  - `k_s4:JERC_ctrlks4_I20TRCNPRDCTCBC.pkl`
  - `kmax:JERC_ctrlkmax_I20TRCNPRDCTCBC.pkl`
  - `leaf_long:JERC_ctrlleaflong_I20TRCNPRDCTCBC.pkl`
  - `q10_mr:JERC_ctrlq10mr_I20TRCNPRDCTCBC.pkl`
- Reuse control parameter NetCDF `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` for native markers.
- Use explicit observation mapping `SR:/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc`. Its planning-time SHA-256 is `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` and must be recomputed at kickoff and preflight.
- Iter005 code, fixtures, manifests, results, and closeout evidence are provenance and regression-design references, not JERC data dependencies and not substitutes for a new preflight.
- Pickle metadata is authoritative for parameter identity, bounds, samples, site, member count, years, variables, and time axes. JERC configuration files are provenance cross-checks only; stale embedded runtime paths are never dereferenced.
- Planning-time shell inspection confirms the renamed `pklfiles` directory contains all 14 expected basenames, each approximately 2.208 GB. Pickle content and schema remain unverified until an approved compute-node preflight.

### Locked analysis parity and interfaces

- Add a required explicit `--site SITE` interface to `development/ELM_diagnose/tools/oat_sensitivity.py`; Iter006 passes `--site JERC`. The tool must validate every pickle's embedded site, record the site in manifests, and derive figure titles and filenames from it. No site default or JERC-specific reusable-code default is allowed.
- Preserve 100 members per parameter; log10 coordinates for `k_l1`--`k_l3` and `k_s1`--`k_s4`; linear coordinates for all other parameters; and exactly 61,320 no-leap hourly samples spanning 2018--2024.
- Preserve arithmetic temporal mean and population standard deviation (`ddof=0`) and the conditional screening score `100 * (P95 - P05) / abs(ensemble median)`.
- Pass the same 13 standard targets through repeated `--target`: `GPP`, `ER`, `SR`, `HR_TOTAL`, `LITFALL`, `LITTER_SOIL_C_TOTAL`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`, `SOIL3C`, and `SOIL4C`.
- Pass only the explicit JERC SR observation through `--observation`; its mean and population temporal standard deviation are contextual horizontal references and do not alter model statistics or OAT scores.
- Preserve the seven independent compensation mappings: `k_l1:LITR1C:K_LITR1:LITR1_HR`, `k_l2:LITR2C:K_LITR2:LITR2_HR`, `k_l3:LITR3C:K_LITR3:LITR3_HR`, `k_s1:SOIL1C:K_SOIL1:SOIL1_HR`, `k_s2:SOIL2C:K_SOIL2:SOIL2_HR`, `k_s3:SOIL3C:K_SOIL3:SOIL3_HR`, and `k_s4:SOIL4C:K_SOIL4:SOIL4_HR`.
- Preserve eight HR pools: `CWDC:K_CWD`, `LITR1C:K_LITR1`, `LITR2C:K_LITR2`, `LITR3C:K_LITR3`, `SOIL1C:K_SOIL1`, `SOIL2C:K_SOIL2`, `SOIL3C:K_SOIL3`, and `SOIL4C:K_SOIL4`, with `FPI` as the N limiter and `FPI_P` as the P limiter.
- Preserve four litter ratios: `leaf_cn:LEAFC_TO_LITTER:LEAFN_TO_LITTER`, `leaf_cp:LEAFC_TO_LITTER:LEAFP_TO_LITTER`, `froot_cn:FROOTC_TO_LITTER:FROOTN_TO_LITTER`, and `froot_cp:FROOTC_TO_LITTER:FROOTP_TO_LITTER`.
- Preserve Iter005 formulas and units: potential pool HR is `poolC * K_pool` in `gC m-2 s-1`; accumulated potential, N-limited, and P-limited HR uses `sum(hourly_flux * 3600)`; actual HR remains intentionally unplotted. Hourly litter ratios use finite positive denominators, while parameter-response ratios use accumulated elemental mass before division.
- Preserve independent interface families: standard targets do not implicitly enable compensation, HR, litter, or observation outputs, and specialized mappings do not modify standard rankings.

### Bounded scope, work units, and exclusions

- Generalize only the reusable site's validation, manifest identity, titles, and filenames needed to support explicit `--site JERC`; create only Iter006-specific wrappers, configurations, fixtures, and validators under `development/ELM_diagnose/slurm/iter006/` after kickoff approval. Preserve all Iter004 and Iter005 code snapshots, Slurm material, outputs, summaries, registry evidence, and published artifacts as closed provenance.
- Work unit one is a bounded compute-node preflight. It validates the explicit site interface, all input identities and hashes, pickle schemas and exact membership, observation schema/time/unit support, required time-by-member arrays, limiter bounds, formulas, unit conversions, deterministic fixtures, dynamic artifact expectations, and site-neutral behavior. A paired synthetic ABBY/JERC fixture must prove identical numerical calculations for identical synthetic data while permitting only declared site metadata, titles, and filename differences.
- Work unit two is the JERC diagnostic. It consumes only the passing manifest, loads one pickle at a time, retains bounded summaries, generates into hidden staging, validates before publication, and atomically publishes only a complete results directory.
- Proposed output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter006_jerc_oat_extended`, with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`.
- No ELM simulation, postprocessing, input repair, member/time dropping, ABBY regeneration, cross-site comparison, surrogate, PAWN/Sobol analysis, interaction inference, optimization, tuning, or parameter-value recommendation is in scope.

### Tentative acceptance gates and decision rule

- Input gate: exactly the declared 14 JERC pickles, shared control NetCDF, and JERC SR observation exist, are readable, and match newly recorded hashes; every pickle reports site `JERC`, one varied parameter, 100 finite bounded samples, the expected required variables, and an exact 2018--2024 hourly axis.
- Interface and parity gate: a required `--site JERC` controls site validation and presentation without changing calculations; ordered targets and all specialized mappings match this plan; paired synthetic-site fixtures prove numeric parity; no ABBY or JERC default remains in reusable code.
- Observation gate: JERC SR has unique hourly timestamps, recognized/convertible units, and finite valid overlap in the model window; count, coverage, range, mean, and population standard deviation are recorded. Observation context never enters an OAT score.
- Calculation gate: target derivations, population statistics, conditional score, HR multiplication/limiting/integration order, and litter ratios reproduce the Iter005 contract. FPI/FPI_P must be finite in `[0,1]`; every flux-weighted member denominator must be finite and positive; hourly unsupported ratios remain gaps with recorded support.
- Artifact gate: publish exactly 14 parameter rows, 1,400 member rows, 364 sensitivity-score rows, 40,040 response-curve rows, one observation row, 37,800 HR-pathway rows, 420 HR-curve rows, 5,600 litter member-ratio rows, 3,433,920 litter time-series rows, 560 litter-curve rows, and 44 JERC-labelled PNGs, totaling 3,520,119 data rows. Manifests must cover exact membership and hashes.
- Publication/review/accounting/record gate: validation passes on hidden staging before atomic publication; representative figures pass visual inspection; independent read-only review passes or all concerns are resolved; all jobs are terminally reconciled; and iteration report, summary, registry, and handoff agree.
- ABBY table hashes are not a valid regression oracle for JERC values. Exact-analysis parity is established by locked interfaces/formulas, paired synthetic fixtures, schemas, counts, input/output manifests, and review.
- Decision rule: if every gate passes, accept a validated JERC range-conditional descriptive OAT/pathway/stoichiometry package. A genuine input, schema, dependency, numerical, or scientific gate failure stops for classification and a fresh decision; it is not silently repaired or reframed as a scientific conclusion.

### Proposed site, resources, retries, cancellation, evidence, and authority boundary

- Proposed HPC site/profile: Puma using `development/hpc/puma.md`, account `chopinsong`, partition `standard`, and environment `OLMT_puma`; revalidate current account, limits, storage, module, and environment availability at kickoff/preflight.
- Proposed initial resources: one node/task and eight CPUs (40 GB) for each work unit; two hours for preflight and four hours for diagnostic. This matches the successful Iter005 envelope and similarly sized JERC pickles.
- Proposed retry budget: two retries after the initial attempt for each work unit. Autonomous retry is limited to classified scheduler/resource failure or a minimal correction restoring the locked interface, calculation, validation, or publication contract without changing inputs, formulas, targets, mappings, interpretation, or gates. Retry resources may rise only to 12 CPUs (60 GB) and six hours. Material changes require a revised package and fresh approval.
- Proposed monitoring: immediate job-identity validation, then one retained runtime-supported state-change monitor at 300-second cadence with unchanged output suppressed; reconcile every job through job-scoped `sacct`. Query/transport failure means unknown state, not completion or retry authority.
- Proposed cancellation: only recorded Iter006 job IDs, only on explicit user direction or a proven universal pre-execution defect covered by the eventual runtime contract, followed by terminal accounting.
- Expected evidence: source/config/submitted hashes and byte identity; immutable input, validation, and output manifests; fixture and observation receipts; table/figure counts; representative visual checks; reviewer identity/findings; job IDs, logs, accounting, and resources; compact JERC interpretation; and cross-record validation.
- Expected Git records after eligible results: `iterations/iter006.md`, `summaries/iter006/`, an `ITERATION_SUMMARY.md` append, one `registry.csv` row, rebuilt `handoff/CURRENT.md`, and Iter006 execution material. Large outputs remain outside Git.
- Stop at validated closeout with no active or unaccounted jobs, or earlier for exhausted authority, immutable rejection without an in-contract correction, or a fresh material decision outside the approved package.
- This approved planning-only proposal grants no Iter006 initialization, Python execution, implementation, directory creation, review launch, scheduler operation, retry, cancellation, output publication, or commit authority. Before any runtime action, present one consolidated kickoff package containing this plan unchanged, current bootstrap evidence, exact lifecycle and outside-sandbox authority, resources, monitoring, retry/cancellation terms, and the closeout-commit choice, then obtain fresh explicit approval.
