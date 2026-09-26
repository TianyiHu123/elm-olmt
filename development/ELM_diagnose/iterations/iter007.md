# iter007 - ABBY vertical-soil-carbon extended OAT diagnostic

## Status

- Iteration ID: `iter007`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter007_abby_ctrlvertc_oat_extended`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-15T14:08:59-07:00`
- Closed: `2026-09-15T19:19:52-07:00`
- Objective: Apply the complete Iter005/Iter006 extended OAT diagnostic to 13 ABBY vertical-soil-carbon one-parameter ensembles with explicit dynamic parameter mapping.
- Bounded scope: 13 exact ABBY vertical-soil-carbon pickles; 1,300 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.

## Finalized Plan

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

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approve the complete package and authorize the agent to execute outside the Codex sandbox`; `2026-09-15T14:08:59-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Complete Iter007 through initialization, preparation, independent review, one bounded compute-node preflight, one diagnostic, evaluation, four-record validation, and closeout. Two compute work units. Stop at validated closeout or earlier for exhausted authority/retries, immutable rejection without an authorized correction, or a new material decision. |
| Confirmed HPC system and site profile | Puma host `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; account `chopinsong`; partition `standard`; module `micromamba/2.0.2-2`; environment `OLMT_puma`. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended` with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`. Root was absent at kickoff and may be created. Retain attempts; no automatic deletion, overwrite, or backup. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | The finalized plan above is immutable: exact 13-pickle ABBY vertical-soil-carbon mapping, control NetCDF, ABBY SR observation, interfaces, formulas, shapes, targets, mappings, counts, exclusions, and pass rule. |
| Lifecycle authority | Primary agent may initialize records; generalize the exact-input parameter parser; create Iter007 fixtures, wrappers, configs, validators, and external run directories; launch and wait for independent read-only review; run static checks; submit, monitor, account, evaluate, publish, update records, cross-validate, and close. |
| Resources, monitoring and wait mechanism, and retry boundaries | Preflight: 1 node/task, 8 CPUs/40 GB, 2 hours. Diagnostic: 1 node/task, 12 CPUs/60 GB, 4 hours. At most two retries after each initial attempt; maximum 16 CPUs/80 GB and 6 hours. Scheduler/resource failures may retry. One minimal preflight-only correction restoring the locked contract may consume a retry. Diagnostic application/code/interface/schema/data/dependency/dimensionality/numerical failures require fresh approval. Immediate identity query, then retained 60-second `watch -g` state-change monitoring through the active exec handle; reconcile with job-scoped `sacct`. A recorded lost-handle failure may use one detached `tmux` state-change detector; if neither remains supported, checkpoint. |
| Cancellation scope | Only recorded Iter007 job IDs, only on explicit user direction or a proven universal pre-execution defect covered by this contract, followed by terminal accounting. |
| Outside-sandbox authority | Approved `sbatch` for locked work and in-contract resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` only under the stated conditions. |
| Closeout branch | One tightly scoped verified closeout commit is authorized; no push. |

## Declared Diagnostic Inputs and Bootstrap Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| 13 ABBY vertical-soil-carbon pickles | OAT inputs | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/pklfiles` | ELMcase pickle; content pending preflight | Approximately 3.140 GB each; approximately 39 GB total | Exact basenames and sizes refreshed at kickoff; content and shape require compute-node preflight |
| 13 ABBY configs | provenance cross-check | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/ABBY/config` | `use_vertsoilc=.true.`; hourly 2018--2024 | 13 files; identical postprocessing blocks | Full required-variable union plus out-of-scope extra variables |
| 13 parameter files | range/name cross-check | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrlvertc_sensi/params` | one parameter per file | 13 files | Confirms `decomp_depth_efolding` and absence of `grpnow`/`kmax` |
| control parameter NetCDF | native markers | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` | NetCDF | SHA-256 `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9` | Exists; header contains `decomp_depth_efolding`; revalidate in preflight |
| ABBY observation | contextual SR reference | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` | NEON v4 NetCDF | SHA-256 `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` | Exists; schema/time/unit support pending preflight |
| repository | implementation source | `/xdisk/chopinsong/tianyihu/elm-olmt` | branch `feature/ELM_diagnostics` | kickoff commit `ae143bd` | Clean at approval; execution pins commit plus exact source/config hashes |
| Puma resources | runtime dependency | Puma | `standard/chopinsong` | xdisk 17.5/19.5 TB; home 41.7/50 GB | Limits exceed contract; allocation expiration unavailable to non-PI |

