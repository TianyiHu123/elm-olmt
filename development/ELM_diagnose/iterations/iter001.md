# iter001 - Nine-site seed-resolved ELM SR diagnostic

## Status

- Iteration ID: `iter001`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter001_nine_site_sr`
- Status: `failed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-28T20:24:11-07:00`
- Closed: `2026-08-28T20:41:00-07:00`

## Finalized Plan

- Sequential ID and work type: `iter001`; reusable diagnostic implementation and bounded nine-site execution.
- Evidence-derived objective and optional hypothesis: compare optimized historical ELM `SR` outputs, separately by available `ctrlopt` seed, with the operational `ppe6` control and the coupling campaign's site observations. No scientific-improvement hypothesis or cross-site claim is in scope.
- Proposed diagnostic inputs, upstream dependencies, and trust assumptions: nine operational `pklfiles/<SITE>_ppe6_I20TRCNPRDCTCBC.pkl` controls; every current `pklfiles/<SITE>_ctrlopt*_I20TRCNPRDCTCBC.pkl` candidate (60 files); and `SR` in each standard coupling NetCDF observation file. `model_ELM.load_obs_nc` remains the conversion and collocation authority.
- Bounded scope, work units, and exclusions: one integrated nine-site work unit; scalar hourly `SR` only; five figures per site (hourly, complete-day daily, monthly climatology, UTC diurnal, hourly boxplot); seed-level optimized overlays and metrics; control ensemble mean plus standard-deviation spread. Excludes parameter extraction, score thresholds, ranking, cross-site pooling, local-time conversion, CSV observations, and non-`SR` targets.
- Tentative acceptance gates and decision rule: input/shape/unit/time compatibility, common finite support, and expected-artifact completeness only. A complete package passes without a numerical skill threshold; failure of any requested input or compatibility check fails the integrated package.
- Proposed site and resource envelope, preflight, review, retry, cancellation, and stop boundaries: Puma standard; one node, four CPUs (20 GB implied), one-hour substantive cap; one 15-minute compute-node preflight; independent read-only review; 300-second monitoring cadence; one minimal re-reviewed preflight-only correction/rerun; no substantive automatic retry. Cancellation is limited to a proven universal pre-execution defect for a recorded Iter001 job. Stop only after terminal accounting, validation, records, and the authorized closeout commit.
- Expected evidence, artifacts, and record updates: deterministic external figures and CSV/JSON tables, input receipt/hashes, submitted scripts/configuration, logs, terminal accounting, review findings, Iter001 report, summary, registry, current handoff, validator result, and one closeout commit.
- Fresh consolidated kickoff-approval boundary: approved by the user in the request beginning “Start the ELM diagnostic iteration 1 ... Use this kickoff package”.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `2026-08-28T20:24:11-07:00`; “Start the ELM diagnostic iteration 1 by following development/ELM_diagnose/WORKFLOW.md. Begin at Section 4A and continue until the workflow-defined stop condition is reached. Use this kickoff package you just showed for this iteration.” |
| Kickoff goal, finite work-unit count, and stop conditions | Implement and close one integrated nine-site `SR` diagnostic; one preflight and one substantive work unit. Stop at validated closeout with no active/unaccounted job. |
| Confirmed HPC system and site profile | Puma; `development/hpc/puma.md`; `OLMT_puma`. |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter001/`; create authorized run directories; reuse deterministic paths for authorized reruns; retain unchanged after closeout; no automated deletion or backup. |
| Locked diagnostic inputs, dependencies, scope, exclusions, gates, and decision rule | Nine ensemble `ppe6` controls; all 60 current `ctrlopt` historical candidates; nine standard coupling SR NetCDF observations; `SR` only; seed-resolved optimized lines/metrics and control ensemble mean plus standard-deviation spread; UTC common finite support; no cross-site ranking or score gate. A preparation receipt locks exact paths, hashes, units, time ranges, and 60-file membership. |
| Lifecycle authority | Preparation, review, preflight, submission, monitoring, terminal accounting, evaluation, records, validation, and closeout are authorized. |
| Resources, monitoring cadence, and retry boundaries | One node, one task, four CPUs, standard partition/account `chopinsong`, 01:00:00 substantive cap; 00:15:00 preflight cap; 300-second cadence except immediate identity and terminal/reconciliation checks; one minimal preflight-only correction and re-reviewed rerun; no automatic substantive retry. |
| Cancellation scope | Only recorded Iter001 job IDs; only for a proven universal pre-execution defect while pending or before substantive processing. |
| Outside-sandbox authority | Authorized `sbatch` for the locked preflight and substantive submission plus allowed preflight rerun; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the recorded condition. |
| Closeout branch | One scoped closeout commit authorized; generated outputs remain outside Git. |

## Declared Diagnostic Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Operational controls | One ensemble-control pickle per site | `pklfiles/<SITE>_ppe6_I20TRCNPRDCTCBC.pkl` | serialized `ELMcase`; one scalar SR value per UTC hour and ensemble member | Locked in receipt during preparation | Same nine operational inputs as coupling; all nine present at bootstrap. |
| Optimized outputs | Separate optimized seed realization per site | `pklfiles/<SITE>_ctrlopt*_I20TRCNPRDCTCBC.pkl` | serialized `ELMcase`; one scalar SR value per UTC hour and seed file | Locked in receipt during preparation | All current matching historical candidates; bootstrap count `60`. |
| Observations | Per-site SR reference | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/<SITE>/<SITE>_cdo_merge.nc` | NetCDF; existing `model_ELM.load_obs_nc` conversion/collocation | Locked in receipt during preparation | Same nine files as coupling; all present at bootstrap. |
| Repository source | Implementation | repository commit | `e0d8a8a3ffaa7d4d2d848a3b9237b0eb26cdf225` | Source manifest during preparation | Clean bootstrap worktree. |

## Acceptance Gates and Decision Rule

- Required completeness: exactly nine controls, exactly 60 optimized candidates, exactly nine observation files, scalar `SR` targets, five figures per site, machine-readable receipt/metrics, and required durable records.
- Acceptance gates: supported units through `model_ELM.load_obs_nc`; nonempty common finite UTC timestamp intersection; complete 24-hour UTC days for daily plot; expected figures/tables exist; all observed site-seed/control metric rows are finite where mathematically defined.
- Decision rule: pass only when the integrated package satisfies all integrity gates. Metric values are descriptive, not selection or scientific-validation criteria.
- Conditional comparative metrics, aggregation, ranking, or tie-breaker: hourly-overlap `n`, RMSE, bias, MAE, R2, Pearson r, and KGE per optimized seed and per control against observations; no pooled metric, ranking, or tie-breaker.
- Changes requiring fresh authorization: input membership, target, observation behavior, resource cap, scope, gate, retry, cancellation, or output-root changes.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `slurm/iter001/preflight_iter001.slurm` / `545f334a4071ef04a6d0f72ab5c9871ae04dc312254de4912ff8948e9d8612ec` | submitted script/config byte-identical to canonical | `.../elm_diagnose_iter001/preflight`; `slurm_23718019.out/err` | locked inputs | commit `e0d8a8a3ffaa7d4d2d848a3b9237b0eb26cdf225`; reviewed Python `2d8be8d6ef40c7048d356289f884e6829d38e667260ee1d7a15d775d79b829e7` | `23718019` | `FAILED 1:0` | No rerun: input-interface failure. |
| diagnostic | not prepared after failed preflight | none | none | not eligible | none | none | not submitted | No substantive retry authority. |

## Independent Read-Only Review

- Reviewer: independent read-only `/root/iter001_review`.
- Reviewed source hash: Python `2d8be8d6ef40c7048d356289f884e6829d38e667260ee1d7a15d775d79b829e7`; Slurm `545f334a4071ef04a6d0f72ab5c9871ae04dc312254de4912ff8948e9d8612ec`; config `78ac8c4f2a392b850e2db30171bddd144d52586adc05c8852f75d6ab7ebab773`.
- Outcome: `pass` after the reviewer-required common-UTC-support, complete-day, seed-identity, and forcing-identity corrections.
- Findings and primary-agent response: all findings were corrected and re-reviewed before submission; the reviewer made no edits or runtime calls.

## Execution and Diagnostics

- Static validation: `bash -n development/ELM_diagnose/slurm/iter001/preflight_iter001.slurm` and `git diff --check` passed; canonical/submitted copies were byte-identical.
- Preflight: `23718019` submitted at `2026-08-28T20:35:52-07:00` from the approved run directory.
- Exact submission command: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter001/preflight/submission_config.env ./submit_preflight_iter001.slurm </dev/null`.
- Job identity checks: immediate `squeue`/`scontrol` recorded `RUNNING`, `standard`, account `chopinsong`, four CPUs, 20 GB, 15 minutes, and the intended external directory.
- Queue and terminal accounting: at the 300-second contract cadence, `sacct` reported `FAILED 1:0`, elapsed `00:00:28`, total CPU `00:07.925`, and `MaxRSS=2529772K`.
- Resource diagnostics: `seff 23718019` reported 2.41 GB/20 GB (12.06%) and 7.925 CPU seconds (7.08%); not resource-limited.
- Failure, rejection, retry, or cancellation evidence: `preflight_result.json` records `ValueError: ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl: missing case.output['SR']`. This input-interface failure blocks the package; no cancellation was needed and no unchanged retry is authorized.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| integrated diagnostic | no | failed preflight receipt and terminal accounting | fail | The first locked optimized pickle does not expose `case.output['SR']`; no valid optimized series is available. |

- Overall acceptance result: `fail`.
- Overall decision and closeout conclusion: Iter001 is closed failed before substantive diagnostics; no result, metric, or model-performance conclusion is made.
- Limitations: only the first optimized pickle was needed to establish the universal input-interface failure; remaining candidates were not validated.
- Next action: obtain a fresh consolidated package identifying compatible optimized historical outputs containing `SR`, or authorizing their generation/postprocessing.

## Proposed Next-Iteration Plan (Planning Only)

No Iter002 proposal is made. A new plan must resolve the failed optimized-output interface and receive fresh approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter001/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded: `git diff --check` plus the four-record status/receipt scan on `2026-08-28T20:41:00-07:00`; pass.
- [x] No job is active or unaccounted and every failure is classified
- [ ] Authorized closeout branch pending: one scoped commit authorized
