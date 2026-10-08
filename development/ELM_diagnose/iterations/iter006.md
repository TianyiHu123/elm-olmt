# iter006 - JERC extended OAT pathway and stoichiometry diagnostic

## Status

- Iteration ID: `iter006`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter006_jerc_oat_extended`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-10T19:39:47-07:00`
- Closed: `2026-09-11T16:03:29-07:00`
- Objective: Apply the complete Iter005 ABBY extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles with explicit site-generalized tooling.
- Bounded scope: 14 exact JERC pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.

## Finalized Plan


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

### Approved closeout-table addition

- The compact Iter006 result must include the same `Mean HR and SR flux comparison` table structure as Iter005, with potential HR, P-limited HR, N-limited HR, model SR, and observed SR rows.
- Required columns are flux, timesteps used, mean flux in `gC m-2 day-1`, and percentage difference from model SR.
- Potential and limited HR means divide each member's accumulated total by the 2,555-day model window and then average equally across all 1,400 members. Model SR is the direct mean across 61,320 model hours and all members. Observed SR uses only finite valid JERC observation hours without filling missing hours.
- Percentage difference is `100 * (mean flux / model SR mean - 1)`. Also report N-limitation reduction relative to potential HR and state observation coverage/time-support limitations.
- This table is descriptive, adds no acceptance threshold or cross-site comparison, uses existing diagnostic outputs during evaluation, and adds no scheduler work unit.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User first responded `Entire kickoff package approved, outside sandbox execution authorized` and added the Iter005-style summary-table requirement; the complete revised package was approved by `yes, approved.` at `2026-09-10T19:39:47-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Initialize, implement, execute, evaluate, and close exactly two work units: one bounded compute-node preflight and one JERC diagnostic. Stop at validated closeout with no active or unaccounted job, or earlier only for exhausted authority, immutable rejection without an authorized correction, a required material decision, or exhaustion of supported monitoring/wake strategies. |
| Confirmed HPC system and site profile | Puma login node `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; account `chopinsong`; partition `standard`; `OLMT_puma` must be revalidated on the compute-node preflight. |
| Approved output and storage policy | Root `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter006_jerc_oat_extended`; only `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`; directory creation and retention authorized; no automatic deletion, replacement, or backup; `/xdisk` is temporary and unbacked. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | The finalized plan and closeout-table addition above are immutable. Exact 14 JERC pickles under renamed `pklfiles`, control NetCDF, JERC SR observation, interfaces, formulas, targets, mappings, output counts, exclusions, and pass rule are locked. |
| Lifecycle authority | Iteration initialization, preparation, tracked implementation/documentation, external-directory creation, submitted copies, independent read-only review, compute-node preflight and diagnostic, submission, agent-owned monitoring, accounting, authorized retry, evaluation, records, validation, closeout, and one scoped commit. |
| Resources, monitoring and wait mechanism, and retry boundaries | Initial preflight: 1 node/task, 8 CPUs/40 GB, 2 hours. Initial diagnostic: 1 node/task, 8 CPUs/40 GB, 4 hours. At most two retries after each initial attempt for classified scheduler/resource failure, maximum 12 CPUs/60 GB and 6 hours. One minimal preflight-only correction and rerun may restore the locked contract and consumes the preflight attempt budget; diagnostic application/code/interface/schema/data/dependency/numerical failures require fresh approval. Use one retained Puma state-change detector at 300-second cadence, suppress unchanged output, retain its handle, and reconcile terminal state with job-scoped `sacct`. |
| Cancellation scope | Initially none; after submission, only recorded Iter006 job IDs, only on explicit user direction or a proven universal pre-execution defect covered by this contract, followed by terminal reconciliation. |
| Outside-sandbox authority | Locked `sbatch` submissions and authorized scheduler/resource resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only within the recorded cancellation scope. |
| Closeout branch | One tightly scoped Iter006 closeout commit authorized; generated outputs remain outside Git; no push. |

