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

### Seed-versus-control hourly metrics

Each optimized entry is `seed median [minimum, maximum]` across the available seeds for that site; the value after `/` is the `ppe6` control ensemble-mean metric. Bold marks the better of the seed median and control mean: lower RMSE/MAE and absolute bias, higher `R2`, Pearson `r`, and KGE. All metrics use the same intersected, finite hourly observations for a site. RMSE, bias, and MAE are in `gC m-2 day-1`; `R2`, Pearson `r`, and KGE are unitless. These are descriptive comparisons, not a cross-site ranking or selection rule.

| Site | Seeds | Hourly n | RMSE: seed / control | Bias: seed / control | MAE: seed / control | R2: seed / control | Pearson r: seed / control | KGE: seed / control |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| ABBY | 9 | 26,264 | **6.663 [6.658, 6.673]** / 6.690 | **-6.180 [-6.191, -6.175]** / -6.213 | **6.180 [6.175, 6.191]** / 6.213 | **-5.429 [-5.450, -5.420]** / -5.481 | 0.631 [0.629, 0.635] / **0.699** | -0.284 [-0.285, -0.284] / **-0.271** |
| JERC | 1 | 51,882 | 1.659 [1.659, 1.659] / **1.575** | 1.514 [1.514, 1.514] / **1.427** | 1.530 [1.530, 1.530] / **1.449** | -2.798 [-2.798, -2.798] / **-2.423** | 0.636 [0.636, 0.636] / **0.638** | -0.209 [-0.209, -0.209] / **-0.156** |
| OSBS | 4 | 26,051 | **1.119 [1.100, 1.197]** / 1.236 | **1.044 [1.024, 1.127]** / 1.163 | **1.045 [1.026, 1.128]** / 1.164 | **-5.412 [-6.344, -5.202]** / -6.821 | **0.530 [0.524, 0.531]** / 0.529 | **-0.177 [-0.258, -0.161]** / -0.284 |
| RMNP | 8 | 35,001 | **0.928 [0.920, 0.934]** / 0.937 | **-0.527 [-0.536, -0.522]** / -0.542 | **0.570 [0.566, 0.572]** / 0.576 | **0.225 [0.215, 0.238]** / 0.210 | 0.838 [0.827, 0.853] / **0.841** | **0.193 [0.188, 0.202]** / 0.184 |
| SOAP | 9 | 26,191 | **7.450 [7.446, 7.454]** / 7.635 | **-5.090 [-5.094, -5.086]** / -5.257 | **5.094 [5.090, 5.098]** / 5.260 | **-0.621 [-0.623, -0.619]** / -0.703 | **0.685 [0.683, 0.685]** / 0.656 | **-0.176 [-0.177, -0.175]** / -0.215 |
| TALL | 9 | 51,051 | 1.337 [1.333, 1.337] / **1.332** | **0.029 [-0.017, 0.032]** / -0.104 | 1.033 [1.020, 1.033] / **0.999** | 0.117 [0.117, 0.122] / **0.123** | 0.343 [0.342, 0.350] / **0.360** | **0.073 [0.066, 0.074]** / 0.066 |
| TEAK | 2 | 35,023 | **0.750 [0.748, 0.751]** / 0.759 | **-0.072 [-0.081, -0.062]** / -0.080 | **0.582 [0.580, 0.584]** / 0.585 | **0.246 [0.243, 0.250]** / 0.227 | **0.509 [0.504, 0.514]** / 0.487 | **0.251 [0.243, 0.259]** / 0.240 |
| WREF | 9 | 26,267 | 8.035 [8.023, 8.053] / **7.936** | -6.785 [-6.806, -6.772] / **-6.679** | 6.785 [6.772, 6.806] / **6.679** | -2.250 [-2.265, -2.240] / **-2.170** | 0.704 [0.699, 0.715] / **0.717** | -0.317 [-0.319, -0.317] / **-0.302** |
| YELL | 9 | 35,011 | **3.217 [3.211, 3.222]** / 3.233 | **-2.630 [-2.633, -2.626]** / -2.648 | **2.630 [2.626, 2.633]** / 2.648 | **-1.222 [-1.228, -1.214]** / -1.243 | 0.709 [0.700, 0.717] / **0.719** | **-0.141 [-0.144, -0.138]** / -0.146 |

## Proposed Next-Iteration Plan (Planning Only)

### Iter003 — generalized carbon-flux diagnostic tool and SR package

- **Sequential ID and work type:** `iter003`; reusable-tool implementation plus one bounded nine-site `SR` diagnostic package.
- **Evidence-derived objective:** replace the Iter002-only, receipt-driven `SR` utility with a readable general carbon-flux diagnostic tool. Its first package will compare the retained control and optimized model outputs with `SR` observations for the same nine NEON sites. This work establishes a diagnostic interface and descriptive evidence only; it makes no scientific-improvement, cross-site ranking, parameter-selection, or model-validation claim.
- **Selected site and environment:** Puma, using `development/hpc/puma.md` and `OLMT_puma`.

#### Direct configuration contract

On approval, create the tracked configuration `development/ELM_diagnose/configs/iter003_sr.yml` and the reusable entry point `development/ELM_diagnose/tools/flux_diagnostics.py`. The only runtime command-line arguments will be `--config <YAML>` and `--output <directory>` (with an optional non-writing `--validate-only` mode for future use). The YAML, not a preflight-generated receipt, is the authoritative input contract. It must list absolute paths explicitly: no glob, path template, inferred site membership, or generated configuration is allowed.

Each site has an `observation` block with `label: obs`, the full NetCDF path, `value_variable: SR`, and `error_variable: SR_err`; it has one `control` series with `label: ctrl`; and it has one `optimized` series per listed seed, whose label is that seed number. A series owns a `pickle_paths` array. A one-dimensional output contributes one member; a two-dimensional output contributes its member columns; and all members contributed by every path in the same series are concatenated. Thus a series may mix single-run and ensemble pickles without changing the input schema. Labels must be unique within a site. The tool derives safe filename fragments from labels and records the source-pickle/member mapping in its manifest.

The direct input inventory is the retained passing Iter002 membership below. `PKL_ROOT` is `/xdisk/chopinsong/tianyihu/elm-olmt/pklfiles`; every filename in the control and optimized columns must be expanded to its full `PKL_ROOT` path in the YAML. The observation paths are already absolute.

| Site | Control filename (`label: ctrl`) | Optimized label: filename (`role: optimized`) | Observation (`label: obs`) |
| --- | --- | --- | --- |
| ABBY | `ABBY_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: ABBY_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: ABBY_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: ABBY_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: ABBY_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9014: ABBY_ctrlopt9014_I20TRCNPRDCTCBC.pkl`; `9015: ABBY_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: ABBY_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: ABBY_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/ABBY/ABBY_cdo_merge.nc` |
| JERC | `JERC_ppe6_I20TRCNPRDCTCBC.pkl` | `9017: JERC_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/JERC/JERC_cdo_merge.nc` |
| OSBS | `OSBS_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: OSBS_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: OSBS_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9013: OSBS_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9017: OSBS_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/OSBS/OSBS_cdo_merge.nc` |
| RMNP | `RMNP_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: RMNP_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: RMNP_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: RMNP_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: RMNP_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: RMNP_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9015: RMNP_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: RMNP_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: RMNP_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/RMNP/RMNP_cdo_merge.nc` |
| SOAP | `SOAP_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: SOAP_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: SOAP_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: SOAP_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: SOAP_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: SOAP_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9014: SOAP_ctrlopt9014_I20TRCNPRDCTCBC.pkl`; `9015: SOAP_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: SOAP_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: SOAP_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/SOAP/SOAP_cdo_merge.nc` |
| TALL | `TALL_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: TALL_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: TALL_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: TALL_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: TALL_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: TALL_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9014: TALL_ctrlopt9014_I20TRCNPRDCTCBC.pkl`; `9015: TALL_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: TALL_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: TALL_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/TALL/TALL_cdo_merge.nc` |
| TEAK | `TEAK_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: TEAK_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9016: TEAK_ctrlopt9016_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/TEAK/TEAK_cdo_merge.nc` |
| WREF | `WREF_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: WREF_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: WREF_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: WREF_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: WREF_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: WREF_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9014: WREF_ctrlopt9014_I20TRCNPRDCTCBC.pkl`; `9015: WREF_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: WREF_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: WREF_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/WREF/WREF_cdo_merge.nc` |
| YELL | `YELL_ppe6_I20TRCNPRDCTCBC.pkl` | `9009: YELL_ctrlopt9009_I20TRCNPRDCTCBC.pkl`; `9010: YELL_ctrlopt9010_I20TRCNPRDCTCBC.pkl`; `9011: YELL_ctrlopt9011_I20TRCNPRDCTCBC.pkl`; `9012: YELL_ctrlopt9012_I20TRCNPRDCTCBC.pkl`; `9013: YELL_ctrlopt9013_I20TRCNPRDCTCBC.pkl`; `9014: YELL_ctrlopt9014_I20TRCNPRDCTCBC.pkl`; `9015: YELL_ctrlopt9015_I20TRCNPRDCTCBC.pkl`; `9016: YELL_ctrlopt9016_I20TRCNPRDCTCBC.pkl`; `9017: YELL_ctrlopt9017_I20TRCNPRDCTCBC.pkl` | `/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/YELL/YELL_cdo_merge.nc` |

#### Locked diagnostic behavior

