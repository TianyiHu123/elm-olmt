# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: `none`
- Most recent iteration: `iter003`
- Status: `completed`
- Phase: `closed`
- Active job scope: `none`
- Active monitoring: `none`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-07T19:38:35-07:00`

## Completed Iter003

- Retry two `23729042` completed `0:0` in 02:29 after vectorizing complete-day aggregation; 21.6 GB/30 GB peak memory.
- Accepted package: 45 figures, 69 series rows, 960 member rows, passing receipt, and nine-site manifest at `.../elm_diagnose_iter003/results_retry2/`.
- The package is descriptive only. Monitoring-wrapper and agent-continuity evidence remains recorded for a separate workflow-improvement scope.

## Completed Iter002

- Goal: generate the recovered, integrated nine-site seed-resolved `SR` diagnostic package.
- Inputs: nine `ppe6` controls, all 60 updated `ctrlopt` pickles, and nine standard coupling SR NetCDF observations, locked by the passing preflight receipt.
- Execution: preflight `23723017` completed. Initial diagnostic `23723072` failed only because the installed Matplotlib rejects `Axes.boxplot(labels=...)`. The user authorized a minimal revision; focused independent review passed the `labels=` to `tick_labels=` correction. Retry `23723308` completed `0:0` in 2:51 using 22.94/30 GB.
- Deliverables: every site has raw-hourly, complete-day daily, monthly climatology, UTC diurnal, and hourly-distribution plots (45 PNGs total). `metrics.csv` has 69 descriptive hourly rows: 60 optimized seeds and nine control means.
- Scope result: accepted for descriptive diagnostics only. No cross-site ranking, score threshold, parameter selection, or scientific conclusion was made.

## Artifact References

- Iteration record: `development/ELM_diagnose/iterations/iter002.md`
- Registry: `development/ELM_diagnose/registry.csv`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Immutable input receipt: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/preflight/preflight_result.json`
- Figures/metrics/manifest: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter002/results/`
- Canonical retry material: `development/ELM_diagnose/tools/iter002_sr_diagnostics.py` and `development/ELM_diagnose/slurm/iter002/`

## Current Objective

Iter003 is closed. The planning-only Iter004 ABBY OAT sensitivity proposal below is finalized;
await the `br_mr` historical pickle and then a fresh consolidated kickoff approval.

## Current Risks or Blockers

- Historical evidence: the Iter003 foreground terminal sleep-loop was lost by the Codex wrapper.
  This is not a permanent prohibition; future monitoring strategy selection is governed by
  `WORKFLOW.md` Section D and the active runtime contract. See `iterations/iter003.md`.

## Agent-Continuity Failure to Carry Forward

- The agent repeatedly ended turns while Iter003 still had an approved next action (review retrieval, materialization, submission, or cadence observation), requiring the user to issue `continue`. Record this as a control-flow failure to diagnose in a future workflow-improvement scope; it is not an HPC failure and does not change current runtime authority.

## Next Iteration Plan: Iter004 ABBY OAT sensitivity diagnostic

This is a planning-only proposal for `iter004`; it grants no initialization, Python, scheduler,
retry, cancellation, commit, or output-directory authority. The plan assumes the complete
14-parameter input set. The only current waiting condition is arrival of the `br_mr` historical
pickle; do not initialize or run a partial 13-parameter Iter004 package.

### Identity, objective, and method boundary

- Sequential ID and work type: `iter004`, reusable diagnostic implementation plus one ABBY
  application.
- Objective: develop an input-driven OAT diagnostic and rank the range-wide response of ELM carbon
  fluxes and pools to 14 separately perturbed parameters, using each member's 2018--2024 hourly
  mean and temporal standard deviation.
- Hypothesis: the robust response spread over each user-selected reasonable parameter range will
  identify a compact set of parameters for later model-tuning work.
- Method boundary: use an OAT response-spread score, not PAWN, Sobol, a surrogate, a causal
  mediation claim, or an interaction estimate. Rankings are conditional on the declared parameter
  ranges and sampling distributions. Iter004 recommends no parameter values and performs no ELM
  model run, postprocessing, optimization, or tuning.

### Locked proposed inputs and interface

- Pickle root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/ABBY/pklfiles`.
- Control parameter file:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ctrl_sensi/params/clm_params_c211124.nc`.
- The command line, not a YAML file or automatic directory discovery, supplies one repeated
  `--parameter-pickle PARAMETER:EXACT_BASENAME` argument for every case:

| Parameter | Exact pickle basename | Sampling coordinate |
| --- | --- | --- |
| `act25` | `ABBY_ctrlact25_I20TRCNPRDCTCBC.pkl` | linear |
| `br_mr` | `ABBY_ctrlbrmr_I20TRCNPRDCTCBC.pkl` | linear |
| `grperc` | `ABBY_ctrlgrperc_I20TRCNPRDCTCBC.pkl` | linear |
| `grpnow` | `ABBY_ctrlgrpnow_I20TRCNPRDCTCBC.pkl` | linear |
| `k_l1` | `ABBY_ctrlkl1_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_l2` | `ABBY_ctrlkl2_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_l3` | `ABBY_ctrlkl3_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s1` | `ABBY_ctrlks1_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s2` | `ABBY_ctrlks2_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s3` | `ABBY_ctrlks3_I20TRCNPRDCTCBC.pkl` | log10 |
| `k_s4` | `ABBY_ctrlks4_I20TRCNPRDCTCBC.pkl` | log10 |
| `kmax` | `ABBY_ctrlkmax_I20TRCNPRDCTCBC.pkl` | linear |
| `leaf_long` | `ABBY_ctrlleaflong_I20TRCNPRDCTCBC.pkl` | linear |
| `q10_mr` | `ABBY_ctrlq10mr_I20TRCNPRDCTCBC.pkl` | linear |

- Canonical interface shape:

  ```text
  oat_sensitivity.py
    --pickle-dir <absolute directory>
    --parameter-pickle <parameter:exact basename>  # repeated exactly 14 times
    --log-parameters k_l1,k_l2,k_l3,k_s1,k_s2,k_s3,k_s4
    --control-paramfile <absolute NetCDF path>
    --output <absolute output directory>
    [--validate-only | --manifest <validated manifest>]
  ```

- Reject path components in the basename, glob metacharacters (`*`, `?`, or bracket patterns),
  duplicate parameter mappings, duplicate filenames, missing or extra parameters, and any mapping
  outside the exact 14-parameter set. Do not infer a case from an unlisted file.
- Pickle metadata is authoritative for parameter selector, embedded minimum/maximum, samples,
  `nsamples`, site, postprocessing years/frequency, outputs, and `taxis`. The transferred range
  files and configs are non-authoritative provenance/cross-check material; stale Perlmutter paths
  must never be dereferenced.
- The control parameter NetCDF supplies a plotted native-parameter marker only when the modified
  scalar or slice resolves unambiguously to one value. A heterogeneous or unavailable native
  value is recorded and omits only that marker; it does not invent a scalar reference.
- There is no control historical-response pickle in scope. Do not interpolate or label an ensemble
  response as an observed control run.

### Diagnostic targets, units, and statistics

- Primary targets: `GPP`, `ER`, `SR`, `HR_TOTAL`, `LITFALL`,
  `LITTER_SOIL_C_TOTAL`, `LITR1C`, `LITR2C`, `LITR3C`, `SOIL1C`, `SOIL2C`,
  `SOIL3C`, and `SOIL4C`.
- Derive hourly totals before temporal aggregation:

  ```text
  HR_TOTAL = CWDC_HR + LITR1_HR + LITR2_HR + LITR3_HR
             + SOIL1_HR + SOIL2_HR + SOIL3_HR + SOIL4_HR

  LITTER_SOIL_C_TOTAL = LITR1C + LITR2C + LITR3C
                         + SOIL1C + SOIL2C + SOIL3C + SOIL4C
  ```

- `LITTER_SOIL_C_TOTAL` is labeled `Total SOC` in figures and excludes `CWDC`.
- For every member and target, calculate the arithmetic mean and population standard deviation
  (`ddof=0`) across every hourly sample in 2018--2024. The standard deviation intentionally combines
  diurnal, seasonal, interannual, and weather-driven variation.
- Do not accumulate fluxes. `model_ELM/postprocess.py` already scales carbon-flux samples from
  `gC m-2 s-1` to hourly sampled daily-equivalent rates in `gC m-2 day-1`; their temporal standard
  deviations retain `gC m-2 day-1`. A cumulative flux, which is outside scope, would require time
  integration rather than an unscaled sum of these hourly samples.
- For each parameter, target, and member statistic, define the primary score as:

  ```text
  OAT response spread (%) = 100 * (P95 - P05) / abs(ensemble median)
  ```

  Require a finite nonzero median for the normalized score. Rank parameters from largest to
  smallest separately for each target and for mean versus temporal variability. Spearman
  correlation may be retained only as a secondary direction indicator.

### Response curves, heatmaps, and compensation plots

- Normalize each parameter to `[0, 1]` from its embedded bounds using the locked linear or log10
  coordinate. Plot all 100 members lightly and connect ten equal-count bin medians; do not fit or
  extrapolate a surrogate response.
- Produce 26 response-curve atlases: one 14-panel mean atlas and one 14-panel variability atlas for
  each of the 13 targets.
- Produce two 14-by-13 sensitivity heatmaps containing the response-spread score and rank: one for
  member means and one for member temporal standard deviations.
- Produce seven two-panel compensation figures. Each mean/variability panel compares normalized
  bin-median responses of the parameter's corresponding pool C, actual regulated `K_*`, and pool
  HR: `k_l1`/`LITR1`, `k_l2`/`LITR2`, `k_l3`/`LITR3`, and `k_s1`--`k_s4`/`SOIL1`--`SOIL4`.

### Work units, implementation, and proposed resources

- Reusable entry point: `development/ELM_diagnose/tools/oat_sensitivity.py`; document its interface,
  outputs, validation contract, units, score interpretation, and limitations in
  `development/ELM_diagnose/tools/README.md`.
- Iteration-specific canonical wrappers and validators belong under
  `development/ELM_diagnose/slurm/iter004/`. No Iter004 YAML is proposed.
- Work unit one, preflight: resolve the 14 explicit mappings, load one pickle at a time, validate
  structure and metadata, hash the inputs, and write a validation receipt plus immutable
  `input_manifest.json`; calculate no rankings or substantive figures.
- Work unit two, diagnostic: consume only the passing manifest and matching hashes, load one pickle
  at a time, retain compact member summaries, generate the tables/figures, and atomically publish
  only a complete package.
- Proposed output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter004_abby_oat/`,
  with separate `preflight/` and `results/` work-unit directories. Retain outputs without automatic
  backup or deletion; keep large data outside Git.
- Proposed Puma profile and environment: `development/hpc/puma.md`, `standard`/`chopinsong`, and
  `OLMT_puma`. Initial preflight and diagnostic each request one node/task, six CPUs (30 GB), and
  two hours. A resource-only retry may be proposed at eight CPUs (40 GB) and four hours.
- Obtain independent read-only review of the plan, implementation, canonical/submitted identity,
  exact mappings, manifest logic, fixtures, units, gates, and Slurm material before preflight.
- Proposed retry boundary: one minimal preflight-only correction/rerun for wrapper, import, or
  receipt defects that changes no input, method, score, gate, or scientific scope. Application,
  schema, input, numerical, or scientific failures receive no automatic retry. A separately
  approved resource-only retry must retain inputs and methods; after any retry, ask the user to
  retry again or close.
- Proposed cancellation boundary: only recorded Iter004 job IDs, and only for a proven universal
  pre-execution defect or explicit user direction. Empty `squeue` is not completion; reconcile all
  jobs through job-scoped terminal accounting.

### Tentative acceptance gates and decision rule

- Input gate: all 14 exact files exist and load; each mapping agrees with exactly one
  `ensemble_parms` value; every case is ABBY, single-parameter, 100-member, bounded, finite, and
  consistent with its locked linear/log sampling coordinate.
- Time/output gate: every required raw variable exists as an unambiguous `time x member` matrix;
  all cases have exactly matching hourly `taxis` for 2018--2024 and the expected 61,320 no-leap
  samples; primary and derived arrays are finite and shape-compatible. No interpolation, member
  dropping, or time-axis repair is permitted.
- Calculation gate: a deterministic synthetic fixture verifies orientation, hourly summation before
  aggregation, `ddof=0`, linear/log normalization, ten-member bins, quantiles, score/rank direction,
  and all seven compensation mappings.
- Artifact gate for 14 passing cases: `parameter_metadata.csv` has 14 rows;
  `member_metrics.csv` has 1,400 parameter-member rows; `sensitivity_scores.csv` has 364
  parameter-target-statistic rows; `response_curves.csv` has complete raw/bin provenance; exactly
  35 PNGs exist (26 atlases, two heatmaps, seven compensation figures); validation receipt, input
  manifest, and output manifest are present, internally consistent, and hash-complete.
- Review/accounting/record gate: independent review passes or has explicitly resolved concerns;
  every job has authoritative terminal state and resource evidence; artifacts, source/config
  hashes, iteration report, `CURRENT.md`, registry, and cumulative summary agree.
- Pass decision: accept the package as a descriptive, range-dependent OAT screening result and
  report complete rankings without automatically selecting tuning parameters. Any failed immutable
  gate rejects the work unit and prevents partial publication or scientific interpretation.
- Stop boundary: validated closeout with no active/unaccounted jobs, followed by the user-selected
  retry-or-close decision when applicable. A future kickoff package must separately ask whether one
  tightly scoped closeout commit is authorized.

### Expected durable evidence and fresh approval boundary

- On a future approved kickoff, create `iterations/iter004.md`, update `handoff/CURRENT.md`, record
  exact mappings and runtime authority, create reviewed canonical/submitted material, and later
  update `registry.csv` and `ITERATION_SUMMARY.md` only at validated closeout.
- Arrival of `br_mr` does not itself authorize initialization. Before any Iter004 file creation,
  Python, output-directory creation, review launch, or scheduler action, revalidate all 14 paths and
  present one fresh consolidated kickoff package containing this unchanged plan, exact output and
  resource contract, finite work units, monitoring/accounting authority, retry/cancellation terms,
  stop conditions, outside-sandbox scheduler authority, and commit choice.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, and `iterations/iter003.md`.
2. Treat Iter003 outputs and failed/cancelled attempts as retained provenance.
3. Verify arrival and static identity of all 14 planned Iter004 pickles, including `br_mr`.
4. Present the complete Iter004 kickoff package and obtain fresh approval before initialization or
   runtime work.
