# Coupling Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their
iteration under `slurm/iterXXX/`.

## Iter002 release utilities

- `release_forcing_surrogate.py` — reproduction gate, full-data `forcing-surrogate-v1` build,
  and full-data in-sample permutation importance.
- `validate_iter002_release.py` — fresh-process load, batch inference, negative schema gates,
  and sidecar identity checks.

## Iter003 coupled evaluation

- `evaluate_coupled_surrogate.py` — PPE batch client over both spinup variants and the locked
  forcing artifact; writes per-member metrics, per-site median summaries, feedback plots, and
  optional NetCDF timeseries (`--save-timeseries`).

## Iter004 offline-versus-coupled comparison

- `evaluate_offline_coupled_comparison.py` — nine-site PPE client comparing offline
  forcing-v1 (ELM restart spinup) vs coupled `drop32`/`drop21_corr080`; writes metrics,
  timeseries NetCDF, and the locked four-figure plot package per site.

## Iter005 mean-spinup offline baseline

- `evaluate_mean_spinup_offline_comparison.py` — nine-site PPE client for offline
  forcing-v1 with site-mean ELM restart spinup; overlays Iter004 member-restart offline
  and coupled arms; writes metrics, timeseries NetCDF, and two annotated plot types per
  site (timeseries; SR vs member).
