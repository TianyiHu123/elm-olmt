# iter008 - ABBY vertical-soil-carbon C:N nutrient-stress OAT diagnostic

## Status

- Iteration ID: `iter008`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter008_abby_ctrlvertc_cn_oat`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-25T20:06:03-07:00`
- Closed: `2026-09-25T21:19:10-07:00`
- Objective: Characterize how separate perturbations of `cn_s1`--`cn_s4` affect realized decomposition, microbial N/P demand satisfaction, plant N/P demand satisfaction, ecosystem carbon fluxes, and mineral nutrient cycling in the ABBY vertical-soil-carbon configuration.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 27 direct raw metrics; four accumulated satisfaction ratios; 58 response endpoints; 27,555 CSV rows; 11 figures; descriptive OAT only.

## Finalized Plan

The finalized planning-only proposal is recorded identically in commit `8e6f551` under `development/ELM_diagnose/iterations/iter007.md` and `development/ELM_diagnose/handoff/CURRENT.md`; that exact proposal is incorporated unchanged into this contract.

- Inputs are exactly `cn_s1:ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl`, `cn_s2:ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl`, `cn_s3:ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl`, and `cn_s4:ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl` beneath the declared ABBY `pklfiles` root. No discovery or globbing is permitted; unrelated directory files are ignored and never consumed.
- Declared linear ranges are `9`--`18` for `cn_s1`/`cn_s2` and `7`--`16` for `cn_s3`/`cn_s4`; each ensemble has 100 members and the required time contract is 61,320 no-leap hours for 2018--2024.
- Raw member responses are arithmetic temporal mean and population standard deviation (`ddof=0`). The four microbial/plant N/P satisfaction responses divide separately accumulated actual uptake or immobilization by separately accumulated potential demand; finite positive denominators are required and unsupported ratios remain explicit gaps without clipping or zero coercion.
- The 11 locked figures cover FPI/FPI_P; microbial N and P absolute/ratio responses; plant N and P absolute/ratio responses; GPP; SR; direct model HR; all eight direct pool-HR outputs; and N/P mineral-cycle context. Direct `HR` is never replaced by a pool sum. No `poolC * K`, constructed nutrient-limited HR, heatmap, observation, time-series, global-sensitivity, optimization, tuning, cross-site, or cross-configuration analysis is in scope.
- Machine-readable artifacts are exactly 4 `parameter_metadata.csv` rows, 31 `metric_definitions.csv` rows, 400 `member_metrics.csv` rows, 25,520 `response_curves.csv` rows, 1,600 `ratio_support.csv` rows, 27,555 CSV data rows total, 11 PNGs, and input/validation/output manifests.
- Work units are one bounded compute-node preflight and one diagnostic after preflight passes. Generate in attempt-local staging and atomically publish only a complete `results/` directory.
- Technical acceptance depends on immutable input, calculation, artifact, publication, independent-review, accounting, and record gates, not on whether the scientific hypothesis is supported. Results remain baseline-conditioned, range-dependent descriptive OAT evidence and cannot establish interactions, causality, optimum parameter values, or whole-ecosystem N limitation.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `complete package approved`; `2026-09-25T20:06:03-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Complete initialization, reusable implementation, independent read-only review, preflight, diagnostic, monitoring, terminal accounting, evaluation, records, validation, and closeout for exactly two compute work units. Stop for a fresh material decision, unapproved application/data/interface failure, exhausted retries, unavailable monitoring, explicit user stop, or validated closeout. |
| Confirmed HPC system and site profile | Puma login host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; `standard/chopinsong`; `OLMT_puma`; module pin `micromamba/2.0.2-2` revalidated by preflight. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter008_abby_ctrlvertc_cn_oat`; top-level `preflight/attempt_N`, `diagnostic/attempt_N`, and atomic `results`; root was absent at kickoff; create exact directories, retain failed attempts, never delete/overwrite/auto-backup existing material. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | Finalized plan above and commit `8e6f551`; exact four mappings/hashes below; control NetCDF only for native markers; no observations; immutable 27-variable/four-ratio/11-figure/27,555-row contract. |
| Lifecycle authority | Primary agent is sole writer/operator and may initialize records; implement reusable and iteration-specific material; create external root/attempts; launch and await one independent read-only reviewer; submit/monitor/account; validate/evaluate; update four records; and close out. Reviewer remains read-only. |
| Resources, monitoring and wait mechanism, and retry boundaries | Preflight 1 node/task, 12 CPUs/60 GB/2 h; diagnostic 1 node/task, 12 CPUs/60 GB/4 h. One initial plus at most three retries per work unit; scheduler/resource retry maximum 16 CPUs/80 GB/6 h. One minimal preflight-only contract-restoring correction; diagnostic application/code/data/schema/unit/sign/dimensionality/dependency/numerical failures require fresh approval. Ongoing profile state-change detector at 300 s through one retained terminal session, waited on in bounded tool calls; one materially different detached `tmux` fallback if the handle is demonstrably lost; terminal job-scoped `sacct` required. |
| Cancellation scope | Only recorded Iter008 job IDs, for verified identity mismatch, proven universal pre-execution defect, writes outside approved scope, contract overrun, or explicit user instruction. Cancellation grants no fix or retry. |
| Outside-sandbox authority | Approved `sbatch` for locked attempts/retries; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only for recorded Iter008 IDs under the stated conditions. |
| Closeout branch | Exactly one scoped closeout commit authorized; no push. |

