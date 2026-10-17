# ELM Diagnostic Workflow Tools

Keep reusable validation and analysis engines here. Keep iteration wrappers, locked inventories,
fixtures, and artifact validators under `slurm/iterXXX/`. This README describes tool interfaces; it
does not grant runtime or scheduler authority. Follow `../WORKFLOW.md`, the active iteration record,
and the selected HPC profile before executing a diagnostic.

## Current utilities

| Tool | Purpose | Invocation / contract |
| --- | --- | --- |
| `flux_diagnostics.py` | YAML-driven, multi-site comparison of explicit control and optimized ELM flux series with observations. | Requires `--config` and a new `--output` directory. `--validate-only` reads and validates every configured input but writes nothing. A production run publishes five figures per site, `series_metrics.csv`, `member_metrics.csv`, `input_receipt.json`, and `manifest.json` through a staging-directory rename. |
| `iter002_sr_diagnostics.py` | Produces the Iter002 integrated nine-site `SR` diagnostic package from a passing preflight receipt: hourly, complete-day daily, monthly-climatology, UTC-diurnal, and hourly-distribution figures plus seed-level and `ppe6` control-mean hourly metrics. | Called by `slurm/iter002/diagnostic_iter002.slurm` with `--receipt` and `--output`. It verifies the receipt status and hashes of all control, optimized, and observation inputs before analysis; expected successful output is 45 PNGs, `metrics.csv` with 69 rows, and `manifest.json`. This is currently Iter002-specific (`SR`, nine sites, and the locked Puma repository root), not a general command-line diagnostic interface. |
| `oat_sensitivity.py` | Validates and analyzes explicit one-parameter-at-a-time ELM ensemble pickles without inferring directory membership. Independent interfaces select transient statistics and targets, observation references, optional compensation mappings, accumulated potential/N/P-limited pathways, litter-flux stoichiometry, and final-restart decomposer C/N/P states. | Supply ordered exact `PARAMETER:BASENAME` pickle mappings and an explicit `--log-parameters` subset, plus repeated `--target` and any needed optional-family arguments. Repeated `--statistic` selects `mean` and/or `temporal_std`; omission preserves both historical products. At most 36 mappings use a deterministic dynamic atlas. Restart and config/parameter provenance interfaces require complete ordered mappings and absolute roots. Compensation, litter ratios, observations, pathways, and restart analysis are independently optional. HR pathways require both limiter arguments. `--regression-results` locks core tables to a reference package. `--validate-only` writes a passing receipt and immutable manifest; `--manifest` revalidates it before atomic publication. |
| `oat_nutrient_diagnostics.py` | Iter008/Iter009 ABBY C:N nutrient-stress and pool-context analysis for the exact ordered `cn_s1`--`cn_s4` inventory. | Requires explicit pickle, config, parameter-file, control-file, and `SR` observation mappings. Uses mutually exclusive `--validate-only` and `--manifest` modes. Production emits six CSV tables, 17 fixed figures, and `output_manifest.json`; unsupported ratios remain explicit gaps. |
| `oat_carbon_balance.py` | Iter010 partial-boundary carbon-balance extension for the four locked ABBY C:N pickles and the validated Iter009 core package. | Requires the exact ordered `cn_s1`--`cn_s4` mappings, their provenance roots, the locked Iter009 input manifest/results, and a control parameter file. Uses `--validate-only` then `--manifest`. Production copies the verified 17-figure core package, adds four carbon-balance tables and four figures, and publishes 39,542 CSV data rows and 21 figures in total. |

## General flux diagnostics

`flux_diagnostics.py` takes a YAML document with top-level `variable`, `units`, and nonempty
`sites`. Each site declares one observation and a list of explicitly named series. Every series has
a unique `label`, a `role` of `control` or `optimized`, and one or more absolute `pickle_paths`;
exactly one control series is required. The observation must use label `obs`, name the selected
variable in `value_variable`, and may declare an uncertainty variable in `error_variable`. See
`../configs/iter003_sr.yml` for the complete schema in use.