## Acceptance Gates and Decision Rule

- Required completeness: exactly 13 declared parameters, 1,300 members, 61,320 hours per member, all locked interfaces, 3,268,682 table rows, and 44 ABBY-labelled PNGs.
- Acceptance gates: finalized-plan input, configuration, interface/parity, observation, calculation/shape, artifact, publication, independent-review, terminal-accounting, and record gates.
- Decision rule: accept only when every immutable gate passes; otherwise classify and stop or retry only within the approved boundary. No partial publication or scientific interpretation.
- Conditional comparative metrics: none; Iter005/006 outputs are provenance and fixture references only.
- Changes requiring fresh authorization: input membership, targets, formulas, vertical aggregation, extra-variable analysis, comparisons, interpretation, output root, maximum resources, retry budget, diagnostic code/data fixes outside the preflight-only correction, or broader cancellation.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight attempt 1 | `preflight_iter007.slurm` / `f37dc3d8` | submitted copy byte-identical; config `9215c441` | `.../preflight/attempt_1`; `slurm_23882414.out/.err` | tool `023cdcb1`; fixture `d4ecce40`; locked inputs/configs/parameter files and dependency hashes | kickoff `ae143bd`; dirty source pinned by hashes | `23882414` | `FAILED 1:0`; 11 seconds; 4,680 KB batch MaxRSS | monitor exec session `75320` detected queue exit; terminally reconciled; application failure before Python; retry correction authorized |
| preflight attempt 2 | `preflight_iter007.slurm` / `cd3d7fa3` | submitted copy byte-identical; config `cf554e52` | `.../preflight/attempt_2`; `slurm_23882462.out/.err` | tool `023cdcb1`; fixture `d4ecce40`; unchanged locked inputs/dependencies | kickoff `ae143bd`; dirty source pinned by hashes | `23882462` | `FAILED 1:0`; 9 seconds; 4,564 KB batch MaxRSS | monitor exec session `78991` detected queue exit; terminally reconciled; fresh approval required before another correction/retry |
| preflight attempt 3 | unchanged wrapper `cd3d7fa3` | submitted copy byte-identical; corrected config `c36b8938` | `.../preflight/attempt_3`; `slurm_23882524.out/.err` | tool `023cdcb1`; fixture `d4ecce40`; unchanged locked inputs/dependencies | kickoff `ae143bd`; dirty source pinned by hashes | `23882524` | `COMPLETED 0:0`; 4m34s; 41,941,832 KB batch MaxRSS | state-only monitor `26016` detected queue exit; terminally reconciled; preflight passed |
| diagnostic | `diagnostic_iter007.slurm` / `be5804d7` | submitted copy byte-identical; config `1eae8148` | `.../diagnostic/attempt_1`; `slurm_23882574.out/.err` | validator `650d3fe6`; tool `023cdcb1`; input manifest `bf459ada` | kickoff `ae143bd`; dirty source pinned by hashes | `23882574` | `COMPLETED 0:0`; 3m18s; 45,076,324 KB batch MaxRSS | state-only monitor `52537` detected queue exit; terminally reconciled; results atomically published |

Monitoring outcomes are `active`, `handoff`, `failed`, `unsupported`, or `finished`. Workload state is recorded separately.

## Independent Read-Only Review

