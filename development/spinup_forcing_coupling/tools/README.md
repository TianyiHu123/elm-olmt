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