The tool preserves observation gaps, collocates observations to the control forcing time, and
requires paired finite hourly support plus at least one complete paired UTC day at each site. It
reports RMSE, bias, MAE, R2, Pearson correlation, and KGE for each series mean and member. Its five
figures per site cover hourly and complete-day time series, monthly climatology, UTC diurnal cycle,
and the hourly distribution. Existing output or staging directories are never overwritten.

## OAT two-phase execution

The three OAT engines separate validation from production. `--validate-only` validates the exact
declared inventory and writes an input manifest plus a validation receipt to a new output
directory. A production invocation replaces `--validate-only` with
`--manifest ABSOLUTE_INPUT_MANIFEST`, revalidates the inputs and manifest contract, and writes to a
different new output directory. Iteration wrappers remain authoritative for the full argument
list, locked input identities, expected artifact counts, and scheduler resources.

## OAT sensitivity interpretation and validation

`oat_sensitivity.py` is a baseline-conditioned, range-dependent screening diagnostic. It must not
be described as PAWN, Sobol, joint/global sensitivity, parameter interaction, mediation, causal
effect, or parameter-value selection. The primary score is
`100 * (P95 - P05) / abs(ensemble median)`. A nonfinite/incomplete ensemble or zero median is
retained as an explicit unsupported score with a reason, never changed to zero. Rankings are
separate for each target and each selected statistic; temporal population standard deviations use
`ddof=0`. Spearman direction is intentionally not required.

Its required scientific interfaces are `--site`, `--pickle-dir`, repeated ordered
`--parameter-pickle PARAMETER:BASENAME` mappings, an explicit comma-separated `--log-parameters`
subset, `--control-paramfile`, one or more repeated `--target` selections, and `--output`.
Repeated `--statistic` selects `mean` and/or `temporal_std`; omission preserves both historical
products. Between one and 36 mappings use a deterministic dynamic atlas.

Flux values are already hourly sampled daily-equivalent rates in `gC m-2 day-1`; the tool does not
accumulate them. `HR` is always direct `case.output["HR"]`; the historical constructed `HR_TOTAL`
is never substituted for it. `HR_TOTAL`, `LITTER_SOIL_C_TOTAL`, and `DECOMP_C_TOTAL` are summed
hourly before temporal statistics. `DECOMP_C_TOTAL` includes `CWDC` plus the three litter and four
soil pools; `LITTER_SOIL_C_TOTAL` excludes `CWDC` and is labeled `Total SOC`. Targets are selected
only by repeated `--target` arguments. Transient observations use
`--observation TARGET:NETCDF_VARIABLE:SERIES_LABEL:ABSOLUTE_NETCDF`. They add horizontal context to
their selected target atlases and never alter the model statistics or score. Compensation figures
are created only for explicit `--compensation PARAMETER:POOL:RATE:RESPIRATION` mappings and express
each pool C, regulated `K_*`, and pool HR bin median as percentage departure from that response's
ensemble median: `100 * (response - median) / abs(median)`.

Accumulated HR diagnostics require one or more `--hr-pool POOL:RATE` mappings plus both
`--hr-n-limiter` and `--hr-p-limiter`. They multiply each configured pool C by its regulated
per-second rate, apply the N and P limiters separately, sum the configured pools, and integrate
hourly fluxes with a 3,600-second factor. Litter-ratio diagnostics are created only for explicit
`--litter-ratio LABEL:CARBON_FLUX:NUTRIENT_FLUX` mappings. Time series use only finite values with
positive nutrient-flux denominators and report member support; member responses are flux-weighted
ratios of accumulated fluxes. These specialized diagnostics do not enter the core OAT rankings.

