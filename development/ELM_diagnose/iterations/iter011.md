# iter011 - ABBY transient and spinup-state OAT sensitivity

## Status

- Iteration ID: `iter011`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter011_abby_ctrlvertc_oat_spinup`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-04T22:22:23-07:00`
- Closed: `2026-10-05T03:39:07-07:00`

## Finalized Plan

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

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response `approve this complete kickoff package and authorize the primary agent to execute outside the Codex sandbox`; `2026-10-04T22:22:23-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Complete Iter011 through initialization, preparation, independent review, one bounded compute-node preflight, one diagnostic, evaluation, cross-record validation, and closeout. Two compute work units. Stop at validated closeout or earlier for exhausted retries/authority, immutable rejection without an authorized correction, input identity mismatch, unavailable authoritative monitoring, a fresh material decision, or explicit user stop. |
| Confirmed HPC system and site profile | Puma host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; account `chopinsong`; partition `standard`; validate `micromamba/2.0.2-2` and `OLMT_puma` on the compute node. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup` with `preflight/attempt_N`, `diagnostic/attempt_N`, hidden staging, and atomic `results/`; root was absent at kickoff and may be created; retain attempts; never overwrite, delete, or automatically back up; `/xdisk` is temporary and unbacked. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | The finalized plan above is immutable: exact 21 pickle/config/parameter/restart mappings and 2,100 members; direct transient means; exact lowercase vertical restart pools; contextual observed SR; potential/N/P-limited pathways; 80,200 rows; 11 figures; descriptive OAT boundary; all declared gates and exclusions. |
| Lifecycle authority | Primary agent may initialize, implement, create approved paths, launch and wait for read-only review, submit, monitor, account, evaluate, update records, validate, and close out within this contract. |
| Resources, monitoring and wait mechanism, and retry boundaries | Each unit uses one node/task and 16 CPUs with standard-derived 80 GB; preflight two hours, diagnostic four hours, retries at most six hours. Immediate identity check; retained 60-second state-change monitor with unchanged-output suppression; wait on the same handle; job-scoped terminal `sacct`; one materially different recorded fallback only if the first monitor is lost/unsupported. One initial attempt plus at most three retries per unit; at most one minimal preflight-only correction; other automatic retries scheduler/resource-only; no diagnostic application/code/data/schema/numerical retry without fresh authority. |
| Cancellation scope | Recorded Iter011 job IDs only for identity mismatch, proven universal pre-execution defect, out-of-root writes, resource-contract overrun, or explicit user instruction; terminal accounting required. |
| Outside-sandbox authority | Approved locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits` throughout monitoring/accounting; bounded `scancel` under the stated conditions. |
| Closeout branch | Exactly one scoped closeout commit; no push. |

## Declared Diagnostic Inputs and Evidence

- Repository state at kickoff: clean `feature/ELM_diagnostics` commit `3399850d83ff504d1b8f12a4ed9364bf7b471ecf`; local planning commit intentionally unpushed.
- Read-only inventory: 21 pickles, 21 configs, 21 parameter files, 21 restart cases, and 2,100 restart files; output root absent.
- Dependency hashes: environment `02283ec147688734ecbb3aa3a562e85f5c060c8810ca5ea66c8a81fd092878bb`; initial engine `023cdcb173554d3775072405c876fea9ffbffd1742b32db7f1d158b64153062e`; control parameters `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9`; ABBY observation `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`.
- Capacity at kickoff: `/xdisk/chopinsong` 17.5 TB used of 19.5 TB; home 42.2 GB of 50 GB; group 473.5 GB of 500 GB. No installation or environment repair is authorized.
- Iter010 terminal accounting revalidated: jobs `24025653` and `24025871` are `COMPLETED 0:0`.

## Acceptance Gates and Decision Rule

- Required completeness: exactly 21 parameters, 2,100 transient members, 2,100 paired restart members, five transient endpoints, three spinup endpoints, three pathways, 80,200 primary table rows, 11 figures, complete manifests, reviews, terminal accounting, and consistent records.
- Acceptance gates and decision rule are the immutable input/provenance, calculation, artifact/visual, publication/review/accounting/record gates in the finalized plan; scientific direction never controls technical acceptance.
- Any input, calculation, artifact, interpretation, resource-cap, retry, cancellation, or closeout change beyond the contract requires fresh authorization.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight preparation 1 | `preflight_iter011.slurm` `49f204ac4fc1f00407ff1aab404684f3eabe648510f07fb2dd29611436132987` | byte-identical `submit_preflight_iter011.slurm`; config `50dcff7ce375593e5f250c3f8d88466f175313b84c5f58b7ec498099a0838868` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/preflight/attempt_1` | args `48a1848df4a637a93c8539e6e4658cb5616b920b579a63b55eb9b9d55b57bd5a`; provenance list `a0056207280a769fcd7337e5edfeb319d1d80fb8d7af7c92e2fbdba4360d305a` | kickoff commit `3399850`; engine `e36983d5c7cd69af937c4070465a78866d2878846857e8c3137a4fe3983ee8a0`; fixture `6def39155bf609c4d788ef5086cdda1f92f283048b2ebd581e5e77e4743d3c56`; validator `f0c715823143907c368ca6e65352288c26e44cff1fa01e152d720a438171df10` | none | superseded before submission | read-only review blocked; never submitted and does not consume a runtime attempt |
| preflight preparation 2 | `preflight_iter011.slurm` `49f204ac4fc1f00407ff1aab404684f3eabe648510f07fb2dd29611436132987` | byte-identical `submit_preflight_iter011.slurm`; config `fa0aaf7d3e6183be5f64045c74c2b5fd9377de2d83f5a2ade4be61dfb8efe502` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/preflight/attempt_2` | args `c6c859adefc41969c743c3d180901c089fa6949c1588dd1b527d525d1fb28fd9`; provenance list `a0056207280a769fcd7337e5edfeb319d1d80fb8d7af7c92e2fbdba4360d305a` | kickoff commit `3399850`; engine `96e59c3de95e244c2abe02ecf3c36ac365ae6026a1cf8df9e35e777d4c37d611`; fixture `6def39155bf609c4d788ef5086cdda1f92f283048b2ebd581e5e77e4743d3c56`; validator `df0097e49388895bcc20750d96b238c22db5bbf4d4e1c80ba04568fc266c9db1`; docs `c416a99a9738afb098e7b9cfd6bcdacbe0cbe0f640912f7ab4c61f72acbd5136` | none | superseded before re-review | preserved and never submitted; final static observation-coverage assertion added in preparation 3 |
| preflight initial | `preflight_iter011.slurm` `49f204ac4fc1f00407ff1aab404684f3eabe648510f07fb2dd29611436132987` | byte-identical `submit_preflight_iter011.slurm`; config `bca278cb28745974620c30e9ddbfb0150fc20c9138bfe2a2d762ac7395e4e926` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/preflight/attempt_3`; logs `slurm_24101686.{out,err}` | args `c6c859ad...`; provenance list `a0056207...` | engine `96e59c3d...`; fixture `6def3915...`; validator `3d37a599...` | parent job `24101686` | `FAILED 1:0` | terminal `sacct`: 16 s, total CPU 0.987 s, batch MaxRSS 201552K; monitor finished; all 42 checksums passed, then fixture import failed with `ModuleNotFoundError: development`; classified preflight-only launch defect |
| preflight correction rerun | `preflight_iter011.slurm` `49f204ac4fc1f00407ff1aab404684f3eabe648510f07fb2dd29611436132987` | byte-identical script; config `545fa60909abdc8eac674a0f199caff80260c59441ba28d5c82adfd530409dca` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/preflight/attempt_4`; logs `slurm_24102996.{out,err}` | args `c6c859ad...`; provenance list `a0056207...` | engine `96e59c3d...`; fixture `3dcab08f...`; validator `3d37a599...` | parent job `24102996` | `COMPLETED 0:0` | identity pass; retained monitor exec session `3393` outcome `finished`; terminal `sacct` 3:28 elapsed, 02:17.330 TotalCPU, batch MaxRSS 80962140K on `r7u06n1`; passing manifest `7f528763...`, receipt `cb008b68...` |
| diagnostic | `diagnostic_iter011.slurm` `54b114889b289092b280f277d0ae516d1a2c980500bf0b1fb244a1b25aa46df8` | byte-identical `submit_diagnostic_iter011.slurm`; config `8ec86dcbddd45399fd6554ce4ff0532cc493fe79ae40df38f46e3f6857fa219a` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/diagnostic/attempt_1`; logs `slurm_24103048.{out,err}` | arguments `c6c859ad...`; passing input manifest `7f528763...` | engine `96e59c3d...`; validator `3d37a599...`; commit `3399850` | parent job `24103048` | `FAILED 1:0` | monitor session `14942` outcome `finished`; terminal 4:00, 03:03.260 TotalCPU, batch MaxRSS 80954692K, node `r7u03n2`; engine generated 80,200 rows/11 figures and output manifest `0e13dfa6...`, then validator rejected supported score rows because their intentionally blank `rejection_reason` failed an overbroad nonempty-column assertion |
| validator-only correction | `validate_only_iter011.slurm` `c06d8593abb9b2ecea3430cf63d1ff8192ba526a7d70649f97bb875cf87b0842` | byte-identical `submit_validator_only_iter011.slurm`; config `5baf0fbd6228c69bb20a91b5d2b5422d8e3ebd2aedb62fd2d1b6dbdb176e528b` | diagnostic `attempt_1`; logs `slurm_validator_only_24103109.{out,err}` | passing input manifest `7f528763...`; published output manifest `0e13dfa6...` | corrected validator `708d6e82...`; commit `3399850` | parent job `24103109` | `COMPLETED 0:0` | terminal during immediate identity check; no retained monitor needed; 12 s elapsed, 1.934 s TotalCPU, batch MaxRSS 146992K, node `r7u01n2`; artifact validator passed 80,200 rows/11 figures/63 restart samples and atomically published final `results/` |