## Declared Diagnostic Inputs and Bootstrap Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| 14 JERC OAT pickles | Model ensembles | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/JERC/pklfiles` | Expected ELMcase pickles; content pending preflight | each about 2.208 GB; hashes pending | Exact approved basenames present; old `pkfiles` absent |
| Control parameter NetCDF | Native markers | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` | NetCDF | 89,832 bytes; SHA-256 `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9` | Same dependency accepted by Iter004/Iter005 |
| JERC SR observation | Contextual reference | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc` | NEON v4 NetCDF | 864,814 bytes; SHA-256 `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` | Exists; schema/time/unit pending preflight |
| Repository | Source identity | `/xdisk/chopinsong/tianyihu/elm-olmt` | branch `feature/ELM_diagnostics` | kickoff HEAD `3bd5611`; clean at bootstrap | Approved planning commit |
| Puma capacity | Runtime envelope | account `chopinsong` | bootstrap snapshot | 104/3290 CPUs; 520/16998 GB; xdisk 17.4/19.5 TB; home 41.4/50 GB | Sufficient for initial 8 CPUs/40 GB; xdisk expiration PI-only |

## Approved Material Revision After Attempt Two

- Approval: after the attempt-two `leaf_cn` rejection was checkpointed, the user responded `approved the revision and I'll give you 2 more budgets for retry for both preflight and diagnostic run.` at `2026-09-10T20:24:18-07:00`.
- Revised calculation gate: for each flux-weighted litter ratio, retain every declared member. A member with finite accumulated carbon, finite accumulated nutrient, and a positive accumulated nutrient denominator remains supported and uses accumulated elemental mass before division. Otherwise its ratio is an explicit blank gap with `supported=False` and one recorded reason: `nonfinite_carbon_total`, `nonfinite_nutrient_total`, `nonfinite_carbon_and_nutrient_totals`, or `nonpositive_nutrient_total`.
- Revised curve and plot gate: form the same ten parameter bins from all 100 declared members, report declared, valid, and rejected counts per bin, compute a median only from supported members, leave the median blank when a bin has no support, and omit invalid points from plotting. Preserve exactly 5,600 member rows, 560 curve rows, all other row counts, and 44 figures.
- Revised manifest/schema gate: record this support contract in the input manifest, record per-case/per-ratio support counts, and validate member support/reason consistency and curve support counts. Use input/output manifest schema v4 and validation-receipt schema v3 so the revised contract cannot be confused with attempts one or two.
- Revised retry authority: from this approval, at most two additional preflight attempts are authorized. The diagnostic retains one initial attempt and at most two retries. Each retry remains bounded by the existing same-scope resource maxima and monitoring, accounting, cancellation, output, and outside-sandbox terms; no other input, formula, interpretation, or artifact-count change is authorized.
- Closeout-table requirement and one scoped closeout commit authority are unchanged.

## Acceptance Gates and Decision Rule