- The reusable code is formatted as conventional, separately named functions for configuration, validation/loading, time alignment, aggregation, metrics, plotting, and manifest writing. It must not retain Iter002 hard-coded repository, target, site-count, or receipt assumptions.
- Every merged member must have an unambiguous `time × member` orientation and the identical `taxis` of the other members in its series and site. A mismatch is an input-integrity failure, not an instruction to interpolate or silently merge.
- Time-series plots retain the aligned timestamp grid. Missing/invalid model values, observations, or error values are represented as `NaN`; Matplotlib must therefore show a visual gap instead of connecting the endpoints of a missing interval. Metrics use only the paired finite observations for the specific member or series being evaluated.
- Produce five figures per site: hourly time series, complete-UTC-day daily time series, monthly climatology, UTC-hour diurnal climatology, and hourly distribution. Each filename contains site and target variable: `<SITE>_SR_hourly_timeseries.png`, `<SITE>_SR_daily_timeseries.png`, `<SITE>_SR_monthly_climatology.png`, `<SITE>_SR_utc_diurnal.png`, and `<SITE>_SR_hourly_distribution.png`.
- Plot each configured series as its member mean; show its ±1 standard-deviation band only when it has multiple members. A single-member series has only its line. Plot observation `obs` as a line. Plot its `±1σ` shaded band only where the configured `SR_err` variable exists in that NetCDF file and is valid; if absent or unusable, omit the band and record `missing_in_file` or `invalid` in the manifest. Do not display a synthetic fallback as observation uncertainty.
- Daily points require all 24 UTC hours for the relevant plotted quantity; otherwise that day is `NaN` and appears as a gap. Monthly and diurnal means use valid values in their bins. Their observation uncertainty is propagated as the standard error of the mean under the explicitly recorded independent-error assumption.
- Write `series_metrics.csv` for each configured control/optimized series and `member_metrics.csv` for every contributing member. Retain descriptive hourly RMSE, bias, MAE, R2, Pearson r, KGE, and paired-count columns; do not rank, select, pool across sites, or impose performance thresholds.
- Write a manifest and immutable input receipt from the direct YAML that record source and configuration hashes, paths, pickle/member counts, time-axis identity, observation-error availability, valid counts, output paths, and source identity.

#### Proposed execution, evidence, and gates

- **Finite work units and output:** one integrated nine-site diagnostic job. The proposed output root is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter003/`; it is not authorized for creation until kickoff approval. Retain generated artifacts without automated deletion or backup.
- **Proposed resources and monitoring:** one Puma standard node/task, six CPUs (30 GB under the shared profile), one-hour cap, `OLMT_puma`, and the documented 300-second monitoring cadence, with immediate identity and terminal-accounting exceptions. The one job validates the direct YAML and every input before writing diagnostic outputs; no separate preflight job generates configuration. No automatic substantive retry is proposed. A code/interface/input failure preserves evidence and requires fresh authority; cancellation is limited to recorded Iter003 job IDs and a proven universal pre-execution defect.
- **Review and validation:** after kickoff, an independent read-only reviewer must review the source, direct YAML, Slurm wrapper, static checks, and canonical/submitted identity. The compute-node job must validate all listed paths and hashes, scalar/ensemble target shapes, time-axis compatibility, `SR` availability, observation time overlap, optional `SR_err` availability, and declared artifact completeness before accepting outputs.
- **Acceptance gates and decision rule:** pass only if all nine declared sites, one control series per site, all 60 declared optimized series, and nine observation files are present and identity-locked; every configured series has compatible members; every site has nonempty paired hourly support and at least one complete UTC day; five variable-named figures/site, both metric tables, manifest, and receipt exist; and the required records agree. Observation-error shading is conditional and not a gate: unavailable `SR_err` is recorded and unshaded. Results remain descriptive only.
- **Expected records and closeout:** on a later approved kickoff, create `iterations/iter003.md`, the YAML/tool/Slurm material, an external output directory, independent-review evidence, job ledger, summary, registry row, validator evidence, handoff, and at most one scoped closeout commit only if expressly included in that future package.

#### Fresh approval boundary

This is a planning-only proposal. It authorizes no Iter003 file or directory creation, Python/runtime execution, scheduler submission/monitoring/cancellation, retry, or implementation commit. A later consolidated kickoff package must restate the finalized scope, exact resources, output root, review, scheduler and outside-sandbox authority, retry/cancellation limits, and closeout-commit authority before initialization.

## Closeout Checklist

- [x] Records, summaries, registry, and handoff finalized
- [x] Validator passes (static record/artifact checks and `git diff --check`)
- [x] No active or unaccounted jobs (`23723017`, `23723072`, and `23723308` terminally accounted)
- [x] Authorized closeout commit prepared