## Declared Diagnostic Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| `cn_s1` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns1_I20TRCNPRDCTCBC.pkl` | validated ELMcase | 4,121,205,317 bytes; `fca486c11cf2a7c087195a7608b49d9b26c87c7369cd5a9418d6e44f4d9fcc1f` | exact identity, content, 100 members, range, time axis, and variables passed preflight |
| `cn_s2` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns2_I20TRCNPRDCTCBC.pkl` | validated ELMcase | 4,121,205,317 bytes; `40589f8c95da4d12940dc99f1acfbe118721399e826283365fd628c3642c2297` | exact identity, content, 100 members, range, time axis, and variables passed preflight |
| `cn_s3` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns3_I20TRCNPRDCTCBC.pkl` | validated ELMcase | 4,121,205,317 bytes; `b3d5d2aa40c48211551a16cd8db8ffca56430dc13f323087aeeffaf87ee525f1` | exact identity, content, 100 members, range, time axis, and variables passed preflight |
| `cn_s4` pickle | OAT input | `.../ABBY/pklfiles/ABBY_ctrlvertccns4_I20TRCNPRDCTCBC.pkl` | validated ELMcase | 4,121,205,317 bytes; `c68eaafb6b0dbe54c5aa7eb604842ee36673228cb0357ecdd4b973ff35954ff6` | exact identity, content, 100 members, range, time axis, and variables passed preflight |
| Control parameter NetCDF | Native markers | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc` | validated NetCDF | `3876806bdaf2c432dde41db748b139b962068f6c1b0a1c86324c60eaf91042e9` | native markers `12`, `12`, `10`, and `10` validated for `cn_s1`--`cn_s4` |
| Repository/environment | Execution source | `/xdisk/chopinsong/tianyihu/elm-olmt` | `feature/ELM_diagnostics`; kickoff commit `8e6f551` | environment YAML `02283ec147688734ecbb3aa3a562e85f5c060c8810ca5ea66c8a81fd092878bb` | Clean at kickoff; execution source subsequently pinned by hashes |

- Storage evidence: `/xdisk/chopinsong` 17.5/19.5 TB; home 39.1/50 GB; group storage 473.5/500 GB. Allocation expiration is PI-only and unavailable.
- Account evidence: group standard use 286/3290 CPUs and 1.4 TB/16,998 GB; 29 submitted jobs; no user standard allocation shown. Contract fits limits.
- Four config and four parameter-file SHA-256 values are preserved in kickoff evidence and will be pinned in submission configuration.

## Acceptance Gates and Decision Rule

- Required completeness: exact four mappings/400 members; exact identities/ranges/provenance/variables/units/signs/time axes/shapes; four fixture-validated ratios; 27,555 CSV rows; 11 figures; complete manifests; visual inspection; independent reviews; terminal accounting; consistent records.
- Calculation gate: direct hourly means and `ddof=0` standard deviations; separately integrated numerator/denominator ratios; finite positive denominators; explicit unsupported gaps; no clipping/coercion; FPI/FPI_P in `[0,1]`.
- Artifact gate: Figure 8 uses direct `HR`; Figure 9 contains all eight direct pool-HR outputs; removed constructed-HR and heatmap products are absent.
- Decision rule: technical pass is independent of hypothesis outcome. Report ranges, directions, support, nonlinearities, and microbial--plant trade-offs without global, causal, optimization, or whole-ecosystem limitation claims.
- Changes requiring fresh authorization: input membership, calculations, variables, figures, output root, gates, interpretation, maximum resources, retry count, diagnostic application/data correction, cancellation expansion, or closeout branch.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter008.slurm` / `61fe944e` | submitted copy byte-identical `61fe944e`; config byte-identical `d3937af7` | `.../preflight/attempt_1`; logs `slurm_%j.out/.err` | tool `31000fb1`; locked inputs/configs/parameters/control/environment | kickoff `8e6f551`; dirty source pinned by hashes | `24015245` | `COMPLETED 0:0`; elapsed 00:01:38; MaxRSS 20,662,444 K; receipt pass | monitor session `47630` handed off on queue query; terminal `sacct` complete |
| diagnostic | `diagnostic_iter008.slurm` / `837afd4d` | submitted copy byte-identical `837afd4d`; config byte-identical `cc8d34b3`; template `54260498` | `.../diagnostic/attempt_1` | validator `8aaa127c`; tool `31000fb1`; manifest `2c90f754`; receipt `56fb4d94` | kickoff `8e6f551`; dirty source pinned by hashes | `24015300` | `COMPLETED 0:0`; elapsed 00:01:00; MaxRSS 4,369,696 K; validation/publication pass | monitor session `24507` handed off after `COMPLETING`; terminal `sacct` complete |

Monitoring outcomes are `active`, `handoff`, `failed`, `unsupported`, or `finished`. Workload state is recorded separately.

## Independent Read-Only Review

- Reviewer: `01a0dbb6-277e-7ad2-be12-36d57f1b962f` (`Galileo`), read-only preparation review
- Reviewed source hashes: tool `1468f0c6`, preflight wrapper `c90e76b5`, diagnostic wrapper `9eb21aca`, validator `299d7edf`, preflight config `82335393`, and diagnostic template `31032510`
- Outcome: `block`
- Findings and primary-agent response: reviewer found incorrect per-second labels for postprocessed daily N/P fluxes, incomplete dependency provenance in the input manifest, missing selector-zero enforcement, and incomplete artifact-map key coverage. The implementation now uses daily units; requires exact config and parameter-file mappings and records their absolute paths, sizes, and hashes; enforces selector zero; and requires exact payload key coverage. Corrected hashes are tool `31000fb1`, preflight wrapper `61fe944e`, diagnostic wrapper `837afd4d`, validator `8aaa127c`, and diagnostic template `54260498`. No job was submitted. Passing independent re-review is required before submission.
- Re-reviewer: `01a0dbbb-cdf9-77a0-a9db-62c58c0bc055` (`Raman`), read-only corrected-package review.
- Re-review outcome: `pass` at `2026-09-25T20:44:05-07:00`. The reviewer confirmed all four corrections, exact scientific/count contracts, wrapper safeguards, source/dependency hashes, byte-identical submitted copies, and absent outputs. The corrected package is eligible for preflight submission.
- Diagnostic launch review: reviewer `01a0dbbb-cdf9-77a0-a9db-62c58c0bc055` (`Raman`) returned `pass` at `2026-09-25T20:55:37-07:00` after verifying terminal preflight evidence, exact manifest/receipt hashes, byte-identical wrapper/config, pinned source/dependency identities, resource request, guards, output absence, validator, and atomic publication.
- Final result review: the same independent read-only reviewer returned `pass` with no blocking concern. It verified terminal accounting, empty diagnostic stderr, all three pass markers, all 16 payload hashes/sizes, exact rows/figures, 23,200 member plus 2,320 bin response rows, 61,320-hour member coverage, 1,600 supported ratios, direct HR and all eight direct pool-HR metrics, excluded-artifact absence, all 11 figures, and the interpretation boundary. Non-blocking notes are the descriptive `cn_s1` upper-range discontinuity and the tall but legible full-resolution pool atlas.

## Execution and Diagnostics

- Static validation: corrected `git diff --check` and `bash -n` pass; canonical source hashes recorded above. Repository Python remains reserved for compute-node preflight.
- Preflight: job `24015245` passed with `NUTRIENT_OAT_PREFLIGHT_PASS parameters=4 members=400 hours=61320`; receipt status and fixture status are `pass`; input manifest `2c90f754`; receipt `56fb4d94`; stderr contains only an ArviZ future warning.
- Diagnostic: attempt one job `24015300` completed `0:0`; stdout records generator, artifact-validator, and atomic-publication passes; stderr is empty; output manifest `9d5c8b07`.
- Exact diagnostic submission command: from `.../diagnostic/attempt_1`, `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter008_abby_ctrlvertc_cn_oat/diagnostic/attempt_1/submission_config.env ./submit_diagnostic_iter008.slurm </dev/null`.
- Job identity checks: preflight job `24015245` matched `elm-diag-i008-preflight`, `standard/chopinsong`, 12 CPUs, 60 GB, 2 h, submitted command, workdir, logs, and `/dev/null` stdin at `2026-09-25T20:45:01-07:00`.
- Diagnostic job `24015300` matched `elm-diag-i008-diagnostic`, `standard/chopinsong`, 12 CPUs, 60 GB, 4 h, submitted command, workdir, logs, and `/dev/null` stdin.
- Queue and terminal accounting: preflight job `24015245` and diagnostic job `24015300` are both `COMPLETED 0:0`; diagnostic elapsed `00:01:00`, TotalCPU `00:44.928`, 12 allocated CPUs, batch MaxRSS `4369696K`.
- Resource diagnostics: preflight `seff` reports 4.1% CPU and 19.71/60 GB memory; diagnostic reports 6.24% CPU and 4.17/60 GB memory. Neither work unit had a resource failure.
- Failure, rejection, retry, or cancellation evidence: initial preparation review blocked before submission; no compute attempt or retry was consumed.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | four exact inputs, 400 members, 61,320 hours; manifests and fixture pass; terminal accounting complete | pass | all declared preflight gates passed |
| diagnostic | yes | generator, exact artifact validator, and atomic-publication markers pass; output manifest status pass; terminal accounting complete | pass | all declared execution gates passed |

- Artifact validation: exactly 4 parameter rows, 31 metric definitions, 400 member rows, 25,520 response rows, 1,600 ratio-support rows, 27,555 CSV data rows, and 11 declared PNGs. All 1,600 ratios are supported; no ratio value was coerced to zero. Output-manifest membership, byte sizes, and hashes match the published payload, and attempt-local staging is absent after atomic publication.
- Visual validation: all 11 PNGs were inspected. Titles, parameter facets, native-value markers, axes, units, legends, member support, and response lines are legible; the 8-row pool-HR panel includes every direct pool output. No constructed-HR or heatmap artifact exists.
- Endpoint evidence uses the lowest and highest sampled parameter values, not extrapolated declared bounds. Raising `cn_s1`, `cn_s2`, `cn_s3`, and `cn_s4` changed microbial N satisfaction by `+2.3%`, `+25.4%`, `+108.4%`, and `+118.6%`, respectively, and microbial P satisfaction by `+22.2%`, `+33.7%`, `+96.1%`, and `+95.7%`. Potential N immobilization fell `19.8%`--`66.7%`; potential P immobilization fell `43.3%`--`63.8%`. Actual immobilization generally fell too, except for small increases under `cn_s4` (`+4.4%` N, `+4.7%` P), so higher satisfaction mainly reflects demand falling faster than realized immobilization.
- Plant N/P satisfaction changed little and nearly in parallel: `cn_s1` about `+0.6%`, `cn_s2` about `-3.6%`, `cn_s3` about `+1.4%`, and `cn_s4` about `+4.3%`. The tested C:N changes therefore do not show broad relief of plant nutrient demand; only `cn_s4` yields a modest improvement over its sampled range.
- Direct HR changed by `+1.0%`, `-5.4%`, `-0.7%`, and `+4.6%` from low to high sampled `cn_s1`--`cn_s4`; SR follows nearly the same directions. All nonzero direct pool-HR components respond coherently for `cn_s2` (declines) and `cn_s4` (increases), while `cn_s3` effects are small and `CWDC_HR` remains zero. Thus microbial satisfaction relief does not imply increased realized decomposition: `cn_s2` and `cn_s3` improve satisfaction while HR is flat or lower.
- `FPI` and `FPI_P` generally rise with C:N, most strongly for `cn_s3`/`cn_s4`. `cn_s1` exhibits a reproducible high-range discontinuity across several responses near the upper sampled range; it is descriptive model behavior here, not an inferred threshold.
- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: accepted the validated baseline-conditioned ABBY C:N OAT package. Increasing pool C:N can relieve microbial N/P demand mismatch, strongest for pools 3 and 4, but does not generally relieve plant stress or guarantee higher decomposition.
- Limitations: `/xdisk` is temporary and unbacked; allocation expiration unavailable to non-PI; scientific interpretation remains conditional on the declared OAT ranges.
- Next action: workflow complete; no next iteration is proposed, and any new diagnostic requires a fresh planning package and approval.

## Proposed Next-Iteration Plan (Planning Only)

Workflow complete. No next iteration is proposed; any new diagnostic requires a fresh planning package and approval.

## Final Closeout Validator

- Identity: inline bounded validator using Python's CSV-aware standard-library parser plus shell identity, artifact, row-count, hash, submitted-copy, `bash -n`, and `git diff --check` checks; command scope is the iteration report, compact result, cumulative summary, registry, current handoff, canonical/submitted execution material, and published result package.
- Result: `ITER008_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=27555 ratios_supported=1600 terminal_jobs=2 next_state=workflow_complete`.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter008/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit
