# ELM Diagnostic Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their iteration under `slurm/iterXXX/`.

## Current utilities

| Tool | Purpose | Invocation / contract |
| --- | --- | --- |
| `iter002_sr_diagnostics.py` | Produces the Iter002 integrated nine-site `SR` diagnostic package from a passing preflight receipt: hourly, complete-day daily, monthly-climatology, UTC-diurnal, and hourly-distribution figures plus seed-level and `ppe6` control-mean hourly metrics. | Called by `slurm/iter002/diagnostic_iter002.slurm` with `--receipt` and `--output`. It verifies the receipt status and hashes of all control, optimized, and observation inputs before analysis; expected successful output is 45 PNGs, `metrics.csv` with 69 rows, and `manifest.json`. This is currently Iter002-specific (`SR`, nine sites, and the locked Puma repository root), not a general command-line diagnostic interface. |
