# ELM Diagnostic Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their iteration under `slurm/iterXXX/`.

## Current utilities

| Tool | Purpose | Invocation / contract |
| --- | --- | --- |
| `iter002_sr_diagnostics.py` | Produces the Iter002 integrated nine-site `SR` diagnostic package from a passing preflight receipt: hourly, complete-day daily, monthly-climatology, UTC-diurnal, and hourly-distribution figures plus seed-level and `ppe6` control-mean hourly metrics. | Called by `slurm/iter002/diagnostic_iter002.slurm` with `--receipt` and `--output`. It verifies the receipt status and hashes of all control, optimized, and observation inputs before analysis; expected successful output is 45 PNGs, `metrics.csv` with 69 rows, and `manifest.json`. This is currently Iter002-specific (`SR`, nine sites, and the locked Puma repository root), not a general command-line diagnostic interface. |
| `oat_sensitivity.py` | Validates and analyzes explicit one-parameter-at-a-time ELM ensemble pickles without inferring directory membership. It computes 2018--2024 hourly member means and population standard deviations, range-dependent response-spread scores, response atlases, heatmaps, and decomposition-compensation plots. | Supply one `--parameter-pickle PARAMETER:EXACT_BASENAME` for every member of the tool's exact 14-parameter interface, the exact log-parameter set, an absolute pickle directory, control parameter NetCDF, and absolute output. `--validate-only` writes a passing receipt and immutable input manifest; `--manifest` requires and revalidates that manifest before atomically publishing results. |

## OAT sensitivity interpretation and validation

`oat_sensitivity.py` is a baseline-conditioned, range-dependent screening diagnostic. It must not
be described as PAWN, Sobol, joint/global sensitivity, parameter interaction, mediation, causal
effect, or parameter-value selection. The primary score is
`100 * (P95 - P05) / abs(ensemble median)` and therefore requires a finite nonzero median.
Rankings are separate for each target and for member temporal means versus temporal population
standard deviations (`ddof=0`). Spearman direction is intentionally not required.

Flux values are already hourly sampled daily-equivalent rates in `gC m-2 day-1`; the tool does not
accumulate them. `HR_TOTAL` and `LITTER_SOIL_C_TOTAL` are summed hourly before temporal statistics.
The latter excludes `CWDC` and is labeled `Total SOC`. Compensation figures express each pool C,
regulated `K_*`, and pool HR bin median as percentage departure from that response's ensemble
median: `100 * (response - median) / abs(median)`.

Validation rejects inferred or duplicate mappings, path components, globs, missing parameters,
non-ABBY or multi-parameter cases, member counts other than 100, invalid bounds/samples, ambiguous
array orientation, non-finite required outputs, and anything other than identical 61,320-sample
2018--2024 no-leap hourly axes. It never interpolates, drops members, repairs time axes, or follows
embedded runtime paths. Native parameter markers are plotted only when the exact modified scalar
or slice in the control NetCDF resolves to one finite value inside the sampled range.

Production reads only a passing manifest with matching hashes, loads one pickle at a time, retains
compact member statistics, writes into hidden staging, and renames staging to the final output only
after all expected tables and 35 figures pass internal checks. The manifest records hashes for
every published artifact. Incomplete staging is retained as failure evidence and is never treated
as a result package.