- Reviewer: `/root/iter007_review`
- Reviewed source hash: initial tool `023cdcb1`, wrapper `eaa6def7`, config `b68f0574`, fixture `d4ecce40`, validator `21862aba`, diagnostic wrapper `be5804d7`; focused re-review wrapper `f37dc3d8`, config `9215c441`, and validator `650d3fe6`.
- Outcome: initial `block`; focused re-review `pass` at `2026-09-15T14:25:36-07:00`, with no outstanding concern blocking submission.
- Findings and primary-agent response: reviewer found that the compute-node preflight did not itself validate the 13 configs/parameter files, vertical-soil-C flags, identical postprocessing contract, mapping/exclusions, or locked control/observation hashes; the exact submission command was not recorded. The primary agent added explicit runtime provenance/hash checks, pinned config/parameter roots and identities, recorded the command below, hardened the artifact validator to require exact mappings/interfaces/hashes and parameter membership in every table, and rematerialized byte-identical preflight copies. Focused review accepted the exact inventories, `use_vertsoilc = .true.`, then-pinned postprocessing digest, config-to-parameter associations, exact parameter names, dependency hashes, exact submission command, and hardened table validator. Attempts one and two plus the later full traced reproduction exposed that the accepted digest was mistyped; attempt three corrected it to the independently reproduced SHA `97be0806c99b565c06e3e0ccecf8db865b9f78c3501b6f0c2771e8ac3087624b`.
- Attempt-two correction review: `pass` at `2026-09-15T14:34:16-07:00`. The reviewer reproduced the newline-sensitive `read` failure and newline-safe `awk` result; confirmed the wrapper diff is exactly the one-line token-reader change and the config diff only advances attempt paths; confirmed canonical/materialized SHA-256 `cd3d7fa36dd70275cf648fb35b2a5704b726c47c5942325c298675874df6ec84` and `cf554e52d41be54c20bcf33398268b255f5078028f1dd5c3f68475a68a2545f9`; and judged the change precisely within the authorized minimal preflight-only correction.
- Remaining-retry authorization: user response `retry authorized.` at `2026-09-15T14:41:42-07:00`, authorizing the exact checkpointed second minimal correction and attempt-three retry: correct only the pinned postprocessing SHA, retain the newline-safe reader, independently review/materialize the third attempt, and submit with unchanged 8-CPU/40-GB/2-hour resources. No other package term changes.
- Attempt-three correction review: `pass` at `2026-09-15T14:44:11-07:00`. The reviewer confirmed unchanged byte-identical wrapper SHA `cd3d7fa36dd70275cf648fb35b2a5704b726c47c5942325c298675874df6ec84`, byte-identical corrected config SHA `c36b8938a11a7f94e6853b28aeba85916f912a48e2c9392198da6bb1016e9835`, a config diff limited to attempt paths and the corrected digest, independent agreement of all 13 blocks, absent attempt-three artifacts, exact recorded command, and unchanged authorized resources/scope.
- Diagnostic launch review: `pass` at `2026-09-15T14:58:02-07:00`. The reviewer confirmed manifest `bf459ada` schema/status and exact ordered inputs/interfaces/hashes/case dimensions; receipt `167cd729` and passing logs; byte-identical wrapper `be5804d7` and config `1eae8148`; pinned tool/validator/commit/paths; absent output and staging; hidden-staging generation, hardened validation, and atomic publication; exact command; and unchanged 12-CPU/60-GB/4-hour scope. No launch blocker remains.
- Final result review: initial outcome `block` on a report-only pathway aggregation error; published artifacts passed. The primary extraction had added the eight pool rows and the already-summed `TOTAL` row, doubling all three pathway means. The correction uses exactly 1,300 `TOTAL` rows per pathway and leaves the published artifacts unchanged; the focused re-review passed as recorded below.
- Focused pathway re-review: `pass` at `2026-09-15T19:19:52-07:00`. Corrected accumulations, daily rates, model-SR-relative percentages, and the `75.68%` N-limitation reduction exactly reproduce the published table; no superseded values remain. The final independent results gate is clear.
- Final closeout-record review: initial outcome `block` on two stale report-only status phrases that contradicted the already recorded passing focused review and diagnostic gate. Both phrases were corrected without changing evidence, calculations, artifacts, or derivative records. Focused closeout re-review passed at `2026-09-15T19:26:55-07:00`; no live gate remains pending.

