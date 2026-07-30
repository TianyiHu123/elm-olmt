# Spinup Surrogate Summary Evidence

This directory contains repository-tracked evidence used to compare spinup-surrogate iterations
and support release decisions.

Before compacting or removing any reports, a complete copy of this directory was stored on Puma
on 2026-07-29 at:

```text
/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_summary/
```

This is a temporary Puma `/xdisk` backup, not a permanent or portable archive. Puma `/xdisk`
storage is unbacked, and the path will need to change when the project moves to another HPC
system. Preserve any required durable copy separately.

## Tracked retention policy

Keep repository copies small and decision-focused:

- retain per-variant metric summaries, exact feature frequencies, gate decisions, final
  permutation-importance summaries, release manifests and validation reports, and final
  decision plots;
- use the `spinup-feature-stability-compact-v1` schema for feature-stability reports;
- keep exhaustive all-pair correlation tables, raw per-seed statistics, models, memmaps, and
  intermediate outputs outside Git;
- record the full report's SHA-256, byte size, and backup path in every compact report.

The compact schema preserves per-target gate metrics, per-feature median importance and stability
fields, threshold-crossing correlation pairs, surviving representatives, and cross-target strong
features. It omits the redundant full distribution summaries and correlations for pairs that did
not cross a configured threshold.

`iter006` through `iter011` use the compact schema. The smaller legacy `iter005`
feature-stability reports do not contain the later correlation diagnostics and remain unchanged.

For future aggregation, `tools/analyze_feature_stability.py` writes compact output by default.
Use `--full-output-json` to save the corresponding full report outside the repository:

```bash
python development/spinup_surrogate/tools/analyze_feature_stability.py \
  --stats-dir /path/to/surrogate_spinup \
  --variant example_variant \
  --output-json development/spinup_surrogate/summaries/iterXXX/example_feature_stability.json \
  --full-output-json /path/to/full_reports/example_feature_stability.json
```