- Required completeness: exact locked inputs, two work units, 44 JERC-labelled figures, 3,520,119 data rows, the required closeout comparison table, complete manifests, representative visual checks, terminal accounting, and consistent durable records.
- Acceptance gates: all finalized-plan input, site/parity, observation, calculation, artifact, publication, independent-review, scheduler-accounting, and record gates.
- Decision rule: accept only a validated JERC range-conditional descriptive OAT/pathway/stoichiometry package when every gate passes; otherwise classify and stop or retry only within the approved contract.
- Conditional comparative metrics, aggregation, ranking, or tie-breaker: none; the mean-HR/SR table is descriptive and model-SR-referenced only.
- Changes requiring fresh authorization: inputs, formulas, targets, mappings, scientific interpretation, site comparison, gates, output root, resource maxima, retry budget, diagnostic application/code fixes, or cancellation beyond recorded Iter006 jobs.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight attempt 1 | wrapper `c1322c83`; tool `3281aea9`; fixture `080d6329`; config `5ca1d5ae` | byte-identical submitted wrapper/config | `.../preflight/attempt_1`; empty `slurm_23856493.out/err` | locked JERC inputs; `OLMT_puma` | kickoff HEAD `3bd5611`; hash-pinned dirty source | `23856493` | `FAILED 1:0`; 00:00:10; 00:00.034 CPU; 2.77 MB/40 GB | identity matched; detector outcome `handoff` after a non-fatal setup typo and successful empty-queue query; `sacct` reconciled; classified abbreviated/full commit-SHA preamble mismatch; minimal correction used; two retry attempts remained before attempt two |
| preflight attempt 2 | wrapper `c1322c83`; tool `3281aea9`; fixture `080d6329`; config `c3951c20` | byte-identical submitted wrapper/config | `.../preflight/attempt_2`; `slurm_23856561.out/err` | locked JERC inputs; `OLMT_puma` | full kickoff HEAD `3bd5611be007cbb4544083861fe15ba065a3f6c4`; hash-pinned dirty source | `23856561` | `FAILED 1:0`; 00:03:25; 02:37.880 CPU; 30.79 GB/40 GB | identity matched; detector session `12372` observed `PENDING` then `RUNNING` and reached queue-to-accounting handoff; retired after `sacct` reconciliation; scientific calculation gate rejected `leaf_long`; superseded only by the approved explicit-gap revision |
| preflight attempt 3 | wrapper `c1322c83`; tool `1795351e`; fixture `080d6329`; validator `a56c538e`; config `f79b33f8` | byte-identical submitted wrapper/config | `.../preflight/attempt_3`; `slurm_23856771.out/err` | locked JERC inputs; `OLMT_puma` | full kickoff HEAD `3bd5611be007cbb4544083861fe15ba065a3f6c4`; revised hash-pinned dirty source | `23856771` | `COMPLETED 0:0`; 00:02:49; 02:27.804 CPU; 5.85 GB/40 GB | identity matched; platform usage interruption occurred before the planned detector started; resumed job-scoped `squeue` handed off to complete `sacct`; no active handle; one additional preflight attempt remains unused |
| diagnostic attempt 1 | wrapper `e992ece9`; tool `1795351e`; validator `a56c538e`; config `03ec8f14` | byte-identical submitted wrapper/config | `.../diagnostic/attempt_1`; `slurm_23861155.out/err` | passing preflight manifest `b10901c1` | kickoff HEAD `3bd5611`; hash-pinned dirty source | `23861155` | `COMPLETED 0:0`; 00:03:33; 02:53.476 CPU; 32.87 GB/40 GB | identity matched; detector session `65404` observed PENDING/RUNNING then returned expected completed-job query failure and handed off; `sacct` reconciled; two retries unused |

## Independent Read-Only Review

- Reviewer: independent read-only `/root/iter006_review`.
- Reviewed source hash: initial tool `12b9608f`, fixture `3f8a3446`, and review-set aggregate `64aa6d31`.
- Outcome: focused re-review `pass`; review-set aggregate `22a9c3ba`.
- Findings and primary-agent response: the initial paired-site fixture only relabelled a helper result and literal filenames, so it did not exercise the immutable parity contract. The correction drives paired synthetic ABBY/JERC cases through embedded-site validation, all standard and specialized numerical row builders, manifest construction, and all 44 presentation outputs per site; it requires exact numeric equality, site-only manifest difference, equal figure membership after removing the site prefix, and restoration of the bounded fixture time-size override. Focused re-review passed tool `3281aea9`, fixture `080d6329`, wrapper `c1322c83`, and byte-identical config `5ca1d5ae` with no concerns.
- Attempt-two focused review: `pass_with_concerns`; it verified exact failure reproduction, immutable attempt-one archive `5ca1d5ae`, attempt-two config `c3951c20`, byte identity, and unchanged execution/scientific scope. Its sole record-only concern was a stale sentence naming attempt one; that sentence is corrected to attempt two before resubmission, with no execution-material re-review required.
- Material-revision first review: `block`. It found that flux-weighted plotting still used the NaN-sensitive general bin helper, the artifact validator did not constrain support tokens/reasons or reconcile member/curve/manifest counts, the paired fixture did not exercise gaps through row and plot creation, diagnostic hashes were stale, and the attempt-three ledger was stale. The primary agent corrected each item; passing focused re-review is required before submission.
- Material-revision focused re-review: `pass_with_concerns`; no execution-material defect remains. Reviewer verified the explicit-gap plotting, all four rejection classes through 5,600 member and 560 curve fixture rows plus all 44 plots/site, exact validator reconciliation, current diagnostic template, and byte-identical attempt-three copies. Its two record-only concerns (stale diagnostic-template and next-action wording) were corrected before submission without another review.
- Diagnostic launch review: `pass_with_concerns`; no launch-material blocker. Reviewer verified passing preflight `23856771`, manifest `b10901c1`, exact support counts, wrapper/tool/validator/config hashes and byte equality, resources, absent output/staging, atomic validation/publication, and approved authority. Its record-only phase and next-action concerns were corrected during this transition without re-review.

## Execution and Diagnostics

- Static validation: `bash -n`, canonical/submitted `cmp`, explicit-site/mapping/static string checks, pinned source hashes, and `git diff --check` pass; all repository Python ran only on the compute-node preflight.
- Preflight: attempt one `23856493` failed `1:0` after ten seconds with empty stdout/stderr, before logged Python execution. Attempt two `23856561` passed the full paired-site fixture, observation validation, and the first 12 parameter pickles, then failed the locked litter-ratio calculation gate while loading `leaf_long`.
- Exact submission commands: preflight attempts one and two used `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=<attempt_N>/submission_config.env ./submit_preflight_iter006.slurm </dev/null` from their locked run directories and returned `23856493` and `23856561`.
- Job identity checks: `23856493` and `23856561` each matched job name `elm-diag-i006-preflight`, standard/chopinsong, 8 CPUs/40 GB, 2-hour limit, locked command, attempt-specific work directory, and log paths.
- Queue and terminal accounting: job-scoped `sacct` reconciles both parents as `FAILED 1:0`; attempt one elapsed 00:00:10 and attempt two elapsed 00:03:25. Attempt-two batch MaxRSS was 32,290,784 KB (30.79 GB), with 02:37.880 TotalCPU on eight CPUs. `seff` reports 9.63% CPU efficiency and 76.99% memory efficiency. Neither failure is an unaccounted scheduler state.
- Resource diagnostics: attempt-one 2.77 MB/40 GB MaxRSS and 00:00.034 CPU established a pre-execution failure. Attempt-two completed substantial validation within 30.79 GB/40 GB and failed on an explicit value check, not resource capacity.
- Failure, rejection, retry, or cancellation evidence: attempt one failed because config `5ca1d5ae` pinned abbreviated commit `3bd5611` while the wrapper compared the full SHA; the authorized correction produced config `c3951c20`. Attempt two produced receipt `validation_receipt.json` SHA-256 `ba4ff6a06119f3ef5f7f953360fe74aef05b16a4d0992f288820cd45953fb837` with schema v2, status `fail`, and exact error `ValueError: leaf_cn: every member requires finite totals and a positive accumulated denominator`. Stdout SHA-256 is `8c8029fb61f8be00a5224bff269ebe7c9dcb787a531fef957a43146ddf61ff8b`; stderr SHA-256 is `ed4ebd4a957149136e8bd0b6fc760a4c7bbdd79339b9a7a11dfce96989fbeb46`. The fixture passed, the JERC observation supplied 51,882 valid timesteps, and pickles through `kmax` passed before `leaf_long` was rejected; `q10_mr` was not reached. Detector session `12372` reached expected queue-to-accounting handoff and is retired. No cancellation occurred.
- Passing revised preflight evidence: attempt three receipt SHA-256 `a479421cc84565804857ab692622f387d37a90ee9e39b65678129722ba6e7a01` has schema v3/status pass; input manifest SHA-256 `b10901c14c8d5689f1a704038860f51d79d9fa3ca663bfdef510555c9f5941f0` has schema v4/status pass, tool `1795351e`, all 14 pickles, 1,400 members, 61,320 hours, and 51,882 valid JERC SR observations. `leaf_long` retains 95 supported and five rejected members per ratio; `q10_mr` retains 68 supported and 32 rejected per ratio; all other cases retain 100. Stdout/stderr SHA-256 are `f6ce5c7705c15a0ae17ba84702a169a06344ae37b983495dd6f2cde8f5f172a0` and the empty-file hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Diagnostic execution and publication: job `23861155` passed generation, artifact validation, and atomic publication. Output manifest SHA-256 is `256cc1e1318aaa3e2a2ceaa123fdb06f2fd9e7ff224f4950caea659e4571ec31`; stdout/stderr SHA-256 are `5d89e4c4338cface9e9db26ae0800a9d85994d696348db246769582fde93697a` and `700b522dbc98e02f0e58823af43281e6983e5e375bf40c59622be340a005922e`. The only stderr content is an ArviZ future warning. Hidden staging is absent after publication.
- Diagnostic accounting: `sacct` records parent/batch/extern `COMPLETED 0:0`, 00:03:33 elapsed, 02:53.476 TotalCPU, eight CPUs, and batch MaxRSS 34,464,692 KB. `seff` reports 10.18% CPU efficiency and 32.87/40 GB (82.17%) memory efficiency. Detector `65404` is retired with outcome `handoff`; terminal accounting, not the detector, establishes completion.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | attempt-three manifest `b10901c1`; receipt `a479421c`; logs `f6ce5c77`/`e3b0c442`; terminal `sacct` for `23856493`, `23856561`, `23856771` | pass under approved revision | all 14 inputs pass; unsupported `leaf_long` and `q10_mr` ratios are retained with explicit support counts and no member dropping |
| diagnostic | yes | output manifest `256cc1e1`; logs `5d89e4c`/`700b522d`; terminal `sacct` `23861155`; independent result review | pass | exact 3,520,119 data rows, 44 JERC PNGs, 54 verified artifact hashes, support reconciliation, and atomic publication pass |

- Overall acceptance result: `pass`.
- Work-unit results: revised preflight `pass` on attempt three; diagnostic `pass` on attempt one; publication, review, terminal-accounting, artifact, support, and record gates pass.
- Completeness and provenance: the published package contains exactly 14 parameter rows, 1,400 member rows, 364 sensitivity-score rows, 40,040 response-curve rows, one observation row, 37,800 HR-pathway rows, 420 HR-curve rows, 5,600 litter member-ratio rows, 3,433,920 litter time-series rows, 560 litter-curve rows, and 44 PNGs. The output manifest is `256cc1e1` and links input manifest `b10901c1`.
- Observation context: 51,882 valid observed SR hours give mean `1.326166` and population temporal SD `0.851455` gC m-2 day-1. Across 1,400 model members, SR means span `0.000000`--`5.624627` and temporal SDs span `0.000000`--`1.540170`, so both observed summaries are bracketed. Observation coverage is `84.61%` and does not enter OAT scores.
- Pathway result: pooled mean potential and P-limited HR are identical at `3.961651` gC m-2 day-1; N-limited HR is `3.560783`, a `10.12%` reduction from potential. Model SR is `2.930035`; relative differences from it are `+35.21%`, `+35.21%`, and `+21.53%`. Observed SR is `-54.74%` relative to model SR.
- Stoichiometry result: every ratio retains 1,363 supported and 37 rejected member rows; all 148 rejections are `nonpositive_nutrient_total`. Supported leaf C:N/C:P and fine-root C:N/C:P are effectively fixed at `70`/`1050` and `42`/`1000`.
- Standard OAT result: `q10_mr` leads mean and temporal-standard-deviation response spread for GPP, ER, and SR and most aggregate flux targets. Matched decomposition rates lead corresponding mean litter/soil pools; `k_s4` leads mean total litter-plus-soil C. These are range-conditional screening results only.
- Zero-productivity hypothesis: the response cutoffs for `leaf_long` and `q10_mr` are produced by retained zero-valued members, not by member removal. All five zero-response `leaf_long` samples lie at `1.039381`--`1.165701` within the declared `1.0`--`5.0` range; the smallest sampled nonzero case is `1.300837`. All 32 zero-response `q10_mr` samples lie at `2.172782`--`2.993918` within the declared `1.0`--`3.0` range; the largest sampled nonzero case is `2.143543`. For all 37 members, both the temporal mean and population standard deviation are exactly zero for `GPP`, `ER`, `SR`, `HR_TOTAL`, `LITFALL`, `LITTER_SOIL_C_TOTAL`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`, `SOIL3C`, and `SOIL4C`; accumulated total potential, N-limited, and P-limited HR are also zero. Their four accumulated litter nutrient denominators are nonpositive, map to explicit ratio gaps, and are consistent with absent litter nutrient flux.
- Interpretation of the zero regime: sufficiently low sampled `leaf_long` or high sampled `q10_mr` is associated with an abrupt zero-productivity and zero-respiration state, consistent with possible vegetation collapse or loss of active vegetation. This remains a hypothesis rather than confirmed die-off because vegetation loss alone need not make soil and heterotrophic respiration exactly zero; a broader model-state collapse, inactive land column/PFT, failed upstream simulation, or postprocessing fill behavior could produce the same signature. Confirmation requires vegetation-state variables and original simulation-status evidence. The sampled gaps `1.165701`--`1.300837` for `leaf_long` and `2.143543`--`2.172782` for `q10_mr` prevent claiming an exact threshold.
- Representative visual checks: the mean heatmap, SR mean atlas, HR-pathway atlas, and leaf C:N flux-weighted atlas are complete and correctly JERC-labelled, with coherent response and gap behavior. Heatmap label contrast is weak in some cells, and offset notation magnifies machine-scale noise in near-constant litter-ratio panels; neither changes numerical evidence.
- Independent result review: `/root/iter006_review`, outcome `pass_with_concerns`; it independently matched all 54 artifact hashes, counts, support totals, HR/SR calculations, percentages, and representative visuals. All record concerns are resolved; the two visual-quality concerns are retained as limitations.
- Overall decision and closeout conclusion: Accepted validated JERC range-conditional descriptive OAT and pathway/stoichiometry package under the approved explicit-gap support contract; no global sensitivity, interaction, causal, optimization, tuning, parameter-value, or cross-site claim.
- Limitations: conclusions are conditional on declared parameter ranges and separate OAT ensembles. Observation support is incomplete and not exactly time-matched. Undefined ratios are gaps, not zeros. Near-constant ratio plot offsets and heatmap contrast can mislead visually if read without the tables. `/xdisk` is temporary and unbacked; allocation expiration remains PI-only.
- Next state: workflow intentionally stopped after Iter006 closeout; no next iteration is proposed automatically.

### Final closeout validator

- Identity: inline bounded shell validator using `set -eu`, fixed-string cross-record checks, registry-row uniqueness, manifest-derived artifact counts, output-manifest identity, `bash -n`, submitted-copy equality, and `git diff --check`; executed from the repository root at `2026-09-11T16:03:29-07:00`.
- Command scope: `iterations/iter006.md`, `summaries/iter006/ITER006_RESULT.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`, Iter006 canonical/submitted execution material, and the published external result directory.
- Result: `ITER006_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=44 data_rows=3520119 terminal_jobs=4 next_state=intentionally_stopped`.

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

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter006/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit
