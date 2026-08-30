# iter002 - Nine-site seed-resolved ELM SR diagnostic recovery

## Status

- Iteration ID: `iter002`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter002_nine_site_sr`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-29T16:47:14-07:00`
- Closed: `2026-08-29T17:27:04-07:00`

## Finalized Plan

- Objective: validate newly postprocessed optimized pickles and generate the nine-site seed-resolved `SR` diagnostic package.
- Inputs: nine `ppe6` control ensembles; all 60 current `ctrlopt` historical pickles; standard coupling per-site SR NetCDF observations; existing `model_ELM.load_obs_nc` conversion/collocation.
- Scope: scalar hourly SR; separate optimized seeds; control mean plus SD; raw hourly, complete-day daily, monthly, UTC diurnal, and hourly boxplot figures; hourly observation metrics per seed and control. No parameter extraction, model run, ranking, pooling, local-time conversion, non-SR target, or score threshold.
- Gate and decision rule: exact membership, target shape, supported units, optimized/control `taxis` and forcing identity, common finite UTC support, one complete day, and expected artifact completeness. Metrics are descriptive only.
- Runtime: Puma standard / `OLMT_puma`; preflight completed at 4 CPUs/20 GB/15 minutes; revised package approved a 6-CPU/30-GB one-hour integrated substantive job after preflight consumed 20.00/20 GB. 300-second monitoring; no automatic substantive retry. Cancellation only for a recorded job and universal pre-execution defect.
- Outputs and records: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/`; retain without deletion/backup; records, review, terminal accounting, validator, and one closeout commit.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `2026-08-29T16:47:14-07:00`; approved complete Iter002 package, scheduler authority, and outside-sandbox permission; instructed continuation to workflow stop condition. |
| Goal and stop boundary | One integrated nine-site diagnostic, ending only after terminal accounting, evaluation, records validation, and one closeout commit. |
| Site | Puma; `development/hpc/puma.md`; `OLMT_puma`. |
| Output/storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/`; authorized creation; retain; no automated backup/deletion. |
| Locked inputs/scope | Nine `ppe6` ensemble controls, all 60 current `ctrlopt` files, nine standard SR observations, scalar SR only, seed-level optimized plots/metrics, control mean/SD, UTC support, no ranking/threshold. |
| Lifecycle and outside-sandbox authority | Preparation through closeout; locked `sbatch` preflight/substantive and permitted preflight rerun; job-scoped monitoring/accounting; bounded `scancel`. |
| Resources/retry | Standard account `chopinsong`; one node/task, four CPUs/20 GB; 00:15 preflight, 01:00 substantive; 300-second cadence; one minimal re-reviewed preflight-only correction; no substantive automatic retry. |
| Cancellation | Recorded Iter002 job IDs only, for proven universal pre-execution defect. |
| Closeout | One scoped commit authorized; artifacts outside Git. |

### Approved Resource Revision

- `2026-08-29T17:00:00-07:00`: user approved the revised complete package after preflight `23723017` passed but reached 99.99% of its 20-GB allocation. All prior terms remain unchanged; substantive allocation is one node/task, six CPUs, 30 GB, one hour. Preflight remains valid and is not rerun.

## Provenance and Job Ledger

| Work unit | Canonical / submitted material | Run directory | Job IDs | State |
| --- | --- | --- | --- | --- |
| preflight | reviewed wrapper `7a6a4a6fb1e3a6e06f48491c62015d9e8b65b45b81b08f38aaacd9e94b0b8933`; submitted copy byte-identical | `.../elm_diagnose_iter002/preflight` | `23723017` | `COMPLETED 0:0`; 1:53; 20.00/20 GB; receipt pass |
| diagnostic (attempt 1) | reviewed wrapper `0621953afb167498065d77c17dfa1e84e1751bc3cc4567a5d5bb32acbfa13233`; source `745d76a5382768bd72c89cf2cce1079e57c11ccae9f9d502eee9b83017185bf8` | `.../elm_diagnose_iter002/diagnostic` | `23723072` | `FAILED 1:0`; 0:35; 4.70/30 GB; Matplotlib `labels` API incompatibility at ABBY boxplot |
| diagnostic (attempt 2) | same reviewed wrapper; corrected source `32c8824383921de9bbde85265e0af1fcc73f45c3ae58dae8a8ba77ac784bd5b4`; reviewed config `5c8cdf6738a3f4315e7c8821333666dda77ad8b7cdc0fd67e656506110ab7a16`, byte-identical external copy | `.../elm_diagnose_iter002/diagnostic` | `23723308` | `COMPLETED 0:0`; 2:51; 22.94/30 GB; 45 figures and 69 metrics rows |

## Independent Read-Only Review

- Reviewer: independent read-only reviewer.
- Outcome: PASS for the focused retry. The sole `labels=` to `tick_labels=` change matches the Matplotlib 3.11 failure; wrapper/config pinning and static `bash -n` / `git diff --check` passed. Retry config SHA `5c8cdf6738a3f4315e7c8821333666dda77ad8b7cdc0fd67e656506110ab7a16` is byte-identical to its external submitted copy.

## Execution and Diagnostics

- Static validation: immutable preflight passed in job `23723017`; initial substantive wrapper/source passed independent review; focused retry review passed after the one-token Matplotlib API fix.
- Preflight/submission/accounting: substantive attempt `23723072` failed from a Matplotlib API incompatibility, not resource use or input validation. User directed the minimal revision and retry. Retry `23723308` completed `0:0`, elapsed 2:51, CPU 2:16.755, peak memory 22.94/30 GB (76.48%).

## Validation, Evaluation, and Decision

- Overall acceptance result: pass. Preflight receipt covers all 60 optimized inputs and nine controls/observations; retry manifest covers all nine sites; 45 expected PNGs and 69 expected hourly metrics rows exist.
- Results: full seed-resolved rows are retained in `.../elm_diagnose_iter002/results/metrics.csv`; diagnostics are descriptive only, with no cross-site ranking or threshold decision. Optimized RMSE ranges / control-mean RMSE by site are ABBY 6.658–6.673 / 6.690, JERC 1.659 / 1.575, OSBS 1.100–1.197 / 1.236, RMNP 0.920–0.934 / 0.937, SOAP 7.446–7.454 / 7.635, TALL 1.333–1.337 / 1.332, TEAK 0.748–0.751 / 0.759, WREF 8.023–8.053 / 7.936, and YELL 3.211–3.222 / 3.233 gC m-2 day-1.
- Next action: none; any analysis/interpretation beyond the descriptive package requires a new request.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed until Iter002 evidence is evaluated.

## Closeout Checklist

- [x] Records, summaries, registry, and handoff finalized
- [x] Validator passes (static record/artifact checks and `git diff --check`)
- [x] No active or unaccounted jobs (`23723017`, `23723072`, and `23723308` terminally accounted)
- [x] Authorized closeout commit prepared
