# Coupling Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their
iteration under `slurm/iterXXX/`.

## Iter002 release utilities

- `release_forcing_surrogate.py` — reproduction gate, full-data `forcing-surrogate-v1` build,
  and full-data in-sample permutation importance.
- `validate_iter002_release.py` — fresh-process load, batch inference, negative schema gates,
  and sidecar identity checks.