Restart analysis requires an absolute `--restart-root` and complete ordered
`--parameter-restart PARAMETER:CASE_BASENAME` mappings. Every mapped case must contain exactly
`g00001` through `g00100` and the declared final restart basename. Final decomposer C, N, and P
states each sum the eight lowercase `cwd`, `litr1`--`litr3`, and `soil1`--`soil4` `_vr` arrays using
masked-array-aware
`numpy.nansum`. Shapes, dimensions, unit attributes (including consistently absent attributes),
finite support, filenames, and all restart hashes are validated and recorded. No layer-thickness
weighting or vegetation pools are introduced. Optional `--spinup-ratio DECOMP_CN_RATIO` and
`DECOMP_CP_RATIO` endpoints divide the corresponding eight-pool totals; unsupported ratios remain
gaps. `--require-complete-spinup-ratios` requires both ratios. Spinup observations use
`--spinup-observation TARGET:CSV_COLUMN:SERIES_LABEL:ABSOLUTE_CSV`, require restart analysis, and
add context without changing model responses or scores.

Validation rejects inferred or duplicate mappings, path components, globs, duplicate or malformed
parameter names, log or compensation parameters outside the explicit mapping, site mismatches,
multi-parameter cases, member counts other than 100, invalid bounds/samples, ambiguous
array orientation, non-finite required outputs, and anything other than identical 61,320-sample
2018--2024 no-leap hourly axes. It never interpolates, drops members, repairs time axes, or follows
embedded runtime paths. Native parameter markers are plotted only when the exact modified scalar
or slice in the control NetCDF resolves to one finite value inside the sampled range.

The explicit mappings define the production parameter inventory and its display order. The input
directory must contain exactly those mapped pickle basenames. Enabled config/parameter roots must
likewise contain exactly their mapped basenames; parameter names and ranges must agree with the
pickle, and every config must enable vertical soil carbon and bind its mapped parameter file.
Iteration-specific wrappers and manifests, rather than reusable-code defaults, lock the approved
parameter names and membership.

Production reads only a passing manifest with matching hashes, loads one pickle at a time, retains
compact summaries, writes into hidden staging, and renames staging to the final output only after
all dynamically selected tables and figures pass internal checks. The manifest records hashes for
every published artifact. Incomplete staging is retained as failure evidence and is never treated
as a result package.

## Nutrient-stress OAT contract

`oat_nutrient_diagnostics.py` is specialized to four 100-member, 61,320-hour ABBY C:N sweeps. It
computes mean and temporal population SD for direct nutrient, carbon-flux, pool-HR, and pool-stock
variables. Satisfaction metrics and pool-HR-per-pool-C responses use accumulated ratios: sum the
numerator over time, sum the denominator over time, then divide. A zero numerator with a positive
finite denominator is supported; a nonpositive or nonfinite denominator is an explicit unsupported
gap with a rejection reason. Direct `HR` remains distinct from the eight pool-HR pathways.

The fixed production package contains `parameter_metadata.csv`, `metric_definitions.csv`,
`member_metrics.csv`, `response_curves.csv`, `ratio_support.csv`, `observation_summary.csv`, 17
figures, and `output_manifest.json`. This engine deliberately retains its exact four-parameter and
ABBY artifact contract; use `oat_sensitivity.py` for a new inventory or general OAT question.

## Carbon-balance contract

`oat_carbon_balance.py` integrates direct `LITFALL` and direct `HR` as daily-equivalent hourly
samples divided by 24 and summed over time. It defines the eight-pool stock change as
`delta_C = C_end - C_begin`, then computes `rhs_C = HR_C + delta_C`,
`residual_C = input_C - rhs_C`, and absolute relative closure error against nonzero finite input.
It never substitutes constructed pool respiration for direct `HR`, and unsupported relative errors
remain explicit gaps.

The declared stock/flux boundary is partial: available provenance does not exclude every external
transfer. Consequently, closure figures and summaries diagnose nonclosure for this declared
boundary; they do not establish whole-system carbon balance, equilibrium, or carbon-input
limitation. The tool is identity-locked to the Iter010 ABBY inputs and verified Iter009 core
artifacts and should be extended or replaced explicitly for a different inventory.
