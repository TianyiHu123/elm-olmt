# iter013 - ABBY observations and final-spinup stoichiometric ratios

## Status

- Iteration ID: `iter013`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-10T02:21:07-07:00`
- Closed: `2026-10-10T15:58:15-07:00`

## Finalized Plan

### Identity, objective, and interpretation boundary

- The immutable plan is the planning body recorded byte-identically in `iterations/iter012.md` and `handoff/CURRENT.md` at planning commit `92e3112f3083e4a94358b05f72a84ab69fea2906`, SHA-256 `58ef4f8ee171c4f95c3faa9028671146f02c14b617ba963f9e18859f3f55facc`; it is incorporated here without change by this identity and the complete locked terms below.
- Objective: extend Iter012's exact 27-parameter ABBY vertical-soil-carbon OAT package with contextual NEON `GPP_DT` and `GPP_NT` references and final-spinup eight-pool `DECOMP_CN_RATIO` and `DECOMP_CP_RATIO` endpoints, plus contextual observed soil C, soil N, and C:N references.
- Interpretation remains baseline-conditioned, sampled-range descriptive OAT. Observations are contextual only and never enter statistics, scores, ranks, acceptance, calibration, or tuning. No PAWN/Sobol/global, interaction, causal, threshold, optimization, recommendation, cross-site, or boundary-matched-validation claim is allowed.

### Exact inputs and calculations

- Reuse exactly the ordered Iter012 mappings for `act25`, `br_mr`, `cn_s1`--`cn_s4`, `decomp_depth_efolding`, `frootcn`, `grperc`, `k_l1`--`k_l3`, `k_s1`--`k_s4`, `leafcn`, `leaf_long`, `lflitcn`, `livewdcn`, `q10_mr`, `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, and `rf_s3s4`: 27 exact pickles/configs/parameter files/restart cases and 2,700 members. Reject discovery, globs, reordering, substitutions, or extra top-level inputs.
- Preserve exact 61,320-hour 2018--2024 no-leap model coverage, five transient means, direct `HR`, exact eight-pool transient decomposer C, exact final `0201-01-01` restart mapping, and the constructed potential/N/P-limited pathways.
- Retain contextual SR from `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` and add `GPP_DT`/`GPP_NT` from `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/statistics/ABBY_neon_eval_hourly.nc`. Generalize observations input-driven and backward-compatibly to target/source/series/path. Preserve full-window model means; observation means use independent valid support after no-leap conversion and unit conversion. Retain finite zero/positive GPP, reject negative GPP, report every support denominator, and create no collocated model curves or synthetic uncertainty band.
- Preserve `DECOMP_C_TOTAL`, `DECOMP_N_TOTAL`, and `DECOMP_P_TOTAL` as masked-aware sums of all stored vertical elements of exact lowercase `_vr` `cwd`, `litr1`--`litr3`, and `soil1`--`soil4` pools. Add memberwise `DECOMP_CN_RATIO=C/N` in `gC gN-1` and `DECOMP_CP_RATIO=C/P` in `gC gP-1` as ratios of eight-pool sums. Require finite positive denominators; gaps remain explicit and never zero.
- Use `/xdisk/chopinsong/tianyihu/NEON_surfdata/neon_surffiles/NEON_soilC_N_CN.csv`, unique ABBY row, as contextual C, N, and C:N references only. Disclose the observed 0--2 m soil profile versus model all-stored-element CWD+litter+soil boundary mismatch. Add no P/C:P observation.
- Apply `100 * (P95-P05) / abs(ensemble median)` separately to all five spinup endpoints and rank within endpoint. The strict gate requires 100/100 supported ratios for every parameter and all 135 spinup scores supported.

### Outputs, scope, and acceptance

- Publish exactly 109,113 primary CSV rows and 13 PNGs: five transient atlases, five spinup atlases, transient and five-column spinup heatmaps, and one pathway atlas. GPP references use distinct colors and one figure-level legend. Soil references appear only in C, N, and C:N atlases; observations never appear in heatmaps.
- Keep transient and scalar-spinup observations in separate tables with target/source identity, labels, hashes, aggregation, units, raw/retained/rejected support, time/depth coverage, denominator, endpoint/boundary definition, and `enters_scoring=false`.
- Two compute work units: one no-evaluation preflight, then one diagnostic consuming only its passing manifest with hidden staging, exact validation, and atomic publication.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs`; immutable `preflight/attempt_N` and `diagnostic/attempt_N`; never overwrite/delete; no automatic backup; `/xdisk` is temporary and unbacked.
- Exclude ELM simulation/postprocessing, source mutation/repair, model-time/member dropping, interpolation, collocated curves, ER/NEE analysis, alternative/depth-matched stocks, layer weighting, vegetation pools, observed P/C:P, uncertainty bands, compensation/litter/temporal-standard-deviation outputs, cross-site comparison, surrogate/global/causal/optimization/tuning work, and prior-result regeneration.
- Technical acceptance requires exact input/provenance, formula/support, 109,113-row/13-figure artifact and visual, atomic publication, independent review, terminal-accounting, and cross-record gates. Scientific ranking or observation proximity never affects acceptance.

### Resources, retries, monitoring, and authority boundary

- Puma `chopinsong/standard`, `OLMT_puma`, one node/task, four CPUs with scheduler-derived 20 GB, two hours preflight and four hours diagnostic. One initial attempt plus at most three retries per work unit; at most one minimal preflight-only correction; every other automatic retry is same-scope scheduler/resource-only.
- Application/code/interface/schema/data/dependency/numerical/scientific/publication/gate/resource-cap failure stops for classification and fresh authorization. Monitor each submitted job continuously through job-scoped terminal accounting. Cancel recorded Iter013 jobs only for the approved conditions.
- Expected evidence includes exact source/config/submitted identities and hashes, fixtures/receipt, observation conversions/support, independently reproduced totals/ratios/scores/ranks/bins/counts/hashes, all-figure visual review, job/log/resource/accounting evidence, output manifest, scientific report, and final cross-record validation.

## Consolidated Kickoff Package and Runtime Contract

| Field | Approved value |
| --- | --- |
| User response and timestamp | `I confirm the active session is Puma and approve the complete Iter013 kickoff package, including the stated lifecycle, resources, retries, cancellation conditions, outside-sandbox sbatch/monitoring/accounting/scancel authority, and exactly one scoped closeout commit with no push.`; `2026-10-10T02:21:07-07:00` |
| Goal and stop boundary | Execute Iter013 through initialization, implementation, independent review, preflight, diagnostic, continuous monitoring, terminal accounting, evaluation, cross-record validation, and one-commit/no-push closeout. Stop earlier only for an approved stop condition, exhausted authority/retries, review block, input/gate/resource failure requiring a revised package, unavailable authoritative monitoring, or explicit user stop. |
| HPC/profile | Confirmed Puma host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; `OLMT_puma`. |
| Output/storage | Exact root and immutable layout above may be created; no overwrite/delete/automatic backup; `/xdisk` is temporary, unbacked, 91% used with about 2.0 TB free at kickoff; expiration query unavailable to the non-PI account. |
| Locked scope | Finalized plan above; 27 ensembles/2,700 members; GPP references; five spinup endpoints; 109,113 rows; 13 figures; exact exclusions and gates. |
| Lifecycle authority | Initialization, implementation, approved-directory creation, read-only reviewer launch/wait, bounded preflight and diagnostic, monitoring/accounting, evaluation, records, final validation, and closeout. |
| Resources/retries | Four CPUs/derived 20 GB; two-hour preflight; four-hour diagnostic; initial plus at most three attempts per unit; one minimal preflight correction; scheduler/resource-only other retries. |
| Cancellation | Recorded Iter013 job IDs only for identity mismatch, proven universal pre-execution defect, out-of-root writes, resource-contract overrun, or explicit instruction; terminal accounting required. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the approved conditions. |
| Closeout | Exactly one scoped closeout commit; no push. |

## Declared Diagnostic Inputs and Evidence

### Revised attempt-4 authority

- At `2026-10-10T02:53:36-07:00`, the user responded: `I approve the revised Iter013 package, and give you three more retry budget.` At `2026-10-10T15:17:45-07:00`, after a usage-limit interruption, the user explicitly instructed: `you got interrupted by usage limits, resume the workflow now.`
- This authorizes the previously presented narrow correction: compute and record C:N/C:P ratios only when selected, add a restart-backed original-Iter012 no-ratio compatibility fixture, obtain independent re-review, and submit immutable preflight attempt 4 at the unchanged four-CPU/20-GB/two-hour shape. If it passes, continue the already approved diagnostic, evaluation, validation, and one-commit/no-push closeout lifecycle.
- Three additional retries are available under the existing classification boundary: automatic retries remain same-scope scheduler/resource-only; any further application/code/interface/schema/data/dependency/numerical/scientific/publication/gate/resource-cap change still requires fresh approval.

| Input/dependency | Planning identity/evidence |
| --- | --- |
| Repository | clean `feature/ELM_diagnostics` at `92e3112f3083e4a94358b05f72a84ab69fea2906`; one local commit ahead before initialization |
| Finalized plan | `58ef4f8ee171c4f95c3faa9028671146f02c14b617ba963f9e18859f3f55facc` |
| Engine | `development/ELM_diagnose/tools/oat_sensitivity.py`; `96e59c3de95e244c2abe02ecf3c36ac365ae6026a1cf8df9e35e777d4c37d611` |
| Environment | `conda_envs/OLMT_puma.yml`; `02283ec147688734ecbb3aa3a562e85f5c060c8810ca5ea66c8a81fd092878bb` |
| Iter012 arguments | `development/ELM_diagnose/slurm/iter012/oat_args.sh`; `2009a7dcf5c7699b00152da042b963ba8188004a68f8d444e2e33e6360693fca`; 27 mappings per family, five targets, one SR observation, eight pathways |
| Inventory | 27 top-level pickles, 27 configs, 27 parameter files, 27 restart cases, and 2,700 final restart files observed at kickoff |
| SR NetCDF | `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` |
| GPP NetCDF | `abf1d62a02791c36258330206da4c142527ba1ea5a8b1922122ac3e2cb155503` |
| Soil reference CSV | `1869761ef73ac9b7c7789d29c516523cfd0895d6c0c53031e6bf4a147ac22afa` |
| Soil derivation/script | `calc_neon_soilCN.py` `9cd8166c8573adda5800a7ff30aac7a1295cf171a795817948f42928b70a05e0`; `ABBY_surfaceData.csv` `cf74b4002fe3902612571837e660c4e73bfe2ce8ff9fb4171b3f55862849a69b` |

Full deserialization, dimensions, masks, units, member/time parity, all restart schemas, post-calendar observation counts, and exact current hashes remain compute-node preflight gates.

## Acceptance Gates and Decision Rule

- Required completeness and gates are the finalized-plan input, calculation/support, artifact/visual, publication/review/accounting/record gates.
- Decision: pass only if every immutable gate passes; do not reinterpret gates after results.
- Changes requiring fresh authorization: every scope/input/formula/artifact/gate/resource-cap change and every application/code/data/interface/schema/numerical failure outside the one minimal preflight correction.

## Provenance and Job Ledger

| Work unit | Canonical/submitted identity | Run directory/logs | Job scope/state | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| preflight preparation 1 | canonical/submitted script `8c4ac01a...`; arguments `12f5246b...`; config `98718075...`; provenance `1e13d878...`; tool `48fc3b87...`; fixture `5b282153...`; validator `70e6fde0...`; all submitted copies byte-identical | `.../preflight/attempt_1`; no logs | none; deliberately unsubmitted after review block | no monitor invoked; immutable preparation evidence retained |
| preflight attempt 2 | script `8c4ac01a...`; arguments `12f5246b...`; config `7003be00...`; provenance `1e13d878...`; tool `7e084c6a...`; fixture `548a99b5...`; validator `70e6fde0...`; all submitted copies byte-identical; manifest `a0da0e96...`; receipt `815285aa...` | `.../preflight/attempt_2`; logs `c1137383...`/`1b694134...`; GNU time `4edf489e...` | job `24192660` terminal `COMPLETED 0:0`; elapsed `00:06:10`; CPU `04:20.044`; four CPUs/20 GB; Slurm MaxRSS `20970408K` allocation-pegged; independent peak `6413796K`, swaps 0, exit 0 | session `92439` handoff due chatter; session `14410` finished at terminal accounting; receipt/fixture passed, but gate reconciliation found complete ratio support was not machine-enforced; contract's one minimal preflight-only correction invoked |
| preflight attempt 3 | corrected tool `835d072e...`; fixture `8e567e19...`; validator `dc47b853...`; arguments `7d739e87...`; config `3658644b...`; script `8c4ac01a...`; provenance `1e13d878...`; submitted script/arguments/config/provenance byte-identical | `.../preflight/attempt_3` | none; unsubmitted; review-blocked | strict 100/100 enforcement is correct, but ratio support metadata is added unconditionally when ratios are not selected, changing original Iter012 primary output/manifest; one minimal preflight correction is exhausted; fresh approval required before code change or rerun |
| preflight attempt 4 | tool `3b48732f...`; fixture `1743f291...`; validator `dc47b853...`; arguments `7d739e87...`; config `05c9e79c...`; script `8c4ac01a...`; provenance `1e13d878...`; submitted script/arguments/config/provenance byte-identical; command `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=.../attempt_4/submission_config.env ./submit_preflight_iter013.slurm </dev/null` at `2026-10-10T15:20:34-07:00` | `.../preflight/attempt_4`; manifest `808ec4f0...`; receipt `f5c6f8aa...`; logs `6a6abbc4...`/`189d5450...`; GNU time `721cb297...` | parent job `24204148`; terminal `COMPLETED 0:0`; elapsed `00:08:16`; CPU `06:18.351`; four CPUs/20 GB; batch MaxRSS `20970480K` allocation-pegged; independent peak `6412868K`, swaps 0 | monitor session `9882` finished at authoritative terminal accounting; receipt/schema/status pass; exact 27 parameters, 2700 members, 61,320 hours; every C:N and C:P support entry is 100 valid/0 rejected; regression fixture passed; preflight gate `pass` |
| diagnostic attempt 1 | canonical/submitted script `e0db7869...`; arguments `7d739e87...`; config `8213ecca...`; passing manifest `808ec4f0...`; output manifest `99d84254...`; logs `9058868d...`/`e3b0c442...`; GNU time `e8adb695...`; submitted copies byte-identical | `.../diagnostic/attempt_1`; published `.../results` | job `24204180` terminal `COMPLETED 0:0`; elapsed `00:07:33`; CPU `05:59.569`; four CPUs/20 GB; batch MaxRSS `20970544K` allocation-pegged; independent peak `6413020K`, swaps 0 | monitor session `58719` finished at authoritative accounting; generation, validator (`109113` rows/13 figures/135 restart samples), and atomic publication passed; final review `pass_with_concerns`, nonblocking visual concerns recorded |

## Independent Read-Only Review

- Reviewer: `/root/iter013_review`
- Reviewed source hash: `48fc3b87...` (preparation 1 block), `7e084c6a...` (attempt 2 pass), `835d072e...` (attempt 3 block), `3b48732f...` (attempt 4 pass-with-concerns), diagnostic package `e0db7869...`/`8213ecca...`/`808ec4f0...` (pass-with-concerns), and published manifest `99d84254...` (final pass-with-concerns).
- Outcome: preparation 1 `block`; corrected attempt 2 `pass`; attempt 3 minimal-correction re-review `block`; revised attempt 4 `pass_with_concerns`; diagnostic preparation and final results `pass_with_concerns`.
- Findings and response: preparation blockers were corrected and attempt 2 passed review. Post-preflight reconciliation invoked the original single minimal correction to machine-enforce 100/100 ratio support. Attempt 3 re-review confirmed that gate but blocked because ratio support was unconditional under original Iter012 arguments. Revised authority enabled attempt 4, whose input-driven ratio support and restart-backed no-ratio fixture passed. Diagnostic preparation independently passed after a stale handoff timestamp was corrected. Final review reproduced all 2,700 C:N/C:P ratios, all 270 transient/spinup scores and ranks, every response bin, observation semantics, artifact hashes/counts, atomic layout, and all 13 figures. Its only final concerns are modest heatmap annotation contrast and small boundary-warning footer text; both are readable at original resolution and do not affect any immutable correctness gate. No correction is warranted after publication.

## Execution and Diagnostics

- Static validation: shell syntax and `git diff --check` pass; Python compilation and fixtures are locked compute-node preflight gates.
- Preflight: attempt 2 job `24192660` completed `0:0`; attempt 3 remained unsubmitted; revised attempt 4 job `24204148` completed `0:0` and passed all immutable receipt, manifest, ratio-support, regression, and resource gates.
- Diagnostic: attempt 1 job `24204180` completed `0:0`; generation, artifact validation, atomic publication, and independent final review passed.
- Queue/accounting/resources: no active scope; all submitted jobs terminally accounted above.
- Final cross-record validator: `development/ELM_diagnose/slurm/iter013/validate_iter013_closeout.sh`, SHA-256 `2c24842dd3553c333f8767671192bff48d02b083cd86172bb3760ee22090d2f3`; pass marker `ITER013_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=13 csv_rows=109113 transient_scores=135 spinup_scores=135 terminal_jobs=3 next_state=workflow_complete`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Decision: accept the validated baseline-conditioned, sampled-range descriptive OAT extension. `rf_s2s3` leads final-spinup C:N spread (166.2%); `k_s4` leads final-spinup C:P (51.7%) and all three elemental totals. Observations remain independent context only and do not support calibration, proximity scoring, or boundary-matched validation.
- Limitations: SR/GPP observations have partial independent support; the soil reference is boundary-mismatched; heatmap annotations/footer are relatively small at default scale; `/xdisk` is temporary/unbacked. Results support no global/causal, interaction, threshold, optimization, tuning, recommendation, or cross-site claim.
- Next action: no Iter014 plan is proposed. Any future iteration requires a new planning-only proposal and consolidated kickoff approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter013/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Final cross-record validator passed
- [x] No job active or unaccounted
- [x] Exactly one scoped closeout commit created; no push
