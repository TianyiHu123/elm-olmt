# ELM Diagnostic Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their iteration under `slurm/iterXXX/`.

## Current utilities

| Tool | Purpose | Invocation / contract |
| --- | --- | --- |
| `iter002_sr_diagnostics.py` | Produces the Iter002 integrated nine-site `SR` diagnostic package from a passing preflight receipt: hourly, complete-day daily, monthly-climatology, UTC-diurnal, and hourly-distribution figures plus seed-level and `ppe6` control-mean hourly metrics. | Called by `slurm/iter002/diagnostic_iter002.slurm` with `--receipt` and `--output`. It verifies the receipt status and hashes of all control, optimized, and observation inputs before analysis; expected successful output is 45 PNGs, `metrics.csv` with 69 rows, and `manifest.json`. This is currently Iter002-specific (`SR`, nine sites, and the locked Puma repository root), not a general command-line diagnostic interface. |
| `oat_sensitivity.py` | Validates and analyzes explicit one-parameter-at-a-time ELM ensemble pickles without inferring directory membership. Independent interfaces select transient statistics and targets, observation references, optional compensation mappings, accumulated potential/N/P-limited pathways, litter-flux stoichiometry, and final-restart decomposer C/N/P states. | Supply ordered exact `PARAMETER:BASENAME` pickle mappings and an explicit `--log-parameters` subset, plus repeated `--target` and any needed optional-family arguments. Repeated `--statistic` selects `mean` and/or `temporal_std`; omission preserves both historical products. At most 36 mappings use a deterministic dynamic atlas. Restart and config/parameter provenance interfaces require complete ordered mappings and absolute roots. Compensation, litter ratios, observations, pathways, and restart analysis are independently optional. HR pathways require both limiter arguments. `--regression-results` locks core tables to a reference package. `--validate-only` writes a passing receipt and immutable manifest; `--manifest` revalidates it before atomic publication. |

## OAT sensitivity interpretation and validation

`oat_sensitivity.py` is a baseline-conditioned, range-dependent screening diagnostic. It must not
be described as PAWN, Sobol, joint/global sensitivity, parameter interaction, mediation, causal
effect, or parameter-value selection. The primary score is
`100 * (P95 - P05) / abs(ensemble median)`. A nonfinite/incomplete ensemble or zero median is
retained as an explicit unsupported score with a reason, never changed to zero. Rankings are
separate for each target and each selected statistic; temporal population standard deviations use
`ddof=0`. Spearman direction is intentionally not required.

Flux values are already hourly sampled daily-equivalent rates in `gC m-2 day-1`; the tool does not
accumulate them. `HR` is always direct `case.output["HR"]`; the historical constructed `HR_TOTAL`
is never substituted for it. `HR_TOTAL`, `LITTER_SOIL_C_TOTAL`, and `DECOMP_C_TOTAL` are summed
hourly before temporal statistics. `DECOMP_C_TOTAL` includes `CWDC` plus the three litter and four
soil pools; `LITTER_SOIL_C_TOTAL` excludes `CWDC` and is labeled `Total SOC`. Targets are selected only by
repeated `--target` arguments. Observation mappings add horizontal context to their selected
target atlases and never alter the model statistics or score. Compensation figures express each pool C,
regulated `K_*`, and pool HR bin median as percentage departure from that response's ensemble
median: `100 * (response - median) / abs(median)`.

Accumulated HR diagnostics multiply each configured pool C by its regulated per-second `K_*`,
apply `FPI` and `FPI_P` separately, sum the configured pools, and integrate hourly fluxes with a
3600-second factor. Litter-ratio time series use only finite values with positive nutrient-flux
denominators and report member support; member response ratios are flux-weighted totals formed
after converting daily-equivalent flux samples to hourly mass. These specialized diagnostics do
not enter the core OAT rankings.

When restart analysis is enabled, every mapped case must contain exactly `g00001` through
`g00100` and the declared final restart basename. Final decomposer C, N, and P states each sum the
eight lowercase `cwd`, `litr1`--`litr3`, and `soil1`--`soil4` `_vr` arrays using masked-array-aware
`numpy.nansum`. Shapes, dimensions, unit attributes (including consistently absent attributes),
finite support, filenames, and all restart hashes are validated and recorded. No layer-thickness
weighting or vegetation pools are introduced.

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
Iteration-specific wrappers and
manifests, rather than reusable-code defaults, lock the approved parameter names and membership.

Production reads only a passing manifest with matching hashes, loads one pickle at a time, retains
compact summaries, writes into hidden staging, and renames staging to the final output only
after all dynamically selected tables and figures pass internal checks. The manifest records hashes for
every published artifact. Incomplete staging is retained as failure evidence and is never treated
as a result package.