## Independent Read-Only Review

- Reviewer: `/root/iter011_review` (separate read-only agent).
- First reviewed hashes: engine `e36983d5...`; fixture `6def3915...`; validator `f0c71582...`; arguments `48a1848d...`; preflight script `49f204ac...`; config `50dcff7c...`.
- First outcome: `block` before submission.
- Findings and primary-agent response: the first package shell-verified but did not manifest the 21 config/parameter sources, did not bind and range-check their mappings, omitted required definitions/units/coverage/rank metadata in several tables, incompletely locked pathway/direct-HR mappings in the validator, and had stale reusable-tool documentation. The primary agent added ordered provenance interfaces with exact-directory/name/range/config checks and manifest hashes, completed table metadata (including observation coverage), locked all eight pool/rate and component-HR names, updated documentation, and preserved preparations 1 and 2 unsubmitted. Corrected byte-identical preparation 3 is pending re-review on the same reviewer handle.
- Re-review continuity: the first preparation-3 re-review invocation on `/root/iter011_review` failed before returning findings because the selected model was at capacity. No review result was inferred; the same idle reviewer handle was retried.
- Final reviewed hashes: engine `96e59c3d...`; README `c416a99a...`; fixture `6def3915...`; validator `3d37a599...`; arguments `c6c859ad...`; preflight script `49f204ac...`; diagnostic script `54b11488...`; provenance list `a0056207...`; preparation-3 config `bca278cb...`.
- Final outcome: `pass_with_concerns`. All five blocking findings were resolved, canonical/submitted identities passed, and preparation 3 was judged safe to submit.
- Concern rationale: the reviewer mentioned a redundant duplicate staged-manifest write, but direct inspection of `run_preflight()` shows one `atomic_json` call for the manifest and one for the distinct receipt. The parameter-file second field is recorded but not compared to the pickle selector because the pickle selector remains authoritative and the two fields are not declared semantically equivalent; exact name/range/config binding is enforced. Neither concern changes the locked contract or preflight eligibility.
- Minimal-correction re-review continuity: the first attempt-4 review invocation failed before returning findings because the reviewer hit a platform usage limit. No result was inferred and attempt 4 remained unsubmitted; the same reviewer handle is retried after workflow resumption.
- Minimal-correction re-review result: `/root/iter011_review` returned `pass`; reviewed engine `96e59c3d...`, corrected fixture `3dcab08f...`, validator `3d37a599...`, arguments `c6c859ad...`, provenance list `a0056207...`, preflight script `49f204ac...`, and attempt-4 config `545fa609...`. It confirmed the import bootstrap is the sole execution-source change and attempt 4 is safe to rerun.
- Diagnostic submission review: the package passed every technical identity/resource/publication check, but the first review returned `block` because the preflight ledger row had not been reconciled from pending/active to terminal/finished. The primary agent corrected only that record; no source or materialized submission file changed.
- Diagnostic submission re-review: `/root/iter011_review` returned `pass`; the terminal ledger agrees with `CURRENT.md`, no job/monitor is active, and diagnostic attempt 1 is safe to submit. Reviewed diagnostic script `54b11488...`, config `8ec86dcb...`, arguments `c6c859ad...`, engine `96e59c3d...`, validator `3d37a599...`, and input manifest `7f528763...`.
- Validator-only correction authority: at `2026-10-05T03:13:06-07:00`, exact user response `I think just correct the error in the validator, and rerun the validator only, under attempt_1 folder. Other things in the correction package are authorized.` This narrows execution to the preserved diagnostic `attempt_1` staging package and authorizes the exact validator correction, independent review, validator-only submission/monitoring/accounting, atomic publication on pass, evaluation, records, and the already authorized closeout branch. It does not authorize regenerating diagnostic outputs.
- Validator-only correction review: `/root/iter011_review` returned `pass`. It confirmed required-column presence and nonempty metadata remain enforced except conditional `rejection_reason` blanks in the two score tables; the later supported/unsupported semantic checks remain intact. It also confirmed no generation command exists, identities are checked before validation, canonical/submitted wrapper and config copies match, staging is preserved, final results are absent, and atomic publication occurs only after pass. Reviewed hashes: validator `708d6e82...`, wrapper `c06d8593...`, config `5baf0fbd...`, input manifest `7f528763...`, staged output manifest `0e13dfa6...`.

## Execution and Diagnostics

- Static validation: after correction, `bash -n` passed for the argument and Slurm scripts; `git diff --check` passed; canonical/submitted attempt-2 script, configuration, arguments, and provenance checksum list are byte-identical. Repository Python remains reserved for the bounded compute-node preflight.
- Preflight: initial job `24101686` terminal `FAILED 1:0`; correction-rerun job `24102996` `COMPLETED 0:0`, 3:28 elapsed, input manifest `7f528763...`, receipt `cb008b68...`.
- Exact submissions: preflight job `24101686` from attempt 3; correction preflight `24102996` from attempt 4; diagnostic job `24103048` from diagnostic attempt 1; validator-only job `24103109` used `sbatch --parsable --export=ALL,VALIDATOR_ONLY_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter011_abby_ctrlvertc_oat_spinup/diagnostic/attempt_1/validator_only_submission_config.env ./submit_validator_only_iter011.slurm </dev/null` from the same attempt directory.
- Job identity checks: pass. Validator-only job `24103109` matched `elm-diag-i011-validate`, `standard/chopinsong`, 16 CPUs/80 GB/4 h, command `./submit_validator_only_iter011.slurm`, diagnostic `attempt_1` working directory, and declared log paths.
- Queue and terminal accounting: none active. Validator-only job `24103109` is terminal `COMPLETED 0:0` after 12 s with 1.934 s TotalCPU and batch MaxRSS 146,992 KB on `r7u01n2`; it became terminal during the immediate identity check, so the monitor strategy outcome is `finished` without a retained process handle.
- Resource diagnostics: preflight `24101686` used 196.83 MB; passing preflight `24102996` used 77.21 GB; diagnostic `24103048` used 77.20 GB. All remained within 80 GB; neither terminal diagnostic failure nor initial preflight failure was resource-caused.
- Failure, rejection, retry, or cancellation evidence: one authorized preflight-only correction was used. Diagnostic job `24103048` generated the complete 25 MB staging package but failed the original artifact validator's overbroad blank-field assertion; it was not eligible for an automatic scheduler/resource retry. Fresh user authority permitted only the exact validator correction and validator-only continuation under existing diagnostic `attempt_1`. Job `24103109` passed and atomically moved staging to final `results/`; no regeneration, cancellation, or diagnostic retry occurred.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | job `24102996`; `OAT_PREFLIGHT_PASS`; v5 input manifest covers 21 parameters, 21 configs, 21 parameter files, 21 restart cases/2,100 restart files, 21 pickles, and one observation | pass | deterministic fixtures, exact inventories/hashes, all-member inputs, and receipt passed |
| diagnostic | yes | generation job `24103048`; validator-only publication job `24103109`; output manifest `0e13dfa6...`; `ITER011_ARTIFACT_VALIDATE_PASS rows=80200 figures=11 restart_samples=63` | pass | the authorized narrow validator correction restored the declared conditional blank-field contract without regenerating outputs; all artifact checks passed before atomic publication |

- Final independent review: `/root/iter011_review` returned `pass_with_concerns`. It confirmed the exact output-manifest hash, 80,200 rows, 11 figures, all score/rank support, direct-HR and lowercase restart-total definitions, representative score and bin reproductions, pathway component sums/order, observed-SR separation, terminal accounting, and visual legibility. The stale pre-publication sentence it identified is corrected above. Heatmap color scales are dominated by the largest stock scores, but numeric annotations remain legible and the artifact gate passes.
- Quantitative result: `act25` leads mean SR/HR/LITFALL response spreads (`65.3%`/`74.5%`/`74.5%`), while `leaf_long` leads GPP (`68.4%`). `k_s4`, `k_s3`, and `k_s2` lead transient decomposer-C and final-spinup C/N/P spreads. Across all 2,100 members, mean N- and P-limited/potential pathway ratios are `0.293590` and `0.388401`; P-limited exceeds N-limited in every member.
- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: accept the validated baseline-conditioned, sampled-range descriptive ABBY OAT package. Constructed pathways remain distinct from direct model `HR`; no PAWN/Sobol/global-sensitivity, interaction, causal limitation, optimization, tuning, threshold, parameter recommendation, or cross-site/configuration conclusion is supported.
- Limitations: `/xdisk` is temporary and unbacked; observed SR covers 26,264/61,320 model hours and is contextual; OAT results are conditional on separate sampled ranges; extreme `k_s4` scores dominate heatmap colors but annotations remain legible.
- Closeout action: the authorized single closeout commit was created and verified; no push was performed.

## Proposed Next-Iteration Plan (Planning Only)

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

## Final Closeout Validator

- Identity: `development/ELM_diagnose/slurm/iter011/validate_iter011_closeout.sh`, SHA-256 `cc39bbd4d6e0bb67187dc903b4618fa6eae4c581660c59f334cfcf52a8452a08`; exact command `bash development/ELM_diagnose/slurm/iter011/validate_iter011_closeout.sh` from repository root. Scope: iteration report, compact result, cumulative summary, CSV-aware registry shape/uniqueness, handoff, published output manifest and every declared artifact hash/size/row count, canonical/submitted validator-only identities, staging/publication state, Slurm-script syntax, and `git diff --check`.
- Result: `ITER011_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=80200 transient_scores=105 spinup_scores=63 terminal_jobs=4 next_state=workflow_complete`.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter011/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit with no push