## Execution and Diagnostics

- Static validation: `bash -n`, canonical/submitted `cmp`, exact hash checks, dynamic-parameter string audit, plan identity, and `git diff --check` pass. For attempt three, all 13 postprocessing blocks independently compute the corrected pinned SHA and an absolute-path execution of wrapper lines 1--113 passes the complete pre-Python gate. Repository Python remains reserved for compute-node preflight. One earlier relative-path test from the external directory was invalid and explicitly discarded before this valid absolute-path rerun.
- Preflight: attempt-one job `23882414` submitted at `2026-09-15T14:26:10-07:00`; immediate identity check passed. It failed `1:0` after 11 seconds with empty logs and 4,680 KB batch MaxRSS, before environment activation or Python. The first diagnosis identified a real latent defect: every legacy parameter file lacks a terminating newline, so Bash `read` populates the token but returns status 1 under `set -e`. The authorized minimal preflight-only correction replaced that builtin with a newline-safe first-line `awk` token read. Attempt-two job `23882462` was submitted at `2026-09-15T14:34:43-07:00`; its immediate identity check passed, but it failed `1:0` after 9 seconds with empty logs and 4,564 KB batch MaxRSS. A complete traced reproduction of lines 1--113 then showed that both attempts actually stopped earlier at the postprocessing-hash check: the config pins mistyped SHA-256 `97be0806c99b565c06e3e0db865b9f78c3501b6f0c2771e8ac3087624b`, while all 13 live config blocks compute `97be0806c99b565c06e3e0ccecf8db865b9f78c3501b6f0c2771e8ac3087624b`. No Python, pickle deserialization, analysis, artifact creation, or diagnostic work ran.
- Exact submission commands: preflight attempt one, from `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/preflight/attempt_1`: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/preflight/attempt_1/submission_config.env ./submit_preflight_iter007.slurm </dev/null`. Attempt two, from the corresponding `attempt_2` directory, uses its matching config and wrapper. Attempt three, from the corresponding `attempt_3` directory: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/preflight/attempt_3/submission_config.env ./submit_preflight_iter007.slurm </dev/null`. Diagnostic attempt one, from `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/diagnostic/attempt_1`: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/diagnostic/attempt_1/submission_config.env ./submit_diagnostic_iter007.slurm </dev/null`.
- Job identity checks: preflight attempts `23882414` and `23882462` passed their immediate `squeue`/`scontrol` identity checks.
- Attempt-three identity check: job `23882524`, submitted `2026-09-15T14:44:35-07:00`, is `PENDING (Priority)` with expected account `chopinsong`, partition `standard`, 1 task/8 CPUs, 40 GB, 2-hour limit, command, paths, logs, and `/dev/null` stdin.
- Diagnostic identity check: job `23882574`, submitted `2026-09-15T14:58:45-07:00`, is `PENDING (Priority)` with expected account `chopinsong`, partition `standard`, 1 task/12 CPUs, 60 GB, 4-hour limit, command, paths, logs, and `/dev/null` stdin.
- Queue and terminal accounting: preflight `23882414` terminally reconciled as `FAILED 1:0`; batch `FAILED 1:0`, extern `COMPLETED 0:0`; elapsed 11 seconds, 8 CPUs, batch MaxRSS 4,680 KB on `r7u01n2`. Preflight `23882462` terminally reconciled as `FAILED 1:0`; batch `FAILED 1:0`, extern `COMPLETED 0:0`; elapsed 9 seconds, 8 CPUs, batch MaxRSS 4,564 KB on `r7u03n2`.
- Passing preflight accounting and evidence: job `23882524` is terminal `COMPLETED 0:0`; batch and extern both completed; elapsed 4m34s, total CPU 3m39.206s, 8 CPUs, batch MaxRSS 41,941,832 KB on `r7u13n1`. Fixture reported `ITER007_FIXTURE_PASS parameters=13 figures_per_site=44`; runtime reported `OAT_PREFLIGHT_PASS parameters=13 members=1300 hours=61320 observations=1`. Validation receipt schema `elm_oat_validation_receipt_v3` has status `pass`; input manifest SHA-256 is `bf459adab7ce1ed4400ba14a4b217381ecad812510c94164992d54bfe887fd49`; receipt SHA-256 is `167cd7294dadcbb9d5367cce064691696830a5c6d1b2603ade2a42a36b18f1c5`.
- Diagnostic accounting and publication evidence: job `23882574` is terminal `COMPLETED 0:0`; batch and extern both completed; elapsed 3m18s, total CPU 2m39.561s, 12 CPUs, batch MaxRSS 45,076,324 KB on `r4u03n2`. Logs report `OAT_DIAGNOSTIC_GENERATE_PASS parameters=13 member_rows=1300 score_rows=338 figures=44`, `ITER007_ARTIFACT_VALIDATE_PASS rows=3268682 figures=44`, and `ITER007_ATOMIC_PUBLICATION_PASS`. Output manifest schema/status are `elm_oat_output_manifest_v4`/`pass`; SHA-256 is `61a85ab5395a10865996faea1ad425229a594439e53d210941798b45688935ce` and it pins input manifest `bf459ada`.
- Resource diagnostics: `seff` confirms attempt one used 4.57 MB of 40 GB and 0.095 CPU-seconds over 11 seconds; attempt two used 4.46 MB and 0.092 CPU-seconds over 9 seconds. Passing preflight attempt three used 40.00/40.00 GB and 3m39.206s CPU over 4m34s. The diagnostic used 42.99/60.00 GB and 2m39.561s CPU over 3m18s.
- Failure, rejection, retry, or cancellation evidence: attempts one and two both stopped at the mistyped locked postprocessing hash. The attempt-two change corrected a separate latent newline-sensitive parameter-token reader but did not reach it. After the exact second correction and remaining retry were explicitly authorized, attempt three passed. The diagnostic passed on its initial attempt. No cancellation occurred.
- Continuity recovery: a platform usage-limit interruption occurred after diagnostic completion, terminal accounting, locked artifact validation, metric extraction, and representative visual inspection but before records reflected that state. On resumption at `2026-09-15T19:13:13-07:00`, job-scoped `sacct` reconfirmed diagnostic `23882574 COMPLETED 0:0`; no job or monitor remained active, and work resumed from the published result evidence without rerun.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | passing fixture, 13-pickle manifest, receipt, terminal accounting, and logs | pass | all locked input/configuration/interface/observation/calculation/shape preflight gates passed on attempt three |
| diagnostic | yes | terminal accounting, passing hardened validator, output manifest `61a85ab`, exact row/figure counts, atomic publication, visual inspection, and final independent review | pass | all artifact, publication, accounting, calculation, and final-review gates pass |

- Artifact completeness: 13 parameter rows, 1,300 member rows, 338 score rows, 37,180 standard response rows, one observation row, 35,100 HR-pathway rows, 390 HR-curve rows, 5,200 litter member-ratio rows, 3,188,640 litter time-series rows, 520 litter-curve rows, and 44 ABBY-labelled PNGs: exactly 3,268,682 data rows.
- Observation and model coverage: observed SR has 26,264 valid hours (`42.83%` of the 61,320-hour model window), mean `7.501337`, and population temporal SD `2.627639` gC m-2 day-1. Across the 1,300 model members, SR means span `0.830247`--`2.665878` with pooled mean `1.342808`, and temporal SDs span `0.169364`--`0.549677` gC m-2 day-1. The observation mean and SD are above the full member ranges; the observation is contextual and not exactly time-support matched.
- Mean pathway comparison: using exactly the 1,300 `TOTAL` rows per pathway and equal weighting across the 13 separate 100-member OAT ensembles, mean seven-year accumulations are potential `30,105.309996`, P-limited `9,797.224370`, and N-limited `7,321.027060` gC m-2. Dividing each member's accumulation by the full 2,555-day model window gives `11.782900`, `3.834530`, and `2.865373` gC m-2 day-1. Relative to the pooled model SR mean denominator (`1.342808`), they are `+777.48%`, `+185.56%`, and `+113.39%`; observed SR is `+458.63%`. N limitation reduces mean potential HR by `75.68%`; these constructed pathway diagnostics are not the model's actual `HR_TOTAL`, whose pooled member mean is `0.785350` gC m-2 day-1.
- Litter support: all 1,300 members support every ratio; no undefined ratios were coerced to zero. Flux-weighted medians are effectively fixed at leaf C:N `70`, leaf C:P `1050`, fine-root C:N `42`, and fine-root C:P `1000`; only machine-scale numerical scatter is present.
- Range-conditional ranking: `leaf_long` ranks first for mean GPP and ER response spreads (`68.44%` and `70.43%`), while `act25` ranks first for mean SR, HR_TOTAL, and LITFALL (`65.27%`, `74.55%`, and `74.46%`). `k_s4` leads mean total litter-plus-soil C and SOIL4C (`3482.13%` and `3659.67%`), with matched or nearby decomposition rates dominating most pool responses. `decomp_depth_efolding` ranks 13th for the five standard flux means (`0.30%`--`0.57%` spreads), 11th for total litter-plus-soil C (`11.74%`), and 8th--10th for the four soil pools (`8.66%`--`12.59%`) over its sampled `0.1`--`15.0` range. This describes only the declared separate OAT ensembles.
- Visual inspection: mean sensitivity, accumulated HR, SR-response, and hourly litter-ratio panels are complete, ABBY-labelled, and internally coherent. Non-blocking presentation limitations persist: heatmap annotations have weak contrast in low-valued cells, and Matplotlib offset notation visually magnifies machine-scale scatter around fixed litter ratios.
- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: Accepted validated standalone ABBY vertical-soil-carbon range-conditional descriptive OAT and pathway/stoichiometry package; no PAWN/Sobol/global sensitivity, interaction, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site claim.
- Limitations: observation support covers only `42.83%` of model hours and is not time-matched; constructed HR pathways differ from actual model HR; results are conditional on declared parameter ranges and separate OAT ensembles; `/xdisk` is temporary and unbacked; allocation expiration is PI-only.
- Next state: workflow intentionally stopped after Iter007 closeout; no next iteration is proposed automatically.

### Final closeout validator

- Identity: inline bounded shell validator using `set -eu`, fixed-string cross-record checks, CSV-aware registry parsing, registry-row uniqueness, output-manifest artifact hash/size verification, manifest-derived row/figure counts, `bash -n`, submitted-copy equality, superseded-value exclusion, and `git diff --check`; final execution from the repository root at `2026-09-15T19:26:55-07:00`.
- Command scope: `iterations/iter007.md`, `summaries/iter007/ITER007_RESULT.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, Iter007 canonical/submitted execution material, and the published external result directory.
- Validator correction: the first invocation stopped only because the validator asserted 13 registry columns; the fixed schema has 14. The corrected invocation changed that assertion only and completed all checks. Independent closeout review then found two stale status phrases; after their record-only correction and passing focused re-review, the complete validator was rerun and refreshed the result below.
- Result: `ITER007_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=44 data_rows=3268682 terminal_jobs=4 next_state=intentionally_stopped`.

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

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter007/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit
